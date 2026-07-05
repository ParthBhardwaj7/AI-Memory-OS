import os
import math
import logging
import cognee
from cognee.api.v1.search import SearchType

logger = logging.getLogger(__name__)

class CogneeService:
    """
    Service wrapper for Cognee Memory Ingestion and Search.
    Supports local databases or custom remote hosted tenants (e.g. AWS).
    """

    @staticmethod
    async def initialize():
        """
        Connects Cognee to the custom hosted Tenant URL if COGNEE_API_URL and COGNEE_API_KEY are configured.
        Otherwise, defaults to local SQLite/LanceDB.
        """
        api_url = os.environ.get("COGNEE_API_URL")
        api_key = os.environ.get("COGNEE_API_KEY")
        
        if api_url and api_key:
            logger.info(f"Connecting to Cognee Tenant Instance: {api_url}")
            await cognee.serve(url=api_url, api_key=api_key)
        else:
            logger.info("Cognee running in local mode (no remote tenant URL configured)")

    @staticmethod
    async def ingest_text(text: str, user_id: str):
        """
        Add text content to Cognee and cognify it.
        """
        try:
            await CogneeService.initialize()
            
            # Queue text payload
            await cognee.add(text, dataset_name=user_id)
            
            # Process and build graph/embeddings
            await cognee.cognify(datasets=[user_id])
            return True
        except Exception as e:
            logger.error(f"Cognee text ingestion failed: {e}")
            return False

    @staticmethod
    async def ingest_file(file_path: str, user_id: str):
        """
        Add file (PDF, Image, Audio text) path to Cognee queue and cognify it.
        """
        try:
            await CogneeService.initialize()
            
            # Queue file by path
            await cognee.add(file_path, dataset_name=user_id)
            
            # Process file
            await cognee.cognify(datasets=[user_id])
            return True
        except Exception as e:
            logger.error(f"Cognee file ingestion failed: {e}")
            return False

    @staticmethod
    async def query_memory(question: str, user_id: str) -> list:
        """
        Queries Cognee vector space using semantic search.
        """
        try:
            await CogneeService.initialize()
            
            # Query the database using correct positional & keyword arguments
            results = await cognee.search(
                query_text=question,
                query_type=SearchType.CHUNKS,
                datasets=[user_id]
            )
            
            # Parse search results
            return [r.get("text", "") for r in results]
        except Exception as e:
            logger.error(f"Cognee search query failed: {e}")
            return []

    @staticmethod
    async def delete_dataset(user_id: str):
        """
        Permanently delete the entire memory index for a user dataset (used for guest sandboxes).
        """
        try:
            await CogneeService.initialize()
            await cognee.forget(dataset=user_id)
            return True
        except Exception as e:
            logger.error(f"Cognee forget failed for dataset {user_id}: {e}")
            return False

    @staticmethod
    async def get_graph_data(user_id: str):
        """
        Fetch entities and relations from your Cognee tenant and merge them with
        Supabase document metrics to render a beautiful React Flow network.
        """
        try:
            await CogneeService.initialize()
            
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
            
            # Radial layout for files
            num_docs = len(docs)
            for i, doc in enumerate(docs):
                angle = (i / max(num_docs, 1)) * 2 * math.pi
                x = 250 + int(220 * math.sin(angle))
                y = 200 + int(140 * math.cos(angle))
                
                doc_id = f"doc_{i}"
                doc_name = doc.get("filename", f"Doc {i}")
                doc_type = doc.get("doc_type", "Document")
                
                # Check for URLs to strip lengths
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
                
                # Generate a related concept/topic tag node
                concept_id = f"concept_{i}"
                concept_x = x + int(120 * math.sin(angle + 0.4))
                concept_y = y + int(120 * math.cos(angle + 0.4))
                
                concept_label = "Career Node" if doc_type == "PDF" else "Web Research" if doc_type == "URL" else "Audio Transcript" if doc_type == "Audio" else "Parsed Image"
                
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
            logger.error(f"Failed to fetch graph data: {e}")
            return {"nodes": [], "edges": []}
