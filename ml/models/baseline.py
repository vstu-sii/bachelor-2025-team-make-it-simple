import ollama
import json
import time
from datetime import datetime

class BaselineLLM:
    """Базовая LLM модель с использованием Ollama"""
    
    def __init__(self, model_name="deepseek-r1:8b"):
        self.model_name = model_name
        self.setup_model()
    
    def setup_model(self):
        """Проверка доступности модели"""
        try:
            models = ollama.list()
            available_models = [model['name'] for model in models['models']]
            
            if self.model_name not in available_models:
                print(f"Модель {self.model_name} не найдена. Доступные модели: {available_models}")
                print("Установите модель: ollama pull deepseek-r1:8b")
                self.model_available = False
            else:
                self.model_available = True
                print(f"Модель {self.model_name} готова к использованию")
                
        except Exception as e:
            print(f"Ошибка при подключении к Ollama: {e}")
            self.model_available = False
    
    def generate_response(self, prompt, max_retries=3):
        """Генерация ответа с повторами при ошибках"""
        if not self.model_available:
            return {"error": "Модель не доступна"}
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                response = ollama.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'max_tokens': 4000
                    }
                )
                
                end_time = time.time()
                latency = end_time - start_time
                
                return {
                    "content": response['response'],
                    "latency": latency,
                    "tokens_used": response.get('eval_count', 0),
                    "success": True
                }
                
            except Exception as e:
                print(f"Попытка {attempt + 1} не удалась: {e}")
                if attempt == max_retries - 1:
                    return {
                        "error": str(e),
                        "success": False
                    }
                time.sleep(2)
    
    def generate_placement_test(self, course_topics, student_interests=None):
        """Генерация входного тестирования"""
        from ml.prompt_templates import PromptTemplates, ResponseValidator
        
        prompt = PromptTemplates.generate_placement_test(course_topics, student_interests)
        response = self.generate_response(prompt)
        
        if not response.get('success'):
            return response
        
        # Валидация и парсинг ответа
        data, is_valid = ResponseValidator.validate_json_response(response['content'])
        if not is_valid:
            return {
                "error": "Неверный формат ответа",
                "raw_response": response['content'],
                "success": False
            }
        
        if not ResponseValidator.validate_test_structure(data):
            return {
                "error": "Неверная структура теста",
                "raw_response": response['content'],
                "success": False
            }
        
        response['parsed_data'] = data
        return response
    
    def generate_learning_graph(self, course_topics, knowledge_gaps, interests):
        """Генерация графа обучения"""
        from ml.prompt_templates import PromptTemplates, ResponseValidator
        
        prompt = PromptTemplates.generate_learning_graph(course_topics, knowledge_gaps, interests)
        response = self.generate_response(prompt)
        
        if not response.get('success'):
            return response
        
        data, is_valid = ResponseValidator.validate_json_response(response['content'])
        if not is_valid:
            return {
                "error": "Неверный формат ответа",
                "raw_response": response['content'],
                "success": False
            }
        
        if not ResponseValidator.validate_graph_structure(data):
            return {
                "error": "Неверная структура графа",
                "raw_response": response['content'],
                "success": False
            }
        
        response['parsed_data'] = data
        return response
    
    def generate_lesson_plan(self, lesson_topic, course_materials, interests, level):
        """Генерация плана урока"""
        from ml.prompt_templates import PromptTemplates, ResponseValidator
        
        prompt = PromptTemplates.generate_lesson_plan(lesson_topic, course_materials, interests, level)
        response = self.generate_response(prompt)
        
        if not response.get('success'):
            return response
        
        data, is_valid = ResponseValidator.validate_json_response(response['content'])
        if not is_valid:
            return {
                "error": "Неверный формат ответа",
                "raw_response": response['content'],
                "success": False
            }
        
        response['parsed_data'] = data
        return response
    
    def generate_progress_report(self, performance, feedback, test_results):
        """Генерация отчёта о прогрессе"""
        from ml.prompt_templates import PromptTemplates, ResponseValidator
        
        prompt = PromptTemplates.generate_progress_report(performance, feedback, test_results)
        response = self.generate_response(prompt)
        
        if not response.get('success'):
            return response
        
        data, is_valid = ResponseValidator.validate_json_response(response['content'])
        if not is_valid:
            return {
                "error": "Неверный формат ответа",
                "raw_response": response['content'],
                "success": False
            }
        
        response['parsed_data'] = data
        return response

# Пример использования
def test_baseline_model():
    """Тестирование базовой модели"""
    model = BaselineLLM()
    
    if not model.model_available:
        print("Модель не доступна для тестирования")
        return
    
    # Тест генерации теста
    print("Тестирование генерации теста...")
    test_result = model.generate_placement_test(
        course_topics=["Математика: дроби, проценты, уравнения"],
        student_interests="футбол, видеоигры"
    )
    
    if test_result.get('success'):
        print(f"Тест создан за {test_result['latency']:.2f} сек")
        print(f"Название теста: {test_result['parsed_data']['test_title']}")
        print(f"Количество вопросов: {len(test_result['parsed_data']['questions'])}")
    else:
        print(f"Ошибка: {test_result.get('error')}")

if __name__ == "__main__":
    test_baseline_model()
