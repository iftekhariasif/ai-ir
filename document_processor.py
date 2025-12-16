"""
Document processor for extracting text and images from PDFs
Prepares content for storage in Supabase
"""

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption
from pathlib import Path
import base64
from typing import Dict, List
import re


class DocumentProcessor:
    """Processes PDFs to extract text chunks and images"""

    def __init__(self):
        """Initialize document converter"""
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = True
        pipeline_options.images_scale = 2.0
        pipeline_options.generate_page_images = False
        pipeline_options.generate_picture_images = True

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Process PDF and extract text chunks and images

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dict with full_text, chunks, and images
        """
        print(f"📄 Processing PDF: {pdf_path}")

        # Convert PDF
        result = self.converter.convert(pdf_path)
        full_text = result.document.export_to_markdown()

        print(f"✅ Extracted {len(full_text)} characters")

        # Extract images
        images = self._extract_images(result)
        print(f"🖼️  Extracted {len(images)} images")

        # Create text chunks
        chunks = self._create_chunks(full_text)
        print(f"📝 Created {len(chunks)} text chunks")

        return {
            'full_text': full_text,
            'chunks': chunks,
            'images': images
        }

    def _extract_images(self, result) -> List[Dict]:
        """Extract and encode images from document"""
        images = []

        if hasattr(result.document, 'pictures') and result.document.pictures:
            for idx, picture in enumerate(result.document.pictures):
                try:
                    # Get image
                    img = None
                    if hasattr(picture, 'get_image'):
                        img = picture.get_image(result.document)
                    elif hasattr(picture, 'image'):
                        img = picture.image

                    if img:
                        # Convert to base64
                        from io import BytesIO
                        buffer = BytesIO()
                        img.save(buffer, format='PNG')
                        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

                        images.append({
                            'filename': f"image_{idx+1:03d}.png",
                            'base64_data': img_base64,
                            'caption': f"Image {idx+1}",
                            'context': ''  # TODO: Extract surrounding text
                        })

                except Exception as e:
                    print(f"⚠️  Could not extract image {idx+1}: {e}")

        return images

    def _create_chunks(self, text: str, chunk_size: int = 1000) -> List[Dict]:
        """
        Split text into chunks with headings

        Args:
            text: Full markdown text
            chunk_size: Approximate characters per chunk

        Returns:
            List of chunks with text and heading
        """
        chunks = []

        # Split by headings (## or ###)
        sections = re.split(r'(^#{2,3}\s+.+$)', text, flags=re.MULTILINE)

        current_heading = ""
        current_text = ""

        for section in sections:
            # Check if this is a heading
            if re.match(r'^#{2,3}\s+', section):
                # Save previous chunk if it exists
                if current_text.strip():
                    chunks.extend(
                        self._split_large_text(
                            current_text,
                            current_heading,
                            chunk_size
                        )
                    )

                # Update heading
                current_heading = section.replace('#', '').strip()
                current_text = ""
            else:
                current_text += section

        # Add last chunk
        if current_text.strip():
            chunks.extend(
                self._split_large_text(current_text, current_heading, chunk_size)
            )

        return chunks

    def _split_large_text(
        self,
        text: str,
        heading: str,
        chunk_size: int
    ) -> List[Dict]:
        """Split large text into smaller chunks while preserving context"""
        chunks = []
        text = text.strip()

        if not text:
            return chunks

        # If text is small enough, return as single chunk
        if len(text) <= chunk_size:
            chunks.append({
                'text': text,
                'heading': heading
            })
            return chunks

        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        current_chunk = ""

        for para in paragraphs:
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'heading': heading
                })
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        # Add remaining text
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'heading': heading
            })

        return chunks


def process_and_prepare(pdf_path: str, filename: str) -> Dict:
    """
    Convenience function to process PDF and prepare for Supabase storage

    Args:
        pdf_path: Path to PDF file
        filename: Original filename

    Returns:
        Dict ready for SupabaseManager.store_document()
    """
    processor = DocumentProcessor()
    result = processor.process_pdf(pdf_path)

    return {
        'filename': filename,
        'full_text': result['full_text'],
        'chunks': result['chunks'],
        'images': result['images']
    }
