import json
import time
from .metrics import MetricsCalculator

class ModelEvaluator:
    def __init__(self, model):
        self.model = model
        self.metrics = MetricsCalculator()
    
    def evaluate_entry_test_generation(self, test_cases):
        results = []
        
        for i, test_case in enumerate(test_cases):
            start_time = time.time()
            
            generated = self.model.generate_entry_test(test_case['input'])
            generation_time = time.time() - start_time
            
            validity = self.metrics.calculate_json_validity(
                generated, test_case['expected_output_structure']
            )
            
            structure_similarity = self.metrics.calculate_structure_similarity(
                generated, test_case['expected_output_structure']
            )
            
            results.append({
                'test_case': i,
                'validity_score': validity,
                'structure_similarity': structure_similarity,
                'generation_time': generation_time,
                'generated_output': generated
            })
        
        return self._aggregate_results(results)
    
    def evaluate_lesson_plan_generation(self, test_cases):
        results = []
        
        for i, test_case in enumerate(test_cases):
            start_time = time.time()
            
            generated = self.model.generate_lesson_plan(
                test_case['input'], 
                test_case['lesson_type']
            )
            generation_time = time.time() - start_time
            
            validity = self.metrics.calculate_json_validity(
                generated, test_case['expected_structure']
            )
            
            results.append({
                'test_case': i,
                'validity_score': validity,
                'generation_time': generation_time,
                'generated_output': generated
            })
        
        return self._aggregate_results(results)
    
    def _aggregate_results(self, results):
        if not results:
            return {}
        
        return {
            'average_validity': sum(r['validity_score'] for r in results) / len(results),
            'average_generation_time': sum(r['generation_time'] for r in results) / len(results),
            'success_rate': sum(1 for r in results if r['validity_score'] > 0) / len(results),
            'detailed_results': results
        }
