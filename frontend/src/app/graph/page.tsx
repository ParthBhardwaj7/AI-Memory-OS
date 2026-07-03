"use client";

import { useEffect, useState } from "react";
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType
} from "reactflow";
import "reactflow/dist/style.css";
import { Brain, RefreshCw } from "lucide-react";
import { memoryApi } from "@/lib/api";

export default function MemoryGraphPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);

  // TODO IMPLEMENTATION STEPS FOR DEVELOPER 2:
  // 1. Fetch graph data containing `{ nodes, edges }` using `memoryApi.getGraph()`.
  // 2. Set node parameters, node styles, and edge arrow configurations.
  // 3. (Optional) Implement custom node components (e.g. Node for PDF, Node for Topic).

  const fetchGraphData = async () => {
    setLoading(true);
    try {
      const res = await memoryApi.getGraph("default-user");
      if (res.status === "success") {
        // Format edges with standard markers (arrows) if desired
        const formattedEdges = res.edges.map((edge: any) => ({
          ...edge,
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 15,
            height: 15,
            color: "#6366f1",
          },
          style: { stroke: "#475569" }
        }));
        
        // Add styling properties to nodes
        const formattedNodes = res.nodes.map((node: any) => ({
          ...node,
          style: {
            background: "#0f172a",
            color: "#f8fafc",
            border: "1px solid #334155",
            borderRadius: "12px",
            padding: "10px",
            fontWeight: "600",
            fontSize: "12px",
            boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
          }
        }));

        setNodes(formattedNodes);
        setEdges(formattedEdges);
      }
    } catch (err) {
      console.error("Failed to load graph data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphData();
  }, []);

  return (
    <div className="flex flex-col h-screen p-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-4 mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-teal-100 border border-teal-200 text-teal-700 rounded-lg">
            <Brain className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Memory Knowledge Graph</h1>
            <p className="text-xs text-slate-500">Visual mapping of cognitive connections extracted by Cognee</p>
          </div>
        </div>
        
        <button
          onClick={fetchGraphData}
          disabled={loading}
          className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-white hover:bg-blue-50 border border-slate-200 text-xs font-semibold text-slate-900 transition-colors duration-200"
        >
          <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Graph</span>
        </button>
      </div>

      {/* Canvas Area */}
      <div className="flex-1 bg-slate-50 border border-slate-200 rounded-2xl overflow-hidden relative">
        {loading ? (
          <div className="absolute inset-0 bg-white/95 flex items-center justify-center space-x-2 text-teal-700 text-sm font-semibold z-10">
            <span className="h-4 w-4 border-2 border-teal-700 border-t-transparent rounded-full animate-spin"></span>
            <span>Loading cognitive relationships...</span>
          </div>
        ) : nodes.length === 0 ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500 space-y-2 z-10">
            <Brain className="h-12 w-12 text-slate-700" />
            <p className="font-semibold text-sm">No memory nodes ingested yet.</p>
          </div>
        ) : null}

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          minZoom={0.5}
          maxZoom={1.5}
        >
          <Controls className="bg-white border border-slate-200 rounded text-slate-900 fill-slate-900" />
          <MiniMap 
            nodeColor="#0f766e"
            maskColor="rgba(255, 255, 255, 0.85)"
            className="bg-white border border-slate-200 rounded"
          />
          <Background color="#334155" gap={16} />
        </ReactFlow>
      </div>
    </div>
  );
}
