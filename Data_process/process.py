# %%
import os
import re
import time
import shutil
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
# %%
load_dotenv()
BASE_DIR = Path(__file__).parent
MARKDOWN_DIR = BASE_DIR / "markdown"
CHROMA_DIR = BASE_DIR / "chroma_db"
EMBEDDING_API_BASE = os.getenv("EMBEDDING_API_BASE")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
CHUNK_SIZE = 350
CHUNK_OVERLAP = 50
HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
SECTION_NUM_PATTERN = re.compile(r"^(\d+(?:\.\d+)*(?:[a-z])?)\s", re.UNICODE)
# %%
def normalize_headers(text: str) -> str:
    lines = text.split("\n")
    result = []
    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if not m:
            result.append(line)
            continue
        title = m.group(2).strip()
        title_clean = re.sub(r"\s+", "", title)
        sm = SECTION_NUM_PATTERN.match(title_clean)
        if sm:
            section_num = sm.group(1)
            depth = section_num.count(".") + 1
            if depth > 3:
                depth = 3
            hashes = "#" * depth
            result.append(f"{hashes} {title}")
        else:
            result.append(f"# {title}")
    return "\n".join(result)
# %%
def load_markdown_files() -> list[Document]:
    docs = []
    md_files = sorted(MARKDOWN_DIR.glob("*.md"))
    if not md_files:
        print(f"markdown 目录中没有 .md 文件: {MARKDOWN_DIR}")
        return docs
    for f in md_files:
        content = f.read_text(encoding="utf-8")
        content = normalize_headers(content)
        docs.append(Document(page_content=content, metadata={"source": f.stem}))
    print(f"加载了 {len(docs)} 个 markdown 文件")
    return docs
# %%
HEADERS_TO_SPLIT_ON = [
    ("#", "Header1"),
    ("##", "Header2"),
    ("###", "Header3"),
]
def split_documents(docs: list[Document]) -> list[Document]:
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    all_splits = []
    for doc in docs:
        md_splits = md_splitter.split_text(doc.page_content)
        for split in md_splits:
            split.metadata.update(doc.metadata)
        char_splits = char_splitter.split_documents(md_splits)
        all_splits.extend(char_splits)
    print(f"共切分为 {len(all_splits)} 个文本块")
    return all_splits
# %%
def get_embeddings() -> OpenAIEmbeddings:
    kwargs = {}
    if EMBEDDING_API_BASE:
        kwargs["base_url"] = EMBEDDING_API_BASE
    if EMBEDDING_API_KEY:
        kwargs["api_key"] = EMBEDDING_API_KEY
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        check_embedding_ctx_length=False,
        chunk_size=10,
        max_retries=5,
        **kwargs,
    )
# %%
def index_documents(splits: list[Document]):
    embeddings = get_embeddings()
    if CHROMA_DIR.exists():
        print(f"检测到已有 Chroma 数据库: {CHROMA_DIR}，将删除并重建")
        shutil.rmtree(CHROMA_DIR)
    vector_store = Chroma(
        collection_name="license_knowledge",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    batch_size = 10
    total = len(splits)
    for i in range(0, total, batch_size):
        batch = splits[i : i + batch_size]
        for attempt in range(5):
            try:
                vector_store.add_documents(batch)
                break
            except Exception as e:
                if attempt < 4:
                    wait = 5 * (attempt + 1)
                    print(f"  批次 {i//batch_size + 1} 失败 ({e})，{wait}秒后重试...")
                    time.sleep(wait)
                else:
                    raise
        print(f"  已索引 {min(i + batch_size, total)}/{total}")
        if i + batch_size < total:
            time.sleep(1)
    count = vector_store._collection.count()
    print(f"索引完成，共存储 {count} 条向量")
# %%
def main():
    docs = load_markdown_files()
    if not docs:
        return
    splits = split_documents(docs)
    if not splits:
        print("切分结果为空，跳过索引")
        return
    index_documents(splits)
    print("全部完成")
# %%
if __name__ == "__main__":
    main()
