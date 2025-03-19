# PDF to Markdown Converter

A tool to convert PDF files to Markdown format with embedded images, using PyMuPDF and pymupdf4llm.

## Features

- Convert single PDF files to markdown with images
- Batch process multiple PDF files
- Supports recursive directory processing
- Parallel processing for faster batch conversion
- Detailed logging

## Requirements

- Python 3.6+
- PyMuPDF (fitz)
- pymupdf4llm

Install dependencies:

```bash
pip install -r requirements.txt
```

## Available Scripts

- `fixed_pdf2md.py`: Converts a single PDF file to markdown with images
- `batch_pdf2md.py`: Converts multiple PDF files in a directory

## Usage

### Convert a Single PDF

```bash
python3 ./fixed_pdf2md.py /path/to/your.pdf [output_directory]
```

### Convert Multiple PDFs

```bash
python3 ./batch_pdf2md.py /path/to/pdfs -o output_directory -r
```

Options:
- `-o`, `--output`: Specify output directory (default: input-markdown)
- `-r`, `--recursive`: Process subdirectories recursively
- `-d`, `--debug`: Enable debug logging
- `-w`, `--workers`: Number of worker processes for parallel conversion

## Output

The conversion creates a directory with:
- A markdown file with the same name as the PDF
- An "images" subdirectory containing extracted images

## Logging

Batch conversion progress is logged to `batch_pdf2md.log`