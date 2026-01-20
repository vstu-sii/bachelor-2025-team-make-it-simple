"""
Модуль для A/B тестирования промптов AI-тьютора.
"""

import hashlib
import random
import json
import time
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ai_tutor import mistral_generate
from langfuse_integration import trace_mistral_call, calculate_cost_estimate
from config import validate_config

class PromptVariant(Enum):
    """Варианты промптов для A/B тестирования."""
    VARIANT_A = "A"  # Базовый вариант
    VARIANT_B = "B"  # Оптимизированный вариант
    VARIANT_C = "C"  # Экспериментальный вариант

@dataclass
class ExperimentResult:
    """Результат эксперимента."""
    variant: PromptVariant
    prompt: str
    response: str
    metrics: Dict[str, Any]
    timestamp: datetime
    trace_id: Optional[str] = None

class ABTestingManager:
    """Менеджер A/B тестирования промптов."""
    
    def __init__(self):
        self.config = validate_config()
        self.experiments = {}
        self.results = []
        
    def register_experiment(self, experiment_id: str, variants: Dict[PromptVariant, str]):
        """
        Регистрация эксперимента.
        
        Args:
            experiment_id: Уникальный ID эксперимента
            variants: Словарь с вариантами промптов
        """
        self.experiments[experiment_id] = variants
        print(f"✅ Эксперимент зарегистрирован: {experiment_id} с {len(variants)} вариантами")
    
    def get_variant(self, experiment_id: str, user_id: str = None) -> Tuple[PromptVariant, str]:
        """
        Получение варианта промпта для пользователя.
        
        Args:
            experiment_id: ID эксперимента
            user_id: ID пользователя (для консистентности)
            
        Returns:
            Кортеж (вариант, промпт)
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Эксперимент {experiment_id} не зарегистрирован")
        
        variants = self.experiments[experiment_id]
        
        # Если user_id предоставлен, детерминированный выбор
        if user_id:
            # Хэшируем user_id для детерминированного распределения
            user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
            variant_idx = user_hash % len(variants)
            variant = list(variants.keys())[variant_idx]
        else:
            # Случайный выбор
            variant = random.choice(list(variants.keys()))
        
        prompt = variants[variant]
        return variant, prompt
    
    def run_experiment(self, experiment_id: str, input_data: Dict[str, Any], 
                      user_id: str = None, metadata: Dict[str, Any] = None) -> ExperimentResult:
        """
        Запуск одного экспериментального запроса.
        
        Args:
            experiment_id: ID эксперимента
            input_data: Входные данные для промпта
            user_id: ID пользователя
            metadata: Дополнительные метаданные
            
        Returns:
            Результат эксперимента
        """
        if metadata is None:
            metadata = {}
        
        # Получаем вариант промпта
        variant, prompt_template = self.get_variant(experiment_id, user_id)
        
        # Форматируем промпт с входными данными
        try:
            prompt = prompt_template.format(**input_data)
        except KeyError as e:
            raise ValueError(f"Отсутствуют данные для промпта: {e}")
        
        print(f"🧪 Запуск эксперимента {experiment_id}, вариант {variant.value}")
        print(f"   Промпт: {prompt[:100]}...")
        
        # Генерируем trace_id для трассировки
        trace_id = f"ab_test_{experiment_id}_{variant.value}_{int(time.time())}"
        
        # Выполняем запрос
        start_time = time.time()
        response = mistral_generate(
            prompt=prompt,
            temperature=metadata.get("temperature", 0.7),
            max_tokens=metadata.get("max_tokens", 2000),
            trace_id=trace_id
        )
        latency = time.time() - start_time
        
        # Собираем метрики
        prompt_tokens = len(prompt.split())
        completion_tokens = len(response.split())
        total_tokens = prompt_tokens + completion_tokens
        
        metrics = {
            "latency": latency,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost_usd": calculate_cost_estimate(prompt_tokens, completion_tokens),
            "variant": variant.value,
            "experiment_id": experiment_id,
            "user_id": user_id,
            **metadata
        }
        
        # Трассировка в Langfuse
        langfuse_metadata = {
            "model": "mistral-medium",
            "temperature": metadata.get("temperature", 0.7),
            "max_tokens": metadata.get("max_tokens", 2000),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "latency": latency,
            "success": True,
            "experiment_id": experiment_id,
            "variant": variant.value,
            "trace_name": f"A/B Test - {experiment_id}",
            "session_id": user_id or "anonymous",
            "function": "ab_testing"
        }
        
        trace_mistral_call(
            prompt=prompt[:500],
            response=response[:1000],
            metadata=langfuse_metadata,
            trace_id=trace_id
        )
        
        # Создаем результат
        result = ExperimentResult(
            variant=variant,
            prompt=prompt,
            response=response,
            metrics=metrics,
            timestamp=datetime.now(),
            trace_id=trace_id
        )
        
        self.results.append(result)
        return result
    
    def run_batch_experiment(self, experiment_id: str, batch_inputs: List[Dict[str, Any]],
                           user_ids: List[str] = None, metadata: Dict[str, Any] = None) -> List[ExperimentResult]:
        """
        Запуск батча экспериментов.
        
        Args:
            experiment_id: ID эксперимента
            batch_inputs: Список входных данных
            user_ids: Список ID пользователей
            metadata: Дополнительные метаданные
            
        Returns:
            Список результатов
        """
        results = []
        
        print(f"🧪 Запуск батча экспериментов {experiment_id} ({len(batch_inputs)} запросов)")
        
        for i, input_data in enumerate(batch_inputs):
            user_id = user_ids[i] if user_ids and i < len(user_ids) else None
            
            try:
                result = self.run_experiment(
                    experiment_id=experiment_id,
                    input_data=input_data,
                    user_id=user_id,
                    metadata=metadata
                )
                results.append(result)
                print(f"   [{i+1}/{len(batch_inputs)}] Вариант {result.variant.value} завершен")
                
            except Exception as e:
                print(f"   [{i+1}/{len(batch_inputs)}] Ошибка: {e}")
        
        return results
    
    def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Анализ результатов эксперимента.
        
        Args:
            experiment_id: ID эксперимента
            
        Returns:
            Статистика по эксперименту
        """
        # Фильтруем результаты по experiment_id
        exp_results = [r for r in self.results if r.metrics.get("experiment_id") == experiment_id]
        
        if not exp_results:
            return {"error": f"Нет результатов для эксперимента {experiment_id}"}
        
        # Группируем по вариантам
        variant_results = {}
        for result in exp_results:
            variant = result.variant.value
            if variant not in variant_results:
                variant_results[variant] = []
            variant_results[variant].append(result)
        
        # Считаем статистику
        analysis = {
            "experiment_id": experiment_id,
            "total_requests": len(exp_results),
            "variants": {},
            "summary": {}
        }
        
        for variant, results in variant_results.items():
            latencies = [r.metrics["latency"] for r in results]
            prompt_tokens = [r.metrics["prompt_tokens"] for r in results]
            completion_tokens = [r.metrics["completion_tokens"] for r in results]
            costs = [r.metrics["cost_usd"] for r in results]
            
            # Проверяем валидность JSON ответов
            json_valid_count = 0
            for r in results:
                try:
                    json.loads(r.response)
                    json_valid_count += 1
                except:
                    pass
            
            variant_stats = {
                "request_count": len(results),
                "percentage": len(results) / len(exp_results) * 100,
                "latency": {
                    "mean": sum(latencies) / len(latencies) if latencies else 0,
                    "min": min(latencies) if latencies else 0,
                    "max": max(latencies) if latencies else 0,
                },
                "tokens": {
                    "prompt_mean": sum(prompt_tokens) / len(prompt_tokens) if prompt_tokens else 0,
                    "completion_mean": sum(completion_tokens) / len(completion_tokens) if completion_tokens else 0,
                    "total_mean": sum([p+c for p,c in zip(prompt_tokens, completion_tokens)]) / len(prompt_tokens) if prompt_tokens else 0,
                },
                "cost": {
                    "total": sum(costs),
                    "mean": sum(costs) / len(costs) if costs else 0,
                },
                "quality": {
                    "json_valid_percentage": json_valid_count / len(results) * 100 if results else 0,
                }
            }
            
            analysis["variants"][variant] = variant_stats
        
        # Определяем winner
        analysis["winner"] = self._determine_winner(analysis["variants"])
        
        return analysis
    
    def _determine_winner(self, variant_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Определение победителя эксперимента.
        
        Критерии:
        1. Качество (валидность JSON)
        2. Стоимость (ниже лучше)
        3. Latency (ниже лучше)
        4. Token usage (ниже лучше)
        """
        if not variant_stats:
            return {"variant": None, "reason": "Нет данных"}
        
        best_variant = None
        best_score = -float('inf')
        
        for variant, stats in variant_stats.items():
            # Балльная система
            score = 0
            
            # Качество (важность 40%)
            quality_score = stats["quality"]["json_valid_percentage"]
            score += quality_score * 0.4
            
            # Стоимость (важность 25%, инвертируем - чем дешевле, тем лучше)
            cost_mean = stats["cost"]["mean"]
            if cost_mean > 0:
                # Нормализуем: 1/стоимость
                cost_score = 1 / cost_mean
                # Масштабируем
                max_cost = max(s["cost"]["mean"] for s in variant_stats.values())
                min_cost = min(s["cost"]["mean"] for s in variant_stats.values())
                if max_cost > min_cost:
                    normalized_cost = (max_cost - cost_mean) / (max_cost - min_cost)
                    score += normalized_cost * 0.25 * 100
            
            # Latency (важность 20%, инвертируем)
            latency_mean = stats["latency"]["mean"]
            if latency_mean > 0:
                latency_score = 1 / latency_mean
                max_latency = max(s["latency"]["mean"] for s in variant_stats.values())
                min_latency = min(s["latency"]["mean"] for s in variant_stats.values())
                if max_latency > min_latency:
                    normalized_latency = (max_latency - latency_mean) / (max_latency - min_latency)
                    score += normalized_latency * 0.2 * 100
            
            # Token usage (важность 15%, инвертируем)
            total_tokens = stats["tokens"]["total_mean"]
            if total_tokens > 0:
                token_score = 1 / total_tokens
                max_tokens = max(s["tokens"]["total_mean"] for s in variant_stats.values())
                min_tokens = min(s["tokens"]["total_mean"] for s in variant_stats.values())
                if max_tokens > min_tokens:
                    normalized_tokens = (max_tokens - total_tokens) / (max_tokens - min_tokens)
                    score += normalized_tokens * 0.15 * 100
            
            if score > best_score:
                best_score = score
                best_variant = variant
        
        return {
            "variant": best_variant,
            "score": best_score,
            "reason": f"Лучший баланс качества, стоимости и производительности"
        }
    
    def save_results(self, filename: str = "ab_testing_results.json"):
        """Сохранение результатов экспериментов."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "experiments": list(self.experiments.keys()),
            "results": [
                {
                    "variant": r.variant.value,
                    "experiment_id": r.metrics.get("experiment_id"),
                    "timestamp": r.timestamp.isoformat(),
                    "metrics": r.metrics,
                    "trace_id": r.trace_id,
                    "prompt_preview": r.prompt[:200] + "..." if len(r.prompt) > 200 else r.prompt,
                    "response_preview": r.response[:200] + "..." if len(r.response) > 200 else r.response,
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Результаты сохранены в {filename}")
        return filename

# Создаем глобальный менеджер для использования
ab_testing_manager = ABTestingManager()
