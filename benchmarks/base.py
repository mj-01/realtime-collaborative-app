"""
Base benchmark class for all benchmark implementations.

This module provides the abstract base class that all benchmarks
should inherit from, ensuring consistent interface and behavior.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BenchmarkResult:
    """Container for benchmark evaluation results."""
    
    benchmark_name: str
    model_name: str
    total_questions: int
    correct_answers: int
    accuracy: float
    execution_time: float
    timestamp: str
    detailed_results: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class BenchmarkBase(ABC):
    """
    Abstract base class for all benchmark implementations.
    
    This class defines the common interface that all benchmarks
    must implement, including methods for loading data, running
    evaluations, and generating results.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the benchmark.
        
        Args:
            name: Name of the benchmark
            description: Optional description of the benchmark
        """
        self.name = name
        self.description = description
        self.data = None
        self.results = None
    
    @abstractmethod
    def load_data(self, data_path: Union[str, Path]) -> None:
        """
        Load benchmark data from file or URL.
        
        Args:
            data_path: Path to the data file or URL
        """
        pass
    
    @abstractmethod
    def evaluate(self, model, **kwargs) -> BenchmarkResult:
        """
        Run the benchmark evaluation on a model.
        
        Args:
            model: The model to evaluate
            **kwargs: Additional evaluation parameters
            
        Returns:
            BenchmarkResult containing evaluation results
        """
        pass
    
    @abstractmethod
    def run(self, model, data_path: Union[str, Path], **kwargs) -> BenchmarkResult:
        """
        Run the complete benchmark pipeline: load data and evaluate.
        
        Args:
            model: The model to evaluate
            data_path: Path to the data file or URL
            **kwargs: Additional evaluation parameters
            
        Returns:
            BenchmarkResult containing evaluation results
        """
        pass


class BaseBenchmark(BenchmarkBase):
    """
    Legacy base class for backward compatibility.
    
    This class extends BenchmarkBase and provides additional
    utility methods for result management and statistics.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the benchmark.
        
        Args:
            name: Name of the benchmark
            description: Optional description of the benchmark
        """
        super().__init__(name, description)
    
    def run(self, model, data_path: Union[str, Path], **kwargs) -> BenchmarkResult:
        """
        Run the complete benchmark pipeline: load data and evaluate.
        
        Args:
            model: The model to evaluate
            data_path: Path to the data file or URL
            **kwargs: Additional evaluation parameters
            
        Returns:
            BenchmarkResult containing evaluation results
        """
        self.load_data(data_path)
        return self.evaluate(model, **kwargs)
    
    @abstractmethod
    def get_sample_questions(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get a sample of questions from the benchmark.
        
        Args:
            n: Number of sample questions to return
            
        Returns:
            List of sample questions
        """
        pass
    
    def save_results(self, results: BenchmarkResult, output_path: Union[str, Path]) -> None:
        """
        Save benchmark results to a file.
        
        Args:
            results: The results to save
            output_path: Path where to save the results
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                'benchmark_name': results.benchmark_name,
                'model_name': results.model_name,
                'total_questions': results.total_questions,
                'correct_answers': results.correct_answers,
                'accuracy': results.accuracy,
                'execution_time': results.execution_time,
                'timestamp': results.timestamp,
                'detailed_results': results.detailed_results,
                'metadata': results.metadata
            }, f, indent=2)
    
    def load_results(self, results_path: Union[str, Path]) -> BenchmarkResult:
        """
        Load benchmark results from a file.
        
        Args:
            results_path: Path to the results file
            
        Returns:
            Loaded BenchmarkResult object
        """
        with open(results_path, 'r') as f:
            data = json.load(f)
        
        return BenchmarkResult(
            benchmark_name=data['benchmark_name'],
            model_name=data['model_name'],
            total_questions=data['total_questions'],
            correct_answers=data['correct_answers'],
            accuracy=data['accuracy'],
            execution_time=data['execution_time'],
            timestamp=data['timestamp'],
            detailed_results=data['detailed_results'],
            metadata=data['metadata']
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get benchmark metadata.
        
        Returns:
            Dictionary containing benchmark metadata
        """
        return {
            'name': self.name,
            'description': self.description,
            'data_loaded': self.data is not None,
            'has_results': self.results is not None
        }
    
    def __repr__(self) -> str:
        """String representation of the benchmark."""
        return f"{self.__class__.__name__}(name='{self.name}')"
