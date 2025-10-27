import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class LLMEvaluator:
    """Оценка качества LLM моделей"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
    
    def calculate_bleu_score(self, generated, reference, n=4):
        """Упрощенный расчет BLEU score"""
        def get_ngrams(text, n):
            words = text.split()
            return [tuple(words[i:i+n]) for i in range(len(words)-n+1)]
        
        generated_ngrams = get_ngrams(generated, n)
        reference_ngrams = get_ngrams(reference, n)
        
        if not generated_ngrams:
            return 0.0
        
        # Количество совпадающих n-грамм
        matches = len(set(generated_ngrams) & set(reference_ngrams))
        precision = matches / len(generated_ngrams)
        
        # Brevity penalty
        bp = 1.0 if len(generated.split()) > len(reference.split()) else np.exp(1 - len(reference.split())/len(generated.split()))
        
        return bp * precision
    
    def calculate_rouge_score(self, generated, reference):
        """Упрощенный расчет ROUGE-L score"""
        def longest_common_subsequence(text1, text2):
            words1 = text1.split()
            words2 = text2.split()
            
            m, n = len(words1), len(words2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if words1[i-1] == words2[j-1]:
                        dp[i][j] = dp[i-1][j-1] + 1
                    else:
                        dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            
            return dp[m][n]
        
        lcs = longest_common_subsequence(generated, reference)
        recall = lcs / len(reference.split()) if reference else 0
        precision = lcs / len(generated.split()) if generated else 0
        
        if recall + precision == 0:
            return 0.0
        
        f1 = 2 * recall * precision / (recall + precision)
        return f1
    
    def calculate_semantic_similarity(self, text1, text2):
        """Семантическое сходство на основе TF-IDF"""
        if not text1 or not text2:
            return 0.0
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return similarity[0][0]
        except:
            return 0.0
    
    def detect_hallucinations(self, generated_text, source_context):
        """Обнаружение галлюцинаций - проверка фактов не из контекста"""
        # Упрощенная проверка: ищем утверждения в сгенерированном тексте
        # которых нет в исходном контексте
        generated_sentences = re.split(r'[.!?]', generated_text)
        context_sentences = re.split(r'[.!?]', source_context)
        
        hallucination_count = 0
        total_sentences = len(generated_sentences)
        
        if total_sentences == 0:
            return 0.0
        
        for sentence in generated_sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Проверяем, есть ли похожее предложение в контексте
            is_found = False
            for context_sentence in context_sentences:
                if self.calculate_semantic_similarity(sentence, context_sentence) > 0.6:
                    is_found = True
                    break
            
            if not is_found:
                hallucination_count += 1
        
        return hallucination_count / total_sentences
    
    def evaluate_response_quality(self, generated_data, reference_data, context=None):
        """Комплексная оценка качества ответа"""
        metrics = {}
        
        # Преобразуем в текст для метрик
        if isinstance(generated_data, dict):
            generated_text = json.dumps(generated_data, ensure_ascii=False)
        else:
            generated_text = str(generated_data)
            
        if isinstance(reference_data, dict):
            reference_text = json.dumps(reference_data, ensure_ascii=False)
        else:
            reference_text = str(reference_data)
        
        # Вычисляем метрики
        metrics['bleu'] = self.calculate_bleu_score(generated_text, reference_text)
        metrics['rouge'] = self.calculate_rouge_score(generated_text, reference_text)
        metrics['semantic_similarity'] = self.calculate_semantic_similarity(generated_text, reference_text)
        
        if context:
            metrics['hallucination_rate'] = self.detect_hallucinations(generated_text, context)
        else:
            metrics['hallucination_rate'] = 0.0
        
        # Структурная валидность (для JSON)
        if isinstance(generated_data, dict):
            metrics['structural_validity'] = 1.0
        else:
            metrics['structural_validity'] = 0.0
        
        # Общая оценка
        weights = {
            'bleu': 0.2,
            'rouge': 0.3,
            'semantic_similarity': 0.3,
            'structural_validity': 0.2
        }
        
        total_score = 0
        for metric, weight in weights.items():
            total_score += metrics[metric] * weight
        
        metrics['overall_score'] = total_score
        
        return metrics

class PerformanceMetrics:
    """Метрики производительности"""
    
    @staticmethod
    def calculate_latency_metrics(latencies):
        """Расчет метрик задержки"""
        if not latencies:
            return {}
        
        return {
            'mean_latency': np.mean(latencies),
            'median_latency': np.median(latencies),
            'p95_latency': np.percentile(latencies, 95),
            'min_latency': np.min(latencies),
            'max_latency': np.max(latencies),
            'std_latency': np.std(latencies)
        }
    
    @staticmethod
    def calculate_throughput(total_requests, total_time):
        """Расчет пропускной способности"""
        if total_time == 0:
            return 0
        return total_requests / total_time
    
    @staticmethod
    def calculate_success_rate(successful_requests, total_requests):
        """Расчет успешности запросов"""
        if total_requests == 0:
            return 0
        return successful_requests / total_requests
