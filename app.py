"""
Company Information Q&A Chatbot
Streamlit app with Admin and User tabs
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import base64
from io import BytesIO
from PIL import Image

# Import custom modules
from document_processor import process_and_prepare
from supabase_utils import SupabaseManager
from qa_agent import QAAgent

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="IR AI", page_icon="🤖", layout="wide")

# Shadcn-inspired Custom CSS
st.markdown("""
<style>
    /* Global styles */
    .main {
        background-color: #ffffff;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #fafafa;
        border-right: 1px solid #e4e4e7;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 6px;
        border: 1px solid #e4e4e7;
        transition: all 0.2s;
        font-weight: 500;
    }

    .stButton > button:hover {
        background-color: #f4f4f5;
        border-color: #d4d4d8;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background-color: #18181b;
        color: white;
        border: none;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #27272a;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 6px;
        border: 1px solid #e4e4e7;
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 8px;
        border: 1px solid #e4e4e7;
        margin-bottom: 1rem;
    }

    /* Headers */
    h1, h2, h3 {
        font-weight: 600;
        color: #18181b;
    }

    /* Dividers */
    hr {
        border-color: #e4e4e7;
    }

    /* Success/Warning/Error boxes */
    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 6px;
        border-left: 4px solid;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border-radius: 8px;
        border: 2px dashed #e4e4e7;
    }

    /* Tables */
    .stMarkdown table {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Expander */
    .streamlit-expanderHeader {
        border-radius: 6px;
        background-color: #fafafa;
    }

    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Chat"

# Sidebar navigation
with st.sidebar:
    st.title("🤖 IR AI")

    st.divider()

    # AI Provider Selection
    st.subheader("AI Provider")

    # Initialize provider in session state
    if 'ai_provider' not in st.session_state:
        st.session_state.ai_provider = "GEMINI"

    # Provider options
    provider_options = ["GEMINI", "CLAUDE (Coming Soon)", "PERPLEXITY (Coming Soon)"]

    # Get current selection index
    if st.session_state.ai_provider == "GEMINI":
        default_index = 0
    elif st.session_state.ai_provider == "CLAUDE":
        default_index = 1
    else:
        default_index = 0

    selected_provider = st.selectbox(
        "Select AI Model",
        provider_options,
        index=default_index,
        label_visibility="collapsed"
    )

    # Handle selection
    if selected_provider == "GEMINI":
        st.session_state.ai_provider = "GEMINI"
    elif "CLAUDE" in selected_provider:
        st.warning("⚠️ Claude integration coming soon")
        st.session_state.ai_provider = "GEMINI"  # Fallback to Gemini
    elif "PERPLEXITY" in selected_provider:
        st.warning("⚠️ Perplexity integration coming soon")
        st.session_state.ai_provider = "GEMINI"  # Fallback to Gemini

    st.divider()

    # Navigation buttons
    if st.button("Chat", use_container_width=True, type="primary" if st.session_state.current_page == "Chat" else "secondary"):
        st.session_state.current_page = "Chat"
        st.rerun()

    if st.button("Library", use_container_width=True, type="primary" if st.session_state.current_page == "Library" else "secondary"):
        st.session_state.current_page = "Library"
        st.rerun()

    st.divider()

    # API Keys Status
    st.subheader("⚙️ Configuration")

    def get_secret(key: str) -> str:
        """Get secret from Streamlit secrets or environment variable"""
        try:
            return st.secrets.get(key)
        except:
            return os.getenv(key)

    supabase_url = get_secret('SUPABASE_URL')
    supabase_key = get_secret('SUPABASE_KEY')
    gemini_key = get_secret('GEMINI_API_KEY')

    st.text(f"Supabase: {'✅' if supabase_url else '❌'}")
    st.text(f"Gemini API: {'✅' if gemini_key else '❌'}")

    if not all([supabase_url, supabase_key, gemini_key]):
        st.warning("⚠️ Missing API keys")

    st.divider()

    # Clear chat button
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ========================================
# CHAT PAGE - Chat Interface
# ========================================
if st.session_state.current_page == "Chat":
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display images inline if present
            if "images" in message and message["images"]:
                for img_data in message["images"]:
                    try:
                        img_bytes = base64.b64decode(img_data['image_data'])
                        img = Image.open(BytesIO(img_bytes))
                        st.image(img, use_container_width=True)
                    except:
                        pass  # Skip if image data is invalid

    # Chat input at bottom
    if prompt := st.chat_input("Ask a question about the company..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process query with RAG + Pydantic AI
        with st.chat_message("assistant"):
            with st.spinner("Searching for answer..."):
                try:
                    # Get answer from QA agent
                    agent = QAAgent()
                    result = agent.answer_question(prompt)

                    # Display answer
                    st.markdown(result['answer'])

                    # Display relevant images inline (like ChatGPT)
                    if result.get('images'):
                        for idx, img_data in enumerate(result['images'][:3]):
                            # Decode base64 image
                            img_bytes = base64.b64decode(img_data['image_data'])
                            img = Image.open(BytesIO(img_bytes))
                            st.image(img, use_container_width=True)

                    # Display confidence and sources at the bottom
                    st.caption(f"Confidence: {result['confidence'].upper()} | Chunks used: {result['chunks_used']}")

                    if result.get('sources'):
                        with st.expander("📚 Sources"):
                            for source in result['sources']:
                                st.text(f"• {source}")

                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result['answer'],
                        "images": result.get('images', []),
                        "sources": result.get('sources', []),
                        "confidence": result['confidence']
                    })

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

# ========================================
# LIBRARY PAGE - PDF Upload & Processing
# ========================================
elif st.session_state.current_page == "Library":
    # Header with upload button on right
    col1, col2 = st.columns([3, 1])

    with col1:
        st.header("Document Management")

    with col2:
        st.write("")  # Spacing
        if st.button("Upload File", type="primary"):
            st.session_state.show_upload_modal = True

    # Upload modal
    if st.session_state.get('show_upload_modal', False):
        with st.container():
            st.subheader("Upload PDF File")

            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                key="pdf_uploader"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Upload", type="primary", disabled=uploaded_file is None):
                    if uploaded_file:
                        # Save to temp directory
                        temp_dir = Path("temp/uploads")
                        temp_dir.mkdir(parents=True, exist_ok=True)

                        pdf_path = temp_dir / uploaded_file.name
                        with open(pdf_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())

                        st.success(f"✅ Uploaded {uploaded_file.name}")
                        st.session_state.show_upload_modal = False
                        st.rerun()

            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.show_upload_modal = False
                    st.rerun()

            st.divider()

    # Show documents table
    st.divider()
    st.subheader("📁 Document Library")

    try:
        # Get uploaded files (not yet processed)
        temp_upload_dir = Path("temp/uploads")
        uploaded_files = []
        if temp_upload_dir.exists():
            uploaded_files = [f.name for f in temp_upload_dir.glob("*.pdf")]

        # Get processed documents from Supabase
        supabase_manager = SupabaseManager()
        processed_docs = supabase_manager.list_documents()
        processed_filenames = [doc['filename'] for doc in processed_docs] if processed_docs else []

        # Combine both lists
        all_files = set(uploaded_files + processed_filenames)

        if all_files:
            # Table header
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1.5, 1.5])
            with col1:
                st.markdown("**Filename**")
            with col2:
                st.markdown("**Status**")
            with col3:
                st.markdown("**Details**")
            with col4:
                st.markdown("**Process**")
            with col5:
                st.markdown("**Delete**")

            st.divider()

            # Table rows
            for filename in sorted(all_files):
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1.5, 1.5])

                # Check if processed
                is_processed = filename in processed_filenames
                doc_data = None
                if is_processed:
                    doc_data = next((d for d in processed_docs if d['filename'] == filename), None)

                with col1:
                    st.text(filename)

                with col2:
                    if is_processed:
                        st.success("✅ Processed")
                    else:
                        st.warning("⏳ Pending")

                with col3:
                    if is_processed and doc_data:
                        st.text(f"{doc_data['chunk_count']} chunks, {doc_data['image_count']} imgs")
                    else:
                        st.text("Not processed")

                with col4:
                    # Process button
                    if st.button(
                        "🔄 Process",
                        key=f"process_{filename}",
                        disabled=is_processed,
                        help="Convert to markdown and store" if not is_processed else "Already processed"
                    ):
                        with st.spinner(f"Processing {filename}..."):
                            try:
                                pdf_path = temp_upload_dir / filename

                                # Process PDF
                                st.info("⚙️ Extracting text and images...")
                                processed_data = process_and_prepare(str(pdf_path), filename)

                                # Store in Supabase
                                st.info("💾 Storing in Supabase...")
                                result = supabase_manager.store_document(
                                    filename=processed_data['filename'],
                                    full_text=processed_data['full_text'],
                                    chunks=processed_data['chunks'],
                                    images=processed_data['images']
                                )

                                st.success(f"✅ Successfully processed {filename}")
                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")

                with col5:
                    # Delete button
                    if st.button("🗑️", key=f"delete_{filename}", help="Delete this file"):
                        with st.spinner("Deleting..."):
                            try:
                                # Delete from temp if exists
                                temp_file = temp_upload_dir / filename
                                if temp_file.exists():
                                    temp_file.unlink()

                                # Delete from database if processed
                                if is_processed and doc_data:
                                    supabase_manager.delete_document(doc_data['id'])

                                st.success(f"Deleted {filename}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete: {str(e)}")

                st.divider()

        else:
            st.info("No files uploaded yet. Click 'Upload File' to get started.")

    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")
