# Benchmarks Package

A comprehensive benchmarking suite for evaluating AI models and agents across different domains including mathematical reasoning, question answering, and machine learning workflows.

## Features

- **GSM8K Benchmark**: Mathematical reasoning evaluation with 8,000+ grade school math problems
- **Stark Amazon Benchmark**: Product question answering with F1 score metrics
- **Agent Company ML Benchmark**: Machine learning agent evaluation with task completion rates
- **Unified Interface**: Consistent API across all benchmarks
- **Comprehensive Metrics**: Accuracy, F1 score, precision, recall, task completion rates
- **Extensible Design**: Easy to add new benchmarks

## Installation

### Prerequisites

- Python 3.7+
- pip package manager

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd monorepo/benchmarks

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

The benchmarks package requires the following dependencies:

```
# Core dependencies
fastapi>=0.68.0
uvicorn>=0.15.0
pydantic>=1.8.0

# Optional dependencies for specific benchmarks
numpy>=1.21.0  # For Agent Company ML benchmark
pandas>=1.3.0  # For Agent Company ML benchmark
```

## Quick Start

### Running Individual Benchmarks

```bash
# Run GSM8K benchmark
python -m benchmarks.gsm8k

# Run Stark Amazon benchmark  
python -m benchmarks.stark_amazon

# Run Agent Company ML benchmark
python -m benchmarks.agent_company_ml
```

### Using the API

```python
from benchmarks import GSM8KBenchmark, StarkAmazonBenchmark, AgentCompanyMLBenchmark

# Initialize benchmarks
gsm8k = GSM8KBenchmark()
amazon = StarkAmazonBenchmark()
ml_agent = AgentCompanyMLBenchmark()

# Load data and evaluate
results = gsm8k.run(model, "data/gsm8k.json", max_questions=100)
print(f"GSM8K Accuracy: {results.accuracy:.2%}")

results = amazon.run(model, "data/stark_amazon.json", max_questions=50)
print(f"Amazon F1 Score: {results.metadata['f1_score']:.3f}")

results = ml_agent.run(agent, "data/agent_company_ml.json", max_tasks=20)
print(f"ML Agent Completion Rate: {results.metadata['task_completion_rate']:.2%}")
```

## Benchmark Details

### GSM8K Benchmark

**Purpose**: Evaluate mathematical reasoning capabilities

**Dataset**: 8,000 grade school math word problems

**Metrics**:
- Accuracy: Correct answers / Total questions
- Execution time
- Per-question detailed results

**Usage**:
```python
from benchmarks import GSM8KBenchmark

benchmark = GSM8KBenchmark()
results = benchmark.run(model, "data/gsm8k.json", max_questions=1000)

print(f"Accuracy: {results.accuracy:.2%}")
print(f"Correct: {results.correct_answers}/{results.total_questions}")
```

### Stark Amazon Benchmark

**Purpose**: Evaluate product question answering capabilities

**Dataset**: Amazon product questions with rich context

**Metrics**:
- Accuracy: Correct answers / Total questions
- Precision: True positives / (True positives + False positives)
- Recall: True positives / (True positives + False negatives)
- F1 Score: 2 * (Precision * Recall) / (Precision + Recall)

**Usage**:
```python
from benchmarks import StarkAmazonBenchmark

benchmark = StarkAmazonBenchmark()
results = benchmark.run(model, "data/stark_amazon.json", max_questions=500)

print(f"Accuracy: {results.accuracy:.2%}")
print(f"F1 Score: {results.metadata['f1_score']:.3f}")
print(f"Precision: {results.metadata['precision']:.3f}")
print(f"Recall: {results.metadata['recall']:.3f}")
```

### Agent Company ML Benchmark

**Purpose**: Evaluate machine learning agents in corporate settings

**Dataset**: ML workflow tasks including preprocessing, training, evaluation, deployment

**Metrics**:
- Overall Accuracy: Total score / Maximum possible score
- Task Completion Rate: Fully completed tasks (90%+ score)
- Partial Completion Rate: Partially completed tasks (50-90% score)
- Failure Rate: Failed tasks (<50% score)
- Task Type Specific Accuracy: Performance by task type

**Usage**:
```python
from benchmarks import AgentCompanyMLBenchmark

benchmark = AgentCompanyMLBenchmark()
results = benchmark.run(agent, "data/agent_company_ml.json", max_tasks=50)

print(f"Overall Accuracy: {results.accuracy:.2%}")
print(f"Task Completion: {results.metadata['task_completion_rate']:.2%}")
print(f"Partial Completion: {results.metadata['partial_completion_rate']:.2%}")
print(f"Failure Rate: {results.metadata['failure_rate']:.2%}")
```

## Data Format

### GSM8K Data Format

```json
[
  {
    "question": "Janet's ducks lay 16 eggs per day. She eats 3 for breakfast every morning and bakes 4 into muffins for her friends every day. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?",
    "answer": "18"
  }
]
```

### Stark Amazon Data Format

```json
[
  {
    "product_id": "B001234567",
    "title": "Wireless Bluetooth Headphones",
    "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life.",
    "specifications": {
      "battery_life": "30 hours",
      "connectivity": "Bluetooth 5.0",
      "noise_cancellation": "Active"
    },
    "reviews": ["Great sound quality", "Comfortable to wear"],
    "price": "$99.99",
    "category": "Electronics",
    "question": "Does this headphone have noise cancellation?",
    "answer": "Yes"
  }
]
```

### Agent Company ML Data Format

```json
{
  "tasks": [
    {
      "name": "Clean Customer Data",
      "type": "data_preprocessing",
      "description": "Clean and preprocess customer dataset for analysis",
      "max_score": 100,
      "requirements": ["handle_missing_values", "detect_outliers", "validate_data"],
      "expected_output": {"cleaned_data": "DataFrame", "report": "string"}
    }
  ],
  "datasets": {
    "customer_data": {
      "description": "Customer dataset with demographics and behavior",
      "size": 10000,
      "features": ["age", "income", "purchase_history", "satisfaction_score"]
    }
  },
  "evaluation_metrics": {
    "accuracy": "Classification accuracy",
    "precision": "Precision score",
    "recall": "Recall score",
    "f1_score": "F1 score"
  }
}
```

## Model Interface

### For GSM8K and Stark Amazon Benchmarks

Your model should implement a `generate` method:

```python
class MyModel:
    def __init__(self, name="MyModel"):
        self.name = name
    
    def generate(self, prompt, **kwargs):
        """
        Generate a response to the given prompt.
        
        Args:
            prompt: Input text prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response as string
        """
        # Your model implementation here
        return "Generated response"
```

### For Agent Company ML Benchmark

Your agent should implement an `execute_task` method:

```python
class MyMLAgent:
    def __init__(self, name="MyMLAgent"):
        self.name = name
    
    def execute_task(self, task, datasets, **kwargs):
        """
        Execute a machine learning task.
        
        Args:
            task: Task definition dictionary
            datasets: Available datasets dictionary
            **kwargs: Additional execution parameters
            
        Returns:
            Task result dictionary
        """
        # Your agent implementation here
        return {
            "completed": True,
            "result": "Task execution result"
        }
```

## Testing

### Run All Tests

```bash
# Run comprehensive test suite
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_benchmarks.py
```

### Test Coverage

The test suite includes:

- **Unit Tests**: Individual benchmark functionality
- **Integration Tests**: End-to-end pipeline testing
- **Ground Truth Tests**: Validation with known correct answers
- **Error Handling Tests**: Invalid inputs and edge cases
- **Performance Tests**: Larger dataset scalability
- **Metric Validation**: Accuracy of calculated metrics

### Test Results

```bash
# Example test output
Running Comprehensive Benchmark Tests
==================================================
test_gsm8k_benchmark_basic ... ok
test_gsm8k_benchmark_evaluation ... ok
test_stark_amazon_benchmark_basic ... ok
test_stark_amazon_benchmark_evaluation ... ok
test_agent_company_ml_benchmark_basic ... ok
test_agent_company_ml_benchmark_evaluation ... ok
test_ground_truth_comparison ... ok
test_error_handling ... ok
test_benchmark_statistics ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.007s

OK
```

## Advanced Usage

### Custom Benchmark Implementation

```python
from benchmarks.base import BenchmarkBase, BenchmarkResult

class MyCustomBenchmark(BenchmarkBase):
    def __init__(self):
        super().__init__(
            name="MyCustom",
            description="Custom benchmark implementation"
        )
    
    def load_data(self, data_path):
        # Load your custom data
        pass
    
    def evaluate(self, model, **kwargs):
        # Implement evaluation logic
        pass
    
    def run(self, model, data_path, **kwargs):
        # Complete pipeline implementation
        self.load_data(data_path)
        return self.evaluate(model, **kwargs)
```

### Batch Evaluation

```python
# Evaluate multiple models
models = [Model1(), Model2(), Model3()]
results = []

for model in models:
    result = benchmark.run(model, data_file)
    results.append(result)

# Compare results
for i, result in enumerate(results):
    print(f"Model {i+1}: {result.accuracy:.2%} accuracy")
```

### Result Analysis

```python
# Load and analyze results
from benchmarks.base import BenchmarkResult

# Save results
benchmark.save_results(results, "results/gsm8k_results.json")

# Load results
loaded_results = benchmark.load_results("results/gsm8k_results.json")

# Get statistics
stats = benchmark.get_statistics()
print(f"Dataset statistics: {stats}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your benchmark implementation
4. Write comprehensive tests
5. Submit a pull request

### Adding New Benchmarks

1. Inherit from `BenchmarkBase`
2. Implement required methods: `load_data()`, `evaluate()`, `run()`
3. Add comprehensive tests
4. Update documentation
5. Add to package exports

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or contributions:

- Create an issue on GitHub
- Check the documentation
- Review the test suite for usage examples

## Changelog

### v1.0.0
- Initial release
- GSM8K benchmark implementation
- Stark Amazon benchmark implementation  
- Agent Company ML benchmark implementation
- Comprehensive test suite
- Unified API across all benchmarks
