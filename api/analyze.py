"""
Analyze API - PDF to Text Conversion Only
Endpoint: /api/analyze
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import process_pdf_to_markdown

def analyze_pdf(pdf_path, output_folder='output'):
    """
    Analyze PDF and convert to text/markdown (without LEAP categorization)

    Args:
        pdf_path: Path to the PDF file (relative to project root)
        output_folder: Output directory (default: 'output')

    Returns:
        dict with analysis results
    """
    # Get absolute paths
    project_root = Path(__file__).parent.parent
    full_pdf_path = project_root / pdf_path
    full_output_path = project_root / output_folder

    if not full_pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Extract PDF name
    pdf_name = full_pdf_path.stem

    print(f"🔬 Analyzing: {pdf_name}.pdf")

    # Process without LEAP categorization
    result = process_pdf_to_markdown(
        str(full_pdf_path),
        str(full_output_path),
        pdf_name,
        enable_leap=False  # Skip LEAP categorization
    )

    # Return relative paths
    markdown_rel = Path(result['markdown_file']).relative_to(project_root)

    return {
        'success': True,
        'pdf_name': pdf_name,
        'markdown_path': str(markdown_rel),
        'markdown_name': Path(result['markdown_file']).name,
        'image_count': result['image_count'],
        'images_folder': str(Path(result['images_folder']).relative_to(project_root))
    }
