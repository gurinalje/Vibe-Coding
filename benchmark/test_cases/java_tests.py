"""
Java Test Cases for AI Agent Benchmark system.

This module provides Java-specific test cases for benchmarking
code review capabilities.
"""

from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from benchmark.evaluator import TestCase


class JavaTestCases:
    """Java test cases for benchmarking."""
    
    @staticmethod
    def get_all_cases() -> List[TestCase]:
        """Get all Java test cases."""
        cases = []
        cases.extend(JavaTestCases.get_basic_cases())
        cases.extend(JavaTestCases.get_security_cases())
        cases.extend(JavaTestCases.get_performance_cases())
        cases.extend(JavaTestCases.get_style_cases())
        cases.extend(JavaTestCases.get_refactoring_cases())
        return cases
    
    @staticmethod
    def get_basic_cases() -> List[TestCase]:
        """Get basic Java test cases."""
        return [
            TestCase(
                id="java_basic_001",
                name="简单类审查",
                description="测试对简单 Java 类的代码审查能力",
                language="java",
                code='''
public class Calculator {
    private int result;
    
    public Calculator() {
        this.result = 0;
    }
    
    public Calculator add(int value) {
        this.result += value;
        return this;
    }
    
    public Calculator subtract(int value) {
        this.result -= value;
        return this;
    }
    
    public int getResult() {
        return this.result;
    }
    
    public void reset() {
        this.result = 0;
    }
}
''',
                expected_issues=[],
                expected_score=95.0,
                tags=["basic", "class"],
                difficulty="easy",
            ),
            TestCase(
                id="java_basic_002",
                name="接口实现审查",
                description="测试对接口实现的代码审查能力",
                language="java",
                code='''
import java.util.List;
import java.util.ArrayList;

public class StudentManager {
    private List<String> students;
    
    public StudentManager() {
        this.students = new ArrayList<>();
    }
    
    public void addStudent(String name) {
        if (name != null && !name.isEmpty()) {
            students.add(name);
        }
    }
    
    public boolean removeStudent(String name) {
        return students.remove(name);
    }
    
    public List<String> getAllStudents() {
        return new ArrayList<>(students);
    }
    
    public int getStudentCount() {
        return students.size();
    }
}
''',
                expected_issues=[],
                expected_score=90.0,
                tags=["basic", "class", "collection"],
                difficulty="easy",
            ),
        ]
    
    @staticmethod
    def get_security_cases() -> List[TestCase]:
        """Get security-focused Java test cases."""
        return [
            TestCase(
                id="java_security_001",
                name="SQL注入漏洞",
                description="测试检测 SQL 注入漏洞的能力",
                language="java",
                code='''
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import java.sql.ResultSet;

public class UserDao {
    public User findByUsername(String username) {
        try {
            Connection conn = DriverManager.getConnection(DB_URL);
            Statement stmt = conn.createStatement();
            
            // Vulnerable SQL query
            String query = "SELECT * FROM users WHERE username = '" + username + "'";
            ResultSet rs = stmt.executeQuery(query);
            
            if (rs.next()) {
                return new User(rs.getString("username"), rs.getString("email"));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
}
''',
                expected_issues=[
                    {"type": "security", "description": "SQL 注入漏洞"},
                    {"type": "security", "description": "捕获通用 Exception"}
                ],
                expected_score=40.0,
                tags=["security", "sql_injection"],
                difficulty="medium",
            ),
            TestCase(
                id="java_security_002",
                name="命令注入漏洞",
                description="测试检测命令注入漏洞的能力",
                language="java",
                code='''
import java.io.Runtime;

public class CommandExecutor {
    public void executeCommand(String command) {
        try {
            // Vulnerable command execution
            Runtime.getRuntime().exec(command);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public void listFiles(String path) {
        // Another vulnerable pattern
        String[] cmd = {"/bin/sh", "-c", "ls -la " + path};
        try {
            Runtime.getRuntime().exec(cmd);
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}
''',
                expected_issues=[
                    {"type": "security", "description": "命令注入漏洞"},
                    {"type": "best_practice", "description": "使用 System.out.print"}
                ],
                expected_score=30.0,
                tags=["security", "command_injection"],
                difficulty="medium",
            ),
            TestCase(
                id="java_security_003",
                name="硬编码密码",
                description="测试检测硬编码密码的能力",
                language="java",
                code='''
public class DatabaseConfig {
    // Hardcoded credentials
    private static final String DB_URL = "jdbc:mysql://localhost:3306/mydb";
    private static final String DB_USER = "admin";
    private static final String DB_PASSWORD = "password123";
    private static final String API_KEY = "sk-1234567890";
    
    public Connection getConnection() throws Exception {
        return DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
    }
}
''',
                expected_issues=[
                    {"type": "security", "description": "硬编码密码"},
                    {"type": "security", "description": "硬编码 API 密钥"}
                ],
                expected_score=25.0,
                tags=["security", "hardcoded_secrets"],
                difficulty="medium",
            ),
        ]
    
    @staticmethod
    def get_performance_cases() -> List[TestCase]:
        """Get performance-focused Java test cases."""
        return [
            TestCase(
                id="java_perf_001",
                name="字符串拼接",
                description="测试检测字符串拼接的能力",
                language="java",
                code='''
public class StringConcatenator {
    public String concatenate(List<String> items) {
        String result = "";
        for (String item : items) {
            result += item + ", ";  // Inefficient string concatenation
        }
        return result.substring(0, result.length() - 2);
    }
}
''',
                expected_issues=[
                    {"type": "performance", "description": "循环中字符串拼接"}
                ],
                expected_score=70.0,
                tags=["performance", "string_concat"],
                difficulty="easy",
            ),
            TestCase(
                id="java_perf_002",
                name="频繁对象创建",
                description="测试检测频繁对象创建的能力",
                language="java",
                code='''
public class DataProcessor {
    public void processLargeList(List<String> data) {
        for (String item : data) {
            // Creating new StringBuilder in each iteration
            StringBuilder sb = new StringBuilder();
            sb.append(item);
            sb.append(" processed");
            
            // Creating new HashMap in each iteration
            Map<String, String> map = new HashMap<>();
            map.put("value", sb.toString());
            
            processItem(map);
        }
    }
}
''',
                expected_issues=[
                    {"type": "performance", "description": "频繁对象创建"}
                ],
                expected_score=65.0,
                tags=["performance", "object_creation"],
                difficulty="medium",
            ),
        ]
    
    @staticmethod
    def get_style_cases() -> List[TestCase]:
        """Get style-focused Java test cases."""
        return [
            TestCase(
                id="java_style_001",
                name="命名规范",
                description="测试检测 Java 命名规范的能力",
                language="java",
                code='''
public class badClassName {
    public int MyMethod() {
        int MyVariable = 10;
        int another_variable = 20;
        return MyVariable + another_variable;
    }
    
    public void process_data() {
        // Method name should be camelCase
    }
}
''',
                expected_issues=[
                    {"type": "naming", "description": "类名不符合规范"},
                    {"type": "naming", "description": "方法名不符合规范"}
                ],
                expected_score=50.0,
                tags=["style", "naming"],
                difficulty="easy",
            ),
            TestCase(
                id="java_style_002",
                name="捕获通用异常",
                description="测试检测捕获通用异常的能力",
                language="java",
                code='''
public class ExceptionHandler {
    public void riskyOperation() {
        try {
            int result = 10 / 0;
            System.out.println(result);
        } catch (Exception e) {
            System.out.println("Error occurred");
            e.printStackTrace();
        }
    }
    
    public void anotherRiskyOperation() {
        try {
            String data = getData();
            processData(data);
        } catch (Exception e) {
            // Bad practice: catching generic exception
            return;
        }
    }
}
''',
                expected_issues=[
                    {"type": "best_practice", "description": "捕获通用 Exception"},
                    {"type": "best_practice", "description": "使用 System.out.print"}
                ],
                expected_score=45.0,
                tags=["style", "exception"],
                difficulty="medium",
            ),
        ]
    
    @staticmethod
    def get_refactoring_cases() -> List[TestCase]:
        """Get refactoring-focused Java test cases."""
        return [
            TestCase(
                id="java_refactor_001",
                name="重复代码检测",
                description="测试检测重复代码的能力",
                language="java",
                code='''
public class OrderProcessor {
    public void processOrder(Order order) {
        // Validate order
        if (order == null) {
            throw new IllegalArgumentException("Order cannot be null");
        }
        if (order.getItems().isEmpty()) {
            throw new IllegalArgumentException("Order must have items");
        }
        
        // Calculate total
        double total = 0;
        for (OrderItem item : order.getItems()) {
            total += item.getPrice() * item.getQuantity();
        }
        
        // Apply discount
        if (order.getCustomer().isPremium()) {
            total *= 0.9;
        }
        
        // Process payment
        PaymentResult result = paymentService.process(order.getPayment(), total);
        if (!result.isSuccess()) {
            throw new PaymentException("Payment failed");
        }
        
        // Update inventory
        for (OrderItem item : order.getItems()) {
            inventoryService.updateStock(item.getProductId(), -item.getQuantity());
        }
    }
    
    public void processRefund(Order order) {
        // Similar validation code
        if (order == null) {
            throw new IllegalArgumentException("Order cannot be null");
        }
        if (order.getItems().isEmpty()) {
            throw new IllegalArgumentException("Order must have items");
        }
        
        // Similar calculation code
        double total = 0;
        for (OrderItem item : order.getItems()) {
            total += item.getPrice() * item.getQuantity();
        }
        
        // Process refund
        PaymentResult result = paymentService.refund(order.getPayment(), total);
        if (!result.isSuccess()) {
            throw new PaymentException("Refund failed");
        }
        
        // Similar inventory update
        for (OrderItem item : order.getItems()) {
            inventoryService.updateStock(item.getProductId(), item.getQuantity());
        }
    }
}
''',
                expected_issues=[
                    {"type": "refactoring", "description": "重复代码：验证逻辑"},
                    {"type": "refactoring", "description": "重复代码：计算总价"},
                    {"type": "refactoring", "description": "重复代码：库存更新"}
                ],
                expected_score=60.0,
                tags=["refactoring", "duplicate_code"],
                difficulty="medium",
            ),
            TestCase(
                id="java_refactor_002",
                name="过长方法检测",
                description="测试检测过长方法的能力",
                language="java",
                code='''
public class ReportGenerator {
    public String generateReport(SalesData data, ReportConfig config) {
        // Method is too long and does too many things
        StringBuilder report = new StringBuilder();
        
        // Header
        report.append("SALES REPORT\\n");
        report.append("Date: ").append(new Date()).append("\\n");
        report.append("Period: ").append(config.getStartDate()).append(" to ").append(config.getEndDate()).append("\\n\\n");
        
        // Summary
        double totalSales = 0;
        int totalTransactions = 0;
        Map<String, Double> categorySales = new HashMap<>();
        
        for (Sale sale : data.getSales()) {
            if (sale.getDate().after(config.getStartDate()) && sale.getDate().before(config.getEndDate())) {
                totalSales += sale.getAmount();
                totalTransactions++;
                
                String category = sale.getCategory();
                categorySales.put(category, categorySales.getOrDefault(category, 0.0) + sale.getAmount());
            }
        }
        
        report.append("SUMMARY\\n");
        report.append("Total Sales: $").append(String.format("%.2f", totalSales)).append("\\n");
        report.append("Total Transactions: ").append(totalTransactions).append("\\n");
        report.append("Average Sale: $").append(String.format("%.2f", totalSales / totalTransactions)).append("\\n\\n");
        
        // Category breakdown
        report.append("CATEGORY BREAKDOWN\\n");
        for (Map.Entry<String, Double> entry : categorySales.entrySet()) {
            report.append(entry.getKey()).append(": $").append(String.format("%.2f", entry.getValue())).append("\\n");
        }
        report.append("\\n");
        
        // Top products
        report.append("TOP PRODUCTS\\n");
        Map<String, Integer> productSales = new HashMap<>();
        for (Sale sale : data.getSales()) {
            if (sale.getDate().after(config.getStartDate()) && sale.getDate().before(config.getEndDate())) {
                productSales.put(sale.getProductName(), productSales.getOrDefault(sale.getProductName(), 0) + sale.getQuantity());
            }
        }
        
        productSales.entrySet().stream()
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(10)
            .forEach(entry -> report.append(entry.getKey()).append(": ").append(entry.getValue()).append(" units\\n"));
        
        // Footer
        report.append("\\nGenerated by Report Generator v1.0");
        
        return report.toString();
    }
}
''',
                expected_issues=[
                    {"type": "refactoring", "description": "方法过长（超过50行）"},
                    {"type": "refactoring", "description": "单一职责原则违反"},
                    {"type": "refactoring", "description": "建议提取子方法"}
                ],
                expected_score=55.0,
                tags=["refactoring", "long_method"],
                difficulty="hard",
            ),
            TestCase(
                id="java_refactor_003",
                name="过深嵌套检测",
                description="测试检测过深嵌套的能力",
                language="java",
                code='''
public class DataValidator {
    public ValidationResult validate(DataRecord record) {
        ValidationResult result = new ValidationResult();
        
        if (record != null) {
            if (record.getType() != null) {
                if (record.getType().equals("PERSONAL")) {
                    PersonalData personal = (PersonalData) record;
                    if (personal.getName() != null) {
                        if (!personal.getName().isEmpty()) {
                            if (personal.getAge() > 0) {
                                if (personal.getAge() < 150) {
                                    if (personal.getEmail() != null) {
                                        if (personal.getEmail().contains("@")) {
                                            result.setValid(true);
                                        } else {
                                            result.addError("Invalid email format");
                                        }
                                    } else {
                                        result.addError("Email is required");
                                    }
                                } else {
                                    result.addError("Age must be less than 150");
                                }
                            } else {
                                result.addError("Age must be positive");
                            }
                        } else {
                            result.addError("Name cannot be empty");
                        }
                    } else {
                        result.addError("Name is required");
                    }
                } else if (record.getType().equals("BUSINESS")) {
                    // Similar nested validation...
                }
            } else {
                result.addError("Type is required");
            }
        } else {
            result.addError("Record cannot be null");
        }
        
        return result;
    }
}
''',
                expected_issues=[
                    {"type": "refactoring", "description": "嵌套层次过深（超过4层）"},
                    {"type": "refactoring", "description": "建议使用卫语句"},
                    {"type": "refactoring", "description": "建议提取验证方法"}
                ],
                expected_score=50.0,
                tags=["refactoring", "deep_nesting"],
                difficulty="hard",
            ),
        ]