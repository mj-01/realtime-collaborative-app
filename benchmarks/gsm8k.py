"""
GSM8K Benchmark Implementation

This module implements the GSM8K (Grade School Math 8K) benchmark
for evaluating mathematical reasoning capabilities of language models.
GSM8K contains 8,000 grade school math word problems.

Reference: https://github.com/openai/gsm8k
"""

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Union
from datetime import datetime

from .base import BenchmarkBase, BenchmarkResult


class GSM8KBenchmark(BenchmarkBase):
    """
    GSM8K benchmark for mathematical reasoning evaluation.
    
    GSM8K is a dataset of 8,000 high quality linguistically diverse
    grade school math word problems created by human problem writers.
    """
    
    def __init__(self):
        super().__init__(
            name="GSM8K",
            description="Grade School Math 8K - Mathematical reasoning benchmark"
        )
        self.questions = []
        self.answers = []
    
    def load_data(self, data_path: Union[str, Path]) -> None:
        """
        Load GSM8K dataset from file.
        
        Args:
            data_path: Path to the GSM8K dataset file (JSON format)
        """
        data_path = Path(data_path)
        
        if not data_path.exists():
            raise FileNotFoundError(f"GSM8K data file not found: {data_path}")
        
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        self.questions = []
        self.answers = []
        
        for item in data:
            self.questions.append(item['question'])
            self.answers.append(item['answer'])
        
        self.data = data
        print(f"Loaded {len(self.questions)} GSM8K problems")
    
    def run(self, model, data_path: Union[str, Path], **kwargs) -> BenchmarkResult:
        """
        Run the complete GSM8K benchmark pipeline: load data and evaluate.
        
        Args:
            model: The model to evaluate
            data_path: Path to the GSM8K dataset file
            **kwargs: Additional evaluation parameters
            
        Returns:
            BenchmarkResult containing evaluation results
        """
        self.load_data(data_path)
        return self.evaluate(model, **kwargs)
    
    def evaluate(self, model, max_questions: int = None, **kwargs) -> BenchmarkResult:
        """
        Evaluate model on GSM8K benchmark.
        
        Args:
            model: The model to evaluate (must have a generate method)
            max_questions: Maximum number of questions to evaluate (None for all)
            **kwargs: Additional parameters for model generation
            
        Returns:
            BenchmarkResult containing evaluation results
        """
        if not self.questions:
            raise ValueError("No data loaded. Call load_data() first.")
        
        questions_to_evaluate = self.questions[:max_questions] if max_questions else self.questions
        expected_answers = self.answers[:max_questions] if max_questions else self.answers
        
        detailed_results = []
        correct_count = 0
        start_time = time.time()
        
        print(f"Evaluating model on {len(questions_to_evaluate)} GSM8K problems...")
        
        for i, (question, expected_answer) in enumerate(zip(questions_to_evaluate, expected_answers)):
            print(f"Processing question {i+1}/{len(questions_to_evaluate)}", end='\r')
            
            # Generate model response
            try:
                response = model.generate(question, **kwargs)
                predicted_answer = self._extract_answer(response)
                is_correct = self._check_answer(predicted_answer, expected_answer)
                
                if is_correct:
                    correct_count += 1
                
                detailed_results.append({
                    'question_id': i,
                    'question': question,
                    'expected_answer': expected_answer,
                    'model_response': response,
                    'predicted_answer': predicted_answer,
                    'is_correct': is_correct
                })
                
            except Exception as e:
                print(f"\nError processing question {i+1}: {e}")
                detailed_results.append({
                    'question_id': i,
                    'question': question,
                    'expected_answer': expected_answer,
                    'model_response': None,
                    'predicted_answer': None,
                    'is_correct': False,
                    'error': str(e)
                })
        
        execution_time = time.time() - start_time
        accuracy = correct_count / len(questions_to_evaluate)
        
        print(f"\nEvaluation complete!")
        print(f"Accuracy: {accuracy:.2%} ({correct_count}/{len(questions_to_evaluate)})")
        print(f"Execution time: {execution_time:.2f} seconds")
        
        result = BenchmarkResult(
            benchmark_name=self.name,
            model_name=getattr(model, 'name', 'Unknown'),
            total_questions=len(questions_to_evaluate),
            correct_answers=correct_count,
            accuracy=accuracy,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat(),
            detailed_results=detailed_results,
            metadata={
                'max_questions': max_questions,
                'model_kwargs': kwargs
            }
        )
        
        self.results = result
        return result
    
    def get_sample_questions(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get sample questions from the GSM8K dataset.
        
        Args:
            n: Number of sample questions to return
            
        Returns:
            List of sample questions with answers
        """
        if not self.questions:
            raise ValueError("No data loaded. Call load_data() first.")
        
        samples = []
        for i in range(min(n, len(self.questions))):
            samples.append({
                'question_id': i,
                'question': self.questions[i],
                'answer': self.answers[i]
            })
        
        return samples
    
    def _extract_answer(self, response: str) -> str:
        """
        Extract numerical answer from model response.
        
        Args:
            response: Model's response text
            
        Returns:
            Extracted numerical answer as string
        """
        # Look for patterns like "The answer is 42" or "Answer: 42"
        patterns = [
            r"(?:the answer is|answer is|answer:)\s*([+-]?\d+(?:\.\d+)?)",
            r"([+-]?\d+(?:\.\d+)?)\s*(?:is the answer|is the final answer)",
            r"final answer[:\s]*([+-]?\d+(?:\.\d+)?)",
            r"([+-]?\d+(?:\.\d+)?)\s*$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, try to find any number at the end
        numbers = re.findall(r'([+-]?\d+(?:\.\d+)?)', response)
        if numbers:
            return numbers[-1]
        
        return ""
    
    def _check_answer(self, predicted: str, expected: str) -> bool:
        """
        Check if predicted answer matches expected answer.
        
        Args:
            predicted: Predicted answer string
            expected: Expected answer string
            
        Returns:
            True if answers match, False otherwise
        """
        try:
            # Extract numerical values
            pred_num = float(predicted.strip())
            exp_num = float(expected.strip())
            
            # Allow small floating point differences
            return abs(pred_num - exp_num) < 1e-6
            
        except (ValueError, AttributeError):
            # If conversion fails, do string comparison
            return predicted.strip().lower() == expected.strip().lower()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded dataset.
        
        Returns:
            Dictionary containing dataset statistics
        """
        if not self.questions:
            return {"error": "No data loaded"}
        
        # Calculate question length statistics
        question_lengths = [len(q.split()) for q in self.questions]
        
        return {
            "total_questions": len(self.questions),
            "avg_question_length": sum(question_lengths) / len(question_lengths),
            "min_question_length": min(question_lengths),
            "max_question_length": max(question_lengths),
            "description": self.description
        }
