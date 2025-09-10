#!/usr/bin/env python3
"""
Stark Amazon Benchmark Command Line Interface

This module provides a command-line interface for running the Stark Amazon benchmark.
Usage: python -m benchmarks.stark_amazon
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.stark_amazon import StarkAmazonBenchmark


class MockModel:
    """Mock model for demonstration purposes."""
    
    def __init__(self, name="MockModel"):
        self.name = name
    
    def generate(self, prompt, **kwargs):
        """Mock generate method that returns a simple response."""
        # Simple mock: return "Yes" for any question
        return "Yes, this product meets your requirements."


def create_sample_data(output_path: str, num_questions: int = 5):
    """Create sample Stark Amazon data for testing."""
    sample_data = [
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
    
    with open(output_path, 'w') as f:
        json.dump(sample_data[:num_questions], f, indent=2)
    
    print(f"Created sample data with {num_questions} product questions at {output_path}")


def main():
    """Main entry point for Stark Amazon benchmark CLI."""
    parser = argparse.ArgumentParser(
        description="Stark Amazon Product Question Answering Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with sample data
  python -m benchmarks.stark_amazon --sample-data
  
  # Run with custom data file
  python -m benchmarks.stark_amazon --data-file data/stark_amazon.json
  
  # Run with limited questions
  python -m benchmarks.stark_amazon --data-file data/stark_amazon.json --max-questions 50
  
  # Create sample data file
  python -m benchmarks.stark_amazon --create-sample sample.json --num-questions 10
        """
    )
    
    parser.add_argument(
        '--data-file', '-d',
        type=str,
        help='Path to Stark Amazon dataset file (JSON format)'
    )
    
    parser.add_argument(
        '--sample-data', '-s',
        action='store_true',
        help='Use built-in sample data for testing'
    )
    
    parser.add_argument(
        '--create-sample', '-c',
        type=str,
        help='Create sample data file at specified path'
    )
    
    parser.add_argument(
        '--num-questions', '-n',
        type=int,
        default=5,
        help='Number of questions for sample data (default: 5)'
    )
    
    parser.add_argument(
        '--max-questions', '-m',
        type=int,
        help='Maximum number of questions to evaluate (default: all)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file for results (JSON format)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Handle create sample data
    if args.create_sample:
        create_sample_data(args.create_sample, args.num_questions)
        return
    
    # Determine data source
    if args.sample_data:
        # Create temporary sample data
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            create_sample_data(f.name, args.num_questions)
            data_file = f.name
    elif args.data_file:
        data_file = args.data_file
        if not Path(data_file).exists():
            print(f"Error: Data file '{data_file}' not found")
            sys.exit(1)
    else:
        print("Error: Must specify either --data-file or --sample-data")
        parser.print_help()
        sys.exit(1)
    
    try:
        # Initialize benchmark
        benchmark = StarkAmazonBenchmark()
        
        if args.verbose:
            print(f"Initialized {benchmark.name} benchmark")
            print(f"Description: {benchmark.description}")
        
        # Load data
        benchmark.load_data(data_file)
        
        if args.verbose:
            print(f"Loaded {len(benchmark.questions)} product questions")
        
        # Initialize model (using mock for demonstration)
        model = MockModel("DemoModel")
        
        if args.verbose:
            print(f"Using model: {model.name}")
        
        # Run evaluation
        print("Running Stark Amazon benchmark evaluation...")
        results = benchmark.evaluate(model, max_questions=args.max_questions)
        
        # Display results
        print("\n" + "="*50)
        print("STARK AMAZON BENCHMARK RESULTS")
        print("="*50)
        print(f"Model: {results.model_name}")
        print(f"Total Questions: {results.total_questions}")
        print(f"Correct Answers: {results.correct_answers}")
        print(f"Accuracy: {results.accuracy:.2%}")
        print(f"Precision: {results.metadata['precision']:.3f}")
        print(f"Recall: {results.metadata['recall']:.3f}")
        print(f"F1 Score: {results.metadata['f1_score']:.3f}")
        print(f"Execution Time: {results.execution_time:.2f} seconds")
        print(f"Timestamp: {results.timestamp}")
        
        # Show sample results
        if args.verbose and results.detailed_results:
            print("\nSample Results:")
            for i, result in enumerate(results.detailed_results[:3]):
                print(f"\nQuestion {i+1}:")
                print(f"  Product: {result['product_title']}")
                print(f"  Question: {result['question']}")
                print(f"  Expected: {result['expected_answer']}")
                print(f"  Predicted: {result['predicted_answer']}")
                print(f"  Correct: {result['is_correct']}")
        
        # Save results if requested
        if args.output:
            benchmark.save_results(results, args.output)
            print(f"\nResults saved to: {args.output}")
        
        # Clean up temporary file
        if args.sample_data:
            Path(data_file).unlink()
        
        print("\nBenchmark evaluation completed successfully!")
        
    except Exception as e:
        print(f"Error running benchmark: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
