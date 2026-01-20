"""
Модуль для оптимизации промптов AI-тьютора.
"""

import json
import re
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime

from prompt_variants import (
    analyze_prompt_token_usage, 
    calculate_readability,
    calculate_repetition_score,
    estimate_instruction_clarity,
    generate_optimized_prompt,
    PROMPT_BEST_PRACTICES
)

@dataclass
class PromptAnalysis:
    """Анализ промпта."""
    prompt: str
    token_usage: Dict[str, Any]
    readability_score: float
    repetition_score: float
    instruction_clarity: float
    optimization_suggestions: List[str]

class PromptOptimizer:
    """Оптимизатор промптов."""
    
    def __init__(self):
        self.analysis_history = []
        self.optimization_rules = PROMPT_BEST_PRACTICES
    
    def analyze_prompt(self, prompt: str, context: Dict[str, Any] = None) -> PromptAnalysis:
        """
        Полный анализ промпта.
        
        Args:
            prompt: Промпт для анализа
            context: Контекст использования
            
        Returns:
            Анализ промпта
        """
        if context is None:
            context = {}
        
        # Анализ использования токенов
        token_analysis = analyze_prompt_token_usage(prompt)
        
        # Оценка читаемости
        readability = calculate_readability(prompt)
        
        # Оценка повторений
        repetition = calculate_repetition_score(prompt)
        
        # Оценка четкости инструкций
        clarity = estimate_instruction_clarity(prompt)
        
        # Генерация рекомендаций по оптимизации
        suggestions = self._generate_optimization_suggestions(
            prompt, token_analysis, readability, repetition, clarity
        )
        
        analysis = PromptAnalysis(
            prompt=prompt,
            token_usage=token_analysis,
            readability_score=readability,
            repetition_score=repetition,
            instruction_clarity=clarity,
            optimization_suggestions=suggestions
        )
        
        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "prompt_preview": prompt[:200],
            "analysis": analysis,
            "context": context
        })
        
        return analysis
    
    def _generate_optimization_suggestions(self, prompt: str, token_analysis: Dict[str, Any],
                                         readability: float, repetition: float, clarity: float) -> List[str]:
        """Генерация рекомендаций по оптимизации."""
        suggestions = []
        
        # Рекомендации на основе метрик
        if token_analysis["total_words"] > 500:
            suggestions.append("Сократить длину промпта. Текущая длина: {} слов".format(
                token_analysis["total_words"]
            ))
        
        if readability < 60:
            suggestions.append("Упростить язык. Использовать более короткие предложения.")
        
        if repetition > 30:
            suggestions.append("Уменьшить повторы в тексте.")
        
        if clarity < 70:
            suggestions.append("Добавить более четкие инструкции о формате ответа.")
        
        # Структурные рекомендации
        if "```" not in prompt and "формат" not in prompt.lower():
            suggestions.append("Добавить явное указание формата ответа (например, JSON структуру).")
        
        if prompt.count('\n\n') < 2:
            suggestions.append("Лучше структурировать промпт с использованием пустых строк между разделами.")
        
        # Контентные рекомендации
        if not any(word in prompt.lower() for word in ["пример", "примеры", "example"]):
            suggestions.append("Добавить примеры ожидаемого ответа.")
        
        if "только json" not in prompt.lower() and "только json:" not in prompt.lower():
            suggestions.append("Явно указать 'Возвращай ТОЛЬКО JSON'.")
        
        return suggestions
    
    def optimize_prompt(self, prompt: str, target_metrics: Dict[str, Any] = None) -> Tuple[str, PromptAnalysis]:
        """
        Оптимизация промпта.
        
        Args:
            prompt: Исходный промпт
            target_metrics: Целевые метрики
            
        Returns:
            Кортеж (оптимизированный промпт, анализ)
        """
        if target_metrics is None:
            target_metrics = {
                "max_words": 400,
                "min_readability": 70,
                "max_repetition": 20,
                "min_clarity": 80
            }
        
        # Анализируем исходный промпт
        original_analysis = self.analyze_prompt(prompt)
        
        # Генерируем оптимизированную версию
        optimized = generate_optimized_prompt(prompt)
        
        # Анализируем оптимизированную версию
        optimized_analysis = self.analyze_prompt(optimized)
        
        # Проверяем улучшения
        improvements = self._calculate_improvements(original_analysis, optimized_analysis)
        
        print(f"📊 Результаты оптимизации:")
        print(f"   Слов: {original_analysis.token_usage['total_words']} → {optimized_analysis.token_usage['total_words']}")
        print(f"   Читаемость: {original_analysis.readability_score:.1f} → {optimized_analysis.readability_score:.1f}")
        print(f"   Четкость инструкций: {original_analysis.instruction_clarity:.1f} → {optimized_analysis.instruction_clarity:.1f}")
        
        if improvements["words_reduced"] > 0:
            print(f"   ✅ Сокращено слов: {improvements['words_reduced']} ({improvements['words_reduction_percent']:.1f}%)")
        
        return optimized, optimized_analysis
    
    def _calculate_improvements(self, original: PromptAnalysis, optimized: PromptAnalysis) -> Dict[str, Any]:
        """Расчет улучшений после оптимизации."""
        words_reduced = original.token_usage["total_words"] - optimized.token_usage["total_words"]
        words_reduction_percent = (words_reduced / original.token_usage["total_words"]) * 100 if original.token_usage["total_words"] > 0 else 0
        
        readability_improvement = optimized.readability_score - original.readability_score
        clarity_improvement = optimized.instruction_clarity - original.instruction_clarity
        repetition_improvement = original.repetition_score - optimized.repetition_score  # Меньше - лучше
        
        return {
            "words_reduced": max(0, words_reduced),
            "words_reduction_percent": max(0, words_reduction_percent),
            "readability_improvement": readability_improvement,
            "clarity_improvement": clarity_improvement,
            "repetition_improvement": repetition_improvement,
            "overall_improvement": (
                words_reduction_percent * 0.3 +
                readability_improvement * 0.25 +
                clarity_improvement * 0.3 +
                repetition_improvement * 0.15
            )
        }
    
    def batch_optimize_prompts(self, prompts: Dict[str, str]) -> Dict[str, Tuple[str, PromptAnalysis]]:
        """
        Пакетная оптимизация промптов.
        
        Args:
            prompts: Словарь {prompt_id: prompt}
            
        Returns:
            Словарь с оптимизированными промптами и анализом
        """
        results = {}
        
        print(f"🔄 Начинаю пакетную оптимизацию {len(prompts)} промптов...")
        
        for prompt_id, prompt in prompts.items():
            print(f"\n📝 Оптимизация: {prompt_id}")
            try:
                optimized, analysis = self.optimize_prompt(prompt)
                results[prompt_id] = (optimized, analysis)
                print(f"   ✅ Успешно оптимизирован")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                results[prompt_id] = (prompt, None)
        
        return results
    
    def generate_best_practices_report(self) -> Dict[str, Any]:
        """Генерация отчета с best practices."""
        if not self.analysis_history:
            return {"error": "Нет данных для анализа"}
        
        # Анализируем историю оптимизаций
        successful_optimizations = []
        failed_optimizations = []
        
        for record in self.analysis_history:
            if "improvements" in record:
                if record["improvements"]["words_reduction_percent"] > 10:
                    successful_optimizations.append(record)
                else:
                    failed_optimizations.append(record)
        
        # Извлекаем lessons learned
        lessons_learned = []
        
        if successful_optimizations:
            common_success_patterns = self._extract_patterns(successful_optimizations, success=True)
            lessons_learned.extend([
                "Успешные стратегии:",
                *[f"• {pattern}" for pattern in common_success_patterns]
            ])
        
        if failed_optimizations:
            common_failure_patterns = self._extract_patterns(failed_optimizations, success=False)
            lessons_learned.extend([
                "Избегать:",
                *[f"• {pattern}" for pattern in common_failure_patterns]
            ])
        
        # Рекомендации
        recommendations = {
            "before_optimization": [
                "Всегда анализируйте текущий промпт перед оптимизацией",
                "Определите целевые метрики (длина, читаемость, четкость)",
                "Учитывайте контекст использования промпта"
            ],
            "optimization_strategies": [
                "Начинайте с удаления избыточных приветствий и заключений",
                "Структурируйте промпт с помощью заголовков и списков",
                "Явно указывайте формат ответа",
                "Давайте конкретные примеры",
                "Используйте активный залог и повелительное наклонение"
            ],
            "after_optimization": [
                "Тестируйте оптимизированный промпт на реальных запросах",
                "Сравнивайте качество ответов до и после оптимизации",
                "Измеряйте сокращение использования токенов",
                "Документируйте изменения и их эффект"
            ]
        }
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_analyses": len(self.analysis_history),
            "successful_optimizations": len(successful_optimizations),
            "failed_optimizations": len(failed_optimizations),
            "lessons_learned": lessons_learned,
            "recommendations": recommendations,
            "best_practices": PROMPT_BEST_PRACTICES,
            "sample_metrics": {
                "target_word_count": "300-400 слов",
                "target_readability": ">70/100",
                "target_clarity": ">80/100",
                "target_repetition": "<20%"
            }
        }
        
        return report
    
    def _extract_patterns(self, optimizations: List[Dict[str, Any]], success: bool = True) -> List[str]:
        """Извлечение паттернов из оптимизаций."""
        patterns = []
        
        # Анализируем промпты
        all_prompts = [r.get("prompt_preview", "") for r in optimizations]
        
        # Ищем общие характеристики
        if success:
            # Что было в успешных оптимизациях
            if any("```" in p for p in all_prompts):
                patterns.append("Использование code blocks для примеров формата")
            if any("только json" in p.lower() for p in all_prompts):
                patterns.append("Явное указание формата ответа")
            if any("пример:" in p.lower() for p in all_prompts):
                patterns.append("Включение конкретных примеров")
        else:
            # Что было в неудачных оптимизациях
            if any(len(p.split()) > 500 for p in all_prompts):
                patterns.append("Слишком длинные промпты (>500 слов)")
            if any(p.count('\n\n') < 2 for p in all_prompts):
                patterns.append("Плохая структурированность")
            if any("возвращай" not in p.lower() for p in all_prompts):
                patterns.append("Нечеткие инструкции")
        
        return patterns
    
    def save_analysis_report(self, filename: str = "prompt_optimization_report.json"):
        """Сохранение отчета по оптимизации."""
        report = self.generate_best_practices_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Отчет сохранен в {filename}")
        return filename

# Создаем глобальный оптимизатор
prompt_optimizer = PromptOptimizer()
