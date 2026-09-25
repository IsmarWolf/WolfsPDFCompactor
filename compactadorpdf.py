#!/usr/bin/env python3
"""
Wolf's PDF Compactor
====================

Batch-compress PDFs by rasterizing each page into a JPEG at a controlled
resolution and quality. Typically reduces file size by ~80% while keeping
the pages perfectly readable.

Examples
--------
    # Compress every PDF in the input folder
    python compactadorpdf.py

    # Use your own folders and settings
    python compactadorpdf.py --input my/pdfs --output out --dpi 130 --quality 60

    # Only process files ending with these numbers (from 01 to 100)
    python compactadorpdf.py --numbers 34 50-99

    # See all options
    python compactadorpdf.py --help
"""

import argparse
import concurrent.futures
import re
import sys
from pathlib import Path

import pymupdf

# =====================================================================
# CONFIGURATION
# ---------------------------------------------------------------------
# Edit these values directly... or override them from the command line
# (see `python compactadorpdf.py --help`). Values below are the defaults.
# =====================================================================
INPUT_DIR = Path("source_pdfs")       # folder containing the PDFs to compress
OUTPUT_DIR = Path("compressed_pdfs")  # folder where compressed PDFs are saved
MAX_DPI = 150                 # max render resolution in dots per inch
MAX_PAGE_SIDE = 1800          # max page dimension in pixels; balances quality vs size
JPEG_QUALITY = 62             # JPEG quality: 1 = smallest, 100 = best
MAX_WORKERS = 8               # number of PDFs processed in parallel
# =====================================================================


def configurar_saida_padrao():
    """Force UTF-8 output so emojis/messages work on any Windows console."""
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def comprimir_pdf_pymupdf(caminho_entrada, caminho_saida, max_dpi, max_pagina_lado, qualidade):
    """Rebuild a PDF from rasterized JPEG pages.

    Each page is rendered at a scale computed from MAX_DPI and MAX_PAGE_SIDE,
    encoded as a JPEG, and placed on a page with the original dimensions.
    """
    documento_origem = pymupdf.open(caminho_entrada)
    documento_destino = pymupdf.open()
    try:
        for pagina in documento_origem:
            lado_longo = max(pagina.rect.width, pagina.rect.height)
            escala = min(max_dpi / 72.0, max_pagina_lado / lado_longo)
            pixmap = pagina.get_pixmap(
                matrix=pymupdf.Matrix(escala, escala),
                alpha=False,
                colorspace=pymupdf.csRGB,
            )
            imagem_jpeg = pixmap.tobytes("jpeg", jpg_quality=qualidade)

            pagina_nova = documento_destino.new_page(
                width=pagina.rect.width, height=pagina.rect.height
            )
            pagina_nova.insert_image(pagina_nova.rect, stream=imagem_jpeg)
            pixmap = None  # free memory early

        documento_destino.save(
            caminho_saida,
            garbage=4,
            deflate=True,
            clean=True,
            pretty=True,
        )
    finally:
        documento_origem.close()
        documento_destino.close()


def comprimir_pdf(caminho_entrada, pasta_saida, max_dpi, max_pagina_lado, qualidade):
    """Compress a single PDF. Returns (file_name, status)."""
    nome_arquivo = caminho_entrada.name
    caminho_saida = pasta_saida / nome_arquivo

    # Skip files already compressed in a previous run.
    if caminho_saida.exists() and caminho_saida.stat().st_size < caminho_entrada.stat().st_size:
        return nome_arquivo, "pulado"

    try:
        comprimir_pdf_pymupdf(caminho_entrada, caminho_saida, max_dpi, max_pagina_lado, qualidade)

        # Never keep an output that is bigger than the input.
        if caminho_saida.exists() and caminho_saida.stat().st_size >= caminho_entrada.stat().st_size:
            caminho_saida.unlink(missing_ok=True)
            raise RuntimeError("PDF de saída maior que o original — arquivo descartado")
        return nome_arquivo, "ok"
    except Exception as exc:
        print(f"  [ERRO] {nome_arquivo}: {exc}")
        return nome_arquivo, "erro"


def interpretar_numeros(tokens):
    """Turn CLI tokens like ['34', '50-99'] into a set of edition numbers."""
    numeros = set()
    for token in tokens:
        if "-" in token:
            inicio, fim = token.split("-", maxsplit=1)
            numeros.update(range(int(inicio), int(fim) + 1))
        else:
            numeros.add(int(token))
    return numeros


def main():
    configurar_saida_padrao()

    parser = argparse.ArgumentParser(
        prog="compactadorpdf",
        description="Wolf's PDF Compactor — reduce PDF file size in batch.",
    )
    parser.add_argument("--input", type=Path, default=INPUT_DIR,
                        help=f"input folder with the PDFs (default: {INPUT_DIR})")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR,
                        help=f"output folder (default: {OUTPUT_DIR})")
    parser.add_argument("--dpi", type=float, default=MAX_DPI,
                        help=f"max render resolution in DPI (default: {MAX_DPI})")
    parser.add_argument("--max-page-side", type=int, default=MAX_PAGE_SIDE,
                        help=f"max page dimension in pixels (default: {MAX_PAGE_SIDE})")
    parser.add_argument("--quality", type=int, default=JPEG_QUALITY,
                        help=f"JPEG quality 1-100 (default: {JPEG_QUALITY})")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS,
                        help=f"files processed in parallel (default: {MAX_WORKERS})")
    parser.add_argument("--numbers", nargs="+", metavar="N",
                        help="process only files whose name ends with these numbers, "
                             "e.g. --numbers 34 50-99")
    args = parser.parse_args()

    pasta_origem = args.input
    pasta_destino = args.output

    if not pasta_origem.exists() or not pasta_origem.is_dir():
        parser.exit(1, f"[ERRO] A pasta de entrada '{pasta_origem}' não existe.\n")

    pasta_destino.mkdir(parents=True, exist_ok=True)

    arquivos_pdf = sorted(pasta_origem.glob("*.pdf"))
    if args.numbers:
        numeros = interpretar_numeros(args.numbers)
        arquivos_pdf = [
            p for p in arquivos_pdf
            if int(re.search(r"(\d+)\.pdf$", p.name).group(1)) in numeros
        ]

    total = len(arquivos_pdf)
    if total == 0:
        print("Nenhum PDF encontrado na pasta de entrada.")
        return

    print(f"Processando {total} arquivo(s)...")
    print(f"  Entrada : {pasta_origem}")
    print(f"  Saída   : {pasta_destino}")
    print(f"  DPI     : {args.dpi} | Lado máx: {args.max_page_side} px | JPEG: {args.quality}")
    if args.numbers:
        print(f"  Filtro  : edições {sorted(interpretar_numeros(args.numbers))}")
    print("-" * 50)

    concluidos = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futuros = {
            executor.submit(
                comprimir_pdf, pdf, pasta_destino, args.dpi, args.max_page_side, args.quality
            ): pdf
            for pdf in arquivos_pdf
        }

        for futuro in concurrent.futures.as_completed(futuros):
            nome, status = futuro.result()
            concluidos += 1
            origem = futuros[futuro]

            if status == "pulado":
                print(f"[{concluidos}/{total}] SKIP  {nome} (já compactado)")
            elif status == "ok":
                tam_orig = origem.stat().st_size / (1024 * 1024)
                tam_novo = (pasta_destino / nome).stat().st_size / (1024 * 1024)
                print(f"[{concluidos}/{total}] OK    {nome} | {tam_orig:7.1f} MB -> {tam_novo:6.1f} MB")
            else:
                print(f"[{concluidos}/{total}] FAIL  {nome}")

    print("-" * 50)
    print("Concluído!")


if __name__ == "__main__":
    main()