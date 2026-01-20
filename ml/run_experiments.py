#!/usr/bin/env python3
"""
Скрипт запуска экспериментов с AI-тьютором.
"""

import sys
import argparse
from experiments_and_metrics import ExperimentRunner, DEFAULT_TEST_CASES, run_demo_experiments

def main():
    parser = argparse.ArgumentParser(description='Запуск экспериментов AI-тьютора')
    parser.add_argument('--demo', action='store_true', help='Запуск демо экспериментов')
    parser.add_argument('--tests', type=int, default=10, help='Количество тестов для запуска')
    parser.add_argument('--output', type=str, default='experiment_results.json', help='Файл для сохранения результатов')
    parser.add_argument('--list-tests', action='store_true', help='Показать список тестовых случаев')
    
    args = parser.parse_args()
    
    if args.list_tests:
        print("\n📋 ДОСТУПНЫЕ ТЕСТОВЫЕ СЛУЧАИ:")
        print("="*50)
        for i, test in enumerate(DEFAULT_TEST_CASES, 1):
            print(f"\n{i}. {test['name']}")
            print(f"   Тип: {test['type']}")
            print(f"   ID: {test['id']}")
            if test.get('prompt'):
                print(f"   Промпт: {test['prompt'][:80]}...")
        return
    
    if args.demo:
        run_demo_experiments()
    else:
        runner = ExperimentRunner()
        
        # Выбираем тесты для запуска
        tests_to_run = DEFAULT_TEST_CASES[:args.tests]
        
        print(f"\n🚀 Запускаю {len(tests_to_run)} экспериментов...")
        summary = runner.run_batch_experiments(tests_to_run)
        
        # Сохраняем результаты
        runner.save_results(args.output)
        
        print(f"\n✅ Результаты сохранены в {args.output}")

if __name__ == "__main__":
    main()
