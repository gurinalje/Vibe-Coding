"""
AI Agent Benchmark 演示脚本
展示多 Agent 协同代码审查和重构的核心功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.code_analyzer import CodeAnalyzer
from core.security_scanner import SecurityScanner
from core.refactoring_engine import RefactoringEngine
from agents.reviewer_agent import ReviewerAgent
from agents.developer_agent import DeveloperAgent
from agents.critic_agent import CriticAgent
from agents.coordinator import AgentCoordinator


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str):
    """打印章节"""
    print(f"\n--- {title} ---")


async def demo_code_analysis():
    """演示代码分析功能"""
    print_header("演示 1: 代码分析引擎")
    
    # 测试代码（包含多种问题）
    test_code = '''
def process_user_data(users):
    result = []
    for user in users:
        if user is not None:
            if user.get("active") is not None:
                if user["active"] == True:
                    if user.get("age") is not None:
                        if user["age"] > 0:
                            if user["age"] < 150:
                                name = user["name"]
                                email = user["email"]
                                # TODO: 这里应该验证邮箱格式
                                age = user["age"]
                                if age < 18:
                                    category = "minor"
                                else:
                                    if age < 65:
                                        category = "adult"
                                    else:
                                        category = "senior"
                                result.append({
                                    "name": name,
                                    "email": email,
                                    "age": age,
                                    "category": category
                                })
    return result


def calculate_total(items):
    total = 0
    for item in items:
        if item["price"] > 0:
            total = total + item["price"] * item["quantity"]
    return total


class UserManager:
    def __init__(self):
        self.users = []
    
    def add_user(self, user):
        self.users.append(user)
    
    def get_user(self, user_id):
        for user in self.users:
            if user["id"] == user_id:
                return user
        return None
    
    def delete_user(self, user_id):
        for user in self.users:
            if user["id"] == user_id:
                self.users.remove(user)
                return True
        return False
'''
    
    analyzer = CodeAnalyzer()
    result = await analyzer.analyze(test_code, "python")
    
    print_section("代码度量")
    metrics = result.metrics
    print(f"  总行数: {metrics.lines_of_code}")
    print(f"  代码行: {metrics.code_lines}")
    print(f"  注释行: {metrics.comment_lines}")
    print(f"  函数数量: {metrics.functions}")
    print(f"  类数量: {metrics.classes}")
    print(f"  平均函数长度: {metrics.avg_function_length:.1f} 行")
    print(f"  最长函数: {metrics.max_function_length} 行")
    
    print_section("复杂度分析")
    print(f"  圈复杂度: {metrics.cyclomatic_complexity}")
    print(f"  可维护性指数: {metrics.maintainability_index:.2f}")
    print(f"  Halstead 体积: {metrics.halstead_volume:.2f}")
    
    print_section("发现的问题")
    for i, issue in enumerate(result.issues[:5], 1):
        print(f"  {i}. [{issue.severity.upper()}] {issue.category}")
        print(f"     {issue.message}")
        if issue.line_number:
            print(f"     位置: 第 {issue.line_number} 行")
        print()
    
    print_section("质量评分")
    print(f"  综合评分: {result.quality_score:.2f}/100")


async def demo_security_scanning():
    """演示安全扫描功能"""
    print_header("演示 2: 安全扫描器")
    
    # 包含安全漏洞的代码
    vulnerable_code = '''
import os
import sqlite3
import subprocess

class UserService:
    def __init__(self):
        self.db_password = "admin123"
        self.api_key = "sk-1234567890abcdef"
    
    def login(self, username, password):
        # SQL 注入漏洞
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()
    
    def execute_command(self, cmd):
        # 命令注入漏洞
        os.system(cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return result.stdout
    
    def read_file(self, filename):
        # 路径遍历漏洞
        path = "/uploads/" + filename
        with open(path, 'r') as f:
            return f.read()
    
    def query_database(self, user_input):
        # SQL 注入（另一种方式）
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data WHERE id = " + user_input)
        return cursor.fetchall()
'''
    
    scanner = SecurityScanner()
    result = await scanner.scan(vulnerable_code, "python")
    
    print_section("安全扫描结果")
    print(f"  发现漏洞数量: {len(result.vulnerabilities)}")
    print(f"  风险评分: {result.risk_score}/100")
    print()
    
    print_section("发现的漏洞")
    for i, vuln in enumerate(result.vulnerabilities[:5], 1):
        print(f"  {i}. [{vuln.severity.value.upper()}] {vuln.type.value}")
        print(f"     {vuln.description}")
        print(f"     位置: 第 {vuln.line_number} 行")
        print(f"     修复建议: {vuln.recommendation}")
        print()
    
    print_section("敏感信息扫描")
    for info in result.secrets[:3]:
        print(f"  - {info.type}: {info.line_content[:50] if info.line_content else 'N/A'}")


async def demo_refactoring():
    """演示重构引擎功能"""
    print_header("演示 3: 重构引擎")
    
    # 包含重构机会的代码
    refactor_code = '''
def process_orders(orders):
    # 长函数，应该拆分
    valid_orders = []
    total = 0
    
    for order in orders:
        if order["status"] == "pending":
            if order["amount"] > 0:
                if order["customer_id"] is not None:
                    # 计算折扣
                    discount = 0
                    if order["amount"] > 1000:
                        discount = 0.1
                    elif order["amount"] > 500:
                        discount = 0.05
                    elif order["amount"] > 100:
                        discount = 0.02
                    
                    final_amount = order["amount"] * (1 - discount)
                    total += final_amount
                    
                    valid_orders.append({
                        "id": order["id"],
                        "amount": final_amount,
                        "discount": discount
                    })
    
    # 重复的验证逻辑
    for order in valid_orders:
        if order["amount"] > 0:
            if order["id"] is not None:
                pass
    
    return valid_orders, total


def calculate_discount(amount):
    # 重复的折扣计算逻辑
    if amount > 1000:
        return 0.1
    elif amount > 500:
        return 0.05
    elif amount > 100:
        return 0.02
    return 0


def apply_discount(amount, discount_rate):
    return amount * (1 - discount_rate)
'''
    
    engine = RefactoringEngine()
    result = await engine.analyze(refactor_code, "python")
    
    print_section("重构机会分析")
    print(f"  发现重构操作: {len(result.operations)} 个")
    print()
    
    print_section("重构建议")
    for i, op in enumerate(result.operations[:3], 1):
        print(f"  {i}. {op.type.value}")
        print(f"     描述: {op.description}")
        print(f"     影响程度: {op.impact}")
        print(f"     置信度: {op.confidence:.2f}")
        print()


async def demo_multi_agent():
    """演示多 Agent 协同工作"""
    print_header("演示 4: 多 Agent 协同代码审查")
    
    # 创建协调器（已自动初始化所有 Agent）
    coordinator = AgentCoordinator()
    
    # 待审查的代码
    review_code = '''
def authenticate_user(username, password):
    # 硬编码密码
    admin_password = "admin123"
    
    if username == "admin":
        if password == admin_password:
            return True
        else:
            return False
    else:
        # SQL 注入风险
        query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
        result = execute_query(query)
        if result:
            return True
        else:
            return False
'''
    
    print_section("启动多 Agent 审查流程")
    print("  Agent: Reviewer (审查者) - 识别代码问题")
    print("  Agent: Developer (开发者) - 执行重构")
    print("  Agent: Critic (批评者) - 评估审查质量")
    print()
    
    # 执行代码审查
    review_result = await coordinator.review_code(review_code, "python")
    
    print_section("审查结果")
    print(f"  审查意见数量: {len(review_result.get('comments', []))}")
    
    # 执行代码重构
    refactoring_result = await coordinator.refactor_code(review_code, "python")
    
    print_section("重构结果")
    print(f"  重构操作数量: {len(refactoring_result.get('operations', []))}")
    
    print_section("Agent 统计")
    for agent_id, agent in coordinator.agents.items():
        stats = agent.get_statistics()
        print(f"  {agent_id}:")
        print(f"    处理任务数: {stats.get('tasks_processed', 0)}")
        print(f"    平均处理时间: {stats.get('average_processing_time', 0):.4f}s")


async def main():
    """主演示函数"""
    print("\n" + "=" * 70)
    print("  AI Agent Benchmark - 多 Agent 协同代码审查系统演示")
    print("  Vibe Coding - AI 自动化代码重构基准项目")
    print("=" * 70)
    
    try:
        # 演示 1: 代码分析
        await demo_code_analysis()
        
        # 演示 2: 安全扫描
        await demo_security_scanning()
        
        # 演示 3: 重构引擎
        await demo_refactoring()
        
        # 演示 4: 多 Agent 协同
        await demo_multi_agent()
        
        print_header("演示完成")
        print("\n  所有功能演示完成！")
        print("  项目已上传到: https://github.com/gurinalje/Vibe-Coding")
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
