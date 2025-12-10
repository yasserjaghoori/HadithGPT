# HadithGPT API Documentation

Production-ready FastAPI backend for semantic hadith search with AI-powered query enhancement.

## Features

- **Semantic Search**: Uses OpenAI embeddings for intelligent hadith retrieval
- **Query Classification**: Automatically detects greetings vs actual hadith queries
- **Query Enhancement**: GPT-powered query expansion for better results
- **Multi-Collection Search**: Search across Bukhari, Muslim, An-Nasai, Abu Dawood, etc.
- **REST API**: Clean, documented API with OpenAPI/Swagger
- **Production Ready**: Docker support, logging, error handling, CORS

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Run the API

#### Option A: Direct Python

```bash
cd api
python -m uvicorn main:app --reload --port 8000
```

#### Option B: Docker

```bash
docker-compose up --build
```

### 4. Access the API

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T12:34:56.789Z"
}
```

### Get Collections

**GET** `/collections`

Returns all available hadith collections with vector counts.

```json
[
  {
    "name": "hadith-bukhari",
    "vector_count": 7563
  },
  {
    "name": "hadith-muslim",
    "vector_count": 7422
  }
]
```

### Search Hadiths

**POST** `/search`

Search for hadiths with AI-powered semantic understanding.

**Request Body:**

```json
{
  "query": "What did the Prophet say about prayer?",
  "user_id": "user_123",
  "session_id": "session_abc",
  "top_k": 5,
  "collections": ["hadith-bukhari", "hadith-muslim"]
}
```

**Parameters:**
- `query` (required): User's search query (1-500 chars)
- `user_id` (optional): User identifier for tracking
- `session_id` (optional): Session ID for conversation context
- `top_k` (optional): Number of results (1-50, default: 10)
- `collections` (optional): Specific collections to search (default: all)

**Response:**

```json
{
  "query": "What did the Prophet say about prayer?",
  "enhanced_query": "What did the Prophet say about prayer? salah, prayer times, Book of Prayer...",
  "query_type": "HADITH_QUERY",
  "results": [
    {
      "score": 0.89,
      "collection": "hadith-bukhari",
      "hadith_id": 528,
      "collection_reference": "Sahih al-Bukhari 528",
      "in_book_reference": "Book 9, Hadith 7",
      "web_reference": "Vol. 1, Book 9, Hadith 507",
      "grading": "Sahih",
      "narrator": "Narrated Abu Huraira",
      "text": "Allah's Messenger (ﷺ) said, 'The prayer offered in congregation is twenty five times more superior...'",
      "arabic": "حَدَّثَنَا عَبْدُ اللَّهِ بْنُ يُوسُفَ..."
    }
  ],
  "total_results": 1,
  "searched_collections": ["hadith-bukhari", "hadith-muslim"],
  "timestamp": "2025-11-08T12:34:56.789Z"
}
```

**Query Types:**
- `HADITH_QUERY`: Actual hadith search (returns results)
- `GREETING`: User greeting (returns empty results with friendly message)
- `OFF_TOPIC`: Non-Islamic query (returns empty results with redirect message)

## Example Usage

### cURL

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What did the Prophet say about fasting?",
    "top_k": 5
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "What did the Prophet say about charity?",
        "top_k": 5,
        "collections": ["hadith-bukhari"]
    }
)

data = response.json()
for result in data["results"]:
    print(f"Score: {result['score']:.2f}")
    print(f"Text: {result['text'][:200]}...")
    print()
```

### JavaScript (Fetch)

```javascript
const response = await fetch('http://localhost:8000/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "What did the Prophet say about honesty?",
    top_k: 5
  })
});

const data = await response.json();
console.log(data.results);
```

## Deployment

### Railway (Recommended)

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repo
3. Add environment variables:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
4. Deploy!

Railway will automatically detect the Dockerfile and deploy.

### Render

1. Create new Web Service on [Render](https://render.com)
2. Connect repo
3. Set build command: `docker build -t hadithgpt .`
4. Set start command: `docker run -p $PORT:8000 hadithgpt`
5. Add environment variables

### AWS/GCP/Azure

Use the included Dockerfile:

```bash
docker build -t hadithgpt-api .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e PINECONE_API_KEY=your-key \
  hadithgpt-api
```

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
cd api
uvicorn main:app --reload --port 8000
```

### Testing the API

Visit http://localhost:8000/docs for interactive Swagger documentation.

### Adding New Collections

1. Add hadith data to `Data/` folder (JSONL format)
2. Run embedding script:
   ```bash
   python embed_hadiths.py YourCollection_cleaned.jsonl
   ```
3. Restart API - new collection will be automatically available

## Architecture

```
User Query
    ↓
[Classification] → Is it a hadith query?
    ↓ (if yes)
[Query Enhancement] → GPT adds context
    ↓
[Embedding] → Convert to 3072-dim vector
    ↓
[Pinecone Search] → Find similar hadiths
    ↓
[Ranking & Filtering] → Sort by score
    ↓
[Response] → Return results
```

## Configuration

Edit `api/main.py` constants:

```python
EMBEDDING_MODEL = "text-embedding-3-large"  # 3072 dimensions
LLM_MODEL = "gpt-4o-mini"  # Query enhancement
TOP_K = 10  # Default number of results
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Resource not found (e.g., invalid collection)
- `500`: Internal server error

Error response format:

```json
{
  "detail": "Error message here"
}
```

## Performance

- Query classification: ~50ms
- Query enhancement: ~200-500ms
- Embedding creation: ~100-200ms
- Pinecone search: ~50-150ms
- **Total**: ~400-900ms per query

For production, consider:
- Caching frequent queries (Redis)
- Rate limiting
- CDN for static responses
- Load balancing for high traffic

## Security

**Important**: Before production deployment:

1. Update CORS settings in `api/main.py`:
   ```python
   allow_origins=["https://yourdomain.com"]  # Not "*"
   ```

2. Add authentication middleware
3. Set up rate limiting
4. Use environment-based configuration
5. Enable HTTPS only

## Support

For issues or questions:
- GitHub Issues: [Your repo]
- Email: [Your email]

## License

[Your license here]
