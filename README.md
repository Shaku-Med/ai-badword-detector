# Bad Word Detector API

A FastAPI-based REST API for detecting and filtering inappropriate content in text. This API provides comprehensive profanity detection capabilities with support for custom word lists, batch processing, and configurable strictness levels.

## Features

- **Single Text Detection**: Detect profanity in individual text inputs
- **Batch Processing**: Process multiple texts simultaneously
- **Custom Word Management**: Add or remove custom bad words dynamically
- **Strict Mode**: Enhanced detection sensitivity for stricter filtering
- **Censoring**: Automatically censor detected profanity
- **Confidence Scoring**: Get confidence scores for detection accuracy
- **Health Monitoring**: Built-in health check endpoints
- **CORS Support**: Cross-origin resource sharing enabled
- **Persistent Storage**: Custom words are saved to disk

## Quick Start

### Option 1: Automatic Setup (Recommended)
```bash
cd Python/BadWordDetector
python3 setup.py
```

### Option 2: Manual Setup
```bash
cd Python/BadWordDetector

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Start the Server
```bash
# Option 1: Simple run script
python run.py

# Option 2: Direct execution
python main.py

# Option 3: With startup script
python start_server.py
```

The API will be available at `http://localhost:8000`

## Troubleshooting

### "externally managed environment" Error
This error occurs on newer Python installations. Solutions:

1. **Use the setup script:**
   ```bash
   python3 setup.py
   ```

2. **Create virtual environment manually:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

3. **Install python3-venv (Linux):**
   ```bash
   sudo apt install python3-venv
   ```

### Missing Dependencies
If you get import errors:
```bash
pip install fastapi uvicorn requests
```

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## API Endpoints

### 1. Root Endpoint
- **GET** `/` - Get API information and available endpoints

### 2. Single Text Detection
- **POST** `/detect` - Detect profanity in a single text

**Request Body:**
```json
{
  "text": "Your text here",
  "language": "en",
  "strict_mode": false
}
```

**Response:**
```json
{
  "original_text": "Your text here",
  "has_profanity": true,
  "profanity_count": 1,
  "profanity_words": ["badword"],
  "censored_text": "Your text here",
  "confidence_score": 0.25
}
```

### 3. Batch Text Detection
- **POST** `/detect-batch` - Detect profanity in multiple texts

**Request Body:**
```json
{
  "texts": ["Text 1", "Text 2", "Text 3"],
  "language": "en",
  "strict_mode": false
}
```

### 4. Custom Words Management
- **POST** `/custom-words` - Add or remove custom bad words
- **GET** `/custom-words` - Get current custom words

**Add custom words:**
```json
{
  "words": ["customword1", "customword2"],
  "action": "add"
}
```

**Remove custom words:**
```json
{
  "words": ["customword1"],
  "action": "remove"
}
```

### 5. Health Check
- **GET** `/health` - Check API health status

## Testing

Run the test script to verify all endpoints:
```bash
python test_api.py
```

Make sure the server is running before executing the tests.

## Example Usage

### Python Client Example

```python
import requests

# Single text detection
response = requests.post("http://localhost:8000/detect", json={
    "text": "Hello, this is a test message",
    "strict_mode": False
})
result = response.json()
print(f"Has profanity: {result['has_profanity']}")

# Batch detection
response = requests.post("http://localhost:8000/detect-batch", json={
    "texts": ["Clean text", "Text with bad words"],
    "strict_mode": True
})
results = response.json()["results"]

# Add custom words
response = requests.post("http://localhost:8000/custom-words", json={
    "words": ["mycustomword"],
    "action": "add"
})
```

### cURL Examples

```bash
# Single detection
curl -X POST "http://localhost:8000/detect" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello world", "strict_mode": false}'

# Batch detection
curl -X POST "http://localhost:8000/detect-batch" \
     -H "Content-Type: application/json" \
     -d '{"texts": ["Text 1", "Text 2"], "strict_mode": false}'

# Add custom words
curl -X POST "http://localhost:8000/custom-words" \
     -H "Content-Type: application/json" \
     -d '{"words": ["customword"], "action": "add"}'
```

## Configuration

### Environment Variables

You can configure the following environment variables:
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### Custom Words Storage

Custom bad words are automatically saved to `custom_bad_words.json` in the project directory and loaded on server startup.

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Requests**: HTTP library for testing (optional)

## Error Handling

The API includes comprehensive error handling:
- **400 Bad Request**: Invalid request parameters
- **500 Internal Server Error**: Server-side processing errors
- **Connection Errors**: Proper error messages for client connection issues

## Security Features

- Input validation using Pydantic models
- CORS middleware for cross-origin requests
- Error message sanitization
- Request size limits

## Performance

- Async/await support for concurrent requests
- Efficient batch processing
- Memory-efficient custom word storage
- Fast text processing using regex

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License. 