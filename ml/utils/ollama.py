import requests
import json
from utils import env

def pull_model(model: str):
    try:
        response = requests.post(
            url=env.OLLAMA_URL + "/api/pull",
            json={
                 "model": model,
                 "stream": True
            },
            stream=True
         )
    except Exception as e:
        print(f"Couldn't connect to Ollama instance: {e}")
        return 1

    print(f"\nPulling ollama model: {model}")

    if response.status_code != 200:
        print(f"Failed to pull ollama model: {response.status_code} {response.reason}")
        return 1
        
    status = ""

    for line in response.iter_lines():
        if line:
            try:
                json_data = json.loads(line.decode("utf-8"))
                if "error" in json_data.keys():
                    print(f"ERROR - {json_data["error"]}")
                    return 1                    
                
                if json_data["status"] != status:
                    status = json_data["status"]
                    print(status)
                    if "completed" in json_data:
                        print()

                if "completed" in json_data:
                    total = json_data.get('total', 0)
                    completed = json_data['completed']
                    progress_percentage = (completed / total) * 100 if total > 0 else 0
                    print(f"\033[F\033[KDownloading: {completed} / {total} ({progress_percentage:.2f}%)")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e} - Line: {line.decode('utf-8')}")