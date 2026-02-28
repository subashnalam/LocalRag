import os
import shutil
import subprocess
import time
import requests
from pathlib import Path

# --- Configuration ---
BASE_URL = "http://localhost:8000"
DOCUMENTS_DIR = Path("local-rag/data/documents")
PROCESSED_DIR = Path("local-rag/data/processed")
VECTOR_STORE_DIR = Path("local-rag/data/vector_store")
MAIN_SCRIPT_PATH = "local-rag/main.py"

# --- Test Utilities ---
class TestRunner:
    def __init__(self):
        self.server_process = None
        self.results = {}

    def _print_step(self, message):
        print(f"\n{'='*50}")
        print(f"STEP: {message}")
        print(f"{'='*50}")

    def _print_result(self, test_name, success, details=""):
        status = "✅ PASSED" if success else "❌ FAILED"
        self.results[test_name] = success
        print(f"  -> RESULT: {status} {details}")

    def setup_environment(self):
        self._print_step("Setting up clean test environment")
        for dir_path in [PROCESSED_DIR, VECTOR_STORE_DIR, DOCUMENTS_DIR]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create seed documents
        (DOCUMENTS_DIR / "doc1.txt").write_text("The first rule of Fight Club is you do not talk about Fight Club.")
        (DOCUMENTS_DIR / "doc2.txt").write_text("The second rule of Fight Club is you do not talk about Fight Club.")
        print("  -> Environment cleaned and seeded with 2 documents.")

    def start_server(self):
        self._print_step("Starting the RAG server")
        self.server_process = subprocess.Popen(["python", MAIN_SCRIPT_PATH])
        
        # Wait for the server to be ready
        max_wait = 30
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{BASE_URL}/health")
                if response.status_code == 200:
                    print("  -> Server is up and running.")
                    return
            except requests.ConnectionError:
                time.sleep(1)
        
        raise RuntimeError("Server failed to start within the timeout period.")

    def run_tests(self):
        try:
            self.test_initial_health_check()
            self.test_search_endpoint()
            self.test_live_file_creation()
            self.test_live_file_deletion()
        except Exception as e:
            print(f"\nAn error occurred during testing: {e}")
        finally:
            self.shutdown_server()
            self.print_final_report()

    def test_initial_health_check(self):
        test_name = "Initial Health Check & Data Validation"
        self._print_step(test_name)
        try:
            response = requests.get(f"{BASE_URL}/health")
            response.raise_for_status()
            data = response.json()
            assert data["status"] == "healthy"
            assert data["total_documents"] == 2
            self._print_result(test_name, True)
        except Exception as e:
            self._print_result(test_name, False, f"Error: {e}")

    def test_search_endpoint(self):
        test_name = "Search Endpoint"
        self._print_step(test_name)
        try:
            payload = {"query": "first rule of fight club"}
            response = requests.post(f"{BASE_URL}/search", json=payload)
            response.raise_for_status()
            data = response.json()
            assert len(data["results"]) > 0
            assert "first rule" in data["results"][0]["content"].lower()
            self._print_result(test_name, True)
        except Exception as e:
            self._print_result(test_name, False, f"Error: {e}")

    def test_live_file_creation(self):
        test_name = "Live File Creation (File Watcher)"
        self._print_step(test_name)
        try:
            (DOCUMENTS_DIR / "live_doc.txt").write_text("A new document appears.")
            print("  -> New file created. Waiting for watcher...")
            time.sleep(10) # Give the watcher time to process
            
            response = requests.get(f"{BASE_URL}/health")
            response.raise_for_status()
            data = response.json()
            assert data["total_documents"] == 3
            self._print_result(test_name, True, "Document count increased to 3.")
        except Exception as e:
            self._print_result(test_name, False, f"Error: {e}")

    def test_live_file_deletion(self):
        test_name = "Live File Deletion (File Watcher)"
        self._print_step(test_name)
        try:
            os.remove(DOCUMENTS_DIR / "live_doc.txt")
            print("  -> Live file deleted. Waiting for watcher...")
            time.sleep(10) # Give the watcher time to process
            
            response = requests.get(f"{BASE_URL}/health")
            response.raise_for_status()
            data = response.json()
            assert data["total_documents"] == 2
            self._print_result(test_name, True, "Document count returned to 2.")
        except Exception as e:
            self._print_result(test_name, False, f"Error: {e}")

    def shutdown_server(self):
        self._print_step("Shutting down the server")
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("  -> Server process terminated.")

    def print_final_report(self):
        self._print_step("Final Test Report")
        total_tests = len(self.results)
        passed_tests = sum(self.results.values())
        failed_tests = total_tests - passed_tests

        print(f"  -> Summary: {passed_tests}/{total_tests} tests passed.")
        for name, success in self.results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"    - {name}: {status}")
        
        if failed_tests > 0:
            print("\nFunctional testing failed.")
        else:
            print("\nAll functional tests passed successfully!")

if __name__ == "__main__":
    runner = TestRunner()
    runner.setup_environment()
    runner.start_server()
    runner.run_tests()
