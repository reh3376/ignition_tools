# Uvicorn FastAPI Server Guide
## Phase 11.3: SME Agent Integration & Interfaces

This guide provides comprehensive instructions for using uvicorn to run, test, and document the SME Agent FastAPI server.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Server Startup Options](#server-startup-options)
3. [API Documentation](#api-documentation)
4. [Testing the API](#testing-the-api)
5. [Development Workflow](#development-workflow)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Start the Development Server

```bash
# Using the startup script (recommended)
python scripts/start_api_server.py --dev

# Or directly with uvicorn
uvicorn src.ignition.modules.sme_agent.web_interface:app --reload --host 127.0.0.1 --port 8000
```

### 2. Access API Documentation

Once the server is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 3. Test Basic Connectivity

```bash
# Health check
curl http://localhost:8000/health

# Basic chat request
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"question": "What is Ignition?", "complexity": "standard"}'
```

## Server Startup Options

### Using the Startup Script

The `scripts/start_api_server.py` provides a convenient wrapper with comprehensive options:

```bash
# Development mode (auto-reload, debug logging)
python scripts/start_api_server.py --dev

# Production mode
python scripts/start_api_server.py --host 0.0.0.0 --port 8000 --workers 4

# Custom configuration
python scripts/start_api_server.py \
    --host localhost \
    --port 8080 \
    --log-level debug \
    --workers 2

# With SSL (production)
python scripts/start_api_server.py \
    --host 0.0.0.0 \
    --port 443 \
    --ssl-keyfile /path/to/key.pem \
    --ssl-certfile /path/to/cert.pem
```

### Direct Uvicorn Commands

```bash
# Basic development server
uvicorn src.ignition.modules.sme_agent.web_interface:app --reload

# Production server with multiple workers
uvicorn src.ignition.modules.sme_agent.web_interface:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4

# With specific logging
uvicorn src.ignition.modules.sme_agent.web_interface:app \
    --log-level debug \
    --access-log

# SSL configuration
uvicorn src.ignition.modules.sme_agent.web_interface:app \
    --host 0.0.0.0 \
    --port 443 \
    --ssl-keyfile=/path/to/key.pem \
    --ssl-certfile=/path/to/cert.pem
```

## API Documentation

### Swagger UI Features

The Swagger UI at `/docs` provides:

- **Interactive Testing**: Test endpoints directly from the browser
- **Request/Response Examples**: See example payloads and responses
- **Schema Validation**: Real-time validation of request data
- **Authentication Testing**: Test with different session IDs

### Key Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/health` | GET | Health check | `curl http://localhost:8000/health` |
| `/status` | GET | System status | `curl http://localhost:8000/status` |
| `/chat` | POST | Standard chat | See examples below |
| `/chat/stream` | POST | Streaming chat | Server-Sent Events |
| `/analyze` | POST | File analysis | Upload code for analysis |
| `/sessions/{id}` | GET | Session history | Get conversation history |

### Example API Calls

#### Health Check
```bash
curl -X GET http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-17T12:00:00Z",
  "agent_status": {
    "initialized": true,
    "ready": true
  }
}
```

#### Chat Request
```bash
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{
       "question": "Explain Ignition SCADA system",
       "complexity": "standard",
       "context": "Industrial automation training"
     }'
```

Response:
```json
{
  "response": "Ignition is a comprehensive SCADA platform...",
  "confidence": 0.95,
  "session_id": "session_12345",
  "processing_time": 1.23,
  "model_used": "sme_agent_v1"
}
```

#### Streaming Chat
```bash
curl -X POST http://localhost:8000/chat/stream \
     -H "Content-Type: application/json" \
     -H "Accept: text/event-stream" \
     -d '{
       "question": "Detailed Ignition architecture",
       "complexity": "advanced",
       "stream": true
     }'
```

Response (Server-Sent Events):
```
data: {"type": "chunk", "content": "Ignition's architecture consists of..."}
data: {"type": "chunk", "content": " multiple interconnected modules..."}
data: {"type": "complete", "confidence": 0.92, "session_id": "session_12345"}
```

#### File Analysis
```bash
curl -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '{
       "content": "def hello():\n    print(\"Hello World\")",
       "filename": "example.py",
       "complexity": "standard"
     }'
```

## Testing the API

### Automated Testing Script

Use the provided testing script for comprehensive endpoint validation:

```bash
# Test local server
python scripts/test_api_endpoints.py

# Test custom server
python scripts/test_api_endpoints.py --url http://localhost:8080

# Save test results
python scripts/test_api_endpoints.py --output test_results.json
```

### Manual Testing with curl

#### Test Input Validation
```bash
# Empty question (should return 422)
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"question": "", "complexity": "standard"}'

# Invalid complexity (should return 422)
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"question": "Test", "complexity": "invalid"}'
```

#### Test Session Management
```bash
# Get session history (replace with actual session ID)
curl -X GET http://localhost:8000/sessions/session_12345
```

### Testing with Python requests

```python
import requests

# Basic chat test
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "question": "What is Ignition?",
        "complexity": "standard"
    }
)
print(response.json())

# Streaming test
response = requests.post(
    "http://localhost:8000/chat/stream",
    json={
        "question": "Explain Ignition architecture",
        "complexity": "advanced",
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

## Development Workflow

### 1. Start Development Server

```bash
# Terminal 1: Start server with auto-reload
python scripts/start_api_server.py --dev
```

### 2. Make Code Changes

Edit files in `src/ignition/modules/sme_agent/web_interface.py` and the server will automatically reload.

### 3. Test Changes

```bash
# Terminal 2: Run tests
python scripts/test_api_endpoints.py

# Or test specific endpoints
curl http://localhost:8000/health
```

### 4. View Documentation

Open http://localhost:8000/docs in your browser to see updated API documentation.

### 5. Debug Issues

```bash
# Check server logs (in Terminal 1)
# Look for error messages and stack traces

# Test with verbose curl
curl -v http://localhost:8000/health
```

## Production Deployment

### Basic Production Setup

```bash
# Install production dependencies
pip install uvicorn[standard] gunicorn

# Start with multiple workers
uvicorn src.ignition.modules.sme_agent.web_interface:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --access-log \
    --log-level info
```

### Using Gunicorn (Alternative)

```bash
# Install gunicorn
pip install gunicorn

# Start with gunicorn
gunicorn src.ignition.modules.sme_agent.web_interface:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/

EXPOSE 8000

CMD ["uvicorn", "src.ignition.modules.sme_agent.web_interface:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Environment Variables

```bash
# Production environment variables
export ENVIRONMENT=production
export LOG_LEVEL=info
export WORKERS=4
export HOST=0.0.0.0
export PORT=8000

# Optional: SSL configuration
export SSL_KEYFILE=/path/to/key.pem
export SSL_CERTFILE=/path/to/cert.pem
```

## Troubleshooting

### Common Issues

#### 1. Server Won't Start

```bash
# Check if port is in use
lsof -i :8000

# Try different port
python scripts/start_api_server.py --port 8001
```

#### 2. Import Errors

```bash
# Ensure you're in the correct directory
cd /path/to/IGN_scripts

# Check Python path
python -c "import sys; print(sys.path)"

# Install dependencies
pip install -r requirements.txt
```

#### 3. SME Agent Not Initialized

Check the logs for initialization errors:
```bash
# Look for error messages in server output
python scripts/start_api_server.py --dev --log-level debug
```

#### 4. Connection Refused

```bash
# Check if server is running
curl http://localhost:8000/health

# Check firewall settings (if accessing remotely)
# Ensure host is set to 0.0.0.0 for external access
python scripts/start_api_server.py --host 0.0.0.0
```

### Performance Issues

#### 1. Slow Responses

```bash
# Increase workers for production
uvicorn src.ignition.modules.sme_agent.web_interface:app --workers 8

# Monitor resource usage
top -p $(pgrep -f uvicorn)
```

#### 2. Memory Usage

```bash
# Monitor memory usage
ps aux | grep uvicorn

# Consider using gunicorn with worker recycling
gunicorn src.ignition.modules.sme_agent.web_interface:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --max-requests 1000 \
    --max-requests-jitter 100
```

### Logging and Monitoring

#### Enable Detailed Logging

```bash
# Development logging
python scripts/start_api_server.py --dev --log-level debug

# Production logging
uvicorn src.ignition.modules.sme_agent.web_interface:app \
    --log-level info \
    --access-log \
    --log-config logging.conf
```

#### Monitor Server Health

```bash
# Continuous health monitoring
watch -n 5 'curl -s http://localhost:8000/health | jq'

# Check server status
curl -s http://localhost:8000/status | jq
```

## Advanced Configuration

### Custom Uvicorn Configuration

Create `uvicorn_config.py`:

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.ignition.modules.sme_agent.web_interface:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=4,
        access_log=True,
        log_level="info",
        loop="uvloop",  # Performance optimization
        http="httptools",  # Performance optimization
    )
```

### Load Balancing

For high-traffic deployments, consider using a reverse proxy:

#### Nginx Configuration

```nginx
upstream fastapi_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Integration Examples

### JavaScript/Frontend Integration

```javascript
// Basic chat request
async function chatWithSME(question) {
    const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            complexity: 'standard'
        })
    });

    return await response.json();
}

// Streaming chat
async function streamChat(question) {
    const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
            question: question,
            complexity: 'advanced',
            stream: true
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                console.log(data);
            }
        }
    }
}
```

### Python Client Integration

```python
import requests
import json

class SMEAgentClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def chat(self, question, complexity="standard", context=None):
        """Send a chat request to the SME Agent."""
        payload = {
            "question": question,
            "complexity": complexity
        }
        if context:
            payload["context"] = context

        response = self.session.post(
            f"{self.base_url}/chat",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def analyze_file(self, content, filename, complexity="standard"):
        """Analyze code content."""
        payload = {
            "content": content,
            "filename": filename,
            "complexity": complexity
        }

        response = self.session.post(
            f"{self.base_url}/analyze",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def health_check(self):
        """Check server health."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

# Usage example
client = SMEAgentClient()
result = client.chat("What is Ignition SCADA?")
print(result["response"])
```

This comprehensive guide provides everything needed to effectively use uvicorn with the SME Agent FastAPI server for development, testing, and production deployment.
