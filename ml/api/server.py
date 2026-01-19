from flask import Flask, request, jsonify
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import env, ollama
from models.baseline import BaselineModel
from api.vector_db.vector_store import VectorStore

app = Flask(__name__)
model = BaselineModel(env.GENERATING_MODEL)
vector_stores = {}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "model": model.model_name})

@app.route('/generate/entry-test', methods=['POST'])
def generate_entry_test():
    try:
        data = request.json
        result = model.generate_entry_test(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate/course-graph', methods=['POST'])
def generate_course_graph():
    try:
        data = request.json
        result = model.generate_course_graph(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate/lesson-plan', methods=['POST'])
def generate_lesson_plan():
    try:
        data = request.json
        lesson_type = data.get('type', 'theory')
        result = model.generate_lesson_plan(data, lesson_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/evaluate/lesson-results', methods=['POST'])
def evaluate_lesson_results():
    try:
        data = request.json
        result = model.evaluate_lesson_results(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vector-db/upload', methods=['POST'])
def upload_to_vector_db():
    try:
        course_id = request.json.get('course_id')
        text = request.json.get('text')
        
        if course_id not in vector_stores:
            vector_stores[course_id] = VectorStore(course_id)
        
        vector_stores[course_id].add_document(text)
        return jsonify({"status": "success", "course_id": course_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vector-db/search', methods=['POST'])
def search_vector_db():
    try:
        course_id = request.json.get('course_id')
        query = request.json.get('query')
        k = request.json.get('k', 3)
        
        if course_id not in vector_stores:
            return jsonify({"error": "Vector store not found"}), 404
        
        results = vector_stores[course_id].search(query, k)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if ollama.pull_model(env.GENERATING_MODEL):
        quit(1)

    app.run(host='0.0.0.0', port=env.PORT, debug=True)
