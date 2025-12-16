# Database Commands

SQL commands to view and query data in Supabase.

---

## View All Documents

```sql
-- List all uploaded documents
SELECT
    id,
    filename,
    upload_date,
    chunk_count,
    image_count
FROM documents
ORDER BY upload_date DESC;
```

---

## View Document Details

```sql
-- Get full details of a specific document
SELECT *
FROM documents
WHERE filename = 'your-file-name.pdf';

-- Or by ID
SELECT *
FROM documents
WHERE id = 1;
```

---

## View Document Chunks

```sql
-- View all chunks for a document
SELECT
    id,
    document_id,
    chunk_index,
    heading,
    LEFT(text, 100) as text_preview,
    LENGTH(text) as text_length
FROM document_chunks
WHERE document_id = 1
ORDER BY chunk_index;

-- View specific chunk with full text
SELECT *
FROM document_chunks
WHERE id = 123;

-- Count chunks per document
SELECT
    d.filename,
    COUNT(c.id) as chunk_count
FROM documents d
LEFT JOIN document_chunks c ON d.id = c.document_id
GROUP BY d.id, d.filename
ORDER BY chunk_count DESC;
```

---

## View Document Images

```sql
-- List all images for a document
SELECT
    id,
    document_id,
    chunk_id,
    image_index,
    image_format,
    LENGTH(image_data) as image_size_bytes
FROM document_images
WHERE document_id = 1
ORDER BY image_index;

-- Count images per document
SELECT
    d.filename,
    COUNT(i.id) as image_count
FROM documents d
LEFT JOIN document_images i ON d.id = i.document_id
GROUP BY d.id, d.filename
ORDER BY image_count DESC;

-- View images for a specific chunk
SELECT *
FROM document_images
WHERE chunk_id = 123;
```

---

## Search Queries

```sql
-- Search chunks by heading
SELECT
    d.filename,
    c.heading,
    LEFT(c.text, 200) as preview
FROM document_chunks c
JOIN documents d ON c.document_id = d.id
WHERE c.heading ILIKE '%financial%'
ORDER BY d.filename, c.chunk_index;

-- Search chunks by text content
SELECT
    d.filename,
    c.heading,
    c.text
FROM document_chunks c
JOIN documents d ON c.document_id = d.id
WHERE c.text ILIKE '%climate%'
LIMIT 10;

-- Find chunks with images
SELECT
    c.id,
    c.heading,
    COUNT(i.id) as image_count
FROM document_chunks c
LEFT JOIN document_images i ON c.id = i.chunk_id
GROUP BY c.id, c.heading
HAVING COUNT(i.id) > 0
ORDER BY image_count DESC;
```

---

## Statistics

```sql
-- Overall database statistics
SELECT
    (SELECT COUNT(*) FROM documents) as total_documents,
    (SELECT COUNT(*) FROM document_chunks) as total_chunks,
    (SELECT COUNT(*) FROM document_images) as total_images;

-- Average chunks and images per document
SELECT
    AVG(chunk_count) as avg_chunks_per_doc,
    AVG(image_count) as avg_images_per_doc
FROM documents;

-- Document processing summary
SELECT
    filename,
    chunk_count,
    image_count,
    upload_date,
    ROUND(chunk_count::numeric / NULLIF(image_count, 0), 2) as chunks_per_image
FROM documents
ORDER BY upload_date DESC;
```

---

## Vector Search

```sql
-- Test vector search function
-- (Replace the embedding array with actual values from your code)
SELECT
    d.filename,
    c.heading,
    c.similarity
FROM match_document_chunks(
    query_embedding := '[0.1, 0.2, ...]'::vector(768),
    match_threshold := 0.5,
    match_count := 5
) c
JOIN documents d ON c.document_id = d.id;

-- Check if vector extension is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- View embedding dimensions
SELECT
    id,
    heading,
    array_length(embedding::float[], 1) as embedding_dimension
FROM document_chunks
LIMIT 5;
```

---

## Maintenance Queries

```sql
-- Delete a specific document and all related data
DELETE FROM documents WHERE id = 1;
-- (Cascades to chunks and images automatically)

-- Delete all data (⚠️ USE WITH CAUTION)
TRUNCATE documents CASCADE;

-- Find orphaned chunks (shouldn't exist with proper foreign keys)
SELECT c.*
FROM document_chunks c
LEFT JOIN documents d ON c.document_id = d.id
WHERE d.id IS NULL;

-- Find orphaned images
SELECT i.*
FROM document_images i
LEFT JOIN documents d ON i.document_id = d.id
WHERE d.id IS NULL;
```

---

## Recent Activity

```sql
-- Recently uploaded documents
SELECT
    filename,
    upload_date,
    chunk_count,
    image_count
FROM documents
ORDER BY upload_date DESC
LIMIT 10;

-- Latest processed chunks
SELECT
    d.filename,
    c.heading,
    c.chunk_index
FROM document_chunks c
JOIN documents d ON c.document_id = d.id
ORDER BY c.id DESC
LIMIT 20;
```

---

## How to Run These Queries

### In Supabase Dashboard:

1. Go to: https://whsmmliwtyjjgroxhjhg.supabase.co
2. Click **SQL Editor** in left sidebar
3. Click **+ New Query**
4. Paste any query above
5. Click **Run** or press `Cmd/Ctrl + Enter`

### Using Supabase CLI:

```bash
# Install Supabase CLI
npm install -g supabase

# Link to your project
supabase link --project-ref whsmmliwtyjjgroxhjhg

# Run query
supabase db query "SELECT * FROM documents"
```

---

## Useful Filters

```sql
-- Documents uploaded today
SELECT * FROM documents
WHERE upload_date::date = CURRENT_DATE;

-- Documents uploaded in last 7 days
SELECT * FROM documents
WHERE upload_date > NOW() - INTERVAL '7 days'
ORDER BY upload_date DESC;

-- Large documents (many chunks)
SELECT * FROM documents
WHERE chunk_count > 100
ORDER BY chunk_count DESC;

-- Documents with many images
SELECT * FROM documents
WHERE image_count > 50
ORDER BY image_count DESC;
```

---

## Export Data

```sql
-- Export document list as JSON
SELECT json_agg(row_to_json(documents))
FROM documents;

-- Export chunks for a document as JSON
SELECT json_agg(row_to_json(document_chunks))
FROM document_chunks
WHERE document_id = 1;
```

---

## Performance Monitoring

```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

---

## Quick Reference

| Table | Purpose |
|-------|---------|
| `documents` | Stores document metadata (filename, dates, counts) |
| `document_chunks` | Text chunks with embeddings for vector search |
| `document_images` | Extracted images/charts in base64 format |

| Function | Purpose |
|----------|---------|
| `match_document_chunks()` | Vector similarity search for RAG retrieval |
