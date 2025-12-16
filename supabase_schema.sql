-- Supabase Database Schema for Company Q&A Chatbot
-- Run this SQL in your Supabase SQL Editor

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- ========================================
-- Table: documents
-- Stores main document metadata
-- ========================================
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    doc_hash TEXT UNIQUE NOT NULL,
    full_text TEXT,
    chunk_count INTEGER DEFAULT 0,
    image_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Index for faster lookups
CREATE INDEX idx_documents_filename ON documents(filename);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);


-- ========================================
-- Table: document_chunks
-- Stores text chunks with embeddings
-- ========================================
CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    heading TEXT,
    embedding VECTOR(768),  -- Gemini text-embedding-004 produces 768-dim vectors
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Indexes for faster queries
CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);


-- ========================================
-- Table: document_images
-- Stores extracted images
-- ========================================
CREATE TABLE document_images (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES documents(id) ON DELETE CASCADE,
    image_index INTEGER NOT NULL,
    filename TEXT NOT NULL,
    image_data TEXT,  -- Base64 encoded image
    caption TEXT,
    context TEXT,  -- Surrounding text for context
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Index for faster lookups
CREATE INDEX idx_images_document_id ON document_images(document_id);


-- ========================================
-- Function: match_document_chunks
-- Vector similarity search for RAG
-- ========================================
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    document_id BIGINT,
    chunk_index INTEGER,
    text TEXT,
    heading TEXT,
    filename TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.text,
        dc.heading,
        d.filename,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;


-- ========================================
-- Enable Row Level Security (Optional)
-- Uncomment if you want to add RLS
-- ========================================
-- ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE document_images ENABLE ROW LEVEL SECURITY;

-- Example policy (allow all operations for authenticated users)
-- CREATE POLICY "Allow all for authenticated users" ON documents
--     FOR ALL USING (auth.role() = 'authenticated');


-- ========================================
-- Grant permissions
-- ========================================
GRANT ALL ON documents TO anon, authenticated;
GRANT ALL ON document_chunks TO anon, authenticated;
GRANT ALL ON document_images TO anon, authenticated;
GRANT USAGE ON SEQUENCE documents_id_seq TO anon, authenticated;
GRANT USAGE ON SEQUENCE document_chunks_id_seq TO anon, authenticated;
GRANT USAGE ON SEQUENCE document_images_id_seq TO anon, authenticated;


-- ========================================
-- Sample queries for testing
-- ========================================

-- Count total documents
-- SELECT COUNT(*) FROM documents;

-- View all documents
-- SELECT id, filename, chunk_count, image_count, created_at FROM documents ORDER BY created_at DESC;

-- View chunks for a specific document
-- SELECT chunk_index, heading, LEFT(text, 100) as preview FROM document_chunks WHERE document_id = 1;

-- Test vector search (replace [...] with actual embedding vector)
-- SELECT * FROM match_document_chunks('[0.1, 0.2, ...]'::VECTOR(768), 0.7, 5);
