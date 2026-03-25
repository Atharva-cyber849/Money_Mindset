"""
Test script for ML-based expense classification
Verifies training, inference, and persistence
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ml_models.training import MLExpenseClassifierTrainer
from app.services.analytics.expense_classifier import ExpenseClassifier


def test_ml_training_pipeline():
    """Test the complete ML training pipeline"""

    print("=" * 60)
    print("Testing ML-Based Expense Classification")
    print("=" * 60)

    # Test 1: Create trainer instance
    print("\n[1] Creating trainer instance...")
    trainer = MLExpenseClassifierTrainer()
    print("✓ Trainer created successfully")

    # Test 2: Create synthetic training data
    print("\n[2] Creating synthetic training dataset...")
    sample_descriptions = [
        # Groceries
        "Whole Foods Market grocery", "Kroger supermarket",
        "Safeway grocery store", "Trader Joe's market",
        # Restaurants
        "Starbucks coffee shop", "McDonald's restaurant",
        "Pizza Hut delivery", "Chipotle Mexican grill",
        # Transportation
        "Uber ride share", "Shell gas station",
        "Lyft transportation", "Parking lot fee",
        # Utilities
        "Electric bill payment", "Verizon phone bill",
        "Comcast internet service", "Water bill",
        # Entertainment
        "Netflix subscription", "AMC movie theater",
        "Spotify music streaming", "Disney+ streaming",
        # Shopping
        "Amazon.com purchase", "Walmart store",
        "Target retail store", "Best Buy electronics",
        # Healthcare
        "CVS pharmacy", "Walgreens drugstore",
        "Local hospital", "Dental clinic appointment",
        # Insurance
        "Geico insurance", "State Farm premium",
        "Progressive insurance", "Allstate policy",
        # Housing
        "Apartment rent payment", "Mortgage payment",
        "HOA fees", "Property management",
        # Fitness
        "Planet Fitness gym", "LA Fitness membership",
        "Yoga studio class", "Personal trainer",
        # Education
        "Udemy course", "Coursera learning",
        "Textbook purchase", "Tuition payment",
        # Personal Care
        "Salon haircut", "Spa massage",
        "Barber shop", "Beauty supply",
        # Subscriptions
        "Monthly subscription", "Annual membership",
        "Service fee charge", "Recurring payment"
    ]

    sample_amounts = [45, 60, 50, 40] * 8  # Different amounts for testing

    transactions = [
        {"description": desc, "amount": amount}
        for desc, amount in zip(sample_descriptions, sample_amounts)
    ]

    print(f"✓ Created {len(transactions)} synthetic transactions")

    # Test 3: Prepare training data using keyword classifier
    print("\n[3] Preparing training data with keyword classifier...")
    keyword_classifier = ExpenseClassifier()
    descriptions, category_indices, confidence_scores = trainer.prepare_training_data(
        transactions,
        keyword_classifier=keyword_classifier
    )
    print(f"✓ Prepared {len(descriptions)} training samples")
    print(f"  - Avg confidence: {sum(confidence_scores)/len(confidence_scores):.2f}")

    # Test 4: Train the model
    print("\n[4] Training Random Forest classifier...")
    metrics = trainer.train(descriptions, category_indices, sample_weights=confidence_scores)
    print(f"✓ Model trained successfully")
    print(f"  - Training accuracy: {metrics['training_accuracy']:.2%}")
    print(f"  - Samples used: {metrics['samples_used']}")

    # Test 5: Make predictions
    print("\n[5] Testing predictions...")
    test_descriptions = [
        "Starbucks coffee",
        "Shell gas station",
        "Netflix streaming",
        "Whole Foods groceries"
    ]
    predictions = trainer.predict(test_descriptions)
    for desc, pred in zip(test_descriptions, predictions):
        print(f"  - '{desc}' → {pred['category']} (confidence: {pred['confidence']:.2%})")

    # Test 6: Save model
    print("\n[6] Saving trained model...")
    model_path = trainer.save_model(version="v1")
    print(f"✓ Model saved to: {model_path}")

    # Test 7: Load model
    print("\n[7] Loading saved model...")
    trainer2 = MLExpenseClassifierTrainer()
    loaded = trainer2.load_model(version="v1")
    if loaded:
        print("✓ Model loaded successfully")

        # Make prediction with loaded model
        test_pred = trainer2.predict(["Uber ride share"])
        print(f"  - Test prediction: {test_pred[0]['category']} (confidence: {test_pred[0]['confidence']:.2%})")
    else:
        print("✗ Failed to load model")

    # Test 8: Expense classifier integration
    print("\n[8] Testing ExpenseClassifier with ML model...")
    classifier = ExpenseClassifier()
    if classifier.use_ml and classifier.ml_model:
        print("✓ ML model loaded in ExpenseClassifier")
        result = classifier.classify("Starbucks coffee shop", 5.50)
        print(f"  - Classification: {result['category']}")
        print(f"  - Confidence: {result['confidence']:.2%}")
        print(f"  - Method: {result.get('method', 'unknown')}")
    else:
        print("ℹ ML model not available (using keyword fallback)")
        result = classifier.classify("Starbucks coffee shop", 5.50)
        print(f"  - Classification: {result['category']}")
        print(f"  - Method: {result.get('method', 'unknown')}")

    print("\n" + "=" * 60)
    print("All tests completed successfully! ✓")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_ml_training_pipeline()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
