# Product Requirements Document (PRD)

## IR AI - Intelligent Report Analysis & Q&A Chatbot

**Version:** 1.0
**Date:** December 17, 2025
**Author:** Product Team
**Status:** Active Development

---

## 1. Executive Summary

IR AI is an intelligent corporate report analysis platform designed for investor relations and sustainability reporting. The system creates a comprehensive PDF database of corporate reports including TCFD, TNFD, Sustainability Reports, Sustainability Data Books, and Integrated Reports. Business teams can search by company name, specific questions, or keywords to extract relevant information including text, charts, and flow diagrams. The system uses RAG (Retrieval Augmented Generation) technology with vector embeddings to provide accurate, context-aware answers.

### Vision

Build a complete IR analysis ecosystem that enables:
1. **Single Company Analysis** - Search and analyze individual company reports with visual context
2. **Multi-Company Comparison** - Compare multiple companies side-by-side in unified interface
3. **IR Writing Assistant** - Directly fetch information into writing blocks for simultaneous search and content creation

### Key Value Propositions

- **Corporate Report Specialization:** Purpose-built for TCFD, TNFD, sustainability, and integrated reports
- **Visual Intelligence:** Automatic extraction and display of charts, diagrams, and tables
- **Instant Insights:** Get answers from lengthy reports in seconds
- **Multi-Company Comparison:** Analyze and compare multiple companies simultaneously
- **Writing Integration:** Search and write in the same workflow
- **Accurate Responses:** RAG-based system ensures answers are grounded in source documents
- **Multi-Provider AI:** Flexible AI backend supporting Gemini, Claude, and Perplexity
- **Domain Expert Control:** Real-time instruction file editing for continuous improvement

---

## 2. Product Goals & Objectives

### Development Philosophy

Our approach follows four core principles:

1. **"Do It Anyway"** - Build the entire system with minimum viable efficiency first, then iterate
2. **"Love The Unknown"** - Enable domain experts (business solutions team) to edit instruction files in real-time
3. **"For Others"** - Provide intuitive input methods that serve business team needs
4. **"Towards Inspiration"** - Continuously improve system efficiency daily through iterative enhancements

### Primary Goals

1. **Create Comprehensive Corporate Report Database**
   - Support TCFD, TNFD, Sustainability Reports, Sustainability Data Books, Integrated Reports
   - Enable search by company name, specific questions, or keywords
   - Extract and display text, charts, flow diagrams, and tables

2. **Enable Multi-Company Analysis**
   - Compare multiple companies in unified interface
   - Side-by-side visualization of metrics and disclosures
   - Cross-company trend analysis

3. **Integrate Search with Content Creation**
   - IR Writing Assistant with database-backed content blocks
   - Simultaneous search and writing workflow
   - Source citations automatically embedded

4. **Maintain Answer Accuracy**
   - Ensure all answers are grounded in uploaded documents
   - Provide source citations for transparency
   - Confidence scoring for all responses

5. **Empower Domain Experts**
   - Allow business solutions team to refine system instructions
   - Real-time prompt and filter editing without developer intervention
   - Continuous learning from user feedback

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Query Response Time | < 3 seconds | Average API response time |
| Answer Accuracy | >90% | User feedback rating |
| Document Processing Time | <2 minutes per 100 pages | Processing pipeline timing |
| User Engagement | >5 queries per session | Session analytics |
| Daily Active Users | 100+ users | Authentication logs |

---

## 3. Target Users

### Primary Personas

#### 1. Business Solutions Team Member (Primary User)
- **Role:** Analyzes corporate sustainability and IR reports for client projects
- **Pain Points:** Manual extraction of TCFD/TNFD disclosures, comparing multiple companies, scattered visual data
- **Goals:** Quickly find specific disclosures, compare companies, extract charts for reports
- **Use Cases:**
  - "Find climate risk disclosures for Company A"
  - "Compare Scope 3 emissions for Companies A, B, and C"
  - "Extract governance structure diagrams"
- **Special Needs:** Ability to refine search instructions without developer help

#### 2. IR Analyst
- **Role:** Analyzes investor relations reports for insights
- **Pain Points:** Manual data extraction, scattered information across multiple report types
- **Goals:** Quickly find financial metrics, ESG trends, and disclosures
- **Use Cases:**
  - Compare year-over-year sustainability performance
  - Identify climate-related risks
  - Track TCFD/TNFD adoption progress

#### 3. Investment Researcher (ESG Focus)
- **Role:** Research companies for sustainable investment decisions
- **Pain Points:** Time-consuming analysis of sustainability reports, data books, and integrated reports
- **Goals:** Extract ESG metrics from multiple company reports simultaneously
- **Use Cases:**
  - Portfolio ESG screening
  - Due diligence on sustainability practices
  - Benchmark companies against peers

#### 4. Content Writer / IR Writer
- **Role:** Creates investor relations and sustainability content
- **Pain Points:** Switching between research and writing tools, manual citation management
- **Goals:** Search corporate reports while writing, embed sources automatically
- **Use Cases:**
  - Draft sustainability reports using peer company data
  - Create investor presentations with sourced claims
  - Write analysis reports with embedded charts

#### 5. Domain Expert / System Trainer
- **Role:** Business solutions expert who refines system accuracy
- **Pain Points:** Waiting for developers to adjust search parameters, can't improve system in real-time
- **Goals:** Edit instruction files to improve extraction quality, customize output formatting
- **Use Cases:**
  - Refine how the system identifies TNFD disclosures
  - Adjust chart extraction rules
  - Customize comparison table formats

---

## 4. Core Features

### 4.1 Document Management (Library)

**Feature:** Upload and manage PDF documents

**Requirements:**
- Support PDF uploads up to 100MB
- Display document library with status indicators
- Two-step workflow: Upload → Process
- Delete functionality for unwanted documents

**User Flow:**
1. User clicks "Upload File" button
2. Selects PDF from local system
3. File appears in library with "Pending" status
4. User clicks "Process" to extract and store content
5. Status changes to "Processed" with chunk/image counts

**Technical Requirements:**
- PDF processing via Docling library
- Extract text, headings, images, and tables
- Chunk text into 512-token segments
- Generate 768-dimensional embeddings via Gemini
- Store in Supabase with pgvector

### 4.2 Q&A Chat Interface

**Feature:** Natural language question answering

**Requirements:**
- Chat-like interface similar to ChatGPT
- Real-time streaming responses
- Display relevant images inline with answers
- Show confidence level and sources
- Maintain conversation history

**User Flow:**
1. User types question in chat input
2. System searches vector database for relevant chunks
3. AI generates answer based on retrieved context
4. Answer displays with relevant charts/images inline
5. Sources and confidence shown below answer

**Technical Requirements:**
- Vector similarity search (cosine similarity >0.7)
- Retrieve top 5 most relevant chunks
- Context window: ~8000 tokens
- Response format: JSON with answer, sources, confidence
- Image extraction from associated chunks

### 4.3 Multi-Provider AI Support

**Feature:** Switch between AI providers

**Requirements:**
- Support Gemini (default)
- Support Claude (planned)
- Support Perplexity (planned)
- Single dropdown selector in sidebar

**Current State:**
- ✅ Gemini fully integrated
- ⏳ Claude coming soon
- ⏳ Perplexity coming soon

**Technical Requirements:**
- Provider abstraction layer
- Unified API interface
- Fallback to default provider on error
- Provider-specific configuration

### 4.4 Multi-Company Comparison (Phase 2)

**Feature:** Compare multiple companies side-by-side

**Requirements:**
- Select 2-5 companies for comparison
- Unified comparison interface
- Side-by-side metric visualization
- Synchronized chart viewing
- Export comparison tables

**User Flow:**
1. User selects "Compare Companies" mode
2. Chooses 2-5 companies from library
3. Asks comparative question (e.g., "Compare Scope 3 emissions")
4. System retrieves relevant data from each company
5. Displays side-by-side comparison table
6. Shows charts aligned by metric type
7. Highlights differences and trends

**Technical Requirements:**
- Multi-document vector search
- Result aggregation and alignment
- Comparative visualization components
- Export to Excel/CSV functionality

**Example Comparisons:**
- "Compare carbon reduction targets across Companies A, B, C"
- "Show governance structures for all selected companies"
- "Which companies have TNFD disclosures?"

### 4.5 IR Writing Assistant (Phase 3)

**Feature:** Integrated search and writing environment

**Requirements:**
- Rich text editor with writing blocks
- Inline search results from PDF database
- Drag-and-drop charts into writing blocks
- Automatic source citations
- Export to Word/PDF with formatting

**User Flow:**
1. User opens Writing Assistant
2. Creates new document with writing blocks
3. While writing, uses inline search command (e.g., "/search climate risks")
4. System shows relevant chunks and charts
5. User drags content into writing block
6. Sources automatically cited
7. Continues writing with embedded research
8. Exports final document with citations

**Technical Requirements:**
- Rich text editor (e.g., TipTap, Quill)
- Inline command system
- Citation management
- Document export engine (Markdown → Word/PDF)
- Auto-save functionality

**Example Workflow:**
```
[User types]: "Company A has committed to..."
[User types]: /search Company A carbon targets
[System shows]: Relevant paragraphs + charts
[User drags]: Chart into document
[System adds]: "...net-zero by 2050 (Source: Sustainability Report 2024, p.12)"
```

### 4.6 Domain Expert Control Panel (Phase 2-3)

**Feature:** Real-time instruction file editing for business experts

**Requirements:**
- UI for editing system prompts without code changes
- Template management for different report types
- Custom field extraction rules
- Output format customization
- A/B testing of instructions

**User Flow:**
1. Domain expert opens Control Panel
2. Selects report type (e.g., TCFD)
3. Edits instruction template:
   - "When extracting climate risks, prioritize sections: Risk Management, Strategy"
   - "For charts, ensure you capture: axes labels, legends, data sources"
4. Saves new instruction version
5. Tests with sample document
6. Compares old vs new results
7. Activates new instruction for production

**Technical Requirements:**
- Instruction template storage (Supabase or files)
- Version control for instructions
- A/B testing framework
- Rollback capability
- Analytics on instruction performance

**Supported Report Types:**
- TCFD (Task Force on Climate-related Financial Disclosures)
- TNFD (Taskforce on Nature-related Financial Disclosures)
- Sustainability Reports
- Sustainability Data Books
- Integrated Reports
- Annual Reports (IR sections)

### 4.7 Configuration Management

**Feature:** API key management and status display

**Requirements:**
- Display connection status for Supabase and AI provider
- Support both local .env and cloud secrets
- Warning indicators for missing keys

**Technical Requirements:**
- Read from st.secrets (Streamlit Cloud) or os.getenv (local)
- Graceful fallback handling
- No credential logging

---

## 5. Technical Architecture

### 5.1 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit)                 │
│  ┌──────────────┐              ┌──────────────┐        │
│  │ Chat Page    │              │ Library Page │        │
│  │              │              │              │        │
│  │ - Q&A Input  │              │ - Upload     │        │
│  │ - Chat View  │              │ - Process    │        │
│  │ - Images     │              │ - Delete     │        │
│  └──────────────┘              └──────────────┘        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Application Layer (Python)              │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ qa_agent.py │  │ document_    │  │ supabase_     │ │
│  │             │  │ processor.py │  │ utils.py      │ │
│  │ - RAG Logic │  │              │  │               │ │
│  │ - AI Calls  │  │ - Docling    │  │ - Embeddings  │ │
│  └─────────────┘  └──────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   External Services                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Gemini API   │  │ Supabase     │  │ Claude API   │ │
│  │              │  │              │  │ (Future)     │ │
│  │ - Embeddings │  │ - PostgreSQL │  └──────────────┘ │
│  │ - LLM        │  │ - pgvector   │                   │
│  └──────────────┘  └──────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow

**Document Upload Flow:**
```
PDF Upload → Docling Extraction → Text Chunking →
Embedding Generation → Supabase Storage → Status Update
```

**Q&A Flow:**
```
User Question → Embedding Generation → Vector Search →
Context Retrieval → LLM Generation → Response + Images
```

### 5.3 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Streamlit | UI framework |
| Backend | Python 3.12+ | Application logic |
| Document Processing | Docling | PDF text/image extraction |
| Vector Database | Supabase (pgvector) | Semantic search |
| Embeddings | Gemini text-embedding-004 | 768-dim vectors |
| LLM | Gemini 2.5 Flash | Answer generation |
| Styling | Shadcn-inspired CSS | Modern UI |
| Deployment | Streamlit Cloud | Hosting |

### 5.4 Database Schema

**documents**
- id (bigserial, PK)
- filename (text)
- doc_hash (text, unique)
- full_text (text)
- chunk_count (int)
- image_count (int)
- created_at (timestamp)

**document_chunks**
- id (bigserial, PK)
- document_id (bigint, FK)
- chunk_index (int)
- text (text)
- heading (text)
- embedding (vector(768))
- created_at (timestamp)

**document_images**
- id (bigserial, PK)
- document_id (bigint, FK)
- chunk_id (bigint, FK, nullable)
- image_index (int)
- filename (text)
- image_data (text) -- base64
- caption (text)
- context (text)
- created_at (timestamp)

---

## 6. User Stories

### As an IR Analyst

**Story 1: Upload Annual Report**
- **As** an IR analyst
- **I want to** upload our company's annual report
- **So that** I can quickly answer investor questions

**Acceptance Criteria:**
- Can upload PDF files up to 100MB
- Processing completes in <2 minutes for 100-page report
- All text and images are extracted
- Status indicator shows processing progress

**Story 2: Find Financial Metrics**
- **As** an IR analyst
- **I want to** ask "What was the revenue growth in 2024?"
- **So that** I get an accurate answer with source citation

**Acceptance Criteria:**
- Answer includes specific revenue numbers
- Relevant financial charts are displayed
- Sources cite specific sections/pages
- Confidence level is "high"

### As an Investment Researcher

**Story 3: Compare Company Performance**
- **As** an investment researcher
- **I want to** upload multiple company reports
- **So that** I can compare their performance

**Acceptance Criteria:**
- Can upload multiple documents
- Library shows all uploaded documents
- Can ask comparative questions
- Answers cite which company/document

### As a Manager

**Story 4: Quick Executive Summary**
- **As** a manager with limited time
- **I want to** ask "Summarize the key risks"
- **So that** I get a concise overview

**Acceptance Criteria:**
- Summary is <300 words
- Includes bullet points
- Shows relevant risk diagrams
- Response time < 3 seconds

---

## 7. UI/UX Requirements

### 7.1 Design System

**Design Philosophy:** Shadcn-inspired minimalism

**Color Palette:**
- Primary: `#18181b` (Zinc 900)
- Background: `#ffffff` (White)
- Secondary Background: `#f4f4f5` (Zinc 100)
- Border: `#e4e4e7` (Zinc 200)

**Typography:**
- Font: Sans-serif system fonts
- Headers: 600 weight
- Body: 400 weight

**Components:**
- Buttons: Rounded (6px), bordered, hover effects
- Inputs: Rounded (6px), bordered
- Chat Messages: Rounded (8px), bordered
- Expandable sections for sources

### 7.2 Layout

**Sidebar Navigation:**
- App title: "IR AI"
- AI Provider dropdown
- Navigation buttons: "Chat", "Library"
- Configuration status
- Clear Chat button

**Chat Page:**
- Full-width chat container
- Messages flow top to bottom
- Images inline with answers
- Input fixed at bottom
- Confidence and sources below each answer

**Library Page:**
- Header with "Upload File" button (right-aligned)
- Document table:
  - Columns: Filename, Status, Details, Process, Delete
  - Status indicators: ✅ Processed, ⏳ Pending
  - Chunk/image counts
- Modal for file upload

### 7.3 Responsive Design

- Desktop-first design
- Min width: 1024px recommended
- Mobile: Sidebar collapses
- Tables scroll horizontally on mobile

---

## 8. API Requirements

### 8.1 Gemini API

**Endpoints Used:**
- `text-embedding-004`: Generate embeddings
- `gemini-2.5-flash`: Generate answers

**Rate Limits:**
- 60 requests per minute (embedding)
- 15 requests per minute (generation)

**Error Handling:**
- Retry on 429 (rate limit)
- Fallback message on API errors
- Log all errors

### 8.2 Supabase API

**Operations:**
- Insert documents, chunks, images
- Vector search via `match_document_chunks()` RPC
- List/delete documents
- Fetch images by document_id

**Connection:**
- REST API via Python client
- Connection pooling
- Auto-reconnect on failure

---

## 9. Security & Privacy

### 9.1 Data Security

**Requirements:**
- All API keys stored in secrets (not in code)
- HTTPS for all external communications
- No logging of sensitive data
- SQL injection prevention (parameterized queries)

**Compliance:**
- No PII collection
- Document data stored in user's Supabase instance
- User owns all data

### 9.2 Authentication (Future)

**Planned Features:**
- User login (OAuth)
- Document-level permissions
- Role-based access control (Admin, Viewer)
- Audit logs

---

## 10. Performance Requirements

### 10.1 Response Times

| Operation | Target | Max |
|-----------|--------|-----|
| Page Load | <1s | 2s |
| PDF Upload | <500ms | 1s |
| PDF Processing (100 pages) | <2min | 5min |
| Q&A Response | <3s | 5s |
| Document List Load | <500ms | 1s |

### 10.2 Scalability

**Current Limits:**
- Documents: 1000 per account
- Chunks per document: Unlimited
- Images per document: Unlimited
- Concurrent users: 50 (Streamlit Cloud)

**Future Scaling:**
- Move to Cloud Run for auto-scaling
- Redis cache for frequently asked questions
- CDN for image delivery

---

## 11. Testing Requirements

### 11.1 Unit Tests

**Required Coverage:**
- `supabase_utils.py`: 80%
- `qa_agent.py`: 80%
- `document_processor.py`: 80%

**Key Test Cases:**
- Embedding generation
- Vector search accuracy
- Document chunking logic
- Image extraction

### 11.2 Integration Tests

**Scenarios:**
- End-to-end PDF upload and processing
- Q&A with answer validation
- Multi-document handling
- Error handling (missing API keys, etc.)

### 11.3 User Acceptance Testing (UAT)

**Test Plan:**
1. Upload real company reports
2. Ask 20 common questions
3. Validate answer accuracy (>90%)
4. Check image relevance
5. Performance benchmarking

---

## 12. Deployment

### 12.1 Environments

**Development:**
- Local: `localhost:8501`
- Uses `.env` file
- SQLite for testing (optional)

**Production:**
- Platform: Streamlit Cloud
- URL: `https://ir-ai.streamlit.app` (example)
- Uses `st.secrets`
- Supabase production database

### 12.2 Deployment Process

1. **Code Changes:**
   - Develop locally
   - Test with sample PDFs
   - Commit to `main` branch

2. **CI/CD:**
   - Push to GitHub
   - Streamlit Cloud auto-deploys
   - Health check after deployment

3. **Rollback:**
   - Use GitHub to revert commit
   - Streamlit redeploys previous version

### 12.3 Configuration

**Environment Variables:**
```
SUPABASE_URL
SUPABASE_KEY
GEMINI_API_KEY
GEMINI_MODEL
AI_PROVIDER
GOOGLE_CLOUD_PROJECT
```

---

## 13. Documentation Requirements

### 13.1 User Documentation

**Files:**
- `LAUNCH.md`: How to run the app
- `QUICKSTART.md`: Quick start guide
- `DB.md`: Database query reference
- `README.md`: Project overview

**Future:**
- In-app tooltips
- Video tutorials
- FAQ section

### 13.2 Developer Documentation

**Required:**
- Code comments for complex logic
- API documentation
- Database schema diagrams
- Architecture decision records (ADRs)

---

## 14. Roadmap

### Phase 1: Single Company Search & Analysis ✅ (Completed - December 2025)

**Goal:** "Do It Anyway" - Build entire system with minimum efficiency

**Features Delivered:**
- ✅ PDF upload and processing (TCFD, TNFD, Sustainability Reports, Data Books, Integrated Reports)
- ✅ Document library with upload → process workflow
- ✅ Text and image extraction using Docling
- ✅ Vector embeddings with Gemini (768-dim)
- ✅ Semantic search with Supabase pgvector
- ✅ Q&A chat interface
- ✅ Inline image display with answers
- ✅ Source citations and confidence scoring
- ✅ Shadcn-inspired modern UI
- ✅ Deployment to Streamlit Cloud
- ✅ Support for local .env and cloud secrets

**Success Criteria:**
- Can upload and process 100+ page reports in <2 minutes
- Answer accuracy >80% on TCFD/TNFD questions
- Users can search by company name, keywords, or specific questions
- Charts and diagrams display correctly with answers

---

### Phase 2: Multi-Company Comparison & Expert Control (Q1 2026)

**Goal:** "Love The Unknown" + "For Others" - Enable comparison and domain expert refinement

**Features:**
- 🔲 Multi-company comparison interface
  - Select 2-5 companies
  - Side-by-side metric comparison
  - Synchronized chart viewing
  - Comparison table export (Excel/CSV)

- 🔲 Domain Expert Control Panel
  - Real-time instruction file editing
  - Template management for report types (TCFD, TNFD, etc.)
  - Custom field extraction rules
  - A/B testing of instructions
  - Version control and rollback

- 🔲 Enhanced AI Support
  - Claude integration
  - Perplexity integration
  - Provider performance comparison

- 🔲 Advanced Search
  - Filter by report type (TCFD, TNFD, Sustainability, Integrated)
  - Filter by company industry, region, size
  - Date range filtering
  - Saved searches and favorites

- 🔲 Export & Sharing
  - Export conversation history
  - Share Q&A sessions with team
  - Export comparison tables

**Success Criteria:**
- Can compare 5 companies simultaneously in <5 seconds
- Domain experts can edit instructions without developer help
- Answer accuracy improves to >90% through expert refinement
- Users save 2+ hours per comparison analysis

**Technical Milestones:**
- Instruction template storage system
- Multi-document aggregation engine
- Comparison visualization components
- A/B testing framework

---

### Phase 3: IR Writing Assistant (Q2 2026)

**Goal:** "Towards Inspiration" - Integrate search with content creation

**Features:**
- 🔲 Rich Text Writing Environment
  - Block-based editor (TipTap/Quill)
  - Inline search commands (e.g., `/search climate risks`)
  - Drag-and-drop charts into writing blocks
  - Markdown and rich text support

- 🔲 Database-Backed Content
  - Search PDF database while writing
  - Embed search results as content blocks
  - Automatic source citations
  - Chart/table insertion with sources

- 🔲 Collaboration Features
  - Multi-user editing
  - Comments and suggestions
  - Version history
  - Team templates

- 🔲 Export & Publishing
  - Export to Word (.docx) with formatting
  - Export to PDF with citations
  - HTML export for web publishing
  - Template-based output (client reports, etc.)

- 🔲 AI Writing Assistance
  - Suggest relevant sources while writing
  - Auto-complete based on company data
  - Summary generation from multiple sources
  - Tone and style consistency checks

**Success Criteria:**
- Users can search and write in single workflow
- 50% reduction in time to create client reports
- 100% of sources automatically cited
- Export maintains formatting and citations

**Technical Milestones:**
- Rich text editor integration
- Citation management system
- Document export engine
- Real-time collaboration infrastructure

---

### Phase 4: Enterprise & Advanced AI (Q3-Q4 2026)

**Goal:** Scale and enhance with enterprise features and advanced AI

**Features:**
- 🔲 Enterprise Security
  - SSO/SAML authentication
  - Role-based access control (Admin, Analyst, Viewer)
  - Document-level permissions
  - Audit logs and compliance reporting
  - Data retention policies

- 🔲 API & Integrations
  - REST API for programmatic access
  - Slack/Teams integration for search
  - CRM integration (Salesforce, HubSpot)
  - Zapier/Make.com connectors

- 🔲 Advanced AI Features
  - Custom fine-tuned models for corporate reports
  - Multi-language support (Japanese, Chinese, German, French)
  - Automatic report summarization
  - Trend analysis across reports and time periods
  - Predictive insights (e.g., "Companies likely to improve ESG scores")
  - Anomaly detection in disclosures

- 🔲 Analytics & Insights
  - Dashboard with report coverage statistics
  - Industry benchmarking
  - Disclosure gap analysis
  - Timeline views of company changes
  - Alert system for new disclosures

- 🔲 Continuous Improvement
  - Feedback loop from user ratings
  - Auto-refinement of extraction rules
  - Learning from domain expert edits
  - Model performance monitoring

**Success Criteria:**
- Support 1000+ concurrent users
- 95%+ answer accuracy
- <1 second query response time
- Enterprise-grade security compliance (SOC2, ISO 27001)

**Technical Milestones:**
- Scalable infrastructure (Kubernetes, Cloud Run)
- CDN for global performance
- Redis caching layer
- Fine-tuning pipeline
- Multi-language NLP models

---

### Long-Term Vision (2027+)

- 🔮 Real-time report monitoring (auto-process new reports)
- 🔮 Predictive modeling (forecast company ESG trajectories)
- 🔮 Natural language SQL for custom queries
- 🔮 Interactive data visualizations
- 🔮 White-label solutions for consulting firms
- 🔮 Mobile apps (iOS, Android)
- 🔮 Voice interface for queries

---

### Development Approach

Following our "Do It Anyway → Love The Unknown → For Others → Towards Inspiration" philosophy:

**Sprint Structure:**
- 2-week sprints
- Each sprint delivers usable feature increment
- Weekly demos to business solutions team
- Continuous feedback integration

**Efficiency Improvement Strategy:**
1. **Weeks 1-4:** Build minimum viable system (even if accuracy is 70%)
2. **Weeks 5-8:** Enable domain experts to refine instructions
3. **Weeks 9-12:** Iterate daily based on expert feedback
4. **Ongoing:** Measure accuracy improvement week-over-week

**If Target Efficiency Not Met:**
- Domain experts iterate on instruction templates
- A/B test different prompt approaches
- Adjust chunk sizes and embedding parameters
- Incorporate user feedback into training data
- Consider model fine-tuning if needed

**Key Principle:** Ship early, learn fast, improve continuously

---

## 15. Risks & Mitigations

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| API rate limits | High | Medium | Implement caching, queue system |
| Vector search accuracy | High | Low | Fine-tune similarity threshold, use hybrid search |
| Large file processing timeout | Medium | Medium | Implement async processing, progress indicators |
| Embedding cost | Medium | High | Cache embeddings, optimize chunk size |

### Business Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Low user adoption | High | Medium | User testing, improve UX, marketing |
| Data privacy concerns | High | Low | Clear privacy policy, user data ownership |
| Competitor advantage | Medium | Medium | Rapid iteration, unique features |

---

## 16. Dependencies

### External Services
- ✅ Gemini API (Google)
- ✅ Supabase (Database + Vector Search)
- ⏳ Claude API (Anthropic)
- ⏳ Perplexity API

### Python Libraries
- ✅ Streamlit
- ✅ Docling
- ✅ google-generativeai
- ✅ supabase-py
- ⏳ anthropic (future)

### Infrastructure
- ✅ GitHub (version control)
- ✅ Streamlit Cloud (hosting)
- ⏳ Google Cloud Run (future scaling)

---

## 17. Open Questions

### Strategic Questions

1. **Report Type Coverage:** Should we expand beyond TCFD/TNFD to other frameworks (GRI, SASB, CDP)?
2. **Multi-tenancy:** How will we handle multiple client organizations?
3. **Pricing:** Freemium vs subscription model? Per-document or per-user pricing?
4. **Data Retention:** How long to keep uploaded documents? Auto-archive policies?
5. **Compliance:** What certifications needed? GDPR, SOC2, ISO 27001?

### Technical Questions

1. **Comparison Limits:** What's the max number of companies to compare simultaneously? (Current thinking: 5)
2. **Writing Assistant Architecture:** Separate app or integrated into main app?
3. **Instruction File Format:** YAML, JSON, or custom DSL for domain expert templates?
4. **Real-time Collaboration:** Use WebSockets or polling for multi-user editing?
5. **Model Fine-tuning:** When to move from prompt engineering to fine-tuning?

### Business Questions

1. **Target Market:** Focus on consulting firms, corporate IR teams, or investment firms first?
2. **Success Metrics:** What KPIs define "good enough" for each phase?
3. **Domain Expert Availability:** How much time can business solutions team dedicate to instruction refinement?
4. **Competitive Analysis:** How do we differentiate from Bloomberg, FactSet, or generic ChatGPT?
5. **Language Priority:** Which languages to support first after English? (Japanese high priority)

### User Experience Questions

1. **Comparison UI:** Table view, card view, or split-screen view for company comparison?
2. **Writing Assistant UX:** Google Docs-style, Notion-style, or custom design?
3. **Mobile Support:** Is mobile access required? If so, which phase?
4. **Notification System:** How to alert users about new reports or disclosure updates?
5. **Onboarding:** What training is needed for business solutions team to use Expert Control Panel?

---

## 18. Approval & Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Manager | TBD | - | |
| Tech Lead | TBD | - | |
| Design Lead | TBD | - | |
| Security | TBD | - | |

---

## Appendix A: Glossary

- **RAG:** Retrieval Augmented Generation - AI technique combining document retrieval with generation
- **Embedding:** Numerical vector representation of text for semantic search
- **pgvector:** PostgreSQL extension for vector similarity search
- **Chunk:** Segment of text (typically 512 tokens) for processing
- **IR:** Investor Relations
- **LLM:** Large Language Model
- **Vector Database:** Database optimized for similarity search

---

## Appendix B: References

- [Streamlit Documentation](https://docs.streamlit.io)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Supabase Vector Guide](https://supabase.com/docs/guides/ai/vector-embeddings)
- [Docling Documentation](https://github.com/DS4SD/docling)

---

**Document Control:**
- Version: 1.0
- Last Updated: December 17, 2025
- Next Review: January 17, 2026
