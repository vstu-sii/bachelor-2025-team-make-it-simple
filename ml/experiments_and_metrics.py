"""
Эксперименты и метрики для AI-тьютора.
"""

import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Tuple
import hashlib

from ai_tutor import mistral_generate, generate_trace_id
from config import validate_config
from langfuse_integration import trace_mistral_call, calculate_cost_estimate

class ExperimentRunner:
    """Запуск экспериментов и сбор метрик."""
    
    def __init__(self):
        self.config = validate_config()
        self.results = []
        self.metrics_summary = {}
        
    def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Запуск одного тестового случая.
        
        Args:
            test_case: Описание тестового случая
        
        Returns:
            Результаты выполнения
        """
        print(f"\n🧪 Запуск теста: {test_case['name']}")
        print(f"   Тип: {test_case.get('type', 'unknown')}")
        
        start_time = time.time()
        
        # Подготавливаем промпт в зависимости от типа
        if test_case["type"] == "entry_test":
            from prompt_templates import PromptTemplates
            prompt = PromptTemplates.ENTRY_TEST_PROMPT.format(
                course_title=test_case["data"]["course_title"],
                topics=", ".join(test_case["data"]["topics"])
            )
        elif test_case["type"] == "course_graph":
            from prompt_templates import PromptTemplates
            prompt = PromptTemplates.COURSE_GRAPH_PROMPT.format(
                interests=", ".join(test_case["data"]["student_profile"]["interests"]),
                knowledge_gaps=", ".join(test_case["data"]["student_profile"]["knowledge_gaps"]),
                course_title=test_case["data"]["course_title"],
                topics=", ".join(test_case["data"]["topics"])
            )
        else:
            prompt = test_case.get("prompt", "")
        
        # Генерируем trace_id
        trace_id = generate_trace_id(prompt)
        
        # Выполняем запрос
        response = mistral_generate(
            prompt=prompt,
            temperature=test_case.get("temperature", 0.7),
            max_tokens=test_case.get("max_tokens", 1000),
            trace_id=trace_id
        )
        
        # Расчет метрик
        end_time = time.time()
        latency = end_time - start_time
        
        # Простой подсчет токенов (можно заменить на tiktoken для точности)
        prompt_tokens = len(prompt.split())
        completion_tokens = len(response.split())
        total_tokens = prompt_tokens + completion_tokens
        
        # Расчет стоимости
        cost = calculate_cost_estimate(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=self.config.get("model", "mistral-medium")
        )
        
        # Формируем результат
        result = {
            "test_id": test_case["id"],
            "name": test_case["name"],
            "type": test_case["type"],
            "trace_id": trace_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "latency_seconds": round(latency, 3),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost_usd": cost,
                "tokens_per_second": round(completion_tokens / latency, 2) if latency > 0 else 0,
                "success": True if response and "error" not in response.lower() else False
            },
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "response_preview": response[:100] + "..." if len(response) > 100 else response
        }
        
        # Трассировка в Langfuse
        if self.config.get("enable_langfuse", False):
            metadata = {
                "model": self.config.get("model", "mistral-medium"),
                "temperature": test_case.get("temperature", 0.7),
                "max_tokens": test_case.get("max_tokens", 1000),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "latency": latency,
                "success": result["metrics"]["success"],
                "retry_count": 0,  # Можно добавить из ответа mistral_generate
                "cost_usd": cost,
                "trace_name": f"Experiment: {test_case['name']}",
                "session_id": "experiment_session",
                "function": test_case["type"],
                "test_case": True
            }
            
            trace_mistral_call(
                prompt=prompt,
                response=response[:500],  # Ограничиваем для экономии токенов
                metadata=metadata,
                trace_id=trace_id
            )
        
        print(f"   ✅ Завершено за {latency:.2f}с, токены: {total_tokens}, стоимость: ${cost:.6f}")
        
        return result
    
    def run_batch_experiments(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Запуск пакета экспериментов.
        
        Args:
            test_cases: Список тестовых случаев
        
        Returns:
            Сводка по всем экспериментам
        """
        print("\n" + "="*60)
        print("🚀 ЗАПУСК ЭКСПЕРИМЕНТОВ И СБОР МЕТРИК")
        print("="*60)
        
        self.results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] ", end="")
            try:
                result = self.run_test_case(test_case)
                self.results.append(result)
            except Exception as e:
                print(f"❌ Ошибка в тесте {test_case['name']}: {e}")
                error_result = {
                    "test_id": test_case["id"],
                    "name": test_case["name"],
                    "type": test_case["type"],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "metrics": {"success": False}
                }
                self.results.append(error_result)
        
        # Анализ результатов
        self.analyze_results()
        
        # Вывод сводки
        self.print_summary()
        
        # Сохранение результатов
        self.save_results()
        
        return self.metrics_summary
    
    def analyze_results(self):
        """Анализ собранных результатов."""
        successful_results = [r for r in self.results if r["metrics"].get("success", False)]
        
        if not successful_results:
            self.metrics_summary = {"error": "Нет успешных результатов"}
            return
        
        # Базовые метрики
        latencies = [r["metrics"]["latency_seconds"] for r in successful_results]
        prompt_tokens = [r["metrics"]["prompt_tokens"] for r in successful_results]
        completion_tokens = [r["metrics"]["completion_tokens"] for r in successful_results]
        costs = [r["metrics"]["cost_usd"] for r in successful_results]
        
        self.metrics_summary = {
            "total_tests": len(self.results),
            "successful_tests": len(successful_results),
            "success_rate": len(successful_results) / len(self.results) * 100,
            
            "latency": {
                "mean": statistics.mean(latencies) if latencies else 0,
                "median": statistics.median(latencies) if latencies else 0,
                "min": min(latencies) if latencies else 0,
                "max": max(latencies) if latencies else 0,
                "std": statistics.stdev(latencies) if len(latencies) > 1 else 0
            },
            
            "tokens": {
                "total_prompt": sum(prompt_tokens),
                "total_completion": sum(completion_tokens),
                "avg_prompt": statistics.mean(prompt_tokens) if prompt_tokens else 0,
                "avg_completion": statistics.mean(completion_tokens) if completion_tokens else 0,
                "avg_total": statistics.mean([p+c for p,c in zip(prompt_tokens, completion_tokens)])
            },
            
            "cost": {
                "total_usd": sum(costs),
                "avg_per_test": statistics.mean(costs) if costs else 0,
                "cost_per_1000_tokens": (sum(costs) / sum([p+c for p,c in zip(prompt_tokens, completion_tokens)])) * 1000 if sum(prompt_tokens + completion_tokens) > 0 else 0
            },
            
            "throughput": {
                "avg_tokens_per_second": statistics.mean([r["metrics"].get("tokens_per_second", 0) for r in successful_results]) if successful_results else 0
            }
        }
    
    def print_summary(self):
        """Вывод сводки по экспериментам."""
        print("\n" + "="*60)
        print("📊 СВОДКА ЭКСПЕРИМЕНТОВ")
        print("="*60)
        
        if not self.metrics_summary:
            print("Нет данных для анализа")
            return
        
        print(f"\n📈 Общая статистика:")
        print(f"   Всего тестов: {self.metrics_summary['total_tests']}")
        print(f"   Успешных: {self.metrics_summary['successful_tests']}")
        print(f"   Успешность: {self.metrics_summary['success_rate']:.1f}%")
        
        print(f"\n⏱️  Задержка (latency):")
        latency = self.metrics_summary['latency']
        print(f"   Средняя: {latency['mean']:.2f}с")
        print(f"   Медиана: {latency['median']:.2f}с")
        print(f"   Min-Max: {latency['min']:.2f}с - {latency['max']:.2f}с")
        print(f"   Стандартное отклонение: {latency['std']:.2f}с")
        
        print(f"\n🔤 Токены:")
        tokens = self.metrics_summary['tokens']
        print(f"   Всего промпт: {tokens['total_prompt']}")
        print(f"   Всего ответ: {tokens['total_completion']}")
        print(f"   Всего: {tokens['total_prompt'] + tokens['total_completion']}")
        print(f"   Средний запрос: {tokens['avg_total']:.0f} токенов")
        
        print(f"\n💰 Стоимость:")
        cost = self.metrics_summary['cost']
        print(f"   Всего: ${cost['total_usd']:.6f}")
        print(f"   Средняя за тест: ${cost['avg_per_test']:.6f}")
        print(f"   За 1000 токенов: ${cost['cost_per_1000_tokens']:.6f}")
        
        print(f"\n⚡ Пропускная способность:")
        throughput = self.metrics_summary['throughput']
        print(f"   Средняя: {throughput['avg_tokens_per_second']:.1f} токенов/сек")
        
        print("\n" + "="*60)
    
    def save_results(self, filename: str = "experiment_results.json"):
        """
        Сохранение результатов экспериментов в файл.
        
        Args:
            filename: Имя файла для сохранения
        """
        output = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "model": self.config.get("model"),
                "temperature": self.config.get("temperature"),
                "max_tokens": self.config.get("max_tokens")
            },
            "results": self.results,
            "summary": self.metrics_summary
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Результаты сохранены в {filename}")

# Тестовые случаи для экспериментов
DEFAULT_TEST_CASES = [
    {
        "id": "exp_1",
        "name": "Входной тест - базовый английский",
        "type": "entry_test",
        "data": {
            "course_title": "Английский язык для начинающих",
            "topics": ["Present Simple", "Артикли a/an/the", "Базовая лексика"]
        },
        "temperature": 0.7,
        "max_tokens": 1500
    },
    {
        "id": "exp_2",
        "name": "Входной тест - средний уровень",
        "type": "entry_test",
        "data": {
            "course_title": "Английский для среднего уровня",
            "topics": ["Past Continuous", "Present Perfect", "Условные предложения"]
        },
        "temperature": 0.7,
        "max_tokens": 1500
    },
    {
        "id": "exp_3",
        "name": "Граф курса для геймера",
        "type": "course_graph",
        "data": {
            "student_profile": {
                "interests": ["видеоигры", "футбол", "технологии"],
                "knowledge_gaps": ["present_simple", "prepositions"]
            },
            "course_title": "Английский язык для начинающих",
            "topics": ["Present Simple", "Артикли", "Базовая лексика", "Предлоги", "Вопросы"]
        },
        "temperature": 0.5,
        "max_tokens": 1000
    },
    {
        "id": "exp_4",
        "name": "Граф курса для бизнеса",
        "type": "course_graph",
        "data": {
            "student_profile": {
                "interests": ["бизнес", "финансы", "переговоры"],
                "knowledge_gaps": ["business_vocabulary", "formal_writing"]
            },
            "course_title": "Деловой английский",
            "topics": ["Деловая переписка", "Презентации", "Переговоры", "Финансовая лексика"]
        },
        "temperature": 0.5,
        "max_tokens": 1000
    },
    {
        "id": "exp_5",
        "name": "Короткий промпт - приветствие",
        "type": "custom",
        "prompt": "Напиши приветственное сообщение для нового студента английского языка.",
        "temperature": 0.8,
        "max_tokens": 200
    },
    {
        "id": "exp_6",
        "name": "Средний промпт - объяснение грамматики",
        "type": "custom",
        "prompt": "Объясни разницу между Present Simple и Present Continuous на русском языке. Приведи 3 примера для каждого времени.",
        "temperature": 0.6,
        "max_tokens": 500
    },
    {
        "id": "exp_7",
        "name": "Длинный промпт - план урока",
        "type": "custom",
        "prompt": """Создай подробный план урока по теме "Present Perfect" для студентов среднего уровня.
Урок должен длиться 60 минут и включать:
1. Введение в тему (5 мин)
2. Объяснение правил (15 мин)
3. Практические упражнения (25 мин)
4. Проверка понимания (10 мин)
5. Домашнее задание (5 мин)

Предоставь примеры упражнений и материалов.""",
        "temperature": 0.7,
        "max_tokens": 800
    },
    {
        "id": "exp_8",
        "name": "Сложный промпт - анализ ошибок",
        "type": "custom",
        "prompt": """Проанализируй следующие ошибки студента и предложи упражнения для их исправления:

Ошибки:
1. "I have see that movie yesterday." (вместо "I saw that movie yesterday.")
2. "She don't like coffee." (вместо "She doesn't like coffee.")
3. "They was happy." (вместо "They were happy.")

Объясни каждую ошибку на русском и предложи 2 упражнения для каждой.""",
        "temperature": 0.6,
        "max_tokens": 600
    },
    {
        "id": "exp_9",
        "name": "JSON генерация - список тем",
        "type": "custom",
        "prompt": """Верни JSON с 5 темами для курса "Английский для путешествий".
Формат:
{
  "topics": [
    {
      "id": "1",
      "title": "Название темы",
      "description": "Описание темы",
      "difficulty": "beginner/intermediate/advanced"
    }
  ]
}""",
        "temperature": 0.3,
        "max_tokens": 400
    },
    {
        "id": "exp_10",
        "name": "Креативный промпт - диалог",
        "type": "custom",
        "prompt": """Напиши диалог на английском между учителем и студентом на тему "Планы на выходные".
Диалог должен:
- Быть естественным и реалистичным
- Включать 6-8 реплик
- Использовать будущее время (Future Simple)
- Быть подходящим для уровня intermediate""",
        "temperature": 0.9,
        "max_tokens": 300
    }
]

def run_demo_experiments():
    """Запуск демонстрационных экспериментов."""
    print("\n" + "="*60)
    print("🧪 ДЕМОНСТРАЦИЯ ЭКСПЕРИМЕНТОВ И МЕТРИК")
    print("="*60)
    
    # Проверяем конфигурацию
    config = validate_config()
    print(f"\nМодель: {config.get('model')}")
    print(f"Temperature: {config.get('temperature')}")
    print(f"Langfuse: {'✅ Включен' if config.get('enable_langfuse') else '❌ Выключен'}")
    
    # Создаем раннер
    runner = ExperimentRunner()
    
    # Запускаем эксперименты
    print(f"\nЗапускаю {len(DEFAULT_TEST_CASES)} тестовых случаев...")
    
    # Можно запустить все или часть тестов
    test_cases_to_run = DEFAULT_TEST_CASES  # Все тесты
    # test_cases_to_run = DEFAULT_TEST_CASES[:5]  # Первые 5 тестов
    
    summary = runner.run_batch_experiments(test_cases_to_run)
    
    # Сохраняем результаты
    runner.save_results("demo_experiment_results.json")
    
    # Вывод ссылки на Langfuse если включен
    if config.get("enable_langfuse") and runner.results:
        print("\n🔗 Доступ к метрикам в Langfuse:")
        print("   https://cloud.langfuse.com")
        print("   (требуется авторизация с вашими ключами)")
    
    print("\n" + "="*60)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*60)
    
    return summary

if __name__ == "__main__":
    run_demo_experiments()
