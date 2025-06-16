# API Endpoints

This document provides detailed information about the MCP service API endpoints.

## Base URL

All API endpoints are prefixed with `/api/v1` by default. This can be configured using the `API_PREFIX` environment variable.

## Authentication

Currently, the API does not require authentication. However, it's recommended to implement authentication in production environments.

## Endpoints

### Health Check

```http
GET /health
```

Check the health status of the service.

#### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-03-17T12:00:00Z"
}
```

### Machine Status

```http
GET /machines/{machine_id}/status
```

Get the current status of a specific machine.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `machine_id` | string | Unique identifier of the machine |

#### Response

```json
{
  "machine_id": "MACHINE_001",
  "status": "running",
  "last_updated": "2024-03-17T12:00:00Z",
  "metrics": {
    "temperature": 75.5,
    "pressure": 2.1,
    "speed": 1000
  }
}
```

### Update Machine Status

```http
POST /machines/{machine_id}/status
```

Update the status of a specific machine.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `machine_id` | string | Unique identifier of the machine |

#### Request Body

```json
{
  "status": "running",
  "metrics": {
    "temperature": 75.5,
    "pressure": 2.1,
    "speed": 1000
  }
}
```

#### Response

```json
{
  "machine_id": "MACHINE_001",
  "status": "running",
  "last_updated": "2024-03-17T12:00:00Z",
  "metrics": {
    "temperature": 75.5,
    "pressure": 2.1,
    "speed": 1000
  }
}
```

### List Machines

```http
GET /machines
```

Get a list of all machines.

#### Query Parameters

| Name | Type | Description |
|------|------|-------------|
| `status` | string | Filter by machine status |
| `limit` | integer | Maximum number of results |
| `offset` | integer | Number of results to skip |

#### Response

```json
{
  "machines": [
    {
      "machine_id": "MACHINE_001",
      "status": "running",
      "last_updated": "2024-03-17T12:00:00Z"
    },
    {
      "machine_id": "MACHINE_002",
      "status": "idle",
      "last_updated": "2024-03-17T11:55:00Z"
    }
  ],
  "total": 2,
  "limit": 10,
  "offset": 0
}
```

### Machine Metrics

```http
GET /machines/{machine_id}/metrics
```

Get historical metrics for a specific machine.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `machine_id` | string | Unique identifier of the machine |

#### Query Parameters

| Name | Type | Description |
|------|------|-------------|
| `start_time` | string | Start time (ISO 8601) |
| `end_time` | string | End time (ISO 8601) |
| `metric` | string | Specific metric to retrieve |

#### Response

```json
{
  "machine_id": "MACHINE_001",
  "metrics": [
    {
      "timestamp": "2024-03-17T12:00:00Z",
      "temperature": 75.5,
      "pressure": 2.1,
      "speed": 1000
    },
    {
      "timestamp": "2024-03-17T11:55:00Z",
      "temperature": 74.8,
      "pressure": 2.0,
      "speed": 950
    }
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "error": "Bad Request",
  "message": "Invalid request parameters",
  "details": {
    "field": "status",
    "error": "Invalid status value"
  }
}
```

### 404 Not Found

```json
{
  "error": "Not Found",
  "message": "Machine not found",
  "details": {
    "machine_id": "MACHINE_001"
  }
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred",
  "request_id": "req-123456"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. The current limits are:

- 100 requests per minute per IP address
- 1000 requests per hour per IP address

When rate limits are exceeded, the API returns a 429 Too Many Requests response:

```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded",
  "retry_after": 60
}
```

## Best Practices

1. **Error Handling**
   - Always check for error responses
   - Implement proper retry logic
   - Handle rate limiting appropriately

2. **Performance**
   - Use pagination for large result sets
   - Implement caching where appropriate
   - Monitor API usage

3. **Security**
   - Use HTTPS in production
   - Implement proper authentication
   - Validate all input data

4. **Monitoring**
   - Track API usage
   - Monitor response times
   - Set up alerts for errors 