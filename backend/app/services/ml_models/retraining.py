"""
ML Model Retraining Pipeline
Handles periodic retraining of the expense classifier using accumulated corrections
"""
import logging
from typing import Dict, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


def retrain_classifier_model(use_corrections: bool = True) -> Dict:
    """
    Retrain the ML classifier using transactions and user corrections

    Args:
        use_corrections: Whether to include user-corrected transactions

    Returns:
        Retraining results with metrics
    """
    try:
        # Import here to avoid circular imports
        from sqlalchemy.orm import Session
        from app.models.database import SessionLocal
        from app.models.finance import Transaction, ClassificationFeedback
        from app.services.analytics.expense_classifier import ExpenseClassifier
        from app.services.ml_models.training import MLExpenseClassifierTrainer

        db: Session = SessionLocal()
        trainer = MLExpenseClassifierTrainer()
        keyword_classifier = ExpenseClassifier()

        try:
            # Query all transactions with status checks
            transactions = db.query(Transaction).all()

            if len(transactions) < 50:
                logger.warning(
                    f"Only {len(transactions)} transactions available. "
                    "Need at least 50 for meaningful training."
                )
                return {
                    "status": "skipped",
                    "reason": "Insufficient training data",
                    "transactions_count": len(transactions)
                }

            # Prepare training data
            descriptions, category_indices, confidence_scores = trainer.prepare_training_data(
                [
                    {
                        "description": t.description,
                        "amount": t.amount
                    }
                    for t in transactions
                ],
                keyword_classifier=keyword_classifier
            )

            if len(descriptions) < 50:
                logger.warning(
                    f"Only {len(descriptions)} high-confidence samples available after filtering."
                )
                return {
                    "status": "skipped",
                    "reason": "Insufficient high-confidence training samples",
                    "samples_prepared": len(descriptions),
                    "total_transactions": len(transactions)
                }

            # Train the model
            metrics = trainer.train(descriptions, category_indices, sample_weights=confidence_scores)

            # Generate new version number
            latest_version = trainer.get_latest_model_version()
            if latest_version:
                version_num = int(latest_version.replace("v", "")) + 1
            else:
                version_num = 1
            new_version = f"v{version_num}"

            # Save the model
            model_path = trainer.save_model(new_version)

            # Mark corrections as used in training
            if use_corrections:
                db.query(ClassificationFeedback).update(
                    {ClassificationFeedback.is_used_in_training: True}
                )
                db.commit()
                logger.info("Marked corrections as used in training")

            return {
                "status": "success",
                "model_version": new_version,
                "model_path": model_path,
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error during retraining: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
        finally:
            db.close()

    except ImportError as e:
        logger.error(f"Import error in retraining: {e}")
        return {
            "status": "failed",
            "reason": f"Import error: {e}"
        }


def get_model_performance_metrics() -> Dict:
    """
    Get performance metrics for the current model

    Returns:
        Model performance information
    """
    try:
        from app.services.ml_models.training import MLExpenseClassifierTrainer
        import os

        trainer = MLExpenseClassifierTrainer()
        latest_version = trainer.get_latest_model_version()

        if not latest_version:
            return {"status": "no_model", "message": "No trained model found"}

        if not trainer.load_model(latest_version):
            return {"status": "error", "message": "Could not load model"}

        model_dir = trainer.get_latest_model_version()
        metadata_path = os.path.join(
            os.path.dirname(__file__),
            f"../../ml_models/classifier_{latest_version}_metadata.json"
        )

        if os.path.exists(metadata_path):
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            return {
                "status": "success",
                "version": latest_version,
                "metadata": metadata
            }

        return {
            "status": "success",
            "version": latest_version,
            "message": "Model loaded successfully"
        }

    except Exception as e:
        logger.error(f"Error getting model metrics: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
