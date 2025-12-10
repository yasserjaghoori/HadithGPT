#!/bin/bash
# Helper script to set up environment variables for HadithGPT

echo "HadithGPT - Environment Setup"
echo "============================="
echo ""
echo "This script will help you set up your API keys."
echo "You can also manually set them using:"
echo "  export OPENAI_API_KEY='your-key'"
echo "  export PINECONE_API_KEY='your-key'"
echo ""

read -p "Enter your OpenAI API key: " openai_key
read -p "Enter your Pinecone API key: " pinecone_key

export OPENAI_API_KEY="$openai_key"
export PINECONE_API_KEY="$pinecone_key"

echo ""
echo "Environment variables set for this session!"
echo ""
echo "To make them permanent, add these lines to your ~/.zshrc or ~/.bashrc:"
echo "  export OPENAI_API_KEY='$openai_key'"
echo "  export PINECONE_API_KEY='$pinecone_key'"
echo ""
echo "You can now run:"
echo "  python embed_hadiths.py"
echo "  python query_hadiths.py \"your query\""
echo ""

