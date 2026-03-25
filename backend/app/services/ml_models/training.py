"""
ML Expense Classifier Training Pipeline
Handles feature engineering, training, and model persistence
"""
from typing import Dict, List, Tuple, Optional
import os
import joblib
import logging
from datetime import datetime
import json

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np

logger = logging.getLogger(__name__)

# Model storage path
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../../ml_models")
os.makedirs(MODEL_DIR, exist_ok=True)


class MLExpenseClassifierTrainer:
    """
    Trains and manages Random Forest classifier for expense categorization
    """

    CATEGORIES = [
        "groceries", "restaurants", "transportation", "utilities",
        "entertainment", "shopping", "healthcare", "insurance",
        "housing", "fitness", "education", "personal_care", "subscriptions"
    ]

    def __init__(self):
        self.model = None
        self.tfidf_vectorizer = None
        self.scaler = None
        self.category_to_idx = {cat: idx for idx, cat in enumerate(self.CATEGORIES)}
        self.idx_to_category = {idx: cat for cat, idx in self.category_to_idx.items()}

    def create_model(self) -> Pipeline:
        """Create the ML pipeline with TF-IDF and Random Forest"""
        return Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                lowercase=True,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=1,
                max_df=0.95
            )),
            ('classifier', RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                min_samples_split=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            ))
        ])

    def prepare_training_data(
        self,
        transactions: List[Dict],
        keyword_classifier: Optional[object] = None
    ) -> Tuple[List[str], List[int], List[float]]:
        """
        Prepare training data from transactions using keyword-based auto-labeling

        Args:
            transactions: List of transaction dicts with 'description' and 'amount'
            keyword_classifier: ExpenseClassifier instance for auto-labeling

        Returns:
            Tuple of (descriptions, category_indices, confidence_scores)
        """
        descriptions = []
        category_indices = []
        confidence_scores = []

        for txn in transactions:
            description = txn.get("description", "").strip()
            if not description:
                continue

            # Auto-label using keyword classifier
            if keyword_classifier:
                result = keyword_classifier.classify(
                    description,
                    txn.get("amount")
                )
                category = result.get("category", "uncategorized")
                confidence = result.get("confidence", 0.0)

                # Only use high-confidence labels for training
                if confidence >= 0.7 and category in self.category_to_idx:
                    descriptions.append(description)
                    category_indices.append(self.category_to_idx[category])
                    confidence_scores.append(confidence)

        logger.info(
            f"Prepared {len(descriptions)} training samples from {len(transactions)} transactions"
        )
        return descriptions, category_indices, confidence_scores

    def train(
        self,
        descriptions: List[str],
        category_indices: List[int],
        sample_weights: Optional[List[float]] = None
    ) -> Dict:
        """
        Train the Random Forest classifier

        Args:
            descriptions: List of transaction descriptions
            category_indices: List of category indices
            sample_weights: Optional confidence weights for samples

        Returns:
            Training metrics
        """
        if len(descriptions) < 50:
            logger.warning(
                f"Training with only {len(descriptions)} samples. "
                "Recommend at least 100 samples for reliable training."
            )

        self.model = self.create_model()

        # Train with optional sample weights (higher confidence = higher weight)
        self.model.fit(descriptions, category_indices, classifier__sample_weight=sample_weights)

        # Calculate training metrics
        train_score = self.model.score(descriptions, category_indices)
        logger.info(f"Model training accuracy: {train_score:.4f}")

        # Get feature importance
        feature_importance = self.model.named_steps['classifier'].feature_importances_
        feature_names = self.model.named_steps['tfidf'].get_feature_names_out()

        # Top 20 important features
        top_indices = np.argsort(feature_importance)[-20:][::-1]
        top_features = {
            feature_names[i]: float(feature_importance[i])
            for i in top_indices
        }

        metrics = {
            "training_accuracy": float(train_score),
            "samples_used": len(descriptions),
            "categories": len(self.CATEGORIES),
            "top_features": top_features,
            "training_timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"Training metrics: {json.dumps(metrics, indent=2)}")
        return metrics

    def predict(self, descriptions: List[str]) -> List[Dict]:
        """
        Make predictions on new descriptions

        Args:
            descriptions: List of transaction descriptions

        Returns:
            List of predictions with category and confidence
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")

        predictions = self.model.predict(descriptions)
        probabilities = self.model.predict_proba(descriptions)

        results = []
        for pred_idx, probs in zip(predictions, probabilities):
            category = self.idx_to_category[pred_idx]
            confidence = float(probs[pred_idx])
            results.append({
                "category": category,
                "confidence": confidence,
                "probabilities": {
                    self.idx_to_category[i]: float(prob)
                    for i, prob in enumerate(probs)
                }
            })

        return results

    def save_model(self, version: str = "v1") -> str:
        """
        Save trained model and metadata

        Args:
            version: Model version identifier

        Returns:
            Path to saved model
        """
        if self.model is None:
            raise ValueError("No trained model to save")

        model_path = os.path.join(MODEL_DIR, f"classifier_{version}.joblib")
        joblib.dump(self.model, model_path)
        logger.info(f"Model saved to {model_path}")

        # Save metadata
        metadata = {
            "version": version,
            "created_at": datetime.utcnow().isoformat(),
            "categories": self.CATEGORIES,
            "model_type": "RandomForestClassifier",
            "tfidf_features": 1000
        }
        metadata_path = os.path.join(MODEL_DIR, f"classifier_{version}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Metadata saved to {metadata_path}")
        return model_path

    def load_model(self, version: str = "v1") -> bool:
        """
        Load trained model from disk

        Args:
            version: Model version to load

        Returns:
            True if successful, False otherwise
        """
        model_path = os.path.join(MODEL_DIR, f"classifier_{version}.joblib")

        if not os.path.exists(model_path):
            logger.warning(f"Model not found at {model_path}")
            return False

        try:
            self.model = joblib.load(model_path)
            logger.info(f"Model loaded from {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def get_latest_model_version(self) -> Optional[str]:
        """Get the latest model version available"""
        files = os.listdir(MODEL_DIR)
        model_files = [f for f in files if f.startswith("classifier_") and f.endswith(".joblib")]

        if not model_files:
            return None

        # Extract version strings and sort
        versions = [f.replace("classifier_", "").replace(".joblib", "") for f in model_files]
        versions.sort()
        return versions[-1]
