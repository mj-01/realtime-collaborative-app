#!/usr/bin/env python3
"""
Agent Company ML Benchmark Command Line Interface

This module provides a command-line interface for running the Agent Company ML benchmark.
Usage: python -m benchmarks.agent_company_ml
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.agent_company_ml import AgentCompanyMLBenchmark


class MockMLAgent:
    """Mock ML agent for demonstration purposes."""
    
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


def create_sample_data(output_path: str, num_tasks: int = 5):
    """Create sample Agent Company ML data for testing."""
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
    
    sample_data = {
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
    
    with open(output_path, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"Created sample data with {num_tasks} ML tasks at {output_path}")


def main():
    """Main entry point for Agent Company ML benchmark CLI."""
    parser = argparse.ArgumentParser(
        description="Agent Company ML Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with sample data
  python -m benchmarks.agent_company_ml --sample-data
  
  # Run with custom data file
  python -m benchmarks.agent_company_ml --data-file data/agent_company_ml.json
  
  # Run with limited tasks
  python -m benchmarks.agent_company_ml --data-file data/agent_company_ml.json --max-tasks 10
  
  # Create sample data file
  python -m benchmarks.agent_company_ml --create-sample sample.json --num-tasks 10
  
  # Run with different performance levels
  python -m benchmarks.agent_company_ml --sample-data --performance excellent
        """
    )
    
    parser.add_argument(
        '--data-file', '-d',
        type=str,
        help='Path to Agent Company ML dataset file (JSON format)'
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
        '--num-tasks', '-n',
        type=int,
        default=5,
        help='Number of tasks for sample data (default: 5)'
    )
    
    parser.add_argument(
        '--max-tasks', '-m',
        type=int,
        help='Maximum number of tasks to evaluate (default: all)'
    )
    
    parser.add_argument(
        '--performance', '-p',
        choices=['excellent', 'good', 'poor', 'random'],
        default='good',
        help='Performance level for mock agent (default: good)'
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
        create_sample_data(args.create_sample, args.num_tasks)
        return
    
    # Determine data source
    if args.sample_data:
        # Create temporary sample data
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            create_sample_data(f.name, args.num_tasks)
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
        benchmark = AgentCompanyMLBenchmark()
        
        if args.verbose:
            print(f"Initialized {benchmark.name} benchmark")
            print(f"Description: {benchmark.description}")
        
        # Load data
        benchmark.load_data(data_file)
        
        if args.verbose:
            print(f"Loaded {len(benchmark.tasks)} ML tasks")
            print(f"Available datasets: {list(benchmark.datasets.keys())}")
        
        # Initialize agent (using mock for demonstration)
        agent = MockMLAgent("DemoAgent", performance_level=args.performance)
        
        if args.verbose:
            print(f"Using agent: {agent.name} (performance: {args.performance})")
        
        # Run evaluation
        print("Running Agent Company ML benchmark evaluation...")
        results = benchmark.evaluate(agent, max_tasks=args.max_tasks)
        
        # Display results
        print("\n" + "="*50)
        print("AGENT COMPANY ML BENCHMARK RESULTS")
        print("="*50)
        print(f"Agent: {results.model_name}")
        print(f"Total Tasks: {results.total_questions}")
        print(f"Overall Score: {results.metadata['total_score']}/{results.metadata['max_possible_score']}")
        print(f"Overall Accuracy: {results.accuracy:.2%}")
        print(f"Task Completion Rate: {results.metadata['task_completion_rate']:.2%}")
        print(f"Partial Completion Rate: {results.metadata['partial_completion_rate']:.2%}")
        print(f"Failure Rate: {results.metadata['failure_rate']:.2%}")
        print(f"Execution Time: {results.execution_time:.2f} seconds")
        print(f"Timestamp: {results.timestamp}")
        
        # Show task type performance
        if results.metadata['task_type_accuracies']:
            print("\nTask Type Performance:")
            for task_type, acc in results.metadata['task_type_accuracies'].items():
                count = results.metadata['task_type_counts'][task_type]
                print(f"  {task_type}: {acc:.2%} ({count} tasks)")
        
        # Show sample results
        if args.verbose and results.detailed_results:
            print("\nSample Results:")
            for i, result in enumerate(results.detailed_results[:3]):
                print(f"\nTask {i+1}: {result['task_name']}")
                print(f"  Type: {result['task_type']}")
                print(f"  Score: {result['score']}/{result['max_score']} ({result['completion_rate']:.1%})")
                print(f"  Notes: {result['evaluation_notes']}")
        
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
