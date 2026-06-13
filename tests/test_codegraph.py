"""
CodeGraph Tests for AI Agent Benchmark system.

This module contains test cases specifically for CodeGraph / graph algorithm
analysis, including graph model detection, NetworkX code detection, and
architecture analysis capabilities.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.code_analyzer import CodeAnalyzer, CodeIssue


# ======================================================================
#  Graph Algorithm Analysis Tests
# ======================================================================
class TestGraphAlgorithmDetection:
    """Test detection of graph algorithm patterns in Python code."""

    @pytest.mark.asyncio
    async def test_detect_bfs_code(self):
        """Test BFS algorithm detection."""
        analyzer = CodeAnalyzer()

        code = '''
from collections import deque

def bfs(graph, start):
    """广度优先搜索"""
    visited = set()
    queue = deque([start])
    visited.add(start)
    order = []

    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("BFS" in i for i in ids)

    @pytest.mark.asyncio
    async def test_detect_dfs_code(self):
        """Test DFS algorithm detection."""
        analyzer = CodeAnalyzer()

        code = '''
def dfs(graph, node, visited=None):
    """深度优先搜索"""
    if visited is None:
        visited = set()
    visited.add(node)
    result = [node]
    for neighbor in graph[node]:
        if neighbor not in visited:
            result.extend(dfs(graph, neighbor, visited))
    return result
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("DFS" in i for i in ids)

    @pytest.mark.asyncio
    async def test_detect_dijkstra_code(self):
        """Test Dijkstra algorithm detection."""
        analyzer = CodeAnalyzer()

        code = '''
import heapq

def dijkstra(graph, start):
    """Dijkstra 最短路径算法"""
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_dist, current_node = heapq.heappop(priority_queue)
        if current_dist > distances[current_node]:
            continue
        for neighbor, weight in graph[current_node].items():
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    return distances
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("DIJKSTRA" in i for i in ids)

    @pytest.mark.asyncio
    async def test_detect_topological_sort(self):
        """Test topological sort detection."""
        analyzer = CodeAnalyzer()

        code = '''
def topological_sort(graph):
    """拓扑排序"""
    in_degree = {u: 0 for u in graph}
    for u in graph:
        for v in graph[u]:
            in_degree[v] = in_degree.get(v, 0) + 1

    queue = [u for u in in_degree if in_degree[u] == 0]
    order = []

    while queue:
        u = queue.pop(0)
        order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(order) != len(graph):
        raise ValueError("Graph contains a cycle")
    return order
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("TOPO" in i for i in ids)

    @pytest.mark.asyncio
    async def test_detect_cycle_warning(self):
        """Test cycle detection in graph algorithms."""
        analyzer = CodeAnalyzer()

        code = '''
def floyd_warshall(n, edges):
    """Floyd-Warshall 全源最短路径"""
    dist = [[float('inf')] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = w
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("FLOYD" in i for i in ids)


# ======================================================================
#  NetworkX Detection Tests
# ======================================================================
class TestNetworkXDetection:
    """Test detection of NetworkX related code patterns."""

    @pytest.mark.asyncio
    async def test_detect_networkx_import(self):
        """Test NetworkX import detection."""
        analyzer = CodeAnalyzer()

        code = '''
import networkx as nx
from networkx import Graph, shortest_path

def analyze_citation_network():
    G = nx.Graph()
    G.add_edge("Paper_A", "Paper_B")
    G.add_edge("Paper_B", "Paper_C")
    path = nx.shortest_path(G, "Paper_A", "Paper_C")
    return path
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category in ("graph_algorithm", "dependency")]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("NETWORKX_IMPORT" in i for i in ids)

    @pytest.mark.asyncio
    async def test_detect_networkx_digraph(self):
        """Test NetworkX DiGraph detection."""
        analyzer = CodeAnalyzer()

        code = '''
import networkx as nx

def build_dependency_graph():
    G = nx.DiGraph()
    G.add_node("module_a")
    G.add_node("module_b")
    G.add_edge("module_a", "module_b")
    return G
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("NX_DIGRAPH" in i for i in ids)

    @pytest.mark.asyncio
    async def test_detect_pagerank(self):
        """Test PageRank detection."""
        analyzer = CodeAnalyzer()

        code = '''
import networkx as nx

def compute_pagerank(G):
    pr = nx.pagerank(G, alpha=0.85)
    return pr
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        ids = [i.id for i in graph_issues]
        assert any("NX_PAGERANK" in i for i in ids)
        # PageRank should trigger a warning for large graphs
        pagerank_issues = [i for i in graph_issues if "NX_PAGERANK" in i.id]
        assert pagerank_issues[0].severity == "warning"

    @pytest.mark.asyncio
    async def test_detect_betweenness_centrality(self):
        """Test betweenness centrality detection."""
        analyzer = CodeAnalyzer()

        code = '''
import networkx as nx

def find_important_nodes(G):
    bc = nx.betweenness_centrality(G)
    return sorted(bc.items(), key=lambda x: x[1], reverse=True)
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        ids = [i.id for i in graph_issues]
        assert any("NX_BETWEENNESS" in i for i in ids)

    @pytest.mark.asyncio
    async def test_detect_mst(self):
        """Test minimum spanning tree detection."""
        analyzer = CodeAnalyzer()

        code = '''
import networkx as nx

def find_minimum_spanning_tree(G):
    mst = nx.minimum_spanning_tree(G, algorithm="kruskal")
    return mst
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        ids = [i.id for i in graph_issues]
        assert any("NX_MST" in i for i in ids)


# ======================================================================
#  Graph Model / Architecture Detection Tests
# ======================================================================
class TestGraphModelDetection:
    """Test detection of graph model structures and architecture."""

    @pytest.mark.asyncio
    async def test_detect_adjacency_matrix(self):
        """Test adjacency matrix detection."""
        analyzer = CodeAnalyzer()

        code = '''
class Graph:
    """使用邻接矩阵表示的图"""
    def __init__(self, num_vertices):
        self.num_vertices = num_vertices
        self.adj = [[0] * num_vertices for _ in range(num_vertices)]

    def add_edge(self, u, v, weight=1):
        self.adj[u][v] = weight
        self.adj[v][u] = weight

    def get_neighbors(self, vertex):
        return [i for i in range(self.num_vertices) if self.adj[vertex][i] != 0]
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("ADJ_MATRIX" in i or "GRAPH_MUTATION" in i or "GRAPH_QUERY" in i for i in ids)
        # Adjacency matrix should trigger a warning
        matrix_issues = [i for i in graph_issues if "ADJ_MATRIX" in i.id]
        if matrix_issues:
            assert matrix_issues[0].severity == "warning"

    @pytest.mark.asyncio
    async def test_detect_adjacency_list(self):
        """Test adjacency list detection."""
        analyzer = CodeAnalyzer()

        code = '''
class Graph:
    """使用邻接表表示的图"""
    def __init__(self):
        self.adj = {}

    def add_edge(self, u, v):
        if u not in self.adj:
            self.adj[u] = []
        if v not in self.adj:
            self.adj[v] = []
        self.adj[u].append(v)
        self.adj[v].append(u)

    def neighbors(self, vertex):
        return self.adj.get(vertex, [])
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("GRAPH_MUTATION" in i or "GRAPH_QUERY" in i for i in ids)

    @pytest.mark.asyncio
    async def test_detect_graph_class_definition(self):
        """Test graph class definition detection."""
        analyzer = CodeAnalyzer()

        code = '''
class DependencyGraph:
    """项目依赖关系图"""
    def __init__(self):
        self.edges = []

    def add_dependency(self, module_a, module_b):
        self.edges.append((module_a, module_b))

    def topological_order(self):
        pass
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("GRAPH_CLASS" in i for i in ids)

    @pytest.mark.asyncio
    async def test_detect_node_class(self):
        """Test node model class detection."""
        analyzer = CodeAnalyzer()

        code = '''
class TreeNode:
    """二叉树节点"""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("NODE_CLASS" in i for i in ids)


# ======================================================================
#  Java Graph Algorithm Tests
# ======================================================================
class TestJavaGraphAlgorithm:
    """Test graph algorithm detection in Java code."""

    @pytest.mark.asyncio
    async def test_detect_java_bfs(self):
        """Test BFS detection in Java code."""
        analyzer = CodeAnalyzer()

        code = '''
import java.util.*;

public class GraphBFS {
    public List<Integer> bfs(Map<Integer, List<Integer>> graph, int start) {
        Set<Integer> visited = new HashSet<>();
        Queue<Integer> queue = new LinkedList<>();
        List<Integer> order = new ArrayList<>();

        queue.add(start);
        visited.add(start);

        while (!queue.isEmpty()) {
            int vertex = queue.poll();
            order.add(vertex);
            for (int neighbor : graph.get(vertex)) {
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor);
                    queue.add(neighbor);
                }
            }
        }
        return order;
    }
}
'''
        result = await analyzer.analyze(code, "java")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("JAVA_BFS" in i for i in ids)

    @pytest.mark.asyncio
    async def test_detect_java_adj_list(self):
        """Test adjacency list detection in Java code."""
        analyzer = CodeAnalyzer()

        code = '''
import java.util.*;

public class Graph {
    private Map<Integer, List<Integer>> adjacency;

    public Graph() {
        this.adjacency = new HashMap<>();
    }

    public void addEdge(int u, int v) {
        adjacency.computeIfAbsent(u, k -> new ArrayList<>()).add(v);
        adjacency.computeIfAbsent(v, k -> new ArrayList<>()).add(u);
    }

    public List<Integer> neighbors(int vertex) {
        return adjacency.getOrDefault(vertex, Collections.emptyList());
    }
}
'''
        result = await analyzer.analyze(code, "java")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) > 0
        ids = [i.id for i in graph_issues]
        assert any("JAVA_ADJ_LIST" in i for i in ids)


# ======================================================================
#  Integration Tests — Mixed Graph Code
# ======================================================================
class TestGraphCodeIntegration:
    """Integration tests for complex graph code scenarios."""

    @pytest.mark.asyncio
    async def test_analyze_complex_graph_module(self):
        """Test analysis of a complex graph module."""
        analyzer = CodeAnalyzer()

        code = '''
import networkx as nx
import heapq
from collections import deque

class CodeGraph:
    """代码知识图谱"""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.adjacency = {}

    def add_class_node(self, class_name, file_path):
        self.graph.add_node(class_name, type="class", file=file_path)

    def add_method_edge(self, caller, callee, call_count=1):
        self.graph.add_edge(caller, callee, weight=call_count)

    def find_shortest_path(self, source, target):
        return nx.shortest_path(self.graph, source, target)

    def compute_pagerank(self):
        return nx.pagerank(self.graph)

    def find_cycles(self):
        return list(nx.simple_cycles(self.graph))

    def get_communities(self):
        return nx.community.greedy_modularity_communities(self.graph.to_undirected())

    def analyze_complexity(self):
        bc = nx.betweenness_centrality(self.graph)
        return sorted(bc.items(), key=lambda x: x[1], reverse=True)[:10]

    def bfs_traversal(self, start):
        visited = set()
        queue = deque([start])
        visited.add(start)
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in self.graph.successors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return result
'''
        result = await analyzer.analyze(code, "python")
        # Collect both graph_algorithm and dependency category issues
        graph_issues = [i for i in result.issues if i.category in ("graph_algorithm", "dependency")]

        # Should detect multiple graph patterns
        assert len(graph_issues) >= 3
        ids = [i.id for i in graph_issues]

        # Should detect NetworkX import and various features
        assert any("NETWORKX_IMPORT" in i for i in ids)
        assert any("NX_DIGRAPH" in i for i in ids)
        assert any("BFS" in i for i in ids)

    @pytest.mark.asyncio
    async def test_empty_code_no_graph_issues(self):
        """Test that simple code without graph patterns has no graph issues."""
        analyzer = CodeAnalyzer()

        code = '''
def add(a, b):
    return a + b

class SimpleClass:
    def __init__(self):
        self.value = 0
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
        assert len(graph_issues) == 0

    @pytest.mark.asyncio
    async def test_graph_issue_line_numbers(self):
        """Test that graph issues have correct line numbers."""
        analyzer = CodeAnalyzer()

        code = '''
import networkx as nx

def analyze_graph():
    G = nx.DiGraph()
    G.add_edge("a", "b")
    return nx.pagerank(G)
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]

        for issue in graph_issues:
            assert issue.line_number is not None
            assert issue.line_number > 0

    @pytest.mark.asyncio
    async def test_graph_issue_suggestions(self):
        """Test that graph issues have helpful suggestions."""
        analyzer = CodeAnalyzer()

        code = '''
import networkx as nx

def compute_pagerank(G):
    return nx.pagerank(G)
'''
        result = await analyzer.analyze(code, "python")
        graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]

        # At least one issue should have a suggestion
        issues_with_suggestions = [i for i in graph_issues if i.suggestion]
        assert len(issues_with_suggestions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
