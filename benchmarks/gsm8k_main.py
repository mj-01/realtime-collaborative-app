#!/usr/bin/env python3
"""
GSM8K Benchmark Command Line Interface

This module provides a command-line interface for running the GSM8K benchmark.
Usage: python -m benchmarks.gsm8k
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.gsm8k import GSM8KBenchmark


class MockModel:
    """Mock model for demonstration purposes."""
    
    def __init__(self, name="MockModel"):
        self.name = name
    
    def generate(self, question, **kwargs):
        """Mock generate method that returns a simple response."""
        # Simple mock: return "42" for any question
        return "The answer is 42."


def create_sample_data(output_path: str, num_questions: int = 5):
    """Create sample GSM8K data for testing."""
    sample_data = [
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
    
    with open(output_path, 'w') as f:
        json.dump(sample_data[:num_questions], f, indent=2)
    
    print(f"Created sample data with {num_questions} questions at {output_path}")


def main():
    """Main entry point for GSM8K benchmark CLI."""
    parser = argparse.ArgumentParser(
        description="GSM8K Mathematical Reasoning Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with sample data
  python -m benchmarks.gsm8k --sample-data
  
  # Run with custom data file
  python -m benchmarks.gsm8k --data-file data/gsm8k.json
  
  # Run with limited questions
  python -m benchmarks.gsm8k --data-file data/gsm8k.json --max-questions 100
  
  # Create sample data file
  python -m benchmarks.gsm8k --create-sample sample.json --num-questions 10
        """
    )
    
    parser.add_argument(
        '--data-file', '-d',
        type=str,
        help='Path to GSM8K dataset file (JSON format)'
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
        benchmark = GSM8KBenchmark()
        
        if args.verbose:
            print(f"Initialized {benchmark.name} benchmark")
            print(f"Description: {benchmark.description}")
        
        # Load data
        benchmark.load_data(data_file)
        
        if args.verbose:
            print(f"Loaded {len(benchmark.questions)} questions")
        
        # Initialize model (using mock for demonstration)
        model = MockModel("DemoModel")
        
        if args.verbose:
            print(f"Using model: {model.name}")
        
        # Run evaluation
        print("Running GSM8K benchmark evaluation...")
        results = benchmark.evaluate(model, max_questions=args.max_questions)
        
        # Display results
        print("\n" + "="*50)
        print("GSM8K BENCHMARK RESULTS")
        print("="*50)
        print(f"Model: {results.model_name}")
        print(f"Total Questions: {results.total_questions}")
        print(f"Correct Answers: {results.correct_answers}")
        print(f"Accuracy: {results.accuracy:.2%}")
        print(f"Execution Time: {results.execution_time:.2f} seconds")
        print(f"Timestamp: {results.timestamp}")
        
        # Show sample results
        if args.verbose and results.detailed_results:
            print("\nSample Results:")
            for i, result in enumerate(results.detailed_results[:3]):
                print(f"\nQuestion {i+1}:")
                print(f"  Question: {result['question'][:100]}...")
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
