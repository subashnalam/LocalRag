# Issue Log

## Issue: VectorStore Document Update Failure

- **Date:** 2025-06-23
- **Status:** Resolved

### 1. Problem Description

The `VectorStore` component was failing to correctly update documents. When a document was modified and re-processed, the old version was not being deleted from the database, leading to data duplication and incorrect search results. This was identified by the failing `test_update_document_by_re_adding` integration test.

### 2. Root Cause Analysis

The root cause was a subtle but critical inconsistency in how file paths were being handled.

-   **Document Addition:** When a document was added, its metadata stored the `source` file path in whatever format it was received (e.g., a relative path like `test/doc1.txt`).
-   **Document Deletion:** The `remove_document` method, however, was attempting to find the document to delete by using a normalized, absolute path (e.g., `C:\Users\User\Downloads\RAG\test\doc1.txt`).

Because the relative path used for adding and the absolute path used for deleting did not match, the `delete` operation could never find the target document, and the old data was never removed.

### 3. Solution

The solution was to enforce a consistent path normalization strategy across all database operations.

-   **Implementation:** The `pathlib.Path.resolve()` method was used to convert all incoming file paths into a standardized, absolute format.
-   **Affected Methods:**
    -   `VectorStore.add_document_chunks()`: Now normalizes the path before storing it in the document's metadata.
    -   `VectorStore.remove_document()`: Now normalizes the path before using it in the `where` clause of the delete query.

This ensures that the same path format is used for both adding and deleting documents, guaranteeing that the correct document is always targeted for removal. The fix was validated by updating the integration tests to also use normalized paths, and all tests now pass.
