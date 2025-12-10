"""
Query script for Hadith retrieval from Pinecone.

This script uses OpenAI GPT to deeply understand your query, then searches Pinecone for relevant Hadiths.

How it works:
1. 🔍 Your query → GPT understands/enhances it → Better search terms
2. 🎯 Enhanced query → Embedded → Searches Pinecone database
3. 📚 Returns raw Hadith results (no GPT interpretation)
"""

import os
import sys
from typing import List, Dict, Any
from openai import OpenAI
from pinecone import Pinecone

# Configuration
# SECURITY WARNING: Don't hardcode API keys! Use environment variables instead.
# Set them with: export OPENAI_API_KEY="your-key" and export PINECONE_API_KEY="your-key"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "").strip()
PINECONE_INDEX_NAME = "hadith-bukhari"
EMBEDDING_MODEL = "text-embedding-3-large"
LLM_MODEL = "gpt-4o-mini"  # Using gpt-4o-mini as it's more reliable
TOP_K = 5  # Number of Hadiths to retrieve


def is_hadith_query(client: OpenAI, user_query: str, model: str = LLM_MODEL) -> tuple[bool, str]:
    """
    Determine if the user is asking for a hadith or just chatting.

    Returns:
        (is_hadith_request, response_message)
        - If True: proceed with hadith search
        - If False: response_message contains a friendly greeting/redirect
    """
    system_prompt = """You are a hadith search assistant.

Your task: Determine if the user is asking for a hadith or just greeting/chatting.

Respond with ONLY ONE of these:
1. "HADITH_QUERY" - if they're asking about Islamic knowledge, hadith, or Prophet's teachings
2. "GREETING" - if they're just saying hi, hello, how are you, etc.
    - IF GREETING, respond with a friendly Islamic greeting and invite them to ask about hadiths.
3. "OFF_TOPIC" - if they're asking about non-Islamic topics
    - IF OFF_TOPIC, direct them back to hadith topics politely.

Examples:
- "What did the Prophet say about prayer?" → HADITH_QUERY
- "Tell me about fasting" → HADITH_QUERY
- "Hey what's up" → GREETING
- "How are you?" → GREETING
- "What's the weather?" → OFF_TOPIC
- "asalamu alaikum" → GREETING"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.0,
            max_tokens=20
        )
        classification = response.choices[0].message.content.strip().upper()

        if "HADITH_QUERY" in classification:
            return True, ""
        elif "GREETING" in classification:
            return False, "وعليكم السلام! (Wa alaikum salaam!) Welcome! 🤲\n\nI'm here to help you find Hadiths. What would you like to know about?\n\nExamples:\n  - 'What did the Prophet say about prayer?'\n  - 'Hadith about charity'\n  - 'Tell me about fasting in Ramadan'"
        else:  # OFF_TOPIC
            return False, "I specialize in finding Hadiths from Islamic traditions. If you have questions about what the Prophet Muhammad (ﷺ) said or did, I'd be happy to help!\n\nTry asking something like:\n  - 'What did the Prophet say about...'\n  - 'Hadith about...'\n  - 'Tell me about... in Islam'"
    except Exception as e:
        # If classification fails, assume it's a hadith query (fail-safe)
        print(f"⚠️ Classification failed: {e}. Proceeding with search...")
        return True, ""


def understand_query(client: OpenAI, user_query: str, model: str = LLM_MODEL) -> str:
    """
    Use GPT to identify specific hadith identifiers and canonical anchors.
    Converts natural language questions into search hints, unique identifiers, and disambiguation metadata.
    """
    system_prompt = """You are a hadith retriever.

Your task is NOT to explain.
Your task is NOT to broaden topic.
Your task is to identify which specific hadith or cluster of hadith the user most probably means.
Do NOT add ethics/morality expansions.
Do NOT generalize to generic themes.

If user's question maps to a known controversial or often referenced hadith, prioritize THAT.

"""

    user_prompt = f"""User's original query: "{user_query}"

Identify the specific hadith or hadith cluster the user most probably means."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,  # Very low temperature for precise identification
            max_tokens=300
        )
        enhanced_query = response.choices[0].message.content.strip()
        
        # Combine original query with enhanced identifiers for better search
        # This gives semantic search both the natural language AND the canonical anchors
        combined_query = f"{user_query} {enhanced_query}"
        return combined_query
    except Exception as e:
        # Try alternative models if the main one doesn't work
        alternative_models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        for alt_model in alternative_models:
            try:
                print(f"⚠️ Trying alternative model: {alt_model}")
                response = client.chat.completions.create(
                    model=alt_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=300
                )
                enhanced_query = response.choices[0].message.content.strip()
                combined_query = f"{user_query} {enhanced_query}"
                return combined_query
            except:
                continue
        
        # Fallback: return original query if all models fail
        print(f"⚠️ Could not enhance query with GPT. Using original query. Error: {str(e)}")
        return user_query


def create_query_embedding(client: OpenAI, query: str) -> List[float]:
    """Create embedding for the search query."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query
    )
    return response.data[0].embedding


def search_hadiths(
    index, 
    query_embedding: List[float], 
    top_k: int = TOP_K,
    filter_dict: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Search for similar Hadiths in Pinecone.
    
    Args:
        index: Pinecone index object
        query_embedding: Query vector
        top_k: Number of results to return
        filter_dict: Optional metadata filter (e.g., {"chapterId": 1})
    
    Returns:
        List of matching Hadiths with metadata and scores
    """
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter_dict
    )
    
    return results.matches


def format_results(matches: List[Dict[str, Any]]) -> str:
    """Format search results for display."""
    output = []
    for i, match in enumerate(matches, 1):
        metadata = match.get('metadata', {})
        score = match.get('score', 0)

        output.append(f"\n{'='*80}")
        output.append(f"Result {i} (Similarity Score: {score:.4f})")
        output.append(f"{'='*80}")
        output.append(f"Hadith ID: {metadata.get('hadith_id', 'N/A')}")
        output.append(f"Collection: {metadata.get('collection_reference', 'N/A')}")
        output.append(f"In-Book Reference: {metadata.get('in_book_reference', 'N/A')}")
        output.append(f"Web Reference: {metadata.get('web_reference', 'N/A')}")
        output.append(f"Grading: {metadata.get('grading', 'N/A')}")
        output.append(f"\n📖 Narrator:")
        output.append(f"  {metadata.get('narrator', 'N/A')}")
        output.append(f"\n📝 Text:")
        text = metadata.get('text', 'N/A')
        # Print text with word wrap
        words = text.split()
        line = []
        line_len = 0
        for word in words:
            if line_len + len(word) + 1 > 80:
                output.append(' '.join(line))
                line = [word]
                line_len = len(word)
            else:
                line.append(word)
                line_len += len(word) + 1
        if line:
            output.append(' '.join(line))
        output.append(f"\n🕌 Arabic (truncated):")
        output.append(f"  {metadata.get('arabic', 'N/A')[:200]}...")

    return '\n'.join(output)


def main():
    # Get query from command line or prompt
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        print("="*80)
        print("🔍 Hadith Search")
        print("="*80)
        print("\nWhat Hadith are you looking for?")
        print("Examples:")
        print("  - 'What did the Prophet say about prayer?'")
        print("  - 'Hadith about fasting in Ramadan'")
        print("  - 'Mercy and compassion'")
        print()
        query = input("Enter your query: ").strip()
        print()
    
    if not query:
        print("❌ No query provided. Exiting.")
        return
    
    # Initialize clients
    if not OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY environment variable not set")
        print("\nTo fix this, run:")
        print('  export OPENAI_API_KEY="your-openai-api-key"')
        print('  export PINECONE_API_KEY="your-pinecone-api-key"')
        print("\nOr add them to your shell config file (~/.zshrc for zsh):")
        print('  echo \'export OPENAI_API_KEY="your-key"\' >> ~/.zshrc')
        print('  echo \'export PINECONE_API_KEY="your-key"\' >> ~/.zshrc')
        print('  source ~/.zshrc')
        sys.exit(1)
    if not PINECONE_API_KEY:
        print("❌ ERROR: PINECONE_API_KEY environment variable not set")
        print("\nTo fix this, run:")
        print('  export PINECONE_API_KEY="your-pinecone-api-key"')
        print("\nOr add it to your shell config file (~/.zshrc for zsh):")
        print('  echo \'export PINECONE_API_KEY="your-key"\' >> ~/.zshrc')
        print('  source ~/.zshrc')
        sys.exit(1)
    
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Get index
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing_indexes:
        raise ValueError(f"Index '{PINECONE_INDEX_NAME}' not found! Make sure you've run embed_hadiths.py first.")
    
    index = pc.Index(PINECONE_INDEX_NAME)
    
    # Check index stats
    stats = index.describe_index_stats()
    print(f"✓ Connected to Pinecone index: {PINECONE_INDEX_NAME}")
    print(f"  Total vectors in index: {stats.get('total_vector_count', 'N/A')}")
    print(f"  Using embedding model: {EMBEDDING_MODEL}")
    print(f"  Using LLM model: {LLM_MODEL}")
    print(f"  Top K results: {TOP_K}\n")
    
    # STEP 0: Check if this is actually a hadith query
    print("="*80)
    print("🔍 STEP 0: Analyzing Query Type")
    print("="*80)
    is_hadith, greeting_message = is_hadith_query(openai_client, query, model=LLM_MODEL)

    if not is_hadith:
        print("\n" + greeting_message)
        return

    print("✓ Detected: Hadith search request\n")

    print("="*80)
    print("🔍 STEP 1: Identifying Specific Hadith with GPT")
    print("="*80)
    print(f"Original query: \"{query}\"\n")
    print("Identifying canonical identifiers, narrator names, Arabic key phrases, and subject tags...\n")

    # Use GPT to identify specific hadith anchors (not semantic broadening)
    enhanced_query = understand_query(openai_client, query, model=LLM_MODEL)
    
    print(f"✓ Search query with canonical anchors:\n   {enhanced_query}\n")
    
    print("="*80)
    print("🎯 STEP 2: Searching Pinecone Database")
    print("="*80)
    print("Creating embedding and searching...\n")
    
    # Create embedding from the enhanced query
    query_embedding = create_query_embedding(openai_client, enhanced_query)
    
    # Search (optional: add filters)
    # Example filter: {"chapterId": 1} to search only in chapter 1
    filter_dict = None  # Add filters here if needed
    
    matches = search_hadiths(index, query_embedding, top_k=TOP_K, filter_dict=filter_dict)
    
    if not matches:
        print("❌ No results found.")
        return
    
    # Display retrieved Hadiths (raw results, no GPT interpretation)
    print("\n" + "="*80)
    print(f"📚 RETRIEVED HADITHS (Top {len(matches)} results):")
    print("="*80)
    print(format_results(matches))
    
    # Display summary
    print("\n" + "="*80)
    print("📊 SEARCH SUMMARY")
    print("="*80)
    print(f"Found {len(matches)} relevant Hadiths")
    print(f"Top similarity score: {matches[0].get('score', 0):.4f}")
    print(f"Average similarity score: {sum(m.get('score', 0) for m in matches) / len(matches):.4f}")
    print("\n✓ Search complete! Review the Hadiths above to find your answer.")


if __name__ == "__main__":
    main()

