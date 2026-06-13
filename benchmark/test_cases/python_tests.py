"""
Python Test Cases for AI Agent Benchmark system.

This module provides Python-specific test cases for benchmarking
code review capabilities.
"""

from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from benchmark.evaluator import TestCase


class PythonTestCases:
    """Python test cases for benchmarking."""
    
    @staticmethod
    def get_all_cases() -> List[TestCase]:
        """Get all Python test cases."""
        cases = []
        cases.extend(PythonTestCases.get_basic_cases())
        cases.extend(PythonTestCases.get_security_cases())
        cases.extend(PythonTestCases.get_performance_cases())
        cases.extend(PythonTestCases.get_style_cases())
        cases.extend(PythonTestCases.get_refactoring_cases())
        return cases
    
    @staticmethod
    def get_basic_cases() -> List[TestCase]:
        """Get basic Python test cases."""
        return [
            TestCase(
                id="py_basic_001",
                name="简单函数审查",
                description="测试对简单函数的代码审查能力",
                language="python",
                code='''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b

def calculate_average(numbers):
    """Calculate average of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
''',
                expected_issues=[],
                expected_score=95.0,
                tags=["basic", "function"],
                difficulty="easy",
            ),
            TestCase(
                id="py_basic_002",
                name="类定义审查",
                description="测试对类定义的代码审查能力",
                language="python",
                code='''
class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        """Add value to result."""
        self.result += value
        return self
    
    def subtract(self, value):
        """Subtract value from result."""
        self.result -= value
        return self
    
    def get_result(self):
        """Get current result."""
        return self.result
    
    def reset(self):
        """Reset result to zero."""
        self.result = 0
        return self
''',
                expected_issues=[],
                expected_score=90.0,
                tags=["basic", "class"],
                difficulty="easy",
            ),
            TestCase(
                id="py_basic_003",
                name="异常处理审查",
                description="测试对异常处理的代码审查能力",
                language="python",
                code='''
def divide_numbers(a, b):
    """Divide two numbers with error handling."""
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("Error: Division by zero")
        return None
    except TypeError as e:
        print(f"Type error: {e}")
        return None
''',
                expected_issues=[
                    {"type": "best_practice", "description": "使用 print 而非 logging"}
                ],
                expected_score=85.0,
                tags=["basic", "exception"],
                difficulty="easy",
            ),
        ]
    
    @staticmethod
    def get_security_cases() -> List[TestCase]:
        """Get security-focused Python test cases."""
        return [
            TestCase(
                id="py_security_001",
                name="SQL注入漏洞",
                description="测试检测 SQL 注入漏洞的能力",
                language="python",
                code='''
import sqlite3

def get_user(username):
    """Get user from database."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Vulnerable SQL query
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    return user
''',
                expected_issues=[
                    {"type": "security", "description": "SQL 注入漏洞"}
                ],
                expected_score=60.0,
                tags=["security", "sql_injection"],
                difficulty="medium",
            ),
            TestCase(
                id="py_security_002",
                name="命令注入漏洞",
                description="测试检测命令注入漏洞的能力",
                language="python",
                code='''
import os

def list_files(directory):
    """List files in directory."""
    # Vulnerable command execution
    result = os.system(f"ls -la {directory}")
    return result

def execute_command(command):
    """Execute a system command."""
    # Another vulnerable pattern
    import subprocess
    subprocess.call(command, shell=True)
''',
                expected_issues=[
                    {"type": "security", "description": "命令注入漏洞"},
                    {"type": "security", "description": "shell=True 使用"}
                ],
                expected_score=40.0,
                tags=["security", "command_injection"],
                difficulty="medium",
            ),
            TestCase(
                id="py_security_003",
                name="硬编码密码",
                description="测试检测硬编码密码的能力",
                language="python",
                code='''
# Configuration with hardcoded credentials
DATABASE_URL = "postgresql://admin:password123@localhost:5432/mydb"
API_KEY = "sk-1234567890abcdef"
SECRET_KEY = "my-super-secret-key"

def connect_database():
    """Connect to database."""
    import psycopg2
    return psycopg2.connect(DATABASE_URL)
''',
                expected_issues=[
                    {"type": "security", "description": "硬编码密码"},
                    {"type": "security", "description": "硬编码 API 密钥"}
                ],
                expected_score=30.0,
                tags=["security", "hardcoded_secrets"],
                difficulty="medium",
            ),
            TestCase(
                id="py_security_004",
                name="不安全的反序列化",
                description="测试检测不安全反序列化的能力",
                language="python",
                code='''
import pickle
import yaml

def load_user_data(data):
    """Load user data from pickle."""
    # Insecure deserialization
    user = pickle.loads(data)
    return user

def load_config(config_file):
    """Load configuration from YAML file."""
    with open(config_file, 'r') as f:
        # Unsafe YAML loading
        config = yaml.load(f)
    return config
''',
                expected_issues=[
                    {"type": "security", "description": "pickle 不安全反序列化"},
                    {"type": "security", "description": "yaml.load 不安全"}
                ],
                expected_score=35.0,
                tags=["security", "deserialization"],
                difficulty="medium",
            ),
        ]
    
    @staticmethod
    def get_performance_cases() -> List[TestCase]:
        """Get performance-focused Python test cases."""
        return [
            TestCase(
                id="py_perf_001",
                name="循环中字符串拼接",
                description="测试检测循环中字符串拼接的能力",
                language="python",
                code='''
def build_string(items):
    """Build a string from items."""
    result = ""
    for item in items:
        result += str(item) + ", "
    return result.rstrip(", ")
''',
                expected_issues=[
                    {"type": "performance", "description": "循环中字符串拼接"}
                ],
                expected_score=75.0,
                tags=["performance", "string_concat"],
                difficulty="easy",
            ),
            TestCase(
                id="py_perf_002",
                name="列表成员测试",
                description="测试检测低效列表成员测试的能力",
                language="python",
                code='''
def check_members(items, targets):
    """Check which targets are in items."""
    result = []
    for target in targets:
        if target in items:  # O(n) operation
            result.append(target)
    return result
''',
                expected_issues=[
                    {"type": "performance", "description": "列表成员测试效率低"}
                ],
                expected_score=70.0,
                tags=["performance", "list_membership"],
                difficulty="medium",
            ),
            TestCase(
                id="py_perf_003",
                name="嵌套循环",
                description="测试检测嵌套循环复杂度的能力",
                language="python",
                code='''
def find_pairs(matrix1, matrix2):
    """Find matching pairs between two matrices."""
    result = []
    for i in range(len(matrix1)):
        for j in range(len(matrix1[i])):
            for k in range(len(matrix2)):
                for l in range(len(matrix2[k])):
                    if matrix1[i][j] == matrix2[k][l]:
                        result.append((i, j, k, l))
    return result
''',
                expected_issues=[
                    {"type": "performance", "description": "深层嵌套循环"}
                ],
                expected_score=50.0,
                tags=["performance", "nested_loops"],
                difficulty="hard",
            ),
        ]
    
    @staticmethod
    def get_style_cases() -> List[TestCase]:
        """Get style-focused Python test cases."""
        return [
            TestCase(
                id="py_style_001",
                name="命名规范",
                description="测试检测命名规范的能力",
                language="python",
                code='''
def MyFunction():
    """This function has bad naming."""
    MyVariable = 10
    another_variable = 20
    return MyVariable + another_variable

class my_class:
    """This class has bad naming."""
    pass
''',
                expected_issues=[
                    {"type": "naming", "description": "函数名不符合规范"},
                    {"type": "naming", "description": "类名不符合规范"}
                ],
                expected_score=65.0,
                tags=["style", "naming"],
                difficulty="easy",
            ),
            TestCase(
                id="py_style_002",
                name="缺少文档字符串",
                description="测试检测缺少文档字符串的能力",
                language="python",
                code='''
def calculate(x, y):
    result = x * y
    return result

def process_data(data):
    processed = []
    for item in data:
        if item > 0:
            processed.append(item * 2)
    return processed
''',
                expected_issues=[
                    {"type": "documentation", "description": "缺少文档字符串"}
                ],
                expected_score=70.0,
                tags=["style", "documentation"],
                difficulty="easy",
            ),
            TestCase(
                id="py_style_003",
                name="裸 except 子句",
                description="测试检测裸 except 子句的能力",
                language="python",
                code='''
def risky_operation():
    """Perform risky operation."""
    try:
        result = 1 / 0
        return result
    except:
        return None

def another_operation():
    """Another risky operation."""
    try:
        data = eval(input("Enter expression: "))
        return data
    except:
        print("Error occurred")
        return None
''',
                expected_issues=[
                    {"type": "best_practice", "description": "使用裸 except 子句"},
                    {"type": "security", "description": "使用 eval()"}
                ],
                expected_score=40.0,
                tags=["style", "exception", "security"],
                difficulty="medium",
            ),
        ]
    
    @staticmethod
    def get_refactoring_cases() -> List[TestCase]:
        """Get refactoring-focused Python test cases."""
        return [
            TestCase(
                id="py_refactor_001",
                name="重复代码检测",
                description="测试检测重复代码的能力",
                language="python",
                code='''
def process_user_data(users):
    """Process user data for reporting."""
    result = []
    for user in users:
        if user.get("active", False):
            if user.get("age", 0) >= 18:
                if user.get("email"):
                    result.append({
                        "name": user["name"],
                        "email": user["email"],
                        "age": user["age"],
                        "status": "active"
                    })
    return result

def filter_adult_users(users):
    """Filter adult users from list."""
    result = []
    for user in users:
        if user.get("active", False):
            if user.get("age", 0) >= 18:
                if user.get("email"):
                    result.append(user)
    return result

def get_active_adults(users):
    """Get active adult users."""
    result = []
    for user in users:
        if user.get("active", False):
            if user.get("age", 0) >= 18:
                if user.get("email"):
                    result.append({
                        "id": user["id"],
                        "name": user["name"],
                        "email": user["email"]
                    })
    return result
''',
                expected_issues=[
                    {"type": "refactoring", "description": "重复代码：过滤逻辑"},
                    {"type": "refactoring", "description": "重复代码：条件检查"},
                    {"type": "refactoring", "description": "建议提取公共函数"}
                ],
                expected_score=60.0,
                tags=["refactoring", "duplicate_code"],
                difficulty="medium",
            ),
            TestCase(
                id="py_refactor_002",
                name="过长函数检测",
                description="测试检测过长函数的能力",
                language="python",
                code='''
def generate_invoice(order_data, customer_info, tax_rates, discounts):
    """Generate invoice with all calculations and formatting."""
    # Too many responsibilities in one function
    
    # Calculate subtotal
    subtotal = 0
    for item in order_data["items"]:
        price = item["price"]
        quantity = item["quantity"]
        item_total = price * quantity
        subtotal += item_total
    
    # Apply discounts
    discount_amount = 0
    if customer_info.get("is_vip", False):
        discount_amount = subtotal * discounts["vip_discount"]
    elif customer_info.get("member_since", 0) < 365:
        discount_amount = subtotal * discounts["loyalty_discount"]
    
    # Calculate tax
    tax_amount = 0
    for item in order_data["items"]:
        tax_rate = tax_rates.get(item["category"], 0)
        item_tax = (item["price"] * item["quantity"]) * tax_rate
        tax_amount += item_tax
    
    # Calculate total
    total = subtotal - discount_amount + tax_amount
    
    # Format invoice
    invoice = []
    invoice.append("=" * 50)
    invoice.append("INVOICE")
    invoice.append("=" * 50)
    invoice.append(f"Customer: {customer_info['name']}")
    invoice.append(f"Date: {order_data['date']}")
    invoice.append("")
    invoice.append("Items:")
    
    for item in order_data["items"]:
        line = f"{item['name']:30} {item['quantity']:>5} x ${item['price']:>10.2f}"
        invoice.append(line)
    
    invoice.append("-" * 50)
    invoice.append(f"Subtotal: ${subtotal:>35.2f}")
    invoice.append(f"Discount: ${discount_amount:>35.2f}")
    invoice.append(f"Tax: ${tax_amount:>38.2f}")
    invoice.append("=" * 50)
    invoice.append(f"TOTAL: ${total:>36.2f}")
    invoice.append("=" * 50)
    
    return "\\n".join(invoice)
''',
                expected_issues=[
                    {"type": "refactoring", "description": "函数过长（超过50行）"},
                    {"type": "refactoring", "description": "单一职责原则违反"},
                    {"type": "refactoring", "description": "建议拆分为多个函数"}
                ],
                expected_score=55.0,
                tags=["refactoring", "long_function"],
                difficulty="hard",
            ),
            TestCase(
                id="py_refactor_003",
                name="过深嵌套检测",
                description="测试检测过深嵌套的能力",
                language="python",
                code='''
def process_order(order, user, inventory, payment_system):
    """Process an order with complex validation."""
    if order is not None:
        if user is not None:
            if user.get("active", False):
                if order.get("items"):
                    for item in order["items"]:
                        if item.get("product_id"):
                            if inventory.has_stock(item["product_id"], item["quantity"]):
                                if user.get("balance", 0) >= item["price"] * item["quantity"]:
                                    # Process payment
                                    payment_result = payment_system.charge(
                                        user["id"], 
                                        item["price"] * item["quantity"]
                                    )
                                    if payment_result.success:
                                        inventory.update_stock(
                                            item["product_id"], 
                                            -item["quantity"]
                                        )
                                    else:
                                        return {"status": "error", "message": "Payment failed"}
                                else:
                                    return {"status": "error", "message": "Insufficient balance"}
                            else:
                                return {"status": "error", "message": "Out of stock"}
                        else:
                            return {"status": "error", "message": "Invalid item"}
                else:
                    return {"status": "error", "message": "Empty order"}
            else:
                return {"status": "error", "message": "User inactive"}
        else:
            return {"status": "error", "message": "User not found"}
    else:
        return {"status": "error", "message": "Order not found"}
    
    return {"status": "success", "message": "Order processed"}
''',
                expected_issues=[
                    {"type": "refactoring", "description": "嵌套层次过深（超过4层）"},
                    {"type": "refactoring", "description": "建议使用卫语句"},
                    {"type": "refactoring", "description": "建议提取验证函数"}
                ],
                expected_score=50.0,
                tags=["refactoring", "deep_nesting"],
                difficulty="hard",
            ),
        ]