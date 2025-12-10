"""
Script to embed Hadiths from Sahih Bukhari and upload to Pinecone.

This script:
1. Loads Hadiths from the JSON file
2. Creates embeddings using OpenAI's embedding model
3. Uploads to Pinecone with metadata for filtering

⚠️ IMPORTANT: Index Management
- Same index name, different Hadith IDs → Will ADD new Hadiths (both collections in index)
- Same index name, same Hadith IDs → Will REPLACE existing Hadiths with those IDs
- Different index name → Creates a separate index (recommended for different collections)

For different Hadith collections, change PINECONE_INDEX_NAME below.
Examples: "hadith-bukhari", "hadith-muslim", "hadith-abudawud"
"""

import json
import os
import sys
import glob
from typing import List, Dict, Any, Optional
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import time

# Configuration
# SECURITY WARNING: Don't hardcode API keys! Use environment variables instead.
# Set them with: export OPENAI_API_KEY="your-key" and export PINECONE_API_KEY="your-key"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "").strip()

EMBEDDING_MODEL = "text-embedding-3-large"  # 3072 dimensions (text-embedding-3-small = 1536 dimensions)
BATCH_SIZE = 100  # Process Hadiths in batches

# Collection to index name mapping (auto-generated, but you can override)
COLLECTION_MAPPING = {
    "bukhari": "hadith-bukhari",
    "sahih-bukhari": "hadith-bukhari",
    "muslim": "hadith-muslim",
    "sahih-muslim": "hadith-muslim",
    "abudawud": "hadith-abudawud",
    "sunan-abudawud": "hadith-abudawud",
    "abu-dawood": "hadith-abudawud",
    "tirmidhi": "hadith-tirmidhi",
    "sunan-tirmidhi": "hadith-tirmidhi",
    "nasai": "hadith-nasai",
    "sunan-nasai": "hadith-nasai",
    "sunan-an-nasai": "hadith-nasai",
    "ibn-majah": "hadith-ibn-majah",
    "sunan-ibn-majah": "hadith-ibn-majah",
}


def get_index_name_from_filename(filename: str) -> str:
    """Generate index name from filename."""
    # Extract name without extension and path
    basename = os.path.basename(filename).replace('.jsonl', '').replace('.json', '').lower()

    # Remove common prefixes/suffixes (dates, spaces, cleaned suffix, etc.)
    basename = basename.replace(' 10.46.04 pm', '').replace('_cleaned', '').replace(' ', '-').strip()

    # Check if we have a mapping
    for key, index_name in COLLECTION_MAPPING.items():
        if key in basename:
            return index_name

    # Default: create index name from filename
    # Remove special characters, keep only alphanumeric and hyphens
    clean_name = ''.join(c if c.isalnum() or c == '-' else '' for c in basename)
    return f"hadith-{clean_name}"


def list_available_collections() -> List[str]:
    """List all JSONL files in Data/ directory."""
    jsonl_files = glob.glob("Data/*.jsonl")
    if not jsonl_files:
        jsonl_files = glob.glob("*.jsonl")
    return sorted(jsonl_files)


def load_hadiths(jsonl_file_path: str) -> List[Dict[str, Any]]:
    """Load Hadiths from JSONL file (one JSON object per line)."""
    hadiths = []
    with open(jsonl_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                hadith = json.loads(line)
                # Add a unique ID for each hadith (line number)
                hadith['id'] = line_num
                hadiths.append(hadith)
            except json.JSONDecodeError as e:
                print(f"  ⚠️ Warning: Skipping invalid JSON on line {line_num}: {e}")
                continue
    return hadiths


def prepare_hadith_text(hadith: Dict[str, Any]) -> str:
    """
    Prepare text for embedding.
    Combines English text with collection reference for better semantic search.
    """
    # The "English" field contains the full narration including narrator
    english_text = hadith.get('English', '')

    # Add collection reference for context
    collection_ref = hadith.get('Collection Reference', '')

    # Combine for better context
    combined = f"{english_text} {collection_ref}".strip()
    return combined


def create_embeddings(client: OpenAI, texts: List[str]) -> List[Optional[List[float]]]:
    """Create embeddings for a batch of texts."""
    # Filter out empty strings and None values, and ensure all are strings
    valid_texts = []
    valid_indices = []
    
    for idx, text in enumerate(texts):
        if text and isinstance(text, str) and text.strip():
            # OpenAI has a limit of 8,191 tokens per input
            # For safety, we'll also check length (roughly 32k chars = ~8k tokens)
            if len(text.strip()) > 32000:
                print(f"  ⚠️ Warning: Hadith {idx} text too long ({len(text)} chars), truncating...")
                text = text[:32000]
            valid_texts.append(text.strip())
            valid_indices.append(idx)
    
    if not valid_texts:
        raise ValueError("No valid texts to embed in this batch!")
    
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=valid_texts
    )
    
    # Map embeddings back to original positions, filling None for invalid texts
    all_embeddings = [None] * len(texts)
    for i, embedding in enumerate(response.data):
        original_idx = valid_indices[i]
        all_embeddings[original_idx] = embedding.embedding
    
    return all_embeddings


def prepare_vectors(hadiths: List[Dict[str, Any]], embeddings: List[List[float]], collection_name: str = "") -> List[tuple]:
    """
    Prepare vectors for Pinecone upload.
    Format: (id, vector, metadata)

    Args:
        hadiths: List of hadith dictionaries
        embeddings: List of embedding vectors
        collection_name: Name of the collection (used to ensure unique IDs)
    """
    vectors = []
    for hadith, embedding in zip(hadiths, embeddings):
        english_text = hadith.get('English', '')

        # Extract narrator from the English text (usually first line before \n)
        narrator = ''
        if '\n' in english_text:
            narrator = english_text.split('\n')[0]

        metadata = {
            'hadith_id': hadith['id'],
            'collection_reference': hadith.get('Collection Reference', ''),
            'in_book_reference': hadith.get('In-Book Reference', ''),
            'web_reference': hadith.get('Web Reference', ''),
            'grading': hadith.get('Grading', ''),
            'narrator': narrator[:1000],  # Limit narrator in metadata
            'text': english_text[:15000],  # Limit text in metadata (Pinecone has 40KB limit per vector)
            'arabic': hadith.get('Arabic', '')[:1500]  # Limit Arabic text in metadata
        }

        # Pinecone ID should be unique across ALL collections
        # Include collection name to avoid ID collisions
        if collection_name:
            vector_id = f"{collection_name}_{hadith['id']}"
        else:
            vector_id = f"hadith_{hadith['id']}"
        vectors.append((vector_id, embedding, metadata))

    return vectors


def main():
    # Check for command-line argument (collection name or file path)
    json_file = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        # If it's a direct file path
        if os.path.exists(arg):
            json_file = arg
        # If it's a filename in Data/
        elif os.path.exists(f"Data/{arg}"):
            json_file = f"Data/{arg}"
        elif os.path.exists(f"Data/{arg}.jsonl"):
            json_file = f"Data/{arg}.jsonl"
        elif os.path.exists(f"Data/{arg}.json"):
            json_file = f"Data/{arg}.json"
        else:
            # Try to find by partial match
            all_files = list_available_collections()
            matching = [f for f in all_files if arg.lower() in os.path.basename(f).lower()]
            if matching:
                json_file = matching[0]
            else:
                print(f"❌ Could not find collection matching: {arg}")
                print("\nAvailable collections:")
                for f in all_files:
                    print(f"  - {os.path.basename(f)}")
                return
    
    # Initialize clients
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY environment variable not set")
    
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Find JSONL file if not specified
    if not json_file:
        json_files = list_available_collections()
        if not json_files:
            raise FileNotFoundError("No JSONL file found in Data/ directory or current directory")
        
        if len(json_files) == 1:
            json_file = json_files[0]
        else:
            print("📚 Available collections:")
            for i, f in enumerate(json_files, 1):
                filename = os.path.basename(f)
                print(f"  {i}. {filename}")
            print()
            
            # Interactive selection
            try:
                choice = input("Enter the number or name of collection to process (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    print("Cancelled.")
                    return
                
                # Try as number first
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(json_files):
                        json_file = json_files[choice_num - 1]
                    else:
                        print(f"❌ Invalid number. Please choose 1-{len(json_files)}")
                        return
                except ValueError:
                    # Not a number, try as name
                    matching = [f for f in json_files if choice.lower() in os.path.basename(f).lower()]
                    if matching:
                        json_file = matching[0]
                    else:
                        print(f"❌ Could not find collection matching: {choice}")
                        print("\nUsage: python embed_hadiths.py <collection_name>")
                        print(f"Example: python embed_hadiths.py bukhari")
                        return
            except KeyboardInterrupt:
                print("\n\nCancelled.")
                return
    
    # Generate index name from filename
    PINECONE_INDEX_NAME = get_index_name_from_filename(json_file)
    
    print(f"✓ Initialized OpenAI and Pinecone clients")
    print(f"📁 Loading Hadiths from: {json_file}")
    print(f"📌 Index name: {PINECONE_INDEX_NAME}")
    print(f"📊 Embedding model: {EMBEDDING_MODEL}")
    print(f"📦 Batch size: {BATCH_SIZE}\n")
    
    # Load Hadiths
    hadiths = load_hadiths(json_file)
    print(f"✓ Loaded {len(hadiths)} Hadiths\n")
    
    # Check if index exists, create if not
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    
    if PINECONE_INDEX_NAME not in existing_indexes:
        print(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=3072,  # text-embedding-3-large dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print("Waiting for index to be ready...")
        time.sleep(10)
        print("✓ Index created and ready!")
    else:
        print(f"✓ Using existing index: {PINECONE_INDEX_NAME}")
    
    index = pc.Index(PINECONE_INDEX_NAME)
    
    # Process Hadiths in batches
    total = len(hadiths)
    skipped_count = 0
    print(f"\n🚀 Starting to process {total} Hadiths in batches of {BATCH_SIZE}...\n")
    
    for i in range(0, total, BATCH_SIZE):
        batch = hadiths[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"\n📦 Batch {batch_num}/{total_batches} ({len(batch)} Hadiths)")
        
        # Prepare texts for embedding
        texts = [prepare_hadith_text(h) for h in batch]
        
        # Create embeddings
        print("  Creating embeddings...")
        try:
            embeddings = create_embeddings(openai_client, texts)
        except Exception as e:
            print(f"  ❌ Error creating embeddings: {str(e)}")
            print(f"  📊 Batch info: {len(batch)} Hadiths")
            print(f"  📝 Sample texts (first 3):")
            for i, t in enumerate(texts[:3]):
                print(f"    {i+1}. Length: {len(t) if t else 0}, Preview: {str(t)[:50] if t else 'None'}...")
            raise
        
        # Filter out None embeddings and corresponding hadiths
        valid_pairs = [(h, emb) for h, emb in zip(batch, embeddings) if emb is not None]
        batch_skipped = len(batch) - len(valid_pairs)
        skipped_count += batch_skipped
        
        if batch_skipped > 0:
            print(f"  ⚠️ Skipped {batch_skipped} Hadith(s) with empty/invalid text in this batch")
        
        if not valid_pairs:
            print(f"  ⚠️ Warning: No valid embeddings in batch {batch_num}, skipping...")
            continue
        
        valid_batch, valid_embeddings = zip(*valid_pairs)

        # Prepare vectors (only for valid ones)
        # Use the index name as collection identifier to ensure unique IDs
        vectors = prepare_vectors(list(valid_batch), list(valid_embeddings), collection_name=PINECONE_INDEX_NAME)

        # Upload to Pinecone
        print("  Uploading to Pinecone...")
        index.upsert(vectors=vectors)
        
        print(f"  ✓ Uploaded batch {batch_num}")
        
        # Rate limiting - small delay between batches
        if i + BATCH_SIZE < total:
            time.sleep(1)
    
    uploaded_count = total - skipped_count
    print(f"\n✅ Successfully processed {total} Hadiths!")
    if skipped_count > 0:
        print(f"   📤 Uploaded: {uploaded_count} vectors")
        print(f"   ⚠️ Skipped: {skipped_count} Hadiths (empty/invalid text)")
    else:
        print(f"   📤 Uploaded: {uploaded_count} vectors to Pinecone")
    
    # Print index stats
    stats = index.describe_index_stats()
    actual_count = stats.get('total_vector_count', 0)
    print(f"\n📊 Index Stats:")
    print(f"  Total vectors in index: {actual_count:,}")
    
    if actual_count != uploaded_count:
        print(f"  ⚠️ Note: Index shows {actual_count:,} vectors (expected {uploaded_count:,})")
        print(f"     This is normal if you ran the script multiple times (upsert updates existing vectors)")


if __name__ == "__main__":
    main()

