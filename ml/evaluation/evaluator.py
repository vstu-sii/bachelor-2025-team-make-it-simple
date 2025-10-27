import json
import time
import numpy as np
from datetime import datetime
from ml.evaluation.metrics import LLMEvaluator, PerformanceMetrics
from ml.models.baseline import BaselineLLM

class ModelEvaluator:
    """Комплексная оценка модели"""
    
    def __init__(self):
        self.llm_evaluator = LLMEvaluator()
        self.performance_metrics = PerformanceMetrics()
        self.model = BaselineLLM()
    
    def evaluate_test_generation(self, test_cases):
        """Оценка генерации тестов"""
        results = []
        latencies = []
        
        for i, test_case in enumerate(test_cases):
            print(f"Тестирование случая {i+1}/{len(test_cases)}...")
            
            start_time = time.time()
            result = self.model.generate_placement_test(
                test_case['course_topics'],
                test_case.get('student_interests')
            )
            end_time = time.time()
            
            latency = end_time - start_time
            latencies.append(latency)
            
            evaluation = {
                'test_case': test_case,
                'success': result.get('success', False),
                'latency': latency,
                'tokens_used': result.get('tokens_used', 0)
            }
            
            if result.get('success'):
                # Оценка качества сгенерированного контента
                if 'reference' in test_case:
                    quality_metrics = self.llm_evaluator.evaluate_response_quality(
                        result['parsed_data'],
                        test_case['reference'],
                        context=str(test_case['course_topics'])
                    )
                    evaluation['quality_metrics'] = quality_metrics
            
            results.append(evaluation)
        
        return {
            'results': results,
            'performance': self.performance_metrics.calculate_latency_metrics(latencies),
            'success_rate': self.performance_metrics.calculate_success_rate(
                sum(1 for r in results if r['success']), len(results)
            )
        }
    
    def evaluate_lesson_generation(self, lesson_cases):
        """Оценка генерации уроков"""
        results = []
        latencies = []
        
        for i, lesson_case in enumerate(lesson_cases):
            print(f"Тестирование урока {i+1}/{len(lesson_cases)}...")
            
            start_time = time.time()
            result = self.model.generate_lesson_plan(
                lesson_case['lesson_topic'],
                lesson_case['course_materials'],
                lesson_case['interests'],
                lesson_case['student_level']
            )
            end_time = time.time()
            
            latency = end_time - start_time
            latencies.append(latency)
            
            evaluation = {
                'lesson_case': lesson_case,
                'success': result.get('success', False),
                'latency': latency,
                'tokens_used': result.get('tokens_used', 0)
            }
            
            if result.get('success') and 'reference' in lesson_case:
                quality_metrics = self.llm_evaluator.evaluate_response_quality(
                    result['parsed_data'],
                    lesson_case['reference']
                )
                evaluation['quality_metrics'] = quality_metrics
            
            results.append(evaluation)
        
        return {
            'results': results,
            'performance': self.performance_metrics.calculate_latency_metrics(latencies)
        }
    
    def run_benchmark(self, dataset_path):
        """Запуск полного бенчмарка"""
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
        except:
            print(f"Не удалось загрузить dataset: {dataset_path}")
            return None
        
        benchmark_results = {
            'timestamp': datetime.now().isoformat(),
            'model_name': self.model.model_name
        }
        
        # Оценка генерации тестов
        if 'test_cases' in dataset:
            print("Оценка генерации тестов...")
            benchmark_results['test_generation'] = self.evaluate_test_generation(
                dataset['test_cases']
            )
        
        # Оценка генерации уроков
        if 'lesson_cases' in dataset:
            print("Оценка генерации уроков...")
            benchmark_results['lesson_generation'] = self.evaluate_lesson_generation(
                dataset['lesson_cases']
            )
        
        return benchmark_results
    
    def generate_report(self, benchmark_results, output_path):
        """Генерация отчёта"""
        report = {
            'summary': self._generate_summary(benchmark_results),
            'detailed_results': benchmark_results,
            'recommendations': self._generate_recommendations(benchmark_results)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def _generate_summary(self, results):
        """Генерация сводки"""
        summary = {
            'total_tests': 0,
            'successful_tests': 0,
            'average_latency': 0,
            'average_quality_score': 0
        }
        
        for category in ['test_generation', 'lesson_generation']:
            if category in results:
                category_results = results[category]
                summary['total_tests'] += len(category_results['results'])
                summary['successful_tests'] += sum(1 for r in category_results['results'] if r['success'])
                summary['average_latency'] += category_results['performance']['mean_latency']
                
                # Средняя оценка качества
                quality_scores = []
                for result in category_results['results']:
                    if 'quality_metrics' in result:
                        quality_scores.append(result['quality_metrics']['overall_score'])
                
                if quality_scores:
                    summary['average_quality_score'] += np.mean(quality_scores)
        
        return summary
    
    def _generate_recommendations(self, results):
        """Генерация рекомендаций по улучшению"""
        recommendations = []
        
        # Анализ задержек
        for category in ['test_generation', 'lesson_generation']:
            if category in results:
                perf = results[category]['performance']
                if perf['mean_latency'] > 30:
                    recommendations.append(f"Высокая задержка в {category}: {perf['mean_latency']:.2f} сек")
        
        # Анализ качества
        quality_scores = []
        for category in ['test_generation', 'lesson_generation']:
            if category in results:
                for result in results[category]['results']:
                    if 'quality_metrics' in result:
                        quality_scores.append(result['quality_metrics']['overall_score'])
        
        if quality_scores and np.mean(quality_scores) < 0.6:
            recommendations.append("Низкое качество генерации. Рекомендуется улучшить промпты")
        
        return recommendations

# Пример использования
def run_evaluation():
    """Запуск оценки модели"""
    evaluator = ModelEvaluator()
    
    if not evaluator.model.model_available:
        print("Модель не доступна для оценки")
        return
    
    # Запуск бенчмарка
    results = evaluator.run_benchmark('data/datasets/test_questions.json')
    
    if results:
        # Генерация отчёта
        report = evaluator.generate_report(results, 'reports/baseline_report.md')
        print("Оценка завершена. Отчёт сохранён в reports/baseline_report.md")
        
        # Вывод сводки
        summary = report['summary']
        print(f"\nСводка:")
        print(f"Успешных тестов: {summary['successful_tests']}/{summary['total_tests']}")
        print(f"Средняя задержка: {summary['average_latency']:.2f} сек")
        print(f"Среднее качество: {summary['average_quality_score']:.2f}")
        
        if report['recommendations']:
            print("\nРекомендации:")
            for rec in report['recommendations']:
                print(f"- {rec}")
    
    return results

if __name__ == "__main__":
    run_evaluation()
