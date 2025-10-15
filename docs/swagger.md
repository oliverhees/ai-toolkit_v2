# Swagger/OpenAPI Documentation

**Author:** NetzPrinz aka Oliver Hees
**Integration:** Flasgger for Flask

## Overview

The AI Toolkit includes interactive API documentation using Swagger/OpenAPI specification. This provides a user-friendly interface to explore, test, and understand all available API endpoints.

## Accessing Swagger UI

Once the server is running, access the interactive API documentation at:

```
http://localhost:8080/api/docs
```

Or for production:
```
https://your-api-domain.com/api/docs
```

## Features

### Interactive API Explorer
- **Try it out**: Test endpoints directly from the browser
- **Authentication**: Built-in API key authentication
- **Request/Response Examples**: See example payloads and responses
- **Schema Validation**: Automatic validation of request parameters
- **Response Codes**: Complete list of all possible HTTP response codes

### API Specification

The OpenAPI specification is available in JSON format at:
```
http://localhost:8080/apispec.json
```

This can be used to:
- Generate client SDKs
- Import into Postman/Insomnia
- Integrate with API gateways
- Auto-generate documentation

## Using Swagger UI

### 1. Authentication

All endpoints require an API key:

1. Click the **"Authorize"** button at the top of the page
2. Enter your API key in the `x-api-key` field
3. Click **"Authorize"**
4. Click **"Close"**

Your API key will be automatically included in all subsequent requests.

### 2. Testing Endpoints

To test an endpoint:

1. Find the endpoint you want to test (e.g., `/v1/chatterbox/text-to-speech`)
2. Click on the endpoint to expand it
3. Click **"Try it out"**
4. Fill in the required parameters
5. Click **"Execute"**
6. View the response below

### 3. Example: Text-to-Speech

Here's how to test the Text-to-Speech endpoint:

1. Navigate to **Chatterbox TTS** section
2. Expand **POST /v1/chatterbox/text-to-speech**
3. Click **"Try it out"**
4. Enter the following JSON:

```json
{
  "text": "Hello! This is a test of the Chatterbox TTS system.",
  "language": "en",
  "model_type": "english",
  "emotion_intensity": 1.0
}
```

5. Click **"Execute"**
6. Check the response for the generated audio URL

### 4. Asynchronous Requests

For long-running operations, use webhooks:

```json
{
  "text": "Your text here",
  "language": "en",
  "webhook_url": "https://your-app.com/webhook",
  "id": "custom-request-id"
}
```

The API will:
1. Return a 202 (Accepted) response immediately
2. Process the request in the background
3. Send results to your webhook URL when complete

## API Categories

### Chatterbox TTS
Advanced text-to-speech and voice cloning capabilities:
- **POST /v1/chatterbox/text-to-speech** - Generate speech from text
- **POST /v1/chatterbox/voice-cloning** - Clone a voice and generate speech

### Audio
Audio processing and manipulation:
- **POST /v1/audio/concatenate** - Combine multiple audio files
- Additional audio endpoints...

### Video
Video processing and manipulation:
- Video conversion and editing endpoints

### Image
Image processing and conversion:
- Image format conversion
- Image manipulation

### Media
General media processing:
- Transcription
- Metadata extraction
- Format conversion

### Storage
Cloud storage integration:
- S3 upload/download
- Google Cloud Storage integration

### Code
Code execution endpoints:
- Python code execution
- Sandboxed execution environment

## Response Format

All endpoints follow a consistent response format:

### Success Response (200)
```json
{
  "code": 200,
  "id": "your-custom-id",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "https://storage.example.com/output-file.wav",
  "message": "success",
  "run_time": 2.345,
  "queue_time": 0.123,
  "total_time": 2.468,
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

### Async Response (202)
```json
{
  "code": 202,
  "id": "your-custom-id",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "processing",
  "pid": 12345,
  "queue_id": 67890,
  "max_queue_length": "unlimited",
  "queue_length": 1,
  "build_number": "1.0.123"
}
```

### Error Response (400/401/429/500)
```json
{
  "code": 400,
  "id": "your-custom-id",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Error description here",
  "pid": 12345,
  "queue_id": 67890,
  "build_number": "1.0.123"
}
```

## HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Successful synchronous request |
| 202 | Accepted | Accepted for async processing (webhook) |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Invalid or missing API key |
| 429 | Too Many Requests | Queue limit reached |
| 500 | Internal Server Error | Server-side error occurred |

## Generating Client Code

Swagger UI can generate client code in multiple languages:

1. Click **"Servers"** dropdown
2. Select your server URL
3. Use the **"Download"** button to get the OpenAPI spec
4. Use tools like [swagger-codegen](https://swagger.io/tools/swagger-codegen/) or [openapi-generator](https://openapi-generator.tech/)

Example:
```bash
# Install openapi-generator
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8080/apispec.json \
  -g python \
  -o ./python-client

# Generate JavaScript client
openapi-generator-cli generate \
  -i http://localhost:8080/apispec.json \
  -g javascript \
  -o ./js-client
```

## Importing to API Tools

### Postman
1. Open Postman
2. Click **Import**
3. Enter URL: `http://localhost:8080/apispec.json`
4. Click **Import**

### Insomnia
1. Open Insomnia
2. Click **Create** > **Import From** > **URL**
3. Enter: `http://localhost:8080/apispec.json`
4. Click **Fetch and Import**

## Adding Documentation to New Endpoints

When creating new endpoints, add Swagger documentation as a docstring:

```python
@app.route("/v1/my-endpoint", methods=["POST"])
@authenticate
def my_endpoint():
    """
    My Endpoint Title
    ---
    tags:
      - My Category
    summary: Brief description
    description: |
      Longer description here

      **Features:**
      - Feature 1
      - Feature 2
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - param1
          properties:
            param1:
              type: string
              example: "example value"
              description: Parameter description
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            result:
              type: string
    security:
      - ApiKeyAuth: []
    """
    # Your endpoint logic here
    pass
```

## Configuration

Swagger is configured in `app.py`:

```python
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}
```

### Environment Variables

Configure Swagger behavior with environment variables:

```bash
# Set API host for Swagger
export API_HOST=api.example.com

# Or for local development
export API_HOST=localhost:8080
```

## Security Considerations

### Production Deployment

For production environments, consider:

1. **Disable Swagger UI** (if not needed publicly):
```python
swagger_config = {
    "swagger_ui": False,  # Disable UI
}
```

2. **Restrict Access**: Use reverse proxy rules to limit access
```nginx
location /api/docs {
    allow 10.0.0.0/8;  # Internal network only
    deny all;
}
```

3. **API Key Rotation**: Regularly rotate API keys
4. **Rate Limiting**: Implement rate limiting on all endpoints

## Troubleshooting

### Swagger UI Not Loading

1. Check server is running: `curl http://localhost:8080/api/docs`
2. Verify Flasgger is installed: `pip list | grep flasgger`
3. Check app.py imports: Ensure `from flasgger import Swagger` is present

### Documentation Not Showing

1. Ensure docstrings are properly formatted YAML
2. Check indentation (YAML is indent-sensitive)
3. Verify the endpoint is registered (check Flask routes)

### "Try it out" Not Working

1. Click **"Authorize"** and enter your API key
2. Check browser console for errors
3. Verify CORS settings if accessing from different domain

## Best Practices

1. **Always document new endpoints** with Swagger specs
2. **Include examples** for all parameters
3. **Document all response codes** including errors
4. **Keep descriptions clear** and concise
5. **Use tags** to organize endpoints by category
6. **Update docs** when changing endpoint behavior

## Related Resources

- [Flasgger Documentation](https://github.com/flasgger/flasgger)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI Documentation](https://swagger.io/tools/swagger-ui/)
- [Main API Documentation](../README.md)
- [Chatterbox TTS Documentation](./chatterbox/README.md)

## Support

For issues with Swagger integration:
1. Check the Flasgger documentation
2. Verify your YAML syntax
3. Review the app.py configuration
4. Check server logs for errors
