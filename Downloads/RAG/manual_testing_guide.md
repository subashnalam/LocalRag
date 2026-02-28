# Manual API Testing Guide

This guide provides commands to interact with the server's primary endpoints. Choose the command that matches your terminal (PowerShell or Bash/CMD).

---

### 1. Health Check

This command checks if the server is running.

**For PowerShell:**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health
```

**For Bash/CMD (standard curl):**
```bash
curl -X GET http://localhost:8000/health
```

---

### 2. Search Endpoint

This is the correct way to query the search endpoint.

**For PowerShell:**
```powershell
$body = @{
  query = "first rule of fight club"
} | ConvertTo-Json

Invoke-WebRequest -Method POST -Uri http://localhost:8000/search -ContentType "application/json" -Body $body
```

**For Bash/CMD (standard curl):**
```bash
curl -X POST http://localhost:8000/search \
-H "Content-Type: application/json" \
-d '{
  "query": "first rule of fight club"
}'
```
**Expected Output:** A JSON object with a `results` array containing the full sentence chunk.

---

### 3. MCP Endpoint (For Comparison)

This endpoint expects a different structure.

**For PowerShell:**
```powershell
$body = @{
  tool_name = "some_tool"
  arguments = @{ key = "value" }
} | ConvertTo-Json

Invoke-WebRequest -Method POST -Uri http://localhost:8000/mcp -ContentType "application/json" -Body $body
```

**For Bash/CMD (standard curl):**
```bash
curl -X POST http://localhost:8000/mcp \
-H "Content-Type: application/json" \
-d '{
  "tool_name": "some_tool",
  "arguments": { "key": "value" }
}'
```

The automated functional test script succeeded because it correctly targeted the `/search` endpoint. Please use the appropriate command from **#2** for your manual verification.
