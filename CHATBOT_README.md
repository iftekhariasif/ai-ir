# Company Q&A Chatbot

AI-powered chatbot that answers questions about company documents using RAG (Retrieval Augmented Generation) with visual context.

## Features

✅ PDF upload and automatic processing
✅ Text extraction and chunking with Docling
✅ Image/chart/diagram extraction
✅ Vector embeddings with Gemini
✅ Semantic search with Supabase pgvector
✅ Q&A with Pydantic AI
✅ Visual context (shows relevant charts with answers)
✅ Two-tab interface (Admin + User)

---

## Architecture

```
User uploads PDF (Admin tab)
    ↓
Docling extracts text + images
    ↓
Text chunked by sections
    ↓
Gemini generates embeddings
    ↓
Stored in Supabase (text + vectors + images)
    ↓
User asks question (User tab)
    ↓
Query embedded → Vector search
    ↓
Pydantic AI generates answer with context
    ↓
Display answer + relevant charts
```

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor
3. Run the schema from `supabase_schema.sql`
4. Copy your project URL and anon key

### 3. Configure Environment Variables

Create `.env` file:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash

# Optional (if using OpenAI instead of Gemini)
OPENAI_API_KEY=your-openai-key
```

### 4. Run the App

```bash
streamlit run app.py
```

App will open at: `http://localhost:8501`

---

## Usage

### Admin Tab (Upload PDFs)

1. Click **⚙️ Admin** tab
2. Upload a PDF file
3. Click **🔄 Convert to Markdown & Store**
4. Wait for processing (extracts text, images, generates embeddings)
5. View processing details in the expander

### User Tab (Ask Questions)

1. Click **👤 User Chat** tab
2. Type a question in the chat input
3. AI searches for relevant content
4. Answer displayed with:
   - Generated response
   - Confidence level
   - Source sections
   - Relevant charts/diagrams

---

## File Structure

```
app.py                  # Main Streamlit app
document_processor.py   # PDF extraction with Docling
supabase_utils.py       # Supabase storage & retrieval
qa_agent.py             # Pydantic AI Q&A agent
supabase_schema.sql     # Database schema
requirements.txt        # Python dependencies
.env                    # Environment variables (create this)
```

---

## How It Works

### Document Processing

1. **Extract**: Docling extracts text and images from PDF
2. **Chunk**: Text split into sections by headings (~1000 chars each)
3. **Embed**: Gemini generates 768-dim vectors for each chunk
4. **Store**: Text, embeddings, and images saved to Supabase

### Question Answering

1. **Embed Query**: User question → embedding vector
2. **Search**: Cosine similarity search in Supabase pgvector
3. **Retrieve**: Top 5 most similar chunks + associated images
4. **Generate**: Pydantic AI generates answer from context
5. **Display**: Answer + relevant visuals shown to user

### RAG Pipeline

```python
# Simplified flow
question = "What are the climate risks?"
    ↓
embedding = generate_embedding(question)
    ↓
chunks = search_similar_chunks(embedding, limit=5)
    ↓
context = build_context(chunks)
    ↓
answer = pydantic_ai.run(question, context)
    ↓
display(answer, chunks.images)
```

---

## Supabase Tables

### `documents`
- Stores document metadata
- Fields: `id`, `filename`, `full_text`, `chunk_count`, `image_count`

### `document_chunks`
- Stores text chunks with embeddings
- Fields: `id`, `document_id`, `text`, `heading`, `embedding` (vector)

### `document_images`
- Stores extracted images
- Fields: `id`, `document_id`, `image_data` (base64), `caption`, `context`

### Vector Search Function

```sql
match_document_chunks(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
```

Returns most similar chunks using cosine similarity.

---

## Configuration

### Sidebar Status

The sidebar shows API key status:

- ✅ Supabase URL
- ✅ Supabase Key
- ✅ Gemini API

If any are missing, update `.env` file.

### Clear Chat History

Click **🗑️ Clear Chat History** in sidebar to reset conversation.

---

## Troubleshooting

### Error: "SUPABASE_URL and SUPABASE_KEY must be set"

- Check `.env` file exists
- Verify keys are correct
- Restart Streamlit app

### Error: "GEMINI_API_KEY not found"

- Add `GEMINI_API_KEY` to `.env`
- Get API key from [ai.google.dev](https://ai.google.dev)

### Error: Vector search not working

- Ensure `pgvector` extension is enabled in Supabase
- Run `supabase_schema.sql` in SQL Editor
- Check `match_document_chunks` function exists

### Images not displaying

- Check image extraction in processing details
- Verify base64 encoding is valid
- Images stored in `document_images` table

### Slow search performance

- Reduce `max_chunks` in `qa_agent.py`
- Increase `match_threshold` to filter more results
- Add more indexes to Supabase tables

---

## API Reference

### DocumentProcessor

```python
from document_processor import process_and_prepare

result = process_and_prepare(
    pdf_path="document.pdf",
    filename="document.pdf"
)
# Returns: {filename, full_text, chunks, images}
```

### SupabaseManager

```python
from supabase_utils import SupabaseManager

db = SupabaseManager()

# Store document
db.store_document(filename, full_text, chunks, images)

# Search
results = db.search_similar_chunks(query="climate risks", limit=5)

# List documents
docs = db.list_documents()
```

### QAAgent

```python
from qa_agent import QAAgent

agent = QAAgent()
result = agent.answer_question("What are the company's goals?")
# Returns: {answer, sources, images, confidence}
```

---

## Advanced Configuration

### Change Embedding Model

Update in `.env`:

```bash
GEMINI_MODEL=gemini-2.5-flash
```

Or use OpenAI embeddings by modifying `supabase_utils.py`.

### Adjust Chunk Size

Edit `document_processor.py`:

```python
chunks = self._create_chunks(full_text, chunk_size=1500)
```

### Customize System Prompt

Edit `qa_agent.py`:

```python
system_prompt="""Your custom instructions here..."""
```

---

## Cost Estimation

**Per PDF (avg 50 pages):**
- Gemini embeddings: ~$0.00001/embedding × 50 chunks = ~$0.0005
- Gemini chat: ~$0.001/query
- Supabase: Free tier (500MB storage, 2GB bandwidth)

**Monthly (100 PDFs, 1000 queries):**
- Processing: ~$0.05
- Queries: ~$1.00
- Supabase: Free tier sufficient

Total: **~$1/month** for moderate usage

---

## Future Improvements

- [ ] Multi-file upload
- [ ] Document management (delete, re-process)
- [ ] Chat history persistence
- [ ] Export answers to PDF
- [ ] Support for other file types (DOCX, PPT)
- [ ] Multi-language support
- [ ] User authentication
- [ ] Answer caching
- [ ] Conversation memory

---

## License

MIT

---

## Support

For issues or questions:
1. Check Troubleshooting section
2. Review Supabase logs
3. Check Streamlit terminal output for errors
