# Local RAG System - Testing Instructions

This document provides instructions for testing the Local RAG system to ensure it is fully functional.

## 1. Start the Application

Run the following command in your terminal to start the application:

```bash
local-rag\venv\Scripts\python local-rag\main.py
```

## 2. Verify Document Ingestion

On startup, the application should automatically scan the `local-rag/data/documents` directory and process any existing files.

**Expected Outcome:**

You should see log messages in your terminal indicating that the application has found and processed the `chat_manager_prd.md` file. Look for messages similar to this:

```
INFO: Scanning for existing documents in local-rag\data\documents...
INFO: Found existing document: local-rag\data\documents\chat_manager_prd.md
```

**If the Application Crashes:**

If the file watcher process stops unexpectedly, a critical error has likely occurred. Check the log file for a detailed traceback.

1.  **Open the log file**: `local-rag/logs/rag_system.log`
2.  **Look for a "CRITICAL" error message** at the end of the file. It will look something like this:

    ```
    CRITICAL: File watcher process crashed: [Error details]
    Traceback (most recent call last):
      ... (full error stack trace) ...
    ```
3.  **Provide this traceback** to help diagnose the root cause of the failure.

## 3. How to Execute `mcp_query.json`

A dedicated script has been created to execute the query defined in your `mcp_query.json` file.

**Instructions:**

1.  **Ensure the main application is running** in a terminal:
    ```bash
    local-rag\venv\Scripts\python local-rag\main.py
    ```
2.  **Open a NEW terminal**.
3.  **Install the `requests` dependency** if you haven't already:
    ```bash
    local-rag\venv\Scripts\pip install -r local-rag\requirements.txt
    ```
4.  **Run the test client script**:
    ```bash
    local-rag\venv\Scripts\python local-rag\test_client.py
    ```

**What this script does:**

The `test_client.py` script will automatically:
1.  Read the content of the `mcp_query.json` file located in the root directory.
2.  Send that content as a `POST` request to the running MCP server at `http://localhost:8000/mcp`.
3.  Print the server's response to your terminal.

This provides a direct way to execute the JSON file and see the result.
