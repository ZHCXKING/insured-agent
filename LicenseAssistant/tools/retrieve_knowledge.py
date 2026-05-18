# %%
import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
# %%
class RetrieveKnowledgeInput(BaseModel):
    query: str = Field(..., description="搜索查询关键词，用于从保险考试知识库中检索相关内容")
# %%
_vector_store = None
# %%
def _get_vector_store() -> Chroma:
    global _vector_store
    if _vector_store is not None:
        return _vector_store
    chroma_dir = str(Path(__file__).resolve().parent.parent.parent / "Data_process" / "chroma_db")
    embedding_api_base = os.getenv("EMBEDDING_API_BASE")
    embedding_api_key = os.getenv("EMBEDDING_API_KEY")
    embedding_model = os.getenv("EMBEDDING_MODEL")
    kwargs = {}
    if embedding_api_base:
        kwargs["base_url"] = embedding_api_base
    if embedding_api_key:
        kwargs["api_key"] = embedding_api_key
    embeddings = OpenAIEmbeddings(model=embedding_model, check_embedding_ctx_length=False, **kwargs)
    _vector_store = Chroma(
        collection_name="license_knowledge",
        embedding_function=embeddings,
        persist_directory=chroma_dir,
    )
    return _vector_store
# %%
@tool(args_schema=RetrieveKnowledgeInput)
def retrieve_knowledge(**kwargs) -> str:
    """
    从保险考试知识库中检索与查询相关的内容。知识库包含：保险原理及实务、一般保险、长期保险、投资相连长期保险、旅游保险代理人考试资料，以及持牌保险中介人准则指引。当需要回答关于考试内容、保险法规、上牌要求等专业知识时使用此工具。
    """
    query = kwargs.get("query")
    vector_store = _get_vector_store()
    retrieved_docs = vector_store.similarity_search(query, k=5)
    if not retrieved_docs:
        return "未找到与查询相关的知识内容。"
    results = []
    for doc in retrieved_docs:
        source = doc.metadata.get("source", "未知来源")
        h1 = doc.metadata.get("Header1", "")
        h2 = doc.metadata.get("Header2", "")
        h3 = doc.metadata.get("Header3", "")
        section_parts = [p for p in [h1, h2, h3] if p]
        section = " > ".join(section_parts) if section_parts else ""
        entry = f"来源: {source}"
        if section:
            entry += f"\n章节: {section}"
        entry += f"\n内容: {doc.page_content}"
        results.append(entry)
    return "\n\n---\n\n".join(results)