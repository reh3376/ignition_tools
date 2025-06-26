# IGN Scripts: Frontend/Backend Separation Migration Plan

## Overview
Migrate from monorepo to separate repositories with API-driven architecture.

## Phase 1: API Layer Creation (Week 1-2)

### 1.1 Create API Module Structure
```
src/api/
├── __init__.py
├── main.py              # FastAPI application
├── routers/
│   ├── sme_agent.py     # SME Agent endpoints
│   ├── refactoring.py   # Code intelligence endpoints
│   ├── data_integration.py
│   └── modules.py       # Module management
├── models/              # Pydantic models
│   ├── requests.py
│   └── responses.py
└── middleware/
    ├── auth.py
    └── cors.py
```

### 1.2 FastAPI Dependencies
```bash
pip install fastapi uvicorn pydantic[email] python-multipart
```

### 1.3 API Wrapper Implementation
Transform CLI commands to API endpoints:
```python
# api/routers/sme_agent.py
from fastapi import APIRouter
from src.ignition.modules.sme_agent import SMEAgentModule

router = APIRouter(prefix="/sme", tags=["SME Agent"])

@router.post("/validate-env")
async def validate_environment():
    module = SMEAgentModule()
    return module.validate_environment()

@router.post("/ask")
async def ask_question(question: str):
    module = SMEAgentModule()
    return module.ask_question(question)
```

## Phase 2: Frontend Repository Setup (Week 2-3)

### 2.1 Create New Repository
```bash
# Create new repository: ignition-frontend
git init ignition-frontend
cd ignition-frontend

# Copy frontend files
cp -r ../IGN_scripts/frontend/* .
```

### 2.2 Update Package Configuration
```json
{
  "name": "ignition-frontend",
  "scripts": {
    "dev": "vite --port 3000",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "react": "^18.2.0"
  }
}
```

### 2.3 Environment Configuration
```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api

# .env.production
VITE_API_BASE_URL=https://api.ignition-scripts.com/api
```

## Phase 3: API Client Integration (Week 3-4)

### 3.1 API Client Setup
```typescript
// src/lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
});

export default apiClient;
```

### 3.2 Type-Safe API Calls
```typescript
// src/lib/api/sme.ts
import apiClient from './client';

export interface SMEValidationResponse {
  status: 'valid' | 'invalid';
  components: ComponentStatus[];
  errors: string[];
}

export const smeApi = {
  validateEnvironment: (): Promise<SMEValidationResponse> =>
    apiClient.post('/sme/validate-env').then(res => res.data),

  askQuestion: (question: string) =>
    apiClient.post('/sme/ask', { question }).then(res => res.data),
};
```

## Phase 4: Development Workflow (Week 4-5)

### 4.1 Local Development Setup
```bash
# Terminal 1: Backend API
cd ignition-backend
uvicorn src.api.main:app --reload --port 8000

# Terminal 2: Frontend Dev Server
cd ignition-frontend
npm run dev
```

### 4.2 Docker Compose for Development
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  backend:
    build: ./ignition-backend
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
    volumes:
      - ./ignition-backend:/app

  frontend:
    build: ./ignition-frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://backend:8000/api
    volumes:
      - ./ignition-frontend:/app

  neo4j:
    image: neo4j:5
    environment:
      - NEO4J_AUTH=neo4j/password
    ports:
      - "7474:7474"
      - "7687:7687"
```

## Phase 5: CI/CD Pipeline Setup (Week 5-6)

### 5.1 Backend Pipeline
```yaml
# .github/workflows/backend.yml
name: Backend CI/CD
on:
  push:
    paths: ['src/**', 'tests/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/
      - name: Run linting
        run: ruff check .
```

### 5.2 Frontend Pipeline
```yaml
# .github/workflows/frontend.yml
name: Frontend CI/CD
on:
  push:
    paths: ['src/**', 'public/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test
      - name: Build
        run: npm run build
```

## Phase 6: Deployment Strategy (Week 6-7)

### 6.1 Backend Deployment
```dockerfile
# ignition-backend/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ src/
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0"]
```

### 6.2 Frontend Deployment
```dockerfile
# ignition-frontend/Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

## Risk Mitigation

### 1. Gradual Migration
- Keep monorepo during transition
- Run both old CLI and new API in parallel
- Frontend calls API, which wraps CLI initially

### 2. API Contract Testing
```python
# tests/api/test_contracts.py
def test_sme_validation_response_schema():
    response = client.post("/sme/validate-env")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
```

### 3. Rollback Strategy
- Keep git submodules linking to specific versions
- Feature flags for API vs CLI usage
- Deployment rollback procedures

## Success Metrics

### Technical Metrics
- API response time < 200ms for 95% of requests
- Frontend build time < 2 minutes
- Backend test coverage > 80%
- Zero breaking API changes without versioning

### Development Metrics
- Independent deployment capability
- Reduced merge conflicts
- Faster development cycles
- Clear team ownership boundaries

## Timeline Summary

| Week | Backend | Frontend | Integration |
|------|---------|----------|-------------|
| 1-2  | API layer creation | - | - |
| 2-3  | API endpoints | New repo setup | - |
| 3-4  | Testing & docs | API integration | Local dev workflow |
| 4-5  | Performance tuning | UI completion | Docker setup |
| 5-6  | CI/CD setup | CI/CD setup | E2E testing |
| 6-7  | Production deploy | Production deploy | Monitoring |

## Post-Migration Benefits

1. **Independent Scaling**: Deploy frontend and backend separately
2. **Team Autonomy**: Frontend and backend teams work independently
3. **Technology Evolution**: Upgrade React/Python versions independently
4. **Security**: Clear API boundaries and authentication
5. **Performance**: Optimized deployment strategies for each component
