import json
import evaluate
from sklearn.metrics import accuracy_score
import numpy as np

class MetricsCalculator:
    def __init__(self):
        self.bleu = evaluate.load('bleu')
        self.rouge = evaluate.load('rouge')
    
    def calculate_json_validity(self, generated, expected_structure):
        try:
            json.loads(json.dumps(generated))
            return 1.0
        except:
            return 0.0
    
    def calculate_bleu(self, generated_text, reference_text):
        if not generated_text or not reference_text:
            return 0.0
        
        try:
            result = self.bleu.compute(
                predictions=[generated_text],
                references=[[reference_text]]
            )
            return result['bleu']
        except:
            return 0.0
    
    def calculate_rouge(self, generated_text, reference_text):
        if not generated_text or not reference_text:
            return {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}
        
        try:
            result = self.rouge.compute(
                predictions=[generated_text],
                references=[[reference_text]]
            )
            return {k: v for k, v in result.items()}
        except:
            return {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}
    
    def calculate_structure_similarity(self, generated, expected):
        if not isinstance(generated, dict) or not isinstance(expected, dict):
            return 0.0
        
        generated_keys = set(generated.keys())
        expected_keys = set(expected.keys())
        
        if not expected_keys:
            return 0.0
        
        intersection = generated_keys.intersection(expected_keys)
        return len(intersection) / len(expected_keys)
