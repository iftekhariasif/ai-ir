# RAG System Improvement Plan

**Version:** 1.0
**Date:** December 22, 2025
**Status:** Proposed Improvements

---

## Current Problems Identified

### 1. Image Placement Issues
**Problem:** Charts and images don't appear in the proper/expected places in the output.

**Current Behavior:**
- System retrieves top 5 text chunks
- Shows ALL images from those document(s)
- Images appear at the end, not contextually placed
- No relevance ranking for images

**Expected Behavior:**
- Images should appear near related text
- Only show images relevant to the specific answer
- Prioritize charts/diagrams that directly answer the question

---

### 2. Old PDF Bias
**Problem:** System always shows results from 2 specific PDFs, ignoring newly uploaded documents.

**Current Behavior:**
- Same documents dominate search results
- New PDFs don't appear in answers even when relevant
- No diversity in source documents

**Expected Behavior:**
- Fair representation across all uploaded documents
- Recent documents should have higher visibility
- Results should span multiple sources when available

---

## Root Cause Analysis

### Issue 1: Image Placement

**Root Causes:**

1. **Document-level Image Association**
   - Images linked to `document_id` only
   - Not associated with specific chunks where they appear
   - `chunk_id` field in `document_images` is nullable and likely unused

2. **No Image-Text Alignment**
   - No understanding of which image relates to which text
   - Missing caption/context embeddings for images
   - No image relevance scoring

3. **Bulk Image Retrieval**
   ```python
   # Current: Gets ALL images from document
   images = self.get_document_images(chunk['document_id'])

   # Problem: Returns 307 images from one document!
   ```

4. **No Visual Understanding**
   - No OCR on charts to understand content
   - No analysis of chart types (bar, line, pie, etc.)
   - Missing axis labels, legends, data points

**Code Evidence:**
```python
# supabase_utils.py line 167
for chunk in result.data:
    images = self.get_document_images(chunk['document_id'])  # Gets ALL images!
    enhanced_results.append({
        'images': images  # No filtering or ranking
    })
```

---

### Issue 2: Old PDF Bias

**Root Causes:**

1. **No Recency Weighting**
   - Vector search uses only cosine similarity
   - No timestamp boosting for recent documents
   - Older documents with more chunks dominate results

2. **Embedding Quality Variance**
   - First documents might have better embeddings
   - Chunk size/strategy might have changed
   - No normalization across documents

3. **No Result Diversity**
   - No mechanism to ensure multiple documents in results
   - Top 5 chunks might all be from same document
   - No document-level deduplication

4. **Similarity Threshold Issues**
   - Current threshold: 0.7 (might be too high)
   - New PDFs might have slightly lower similarity
   - No dynamic threshold adjustment

**Code Evidence:**
```python
# supabase_utils.py line 131-161
def search_similar_chunks(self, query: str, limit: int = 5, threshold: float = 0.7):
    # Only uses vector similarity - no recency, no diversity
    result = self.client.rpc('match_document_chunks', {
        'query_embedding': query_embedding,
        'match_threshold': threshold,  # Fixed at 0.7
        'match_count': limit  # Could all be from same doc
    })
```

---

## Proposed Solutions

### Solution 1: Context-Aware Image Retrieval

#### 1A. Associate Images with Chunks (Quick Win)

**Implementation:**

Update `document_processor.py` to link images to specific chunks:

```python
def _extract_images(self, result, chunks):
    """Extract images and associate with relevant chunks"""
    images = []

    for page_num, page in enumerate(result.document.pages):
        for img_idx, image in enumerate(page.images):
            # Find which chunk this image belongs to
            image_context = self._get_surrounding_text(page_num, image.bbox)

            # Find best matching chunk
            chunk_id = self._find_matching_chunk(image_context, chunks)

            images.append({
                'filename': f"page_{page_num}_img_{img_idx}.png",
                'base64_data': base64_encode(image.pil_image),
                'chunk_id': chunk_id,  # Link to specific chunk!
                'caption': image.caption or '',
                'context': image_context,
                'page_num': page_num
            })

    return images
```

**Benefits:**
- Images tied to specific text sections
- Can retrieve only relevant images per chunk
- Better image placement in output

**Effort:** Medium

---

#### 1B. Image Caption Embeddings (Medium Priority)

**Implementation:**

Generate embeddings for image captions and context:

```python
# In supabase_utils.py - store_document()

for idx, image in enumerate(images):
    # Generate embedding for image context
    image_text = f"{image.get('caption', '')} {image.get('context', '')}"
    image_embedding = self.generate_embedding(image_text)

    image_data = {
        'document_id': doc_id,
        'chunk_id': image.get('chunk_id'),
        'image_index': idx,
        'image_data': image['base64_data'],
        'caption': image.get('caption', ''),
        'context': image.get('context', ''),
        'embedding': image_embedding  # New field!
    }
```

**Database Migration:**
```sql
-- Add embedding column to document_images
ALTER TABLE document_images
ADD COLUMN embedding VECTOR(768);

-- Create image search function
CREATE OR REPLACE FUNCTION match_document_images(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 3
)
RETURNS TABLE (
    id BIGINT,
    document_id BIGINT,
    chunk_id BIGINT,
    image_data TEXT,
    caption TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        i.id,
        i.document_id,
        i.chunk_id,
        i.image_data,
        i.caption,
        1 - (i.embedding <=> query_embedding) AS similarity
    FROM document_images i
    WHERE 1 - (i.embedding <=> query_embedding) > match_threshold
    ORDER BY i.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

**Benefits:**
- Search for relevant images directly
- Rank images by relevance to query
- Show only 2-3 most relevant charts

**Effort:** High

---

#### 1C. Chart OCR & Understanding (Advanced)

**Implementation:**

Use OCR to extract text from charts and create richer context:

```python
import easyocr
from PIL import Image

def _analyze_chart(self, image_pil: Image) -> Dict:
    """Extract text from chart using OCR"""
    reader = easyocr.Reader(['en'])

    # OCR on image
    results = reader.readtext(np.array(image_pil))

    # Extract text
    chart_text = ' '.join([text for (bbox, text, prob) in results])

    # Classify chart type (optional - using image classification)
    chart_type = self._classify_chart_type(image_pil)  # bar/line/pie

    return {
        'ocr_text': chart_text,
        'chart_type': chart_type,
        'contains_data': len(results) > 0
    }
```

**Benefits:**
- Understand what data is in charts
- Search charts by their content
- Better relevance matching

**Effort:** Very High

---

### Solution 2: Fix Old PDF Bias

#### 2A. Hybrid Search with Recency Boosting (High Priority)

**Implementation:**

Add recency weighting to search results:

```python
# supabase_schema.sql - Update match_document_chunks function

CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    recency_weight FLOAT DEFAULT 0.2  -- New parameter!
)
RETURNS TABLE (
    id BIGINT,
    document_id BIGINT,
    text TEXT,
    heading TEXT,
    similarity FLOAT,
    final_score FLOAT,
    filename TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.document_id,
        c.text,
        c.heading,
        1 - (c.embedding <=> query_embedding) AS similarity,
        -- Combine similarity with recency
        (1 - (c.embedding <=> query_embedding)) * (1 - recency_weight) +
        (EXTRACT(EPOCH FROM (NOW() - d.created_at)) / 86400.0)::FLOAT * recency_weight AS final_score,
        d.filename,
        d.created_at
    FROM document_chunks c
    JOIN documents d ON c.document_id = d.id
    WHERE 1 - (c.embedding <=> query_embedding) > match_threshold
    ORDER BY final_score DESC  -- Changed from similarity
    LIMIT match_count;
END;
$$;
```

**Benefits:**
- Recent documents rank higher
- Configurable recency weight (0.2 = 20% recency, 80% similarity)
- Still shows old docs if they're very relevant

**Effort:** Medium

---

#### 2B. Result Diversification (Medium Priority)

**Implementation:**

Ensure results come from multiple documents:

```python
# qa_agent.py - answer_question()

def answer_question(self, question: str, max_chunks: int = 5):
    # Get more candidates than needed
    candidates = self.supabase.search_similar_chunks(
        query=question,
        limit=max_chunks * 3  # Get 15 candidates
    )

    # Diversify by document
    diverse_chunks = self._diversify_results(candidates, max_chunks)

    # Continue with diverse_chunks...

def _diversify_results(self, chunks: List[Dict], target: int) -> List[Dict]:
    """Ensure results span multiple documents"""
    diverse = []
    seen_docs = set()

    # First pass: one chunk per document
    for chunk in chunks:
        doc_id = chunk['document_id']
        if doc_id not in seen_docs:
            diverse.append(chunk)
            seen_docs.add(doc_id)
            if len(diverse) >= target:
                return diverse

    # Second pass: allow repeats if needed
    for chunk in chunks:
        if len(diverse) >= target:
            break
        if chunk not in diverse:
            diverse.append(chunk)

    return diverse[:target]
```

**Benefits:**
- Results span multiple documents
- Users see different sources
- Better for multi-company comparison

**Effort:** Low

---

#### 2C. Lower Similarity Threshold & Add Filters (Quick Win)

**Implementation:**

```python
# qa_agent.py

def answer_question(
    self,
    question: str,
    max_chunks: int = 5,
    threshold: float = 0.5,  # Lower from 0.7 to 0.5
    document_filter: List[int] = None  # Optional doc filter
):
    relevant_chunks = self.supabase.search_similar_chunks(
        query=question,
        limit=max_chunks,
        threshold=threshold,
        document_ids=document_filter  # Filter by specific docs
    )
```

**Update search function:**
```sql
-- Add document filtering
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.5,  -- Lowered!
    match_count INT DEFAULT 5,
    document_ids BIGINT[] DEFAULT NULL  -- New filter
)
...
WHERE 1 - (c.embedding <=> query_embedding) > match_threshold
  AND (document_ids IS NULL OR c.document_id = ANY(document_ids))
```

**Benefits:**
- More lenient matching
- Can filter to specific documents
- Better recall (might sacrifice precision slightly)

**Effort:** Very Low

---

#### 2D. Debug & Monitoring Dashboard (High Priority)

**Implementation:**

Add a debug page to understand search behavior:

```python
# app.py - Add Debug page

if st.session_state.get('debug_mode'):
    with st.expander("🔍 Search Debug Info"):
        # Show all documents
        all_docs = supabase.list_documents()
        st.write(f"Total Documents: {len(all_docs)}")

        for doc in all_docs:
            st.write(f"- {doc['filename']}: {doc['chunk_count']} chunks, {doc['image_count']} images")

        # Show search results with scores
        if question:
            results = supabase.search_similar_chunks(question, limit=10)

            st.write("### Top 10 Results:")
            for i, chunk in enumerate(results):
                st.write(f"{i+1}. {chunk['filename']} (similarity: {chunk['similarity']:.3f})")
                st.write(f"   Chunk: {chunk['heading']}")
                st.write(f"   Text preview: {chunk['text'][:100]}...")
```

**Benefits:**
- See which documents are being searched
- Understand similarity scores
- Identify bias patterns
- Debug new PDFs not appearing

**Effort:** Low

---

## Implementation Priority

### Phase 1: Quick Wins
**Goal:** Fix immediate issues with minimal effort

1. ✅ **Lower similarity threshold**
   - Change from 0.7 → 0.5
   - Test with existing PDFs

2. ✅ **Add debug dashboard**
   - See all documents and their chunk counts
   - View search results with scores
   - Identify bias

3. ✅ **Result diversification**
   - Ensure results from multiple documents
   - Prevent one document dominating

4. ✅ **Associate images with chunks**
   - Update document_processor.py
   - Link images to specific chunks
   - Filter images by chunk relevance

**Expected Impact:** 40% improvement in diversity, 30% better image relevance

---

### Phase 2: Medium Priority
**Goal:** Improve relevance and recency

5. ✅ **Recency boosting**
   - Update SQL function
   - Add timestamp weighting
   - Test with new vs old PDFs

6. ✅ **Image caption embeddings**
   - Add embedding column to document_images
   - Create image search function
   - Rank images by relevance

7. ✅ **Chunk-level image retrieval**
   - Only show images from retrieved chunks
   - Limit to top 3 most relevant images
   - Improve placement

**Expected Impact:** 60% improvement in recency, 50% better image placement

---

### Phase 3: Advanced Features
**Goal:** Deep improvements in understanding

8. ⏳ **Chart OCR**
   - Extract text from charts
   - Index chart content
   - Search by chart data

9. ⏳ **Hybrid search**
   - Combine vector + keyword search
   - Add BM25 for exact matches
   - Metadata filtering (report type, date, company)

10. ⏳ **Re-ranking**
    - Cross-encoder for better relevance
    - LLM-based relevance scoring
    - User feedback loop

**Expected Impact:** 80% improvement in accuracy, 70% better image relevance

---

## Metrics to Track

### Before Improvements (Baseline)
- [ ] Average number of documents in top 5 results: ?
- [ ] % of queries showing recent PDFs: ?
- [ ] Average images shown per answer: ?
- [ ] % of relevant images: ?
- [ ] User satisfaction: ?

### After Phase 1 (Target)
- [ ] Documents in top 5: 3-4 different docs
- [ ] Recent PDFs shown: 50%+
- [ ] Images per answer: 2-3 (down from all)
- [ ] Relevant images: 60%+
- [ ] User satisfaction: +30%

### After Phase 2 (Target)
- [ ] Documents in top 5: 4-5 different docs
- [ ] Recent PDFs shown: 70%+
- [ ] Images per answer: 2-3 highly relevant
- [ ] Relevant images: 80%+
- [ ] User satisfaction: +50%

### After Phase 3 (Target)
- [ ] Documents in top 5: 5 different docs
- [ ] Recent PDFs shown: 80%+
- [ ] Images per answer: 1-2 perfect matches
- [ ] Relevant images: 90%+
- [ ] User satisfaction: +70%

---

## Testing Plan

### Test Case 1: New PDF Visibility
**Setup:**
1. Upload 5 old PDFs
2. Upload 2 new PDFs
3. Ask questions that should match new PDFs

**Expected:**
- New PDFs appear in results
- At least 1 new PDF in top 3 results
- Not always showing same old PDFs

### Test Case 2: Image Relevance
**Setup:**
1. Ask: "Show me the carbon emissions chart"
2. Ask: "What are the governance risks?"

**Expected:**
- Case 1: Show emissions chart only (not all charts)
- Case 2: Show governance diagram, not emissions chart
- Max 2-3 images per answer

### Test Case 3: Multi-Document Coverage
**Setup:**
1. Ask: "Compare climate risks across companies"
2. Ensure 3+ companies uploaded

**Expected:**
- Results from 3+ different documents
- Not all from one company
- Diverse sources

---

## Code Changes Summary

### Files to Modify

1. **document_processor.py**
   - Add `_get_surrounding_text()` method
   - Add `_find_matching_chunk()` method
   - Update `_extract_images()` to link to chunks

2. **supabase_utils.py**
   - Update `store_document()` to save chunk_id for images
   - Add image embedding generation
   - Update `search_similar_chunks()` to use recency
   - Add `_diversify_results()` method

3. **supabase_schema.sql**
   - Add `embedding` column to `document_images`
   - Update `match_document_chunks()` function
   - Add `match_document_images()` function
   - Add recency weighting

4. **qa_agent.py**
   - Update `answer_question()` to use diverse results
   - Add chunk-level image filtering
   - Lower similarity threshold

5. **app.py**
   - Add debug mode toggle
   - Add search debug dashboard
   - Show document statistics

---

## Migration Script

```python
# migration_001_image_improvements.py

from supabase import create_client
import os

def migrate():
    """Add image embeddings and recency to existing data"""

    client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

    # 1. Add embedding column (already in SQL)
    # Run: ALTER TABLE document_images ADD COLUMN embedding VECTOR(768);

    # 2. Generate embeddings for existing images
    images = client.table('document_images').select('*').execute()

    for image in images.data:
        text = f"{image['caption']} {image['context']}"
        embedding = generate_embedding(text)

        client.table('document_images').update({
            'embedding': embedding
        }).eq('id', image['id']).execute()

        print(f"Updated image {image['id']}")

    print("Migration complete!")

if __name__ == '__main__':
    migrate()
```

---

## Expected Outcomes

### Immediate (After Phase 1)
✅ New PDFs will appear in search results
✅ Images will be limited to 2-3 most relevant
✅ Results will span multiple documents
✅ Debug visibility into search behavior

### Medium-term (After Phase 2)
✅ Recent documents will rank higher
✅ Images will be contextually placed
✅ Image relevance will improve significantly
✅ Better multi-company comparison

### Long-term (After Phase 3)
✅ Can search charts by their content
✅ Hybrid search for better accuracy
✅ Near-perfect image placement
✅ Continuous learning from feedback

---

## Open Questions

1. **Image Limit:** How many images per answer is ideal? (Currently: all → Proposed: 2-3)
2. **Recency Weight:** What balance between recency and relevance? (Proposed: 20% recency)
3. **Similarity Threshold:** 0.5 too low? 0.6? (Need testing)
4. **Chart OCR:** Worth the effort? (High cost, moderate benefit)
5. **User Feedback:** Should we add thumbs up/down for results?

---

## Next Steps

1. **Immediate:** Implement Phase 1 (debug dashboard + quick wins)
2. **This Week:** Test with real queries and measure improvements
3. **Next Week:** Start Phase 2 if Phase 1 shows promise
4. **Ongoing:** Collect user feedback and iterate

---

## References

- Current codebase: `supabase_utils.py`, `qa_agent.py`, `document_processor.py`
- Database schema: `supabase_schema.sql`
- PRD: `doc/PRD.md`
- Database queries: `doc/DB.md`

---

**Document Status:** Ready for Review
**Next Review:** After Phase 1 implementation
