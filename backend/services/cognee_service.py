import os
import sys
import platform

# Cognee storage path: env var takes priority (Render injects /tmp/cognee_system),
# otherwise detect OS and use appropriate default
if not os.environ.get("SYSTEM_ROOT_DIRECTORY"):
    if platform.system() == "Windows":
        os.environ["SYSTEM_ROOT_DIRECTORY"] = "C:/Users/parth/.cognee_system"
        os.environ["DATA_ROOT_DIRECTORY"] = "C:/Users/parth/.cognee_system/data"
    else:
        os.environ["SYSTEM_ROOT_DIRECTORY"] = "/tmp/cognee_system"
        os.environ["DATA_ROOT_DIRECTORY"] = "/tmp/cognee_system/data"

import math
import logging
import cognee
from cognee.api.v1.search import SearchType

logger = logging.getLogger(__name__)

# --- One-time initialization flag ---
_cognee_initialized = False

async def _ensure_initialized():
    """
    Configure Cognee LLM + Embedding providers from environment variables.
    This runs once per process lifetime.
    """
    global _cognee_initialized
    if _cognee_initialized:
        return

    llm_api_key       = os.environ.get("LLM_API_KEY", "")
    llm_endpoint      = os.environ.get("LLM_ENDPOINT", "https://openrouter.ai/api/v1")
    llm_model         = os.environ.get("LLM_MODEL", "google/gemini-2.5-flash")

    emb_api_key       = os.environ.get("EMBEDDING_API_KEY", llm_api_key)
    emb_provider      = os.environ.get("EMBEDDING_PROVIDER", "custom")
    emb_endpoint      = os.environ.get("EMBEDDING_ENDPOINT", "https://openrouter.ai/api/v1")
    emb_model         = os.environ.get("EMBEDDING_MODEL", "openai/text-embedding-3-small")
    emb_dimensions    = int(os.environ.get("EMBEDDING_DIMENSIONS", "1536"))

    # For LiteLLM custom OpenAI-compatible endpoints, non-OpenAI models must be prefixed with 'openai/'
    if llm_model.startswith("openrouter/"):
        llm_model = llm_model.replace("openrouter/", "openai/", 1)
    elif not llm_model.startswith("openai/"):
        llm_model = f"openai/{llm_model}"

    # Keep the openrouter/ prefix intact for embeddings so LiteLLM routes correctly to OpenRouter provider
    pass

    try:
        # Configure LLM provider
        cognee.config.set_llm_config({
            "llm_provider": "openai",          # openai-compatible interface
            "llm_model": llm_model,
            "llm_endpoint": llm_endpoint,
            "llm_api_key": llm_api_key,
            "llm_instructor_mode": "tool_call",
            "llm_args": {
                "max_tokens": 4000
            }
        })

        # Configure Embedding provider
        cognee.config.set_embedding_config({
            "embedding_provider": emb_provider,
            "embedding_model": emb_model,
            "embedding_endpoint": emb_endpoint,
            "embedding_api_key": emb_api_key,
            "embedding_dimensions": emb_dimensions,
        })

        _cognee_initialized = True
        logger.info(f"[Cognee] Initialized — LLM: {llm_model} | Embedding: {emb_model}")
    except Exception as e:
        logger.error(f"[Cognee] Initialization failed: {e}")
        raise


class CogneeService:
    """
    Service wrapper for Cognee Memory Ingestion and Search.
    Uses local SQLite + LanceDB (built into cognee package).
    LLM & Embedding calls go via OpenRouter.
    """

    @staticmethod
    async def ingest_text(text: str, user_id: str) -> bool:
        """
        Add plain text to Cognee and build the knowledge graph for a user.
        """
        try:
            await _ensure_initialized()
            logger.info(f"[Cognee] ingest_text | user={user_id!r} | chars={len(text)}")

            sanitized_user_id = user_id.replace(".", "_").replace(" ", "_").replace("@", "_")
            await cognee.add(text, dataset_name=sanitized_user_id)
            await cognee.cognify(datasets=[sanitized_user_id])

            logger.info(f"[Cognee] ingest_text SUCCESS | user={user_id!r}")
            return True
        except Exception as e:
            logger.error(f"[Cognee] ingest_text FAILED | user={user_id!r} | error={e}")
            return False

    @staticmethod
    async def ingest_file(file_path: str, user_id: str) -> bool:
        """
        Add a file (PDF etc.) to Cognee and build the knowledge graph.
        """
        try:
            await _ensure_initialized()
            logger.info(f"[Cognee] ingest_file | user={user_id!r} | path={file_path!r}")

            sanitized_user_id = user_id.replace(".", "_").replace(" ", "_").replace("@", "_")
            await cognee.add(file_path, dataset_name=sanitized_user_id)
            await cognee.cognify(datasets=[sanitized_user_id])

            logger.info(f"[Cognee] ingest_file SUCCESS | user={user_id!r}")
            return True
        except Exception as e:
            logger.error(f"[Cognee] ingest_file FAILED | user={user_id!r} | error={e}")
            return False

    @staticmethod
    async def query_memory(question: str, user_id: str) -> list:
        """
        Semantic search over the user's memory chunks stored in Cognee.
        Returns a list of relevant text snippets.
        """
        try:
            await _ensure_initialized()
            logger.info(f"[Cognee] query_memory | user={user_id!r} | question={question!r}")

            sanitized_user_id = user_id.replace(".", "_").replace(" ", "_").replace("@", "_")
            results = await cognee.search(
                query_text=question,
                query_type=SearchType.CHUNKS,
                datasets=[sanitized_user_id]
            )

            logger.info(f"[Cognee] query_memory returned {len(results)} raw results | user={user_id!r}")

            # Robustly parse whatever Cognee returns (dict, object, or string)
            parsed = []
            for r in results:
                if isinstance(r, dict):
                    text = (
                        r.get("text")
                        or r.get("chunk_text")
                        or r.get("content")
                        or str(r)
                    )
                elif hasattr(r, "text"):
                    text = r.text
                elif hasattr(r, "chunk_text"):
                    text = r.chunk_text
                else:
                    text = str(r)

                text = (text or "").strip()
                if text:
                    parsed.append(text)

            logger.info(f"[Cognee] query_memory parsed {len(parsed)} chunks | user={user_id!r}")
            return parsed

        except Exception as e:
            logger.error(f"[Cognee] query_memory FAILED | user={user_id!r} | error={e}")
            return []

    @staticmethod
    async def delete_dataset(user_id: str) -> bool:
        """
        Wipe all memory for a user dataset (used for guest sandbox cleanup).
        """
        try:
            await _ensure_initialized()
            sanitized_user_id = user_id.replace(".", "_").replace(" ", "_").replace("@", "_")
            await cognee.forget(dataset=sanitized_user_id)
            logger.info(f"[Cognee] Deleted dataset for user={user_id!r}")
            return True
        except Exception as e:
            logger.error(f"[Cognee] delete_dataset FAILED | user={user_id!r} | error={e}")
            return False

    @staticmethod
    async def get_graph_data(user_id: str) -> dict:
        """
        Fetch documents from Supabase and build a React Flow-compatible graph.
        """
        try:
            from db.supabase import supabase
            res = supabase.table("documents").select("filename, doc_type").eq("user_id", user_id).execute()
            docs = res.data or []

            # Root brain node
            nodes = [
                {
                    "id": "root_brain",
                    "type": "input",
                    "data": {"label": "🧠 Memory Core (Cognee)"},
                    "position": {"x": 250, "y": 20}
                }
            ]
            edges = []

            num_docs = len(docs)
            for i, doc in enumerate(docs):
                angle = (i / max(num_docs, 1)) * 2 * math.pi
                x = 250 + int(220 * math.sin(angle))
                y = 200 + int(140 * math.cos(angle))

                doc_id = f"doc_{i}"
                doc_name = doc.get("filename", f"Doc {i}")
                doc_type = doc.get("doc_type", "Document")

                if len(doc_name) > 30:
                    doc_name = doc_name[:27] + "..."

                nodes.append({
                    "id": doc_id,
                    "data": {"label": f"📄 {doc_type}: {doc_name}"},
                    "position": {"x": x, "y": y}
                })
                edges.append({
                    "id": f"e_root_{doc_id}",
                    "source": "root_brain",
                    "target": doc_id,
                    "label": "ingested"
                })

                concept_id = f"concept_{i}"
                concept_x = x + int(120 * math.sin(angle + 0.4))
                concept_y = y + int(120 * math.cos(angle + 0.4))
                concept_label = (
                    "Career Node" if doc_type == "PDF"
                    else "Web Research" if doc_type == "URL"
                    else "Audio Transcript" if doc_type == "Audio"
                    else "Parsed Image"
                )
                nodes.append({
                    "id": concept_id,
                    "data": {"label": f"🏷️ {concept_label}"},
                    "position": {"x": concept_x, "y": concept_y}
                })
                edges.append({
                    "id": f"e_concept_{i}",
                    "source": doc_id,
                    "target": concept_id,
                    "label": "classifies"
                })

            return {"nodes": nodes, "edges": edges}
        except Exception as e:
            logger.error(f"[Cognee] get_graph_data FAILED | user={user_id!r} | error={e}")
            return {"nodes": [], "edges": []}
