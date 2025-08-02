## This app aggregates user content about stocks and a llm gives a summary.

### 1. Run API

uvicorn main:app --reload

### 2. View on Web

http://127.0.0.1:8000

### 3. Close App
<pre>
```bash
lsof -i :8000  
kill -9 *<PID>*  
pkill -f "uvicorn"
```
</pre>

