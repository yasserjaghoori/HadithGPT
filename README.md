# HadithGPT 🤲

AI-powered hadith search application with semantic understanding using OpenAI embeddings and Pinecone vector database.

## 📋 Overview

HadithGPT is a modern web application that allows users to search through hadith collections using natural language queries. It uses advanced AI technology to understand query intent and find the most relevant hadiths across multiple authenticated collections.

### Features

- 🔍 **Semantic Search**: Natural language queries powered by OpenAI embeddings
- 📚 **Multiple Collections**: Search across 7 major hadith collections (Bukhari, Muslim, Abu Dawud, Tirmidhi, Nasai, Ibn Majah, Musnad Ahmed)
- 🤖 **Smart Query Enhancement**: AI-powered query understanding and disambiguation
- 🔗 **Hadith Clustering**: Automatically groups hadiths describing the same event
- 🎨 **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS
- 🌙 **Dark Mode**: Toggle between light and dark themes
- 📱 **Mobile Friendly**: Fully responsive design

## 🏗️ Architecture

- **Frontend**: Next.js 14 (React) with TypeScript
- **Backend**: FastAPI (Python)
- **Vector Database**: Pinecone
- **AI/ML**: OpenAI (embeddings + GPT-4o-mini)
- **Styling**: Tailwind CSS
- **Authentication** (optional): Supabase

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+** (with pip)
- **Node.js 18+** (with npm)
- **Git**

You'll also need API keys from:
- [OpenAI](https://platform.openai.com/api-keys)
- [Pinecone](https://app.pinecone.io/)
- [Supabase](https://supabase.com/) (optional, for authentication)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yasserjaghoori/HadithGPT.git
cd HadithGPT
```

### 2. Set Up Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=your-openai-api-key-here

# Pinecone API Key (required)
PINECONE_API_KEY=your-pinecone-api-key-here

# Supabase (optional - for user auth)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 3. Install Backend Dependencies

```bash
pip install -r api/requirements.txt
```

### 4. Prepare Hadith Data (One-time setup)

If you haven't already embedded your hadith collections in Pinecone:

```bash
# Make sure your hadith data files are in the Data/ directory
python embed_hadiths.py
```

This will:
- Read hadith collections from the `Data/` folder
- Create embeddings using OpenAI
- Store vectors in Pinecone (one index per collection)

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 6. Run the Application

You need to run both the backend and frontend:

#### Terminal 1: Start the Backend API

```bash
python3 api/main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

#### Terminal 2: Start the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at:
- **Website**: http://localhost:3000

### 7. Access the Application

Open your browser and navigate to **http://localhost:3000**

## 🎯 Usage

### Basic Search

1. Open http://localhost:3000
2. Enter a query in natural language:
   - "What did the Prophet say about prayer?"
   - "Hadiths about charity in Ramadan"
   - "The hadith about the fly in the drink"
3. View the results with full hadith text, narrator chains, and references

### API Usage

You can also use the API directly:

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What did the Prophet say about prayer?",
    "top_k": 5
  }'
```

## 📁 Project Structure

```
HadithGPT/
├── api/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js pages
│   │   ├── components/     # React components
│   │   ├── lib/            # Utilities and API clients
│   │   └── types/          # TypeScript types
│   ├── package.json
│   └── next.config.js
├── Data/                    # Hadith data files (JSONL)
├── embed_hadiths.py        # Script to embed hadiths
├── query_hadiths.py        # CLI query tool
├── .env                    # Environment variables (not in repo)
├── .env.example            # Example environment file
└── README.md
```

## 🛠️ Development

### Backend Development

The backend uses FastAPI with automatic reload:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

Next.js development server with hot reload:

```bash
cd frontend
npm run dev
```

### Adding New Hadith Collections

1. Add your hadith collection as a JSONL file in the `Data/` directory
2. Each line should be a JSON object with these fields:
   ```json
   {
     "hadith_id": 1,
     "collection_reference": "Sahih Bukhari 1",
     "narrator": "Narrated by...",
     "text": "The hadith text in English",
     "arabic": "النص العربي",
     "grading": "Sahih",
     "in_book_reference": "Book 1, Hadith 1",
     "web_reference": "https://..."
   }
   ```
3. Run the embedding script:
   ```bash
   python embed_hadiths.py
   ```

## 🔧 Configuration

### Backend Configuration

Edit `api/main.py` to customize:

- `EMBEDDING_MODEL`: OpenAI embedding model (default: `text-embedding-3-large`)
- `LLM_MODEL`: GPT model for query enhancement (default: `gpt-4o-mini`)
- `TOP_K`: Default number of results (default: 10)

### Frontend Configuration

Edit `frontend/src/lib/api.ts` to customize the API endpoint if needed.

## 📊 API Endpoints

### `POST /search`
Search for hadiths

**Request:**
```json
{
  "query": "What did the Prophet say about prayer?",
  "top_k": 10,
  "collections": ["hadith-bukhari", "hadith-muslim"]
}
```

**Response:**
```json
{
  "query": "What did the Prophet say about prayer?",
  "enhanced_query": "...",
  "query_type": "HADITH_QUERY",
  "results": [...],
  "total_results": 10,
  "searched_collections": ["hadith-bukhari", "hadith-muslim"],
  "clusters": [...],
  "timestamp": "2025-12-10T23:00:00"
}
```

### `GET /collections`
Get list of available hadith collections

### `GET /health`
Health check endpoint

## 🐛 Troubleshooting

### Port Already in Use

If port 8000 or 3000 is already in use:

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### API Key Errors

Make sure your `.env` file has valid API keys and is in the root directory.

### Missing Dependencies

```bash
# Backend
pip install -r api/requirements.txt

# Frontend
cd frontend && npm install
```

### Import Errors (VSCode)

If you see red underlines in VSCode for imports:
1. Press `Cmd + Shift + P` (macOS) or `Ctrl + Shift + P` (Windows/Linux)
2. Type "Python: Select Interpreter"
3. Choose the Python interpreter where packages are installed

### Notes on Git/GitHub: 
https://docs.google.com/document/d/1z92pn1YjdGyuWs3j3WZZJBX4JxNrAGJF6LNLqGpze1A/edit?usp=sharing

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

## 🙏 Acknowledgments

- Hadith data sourced from authenticated collections
- Built with [OpenAI](https://openai.com/), [Pinecone](https://www.pinecone.io/), [FastAPI](https://fastapi.tiangolo.com/), and [Next.js](https://nextjs.org/)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
