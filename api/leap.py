"""
LEAP API - AI-based LEAP Framework Categorization
Endpoint: /api/leap
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import categorize_leap_content

def categorize_leap(markdown_path, pdf_name, output_folder='output'):
    """
    Categorize markdown content into LEAP framework phases

    Args:
        markdown_path: Path to the markdown file (relative to project root)
        pdf_name: Name of the PDF (without extension)
        output_folder: Output directory (default: 'output')

    Returns:
        dict with LEAP file paths
    """
    # Get absolute paths
    project_root = Path(__file__).parent.parent
    full_markdown_path = project_root / markdown_path
    full_output_path = project_root / output_folder

    if not full_markdown_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    print(f"📊 Categorizing into LEAP framework: {pdf_name}")

    # Read the markdown content
    with open(full_markdown_path, 'r', encoding='utf-8') as f:
        full_text = f.read()

    # Count images (estimate from markdown)
    image_count = full_text.count('![Image')

    # Generate LEAP categorized files
    leap_files = categorize_leap_content(
        full_text,
        str(full_output_path),
        pdf_name,
        image_count
    )

    # Return relative paths
    leap_files_rel = {}
    for phase, file_path in leap_files.items():
        leap_files_rel[phase] = str(Path(file_path).relative_to(project_root))

    return {
        'success': True,
        'pdf_name': pdf_name,
        'leap_files': leap_files_rel,
        'phases': list(leap_files.keys())
    }
