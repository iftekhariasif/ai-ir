# TNFD LEAP Analysis - Usage Guide

## 🎯 Simplified Architecture

The project has been restructured with `main.py` as the single entry point:

```
pdf-extract/
├── main.py              # ⭐ SINGLE ENTRY POINT (everything in one file)
├── client/              # Frontend
│   └── index.html       # PDF & Markdown viewer
├── api/                 # Backend API modules
│   ├── analyze.py       # PDF to text conversion
│   └── leap.py          # LEAP categorization
├── input/               # Put PDFs here
└── output/              # Generated markdown and images
```

## 🚀 Quick Start

### 1. Start the Server

```bash
source venv/bin/activate
python main.py
```

The server will start on http://localhost:5555

### 2. Use the Web Interface

1. **Open browser**: http://localhost:5555
2. **Select PDF**: Choose from dropdown (files in `input/` folder)
3. **Analyze**: Click "🔬 Analyze PDF" button
   - Converts PDF to markdown
   - Extracts images
   - Saves to `output/` folder
4. **Compare**: View PDF and markdown side-by-side automatically
5. **LEAP Mode** (optional):
   - Toggle "LEAP Analysis Mode" ON
   - Generates L.md, E.md, A.md, P.md files
   - Select phase from dropdown to view

## 📡 API Endpoints

### POST /api/analyze
Convert PDF to text/markdown only (no LEAP categorization)

**Request:**
```json
{
  "pdf_path": "input/document.pdf"
}
```

**Response:**
```json
{
  "success": true,
  "pdf_name": "document",
  "markdown_path": "output/document_full_text.md",
  "markdown_name": "document_full_text.md",
  "image_count": 5,
  "images_folder": "output/document_images"
}
```

### POST /api/leap
Generate LEAP framework categorization

**Request:**
```json
{
  "markdown_path": "output/document_full_text.md",
  "pdf_name": "document"
}
```

**Response:**
```json
{
  "success": true,
  "pdf_name": "document",
  "leap_files": {
    "L": "output/document_L.md",
    "E": "output/document_E.md",
    "A": "output/document_A.md",
    "P": "output/document_P.md"
  },
  "phases": ["L", "E", "A", "P"]
}
```

## 🔄 How It Works

### Analysis Workflow:
1. **User selects PDF** → Frontend calls `/api/analyze`
2. **main.py** → Processes request directly
3. **main.py** → `process_pdf_to_markdown()` with `enable_leap=False`
4. **Result** → Returns markdown + images paths

### LEAP Workflow:
1. **User toggles LEAP ON** → Frontend calls `/api/leap`
2. **main.py** → Handles request directly
3. **main.py** → `categorize_leap_content()` function
4. **Result** → Returns L.md, E.md, A.md, P.md paths

## 🎨 Frontend Features

- **Side-by-side viewing**: PDF on left, markdown on right
- **Auto-population**: Dropdowns auto-fill from folders
- **Analyze workflow**: One-click PDF processing
- **LEAP toggle**: Enable/disable LEAP categorization
- **Phase selection**: View specific LEAP phases
- **Streamlit-inspired design**: Clean, modern UI

## 📝 Core Functions (main.py)

### `process_pdf_to_markdown(pdf_path, output_folder, pdf_name, enable_leap=True)`
Core processing function that:
- Extracts text and images from PDF
- Generates markdown with embedded images
- Optionally creates LEAP categorized files

### `categorize_leap_content(full_text, output_folder, pdf_name, image_count)`
LEAP categorization function that:
- Analyzes content using keyword matching
- Generates separate files for L, E, A, P phases
- Returns paths to categorized files

## 🔧 Configuration

No configuration needed! Just:
1. Put PDFs in `input/` folder
2. Run `python main.py`
3. Open http://localhost:5555

## ✨ Key Benefits

- ✅ **Single entry point** - Everything in main.py
- ✅ **No separate server file** - All in one place
- ✅ **Clear workflow** - Analyze → LEAP categorization
- ✅ **Frontend-focused** - Browser-based interface
- ✅ **Simple structure** - Easy to understand and maintain
- ✅ **API built-in** - Flask server integrated directly

## 📦 Old API (api/pdf_to_markdown.py)

The old `api/pdf_to_markdown.py` with Google Drive integration is still available for n8n workflows but is separate from the main web interface workflow.

For n8n integration, start it separately:
```bash
MODE=prod python main.py
```

Or run the FastAPI directly:
```bash
cd api
python pdf_to_markdown.py
```
