import os
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns

class VectorDBAnalyzer:
    def __init__(self, db_path="course_vector_db"):
        self.db_path = db_path
        self.embeddings_path = f"{db_path}/embeddings.npy"
        self.metadata_path = f"{db_path}/metadata.pkl"
        self.chunks_path = f"{db_path}/chunks.pkl"
        
        self.embeddings = None
        self.metadata = []
        self.chunks = []
        
        self.load_database()
    
    def load_database(self):
        """Загрузка векторной базы данных"""
        print("=" * 60)
        print("АНАЛИЗ ВЕКТОРНОЙ БАЗЫ ДАННЫХ")
        print("=" * 60)
        
        if not os.path.exists(self.db_path):
            print(f"ОШИБКА: Директория {self.db_path} не существует!")
            return False
        
        # Загрузка эмбеддингов
        if os.path.exists(self.embeddings_path):
            self.embeddings = np.load(self.embeddings_path)
            print(f"УСПЕХ: Эмбеддинги загружены: {self.embeddings.shape}")
        else:
            print("ОШИБКА: Файл эмбеддингов не найден")
            return False
        
        # Загрузка метаданных
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            print(f"УСПЕХ: Метаданные загружены: {len(self.metadata)} записей")
        else:
            print("ОШИБКА: Файл метаданных не найден")
        
        # Загрузка чанков
        if os.path.exists(self.chunks_path):
            with open(self.chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)
            print(f"УСПЕХ: Текстовые чанки загружены: {len(self.chunks)} чанков")
        else:
            print("ОШИБКА: Файл чанков не найден")
        
        return True
    
    def print_basic_info(self):
        """Вывод основной информации о базе данных"""
        print("\n" + "=" * 60)
        print("ОСНОВНАЯ ИНФОРМАЦИЯ")
        print("=" * 60)
        
        if self.embeddings is None:
            print("ОШИБКА: Эмбеддинги не загружены")
            return
        
        print(f"Размерность эмбеддингов: {self.embeddings.shape}")
        print(f"Количество чанков: {len(self.chunks)}")
        print(f"Количество метаданных: {len(self.metadata)}")
        
        # Информация о курсах и файлах
        courses = set()
        files = set()
        for meta in self.metadata:
            courses.add(meta['course'])
            files.add(meta['file'])
        
        print(f"Количество курсов: {len(courses)}")
        print(f"Количество файлов: {len(files)}")
        
        # Длины чанков
        if self.metadata:
            chunk_lengths = [meta['text_length'] for meta in self.metadata]
            print(f"Средняя длина чанка: {np.mean(chunk_lengths):.1f} слов")
            print(f"Минимальная длина чанка: {np.min(chunk_lengths)} слов")
            print(f"Максимальная длина чанка: {np.max(chunk_lengths)} слов")
    
    def analyze_embeddings(self):
        """Детальный анализ эмбеддингов"""
        print("\n" + "=" * 60)
        print("АНАЛИЗ ЭМБЕДДИНГОВ")
        print("=" * 60)
        
        if self.embeddings is None:
            print("ОШИБКА: Эмбеддинги не загружены")
            return
        
        # Базовая статистика
        print("Статистика эмбеддингов:")
        print(f"   - Минимальное значение: {np.min(self.embeddings):.6f}")
        print(f"   - Максимальное значение: {np.max(self.embeddings):.6f}")
        print(f"   - Среднее значение: {np.mean(self.embeddings):.6f}")
        print(f"   - Стандартное отклонение: {np.std(self.embeddings):.6f}")
        
        # Нулевые векторы
        zero_vectors = np.all(self.embeddings == 0, axis=1)
        print(f"   - Нулевые векторы: {np.sum(zero_vectors)}")
        
        # Анализ по измерениям
        print(f"\nАнализ по измерениям (первые 10 из {self.embeddings.shape[1]}):")
        for dim in range(min(10, self.embeddings.shape[1])):
            dim_data = self.embeddings[:, dim]
            print(f"   Измерение {dim}: min={np.min(dim_data):.4f}, max={np.max(dim_data):.4f}, mean={np.mean(dim_data):.4f}")
    
    def analyze_similarity(self):
        """Анализ схожести между эмбеддингами"""
        print("\n" + "=" * 60)
        print("АНАЛИЗ СХОЖЕСТИ")
        print("=" * 60)
        
        if self.embeddings is None or len(self.embeddings) < 2:
            print("ОШИБКА: Недостаточно данных для анализа схожести")
            return
        
        # Вычисляем косинусную схожесть
        similarity_matrix = cosine_similarity(self.embeddings)
        
        # Исключаем диагональ (схожесть с самим собой)
        np.fill_diagonal(similarity_matrix, 0)
        
        print("Статистика схожести:")
        print(f"   - Средняя схожесть: {np.mean(similarity_matrix):.4f}")
        print(f"   - Минимальная схожесть: {np.min(similarity_matrix):.4f}")
        print(f"   - Максимальная схожесть: {np.max(similarity_matrix):.4f}")
        
        # Находим наиболее похожие пары
        max_sim_idx = np.unravel_index(np.argmax(similarity_matrix), similarity_matrix.shape)
        max_similarity = similarity_matrix[max_sim_idx]
        
        print(f"\nНаиболее похожие чанки:")
        print(f"   - Схожесть: {max_similarity:.4f}")
        print(f"   - Чанк {max_sim_idx[0]}: {self.chunks[max_sim_idx[0]][:100]}...")
        print(f"   - Чанк {max_sim_idx[1]}: {self.chunks[max_sim_idx[1]][:100]}...")
    
    def show_sample_embeddings(self, num_samples=5):
        """Показать примеры эмбеддингов"""
        print("\n" + "=" * 60)
        print("ПРИМЕРЫ ЭМБЕДДИНГОВ")
        print("=" * 60)
        
        if self.embeddings is None:
            print("ОШИБКА: Эмбеддинги не загружены")
            return
        
        num_samples = min(num_samples, len(self.embeddings))
        
        for i in range(num_samples):
            print(f"\nЧанк {i}:")
            print(f"   Текст: {self.chunks[i][:150]}...")
            print(f"   Длина: {len(self.chunks[i].split())} слов")
            if i < len(self.metadata):
                print(f"   Файл: {self.metadata[i]['file']}")
                print(f"   Курс: {self.metadata[i]['course']}")
            print(f"   Эмбеддинг (первые 10 значений):")
            embedding_preview = self.embeddings[i][:10]
            for j, val in enumerate(embedding_preview):
                print(f"      [{j}]: {val:.6f}")
    
    def analyze_by_course(self):
        """Анализ эмбеддингов по курсам"""
        print("\n" + "=" * 60)
        print("АНАЛИЗ ПО КУРСАМ")
        print("=" * 60)
        
        if not self.metadata:
            print("ОШИБКА: Метаданные не загружены")
            return
        
        # Группируем по курсам
        courses = {}
        for i, meta in enumerate(self.metadata):
            course = meta['course']
            if course not in courses:
                courses[course] = []
            courses[course].append(i)
        
        print("Распределение по курсам:")
        for course, indices in courses.items():
            print(f"   - {course}: {len(indices)} чанков")
            
            if len(indices) > 1 and self.embeddings is not None:
                # Средний эмбеддинг для курса
                course_embeddings = self.embeddings[indices]
                avg_embedding = np.mean(course_embeddings, axis=0)
                print(f"     Средняя норма эмбеддинга: {np.linalg.norm(avg_embedding):.4f}")
    
    def create_visualizations(self):
        """Создание визуализаций (если установлен matplotlib)"""
        print("\n" + "=" * 60)
        print("ВИЗУАЛИЗАЦИИ")
        print("=" * 60)
        
        if self.embeddings is None or len(self.embeddings) < 2:
            print("ОШИБКА: Недостаточно данных для визуализации")
            return
        
        try:
            # Гистограмма значений эмбеддингов
            plt.figure(figsize=(15, 5))
            
            plt.subplot(1, 3, 1)
            plt.hist(self.embeddings.flatten(), bins=50, alpha=0.7)
            plt.title('Распределение значений эмбеддингов')
            plt.xlabel('Значение')
            plt.ylabel('Частота')
            
            # Гистограмма длин чанков
            plt.subplot(1, 3, 2)
            if self.metadata:
                chunk_lengths = [meta['text_length'] for meta in self.metadata]
                plt.hist(chunk_lengths, bins=20, alpha=0.7, color='green')
                plt.title('Распределение длин чанков')
                plt.xlabel('Длина (слов)')
                plt.ylabel('Частота')
            
            # Heatmap схожести (только для первых 20 чанков)
            plt.subplot(1, 3, 3)
            num_show = min(20, len(self.embeddings))
            small_similarity = cosine_similarity(self.embeddings[:num_show])
            sns.heatmap(small_similarity, annot=True, fmt='.2f', cmap='YlOrRd')
            plt.title(f'Матрица схожести (первые {num_show} чанков)')
            
            plt.tight_layout()
            plt.savefig('embedding_analysis.png', dpi=150, bbox_inches='tight')
            print("УСПЕХ: Визуализации сохранены в файл 'embedding_analysis.png'")
            
        except ImportError:
            print("ОШИБКА: Для визуализации установите matplotlib и seaborn:")
            print("   pip install matplotlib seaborn")
        except Exception as e:
            print(f"ОШИБКА при создании визуализаций: {e}")
    
    def export_embeddings_info(self, filename="embeddings_report.txt"):
        """Экспорт информации об эмбеддингах в файл"""
        print(f"\nЭкспорт отчета в файл {filename}...")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("ОТЧЕТ О ВЕКТОРНОЙ БАЗЕ ДАННЫХ\n")
            f.write("=" * 50 + "\n\n")
            
            # Основная информация
            f.write("ОСНОВНАЯ ИНФОРМАЦИЯ:\n")
            f.write(f"- Размерность эмбеддингов: {self.embeddings.shape}\n")
            f.write(f"- Количество чанков: {len(self.chunks)}\n")
            f.write(f"- Количество метаданных: {len(self.metadata)}\n")
            
            # Детальная информация об эмбеддингах
            f.write("\nДЕТАЛЬНАЯ ИНФОРМАЦИЯ ОБ ЭМБЕДДИНГАХ:\n")
            for i in range(min(10, len(self.embeddings))):
                f.write(f"\nЧанк {i}:\n")
                f.write(f"Текст: {self.chunks[i][:200]}...\n")
                f.write(f"Эмбеддинг (норма): {np.linalg.norm(self.embeddings[i]):.4f}\n")
                f.write("Первые 20 значений: " + 
                       " ".join([f"{x:.4f}" for x in self.embeddings[i][:20]]) + "\n")
        
        print(f"УСПЕХ: Отчет сохранен в файл {filename}")

def main():
    # Анализ базы данных
    analyzer = VectorDBAnalyzer("bachelor-2025-team-make-it-simple/ml/api/vector_db/my_course_database/")
    
    # Если база загружена успешно, проводим анализ
    if analyzer.embeddings is not None:
        # Основная информация
        analyzer.print_basic_info()
        
        # Детальный анализ эмбеддингов
        analyzer.analyze_embeddings()
        
        # Анализ схожести
        analyzer.analyze_similarity()
        
        # Примеры эмбеддингов
        analyzer.show_sample_embeddings()
        
        # Анализ по курсам
        analyzer.analyze_by_course()
        
        # Визуализации
        analyzer.create_visualizations()
        
        # Экспорт отчета
        analyzer.export_embeddings_info()
        
        print("\n" + "=" * 60)
        print("АНАЛИЗ ЗАВЕРШЕН")
        print("=" * 60)
    else:
        print("\nОШИБКА: Не удалось загрузить базу данных для анализа")

if __name__ == "__main__":
    main()