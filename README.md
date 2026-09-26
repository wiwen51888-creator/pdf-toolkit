# pdf-toolkit

PDF 工具箱：合并、拆分、加水印、加密、提取文本。

## 安装

```bash
pip install -r requirements.txt
```

## 用法

```bash
# 合并多个 PDF
python pdf_tool.py merge a.pdf b.pdf c.pdf -o merged.pdf

# 拆分：每页一个文件
python pdf_tool.py split input.pdf --out-dir ./pages

# 提取指定页（1-3 页 + 第 5 页）
python pdf_tool.py split input.pdf --pages 1-3,5 --out-dir ./pages

# 加水印
python pdf_tool.py watermark input.pdf -t "机密" -o marked.pdf

# 提取文本
python pdf_tool.py extract input.pdf -o output.txt

# 加密
python pdf_tool.py encrypt input.pdf -p 123456 -o locked.pdf
```

## 子命令

- `merge`：合并多个 PDF
- `split`：拆分（支持按页范围）
- `watermark`：加文字水印
- `extract`：提取文本
- `encrypt`：加密（设置打开密码）