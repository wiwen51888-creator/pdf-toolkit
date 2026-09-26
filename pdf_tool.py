#!/usr/bin/env python
"""PDF 工具箱：合并 / 拆分 / 水印 / 提取文本 / 加密。"""

import argparse
import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def parse_pages(spec: str, total: int) -> list[int]:
    """解析 "1-3,5" 形式的页码，返回 0-based 索引列表。"""
    result: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            result.extend(range(int(a) - 1, int(b)))
        elif part:
            result.append(int(part) - 1)
    return [i for i in result if 0 <= i < total]


def cmd_merge(args) -> int:
    writer = PdfWriter()
    for f in args.inputs:
        reader = PdfReader(f)
        for page in reader.pages:
            writer.add_page(page)
    out = args.output or "merged.pdf"
    with open(out, "wb") as fh:
        writer.write(fh)
    print(f"已合并 {len(args.inputs)} 个文件 -> {out}")
    return 0


def cmd_split(args) -> int:
    reader = PdfReader(args.input)
    out_dir = Path(args.out_dir or "pages")
    out_dir.mkdir(parents=True, exist_ok=True)
    indices = parse_pages(args.pages, len(reader.pages)) if args.pages else range(len(reader.pages))
    count = 0
    for i in indices:
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        target = out_dir / f"page_{i + 1:03d}.pdf"
        with open(target, "wb") as fh:
            writer.write(fh)
        count += 1
    print(f"已拆分 {count} 页 -> {out_dir}")
    return 0


def cmd_watermark(args) -> int:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as rl_canvas

    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    c.setFont("Helvetica", 40)
    c.setFillGray(0.5, 0.3)
    c.saveState()
    c.translate(300, 400)
    c.rotate(45)
    c.drawCentredString(0, 0, args.text)
    c.restoreState()
    c.save()
    buf.seek(0)
    watermark = PdfReader(buf).pages[0]

    reader = PdfReader(args.input)
    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(watermark)
        writer.add_page(page)
    out = args.output or "watermarked.pdf"
    with open(out, "wb") as fh:
        writer.write(fh)
    print(f"已加水印 -> {out}")
    return 0


def cmd_extract(args) -> int:
    reader = PdfReader(args.input)
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    text = "\n\n".join(parts)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"已提取文本 -> {args.output}")
    else:
        print(text)
    return 0


def cmd_encrypt(args) -> int:
    reader = PdfReader(args.input)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(args.password)
    out = args.output or "encrypted.pdf"
    with open(out, "wb") as fh:
        writer.write(fh)
    print(f"已加密 -> {out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="PDF 工具箱")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("merge", help="合并 PDF")
    p.add_argument("inputs", nargs="+")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_merge)

    p = sub.add_parser("split", help="拆分 PDF")
    p.add_argument("input")
    p.add_argument("--pages", help="页码，如 1-3,5")
    p.add_argument("--out-dir")
    p.set_defaults(func=cmd_split)

    p = sub.add_parser("watermark", help="加水印")
    p.add_argument("input")
    p.add_argument("-t", "--text", required=True)
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_watermark)

    p = sub.add_parser("extract", help="提取文本")
    p.add_argument("input")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("encrypt", help="加密")
    p.add_argument("input")
    p.add_argument("-p", "--password", required=True)
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_encrypt)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())