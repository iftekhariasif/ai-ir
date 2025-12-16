# Quick Start Guide

## Setup Checklist

### ✅ 1. Environment Configured
Your `.env` file is already set up with:
- Supabase URL
- Supabase Key
- Gemini API Key

### ⏳ 2. Install Dependencies (Running...)
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 📊 3. Set Up Supabase Database

**IMPORTANT: You must do this step!**

1. Open your Supabase dashboard: https://whsmmliwtyjjgroxhjhg.supabase.co
2. Click **SQL Editor** in left sidebar
3. Click **+ New Query**
4. Copy ALL contents from `supabase_schema.sql`
5. Paste into SQL editor
6. Click **Run** button

This creates:
- `documents` table
- `document_chunks` table (with vector embeddings)
- `document_images` table
- `match_document_chunks()` search function

###  4. Run the App

```bash
source venv/bin/activate
streamlit run app.py
```

App opens at: http://localhost:8501

---

## First Steps

### Upload a PDF (Admin Tab)

1. Click **⚙️ Admin** tab
2. Upload a company PDF
3. Click **🔄 Convert to Markdown & Store**
4. Wait for processing (~30-60 seconds)
5. See extracted chunks and images

### Ask Questions (User Tab)

1. Click **👤 User Chat** tab
2. Type a question like:
   - "What are the company's main goals?"
   - "What climate risks are mentioned?"
   - "Summarize the financial performance"
3. Get answer with:
   - AI-generated response
   - Relevant sections cited
   - Charts/diagrams displayed

---

## Troubleshooting

### Dependencies not installing?

The current installation process might take 5-10 minutes due to dependency resolution. If it fails:

```bash
# Try installing core packages first
venv/bin/pip install streamlit google-generativeai
venv/bin/pip install supabase openai
venv/bin/pip install pydantic-ai
```

### Supabase error: "function match_document_chunks does not exist"

You forgot to run the SQL schema! Go to step 3 above.

### Gemini API error?

Check your API key is correct in `.env` file. Get a key from: https://ai.google.dev

### No answer from chatbot?

Make sure you've uploaded at least one PDF in the Admin tab first.

---

## Architecture Overview

```
┌─────────────┐
│  Admin Tab  │  Upload PDF
└──────┬──────┘
       │
       ▼
  ┌─────────┐
  │ Docling │  Extract text + images
  └────┬────┘
       │
       ▼
  ┌─────────┐
  │  Gemini │  Generate embeddings
  └────┬────┘
       │
       ▼
  ┌──────────┐
  │ Supabase │  Store everything
  └──────────┘
       ▲
       │
  ┌────┴──────┐
  │  Search   │  Vector similarity
  └────┬──────┘
       │
       ▼
  ┌─────────────┐
  │ Pydantic AI │  Generate answer
  └──────┬──────┘
         │
         ▼
   ┌──────────┐
   │ User Tab │  Display answer + charts
   └──────────┘
```

---

## What You Built

- ✅ PDF upload system
- ✅ Text extraction with Docling
- ✅ Image/chart extraction
- ✅ Vector embeddings with Gemini
- ✅ Supabase storage with pgvector
- ✅ RAG pipeline for Q&A
- ✅ Pydantic AI agent
- ✅ Visual context in answers
- ✅ Streamlit interface

---

## Next Steps

1. ⏳ **Wait for pip install to complete**
2. 📊 **Run SQL schema in Supabase** (CRITICAL!)
3. ▶️ **Run the app**: `streamlit run app.py`
4. 📄 **Upload your first PDF**
5. 💬 **Ask questions and test!**

---

Good luck! 🚀
