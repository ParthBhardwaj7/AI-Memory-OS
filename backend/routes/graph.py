from fastapi import APIRouter, HTTPException
from services.cognee_service import CogneeService

router = APIRouter()

@router.get("/{user_id}")
async def get_graph(user_id: str):
    """
    GET /graph/{user_id}
    
    TODO IMPLEMENTATION STEPS:
    1. Query Cognee graph database engine or memory space using `CogneeService.get_graph_data(user_id)`.
    2. Extract entities (nodes) and relations (edges).
    3. Transform the entities and relations into React Flow compatible format:
       Nodes: [{"id": "node_1", "data": {"label": "Resume"}, "position": {"x": 100, "y": 100}}]
       Edges: [{"id": "edge_1", "source": "node_1", "target": "node_2", "label": "mentions"}]
    4. Return the nodes and edges array.
    """
    try:
        # graph_data = CogneeService.get_graph_data(user_id)
        
        # Mock react-flow graph data representing a basic knowledge graph
        mock_nodes = [
            {"id": "user", "type": "input", "data": {"label": "User Memory OS"}, "position": {"x": 250, "y": 0}},
            {"id": "doc1", "data": {"label": "Resume.pdf"}, "position": {"x": 100, "y": 150}},
            {"id": "topic1", "data": {"label": "Software Engineer"}, "position": {"x": 50, "y": 300}},
            {"id": "doc2", "data": {"label": "Meeting Notes"}, "position": {"x": 400, "y": 150}},
            {"id": "topic2", "data": {"label": "FastAPI Refactor"}, "position": {"x": 450, "y": 300}}
        ]
        
        mock_edges = [
            {"id": "e1-1", "source": "user", "target": "doc1", "label": "uploaded"},
            {"id": "e1-2", "source": "user", "target": "doc2", "label": "uploaded"},
            {"id": "e2-1", "source": "doc1", "target": "topic1", "label": "mentions role"},
            {"id": "e2-2", "source": "doc2", "target": "topic2", "label": "discusses"}
        ]
        
        return {
            "status": "success",
            "nodes": mock_nodes,
            "edges": mock_edges
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
