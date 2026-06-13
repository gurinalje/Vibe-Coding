"""
CodeGraph 分析演示 -- AI Agent Benchmark
演示如何使用 AI Agent Benchmark 对图算法、知识图谱、架构分析代码进行深度审查
"""

import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.code_analyzer import CodeAnalyzer
from core.security_scanner import SecurityScanner
from core.refactoring_engine import RefactoringEngine
from core.performance_analyzer import PerformanceAnalyzer
from core.report_generator import ReportGenerator, ReportFormat


def print_header(title):
    # type: (str) -> None
    """打印标题"""
    print("\n" + "=" * 70)
    print("  " + title)
    print("=" * 70)


def print_section(title):
    # type: (str) -> None
    """打印章节"""
    print("\n--- " + title + " ---")


# ======================================================================
#  示例代码片段 (使用普通字符串避免三引号嵌套问题)
# ======================================================================

CODEGRAPH_SNIPPET = (
    "import networkx as nx\n"
    "from collections import deque\n"
    "import heapq\n"
    "\n"
    "\n"
    "class CodeGraph:\n"
    "    # 代码知识图谱\n"
    "    def __init__(self):\n"
    "        self.graph = nx.DiGraph()\n"
    "        self.index = {}\n"
    "\n"
    "    def add_file(self, file_path, module_name):\n"
    '        self.graph.add_node(module_name, type="module", file=file_path)\n'
    '        self.index[module_name] = {"type": "module", "file": file_path}\n'
    "\n"
    "    def add_class(self, class_name, parent_module):\n"
    '        self.graph.add_node(class_name, type="class")\n'
    '        self.graph.add_edge(parent_module, class_name, relation="contains")\n'
    "\n"
    "    def add_method(self, method_name, parent_class):\n"
    '        self.graph.add_node(method_name, type="method")\n'
    '        self.graph.add_edge(parent_class, method_name, relation="defines")\n'
    "\n"
    "    def add_call(self, caller, callee):\n"
    "        if self.graph.has_edge(caller, callee):\n"
    '            self.graph[caller][callee]["weight"] += 1\n'
    "        else:\n"
    '            self.graph.add_edge(caller, callee, relation="calls", weight=1)\n'
    "\n"
    "    def find_cycles(self):\n"
    "        return list(nx.simple_cycles(self.graph))\n"
    "\n"
    "    def pagerank(self, alpha=0.85):\n"
    "        return nx.pagerank(self.graph, alpha=alpha)\n"
    "\n"
    "    def betweenness(self):\n"
    "        return nx.betweenness_centrality(self.graph)\n"
    "\n"
    "    def shortest_path(self, source, target):\n"
    "        return nx.shortest_path(self.graph, source, target)\n"
    "\n"
    "    def communities(self):\n"
    "        undirected = self.graph.to_undirected()\n"
    "        return list(nx.community.greedy_modularity_communities(undirected))\n"
    "\n"
    "    def topological_sort(self):\n"
    "        return list(nx.topological_sort(self.graph))\n"
    "\n"
    "    def bfs_from(self, start):\n"
    "        visited = set()\n"
    "        queue = deque([start])\n"
    "        visited.add(start)\n"
    "        result = []\n"
    "        while queue:\n"
    "            node = queue.popleft()\n"
    "            result.append(node)\n"
    "            for neighbor in self.graph.successors(node):\n"
    "                if neighbor not in visited:\n"
    "                    visited.add(neighbor)\n"
    "                    queue.append(neighbor)\n"
    "        return result\n"
    "\n"
    "    def dfs_from(self, start, visited=None):\n"
    "        if visited is None:\n"
    "            visited = set()\n"
    "        visited.add(start)\n"
    "        result = [start]\n"
    "        for neighbor in self.graph.successors(start):\n"
    "            if neighbor not in visited:\n"
    "                result.extend(self.dfs_from(neighbor, visited))\n"
    "        return result\n"
    "\n"
    "    def dijkstra_from(self, source):\n"
    "        dist = {node: float('inf') for node in self.graph.nodes()}\n"
    "        dist[source] = 0\n"
    "        prev = {node: None for node in self.graph.nodes()}\n"
    "        pq = [(0, source)]\n"
    "\n"
    "        while pq:\n"
    "            d, u = heapq.heappop(pq)\n"
    "            if d > dist[u]:\n"
    "                continue\n"
    "            for v in self.graph.successors(u):\n"
    '                w = self.graph[u][v].get("weight", 1)\n'
    "                if dist[u] + w < dist[v]:\n"
    "                    dist[v] = dist[u] + w\n"
    "                    prev[v] = u\n"
    "                    heapq.heappush(pq, (dist[v], v))\n"
    "\n"
    "        return dist, prev\n"
    "\n"
    "\n"
    "def build_sample_graph():\n"
    "    cg = CodeGraph()\n"
    "\n"
    '    cg.add_file("auth.py", "auth_module")\n'
    '    cg.add_file("user.py", "user_module")\n'
    '    cg.add_file("order.py", "order_module")\n'
    '    cg.add_file("payment.py", "payment_module")\n'
    "\n"
    '    cg.add_class("AuthService", "auth_module")\n'
    '    cg.add_class("UserService", "user_module")\n'
    '    cg.add_class("OrderService", "order_module")\n'
    '    cg.add_class("PaymentService", "payment_module")\n'
    "\n"
    '    cg.add_method("AuthService.login", "AuthService")\n'
    '    cg.add_method("AuthService.register", "AuthService")\n'
    '    cg.add_method("UserService.get_user", "UserService")\n'
    '    cg.add_method("UserService.update_user", "UserService")\n'
    '    cg.add_method("OrderService.create_order", "OrderService")\n'
    '    cg.add_method("OrderService.cancel_order", "OrderService")\n'
    '    cg.add_method("PaymentService.process_payment", "PaymentService")\n'
    '    cg.add_method("PaymentService.refund", "PaymentService")\n'
    "\n"
    '    cg.add_call("AuthService.login", "UserService.get_user")\n'
    '    cg.add_call("AuthService.register", "UserService.update_user")\n'
    '    cg.add_call("OrderService.create_order", "PaymentService.process_payment")\n'
    '    cg.add_call("OrderService.create_order", "UserService.get_user")\n'
    '    cg.add_call("OrderService.cancel_order", "PaymentService.refund")\n'
    '    cg.add_call("PaymentService.refund", "UserService.get_user")\n'
    "\n"
    "    return cg\n"
)

GRAPH_SEARCH_CODE = (
    "from collections import deque\n"
    "import heapq\n"
    "\n"
    "\n"
    "def dijkstra(graph, start):\n"
    "    distances = {node: float('infinity') for node in graph}\n"
    "    distances[start] = 0\n"
    "    priority_queue = [(0, start)]\n"
    "\n"
    "    while priority_queue:\n"
    "        current_dist, current_node = heapq.heappop(priority_queue)\n"
    "        if current_dist > distances[current_node]:\n"
    "            continue\n"
    "        for neighbor, weight in graph[current_node].items():\n"
    "            distance = current_dist + weight\n"
    "            if distance < distances[neighbor]:\n"
    "                distances[neighbor] = distance\n"
    "                heapq.heappush(priority_queue, (distance, neighbor))\n"
    "    return distances\n"
    "\n"
    "\n"
    "def bfs(graph, start):\n"
    "    visited = set()\n"
    "    queue = deque([start])\n"
    "    visited.add(start)\n"
    "    order = []\n"
    "    while queue:\n"
    "        vertex = queue.popleft()\n"
    "        order.append(vertex)\n"
    "        for neighbor in graph.get(vertex, []):\n"
    "            if neighbor not in visited:\n"
    "                visited.add(neighbor)\n"
    "                queue.append(neighbor)\n"
    "    return order\n"
    "\n"
    "\n"
    "def topological_sort(graph):\n"
    "    in_degree = {u: 0 for u in graph}\n"
    "    for u in graph:\n"
    "        for v in graph[u]:\n"
    "            in_degree[v] = in_degree.get(v, 0) + 1\n"
    "\n"
    "    queue = deque([u for u in in_degree if in_degree[u] == 0])\n"
    "    order = []\n"
    "\n"
    "    while queue:\n"
    "        u = queue.popleft()\n"
    "        order.append(u)\n"
    "        for v in graph[u]:\n"
    "            in_degree[v] -= 1\n"
    "            if in_degree[v] == 0:\n"
    "                queue.append(v)\n"
    "\n"
    '    if len(order) != len(graph):\n'
    '        raise ValueError("Graph contains a cycle")\n'
    "    return order\n"
    "\n"
    "\n"
    "def floyd_warshall(n, edges):\n"
    "    dist = [[float('inf')] * n for _ in range(n)]\n"
    "    for i in range(n):\n"
    "        dist[i][i] = 0\n"
    "    for u, v, w in edges:\n"
    "        dist[u][v] = w\n"
    "    for k in range(n):\n"
    "        for i in range(n):\n"
    "            for j in range(n):\n"
    "                if dist[i][k] + dist[k][j] < dist[i][j]:\n"
    "                    dist[i][j] = dist[i][k] + dist[k][j]\n"
    "    return dist\n"
)

ADJACENCY_MATRIX_CODE = (
    "class Graph:\n"
    "    # 邻接矩阵表示的无向图\n"
    "    def __init__(self, num_vertices):\n"
    "        self.num_vertices = num_vertices\n"
    "        self.adj = [[0] * num_vertices for _ in range(num_vertices)]\n"
    "\n"
    "    def add_edge(self, u, v, weight=1):\n"
    "        self.adj[u][v] = weight\n"
    "        self.adj[v][u] = weight\n"
    "\n"
    "    def get_neighbors(self, vertex):\n"
    "        return [i for i in range(self.num_vertices) if self.adj[vertex][i] != 0]\n"
    "\n"
    "    def has_edge(self, u, v):\n"
    "        return self.adj[u][v] != 0\n"
)

SECURITY_CODE = (
    "import networkx as nx\n"
    "import pickle\n"
    "import os\n"
    "\n"
    "\n"
    "class CodeGraphAnalyzer:\n"
    "    def __init__(self, data_dir):\n"
    "        self.data_dir = data_dir\n"
    '        self.api_key = "sk-codegraph-secret-12345"\n'
    '        self.db_password = "graph_db_pass_2024"\n'
    "\n"
    "    def load_graph(self, filename):\n"
    "        path = os.path.join(self.data_dir, filename)\n"
    '        with open(path, "rb") as f:\n'
    "            return pickle.load(f)\n"
    "\n"
    "    def run_query(self, query):\n"
    '        os.system("python analyze.py --query " + query)\n'
    "\n"
    "    def export_data(self, data):\n"
    "        return eval(data)\n"
)


# ======================================================================
#  演示函数
# ======================================================================

async def demo_codegraph_analysis():
    """演示 CodeGraph 代码分析"""
    print_header("演示 1: CodeGraph 代码分析")

    analyzer = CodeAnalyzer()
    result = await analyzer.analyze(CODEGRAPH_SNIPPET, "python")

    print_section("代码度量")
    m = result.metrics
    print("  总行数: %d" % m.lines_of_code)
    print("  代码行: %d" % m.code_lines)
    print("  注释行: %d" % m.comment_lines)
    print("  函数数量: %d" % m.functions)
    print("  类数量: %d" % m.classes)
    print("  平均函数长度: %.1f 行" % m.avg_function_length)
    print("  圈复杂度: %d" % m.cyclomatic_complexity)
    print("  可维护性指数: %.2f" % m.maintainability_index)

    print_section("Graph / NetworkX 检测")
    graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
    other_issues = [i for i in result.issues if i.category != "graph_algorithm"]
    print("  图算法相关检测: %d 条" % len(graph_issues))
    print("  其他问题: %d 条" % len(other_issues))
    for i, issue in enumerate(graph_issues, 1):
        line_info = " (第 %d 行)" % issue.line_number if issue.line_number else ""
        print("  %d. [%s] %s%s" % (i, issue.severity.upper(), issue.message, line_info))
        if issue.suggestion:
            print("     建议: %s" % issue.suggestion)

    print_section("质量评分")
    print("  综合评分: %.2f/100" % result.quality_score)


async def demo_graph_search_analysis():
    """演示图搜索算法分析"""
    print_header("演示 2: 图搜索算法分析")

    analyzer = CodeAnalyzer()
    result = await analyzer.analyze(GRAPH_SEARCH_CODE, "python")

    print_section("检测到的图算法")
    graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
    for issue in graph_issues:
        print("  [%s] %s" % (issue.severity.upper(), issue.message))
        if issue.suggestion:
            print("    -> %s" % issue.suggestion)

    print_section("复杂度分析")
    print("  圈复杂度: %d" % result.metrics.cyclomatic_complexity)
    print("  质量评分: %.2f/100" % result.quality_score)


async def demo_adjacency_matrix_analysis():
    """演示邻接矩阵分析"""
    print_header("演示 3: 邻接矩阵代码分析")

    analyzer = CodeAnalyzer()
    result = await analyzer.analyze(ADJACENCY_MATRIX_CODE, "python")

    print_section("邻接矩阵检测")
    graph_issues = [i for i in result.issues if i.category == "graph_algorithm"]
    for issue in graph_issues:
        print("  [%s] %s" % (issue.severity.upper(), issue.message))
        if issue.suggestion:
            print("    -> %s" % issue.suggestion)

    print_section("质量评分")
    print("  质量评分: %.2f/100" % result.quality_score)


async def demo_security_scan():
    """演示安全扫描"""
    print_header("演示 4: CodeGraph 安全扫描")

    scanner = SecurityScanner()
    result = await scanner.scan(SECURITY_CODE, "python")

    print_section("安全扫描结果")
    print("  发现漏洞: %d 个" % len(result.vulnerabilities))
    print("  发现密钥: %d 个" % len(result.secrets))
    print("  风险评分: %d/100" % result.risk_score)

    for i, vuln in enumerate(result.vulnerabilities[:5], 1):
        print("  %d. [%s] %s" % (i, vuln.severity.value.upper(), vuln.title))
        print("     %s" % vuln.description)

    for secret in result.secrets[:3]:
        print("  密钥: %s" % secret.type)


async def demo_refactoring():
    """演示重构分析"""
    print_header("演示 5: CodeGraph 重构分析")

    engine = RefactoringEngine()
    result = await engine.analyze(CODEGRAPH_SNIPPET, "python")

    print_section("重构建议")
    print("  发现重构操作: %d 个" % len(result.operations))
    for i, op in enumerate(result.operations[:5], 1):
        print("  %d. %s" % (i, op.type.value))
        print("     %s" % op.description)
        print("     置信度: %.2f" % op.confidence)


async def demo_performance_analysis():
    """演示性能分析"""
    print_header("演示 6: CodeGraph 性能分析")

    analyzer = PerformanceAnalyzer()
    result = await analyzer.analyze(CODEGRAPH_SNIPPET, "python")

    print_section("性能指标")
    print("  综合评分: %.2f/100" % result.score)
    if result.issues:
        print("  性能问题: %d 个" % len(result.issues))
        for issue in result.issues[:5]:
            print("  - [%s] %s: %s" % (issue.severity, issue.title, issue.description))


async def demo_report_generation():
    """演示报告生成"""
    print_header("演示 7: CodeGraph 分析报告")

    generator = ReportGenerator()
    report = await generator.generate_report(
        code=CODEGRAPH_SNIPPET,
        language="python",
        file_path="codegraph.py",
        project_name="CodeGraph 知识图谱分析系统",
    )

    print_section("报告摘要")
    print("  项目名称: %s" % report.project_name)
    print("  生成时间: %s" % report.generated_at)
    overall = report.summary.metrics.get("overall_score", 0)
    print("  综合评分: %.1f/100" % overall)

    # 导出报告
    output_dir = os.path.join(os.path.dirname(__file__), "codegraph_reports")
    os.makedirs(output_dir, exist_ok=True)

    md_path = os.path.join(output_dir, "codegraph_report.md")
    generator.export_report(report, md_path, ReportFormat.MARKDOWN)
    print("  Markdown 报告已导出: %s" % md_path)

    json_path = os.path.join(output_dir, "codegraph_report.json")
    generator.export_report(report, json_path, ReportFormat.JSON)
    print("  JSON 报告已导出: %s" % json_path)

    # 清理临时文件
    import shutil
    shutil.rmtree(output_dir, ignore_errors=True)


async def main():
    """主演示函数"""
    print("\n" + "=" * 70)
    print("  CodeGraph 分析演示 -- AI Agent Benchmark")
    print("  演示图算法代码分析、知识图谱架构审查能力")
    print("=" * 70)

    try:
        await demo_codegraph_analysis()
        await demo_graph_search_analysis()
        await demo_adjacency_matrix_analysis()
        await demo_security_scan()
        await demo_refactoring()
        await demo_performance_analysis()
        await demo_report_generation()

        print_header("演示完成")
        print("\n  所有 CodeGraph 分析演示完成！")
        print("  AI Agent Benchmark 可以有效分析图算法代码。")
        print("  项目地址: https://github.com/gurinalje/Vibe-Coding")
        print("\n" + "=" * 70)

    except Exception as e:
        print("\n错误: %s" % e)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
