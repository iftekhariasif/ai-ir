"""
Supabase utilities for document storage and retrieval
Handles embeddings, text chunks, and images
"""

import os
from supabase import create_client, Client
from typing import List, Dict, Optional
import google.generativeai as genai
from pathlib import Path
import base64
import hashlib

def get_secret(key: str) -> str:
    """Get secret from Streamlit secrets or environment variable"""
    try:
        import streamlit as st
        return st.secrets.get(key)
    except:
        return os.getenv(key)

class SupabaseManager:
    """Manages Supabase operations for document storage and retrieval"""

    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = get_secret('SUPABASE_URL')
        supabase_key = get_secret('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file or Streamlit secrets")

        self.client: Client = create_client(supabase_url, supabase_key)

        # Configure Gemini for embeddings
        gemini_api_key = get_secret('GEMINI_API_KEY')
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text using Gemini"""
        try:
            # Use Gemini's embedding model
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def store_document(
        self,
        filename: str,
        full_text: str,
        chunks: List[Dict[str, str]],
        images: List[Dict[str, str]]
    ) -> Dict:
        """
        Store document with chunks and images in Supabase

        Args:
            filename: Name of the PDF file
            full_text: Complete extracted text
            chunks: List of text chunks with metadata
            images: List of images with base64 data and metadata

        Returns:
            Dict with document_id and stats
        """
        try:
            # Generate document hash
            doc_hash = hashlib.md5(filename.encode()).hexdigest()

            # 1. Store main document record
            doc_data = {
                'filename': filename,
                'doc_hash': doc_hash,
                'full_text': full_text,
                'chunk_count': len(chunks),
                'image_count': len(images)
            }

            doc_result = self.client.table('documents').upsert(
                doc_data,
                on_conflict='doc_hash'
            ).execute()

            doc_id = doc_result.data[0]['id'] if doc_result.data else None

            if not doc_id:
                raise Exception("Failed to create document record")

            # 2. Store text chunks with embeddings
            stored_chunks = 0
            for idx, chunk in enumerate(chunks):
                # Generate embedding for chunk
                embedding = self.generate_embedding(chunk['text'])

                chunk_data = {
                    'document_id': doc_id,
                    'chunk_index': idx,
                    'text': chunk['text'],
                    'heading': chunk.get('heading', ''),
                    'embedding': embedding
                }

                self.client.table('document_chunks').insert(chunk_data).execute()
                stored_chunks += 1

            # 3. Store images
            stored_images = 0
            for idx, image in enumerate(images):
                image_data = {
                    'document_id': doc_id,
                    'image_index': idx,
                    'filename': image['filename'],
                    'image_data': image['base64_data'],
                    'caption': image.get('caption', ''),
                    'context': image.get('context', '')  # Surrounding text
                }

                self.client.table('document_images').insert(image_data).execute()
                stored_images += 1

            return {
                'document_id': doc_id,
                'filename': filename,
                'chunks_stored': stored_chunks,
                'images_stored': stored_images
            }

        except Exception as e:
            print(f"Error storing document: {e}")
            raise

    def search_similar_chunks(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Search for similar text chunks using vector similarity

        Args:
            query: User's question
            limit: Max number of results
            threshold: Similarity threshold (0-1)

        Returns:
            List of matching chunks with metadata and images
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)

            # Search using pgvector similarity
            # Note: This requires RPC function in Supabase
            result = self.client.rpc(
                'match_document_chunks',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()

            # Enhance results with images
            enhanced_results = []
            for chunk in result.data:
                # Get associated images for this document
                images = self.get_document_images(chunk['document_id'])

                enhanced_results.append({
                    'text': chunk['text'],
                    'heading': chunk['heading'],
                    'similarity': chunk['similarity'],
                    'document_id': chunk['document_id'],
                    'filename': chunk['filename'],
                    'images': images
                })

            return enhanced_results

        except Exception as e:
            print(f"Error searching chunks: {e}")
            return []

    def get_document_images(self, document_id: int) -> List[Dict]:
        """Get all images for a document"""
        try:
            result = self.client.table('document_images').select('*').eq(
                'document_id', document_id
            ).execute()

            return result.data if result.data else []

        except Exception as e:
            print(f"Error fetching images: {e}")
            return []

    def list_documents(self) -> List[Dict]:
        """List all stored documents"""
        try:
            result = self.client.table('documents').select(
                'id, filename, chunk_count, image_count, created_at'
            ).order('created_at', desc=True).execute()

            return result.data if result.data else []

        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

    def delete_document(self, document_id: int) -> bool:
        """Delete a document and all associated chunks/images"""
        try:
            # Delete chunks
            self.client.table('document_chunks').delete().eq(
                'document_id', document_id
            ).execute()

            # Delete images
            self.client.table('document_images').delete().eq(
                'document_id', document_id
            ).execute()

            # Delete document
            self.client.table('documents').delete().eq(
                'id', document_id
            ).execute()

            return True

        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
