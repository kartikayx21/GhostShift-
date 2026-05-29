"""Supply Chain Graph — in-memory graph builder for supply chain visualization."""

import json
from pathlib import Path


class SupplyChainGraph:
    """Builds and queries an in-memory supply chain graph."""

    def __init__(self):
        self.nodes: list[dict] = []
        self.edges: list[dict] = []

    def build_from_scenario(self, scenario: dict) -> "SupplyChainGraph":
        """Build graph from a pre-loaded mock scenario."""
        graph_data = scenario.get("supply_chain_graph", {})
        self.nodes = graph_data.get("nodes", [])
        self.edges = graph_data.get("edges", [])
        return self

    def build_from_findings(self, brand: str, product: str, findings: dict) -> "SupplyChainGraph":
        """Build graph dynamically from investigation findings."""
        # Brand node
        self.add_node(brand.lower().replace(" ", "_"), "brand", brand, "verified", "green")
        # Product node
        prod_id = f"{product.lower().replace(' ', '_')}"
        self.add_node(prod_id, "product", product, "genuine", "green")
        self.add_edge(brand.lower().replace(" ", "_"), prod_id, "MANUFACTURES")

        # Add supplier nodes from component data
        component_data = findings.get("component_tracer", {})
        for supplier in component_data.get("suppliers", []):
            sid = supplier.get("id", supplier.get("name", "").lower().replace(" ", "_"))
            self.add_node(sid, "supplier", supplier.get("name", ""), "verified", "green")
            self.add_edge(sid, brand.lower().replace(" ", "_"), "SUPPLIES_TO", supplier.get("component", ""))

        # Add suspicious factory nodes
        factory_data = findings.get("factory_spy", {})
        for factory in factory_data.get("factories", []):
            fid = factory.get("id", factory.get("name", "").lower().replace(" ", "_"))
            score = factory.get("suspicion_score", 0.5)
            color = "red" if score > 0.6 else "yellow" if score > 0.3 else "green"
            status = "suspicious" if score > 0.3 else "verified"
            self.add_node(fid, "factory", factory.get("name", ""), status, color)

        # Add listing nodes from hunter data
        hunter_data = findings.get("hunter", {})
        for listing in hunter_data.get("suspicious_listings", []):
            lid = listing.get("id", f"listing_{listing.get('platform', 'unknown')}")
            self.add_node(lid, "listing", listing.get("title", "")[:30], "counterfeit", "red")

        return self

    def add_node(self, node_id: str, node_type: str, name: str,
                 status: str = "unknown", color: str = "yellow") -> None:
        """Add a node to the graph."""
        if not any(n["id"] == node_id for n in self.nodes):
            self.nodes.append({
                "id": node_id,
                "type": node_type,
                "name": name,
                "status": status,
                "color": color,
            })

    def add_edge(self, from_id: str, to_id: str, relation: str,
                 label: str = "", suspicious: bool = False) -> None:
        """Add an edge between two nodes."""
        self.edges.append({
            "from": from_id,
            "to": to_id,
            "relation": relation,
            "label": label,
            "suspicious": suspicious,
        })

    def get_graph_data(self) -> dict:
        """Return the full graph as serializable dict."""
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "suspicious_nodes": sum(1 for n in self.nodes if n["color"] in ("red", "yellow")),
                "suspicious_edges": sum(1 for e in self.edges if e.get("suspicious", False)),
            },
        }

    def find_suspicious_paths(self) -> list[dict]:
        """Find paths from suspicious nodes to verified nodes (contamination routes)."""
        paths = []
        suspicious_nodes = {n["id"] for n in self.nodes if n["color"] in ("red", "yellow")}
        verified_nodes = {n["id"] for n in self.nodes if n["color"] == "green"}

        # Simple BFS to find suspicious → verified paths
        adjacency: dict[str, list[dict]] = {}
        for edge in self.edges:
            adjacency.setdefault(edge["from"], []).append(edge)
            adjacency.setdefault(edge["to"], []).append({**edge, "from": edge["to"], "to": edge["from"]})

        for start in suspicious_nodes:
            visited = {start}
            queue = [(start, [start])]
            while queue:
                current, path = queue.pop(0)
                if current in verified_nodes and current != start:
                    paths.append({
                        "path": path,
                        "start_node": start,
                        "end_node": current,
                        "length": len(path),
                        "risk": "high" if len(path) <= 3 else "medium",
                    })
                    continue
                for edge in adjacency.get(current, []):
                    next_node = edge["to"]
                    if next_node not in visited:
                        visited.add(next_node)
                        queue.append((next_node, path + [next_node]))

        return paths

    def get_node(self, node_id: str) -> dict | None:
        """Get a node by ID."""
        return next((n for n in self.nodes if n["id"] == node_id), None)
