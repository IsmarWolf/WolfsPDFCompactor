# PDF Compactor

A simple batch tool for reducing PDF file size by re-encoding scanned or image-heavy pages as JPEGs at a controlled resolution.

This project is useful when you have large PDFs made mostly of scanned documents, forms, reports, or handwritten pages. The script keeps the page layout and readability while shrinking the file size significantly.

Typical results vary by document type, but image-heavy PDFs often shrink by 50% to 90% without major quality loss.

## What it does

The script works by:

1. Opening each PDF page.
2. Rendering it at a limited size and DPI.
3. Saving the page as a JPEG with a chosen quality.
4. Rebuilding the PDF with the same page dimensions.

This is especially effective for scanned documents, where pages are basically images rather than text-heavy vector content.

## Features

- Batch compression of all PDFs in a folder
- Output folder for compressed files
- Skips files that are already compact enough
- Supports custom DPI, page size, and JPEG quality
- Can process a subset of files by numeric suffix
- Uses parallel workers to speed up larger batches

## Requirements

- Python 3.9+
- [PyMuPDF](https://pypi.org/project/PyMuPDF/)

Install the dependency with:

```bash
pip install -r requirements.txt
```

## Installation

```bash
# Clone or download the repository
git clone <repository-url>
cd Compactador

# Optional but recommended
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Quick start

1. Put the PDFs you want to compress inside the `source_pdfs` folder.
2. Run:

```bash
python compactadorpdf.py
```

3. The compressed files will be created in `compressed_pdfs`.

The script skips files that were already compressed in a previous run, so it is safe to run multiple times.

## Examples

```bash
# Process every PDF in the default input folder
python compactadorpdf.py

# Use custom folders
python compactadorpdf.py --input ./incoming --output ./compressed

# Reduce size more aggressively
python compactadorpdf.py --dpi 120 --quality 55 --max-page-side 1400

# Only process files ending with specific numbers
python compactadorpdf.py --numbers 12 15-20

# Show the full command-line help
python compactadorpdf.py --help
```

## Configuration

You can adjust the defaults directly in the script or pass values from the command line.

| Setting | Default | Purpose |
|---|---:|---|
| `INPUT_DIR` | `source_pdfs` | Folder containing PDFs to compress |
| `OUTPUT_DIR` | `compressed_pdfs` | Folder where compressed PDFs are saved |
| `MAX_DPI` | `150` | Maximum rendering resolution |
| `MAX_PAGE_SIDE` | `1800` | Maximum page width or height in pixels |
| `JPEG_QUALITY` | `62` | JPEG quality (lower = smaller, higher = better quality) |
| `MAX_WORKERS` | `8` | Number of files processed in parallel |

### CLI options

```bash
--input PATH            input folder with the PDFs     (default: source_pdfs)
--output PATH           output folder                  (default: compressed_pdfs)
--dpi N                 max render resolution in DPI   (default: 150)
--max-page-side N       max page dimension in pixels   (default: 1800)
--quality N             JPEG quality 1-100             (default: 62)
--workers N             files processed in parallel    (default: 8)
--numbers N...          only process matching file names, e.g. 12 15-20
```

## Typical usage scenarios

This tool works well for:

- scanned contracts and invoices
- PDF reports exported from scanners
- archive folders containing image-based documents
- reducing large document sets without buying special software

## Folder layout

```text
Compactador/
├── compactadorpdf.py
├── requirements.txt
├── README.md
├── source_pdfs/
└── compressed_pdfs/
```

- `source_pdfs` is where you place the original PDFs.
- `compressed_pdfs` is where the compressed versions are written.

## Tips

- Lower `--max-page-side` or `--quality` for stronger compression.
- Raise them when you want a sharper final result.
- The script does not keep an output file if it is not actually smaller than the original.
- Output pages keep the same dimensions as the original, which helps preserve layout.

## License

This project is provided as-is for local use and personal workflows. If you are publishing or distributing it publicly, check the repository license before using it in a formal project environment.

## Summary

If your PDFs are mostly scanned pages, this tool is a practical way to shrink them without needing a heavy desktop application or external dependencies beyond PyMuPDF.