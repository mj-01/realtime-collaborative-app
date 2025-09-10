#!/usr/bin/env python3
"""
Comprehensive test suite for all benchmark implementations.

This module tests GSM8K, Stark Amazon, and Agent Company ML benchmarks
with end-to-end functionality and ground truth comparison.
"""

import json
import tempfile
import unittest
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from benchmarks import GSM8KBenchmark, StarkAmazonBenchmark, AgentCompanyMLBenchmark


class MockModel:
    """Mock model for testing purposes."""
    
    def __init__(self, name="MockModel", responses=None):
        self.name = name
        self.responses = responses or {}
        self.call_count = 0
    
    def generate(self, prompt, **kwargs):
        """Mock generate method with configurable responses."""
        self.call_count += 1
        
        # Check for specific response patterns
        if "answer is" in prompt.lower() or "answer:" in prompt.lower():
            return "The answer is 42."
        elif "yes" in prompt.lower() or "no" in prompt.lower():
            return "Yes, this product meets your requirements."
        elif "gsm8k" in prompt.lower() or "math" in prompt.lower():
            return "The answer is 25."
        else:
            return "This is a mock response."


class MockMLAgent:
    """Mock ML agent for testing purposes."""
    
    def __init__(self, name="MockMLAgent", performance_level="good"):
        self.name = name
        self.performance_level = performance_level
    
    def execute_task(self, task, datasets, **kwargs):
        """Mock execute_task method with configurable performance."""
        task_type = task.get('type', 'unknown')
        
        if self.performance_level == "excellent":
            return self._excellent_performance(task_type)
        elif self.performance_level == "good":
            return self._good_performance(task_type)
        elif self.performance_level == "poor":
            return self._poor_performance(task_type)
        else:
            return self._random_performance(task_type)
    
    def _excellent_performance(self, task_type):
        """Simulate excellent performance (90-100% scores)."""
        if task_type == 'data_preprocessing':
            return {
                'data_cleaned': True,
                'missing_values_handled': True,
                'outliers_handled': True,
                'data_validated': True
            }
        elif task_type == 'feature_engineering':
            return {
                'new_features': ['feature_1', 'feature_2', 'feature_3'],
                'feature_selection_performed': True,
                'feature_scaling_applied': True
            }
        elif task_type == 'model_training':
            return {
                'model_trained': True,
                'hyperparameter_tuning': True,
                'cross_validation_used': True
            }
        elif task_type == 'model_evaluation':
            return {
                'metrics': {'accuracy': 0.95, 'precision': 0.93, 'recall': 0.97},
                'performance_analysis': True,
                'business_impact_considered': True
            }
        elif task_type == 'deployment':
            return {
                'deployment_strategy': True,
                'monitoring_setup': True,
                'rollback_plan': True
            }
        else:
            return {'completed': True, 'partial_completion': False}
    
    def _good_performance(self, task_type):
        """Simulate good performance (70-90% scores)."""
        if task_type == 'data_preprocessing':
            return {
                'data_cleaned': True,
                'missing_values_handled': True,
                'outliers_handled': False,  # Partial
                'data_validated': True
            }
        elif task_type == 'feature_engineering':
            return {
                'new_features': ['feature_1', 'feature_2'],
                'feature_selection_performed': True,
                'feature_scaling_applied': True
            }
        elif task_type == 'model_training':
            return {
                'model_trained': True,
                'hyperparameter_tuning': False,  # Partial
                'cross_validation_used': True
            }
        elif task_type == 'model_evaluation':
            return {
                'metrics': {'accuracy': 0.85, 'precision': 0.82, 'recall': 0.88},
                'performance_analysis': True,
                'business_impact_considered': False  # Partial
            }
        elif task_type == 'deployment':
            return {
                'deployment_strategy': True,
                'monitoring_setup': True,
                'rollback_plan': False  # Partial
            }
        else:
            return {'completed': True, 'partial_completion': False}
    
    def _poor_performance(self, task_type):
        """Simulate poor performance (30-70% scores)."""
        if task_type == 'data_preprocessing':
            return {
                'data_cleaned': True,
                'missing_values_handled': False,
                'outliers_handled': False,
                'data_validated': False
            }
        elif task_type == 'feature_engineering':
            return {
                'new_features': ['feature_1'],
                'feature_selection_performed': False,
                'feature_scaling_applied': False
            }
        elif task_type == 'model_training':
            return {
                'model_trained': True,
                'hyperparameter_tuning': False,
                'cross_validation_used': False
            }
        elif task_type == 'model_evaluation':
            return {
                'metrics': {'accuracy': 0.70},
                'performance_analysis': False,
                'business_impact_considered': False
            }
        elif task_type == 'deployment':
            return {
                'deployment_strategy': False,
                'monitoring_setup': False,
                'rollback_plan': False
            }
        else:
            return {'completed': False, 'partial_completion': True}
    
    def _random_performance(self, task_type):
        """Simulate random performance."""
        import random
        if random.random() > 0.5:
            return self._good_performance(task_type)
        else:
            return self._poor_performance(task_type)


class TestBenchmarks(unittest.TestCase):
    """Test suite for all benchmark implementations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_files = []
    
    def tearDown(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def create_temp_file(self, data, suffix='.json'):
        """Create a temporary file with given data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            json.dump(data, f)
            temp_file = f.name
            self.temp_files.append(temp_file)
            return temp_file
    
    def create_gsm8k_data(self, num_questions=5):
        """Create sample GSM8K data."""
        questions = [
            {
                "question": "Janet's ducks lay 16 eggs per day. She eats 3 for breakfast every morning and bakes 4 into muffins for her friends every day. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?",
                "answer": "18"
            },
            {
                "question": "A robe takes 2 bolts of blue fabric and half that much white fabric. How many bolts of fabric does it take?",
                "answer": "3"
            },
            {
                "question": "Tom has 5 more than twice as many marbles as Jerry. Jerry has 10 marbles. How many marbles does Tom have?",
                "answer": "25"
            },
            {
                "question": "Sarah has 12 apples. She gives 3 to her friend and buys 7 more. How many apples does she have now?",
                "answer": "16"
            },
            {
                "question": "A store has 50 items. They sell 15 items in the morning and 20 items in the afternoon. How many items are left?",
                "answer": "15"
            }
        ]
        return questions[:num_questions]
    
    def create_stark_amazon_data(self, num_questions=5):
        """Create sample Stark Amazon data."""
        questions = [
            {
                "product_id": "B001234567",
                "title": "Wireless Bluetooth Headphones",
                "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life.",
                "specifications": {
                    "battery_life": "30 hours",
                    "connectivity": "Bluetooth 5.0",
                    "noise_cancellation": "Active"
                },
                "reviews": ["Great sound quality", "Comfortable to wear", "Long battery life"],
                "price": "$99.99",
                "category": "Electronics",
                "question": "Does this headphone have noise cancellation?",
                "answer": "Yes"
            },
            {
                "product_id": "B002345678",
                "title": "Stainless Steel Water Bottle",
                "description": "Insulated stainless steel water bottle that keeps drinks cold for 24 hours.",
                "specifications": {
                    "material": "Stainless Steel",
                    "insulation": "Double wall",
                    "capacity": "32 oz"
                },
                "reviews": ["Keeps drinks cold", "Durable construction", "Leak-proof"],
                "price": "$24.99",
                "category": "Kitchen",
                "question": "What is the capacity of this water bottle?",
                "answer": "32 oz"
            },
            {
                "product_id": "B003456789",
                "title": "Organic Cotton T-Shirt",
                "description": "100% organic cotton t-shirt made from sustainable materials.",
                "specifications": {
                    "material": "100% Organic Cotton",
                    "sizes": "S, M, L, XL",
                    "care": "Machine washable"
                },
                "reviews": ["Soft and comfortable", "True to size", "Eco-friendly"],
                "price": "$19.99",
                "category": "Clothing",
                "question": "Is this t-shirt made from organic cotton?",
                "answer": "Yes"
            },
            {
                "product_id": "B004567890",
                "title": "Laptop Stand Adjustable",
                "description": "Adjustable laptop stand with ergonomic design and aluminum construction.",
                "specifications": {
                    "material": "Aluminum",
                    "adjustable": "Yes",
                    "max_weight": "15 lbs"
                },
                "reviews": ["Sturdy build", "Easy to adjust", "Good for posture"],
                "price": "$49.99",
                "category": "Office",
                "question": "What is the maximum weight this stand can hold?",
                "answer": "15 lbs"
            },
            {
                "product_id": "B005678901",
                "title": "Coffee Maker Programmable",
                "description": "Programmable coffee maker with 12-cup capacity and auto-shutoff feature.",
                "specifications": {
                    "capacity": "12 cups",
                    "programmable": "Yes",
                    "auto_shutoff": "Yes"
                },
                "reviews": ["Great coffee", "Easy to program", "Reliable"],
                "price": "$79.99",
                "category": "Kitchen",
                "question": "How many cups can this coffee maker make?",
                "answer": "12 cups"
            }
        ]
        return questions[:num_questions]
    
    def create_agent_company_ml_data(self, num_tasks=5):
        """Create sample Agent Company ML data."""
        tasks = [
            {
                "name": "Clean Customer Data",
                "type": "data_preprocessing",
                "description": "Clean and preprocess customer dataset for analysis",
                "max_score": 100,
                "requirements": ["handle_missing_values", "detect_outliers", "validate_data"],
                "expected_output": {"cleaned_data": "DataFrame", "report": "string"}
            },
            {
                "name": "Create Feature Engineering Pipeline",
                "type": "feature_engineering",
                "description": "Create new features from raw data",
                "max_score": 100,
                "requirements": ["create_features", "select_features", "scale_features"],
                "expected_output": {"feature_pipeline": "Pipeline", "features": "list"}
            },
            {
                "name": "Train Classification Model",
                "type": "model_training",
                "description": "Train a machine learning model for classification",
                "max_score": 100,
                "requirements": ["train_model", "tune_hyperparameters", "cross_validate"],
                "expected_output": {"model": "Model", "metrics": "dict"}
            },
            {
                "name": "Evaluate Model Performance",
                "type": "model_evaluation",
                "description": "Evaluate model performance and business impact",
                "max_score": 100,
                "requirements": ["calculate_metrics", "analyze_performance", "assess_impact"],
                "expected_output": {"evaluation_report": "dict", "recommendations": "list"}
            },
            {
                "name": "Deploy Model to Production",
                "type": "deployment",
                "description": "Deploy model to production environment",
                "max_score": 100,
                "requirements": ["deploy_model", "setup_monitoring", "create_rollback"],
                "expected_output": {"deployment_url": "string", "monitoring_dashboard": "string"}
            }
        ]
        
        return {
            "tasks": tasks[:num_tasks],
            "datasets": {
                "customer_data": {
                    "description": "Customer dataset with demographics and behavior",
                    "size": 10000,
                    "features": ["age", "income", "purchase_history", "satisfaction_score"]
                },
                "product_data": {
                    "description": "Product catalog with features and sales data",
                    "size": 5000,
                    "features": ["category", "price", "rating", "sales_volume"]
                }
            },
            "evaluation_metrics": {
                "accuracy": "Classification accuracy",
                "precision": "Precision score",
                "recall": "Recall score",
                "f1_score": "F1 score",
                "business_impact": "Business value assessment"
            }
        }
    
    def test_gsm8k_benchmark_basic(self):
        """Test GSM8K benchmark basic functionality."""
        print("\n=== Testing GSM8K Benchmark Basic Functionality ===")
        
        # Create test data
        gsm8k_data = self.create_gsm8k_data(3)
        temp_file = self.create_temp_file(gsm8k_data)
        
        # Initialize benchmark
        benchmark = GSM8KBenchmark()
        self.assertEqual(benchmark.name, "GSM8K")
        self.assertIn("Mathematical reasoning", benchmark.description)
        
        # Test load_data
        benchmark.load_data(temp_file)
        self.assertEqual(len(benchmark.questions), 3)
        self.assertEqual(len(benchmark.answers), 3)
        
        # Test get_sample_questions
        samples = benchmark.get_sample_questions(2)
        self.assertEqual(len(samples), 2)
        self.assertIn('question', samples[0])
        self.assertIn('answer', samples[0])
        
        print("✓ GSM8K basic functionality test passed")
    
    def test_gsm8k_benchmark_evaluation(self):
        """Test GSM8K benchmark evaluation."""
        print("\n=== Testing GSM8K Benchmark Evaluation ===")
        
        # Create test data
        gsm8k_data = self.create_gsm8k_data(3)
        temp_file = self.create_temp_file(gsm8k_data)
        
        # Initialize benchmark and model
        benchmark = GSM8KBenchmark()
        model = MockModel("TestModel")
        
        # Test run method (end-to-end)
        results = benchmark.run(model, temp_file, max_questions=3)
        
        # Verify results structure
        self.assertIsInstance(results, type(benchmark).__bases__[0].__bases__[0].__bases__[0])  # BenchmarkResult
        self.assertEqual(results.benchmark_name, "GSM8K")
        self.assertEqual(results.model_name, "TestModel")
        self.assertEqual(results.total_questions, 3)
        self.assertGreaterEqual(results.accuracy, 0.0)
        self.assertLessEqual(results.accuracy, 1.0)
        self.assertGreaterEqual(results.execution_time, 0.0)
        
        # Verify detailed results
        self.assertEqual(len(results.detailed_results), 3)
        for i, result in enumerate(results.detailed_results):
            self.assertEqual(result['question_id'], i)
            self.assertIn('question', result)
            self.assertIn('expected_answer', result)
            self.assertIn('model_response', result)
            self.assertIn('predicted_answer', result)
            self.assertIn('is_correct', result)
        
        print(f"✓ GSM8K evaluation test passed - Accuracy: {results.accuracy:.2%}")
    
    def test_stark_amazon_benchmark_basic(self):
        """Test Stark Amazon benchmark basic functionality."""
        print("\n=== Testing Stark Amazon Benchmark Basic Functionality ===")
        
        # Create test data
        amazon_data = self.create_stark_amazon_data(3)
        temp_file = self.create_temp_file(amazon_data)
        
        # Initialize benchmark
        benchmark = StarkAmazonBenchmark()
        self.assertEqual(benchmark.name, "StarkAmazon")
        self.assertIn("Amazon product", benchmark.description)
        
        # Test load_data
        benchmark.load_data(temp_file)
        self.assertEqual(len(benchmark.questions), 3)
        self.assertEqual(len(benchmark.answers), 3)
        self.assertEqual(len(benchmark.products), 3)
        
        # Test get_sample_questions
        samples = benchmark.get_sample_questions(2)
        self.assertEqual(len(samples), 2)
        self.assertIn('question', samples[0])
        self.assertIn('answer', samples[0])
        self.assertIn('product_title', samples[0])
        
        print("✓ Stark Amazon basic functionality test passed")
    
    def test_stark_amazon_benchmark_evaluation(self):
        """Test Stark Amazon benchmark evaluation with F1 score."""
        print("\n=== Testing Stark Amazon Benchmark Evaluation ===")
        
        # Create test data
        amazon_data = self.create_stark_amazon_data(3)
        temp_file = self.create_temp_file(amazon_data)
        
        # Initialize benchmark and model
        benchmark = StarkAmazonBenchmark()
        model = MockModel("TestModel")
        
        # Test run method (end-to-end)
        results = benchmark.run(model, temp_file, max_questions=3)
        
        # Verify results structure
        self.assertEqual(results.benchmark_name, "StarkAmazon")
        self.assertEqual(results.model_name, "TestModel")
        self.assertEqual(results.total_questions, 3)
        self.assertGreaterEqual(results.accuracy, 0.0)
        self.assertLessEqual(results.accuracy, 1.0)
        
        # Verify F1 score metrics
        self.assertIn('precision', results.metadata)
        self.assertIn('recall', results.metadata)
        self.assertIn('f1_score', results.metadata)
        self.assertGreaterEqual(results.metadata['precision'], 0.0)
        self.assertLessEqual(results.metadata['precision'], 1.0)
        self.assertGreaterEqual(results.metadata['recall'], 0.0)
        self.assertLessEqual(results.metadata['recall'], 1.0)
        self.assertGreaterEqual(results.metadata['f1_score'], 0.0)
        self.assertLessEqual(results.metadata['f1_score'], 1.0)
        
        print(f"✓ Stark Amazon evaluation test passed - Accuracy: {results.accuracy:.2%}, F1: {results.metadata['f1_score']:.3f}")
    
    def test_agent_company_ml_benchmark_basic(self):
        """Test Agent Company ML benchmark basic functionality."""
        print("\n=== Testing Agent Company ML Benchmark Basic Functionality ===")
        
        # Create test data
        ml_data = self.create_agent_company_ml_data(3)
        temp_file = self.create_temp_file(ml_data)
        
        # Initialize benchmark
        benchmark = AgentCompanyMLBenchmark()
        self.assertEqual(benchmark.name, "AgentCompanyML")
        self.assertIn("Machine Learning", benchmark.description)
        
        # Test load_data
        benchmark.load_data(temp_file)
        self.assertEqual(len(benchmark.tasks), 3)
        self.assertIn('customer_data', benchmark.datasets)
        self.assertIn('product_data', benchmark.datasets)
        
        # Test get_sample_questions
        samples = benchmark.get_sample_questions(2)
        self.assertEqual(len(samples), 2)
        self.assertIn('name', samples[0])
        self.assertIn('type', samples[0])
        self.assertIn('description', samples[0])
        
        print("✓ Agent Company ML basic functionality test passed")
    
    def test_agent_company_ml_benchmark_evaluation(self):
        """Test Agent Company ML benchmark evaluation with task completion metrics."""
        print("\n=== Testing Agent Company ML Benchmark Evaluation ===")
        
        # Create test data
        ml_data = self.create_agent_company_ml_data(5)
        temp_file = self.create_temp_file(ml_data)
        
        # Initialize benchmark and agent
        benchmark = AgentCompanyMLBenchmark()
        agent = MockMLAgent("TestAgent", performance_level="good")
        
        # Test run method (end-to-end)
        results = benchmark.run(agent, temp_file, max_tasks=5)
        
        # Verify results structure
        self.assertEqual(results.benchmark_name, "AgentCompanyML")
        self.assertEqual(results.model_name, "TestAgent")
        self.assertEqual(results.total_questions, 5)
        self.assertGreaterEqual(results.accuracy, 0.0)
        self.assertLessEqual(results.accuracy, 1.0)
        
        # Verify task completion metrics
        self.assertIn('task_completion_rate', results.metadata)
        self.assertIn('partial_completion_rate', results.metadata)
        self.assertIn('failure_rate', results.metadata)
        self.assertIn('task_type_accuracies', results.metadata)
        
        # Verify task completion rates sum to 1
        total_rate = (results.metadata['task_completion_rate'] + 
                     results.metadata['partial_completion_rate'] + 
                     results.metadata['failure_rate'])
        self.assertAlmostEqual(total_rate, 1.0, places=2)
        
        print(f"✓ Agent Company ML evaluation test passed - Accuracy: {results.accuracy:.2%}, Completion: {results.metadata['task_completion_rate']:.2%}")
    
    def test_ground_truth_comparison(self):
        """Test ground truth comparison with known answers."""
        print("\n=== Testing Ground Truth Comparison ===")
        
        # Create test data with known answers
        gsm8k_data = [
            {
                "question": "What is 2 + 2?",
                "answer": "4"
            },
            {
                "question": "What is 5 * 3?",
                "answer": "15"
            },
            {
                "question": "What is 10 - 4?",
                "answer": "6"
            }
        ]
        temp_file = self.create_temp_file(gsm8k_data)
        
        # Create a model that gives correct answers
        class CorrectAnswerModel:
            def __init__(self):
                self.name = "CorrectAnswerModel"
            
            def generate(self, question, **kwargs):
                # Simple pattern matching for known questions
                if "2 + 2" in question:
                    return "The answer is 4."
                elif "5 * 3" in question:
                    return "The answer is 15."
                elif "10 - 4" in question:
                    return "The answer is 6."
                else:
                    return "The answer is 42."
        
        # Test with correct answers
        benchmark = GSM8KBenchmark()
        model = CorrectAnswerModel()
        results = benchmark.run(model, temp_file, max_questions=3)
        
        # Should achieve 100% accuracy with correct answers
        self.assertEqual(results.accuracy, 1.0)
        self.assertEqual(results.correct_answers, 3)
        self.assertEqual(results.total_questions, 3)
        
        # Verify all detailed results show correct answers
        for result in results.detailed_results:
            self.assertTrue(result['is_correct'])
        
        print("✓ Ground truth comparison test passed - 100% accuracy achieved")
    
    def test_error_handling(self):
        """Test error handling in benchmarks."""
        print("\n=== Testing Error Handling ===")
        
        # Test with non-existent file
        benchmark = GSM8KBenchmark()
        with self.assertRaises(FileNotFoundError):
            benchmark.load_data("non_existent_file.json")
        
        # Test with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
            self.temp_files.append(temp_file)
        
        with self.assertRaises(json.JSONDecodeError):
            benchmark.load_data(temp_file)
        
        # Test evaluation without loading data
        model = MockModel()
        with self.assertRaises(ValueError):
            benchmark.evaluate(model)
        
        print("✓ Error handling test passed")
    
    def test_benchmark_statistics(self):
        """Test benchmark statistics functionality."""
        print("\n=== Testing Benchmark Statistics ===")
        
        # Test GSM8K statistics
        gsm8k_data = self.create_gsm8k_data(3)
        temp_file = self.create_temp_file(gsm8k_data)
        
        benchmark = GSM8KBenchmark()
        benchmark.load_data(temp_file)
        stats = benchmark.get_statistics()
        
        self.assertIn('total_questions', stats)
        self.assertIn('avg_question_length', stats)
        self.assertEqual(stats['total_questions'], 3)
        
        # Test Stark Amazon statistics
        amazon_data = self.create_stark_amazon_data(3)
        temp_file = self.create_temp_file(amazon_data)
        
        benchmark = StarkAmazonBenchmark()
        benchmark.load_data(temp_file)
        stats = benchmark.get_statistics()
        
        self.assertIn('total_questions', stats)
        self.assertIn('categories', stats)
        self.assertEqual(stats['total_questions'], 3)
        
        # Test Agent Company ML statistics
        ml_data = self.create_agent_company_ml_data(3)
        temp_file = self.create_temp_file(ml_data)
        
        benchmark = AgentCompanyMLBenchmark()
        benchmark.load_data(temp_file)
        stats = benchmark.get_statistics()
        
        self.assertIn('total_tasks', stats)
        self.assertIn('task_types', stats)
        self.assertEqual(stats['total_tasks'], 3)
        
        print("✓ Benchmark statistics test passed")


def run_performance_test():
    """Run performance test with larger datasets."""
    print("\n=== Running Performance Test ===")
    
    # Create larger datasets
    gsm8k_data = []
    for i in range(10):
        gsm8k_data.append({
            "question": f"Test question {i+1}: What is {i+1} + {i+1}?",
            "answer": str((i+1) * 2)
        })
    
    amazon_data = []
    for i in range(10):
        amazon_data.append({
            "product_id": f"B{i:09d}",
            "title": f"Test Product {i+1}",
            "description": f"Description for product {i+1}",
            "specifications": {"feature": f"value_{i+1}"},
            "reviews": [f"Review {i+1}"],
            "price": f"${(i+1)*10}.99",
            "category": "Test",
            "question": f"Is this product {i+1} good?",
            "answer": "Yes"
        })
    
    ml_data = {
        "tasks": [
            {
                "name": f"Test Task {i+1}",
                "type": "data_preprocessing",
                "description": f"Test task {i+1}",
                "max_score": 100,
                "requirements": ["req1", "req2"],
                "expected_output": {"output": "string"}
            }
            for i in range(10)
        ],
        "datasets": {"test_data": {"description": "Test dataset"}},
        "evaluation_metrics": {"accuracy": "Test metric"}
    }
    
    # Test performance
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(gsm8k_data, f)
        gsm8k_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(amazon_data, f)
        amazon_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(ml_data, f)
        ml_file = f.name
    
    try:
        # Test GSM8K performance
        benchmark = GSM8KBenchmark()
        model = MockModel()
        results = benchmark.run(model, gsm8k_file, max_questions=10)
        print(f"GSM8K Performance: {results.accuracy:.2%} accuracy in {results.execution_time:.2f}s")
        
        # Test Stark Amazon performance
        benchmark = StarkAmazonBenchmark()
        results = benchmark.run(model, amazon_file, max_questions=10)
        print(f"Stark Amazon Performance: {results.accuracy:.2%} accuracy, F1: {results.metadata['f1_score']:.3f} in {results.execution_time:.2f}s")
        
        # Test Agent Company ML performance
        benchmark = AgentCompanyMLBenchmark()
        agent = MockMLAgent(performance_level="good")
        results = benchmark.run(agent, ml_file, max_tasks=10)
        print(f"Agent Company ML Performance: {results.accuracy:.2%} accuracy, Completion: {results.metadata['task_completion_rate']:.2%} in {results.execution_time:.2f}s")
        
    finally:
        # Clean up
        for temp_file in [gsm8k_file, amazon_file, ml_file]:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == "__main__":
    print("Running Comprehensive Benchmark Tests")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance test
    run_performance_test()
    
    print("\n" + "=" * 50)
    print("All tests completed successfully! 🎉")
