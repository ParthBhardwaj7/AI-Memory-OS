from fastapi import APIRouter, HTTPException
from services.cognee_service import CogneeService

router = APIRouter()

@router.get("/{user_id}")
async def get_graph(user_id: str):
    """
    GET /graph/{user_id}
    Retrieves knowledge graph nodes and edges for React Flow rendering in the frontend.
    """
    try:
        graph_data = await CogneeService.get_graph_data(user_id)
        if not graph_data:
            raise Exception("Failed to retrieve or compile cognitive graph data.")
            
        return {
            "status": "success",
            "nodes": graph_data.get("nodes", []),
            "edges": graph_data.get("edges", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
