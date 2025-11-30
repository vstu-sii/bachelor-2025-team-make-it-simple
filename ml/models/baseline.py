import ollama
import json
import time
import re

class BaselineModel:
    def __init__(self, model_name="deepseek-r1:8b"):
        self.model_name = model_name
        self.client = ollama.Client()
        
    def generate_response(self, prompt, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        'temperature': 0.3,
                        'top_p': 0.9,
                        'num_predict': 2000
                    }
                )
                
                result = response['response']
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group()
                    return json.loads(json_str)
                else:
                    print(f"Attempt {attempt + 1}: No JSON found in response")
                    print(f"Raw response: {result}")
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                time.sleep(2)
        
        return {"error": "Failed to generate valid response after retries"}
    
    def generate_entry_test(self, course_data):
        from ml.prompt_templates import PromptTemplates
        
        prompt = PromptTemplates.entry_test_prompt(
            course_data['course_title'],
            course_data['topics'],
            str(course_data.get('materials', ''))
        )
        
        return self.generate_response(prompt)
    
    def generate_course_graph(self, graph_input):
        from ml.prompt_templates import PromptTemplates
        
        prompt = PromptTemplates.course_graph_prompt(
            graph_input['student_profile'],
            graph_input['course_title'], 
            graph_input['topics']
        )
        
        return self.generate_response(prompt)
    
    def generate_lesson_plan(self, lesson_input, lesson_type):
        from ml.prompt_templates import PromptTemplates
        
        prompt = PromptTemplates.lesson_plan_prompt(
            lesson_input['lesson_parameters'],
            lesson_type,
            lesson_input.get('theory', '')
        )
        
        return self.generate_response(prompt)
    
    def evaluate_lesson_results(self, evaluation_input):
        from ml.prompt_templates import PromptTemplates
        
        prompt = PromptTemplates.lesson_evaluation_prompt(
            evaluation_input,
            evaluation_input.get('test', {})
        )
        
        return self.generate_response(prompt)
