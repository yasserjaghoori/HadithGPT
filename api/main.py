"""
HadithGPT API - FastAPI Backend
Production-ready API for hadith search with conversation memory support
"""

import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "").strip()
EMBEDDING_MODEL = "text-embedding-3-large"  # 3072 dimensions
LLM_MODEL = "gpt-4o-mini"
TOP_K = 10

# Global clients (initialized on startup)
openai_client = None
pinecone_client = None
available_indexes = []


# Pydantic Models
class QueryRequest(BaseModel):
    """Request model for hadith search"""
    query: str = Field(..., min_length=1, max_length=500, description="User's search query")
    user_id: Optional[str] = Field(None, description="Optional user ID for tracking")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation context")
    top_k: Optional[int] = Field(10, ge=1, le=50, description="Number of results to return")
    collections: Optional[List[str]] = Field(None, description="Specific collections to search (default: all)")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What did the Prophet say about prayer?",
                "user_id": "user_123",
                "session_id": "session_abc",
                "top_k": 5,
                "collections": ["hadith-bukhari", "hadith-muslim"]
            }
        }


class HadithResult(BaseModel):
    """Model for a single hadith result"""
    score: float = Field(..., description="Similarity score (0-1)")
    collection: str = Field(..., description="Collection name")
    hadith_id: int = Field(..., description="Hadith ID")
    collection_reference: str = Field(..., description="Collection reference")
    in_book_reference: str = Field(..., description="In-book reference")
    web_reference: str = Field(..., description="Web reference")
    grading: str = Field(..., description="Hadith grading")
    narrator: str = Field(..., description="Narrator chain")
    text: str = Field(..., description="Hadith text in English")
    arabic: str = Field(..., description="Hadith text in Arabic")


class HadithCluster(BaseModel):
    """Model for a cluster of similar hadiths describing the same event"""
    event_title: str = Field(..., description="LLM-generated title describing the event")
    primary_index: int = Field(..., description="Index of the primary/best hadith to show first")
    hadith_indices: List[int] = Field(..., description="Indices of all hadiths in this cluster")
    reasoning: Optional[str] = Field(None, description="Why these hadiths were grouped together")


class QueryResponse(BaseModel):
    """Response model for hadith search"""
    query: str
    enhanced_query: str
    query_type: str = Field(..., description="HADITH_QUERY, GREETING, or OFF_TOPIC")
    message: Optional[str] = Field(None, description="Optional message for non-hadith queries")
    results: List[HadithResult]
    total_results: int
    searched_collections: List[str]
    timestamp: str
    clusters: Optional[List[HadithCluster]] = Field(None, description="Optional clusters of similar hadiths")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    available_collections: List[Dict[str, Any]]


class CollectionInfo(BaseModel):
    """Information about a hadith collection"""
    name: str
    vector_count: int


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize clients on startup, cleanup on shutdown"""
    global openai_client, pinecone_client, available_indexes

    logger.info("Starting HadithGPT API...")

    # Validate API keys
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set!")
        raise RuntimeError("OPENAI_API_KEY environment variable is required")
    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY not set!")
        raise RuntimeError("PINECONE_API_KEY environment variable is required")

    # Initialize clients
    try:
        # Create httpx client without proxies to avoid Vercel compatibility issues
        import httpx
        http_client = httpx.Client(timeout=60.0)
        openai_client = OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)
        pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

        # Get available indexes
        available_indexes = [idx.name for idx in pinecone_client.list_indexes()]

        logger.info(f"✓ OpenAI client initialized")
        logger.info(f"✓ Pinecone client initialized")
        logger.info(f"✓ Available collections: {', '.join(available_indexes)}")

    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        raise

    yield

    # Cleanup (if needed)
    logger.info("Shutting down HadithGPT API...")


# Initialize FastAPI app
app = FastAPI(
    title="HadithGPT API",
    description="AI-powered hadith search API with semantic understanding",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Core Logic Functions
def classify_query(query: str) -> tuple[str, str]:
    """
    Classify if query is a hadith search, greeting, or off-topic.
    Returns: (classification, message)
    """
    system_prompt = """You are a hadith search assistant.

Determine if the user is asking for a hadith or just greeting/chatting.

Respond with ONLY ONE of these:
1. "HADITH_QUERY" - if they're asking about Islamic knowledge, hadith, or Prophet's teachings
2. "GREETING" - if they're just saying hi, hello, how are you, etc.
3. "OFF_TOPIC" - if they're asking about non-Islamic topics

Examples:
- "What did the Prophet say about prayer?" → HADITH_QUERY
- "Tell me about fasting" → HADITH_QUERY
- "Hey what's up" → GREETING
- "asalamu alaikum" → GREETING
- "What's the weather?" → OFF_TOPIC"""

    try:
        response = openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.0,
            max_tokens=20
        )
        classification = response.choices[0].message.content.strip().upper()

        if "HADITH_QUERY" in classification:
            return "HADITH_QUERY", ""
        elif "GREETING" in classification:
            return "GREETING", "وعليكم السلام! (Wa alaikum salaam!) Welcome! 🤲 I'm here to help you find Hadiths."
        else:
            return "OFF_TOPIC", "I specialize in finding Hadiths. Ask me about what the Prophet Muhammad (ﷺ) said or did!"

    except Exception as e:
        logger.warning(f"Classification failed: {e}. Assuming HADITH_QUERY")
        return "HADITH_QUERY", ""


def enhance_query(query: str) -> str:
    """Enhance query with GPT to identify specific hadiths"""
    system_prompt = """You are a hadith disambiguator and search query enhancer.

Your task is to help find the EXACT hadith or cluster of hadiths the user is looking for.

For FAMOUS/CONTROVERSIAL hadiths (like "slave girl hadith", "fly in drink", etc.):
- Identify the specific well-known hadith
- Include distinctive phrases from the hadith text
- Include the controversial/discussion point

For TOPICAL queries (like "praying in a row alone", "charity in Ramadan"):
- Extract the specific fiqh/aqeedah topic
- Include related common Arabic terminology transliterations (salah, sadaqah, barzakh (barzaq), etc.)
- Include relevant narrator names if applicable
- Include book sections (Book of Prayer, Book of Fasting, etc.)
- Include related actions/scenarios described in the hadith

For BOTH types:
- Do NOT add broad ethical expansions
- Do NOT generalize to generic themes
- Focus on EXACT phrases and terms that would appear in the hadith text
- Include Arabic transliterations of key terms

Return a search-optimized string with canonical identifiers, key phrases, narrator names, Arabic terms, and subject tags."""

    user_prompt = f"""User's original query: "{query}"

Analyze this query and provide:
1. If it's a famous/controversial hadith - identify the specific hadith and its key identifiers
2. If it's a topical query - extract the precise topic, related terms, and Arabic terminology
3. Key phrases that would appear in the hadith text
4. Relevant narrator names
5. Subject classification (salah/prayer, zakah/charity, aqeedah/creed, etc.)

Output format: A search-optimized string combining all these elements."""

    try:
        response = openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=300
        )
        enhanced = response.choices[0].message.content.strip()
        return f"{query} {enhanced}"

    except Exception as e:
        logger.warning(f"Query enhancement failed: {e}. Using original query")
        return query


def create_embedding(text: str) -> List[float]:
    """Create embedding vector from text"""
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embedding: {str(e)}"
        )


def search_collection(index_name: str, query_vector: List[float], top_k: int) -> List[Dict]:
    """Search a single Pinecone index"""
    try:
        index = pinecone_client.Index(index_name)
        results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )

        matches = []
        for match in results.matches:
            metadata = match.metadata
            matches.append({
                "score": match.score,
                "collection": index_name,
                "hadith_id": metadata.get("hadith_id"),
                "collection_reference": metadata.get("collection_reference", ""),
                "in_book_reference": metadata.get("in_book_reference", ""),
                "web_reference": metadata.get("web_reference", ""),
                "grading": metadata.get("grading", ""),
                "narrator": metadata.get("narrator", ""),
                "text": metadata.get("text", ""),
                "arabic": metadata.get("arabic", "")
            })

        return matches

    except Exception as e:
        logger.error(f"Error searching {index_name}: {e}")
        return []


def cluster_hadiths(hadiths: List[Dict]) -> Optional[List[Dict]]:
    """
    Use LLM to cluster hadiths that describe the same event.

    Args:
        hadiths: List of hadith dictionaries with text, narrator, etc.

    Returns:
        List of cluster dictionaries or None if clustering fails/not needed
    """
    if len(hadiths) < 2:
        # No point clustering with less than 2 hadiths
        return None

    try:
        # Prepare hadith summaries for the LLM
        hadith_summaries = []
        for i, hadith in enumerate(hadiths):
            summary = f"""Hadith {i}:
Collection: {hadith['collection']}
Reference: {hadith['collection_reference']}
Narrator: {hadith['narrator']}
Text: {hadith['text'][:500]}..."""  # Limit text length
            hadith_summaries.append(summary)

        hadiths_text = "\n\n".join(hadith_summaries)

        system_prompt = """You are an expert Islamic scholar specializing in hadith analysis.

Your task is to identify which hadiths describe the EXACT SAME SPECIFIC EVENT, not just similar themes or topics.

STRICT CLUSTERING RULES:
1. ONLY cluster if hadiths describe the SAME specific incident with:
   - Same people involved (e.g., names such as "Umar bin Abi Salama" or characters such as "the boy", "the slave girl", "merchant")
   - Same time/place (e.g., "at a meal with a tailor")
   - Same specific conversation or action
   - IF it's the same narrator AND same event, they can be clustered

2. DO NOT cluster if hadiths only share:
   - Similar topic (eating etiquette)
   - Similar teaching (eat with right hand)
   - Similar context (Prophet teaching companions)

3. Examples:
   ✓ CLUSTER: "Prophet teaching Umar bin Abi Salama as a boy at mealtime" (specific boy, specific event)
   ✗ DO NOT CLUSTER: "Prophet teaching about eating with right hand" (general teaching, different occasions)

   ✓ CLUSTER: "The fly falling in the drink incident" (specific event)
   ✗ DO NOT CLUSTER: "Hadiths about insects in food" (general topic)

4. For each cluster, pick the PRIMARY hadith (best chain, most detail)

5. THERE SHOULD NEVER BE DUPLICATE HADITHS ACROSS CLUSTERS!!!!!!!!!!

6. Give each cluster a SPECIFIC descriptive title mentioning the people/place involved

Return your analysis as a JSON object:
{
  "clusters": [
    {
      "event_title": "Specific event title (include people/place)",
      "primary_index": 0,
      "hadith_indices": [0, 3, 5],
      "reasoning": "Why these describe the EXACT same event"
    }
  ],
  "standalone_indices": [1, 2, 4]
}

If NO hadiths should be clustered, return:
{
  "clusters": [],
  "standalone_indices": [0, 1, 2, ...]
}

Be reasonable in clustering - cluster hadiths that clearly describe the same event, but don't force unrelated hadiths together."""

        user_prompt = f"""Analyze these {len(hadiths)} hadiths and identify which ones describe the same events:

{hadiths_text}

Remember: Only cluster hadiths that describe the EXACT SAME event, not just similar topics."""

        response = openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)

        # Validate the response
        if "clusters" not in result:
            logger.warning("LLM did not return clusters field")
            return None

        # Only return clusters if there are actual clusters (not all standalone)
        if len(result["clusters"]) == 0:
            logger.info("No hadiths were clustered - all describe different events")
            return None

        logger.info(f"Successfully clustered hadiths: {len(result['clusters'])} clusters found")
        return result["clusters"]

    except Exception as e:
        logger.error(f"Clustering failed: {e}", exc_info=True)
        # If clustering fails, just return None - the UI will show individual hadiths
        return None


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    collection_info = []
    for idx_name in available_indexes:
        try:
            index = pinecone_client.Index(idx_name)
            stats = index.describe_index_stats()
            collection_info.append({
                "name": idx_name,
                "vector_count": stats.get("total_vector_count", 0)
            })
        except Exception as e:
            logger.error(f"Error getting stats for {idx_name}: {e}")
            collection_info.append({"name": idx_name, "vector_count": 0})

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        available_collections=collection_info
    )


@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/collections", response_model=List[CollectionInfo])
async def get_collections():
    """Get list of available hadith collections"""
    collections = []
    for idx_name in available_indexes:
        try:
            index = pinecone_client.Index(idx_name)
            stats = index.describe_index_stats()
            collections.append(CollectionInfo(
                name=idx_name,
                vector_count=stats.get("total_vector_count", 0)
            ))
        except Exception as e:
            logger.error(f"Error getting stats for {idx_name}: {e}")
            collections.append(CollectionInfo(name=idx_name, vector_count=0))

    return collections


@app.post("/search", response_model=QueryResponse)
async def search_hadiths(request: QueryRequest):
    """
    Search for hadiths across collections.

    This endpoint:
    1. Classifies the query (hadith search vs greeting vs off-topic)
    2. Enhances the query with GPT for better semantic matching
    3. Creates an embedding vector
    4. Searches specified collections (or all if not specified)
    5. Returns ranked results
    """
    try:
        # Step 1: Classify query
        query_type, message = classify_query(request.query)

        if query_type != "HADITH_QUERY":
            return QueryResponse(
                query=request.query,
                enhanced_query=request.query,
                query_type=query_type,
                message=message,
                results=[],
                total_results=0,
                searched_collections=[],
                timestamp=datetime.utcnow().isoformat(),
                clusters=None
            )

        # Step 2: Use default 10 results (simple and predictable)
        top_k = request.top_k if request.top_k else 10
        logger.info(f"Fetching top {top_k} results")

        # Step 3: Enhance query
        enhanced_query = enhance_query(request.query)
        logger.info(f"Enhanced query: {enhanced_query}")

        # Step 4: Create embedding
        query_vector = create_embedding(enhanced_query)

        # Step 5: Determine which collections to search
        if request.collections:
            # Validate requested collections
            invalid = [c for c in request.collections if c not in available_indexes]
            if invalid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid collections: {', '.join(invalid)}. Available: {', '.join(available_indexes)}"
                )
            collections_to_search = request.collections
        else:
            collections_to_search = available_indexes

        if not collections_to_search:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hadith collections found. Please run embed_hadiths.py first."
            )

        # Step 6: Search all collections
        all_results = []
        for collection in collections_to_search:
            results = search_collection(collection, query_vector, top_k)
            all_results.extend(results)

        # Step 7: Sort by score and take top results
        all_results.sort(key=lambda x: x["score"], reverse=True)
        top_results = all_results[:top_k]

        # Convert to Pydantic models
        hadith_results = [HadithResult(**r) for r in top_results]

        # Step 8: Cluster hadiths (optional - LLM decides)
        clusters = None
        if len(top_results) >= 2:
            logger.info("Attempting to cluster hadiths...")
            cluster_data = cluster_hadiths(top_results)
            if cluster_data:
                clusters = [HadithCluster(**c) for c in cluster_data]
                logger.info(f"Created {len(clusters)} clusters")

        return QueryResponse(
            query=request.query,
            enhanced_query=enhanced_query,
            query_type=query_type,
            message=None,
            results=hadith_results,
            total_results=len(hadith_results),
            searched_collections=collections_to_search,
            timestamp=datetime.utcnow().isoformat(),
            clusters=clusters
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
