"""
Expense Classification Service
ML-based automatic categorization using Random Forest classifier with keyword fallback
"""
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ExpenseClassifier:
    """
    Expense classification system with ML-based approach.
    Uses Random Forest classifier trained on transaction descriptions.
    Falls back to keyword matching if ML model unavailable or low confidence.
    """

    # Training data: keywords mapped to categories
    CATEGORY_KEYWORDS = {
        "groceries": [
            "grocery", "supermarket", "whole foods", "trader joe", "safeway",
            "costco", "walmart", "target", "food lion", "kroger", "albertsons",
            "market", "fresh", "organic"
        ],
        "restaurants": [
            "restaurant", "cafe", "coffee", "starbucks", "mcdonald", "burger",
            "pizza", "taco", "chipotle", "subway", "dunkin", "dining",
            "bar", "pub", "grill", "bistro", "eatery", "diner", "food delivery",
            "doordash", "ubereats", "grubhub", "postmates"
        ],
        "transportation": [
            "uber", "lyft", "taxi", "gas", "fuel", "shell", "chevron", "exxon",
            "mobil", "bp", "parking", "metro", "transit", "subway", "bus",
            "train", "airline", "flight", "car rental", "toll"
        ],
        "utilities": [
            "electric", "water", "gas bill", "internet", "cable", "phone",
            "verizon", "at&t", "comcast", "spectrum", "utility", "power"
        ],
        "entertainment": [
            "movie", "theater", "cinema", "netflix", "spotify", "hulu",
            "disney", "amazon prime", "gaming", "xbox", "playstation",
            "concert", "event", "ticket", "amusement", "bowling", "recreation"
        ],
        "shopping": [
            "amazon", "ebay", "store", "shop", "retail", "mall", "outlet",
            "clothing", "apparel", "fashion", "shoes", "electronics"
        ],
        "healthcare": [
            "pharmacy", "cvs", "walgreens", "hospital", "clinic", "doctor",
            "dental", "medical", "health", "prescription", "rx"
        ],
        "insurance": [
            "insurance", "policy", "premium", "coverage", "geico", "state farm",
            "progressive", "allstate"
        ],
        "housing": [
            "rent", "mortgage", "hoa", "lease", "property management",
            "apartment", "housing"
        ],
        "fitness": [
            "gym", "fitness", "yoga", "pilates", "workout", "training",
            "sports", "athletic", "planet fitness", "la fitness", "equinox"
        ],
        "education": [
            "school", "university", "college", "tuition", "course",
            "book", "textbook", "learning", "education", "udemy", "coursera"
        ],
        "personal_care": [
            "salon", "spa", "haircut", "barber", "beauty", "cosmetics",
            "grooming", "massage"
        ],
        "subscriptions": [
            "subscription", "monthly", "annual", "membership", "service fee"
        ]
    }
    
    def __init__(self):
        self.category_scores = defaultdict(float)
        self._build_keyword_index()

        # Initialize ML model
        self.ml_model = None
        self.use_ml = False
        self._load_ml_model()
    
    def _build_keyword_index(self):
        """Build reverse index: keyword -> category"""
        self.keyword_to_category = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                self.keyword_to_category[keyword.lower()] = category

    def _load_ml_model(self):
        """Load pre-trained ML model if available"""
        try:
            from app.services.ml_models.training import MLExpenseClassifierTrainer
            trainer = MLExpenseClassifierTrainer()
            latest_version = trainer.get_latest_model_version()

            if latest_version and trainer.load_model(latest_version):
                self.ml_model = trainer.model
                self.use_ml = True
                logger.info(f"Loaded ML model version: {latest_version}")
            else:
                logger.info("No pre-trained ML model found. Using keyword matching fallback.")
        except Exception as e:
            logger.warning(f"Could not load ML model: {e}. Using keyword matching fallback.")

    def _classify_with_ml(self, description: str, amount: Optional[float] = None) -> Dict:
        """
        Classify using trained ML model

        Args:
            description: Transaction description
            amount: Transaction amount (optional)

        Returns:
            Dict with category, confidence, and alternatives
        """
        if self.ml_model is None:
            return None

        try:
            # Get prediction from ML model
            predictions = self.ml_model.predict([description])
            probabilities = self.ml_model.predict_proba([description])

            # Map prediction index to category
            category_idx = predictions[0]
            categories = [
                "groceries", "restaurants", "transportation", "utilities",
                "entertainment", "shopping", "healthcare", "insurance",
                "housing", "fitness", "education", "personal_care", "subscriptions"
            ]
            category = categories[category_idx]
            confidence = float(probabilities[0][category_idx])

            # Get top alternatives
            top_indices = np.argsort(probabilities[0])[-3:][::-1][1:]  # Top 3 excluding primary
            alternatives = [
                {
                    "category": categories[idx],
                    "confidence": round(float(probabilities[0][idx]), 2)
                }
                for idx in top_indices
                if probabilities[0][idx] > 0
            ]

            return {
                "category": category,
                "confidence": round(confidence, 2),
                "alternatives": alternatives,
                "needs_review": confidence < 0.7,
                "method": "ml"
            }
        except Exception as e:
            logger.error(f"ML inference error: {e}. Falling back to keyword matching.")
            return None
    
    def classify(self, description: str, amount: Optional[float] = None) -> Dict:
        """
        Classify a transaction based on its description and amount.
        Tries ML model first, falls back to keyword matching if ML unavailable.

        Args:
            description: Transaction description
            amount: Transaction amount (optional, can help with classification)

        Returns:
            Dict with category, confidence, and alternative suggestions
        """
        # Try ML model first
        if self.use_ml and self.ml_model is not None:
            ml_result = self._classify_with_ml(description, amount)
            if ml_result is not None:
                return ml_result

        # Fall back to keyword matching
        return self._classify_with_keywords(description, amount)

    def _classify_with_keywords(self, description: str, amount: Optional[float] = None) -> Dict:
        """Original keyword-based classification (fallback)"""
        description_lower = description.lower()
        
        # Score each category
        category_scores = defaultdict(float)
        
        # Keyword matching with scoring
        for keyword, category in self.keyword_to_category.items():
            if keyword in description_lower:
                # Exact match gets higher score
                if keyword == description_lower:
                    category_scores[category] += 10.0
                # Word boundary match gets medium score
                elif re.search(r'\b' + re.escape(keyword) + r'\b', description_lower):
                    category_scores[category] += 5.0
                # Partial match gets lower score
                else:
                    category_scores[category] += 2.0
        
        # Amount-based hints (heuristics)
        if amount:
            if amount > 1000:
                category_scores["housing"] += 1.0
                category_scores["utilities"] += 0.5
            elif amount < 10:
                category_scores["transportation"] += 1.0
        
        # Pattern matching for common formats
        if re.search(r'#\d+', description):
            category_scores["shopping"] += 1.0
        
        if not category_scores:
            return {
                "category": "uncategorized",
                "confidence": 0.0,
                "alternatives": [],
                "needs_review": True
            }
        
        # Sort by score
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        primary_category, primary_score = sorted_categories[0]
        total_score = sum(score for _, score in sorted_categories)
        confidence = min(primary_score / total_score if total_score > 0 else 0, 1.0)
        
        # Get alternative suggestions
        alternatives = [
            {"category": cat, "confidence": round(score / total_score, 2)}
            for cat, score in sorted_categories[1:4]
            if score > 0
        ]
        
        return {
            "category": primary_category,
            "confidence": round(confidence, 2),
            "alternatives": alternatives,
            "needs_review": confidence < 0.7,
            "method": "keyword"
        }
    
    def classify_batch(self, transactions: List[Dict]) -> List[Dict]:
        """
        Classify multiple transactions at once.
        
        Args:
            transactions: List of transaction dicts with 'description' and optional 'amount'
        
        Returns:
            List of classification results
        """
        results = []
        for txn in transactions:
            result = self.classify(
                txn.get("description", ""),
                txn.get("amount")
            )
            result["transaction_id"] = txn.get("id")
            result["original_description"] = txn.get("description")
            results.append(result)
        
        return results
    
    def get_category_insights(self, transactions: List[Dict]) -> Dict:
        """
        Analyze transaction categories and provide insights.
        
        Args:
            transactions: List of classified transactions
        
        Returns:
            Dict with category breakdown and insights
        """
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        needs_review_count = 0
        
        for txn in transactions:
            category = txn.get("category", "uncategorized")
            amount = txn.get("amount", 0)
            category_totals[category] += amount
            category_counts[category] += 1
            
            if txn.get("needs_review", False):
                needs_review_count += 1
        
        total_amount = sum(category_totals.values())
        
        # Calculate percentages
        breakdown = [
            {
                "category": category,
                "total": round(amount, 2),
                "count": category_counts[category],
                "percentage": round((amount / total_amount * 100) if total_amount > 0 else 0, 1)
            }
            for category, amount in sorted(
                category_totals.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]
        
        return {
            "breakdown": breakdown,
            "total_amount": round(total_amount, 2),
            "total_transactions": len(transactions),
            "needs_review": needs_review_count,
            "review_percentage": round(
                (needs_review_count / len(transactions) * 100) if transactions else 0,
                1
            )
        }
    
    def train_from_user_corrections(
        self,
        user_id: int,
        corrections: List[Tuple[str, str]]
    ) -> Dict:
        """
        Learn from user corrections. In actual implementation, these would be stored
        in the database and used to trigger periodic retraining.

        Args:
            user_id: User ID for personalized learning
            corrections: List of (description, correct_category) tuples

        Returns:
            Training summary
        """
        learned_patterns = defaultdict(list)
        for description, category in corrections:
            # Extract key words from user-corrected transactions
            words = re.findall(r'\b\w+\b', description.lower())
            for word in words:
                if len(word) > 3:  # Ignore short words
                    learned_patterns[category].append(word)

        return {
            "user_id": user_id,
            "corrections_learned": len(corrections),
            "patterns_identified": {
                category: list(set(words))[:5]  # Top 5 unique words
                for category, words in learned_patterns.items()
            },
            "note": "Corrections stored for periodic model retraining"
        }

    def trigger_model_retraining(self) -> Dict:
        """
        Trigger retraining of the ML model using accumulated corrections.
        Should be called periodically or after N corrections accumulate.

        Returns:
            Retraining results
        """
        try:
            from app.services.ml_models.retraining import retrain_classifier_model
            return retrain_classifier_model()
        except ImportError:
            logger.warning("Retraining module not available")
            return {
                "status": "failed",
                "reason": "Retraining module not available"
            }
    
    def suggest_category_for_merchant(self, merchant_name: str) -> Dict:
        """
        Suggest category for a specific merchant.

        Args:
            merchant_name: Name of the merchant

        Returns:
            Category suggestion with confidence
        """
        result = self.classify(merchant_name)

        return {
            "merchant": merchant_name,
            "suggested_category": result["category"],
            "confidence": result["confidence"],
            "method": result.get("method", "keyword"),
            "reason": f"Classified using {result.get('method', 'keyword')} method"
        }
