"""
Интеграция с Langfuse для трассировки LLM вызовов.
Поддержка версии 3.12.0+.
"""

import os
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager

# Глобальная переменная для клиента Langfuse
_langfuse_client = None
_langfuse_available = None
_langfuse_version = None

def check_langfuse_available():
    """Проверка доступности Langfuse SDK."""
    global _langfuse_available, _langfuse_version
    
    if _langfuse_available is not None:
        return _langfuse_available
    
    try:
        import importlib.util
        
        # Проверяем наличие модуля
        spec = importlib.util.find_spec("langfuse")
        if spec is None:
            _langfuse_available = False
            return False
        
        # Импортируем и проверяем версию
        import langfuse
        _langfuse_version = getattr(langfuse, '__version__', 'unknown')
        
        if hasattr(langfuse, 'Langfuse'):
            _langfuse_available = True
        else:
            _langfuse_available = False
            
        return _langfuse_available
        
    except ImportError:
        _langfuse_available = False
        return False
    except Exception:
        _langfuse_available = False
        return False

def is_langfuse_available():
    """Публичная функция проверки доступности Langfuse."""
    return check_langfuse_available()

def init_langfuse():
    """
    Инициализация клиента Langfuse.
    
    Returns:
        Langfuse клиент или None если не настроен
    """
    global _langfuse_client
    
    if _langfuse_client is not None:
        return _langfuse_client
    
    # Проверяем доступность SDK
    if not check_langfuse_available():
        print("⚠️ Langfuse SDK не установлен.")
        print("Установите: pip install langfuse")
        return None
    
    try:
        from config import validate_config
        config = validate_config()
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return None
    
    if not config.get("enable_langfuse", False):
        print("ℹ️ Langfuse отключен в конфигурации")
        return None
    
    try:
        import langfuse
        
        secret_key = config.get("langfuse_secret_key", "")
        public_key = config.get("langfuse_public_key", "")
        host = config.get("langfuse_host", "https://cloud.langfuse.com")
        
        if not secret_key or not public_key:
            print("⚠️ Langfuse ключи не указаны в конфигурации")
            return None
        
        _langfuse_client = langfuse.Langfuse(
            secret_key=secret_key,
            public_key=public_key,
            host=host
        )
        print(f"✅ Langfuse клиент инициализирован")
        return _langfuse_client
        
    except ImportError as e:
        print(f"❌ Ошибка импорта Langfuse: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка инициализации Langfuse: {e}")
        return None

def trace_mistral_call(
    prompt: str,
    response: str,
    metadata: Dict[str, Any],
    trace_id: Optional[str] = None
):
    """
    Трассировка вызова к Mistral API в Langfuse.
    
    Args:
        prompt: Промпт отправленный в модель
        response: Ответ от модели
        metadata: Метаданные запроса
        trace_id: ID трассировки (опционально) - игнорируется в 3.12
        
    Returns:
        ID трассировки или None в случае ошибки
    """
    langfuse = init_langfuse()
    if not langfuse:
        return None
    
    try:
        print(f"📊 Начинаю трассировку вызова LLM")
        
        # В версии 3.12 trace создается автоматически при создании span
        # Создаем span для этого вызова
        span = langfuse.start_span(
            name=metadata.get("trace_name", "Mistral API Call"),
            metadata={
                "model": metadata.get("model", "unknown"),
                "temperature": metadata.get("temperature", 0.7),
                "max_tokens": metadata.get("max_tokens", 2000),
                "function": metadata.get("function", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "source": "ai_tutor",
                "trace_id": trace_id if trace_id else "auto_generated"
            }
        )
        
        # Обновляем trace (без id - он берется из текущего контекста)
        try:
            langfuse.update_current_trace(
                name=metadata.get("trace_name", "Mistral API Call"),
                session_id=metadata.get("session_id", "default_session"),
                user_id=metadata.get("user_id", "anonymous"),
                metadata={
                    "project": "AI Tutor",
                    "version": "1.0",
                    "model": metadata.get("model", "unknown"),
                    **metadata.get("trace_metadata", {})
                }
            )
        except TypeError:
            # Если update_current_trace не принимает параметры
            pass
        
        # Создаем observation для генерации
        observation = langfuse.start_observation(
            name=metadata.get("generation_name", "Mistral Generation"),
            as_type="generation",
            model=metadata.get("model", "mistral-medium"),
            input=prompt[:500],  # Ограничиваем длину промпта
            model_parameters={
                "temperature": metadata.get("temperature", 0.7),
                "max_tokens": metadata.get("max_tokens", 2000),
                "top_p": metadata.get("top_p", 0.95),
            },
            metadata={
                "prompt_tokens": metadata.get("prompt_tokens", 0),
                "start_time": time.time()
            }
        )
        
        # Обновляем observation с результатом
        observation.update(
            output=response[:1000],  # Ограничиваем длину ответа
            metadata={
                "completion_tokens": metadata.get("completion_tokens", 0),
                "total_tokens": metadata.get("total_tokens", 0),
                "latency": metadata.get("latency", 0),
                "success": metadata.get("success", True),
                "retry_count": metadata.get("retry_count", 0),
                "cost_usd": metadata.get("cost_usd", 0),
                "end_time": time.time()
            }
        )
        observation.end()
        
        # Завершаем span
        span.end()
        
        # Отправляем данные
        langfuse.flush()
        
        trace_id_actual = span.trace_id if hasattr(span, 'trace_id') else "unknown"
        print(f"✅ Трассировка завершена, trace_id: {trace_id_actual}")
        return trace_id_actual
        
    except Exception as e:
        print(f"⚠️ Ошибка при трассировке: {e}")
        import traceback
        traceback.print_exc()
        return None

def trace_function_call(
    function_name: str,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    metadata: Dict[str, Any] = None
):
    """
    Трассировка вызова функции AI-тьютора.
    
    Args:
        function_name: Название функции
        input_data: Входные данные
        output_data: Выходные данные
        metadata: Дополнительные метаданные
        
    Returns:
        ID трассировки или None
    """
    langfuse = init_langfuse()
    if not langfuse:
        return None
    
    if metadata is None:
        metadata = {}
    
    try:
        # Создаем span для функции
        span = langfuse.start_span(
            name=f"AI Tutor - {function_name}",
            metadata={
                "function": function_name,
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
        )
        
        # Логируем входные данные как observation
        input_obs = langfuse.start_observation(
            name="Function Input",
            as_type="event",
            input=str(input_data)[:500],
            metadata={"type": "function_input"}
        )
        input_obs.end()
        
        # Логируем выходные данные как observation
        output_obs = langfuse.start_observation(
            name="Function Output",
            as_type="event",
            output=str(output_data)[:500],
            metadata={"type": "function_output"}
        )
        output_obs.end()
        
        # Завершаем span
        span.end()
        
        langfuse.flush()
        trace_id = span.trace_id if hasattr(span, 'trace_id') else "unknown"
        print(f"✅ Функция {function_name} трассирована, trace_id: {trace_id}")
        return trace_id
        
    except Exception as e:
        print(f"⚠️ Ошибка при трассировке функции: {e}")
        return None

def calculate_cost_estimate(
    prompt_tokens: int,
    completion_tokens: int,
    model: str = "mistral-medium"
) -> float:
    """
    Расчет примерной стоимости запроса.
    """
    pricing = {
        "mistral-tiny": {"input": 0.14, "output": 0.42},
        "mistral-small": {"input": 0.20, "output": 0.60},
        "mistral-medium": {"input": 0.60, "output": 1.80},
        "mistral-large": {"input": 2.50, "output": 7.50},
    }
    
    model_pricing = pricing.get(model, pricing["mistral-medium"])
    
    input_cost = (prompt_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * model_pricing["output"]
    
    return round(input_cost + output_cost, 6)

def get_langfuse_dashboard_base_url() -> str:
    """
    Получение базового URL дашборда Langfuse.
    """
    try:
        from config import validate_config
        config = validate_config()
        return config.get("langfuse_host", "https://cloud.langfuse.com")
    except:
        return "https://cloud.langfuse.com"

def log_metrics_to_langfuse(
    metrics: Dict[str, Any],
    trace_id: Optional[str] = None
):
    """
    Логирование метрик в Langfuse.
    """
    langfuse = init_langfuse()
    if not langfuse:
        return
    
    try:
        # Создаем observation для метрик
        metrics_obs = langfuse.start_observation(
            name="AI Tutor Metrics",
            as_type="event",
            metadata={"metrics": metrics}
        )
        metrics_obs.end()
        
        langfuse.flush()
        print(f"📈 Метрики отправлены в Langfuse")
        
    except Exception as e:
        print(f"⚠️ Ошибка при логировании метрик: {e}")

@contextmanager
def trace_span(name: str, metadata: Dict[str, Any] = None):
    """
    Контекстный менеджер для создания span.
    
    Args:
        name: Название span
        metadata: Метаданные
        
    Yields:
        Span объект
    """
    langfuse = init_langfuse()
    
    if not langfuse:
        yield None
        return
    
    if metadata is None:
        metadata = {}
    
    span = None
    try:
        span = langfuse.start_span(name=name, metadata=metadata)
        yield span
    finally:
        if span:
            span.end()
            langfuse.flush()

@contextmanager
def trace_generation(name: str, model: str, input_text: str, metadata: Dict[str, Any] = None):
    """
    Контекстный менеджер для создания generation.
    
    Args:
        name: Название generation
        model: Модель
        input_text: Входной текст
        metadata: Метаданные
        
    Yields:
        Observation объект
    """
    langfuse = init_langfuse()
    
    if not langfuse:
        yield None
        return
    
    if metadata is None:
        metadata = {}
    
    observation = None
    try:
        observation = langfuse.start_observation(
            name=name,
            as_type="generation",
            model=model,
            input=input_text,
            metadata=metadata
        )
        yield observation
    finally:
        if observation:
            # Если не обновлено, завершаем как есть
            observation.end()
            langfuse.flush()

# Простая демонстрация работы
def simple_demo():
    """Простая демонстрация работы Langfuse."""
    print("\n🧪 Простая демонстрация Langfuse:")
    
    langfuse = init_langfuse()
    if not langfuse:
        print("❌ Langfuse не инициализирован")
        return
    
    # Создаем span
    span = langfuse.start_span(
        name="Demo Span",
        metadata={"demo": True, "timestamp": time.time()}
    )
    
    print(f"✅ Span создан: {span.id}")
    
    # Создаем generation
    gen = langfuse.start_observation(
        name="Demo Generation",
        as_type="generation",
        model="demo-model",
        input="Demo input"
    )
    
    gen.update(output="Demo output", metadata={"demo": True})
    gen.end()
    
    print(f"✅ Generation создан: {gen.id}")
    
    # Завершаем span
    span.end()
    
    # Отправляем
    langfuse.flush()
    
    print(f"✅ Данные отправлены")
    print(f"📊 Trace ID: {span.trace_id if hasattr(span, 'trace_id') else 'unknown'}")

# Демонстрация работы
if __name__ == "__main__":
    print("="*60)
    print("ДЕМОНСТРАЦИЯ ИНТЕГРАЦИИ LANGfUSE 3.12")
    print("="*60)
    
    # Проверяем доступность
    if not check_langfuse_available():
        print("\n⚠️ Langfuse SDK не установлен.")
        print("Установите: pip install langfuse")
    else:
        print(f"\n✅ Langfuse SDK доступен")
    
    # Инициализируем
    langfuse_client = init_langfuse()
    
    if langfuse_client:
        print("\n✅ Langfuse настроен и готов к работе")
        
        # Простая демонстрация
        simple_demo()
        
        # Демонстрация с метриками
        print("\n📊 Демонстрация с метриками:")
        
        metadata = {
            "model": "mistral-medium",
            "temperature": 0.7,
            "max_tokens": 1000,
            "prompt_tokens": 150,
            "completion_tokens": 350,
            "total_tokens": 500,
            "latency": 2.5,
            "success": True,
            "retry_count": 0,
            "cost_usd": 0.00123,
            "trace_name": "Demo Trace",
            "session_id": "demo_session",
            "function": "demo_generation"
        }
        
        trace_id = trace_mistral_call(
            prompt="What is the capital of France?",
            response="The capital of France is Paris.",
            metadata=metadata
        )
        
        if trace_id:
            print(f"✅ Trace создан: {trace_id}")
            
            # Демонстрация функции
            func_trace_id = trace_function_call(
                function_name="generate_entry_test",
                input_data={"course_title": "English for Beginners"},
                output_data={"questions": 12, "status": "success"},
                metadata={"demo": True}
            )
            
            if func_trace_id:
                print(f"✅ Функция трассирована: {func_trace_id}")
        
        print("\n✅ Демонстрация завершена")
        
    else:
        print("\n❌ Langfuse не инициализирован")
        print("Проверьте настройки в .env файле")
    
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*60)