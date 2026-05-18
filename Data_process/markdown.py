import os
from pathlib import Path
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_mineru import MinerULoader
# %%
load_dotenv()
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "markdown"
OUTPUT_DIR.mkdir(exist_ok=True)
TOKEN = os.getenv("MINERU_TOKEN")
TIMEOUT = int(os.getenv("MINERU_TIMEOUT", "1200"))
MAX_PAGES_PER_BATCH = 200
# %%
def get_page_count(file_path: Path) -> int:
    reader = PdfReader(str(file_path))
    return len(reader.pages)
# %%
def build_page_ranges(total_pages: int) -> list[str]:
    ranges = []
    for start in range(1, total_pages + 1, MAX_PAGES_PER_BATCH):
        end = min(start + MAX_PAGES_PER_BATCH - 1, total_pages)
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")
    return ranges
# %%
def convert_file(file_path: Path):
    print(f"正在解析: {file_path.name}")
    total_pages = get_page_count(file_path)
    print(f"  总页数: {total_pages}")
    if total_pages <= MAX_PAGES_PER_BATCH:
        loader = MinerULoader(
            source=str(file_path),
            mode="precision",
            token=TOKEN,
            language="ch",
            timeout=TIMEOUT,
        )
        docs = loader.load()
        md_content = "\n\n".join(doc.page_content for doc in docs)
    else:
        page_ranges = build_page_ranges(total_pages)
        print(f"  分 {len(page_ranges)} 批解析: {page_ranges}")
        all_contents = []
        for i, page_range in enumerate(page_ranges, 1):
            print(f"  第 {i}/{len(page_ranges)} 批: {page_range}")
            loader = MinerULoader(
                source=str(file_path),
                mode="precision",
                token=TOKEN,
                language="ch",
                pages=page_range,
                timeout=TIMEOUT,
            )
            docs = loader.load()
            all_contents.extend(doc.page_content for doc in docs)
        md_content = "\n\n".join(all_contents)
    output_path = OUTPUT_DIR / f"{file_path.stem}.md"
    output_path.write_text(md_content, encoding="utf-8")
    print(f"已保存: {output_path}")
# %%
def main():
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"data 目录中没有 PDF 文件: {DATA_DIR}")
        return
    for f in pdf_files:
        convert_file(f)
    print(f"完成，共处理 {len(pdf_files)} 个文件")
# %%
if __name__ == "__main__":
    main()