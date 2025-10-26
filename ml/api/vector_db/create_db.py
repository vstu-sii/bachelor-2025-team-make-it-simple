import os
import numpy as np
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Попробуем импортировать PDF-ридеры с обработкой ошибок
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    try:
        import pypdf
        PDF_SUPPORT = True
    except ImportError:
        PDF_SUPPORT = False
        print("Предупреждение: Установите PyPDF2 или pypdf для работы с PDF файлами")

try:
    import ollama
    OLLAMA_SUPPORT = True
except ImportError:
    OLLAMA_SUPPORT = False
    print("Предупреждение: Установите ollama для работы с моделями")

class LocalEmbedder:
    """Локальный эмбеддер на основе TF-IDF"""
    def __init__(self):
        self.vectorizer = None
        self.is_fitted = False
        
    def fit(self, texts):
        """Обучение TF-IDF модели на текстах"""
        if not texts:
            return
            
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            min_df=1,
            max_df=0.95,
            stop_words=None,
            ngram_range=(1, 2)
        )
        self.vectorizer.fit(texts)
        self.is_fitted = True
    
    def transform(self, texts):
        """Преобразование текстов в векторы"""
        if not self.is_fitted or self.vectorizer is None:
            # Если модель не обучена, создаем простые векторы на основе длины
            if isinstance(texts, list):
                return np.ones((len(texts), 1))
            else:
                return np.ones((1, 1))
        
        return self.vectorizer.transform(texts).toarray()
    
    def encode(self, texts):
        """Алиас для transform"""
        if isinstance(texts, str):
            texts = [texts]
        return self.transform(texts)

class CourseVectorDB:
    def __init__(self, db_path="course_vector_db"):
        self.db_path = db_path
        self.embeddings_path = f"{db_path}/embeddings.npy"
        self.metadata_path = f"{db_path}/metadata.pkl"
        self.chunks_path = f"{db_path}/chunks.pkl"
        
        # Используем локальный TF-IDF эмбеддер
        self.embedding_model = LocalEmbedder()
        print("Используется локальный TF-IDF эмбеддер")
        
        # Создание директории если не существует
        os.makedirs(db_path, exist_ok=True)
        
        # Загрузка существующей базы данных
        self.embeddings = None
        self.metadata = []
        self.chunks = []
        self._load_existing_db()
        
        # Обучаем эмбеддер на существующих данных
        if self.chunks:
            print(f"Обучение TF-IDF модели на {len(self.chunks)} существующих чанках...")
            self.embedding_model.fit(self.chunks)
            # Пересчитываем эмбеддинги для всех существующих чанков
            if self.chunks:
                self.embeddings = self.embedding_model.encode(self.chunks)
                self._save_db()
    
    def _load_existing_db(self):
        """Загрузка существующей векторной базы данных"""
        if os.path.exists(self.embeddings_path):
            self.embeddings = np.load(self.embeddings_path)
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        if os.path.exists(self.chunks_path):
            with open(self.chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)
    
    def _save_db(self):
        """Сохранение векторной базы данных"""
        if self.embeddings is not None:
            np.save(self.embeddings_path, self.embeddings)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        with open(self.chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
    
    def extract_text_from_pdf(self, pdf_path):
        """Извлечение текста из PDF файла"""
        if not PDF_SUPPORT:
            print("Ошибка: Не установлены библиотеки для работы с PDF")
            return ""
            
        try:
            # Пробуем разные PDF ридеры
            if 'PyPDF2' in globals():
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text_content = page.extract_text()
                        if text_content:
                            text += text_content + "\n"
                    return text
            elif 'pypdf' in globals():
                with open(pdf_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text_content = page.extract_text()
                        if text_content:
                            text += text_content + "\n"
                    return text
        except Exception as e:
            print(f"Ошибка при чтении PDF {pdf_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, txt_path):
        """Извлечение текста из TXT файла"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(txt_path, 'r', encoding='cp1251') as file:
                    return file.read()
            except Exception as e:
                print(f"Ошибка при чтении TXT {txt_path}: {e}")
                return ""
        except Exception as e:
            print(f"Ошибка при чтении TXT {txt_path}: {e}")
            return ""
    
    def clean_text(self, text):
        """Очистка текста от лишних пробелов и символов"""
        if not text:
            return ""
        # Удаляем множественные пробелы и переносы
        text = re.sub(r'\s+', ' ', text)
        # Удаляем специальные символы, но оставляем буквы, цифры и пунктуацию
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\(\)]', '', text)
        return text.strip()
    
    def chunk_text(self, text, chunk_size=500, overlap=50):
        """Разбивка текста на перекрывающиеся чанки"""
        # Очищаем текст
        text = self.clean_text(text)
        words = text.split()
        chunks = []
        
        if len(words) < 10:
            return chunks
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            # Игнорировать слишком короткие фразы (меньше 10 слов)
            if len(chunk.split()) > 10:
                chunks.append(chunk)
        
        return chunks
    
    def add_file_to_db(self, file_path, course_name="unknown"):
        """Добавление информации из файла в векторную базу"""
        print(f"Добавление файла: {file_path}")
        
        # Извлечение текста в зависимости от типа файла
        if file_path.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.txt'):
            text = self.extract_text_from_txt(file_path)
        else:
            print(f"Неподдерживаемый формат файла: {file_path}")
            return
        
        if not text:
            print(f"Не удалось извлечь текст из {file_path}")
            return
        
        # Разбивка на чанки
        chunks = self.chunk_text(text)
        print(f"Создано {len(chunks)} чанков")
        
        if not chunks:
            print("Нет подходящих чанков для добавления")
            return
        
        # Временно сохраняем новые чанки
        temp_chunks = self.chunks + chunks
        
        # Переобучаем модель на всех данных (старых + новых)
        print("Переобучение модели на всех данных...")
        self.embedding_model.fit(temp_chunks)
        
        # Создаем эмбеддинги для всех чанков
        all_embeddings = self.embedding_model.encode(temp_chunks)
        
        # Обновляем базу данных
        self.embeddings = all_embeddings
        self.chunks = temp_chunks
        
        # Добавляем метаданные для новых чанков
        start_idx = len(self.metadata)
        for i, chunk in enumerate(chunks):
            self.metadata.append({
                'course': course_name,
                'file': os.path.basename(file_path),
                'chunk_id': start_idx + i,
                'text_length': len(chunk.split())
            })
        
        # Сохранение базы данных
        self._save_db()
        print(f"Файл {file_path} успешно добавлен в базу данных")
    
    def add_directory_to_db(self, directory_path, course_name="unknown"):
        """Добавление всех поддерживаемых файлов из директории"""
        if not os.path.exists(directory_path):
            print(f"Директория {directory_path} не существует")
            return
            
        supported_extensions = ['.pdf', '.txt']
        count = 0
        for filename in os.listdir(directory_path):
            if any(filename.lower().endswith(ext) for ext in supported_extensions):
                file_path = os.path.join(directory_path, filename)
                self.add_file_to_db(file_path, course_name)
                count += 1
        
        if count == 0:
            print(f"В директории {directory_path} не найдено поддерживаемых файлов")
        else:
            print(f"Добавлено {count} файлов из директории {directory_path}")
    
    def search_relevant_chunks(self, query, k=10):
        """Поиск релевантных чанков по запросу с использованием косинусного сходства"""
        if self.embeddings is None or len(self.chunks) == 0:
            return []
        
        # Создание эмбеддинга для запроса
        query_embedding = self.embedding_model.encode([query])
        
        # Проверяем совпадение размерностей
        if query_embedding.shape[1] != self.embeddings.shape[1]:
            print(f"Размерность не совпадает: запрос {query_embedding.shape[1]}, база {self.embeddings.shape[1]}")
            print("Переобучаем модель...")
            self.embedding_model.fit(self.chunks)
            self.embeddings = self.embedding_model.encode(self.chunks)
            query_embedding = self.embedding_model.encode([query])
        
        # Вычисление косинусного сходства
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Получение индексов топ-K наиболее похожих чанков
        k = min(k, len(similarities))
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(similarities[idx]), self.metadata[idx]))
        
        return results
    
    def filter_important_sources(self, chunks, min_words=25, min_score=0.1):
        """Фильтрация важных источников - убирает короткие фразы"""
        important_chunks = []
        for chunk, score, metadata in chunks:
            words = chunk.split()
            # Фильтруем короткие фразы и выбираем содержательные блоки
            if len(words) > min_words and score > min_score:
                important_chunks.append((chunk, score, metadata))
        return important_chunks
    
    def extract_information(self, query, max_results=5):
        """Извлечение информации из базы данных по запросу"""
        print(f"Поиск информации по запросу: '{query}'")
        
        # Поиск релевантных чанков
        relevant_chunks = self.search_relevant_chunks(query, k=15)
        
        if not relevant_chunks:
            print("Релевантная информация не найдена")
            return []
        
        # Фильтрация: убираем короткие фразы и выбираем наиболее информативные
        important_chunks = self.filter_important_sources(relevant_chunks)
        
        # Берем топ результатов после фильтрации
        top_chunks = important_chunks[:max_results]
        
        if not top_chunks:
            print("После фильтрации не осталось релевантных результатов")
            return []
        
        print(f"Найдено {len(top_chunks)} релевантных блоков информации")
        
        results = []
        for i, (chunk, score, metadata) in enumerate(top_chunks, 1):
            print(f"\n--- Результат {i} (сходство: {score:.3f}) ---")
            print(f"Курс: {metadata['course']}")
            print(f"Файл: {metadata['file']}")
            print(f"Длина текста: {metadata['text_length']} слов")
            
            # Показываем начало текста (первые 300 символов)
            preview = chunk[:300] + "..." if len(chunk) > 300 else chunk
            print(f"Содержание:\n{preview}")
            
            results.append({
                'content': chunk,
                'similarity_score': score,
                'metadata': metadata,
                'rank': i
            })
        
        return results
    
    def get_db_stats(self):
        """Получение статистики базы данных"""
        courses = set()
        files = set()
        for m in self.metadata:
            courses.add(m['course'])
            files.add(m['file'])
        
        chunk_lengths = [m['text_length'] for m in self.metadata] if self.metadata else [0]
        
        stats = {
            'total_chunks': len(self.chunks),
            'total_courses': len(courses),
            'total_files': len(files),
            'average_chunk_length': np.mean(chunk_lengths) if chunk_lengths else 0
        }
        
        if self.embeddings is not None:
            stats['embedding_dimensions'] = self.embeddings.shape[1]
        
        return stats

class OllamaDeepSeek:
    def __init__(self, model_name="deepseek-r1:8b"):
        self.model_name = model_name
        
    def check_model(self):
        """Проверка доступности модели"""
        if not OLLAMA_SUPPORT:
            print("Ollama не установлен. Установите: pip install ollama")
            return False
        try:
            models = ollama.list()
            available_models = [model['name'] for model in models['models']]
            if self.model_name not in available_models:
                print(f"Модель {self.model_name} не найдена. Доступные модели: {available_models}")
                return False
            return True
        except Exception as e:
            print(f"Ошибка при проверке моделей: {e}")
            return False
    
    def generate_answer(self, query, context_chunks):
        """Генерация ответа на основе контекста используя DeepSeek"""
        if not self.check_model():
            return "Модель Ollama не доступна"
        
        # Объединение контекста
        context_text = "\n\n".join([f"Контекст {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)])
        
        prompt = f"""
        На основе предоставленного контекста курса, ответь на следующий вопрос:
        
        Вопрос: {query}
        
        Контекст:
        {context_text}
        
        Требования к ответу:
        - Точно основан на предоставленном контексте
        - Содержательный и информативный
        - Структурированный и понятный
        - Без выдумывания информации не из контекста
        
        Ответ:
        """
        
        try:
            response = ollama.generate(model=self.model_name, prompt=prompt)
            return response['response']
        except Exception as e:
            return f"Ошибка при обработке запроса: {e}"

def main():
    # Инициализация векторной базы данных
    vector_db = CourseVectorDB("bachelor-2025-team-make-it-simple/ml/api/vector_db/my_course_database/")
    
    # Вывод статистики
    stats = vector_db.get_db_stats()
    print(f"Статистика базы данных: {stats}")
    
    # Пример использования - добавление директории
    directory_path = "bachelor-2025-team-make-it-simple/ml/api/vector_db/pdf_files/"
    vector_db.add_directory_to_db(directory_path)
    
    # Обновленная статистика
    stats = vector_db.get_db_stats()
    print(f"\nОбновленная статистика: {stats}")
    
    # Пример поиска если есть данные
    if stats['total_chunks'] > 0:
        query = "семья"
        print(f"\nПример поиска по запросу: '{query}'")
        results = vector_db.extract_information(query)
        
        if results:
            print(f"\nНайдено {len(results)} релевантных блоков")
        else:
            print("По запросу ничего не найдено")

if __name__ == "__main__":
    main()
