# 🚀 Launch Instructions

Quick guide to run the Company Q&A Chatbot application.

---

## Prerequisites

- Python 3.12+
- Supabase account
- Gemini API key

---

## 1. Environment Setup

### Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

---

## 2. Configure Environment Variables

Create/update `.env` file:

```bash
# Supabase
SUPABASE_URL=https://whsmmliwtyjjgroxhjhg.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash-exp

# AI Provider
AI_PROVIDER=gemini
```

---

## 3. Database Setup (First Time Only)

1. Go to: https://whsmmliwtyjjgroxhjhg.supabase.co
2. Click **SQL Editor** → **+ New Query**
3. Copy entire contents from `supabase_schema.sql`
4. Paste and click **RUN**

---

## 4. Launch Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the app
streamlit run app.py
```

The app will open at: **http://localhost:8501**

---

## 5. Using the Application

### Admin (Upload & Process)

1. Click **⚙️ Admin** in sidebar
2. Click **📤 Upload File**
3. Select PDF and click **Upload**
4. Click **🔄 Process** to convert to markdown
5. File status changes to ✅ Processed

### User (Ask Questions)

1. Click **👤 User Chat** in sidebar
2. Type your question in the chat box
3. Get AI-generated answers with relevant charts
4. Images appear inline with the answer

---

## Troubleshooting

### Port Already in Use

```bash
# Kill existing streamlit process
pkill -f streamlit

# Or use a different port
streamlit run app.py --server.port 8502
```

### Virtual Environment Not Found

```bash
# Recreate venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Tables Not Found

- Make sure you ran `supabase_schema.sql` in Supabase SQL Editor
- Check that all tables exist: `documents`, `document_chunks`, `document_images`

### Gemini API Error

- Verify `GEMINI_API_KEY` in `.env` file
- Get API key from: https://ai.google.dev

---

## Quick Commands Reference

```bash
# Activate environment
source venv/bin/activate

# Run app
streamlit run app.py

# Run in background
nohup streamlit run app.py &

# Check running processes
ps aux | grep streamlit

# Stop app
pkill -f streamlit

# View logs
tail -f nohup.out
```

---

## Deployment (Optional)

### Local Network Access

The app automatically runs on your network:
- Local: http://localhost:8501
- Network: http://192.168.x.x:8501 (shown in terminal)

### Cloud Deployment

See `CHATBOT_README.md` for Google Cloud Run deployment instructions.

---

## File Structure

```
├── app.py                    # Main Streamlit app
├── document_processor.py     # PDF extraction
├── supabase_utils.py         # Database operations
├── qa_agent.py               # Q&A with Gemini
├── supabase_schema.sql       # Database schema
├── requirements.txt          # Dependencies
├── .env                      # Environment variables
└── temp/uploads/             # Uploaded PDFs (auto-created)
```

---

## Support

- **Setup Issues:** Check `CHATBOT_README.md`
- **Quick Start:** See `QUICKSTART.md`
- **Database Schema:** View `supabase_schema.sql`

---

## That's It! 🎉

Your chatbot should now be running. Upload PDFs in Admin tab and start asking questions in User tab!
