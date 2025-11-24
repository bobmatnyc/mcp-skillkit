"""Knowledge graph using NetworkX for relationship queries.

Design Decision: NetworkX DiGraph for Skill Relationships

Rationale: Use directed graph (DiGraph) to model skill dependencies
and relationships. Allows traversal for discovering related skills.

Graph Structure:
- Nodes: skill_id (with attributes: name, category, tags)
- Edges:
    - "depends_on" (from dependencies field)
    - "same_category" (skills in same category)
    - "shared_tag" (skills with common tags)

Trade-offs:
- Memory: In-memory graph vs. external graph database
- Speed: O(1) neighbor access vs. network latency
- Scalability: Limited to single-node memory vs. distributed

Alternatives Considered:
1. Neo4j: Rejected due to operational complexity for small datasets
2. SQLite with joins: Rejected due to poor graph traversal performance
3. Undirected graph: Rejected to preserve dependency direction

Extension Points: Can add graph persistence or Neo4j backend in future.
"""

import logging
from typing import TYPE_CHECKING

import networkx as nx

from mcp_skills.models.skill import Skill


if TYPE_CHECKING:
    from mcp_skills.services.skill_manager import SkillManager


logger = logging.getLogger(__name__)


class GraphStore:
    """Knowledge graph using NetworkX for relationship queries.

    This class manages a directed graph of skills and their relationships:
    - Dependencies (explicit)
    - Category similarity (implicit)
    - Tag overlap (implicit)

    Uses NetworkX DiGraph for efficient graph operations:
    - Node access: O(1)
    - Neighbor traversal: O(degree)
    - BFS traversal: O(n + e)

    Performance:
    - Add node: O(1)
    - Add edge: O(1)
    - Find neighbors: O(degree)
    - BFS traversal: O(n + e) where n=nodes, e=edges
    """

    def __init__(self) -> None:
        """Initialize NetworkX knowledge graph.

        Creates an empty directed graph for storing skill relationships.
        """
        self.graph = nx.DiGraph()
        logger.info("NetworkX knowledge graph initialized")

    def add_skill(self, skill: Skill) -> None:
        """Add skill node to graph.

        Creates a node with skill metadata. Does not create edges yet.

        Args:
            skill: Skill object to add as node

        Node Attributes:
        - name: Skill name
        - category: Skill category
        - tags: List of skill tags
        """
        try:
            self.graph.add_node(
                skill.id,
                name=skill.name,
                category=skill.category,
                tags=skill.tags,
            )
            logger.debug(f"Added skill node to graph: {skill.id}")

        except Exception as e:
            logger.error(f"Failed to add skill node {skill.id}: {e}")
            raise

    def add_relationships(
        self,
        skill: Skill,
        all_skills: list[Skill] | None = None,
    ) -> None:
        """Add edges for skill relationships.

        Extracts three types of relationships:
        1. Dependencies: Explicit "depends_on" from skill.dependencies
        2. Category relationships: "same_category" for shared categories
        3. Tag relationships: "shared_tag" for common tags

        Args:
            skill: Skill to extract relationships from
            all_skills: Optional list of all skills for relationship matching
                       (if None, uses existing graph nodes)

        Performance Note:
        - O(n) where n = number of existing skills for category/tag matching
        - Graph edges added lazily (only when target exists)
        """
        try:
            relationships = self.extract_relationships(skill, all_skills)

            for source_id, relation_type, target_id in relationships:
                # Only add edge if target node exists
                if target_id in self.graph:
                    self.graph.add_edge(
                        source_id, target_id, relation_type=relation_type
                    )

            logger.debug(
                f"Added {len(relationships)} relationships for skill: {skill.id}"
            )

        except Exception as e:
            logger.error(f"Failed to add relationships for {skill.id}: {e}")
            # Don't raise - allow graph building to continue

    def extract_relationships(
        self,
        skill: Skill,
        _all_skills: list[Skill] | None = None,
    ) -> list[tuple[str, str, str]]:
        """Identify skill dependencies and relationships.

        Extracts three types of relationships:
        1. Dependencies: Explicit "depends_on" from skill.dependencies
        2. Category relationships: "same_category" for shared categories
        3. Tag relationships: "shared_tag" for common tags

        Args:
            skill: Skill to extract relationships from
            all_skills: Optional list of all skills (if None, uses graph nodes)

        Returns:
            List of (source_id, relation_type, target_id) tuples

        Performance Note:
        - O(n) where n = number of existing skills for category/tag matching
        - Graph edges added lazily (only when target exists)
        """
        relationships: list[tuple[str, str, str]] = []

        # 1. Parse dependencies field
        for dep_id in skill.dependencies:
            relationships.append((skill.id, "depends_on", dep_id))

        # 2. Category relationships (same_category)
        # Find other skills in the same category
        for node_id, node_data in self.graph.nodes(data=True):
            if node_id != skill.id and node_data.get("category") == skill.category:
                # Bidirectional relationship for same category
                relationships.append((skill.id, "same_category", node_id))

        # 3. Tag-based relationships (shared_tag)
        # Find skills with overlapping tags
        skill_tags_set = set(skill.tags)
        for node_id, node_data in self.graph.nodes(data=True):
            if node_id == skill.id:
                continue

            node_tags = node_data.get("tags", [])
            shared_tags = skill_tags_set.intersection(set(node_tags))

            if shared_tags:
                # Bidirectional relationship for shared tags
                relationships.append((skill.id, "shared_tag", node_id))

        return relationships

    def find_related(
        self,
        skill_id: str,
        max_depth: int = 2,
    ) -> list[dict[str, float]]:
        """Find related skills via graph traversal.

        Uses BFS (breadth-first search) to find skills connected to
        the seed skill within max_depth hops.

        Args:
            skill_id: Starting skill ID for traversal
            max_depth: Maximum traversal depth

        Returns:
            List of dicts with skill_id and graph-based score

        Performance:
        - Time Complexity: O(n + e) for BFS traversal
        - Expected: <10ms for 1000 skills

        Scoring:
        - Direct neighbors (depth=1): score = 1.0
        - 2 hops away (depth=2): score = 0.5
        - 3 hops away (depth=3): score = 0.33

        Error Handling:
        - Skill not in graph → Return empty list
        - Graph traversal failure → Log error and return empty list
        """
        try:
            if skill_id not in self.graph:
                logger.warning(f"Skill not found in graph: {skill_id}")
                return []

            # BFS traversal from seed node
            visited_nodes = set()
            queue = [(skill_id, 0)]  # (node_id, depth)
            graph_results = []

            while queue:
                current_id, depth = queue.pop(0)

                if current_id in visited_nodes or depth > max_depth:
                    continue

                visited_nodes.add(current_id)

                # Skip the seed node itself
                if current_id != skill_id:
                    # Score based on inverse depth (closer = higher score)
                    score = 1.0 / depth
                    graph_results.append({"skill_id": current_id, "score": score})

                # Add neighbors to queue
                if depth < max_depth:
                    for neighbor in self.graph.neighbors(current_id):
                        if neighbor not in visited_nodes:
                            queue.append((neighbor, depth + 1))

            return graph_results

        except Exception as e:
            logger.error(f"Graph traversal failed for {skill_id}: {e}")
            return []

    def get_related_skills(
        self,
        skill_id: str,
        skill_manager: "SkillManager",
        max_depth: int = 2,
    ) -> list[Skill]:
        """Find related skills and load as Skill objects.

        Convenience method that combines graph traversal with skill loading.

        Args:
            skill_id: Starting skill ID
            skill_manager: SkillManager instance for loading skills
            max_depth: Maximum traversal depth

        Returns:
            List of related Skill objects

        Performance:
        - Time Complexity: O(n + e) for BFS + O(k) for loading k skills
        - Expected: <20ms for 1000 skills

        Example:
            >>> graph_store = GraphStore()
            >>> related = graph_store.get_related_skills(
            ...     "anthropics/pytest",
            ...     skill_manager,
            ...     max_depth=2
            ... )
            >>> related[0].name
            'pytest-fixtures'
        """
        try:
            if skill_id not in self.graph:
                logger.warning(f"Skill not found in graph: {skill_id}")
                return []

            # BFS traversal
            visited_nodes = set()
            queue = [(skill_id, 0)]  # (node_id, depth)
            related_ids = []

            while queue:
                current_id, depth = queue.pop(0)

                if current_id in visited_nodes or depth > max_depth:
                    continue

                visited_nodes.add(current_id)

                # Skip the starting node
                if current_id != skill_id:
                    related_ids.append(current_id)

                # Add neighbors to queue
                if depth < max_depth:
                    for neighbor in self.graph.neighbors(current_id):
                        if neighbor not in visited_nodes:
                            queue.append((neighbor, depth + 1))

            # Load Skill objects
            related_skills = []
            for related_id in related_ids:
                skill = skill_manager.load_skill(related_id)
                if skill:
                    related_skills.append(skill)

            return related_skills

        except Exception as e:
            logger.error(f"Failed to get related skills for {skill_id}: {e}")
            return []

    def clear(self) -> None:
        """Clear all nodes and edges from graph.

        Useful for reindexing operations.
        """
        try:
            node_count = self.graph.number_of_nodes()
            edge_count = self.graph.number_of_edges()
            self.graph.clear()
            logger.info(
                f"Cleared graph: {node_count} nodes, {edge_count} edges removed"
            )
        except Exception as e:
            logger.error(f"Failed to clear graph: {e}")
            raise

    def get_stats(self) -> dict[str, int]:
        """Get graph statistics.

        Returns:
            Dict with node and edge counts
        """
        try:
            return {
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
            }
        except Exception as e:
            logger.error(f"Failed to get graph stats: {e}")
            return {"nodes": 0, "edges": 0}
