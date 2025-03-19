#!/usr/bin/env python3
"""
Fixed PDF to Markdown converter using PyMuPDF and pymupdf4llm
"""

import sys
import os
import fitz
from pathlib import Path
import shutil

# Check if pymupdf4llm is available
try:
    from pymupdf4llm import to_markdown
    print("Successfully imported pymupdf4llm")
except ImportError:
    print("pymupdf4llm not found. Please install it with: pip install pymupdf4llm")
    sys.exit(1)

def convert_pdf(pdf_path, output_dir=None):
    """
    Convert a PDF file to markdown with images
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"PDF file not found: {pdf_path}")
        return False
    
    # Create output directory
    if output_dir is None:
        output_dir = pdf_path.parent / f"{pdf_path.stem}-fixed-markdown"
    else:
        output_dir = Path(output_dir)
    
    images_dir = output_dir / "images"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    output_md_path = output_dir / f"{pdf_path.stem}.md"
    log_path = output_dir / "conversion.log"
    
    print(f"Converting {pdf_path} to {output_md_path}")
    
    with open(log_path, "w") as log:
        log.write(f"Converting {pdf_path} to {output_md_path}\n")
        
        try:
            # Open the PDF
            doc = fitz.open(pdf_path)
            log.write(f"Successfully opened PDF with {len(doc)} pages\n")
            
            # Now use to_markdown with the correct parameters
            log.write("Converting to markdown with pymupdf4llm...\n")
            
            # Based on the function signature check, we need to use:
            # write_images=True, image_path="images", and make sure it returns a string
            md_content = to_markdown(
                doc,
                write_images=True,
                image_path=str(images_dir),
                image_format="png",
                show_progress=True
            )
            
            log.write("Conversion successful\n")
            log.write(f"Writing markdown to {output_md_path}\n")
            
            with open(output_md_path, "w") as f:
                f.write(md_content)
            
            log.write("Successfully wrote markdown content\n")
            
            # Count the number of images extracted
            image_count = len(list(images_dir.glob("*.png")))
            log.write(f"Number of images extracted: {image_count}\n")
            
            # Close the document
            doc.close()
            
            print(f"Successfully converted {pdf_path} to markdown")
            print(f"Output: {output_md_path}")
            print(f"Number of images extracted: {image_count}")
            return True
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            log.write(f"{error_msg}\n")
            import traceback
            log.write(traceback.format_exc())
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fixed_pdf2md.py <pdf_file> [output_directory]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_pdf(pdf_path, output_dir)
    if not success:
        sys.exit(1)