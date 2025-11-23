import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class VectorStore:
    def __init__(self, course_id):
        self.course_id = course_id
        self.vectorizer = TfidfVectorizer()
        self.documents = []
        self.vectors = None
        self.load_data()
    
    def load_data(self):
        data_path = f"ml/api/vector_db/{self.course_id}/documents.json"
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.documents = data.get('documents', [])
                
            if self.documents:
                self.vectors = self.vectorizer.fit_transform([doc['text'] for doc in self.documents])
    
    def save_data(self):
        os.makedirs(f"ml/api/vector_db/{self.course_id}", exist_ok=True)
        data_path = f"ml/api/vector_db/{self.course_id}/documents.json"
        
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump({"documents": self.documents}, f, ensure_ascii=False, indent=2)
    
    def add_document(self, text, metadata=None):
        doc_id = len(self.documents)
        document = {
            "id": doc_id,
            "text": text,
            "metadata": metadata or {}
        }
        self.documents.append(document)
        
        if len(self.documents) == 1:
            self.vectors = self.vectorizer.fit_transform([text])
        else:
            self.vectors = self.vectorizer.fit_transform([doc['text'] for doc in self.documents])
        
        self.save_data()
    
    def search(self, query, k=3):
        if not self.documents:
            return []
        
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.vectors).flatten()
        
        top_indices = np.argsort(similarities)[-k:][::-1]
        results = []
        
        for idx in top_indices:
            if similarities[idx] > 0:
                results.append({
                    "document": self.documents[idx],
                    "similarity": float(similarities[idx])
                })
        
        return results
