"""
Q&A Agent using Google Gemini
Handles question answering with RAG retrieval
"""

import google.generativeai as genai
from typing import List, Dict
import os
import json
from supabase_utils import SupabaseManager

def get_secret(key: str, default: str = None) -> str:
    """Get secret from Streamlit secrets or environment variable"""
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except:
        return os.getenv(key, default)


class QAAgent:
    """Question answering agent with RAG"""

    def __init__(self):
        """Initialize agent with Gemini model"""
        gemini_api_key = get_secret('GEMINI_API_KEY')
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        # Configure Gemini
        genai.configure(api_key=gemini_api_key)

        # Get model name from environment (default to gemini-2.0-flash-exp)
        model_name = get_secret('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        self.model = genai.GenerativeModel(model_name)

        # Initialize Supabase manager
        self.supabase = SupabaseManager()

        # System prompt
        self.system_prompt = """You are a helpful assistant that answers questions about company information.

You will be provided with relevant context from company documents including text excerpts and associated images.

Instructions:
1. Answer questions based ONLY on the provided context
2. If the context doesn't contain enough information, say so honestly
3. Be concise and direct
4. Reference specific sections when relevant
5. Indicate if images/charts support your answer

Response format (return as JSON):
{
  "answer": "Your clear, concise answer here",
  "sources": ["Section 1", "Section 2"],
  "confidence": "high/medium/low"
}

Return ONLY the JSON object, no other text."""

    def answer_question(
        self,
        question: str,
        max_chunks: int = 5
    ) -> Dict:
        """
        Answer a question using RAG

        Args:
            question: User's question
            max_chunks: Maximum context chunks to retrieve

        Returns:
            Dict with answer, sources, images, and metadata
        """
        print(f"🤔 Question: {question}")

        # 1. Retrieve relevant chunks from Supabase
        print("🔍 Searching for relevant content...")
        relevant_chunks = self.supabase.search_similar_chunks(
            query=question,
            limit=max_chunks
        )

        if not relevant_chunks:
            return {
                'answer': "I don't have any information to answer that question. Please make sure documents have been uploaded and processed.",
                'sources': [],
                'images': [],
                'confidence': 'low',
                'chunks_used': 0
            }

        print(f"📚 Found {len(relevant_chunks)} relevant chunks")

        # 2. Build context from chunks
        context = self._build_context(relevant_chunks)

        # 3. Get answer from Gemini
        print("🤖 Generating answer...")

        prompt = f"""{self.system_prompt}

Question: {question}

Context:
{context}

Provide your answer as a JSON object."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Extract JSON from response
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].split('```')[0].strip()

            # Parse JSON response
            result_data = json.loads(response_text)

        except Exception as e:
            print(f"⚠️ Error parsing response: {e}")
            # Fallback to plain text response
            try:
                response = self.model.generate_content(
                    f"Answer this question based on the context:\n\nQuestion: {question}\n\nContext:\n{context}"
                )
                result_data = {
                    'answer': response.text,
                    'sources': [chunk.get('heading', 'Unknown') for chunk in relevant_chunks],
                    'confidence': 'medium'
                }
            except Exception as e2:
                return {
                    'answer': f"Error generating answer: {str(e2)}",
                    'sources': [],
                    'images': [],
                    'confidence': 'low',
                    'chunks_used': 0
                }

        # 4. Collect images from relevant chunks
        all_images = []
        for chunk in relevant_chunks:
            if chunk.get('images'):
                all_images.extend(chunk['images'][:2])  # Max 2 images per chunk

        # 5. Prepare response
        response = {
            'answer': result_data.get('answer', 'No answer generated'),
            'sources': result_data.get('sources', []),
            'images': all_images[:5],  # Max 5 images total
            'confidence': result_data.get('confidence', 'medium'),
            'chunks_used': len(relevant_chunks)
        }

        print(f"✅ Answer generated (confidence: {response['confidence']})")

        return response

    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []

        for idx, chunk in enumerate(chunks, 1):
            heading = chunk.get('heading', 'Untitled Section')
            text = chunk.get('text', '')
            filename = chunk.get('filename', 'Unknown')

            context_part = f"""
--- Context {idx} (from {filename}) ---
Section: {heading}
Content: {text}
"""
            context_parts.append(context_part)

        return "\n".join(context_parts)


# Convenience function for direct usage
def ask_question(question: str) -> Dict:
    """
    Ask a question and get an answer

    Args:
        question: User's question

    Returns:
        Dict with answer and metadata
    """
    agent = QAAgent()
    return agent.answer_question(question)
