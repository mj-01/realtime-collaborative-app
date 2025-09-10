"""
Stark Amazon Benchmark Implementation

This module implements the Stark Amazon benchmark for evaluating
question answering capabilities on Amazon product-related questions.
The benchmark focuses on understanding product descriptions, reviews,
and specifications.

Reference: https://github.com/StarkAI/amazon-benchmark
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Union
from datetime import datetime

from .base import BenchmarkBase, BenchmarkResult


class StarkAmazonBenchmark(BenchmarkBase):
    """
    Stark Amazon benchmark for product question answering evaluation.
    
    This benchmark evaluates models on their ability to answer questions
    about Amazon products based on product descriptions, reviews, and
    specifications.
    """
    
    def __init__(self):
        super().__init__(
            name="StarkAmazon",
            description="Amazon product question answering benchmark"
        )
        self.products = []
        self.questions = []
        self.answers = []
    
    def load_data(self, data_path: Union[str, Path]) -> None:
        """
        Load Stark Amazon dataset from file.
        
        Args:
            data_path: Path to the Stark Amazon dataset file (JSON format)
        """
        data_path = Path(data_path)
        
        if not data_path.exists():
            raise FileNotFoundError(f"Stark Amazon data file not found: {data_path}")
        
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        self.products = []
        self.questions = []
        self.answers = []
        
        for item in data:
            self.products.append({
                'product_id': item.get('product_id', ''),
                'title': item.get('title', ''),
                'description': item.get('description', ''),
                'specifications': item.get('specifications', {}),
                'reviews': item.get('reviews', []),
                'price': item.get('price', ''),
                'category': item.get('category', '')
            })
            self.questions.append(item['question'])
            self.answers.append(item['answer'])
        
        self.data = data
        print(f"Loaded {len(self.products)} Amazon product questions")
    
    def run(self, model, data_path: Union[str, Path], **kwargs) -> BenchmarkResult:
        """
        Run the complete Stark Amazon benchmark pipeline: load data and evaluate.
        
        Args:
            model: The model to evaluate
            data_path: Path to the Stark Amazon dataset file
            **kwargs: Additional evaluation parameters
            
        Returns:
            BenchmarkResult containing evaluation results
        """
        self.load_data(data_path)
        return self.evaluate(model, **kwargs)
    
    def evaluate(self, model, max_questions: int = None, **kwargs) -> BenchmarkResult:
        """
        Evaluate model on Stark Amazon benchmark.
        
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
        products_to_evaluate = self.products[:max_questions] if max_questions else self.products
        
        detailed_results = []
        correct_count = 0
        start_time = time.time()
        
        # For F1 score calculation
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        print(f"Evaluating model on {len(questions_to_evaluate)} Amazon product questions...")
        
        for i, (question, expected_answer, product) in enumerate(zip(questions_to_evaluate, expected_answers, products_to_evaluate)):
            print(f"Processing question {i+1}/{len(questions_to_evaluate)}", end='\r')
            
            # Prepare context for the model
            context = self._prepare_context(product)
            full_prompt = f"Product: {context}\n\nQuestion: {question}\n\nAnswer:"
            
            try:
                response = model.generate(full_prompt, **kwargs)
                predicted_answer = self._extract_answer(response)
                is_correct = self._check_answer(predicted_answer, expected_answer)
                
                # Calculate F1 score components
                if is_correct:
                    correct_count += 1
                    true_positives += 1
                else:
                    false_negatives += 1
                    # Check if model gave any answer (false positive)
                    if predicted_answer and predicted_answer.strip():
                        false_positives += 1
                
                detailed_results.append({
                    'question_id': i,
                    'product_id': product['product_id'],
                    'product_title': product['title'],
                    'question': question,
                    'expected_answer': expected_answer,
                    'model_response': response,
                    'predicted_answer': predicted_answer,
                    'is_correct': is_correct,
                    'context_used': context[:200] + "..." if len(context) > 200 else context
                })
                
            except Exception as e:
                print(f"\nError processing question {i+1}: {e}")
                false_negatives += 1
                detailed_results.append({
                    'question_id': i,
                    'product_id': product['product_id'],
                    'question': question,
                    'expected_answer': expected_answer,
                    'model_response': None,
                    'predicted_answer': None,
                    'is_correct': False,
                    'error': str(e)
                })
        
        execution_time = time.time() - start_time
        accuracy = correct_count / len(questions_to_evaluate)
        
        # Calculate F1 score
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\nEvaluation complete!")
        print(f"Accuracy: {accuracy:.2%} ({correct_count}/{len(questions_to_evaluate)})")
        print(f"Precision: {precision:.3f}")
        print(f"Recall: {recall:.3f}")
        print(f"F1 Score: {f1_score:.3f}")
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
                'model_kwargs': kwargs,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'true_positives': true_positives,
                'false_positives': false_positives,
                'false_negatives': false_negatives
            }
        )
        
        self.results = result
        return result
    
    def get_sample_questions(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get sample questions from the Stark Amazon dataset.
        
        Args:
            n: Number of sample questions to return
            
        Returns:
            List of sample questions with product context and answers
        """
        if not self.questions:
            raise ValueError("No data loaded. Call load_data() first.")
        
        samples = []
        for i in range(min(n, len(self.questions))):
            product = self.products[i]
            samples.append({
                'question_id': i,
                'product_id': product['product_id'],
                'product_title': product['title'],
                'question': self.questions[i],
                'answer': self.answers[i],
                'context': self._prepare_context(product)
            })
        
        return samples
    
    def _prepare_context(self, product: Dict[str, Any]) -> str:
        """
        Prepare product context for the model.
        
        Args:
            product: Product information dictionary
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        if product['title']:
            context_parts.append(f"Title: {product['title']}")
        
        if product['description']:
            context_parts.append(f"Description: {product['description']}")
        
        if product['specifications']:
            specs_text = ", ".join([f"{k}: {v}" for k, v in product['specifications'].items()])
            context_parts.append(f"Specifications: {specs_text}")
        
        if product['price']:
            context_parts.append(f"Price: {product['price']}")
        
        if product['category']:
            context_parts.append(f"Category: {product['category']}")
        
        if product['reviews']:
            # Include first few reviews
            reviews_text = " ".join(product['reviews'][:3])
            context_parts.append(f"Reviews: {reviews_text}")
        
        return "\n".join(context_parts)
    
    def _extract_answer(self, response: str) -> str:
        """
        Extract answer from model response.
        
        Args:
            response: Model's response text
            
        Returns:
            Extracted answer as string
        """
        # Look for common answer patterns
        lines = response.strip().split('\n')
        
        # Try to find the last line that looks like an answer
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith(('Question:', 'Product:', 'Answer:', 'Context:')):
                return line
        
        # If no clear answer found, return the whole response
        return response.strip()
    
    def _check_answer(self, predicted: str, expected: str) -> bool:
        """
        Check if predicted answer matches expected answer.
        
        Args:
            predicted: Predicted answer string
            expected: Expected answer string
            
        Returns:
            True if answers match, False otherwise
        """
        # Normalize both answers
        pred_normalized = predicted.strip().lower()
        exp_normalized = expected.strip().lower()
        
        # Direct string match
        if pred_normalized == exp_normalized:
            return True
        
        # Check if predicted answer contains expected answer
        if exp_normalized in pred_normalized:
            return True
        
        # Check if expected answer contains predicted answer
        if pred_normalized in exp_normalized:
            return True
        
        return False
    
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
        
        # Calculate product context statistics
        context_lengths = [len(self._prepare_context(p).split()) for p in self.products]
        
        # Count categories
        categories = {}
        for product in self.products:
            cat = product.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_questions": len(self.questions),
            "avg_question_length": sum(question_lengths) / len(question_lengths),
            "avg_context_length": sum(context_lengths) / len(context_lengths),
            "categories": categories,
            "description": self.description
        }
