import requests
import json
from pathlib import Path

def execute_json_query(file_path: str):
    """
    Reads a JSON file and sends its content as a POST request to the MCP server.

    Args:
        file_path (str): The path to the JSON file to execute.
    """
    url = "http://localhost:8000/mcp"
    
    try:
        # Read the JSON payload from the specified file
        query_path = Path(file_path)
        if not query_path.is_file():
            print(f"Error: File not found at {file_path}")
            return
            
        with open(query_path, 'r') as f:
            payload = json.load(f)
            
        print(f"Executing query from: {file_path}")
        print("Request Payload:")
        print(json.dumps(payload, indent=2))
        
        # Send the request
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        print("\nResponse received:")
        print(json.dumps(response.json(), indent=2))
        
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"\nAn error occurred while sending the request: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    # This script now directly executes the query from a JSON file.
    # The default file is mcp_query.json in the parent directory.
    
    # Instructions:
    # 1. Make sure the main application is running in one terminal.
    #    (local-rag\\venv\\Scripts\\python local-rag\\main.py)
    #
    # 2. In a *new* terminal, run this script:
    #    (local-rag\\venv\\Scripts\\python local-rag\\test_client.py)

    execute_json_query("mcp_query.json")
