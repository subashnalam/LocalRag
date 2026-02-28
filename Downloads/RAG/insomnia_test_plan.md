# Comprehensive Manual Test Plan for Insomnia

**Prerequisites:**
1.  The Local RAG V2 system is running (`python main.py`).
2.  You have at least one document in the `data/documents` folder.
3.  You have Insomnia installed.

---

### Test Suite 1: Health & Status Monitoring

#### **Test 1.1: Check System Health**

*   **Objective:** Verify that the system is running and healthy.
*   **Insomnia Setup:**
    1.  Create a new **GET** request.
    2.  Set the URL to `http://localhost:8000/health`.
    3.  Click **Send**.
*   **Verification:**
    *   The status code should be `200 OK`.
    *   The response body should be a JSON object.
    *   The `status` field should be `"healthy"`.
    *   The `total_documents` field should be a number greater than 0 (if you have documents).

---

### Test Suite 2: Search Functionality

#### **Test 2.1: Basic Search**

*   **Objective:** Perform a basic search and get relevant results.
*   **Insomnia Setup:**
    1.  Create a new **POST** request.
    2.  Set the URL to `http://localhost:8000/search`.
    3.  Go to the **Body** tab and select **JSON**.
    4.  Enter the following JSON payload (replace `"your search term"` with a term you know is in your documents):
        ```json
        {
          "query": "your search term"
        }
        ```
    5.  Click **Send**.
*   **Verification:**
    *   The status code should be `200 OK`.
    *   The response body should contain a `results` array with JSON objects.
    *   Each object in the `results` array should have `content`, `metadata`, and `score` fields.

#### **Test 2.2: Search with Result Limit**

*   **Objective:** Control the number of search results returned.
*   **Insomnia Setup:**
    1.  Duplicate the "Basic Search" request.
    2.  Modify the JSON payload to include a `limit`:
        ```json
        {
          "query": "your search term",
          "limit": 3
        }
        ```
    3.  Click **Send**.
*   **Verification:**
    *   The status code should be `200 OK`.
    *   The `results` array in the response should contain **at most** 3 items.

---

### Test Suite 3: Document Management

#### **Test 3.1: List All Processed Documents**

*   **Objective:** Get a summary of all documents in the system.
*   **Insomnia Setup:**
    1.  Create a new **GET** request.
    2.  Set the URL to `http://localhost:8000/documents`.
    3.  Click **Send**.
*   **Verification:**
    *   The status code should be `200 OK`.
    *   The response body should contain `total_documents` and `collection_info`.

#### **Test 3.2: Delete a Document via API**

*   **Objective:** Remove a specific document from the system using its file path.
*   **Setup:**
    1.  First, you need a file path. You can get this from the `source` field in a search result, or by looking in your `data/documents` folder. Let's assume the path is `data/documents/my_test_doc.txt`.
*   **Insomnia Setup:**
    1.  Create a new **DELETE** request.
    2.  Set the URL to `http://localhost:8000/documents/data/documents/my_test_doc.txt`.
    3.  Click **Send**.
*   **Verification:**
    *   The status code should be `200 OK`.
    *   The response body should contain a success message.
    *   **Crucially, if you search for content from that document again, you should get no results.**

---

### Test Suite 4: State and Processing

#### **Test 4.1: Force Reprocessing**

*   **Objective:** Trigger a full reprocessing of all documents.
*   **Insomnia Setup:**
    1.  Create a new **POST** request.
    2.  Set the URL to `http://localhost:8000/process`.
    3.  Click **Send**.
*   **Verification:**
    *   The status code should be `200 OK`.
    *   The response body should contain a message like `"Reprocessing initiated - restart system to take effect"`.
    *   **To complete verification, you must restart your `main.py` script and watch the console logs to confirm that all files are being processed again.**

---

### Test Suite 5: Manual File System Tests (No Insomnia Needed)

These tests require you to interact with your file system and observe the running application's console output.

#### **Test 5.1: Add a New Document**

1.  **Action:** Copy a new file into your `data/documents` folder.
2.  **Observe:** Watch the console where `main.py` is running. You should see log messages indicating that a new file has been detected and is being processed.
3.  **Verify in Insomnia:** Rerun the "Check System Health" request. The `total_documents` count should have increased.

#### **Test 5.2: Update an Existing Document**

1.  **Action:** Open an existing file in `data/documents` and make a noticeable change. Save the file.
2.  **Observe:** Watch the console. You should see logs indicating the file was detected and is being re-processed.
3.  **Verify in Insomnia:** Rerun a "Basic Search" for the *new* content you added. It should appear in the results.

#### **Test 5.3: Delete a Document**

1.  **Action:** Delete a file from the `data/documents` folder.
2.  **Action:** Stop and restart the `main.py` script.
3.  **Observe:** Watch the console on startup. You should see a log message indicating that a deleted file was detected and removed from the database.
4.  **Verify in Insomnia:** Rerun the "Check System Health" request. The `total_documents` count should have decreased.
