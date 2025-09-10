"""
Agent Company ML Benchmark Implementation

This module implements a benchmark for evaluating machine learning
agents in a company setting. The benchmark tests various ML tasks
including data preprocessing, model training, evaluation, and
deployment scenarios.

This benchmark simulates real-world ML workflows and challenges
that data scientists and ML engineers face in corporate environments.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Union, Optional
from datetime import datetime

try:
    import numpy as np
    import pandas as pd
    HAS_NUMPY_PANDAS = True
except ImportError:
    HAS_NUMPY_PANDAS = False

from .base import BenchmarkBase, BenchmarkResult


class AgentCompanyMLBenchmark(BenchmarkBase):
    """
    Agent Company ML benchmark for evaluating ML agents in corporate settings.
    
    This benchmark tests ML agents on various tasks including:
    - Data preprocessing and cleaning
    - Feature engineering
    - Model selection and training
    - Model evaluation and validation
    - Deployment and monitoring
    - Business metric optimization
    """
    
    def __init__(self):
        super().__init__(
            name="AgentCompanyML",
            description="Machine Learning agent evaluation in corporate environment"
        )
        self.tasks = []
        self.datasets = {}
        self.evaluation_metrics = {}
    
    def load_data(self, data_path: Union[str, Path]) -> None:
        """
        Load Agent Company ML benchmark data from file.
        
        Args:
            data_path: Path to the benchmark data file (JSON format)
        """
        data_path = Path(data_path)
        
        if not data_path.exists():
            raise FileNotFoundError(f"Agent Company ML data file not found: {data_path}")
        
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        self.tasks = data.get('tasks', [])
        self.datasets = data.get('datasets', {})
        self.evaluation_metrics = data.get('evaluation_metrics', {})
        
        self.data = data
        print(f"Loaded {len(self.tasks)} ML tasks")
        print(f"Available datasets: {list(self.datasets.keys())}")
    
    def run(self, agent, data_path: Union[str, Path], **kwargs) -> BenchmarkResult:
        """
        Run the complete Agent Company ML benchmark pipeline: load data and evaluate.
        
        Args:
            agent: The ML agent to evaluate
            data_path: Path to the benchmark data file
            **kwargs: Additional evaluation parameters
            
        Returns:
            BenchmarkResult containing evaluation results
        """
        self.load_data(data_path)
        return self.evaluate(agent, **kwargs)
    
    def evaluate(self, agent, max_tasks: int = None, **kwargs) -> BenchmarkResult:
        """
        Evaluate ML agent on company benchmark tasks.
        
        Args:
            agent: The ML agent to evaluate (must have execute_task method)
            max_tasks: Maximum number of tasks to evaluate (None for all)
            **kwargs: Additional parameters for agent execution
            
        Returns:
            BenchmarkResult containing evaluation results
        """
        if not self.tasks:
            raise ValueError("No data loaded. Call load_data() first.")
        
        tasks_to_evaluate = self.tasks[:max_tasks] if max_tasks else self.tasks
        
        detailed_results = []
        total_score = 0
        max_possible_score = 0
        start_time = time.time()
        
        # Task completion metrics
        completed_tasks = 0
        failed_tasks = 0
        partial_tasks = 0
        
        # Task type specific metrics
        task_type_scores = {}
        task_type_counts = {}
        
        print(f"Evaluating ML agent on {len(tasks_to_evaluate)} company tasks...")
        
        for i, task in enumerate(tasks_to_evaluate):
            print(f"Processing task {i+1}/{len(tasks_to_evaluate)}: {task['name']}", end='\r')
            
            task_type = task.get('type', 'unknown')
            task_type_counts[task_type] = task_type_counts.get(task_type, 0) + 1
            
            try:
                # Execute the task
                task_result = agent.execute_task(task, self.datasets, **kwargs)
                
                # Evaluate the result
                score = self._evaluate_task_result(task, task_result)
                total_score += score
                max_possible_score += task.get('max_score', 100)
                
                # Update task type scores
                if task_type not in task_type_scores:
                    task_type_scores[task_type] = {'total': 0, 'max': 0}
                task_type_scores[task_type]['total'] += score
                task_type_scores[task_type]['max'] += task.get('max_score', 100)
                
                # Categorize task completion
                if score >= task.get('max_score', 100) * 0.9:  # 90% or higher
                    completed_tasks += 1
                elif score >= task.get('max_score', 100) * 0.5:  # 50% or higher
                    partial_tasks += 1
                else:
                    failed_tasks += 1
                
                detailed_results.append({
                    'task_id': i,
                    'task_name': task['name'],
                    'task_type': task_type,
                    'task_description': task.get('description', ''),
                    'agent_result': task_result,
                    'score': score,
                    'max_score': task.get('max_score', 100),
                    'completion_rate': score / task.get('max_score', 100),
                    'evaluation_notes': self._get_evaluation_notes(task, task_result)
                })
                
            except Exception as e:
                print(f"\nError processing task {i+1}: {e}")
                failed_tasks += 1
                detailed_results.append({
                    'task_id': i,
                    'task_name': task['name'],
                    'task_type': task_type,
                    'agent_result': None,
                    'score': 0,
                    'max_score': task.get('max_score', 100),
                    'completion_rate': 0.0,
                    'error': str(e)
                })
        
        execution_time = time.time() - start_time
        
        # Calculate comprehensive metrics
        accuracy = total_score / max_possible_score if max_possible_score > 0 else 0
        task_completion_rate = completed_tasks / len(tasks_to_evaluate) if tasks_to_evaluate else 0
        partial_completion_rate = partial_tasks / len(tasks_to_evaluate) if tasks_to_evaluate else 0
        failure_rate = failed_tasks / len(tasks_to_evaluate) if tasks_to_evaluate else 0
        
        # Calculate task type specific accuracies
        task_type_accuracies = {}
        for task_type, scores in task_type_scores.items():
            if scores['max'] > 0:
                task_type_accuracies[task_type] = scores['total'] / scores['max']
            else:
                task_type_accuracies[task_type] = 0.0
        
        print(f"\nEvaluation complete!")
        print(f"Overall Score: {total_score}/{max_possible_score} ({accuracy:.2%})")
        print(f"Task Completion Rate: {task_completion_rate:.2%} ({completed_tasks}/{len(tasks_to_evaluate)})")
        print(f"Partial Completion Rate: {partial_completion_rate:.2%} ({partial_tasks}/{len(tasks_to_evaluate)})")
        print(f"Failure Rate: {failure_rate:.2%} ({failed_tasks}/{len(tasks_to_evaluate)})")
        print(f"Execution time: {execution_time:.2f} seconds")
        
        # Print task type specific results
        if task_type_accuracies:
            print("\nTask Type Performance:")
            for task_type, acc in task_type_accuracies.items():
                count = task_type_counts[task_type]
                print(f"  {task_type}: {acc:.2%} ({count} tasks)")
        
        result = BenchmarkResult(
            benchmark_name=self.name,
            model_name=getattr(agent, 'name', 'Unknown'),
            total_questions=len(tasks_to_evaluate),
            correct_answers=int(total_score),
            accuracy=accuracy,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat(),
            detailed_results=detailed_results,
            metadata={
                'max_tasks': max_tasks,
                'total_score': total_score,
                'max_possible_score': max_possible_score,
                'agent_kwargs': kwargs,
                'task_completion_rate': task_completion_rate,
                'partial_completion_rate': partial_completion_rate,
                'failure_rate': failure_rate,
                'completed_tasks': completed_tasks,
                'partial_tasks': partial_tasks,
                'failed_tasks': failed_tasks,
                'task_type_accuracies': task_type_accuracies,
                'task_type_counts': task_type_counts
            }
        )
        
        self.results = result
        return result
    
    def get_sample_questions(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get sample tasks from the Agent Company ML benchmark.
        
        Args:
            n: Number of sample tasks to return
            
        Returns:
            List of sample tasks with descriptions
        """
        if not self.tasks:
            raise ValueError("No data loaded. Call load_data() first.")
        
        samples = []
        for i in range(min(n, len(self.tasks))):
            task = self.tasks[i]
            samples.append({
                'task_id': i,
                'name': task['name'],
                'type': task.get('type', 'unknown'),
                'description': task.get('description', ''),
                'max_score': task.get('max_score', 100),
                'requirements': task.get('requirements', []),
                'expected_output': task.get('expected_output', {})
            })
        
        return samples
    
    def _evaluate_task_result(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:
        """
        Evaluate the result of a specific task.
        
        Args:
            task: Task definition
            result: Agent's result for the task
            
        Returns:
            Score for the task (0-100)
        """
        task_type = task.get('type', 'unknown')
        max_score = task.get('max_score', 100)
        
        if not result:
            return 0.0
        
        # Task-specific evaluation logic
        if task_type == 'data_preprocessing':
            return self._evaluate_preprocessing_task(task, result, max_score)
        elif task_type == 'feature_engineering':
            return self._evaluate_feature_engineering_task(task, result, max_score)
        elif task_type == 'model_training':
            return self._evaluate_model_training_task(task, result, max_score)
        elif task_type == 'model_evaluation':
            return self._evaluate_model_evaluation_task(task, result, max_score)
        elif task_type == 'deployment':
            return self._evaluate_deployment_task(task, result, max_score)
        else:
            return self._evaluate_generic_task(task, result, max_score)
    
    def _evaluate_preprocessing_task(self, task: Dict[str, Any], result: Dict[str, Any], max_score: float) -> float:
        """Evaluate data preprocessing task results."""
        score = 0.0
        
        # Check if data cleaning was performed
        if result.get('data_cleaned', False):
            score += 0.3 * max_score
        
        # Check if missing values were handled
        if result.get('missing_values_handled', False):
            score += 0.2 * max_score
        
        # Check if outliers were detected/handled
        if result.get('outliers_handled', False):
            score += 0.2 * max_score
        
        # Check if data validation was performed
        if result.get('data_validated', False):
            score += 0.3 * max_score
        
        return min(score, max_score)
    
    def _evaluate_feature_engineering_task(self, task: Dict[str, Any], result: Dict[str, Any], max_score: float) -> float:
        """Evaluate feature engineering task results."""
        score = 0.0
        
        # Check if new features were created
        new_features = result.get('new_features', [])
        if len(new_features) > 0:
            score += 0.4 * max_score
        
        # Check if feature selection was performed
        if result.get('feature_selection_performed', False):
            score += 0.3 * max_score
        
        # Check if feature scaling was applied
        if result.get('feature_scaling_applied', False):
            score += 0.3 * max_score
        
        return min(score, max_score)
    
    def _evaluate_model_training_task(self, task: Dict[str, Any], result: Dict[str, Any], max_score: float) -> float:
        """Evaluate model training task results."""
        score = 0.0
        
        # Check if model was trained
        if result.get('model_trained', False):
            score += 0.4 * max_score
        
        # Check if hyperparameter tuning was performed
        if result.get('hyperparameter_tuning', False):
            score += 0.3 * max_score
        
        # Check if cross-validation was used
        if result.get('cross_validation_used', False):
            score += 0.3 * max_score
        
        return min(score, max_score)
    
    def _evaluate_model_evaluation_task(self, task: Dict[str, Any], result: Dict[str, Any], max_score: float) -> float:
        """Evaluate model evaluation task results."""
        score = 0.0
        
        # Check if appropriate metrics were calculated
        metrics = result.get('metrics', {})
        if len(metrics) > 0:
            score += 0.5 * max_score
        
        # Check if model performance was analyzed
        if result.get('performance_analysis', False):
            score += 0.3 * max_score
        
        # Check if business impact was considered
        if result.get('business_impact_considered', False):
            score += 0.2 * max_score
        
        return min(score, max_score)
    
    def _evaluate_deployment_task(self, task: Dict[str, Any], result: Dict[str, Any], max_score: float) -> float:
        """Evaluate deployment task results."""
        score = 0.0
        
        # Check if deployment strategy was defined
        if result.get('deployment_strategy', False):
            score += 0.4 * max_score
        
        # Check if monitoring was set up
        if result.get('monitoring_setup', False):
            score += 0.3 * max_score
        
        # Check if rollback plan was considered
        if result.get('rollback_plan', False):
            score += 0.3 * max_score
        
        return min(score, max_score)
    
    def _evaluate_generic_task(self, task: Dict[str, Any], result: Dict[str, Any], max_score: float) -> float:
        """Evaluate generic task results."""
        # Basic evaluation based on result completeness
        if result.get('completed', False):
            return max_score * 0.8
        elif result.get('partial_completion', False):
            return max_score * 0.5
        else:
            return 0.0
    
    def _get_evaluation_notes(self, task: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Get evaluation notes for a task result."""
        notes = []
        
        if result.get('error'):
            notes.append(f"Error: {result['error']}")
        
        if result.get('warnings'):
            notes.append(f"Warnings: {result['warnings']}")
        
        if result.get('recommendations'):
            notes.append(f"Recommendations: {result['recommendations']}")
        
        return "; ".join(notes) if notes else "No specific notes"
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded benchmark.
        
        Returns:
            Dictionary containing benchmark statistics
        """
        if not self.tasks:
            return {"error": "No data loaded"}
        
        # Count tasks by type
        task_types = {}
        for task in self.tasks:
            task_type = task.get('type', 'unknown')
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        # Calculate total possible score
        total_max_score = sum(task.get('max_score', 100) for task in self.tasks)
        
        return {
            "total_tasks": len(self.tasks),
            "task_types": task_types,
            "total_max_score": total_max_score,
            "available_datasets": list(self.datasets.keys()),
            "evaluation_metrics": list(self.evaluation_metrics.keys()),
            "description": self.description
        }
