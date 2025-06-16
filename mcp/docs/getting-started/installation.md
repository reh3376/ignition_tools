# Installation Guide

This guide covers different methods of installing and running the MCP service.

## Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized deployment)
- Neo4j database (version 4.4 or higher)

## Method 1: Using Docker (Recommended)

### Pull the Image

```bash
docker pull ghcr.io/reh3376/mcp:latest
```

### Run the Container

```bash
docker run -d \
  --name mcp \
  -p 8000:8000 \
  -e NEO4J_URI=bolt://localhost:7687 \
  -e NEO4J_USER=neo4j \
  -e NEO4J_PASSWORD=your_password \
  ghcr.io/reh3376/mcp:latest
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  mcp:
    image: ghcr.io/reh3376/mcp:latest
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=your_password
    depends_on:
      - neo4j

  neo4j:
    image: neo4j:4.4
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/your_password
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

volumes:
  neo4j_data:
  neo4j_logs:
```

Run with:
```bash
docker-compose up -d
```

## Method 2: Manual Installation

### 1. Clone the Repository

```bash
git clone https://github.com/reh3376/mcp.git
cd mcp
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
API_PORT=8000
```

### 5. Run the Service

```bash
uvicorn src.main:app --reload
```

## Verifying the Installation

1. Check the service health:
   ```bash
   curl http://localhost:8000/health
   ```

2. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Neo4j Connection Error**
   - Verify Neo4j is running
   - Check connection credentials
   - Ensure Neo4j bolt port is accessible

2. **Port Already in Use**
   - Check if another service is using port 8000
   - Change the port using the `API_PORT` environment variable

3. **Docker Pull Error**
   - Ensure you're logged in to GitHub Container Registry
   - Check your Docker token permissions

### Getting Help

If you encounter any issues not covered here, please:
1. Check the [GitHub Issues](https://github.com/reh3376/mcp/issues)
2. Create a new issue with detailed information about your problem
3. Include relevant logs and environment details 