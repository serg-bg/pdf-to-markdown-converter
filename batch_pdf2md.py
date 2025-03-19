#!/usr/bin/env python3
"""
Batch PDF to Markdown converter using PyMuPDF and pymupdf4llm
"""

import sys
import os
import fitz
from pathlib import Path
import concurrent.futures
import argparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("batch_pdf2md.log")
    ]
)
logger = logging.getLogger(__name__)

# Check if pymupdf4llm is available
try:
    from pymupdf4llm import to_markdown
    logger.info("Successfully imported pymupdf4llm")
except ImportError:
    logger.error("pymupdf4llm not found. Please install it with: pip install pymupdf4llm")
    sys.exit(1)

def convert_pdf(pdf_path, output_dir=None, debug=False):
    """
    Convert a single PDF file to markdown with images
    """
    if debug:
        logger.setLevel(logging.DEBUG)
    
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        return False
    
    # Create output directory
    if output_dir is None:
        output_dir = pdf_path.parent / f"{pdf_path.stem}-markdown"
    else:
        output_dir = Path(output_dir)
    
    images_dir = output_dir / "images"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    output_md_path = output_dir / f"{pdf_path.stem}.md"
    
    logger.info(f"Converting {pdf_path} to {output_md_path}")
    
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        logger.debug(f"Successfully opened PDF with {len(doc)} pages")
        
        # Use to_markdown with the correct parameters
        md_content = to_markdown(
            doc,
            write_images=True,
            image_path=str(images_dir),
            image_format="png",
            show_progress=True
        )
        
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        # Count the number of images extracted
        image_count = len(list(images_dir.glob("*.png")))
        
        # Close the document
        doc.close()
        
        logger.info(f"Successfully converted {pdf_path.name} to markdown with {image_count} images")
        return True
    
    except Exception as e:
        logger.error(f"Error converting {pdf_path.name}: {str(e)}")
        if debug:
            import traceback
            logger.debug(traceback.format_exc())
        return False

def process_directory(directory_path, output_base_dir=None, recursive=True, debug=False, max_workers=None):
    """
    Process all PDFs in a directory
    """
    directory_path = Path(directory_path)
    
    if not directory_path.exists() or not directory_path.is_dir():
        logger.error(f"Directory not found: {directory_path}")
        return
    
    if output_base_dir is None:
        output_base_dir = directory_path.with_name(f"{directory_path.name}-markdown")
    else:
        output_base_dir = Path(output_base_dir)
    
    # Create output base directory
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Collect all PDF files
    pdf_files = []
    
    if recursive:
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_path = Path(root) / file
                    # Determine relative path from the input directory
                    rel_path = pdf_path.relative_to(directory_path)
                    # Construct output directory
                    out_dir = output_base_dir / rel_path.parent / pdf_path.stem
                    pdf_files.append((pdf_path, out_dir))
    else:
        for file in directory_path.glob("*.pdf"):
            out_dir = output_base_dir / file.stem
            pdf_files.append((file, out_dir))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {directory_path}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Determine the number of workers
    if max_workers is None:
        max_workers = min(32, os.cpu_count() + 4)
    
    logger.info(f"Using {max_workers} workers for parallel processing")
    
    # Process files in parallel
    success_count = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_pdf = {
            executor.submit(convert_pdf, pdf_path, out_dir, debug): pdf_path
            for pdf_path, out_dir in pdf_files
        }
        
        for future in concurrent.futures.as_completed(future_to_pdf):
            pdf_path = future_to_pdf[future]
            try:
                success = future.result()
                if success:
                    success_count += 1
            except Exception as e:
                logger.error(f"Exception processing {pdf_path}: {str(e)}")
    
    logger.info(f"Processed {success_count} of {len(pdf_files)} PDF files successfully")
    return success_count

def main():
    parser = argparse.ArgumentParser(description="Convert PDF files to markdown with images")
    parser.add_argument("input", help="PDF file or directory containing PDFs")
    parser.add_argument("-o", "--output", help="Output directory (defaults to input-markdown)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Process subdirectories recursively")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("-w", "--workers", type=int, help="Number of worker processes")
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    input_path = Path(args.input)
    
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        convert_pdf(input_path, args.output, args.debug)
    elif input_path.is_dir():
        process_directory(input_path, args.output, args.recursive, args.debug, args.workers)
    else:
        logger.error(f"Invalid input: {input_path}. Must be a PDF file or directory containing PDFs.")
        sys.exit(1)

if __name__ == "__main__":
    main()