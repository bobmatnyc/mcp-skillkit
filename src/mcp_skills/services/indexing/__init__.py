"""Indexing services for skills (vector + graph hybrid RAG).

This package provides a hybrid search architecture combining:
- Vector similarity search (ChromaDB)
- Knowledge graph relationships (NetworkX)

Public API:
- IndexingEngine: Main orchestration class
- VectorStore: ChromaDB vector operations
- GraphStore: NetworkX graph operations
- HybridSearcher: Result combination logic
- ScoredSkill: Search result dataclass
- IndexStats: Index statistics dataclass

Example Usage:
    >>> from mcp_skills.services.indexing import IndexingEngine
    >>> engine = IndexingEngine(skill_manager=manager)
    >>> stats = engine.reindex_all(force=True)
    >>> results = engine.search("python testing", top_k=5)
"""

from mcp_skills.services.indexing.engine import IndexingEngine, IndexStats
from mcp_skills.services.indexing.graph_store import GraphStore
from mcp_skills.services.indexing.hybrid_search import HybridSearcher, ScoredSkill
from mcp_skills.services.indexing.vector_store import VectorStore


__all__ = [
    "IndexingEngine",
    "VectorStore",
    "GraphStore",
    "HybridSearcher",
    "ScoredSkill",
    "IndexStats",
]
