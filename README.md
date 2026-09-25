# Wolf's PDF Compactor

Batch-compress PDFs by rasterizing every page into a JPEG at a controlled resolution and quality. Folder of 25 GB of scanned PDFs? This typically cuts it by **~80%**, from ~250 MB down to ~45 MB per file, while keeping pages perfectly readable.

```
Turma da Mônica Jovem Edição 34.pdf    203.3 MB  ->   42.7 MB
Turma da Mônica Jovem Edição 56.pdf    226.1 MB  ->   44.3 MB
...
Total                                21.8  GB  ->  4.4 GB   (-80%)
```

## Why does it work so well?

The input PDFs are usually just scanned images. This tool re-encodes each page:

1. Renders the page at a sensible size (**max 1800 px** per side by default, no need for huge 4000 px scans).
2. Encodes it as a **JPEG** (quality 62 by default).
3. Rebuilds a new PDF with the same page dimensions but dramatically smaller files.

## Requirements

- Python 3.9+
- [PyMuPDF](https://pypi.org/project/PyMuPDF/) (`pip install pymupdf`)

No other dependencies, no Ghostscript needed.

## Installation

```bash
# 1. Clone / download this repository
git clone https://github.com/IsmarWolf/WolfsPDFCompactor.git
cd WolfsPDFCompactor

# 2. (Recommended) create a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Quick Start

1. Put the PDFs you want to compress inside the `pastaorigem` folder.
2. Run the tool:

```bash
python compactadorpdf.py
```

3. Grab the compressed PDFs from the `pastacompactada` folder.

That's it. Files already compressed in a previous run are **skipped automatically**, so you can re-run safely.

## Configuration

Easiest way: edit the values at the top of `compactadorpdf.py`:

| Constant | Default | What it does |
|---|---|---|
| `INPUT_DIR` | `pastaorigem` | Folder with the PDFs to compress |
| `OUTPUT_DIR` | `pastacompactada` | Where compressed PDFs are saved |
| `MAX_DPI` | `150` | Max render resolution (dots per inch) |
| `MAX_PAGE_SIDE` | `1800` | Max page size in pixels — the main size/quality lever |
| `JPEG_QUALITY` | `62` | JPEG quality (1 = smallest, 100 = best) |
| `MAX_WORKERS` | `8` | How many PDFs are processed at the same time |

These same values can also be passed as command-line options (they override the file):

```bash
# Custom folders and a lighter compression
python compactadorpdf.py --input my/pdfs --output out --dpi 120 --quality 55

# Smaller pages = even smaller files
python compactadorpdf.py --max-page-side 1400 --quality 50

# Compress only specific files (#34, and #50 through #99)
python compactadorpdf.py --numbers 34 50-99

# See everything
python compactadorpdf.py --help
```

### Full CLI reference

```
--input PATH            input folder with the PDFs   (default: pastaorigem)
--output PATH           output folder                 (default: pastacompactada)
--dpi N                 max render resolution in DPI  (default: 150)
--max-page-side N       max page dimension in pixels  (default: 1800)
--quality N             JPEG quality 1-100            (default: 62)
--workers N             files in parallel             (default: 8)
--numbers N...          only files ending in these numbers, e.g. 34 50-99
```

## Folder layout

```
wolfs-pdf-compactor/
├── compactadorpdf.py     <- the tool
├── requirements.txt
├── README.md
├── pastaorigem/          <- drop your PDFs here (not committed to git)
└── pastacompactada/      <- compressed PDFs land here (not committed to git)
```

## Tuning tips

- **Bigger reduction** → lower `--max-page-side` (e.g. `1400`) or `--quality` (e.g. `50`).
- **Better quality** → raise them (`--max-page-side 2200 --quality 75`).
- The tool **never writes a file larger than the original** — if a PDF can't be reduced it is skipped.
- Output files keep the same page dimensions as the input, so no layout surprises.

Happy compressing!