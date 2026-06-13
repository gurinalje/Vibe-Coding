"""
Security Scanner for AI Agent Benchmark system.

This module provides security scanning capabilities including
vulnerability detection, secret scanning, and dependency analysis.
"""

import re
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Set
import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class VulnerabilitySeverity(str, Enum):
    """Vulnerability severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VulnerabilityType(str, Enum):
    """Types of vulnerabilities."""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    HARDCODED_SECRET = "hardcoded_secret"
    WEAK_CRYPTOGRAPHY = "weak_cryptography"
    INSECURE_RANDOM = "insecure_random"
    SSRF = "ssrf"
    XXE = "xxe"
    BROKEN_AUTH = "broken_auth"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"


@dataclass
class SecurityVulnerability:
    """A security vulnerability."""
    id: str
    type: VulnerabilityType
    severity: VulnerabilitySeverity
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert vulnerability to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "recommendation": self.recommendation,
            "cwe_id": self.cwe_id,
            "cvss_score": self.cvss_score,
        }


@dataclass
class SecretFinding:
    """A found secret or credential."""
    id: str
    type: str
    secret_hash: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    line_content: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "secret_hash": self.secret_hash,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "line_content": self.line_content,
        }


@dataclass
class ScanResult:
    """Security scan result."""
    vulnerabilities: List[SecurityVulnerability]
    secrets: List[SecretFinding]
    risk_score: float
    summary: str
    recommendations: List[str]
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "secrets": [s.to_dict() for s in self.secrets],
            "risk_score": self.risk_score,
            "summary": self.summary,
            "recommendations": self.recommendations,
            "metrics": self.metrics,
        }


class SecurityScanner:
    """Security scanner for code analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize security scanner.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.scan_rules = self._load_scan_rules()
        self.secret_patterns = self._load_secret_patterns()
        
        logger.info("Security scanner initialized")
    
    def _load_scan_rules(self) -> Dict[str, Any]:
        """Load security scanning rules."""
        return {
            "python": {
                "sql_injection": [
                    (r"execute\s*\(\s*['\"].*%s", "Possible SQL injection via string formatting"),
                    (r"execute\s*\(\s*f['\"]", "Possible SQL injection via f-string"),
                    (r"execute\s*\(\s*['\"].*\+", "Possible SQL injection via concatenation"),
                ],
                "command_injection": [
                    (r"os\.system\s*\(", "Use of os.system()"),
                    (r"os\.popen\s*\(", "Use of os.popen()"),
                    (r"subprocess\.\w+\s*\(.*shell\s*=\s*True", "subprocess with shell=True"),
                    (r"eval\s*\(", "Use of eval()"),
                    (r"exec\s*\(", "Use of exec()"),
                ],
                "path_traversal": [
                    (r"open\s*\(\s*['\"].*\+", "Possible path traversal"),
                    (r"os\.path\.join\s*\(.*\.\.", "Path traversal with .."),
                ],
                "insecure_deserialization": [
                    (r"pickle\.loads?\s*\(", "Insecure deserialization with pickle"),
                    (r"yaml\.load\s*\(\s*[^,]+\s*\)", "yaml.load without Loader"),
                    (r"marshal\.loads?\s*\(", "Insecure deserialization with marshal"),
                ],
                "weak_cryptography": [
                    (r"md5\s*\(", "Use of MD5"),
                    (r"sha1\s*\(", "Use of SHA1"),
                    (r"DES\s*\(", "Use of DES"),
                    (r"RC4\s*\(", "Use of RC4"),
                ],
                "insecure_random": [
                    (r"random\.\w+\s*\(", "Use of non-cryptographic random"),
                ],
            },
            "java": {
                "sql_injection": [
                    (r"Statement\.execute\s*\(", "Direct SQL statement execution"),
                    (r"createStatement\s*\(\)", "Creating SQL statement directly"),
                ],
                "command_injection": [
                    (r"Runtime\.getRuntime\(\)\.exec\s*\(", "Runtime.exec()"),
                    (r"ProcessBuilder\s*\(", "ProcessBuilder usage"),
                ],
                "xss": [
                    (r"response\.getWriter\(\)\.print", "Direct output to response"),
                    (r"innerHTML\s*=", "Direct innerHTML assignment"),
                ],
                "broken_auth": [
                    (r"密码.*=.*['\"]", "Hardcoded password"),
                    (r"password.*=.*['\"]", "Hardcoded password"),
                ],
            },
            "javascript": {
                "xss": [
                    (r"innerHTML\s*=", "Direct innerHTML assignment"),
                    (r"document\.write\s*\(", "Use of document.write()"),
                    (r"\.html\s*\(", "jQuery .html() usage"),
                    (r"eval\s*\(", "Use of eval()"),
                ],
                "prototype_pollution": [
                    (r"__proto__", "Prototype pollution attempt"),
                    (r"constructor\s*\[", "Constructor manipulation"),
                ],
                "insecure_random": [
                    (r"Math\.random\s*\(", "Use of Math.random()"),
                ],
            },
        }
    
    def _load_secret_patterns(self) -> List[Tuple[str, str]]:
        """Load secret detection patterns."""
        return [
            (r"(?:password|passwd|pwd)\s*[=:]\s*['\"]([^'\"]+)['\"]", "Password"),
            (r"(?:api[_-]?key|apikey)\s*[=:]\s*['\"]([^'\"]+)['\"]", "API Key"),
            (r"(?:secret|secret[_-]?key)\s*[=:]\s*['\"]([^'\"]+)['\"]", "Secret Key"),
            (r"(?:token|access[_-]?token|auth[_-]?token)\s*[=:]\s*['\"]([^'\"]+)['\"]", "Token"),
            (r"(?:private[_-]?key)\s*[=:]\s*['\"]([^'\"]+)['\"]", "Private Key"),
            (r"(?:aws[_-]?access[_-]?key[_-]?id)\s*[=:]\s*['\"]([^'\"]+)['\"]", "AWS Access Key"),
            (r"(?:aws[_-]?secret[_-]?access[_-]?key)\s*[=:]\s*['\"]([^'\"]+)['\"]", "AWS Secret Key"),
            (r"(?:github[_-]?token|gh[_-]?token)\s*[=:]\s*['\"]([^'\"]+)['\"]", "GitHub Token"),
            (r"(?:slack[_-]?token)\s*[=:]\s*['\"]([^'\"]+)['\"]", "Slack Token"),
            (r"(?:database[_-]?url|db[_-]?url|dsn)\s*[=:]\s*['\"]([^'\"]+)['\"]", "Database URL"),
            (r"(?:connection[_-]?string)\s*[=:]\s*['\"]([^'\"]+)['\"]", "Connection String"),
            (r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----", "Private Key"),
        ]
    
    async def scan(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None
    ) -> ScanResult:
        """
        Scan code for security issues.
        
        Args:
            code: Code to scan
            language: Programming language
            file_path: Optional file path
            
        Returns:
            Scan result
        """
        logger.info(f"Scanning {language} code for security issues")
        
        vulnerabilities = []
        secrets = []
        
        # Scan for vulnerabilities
        vulnerabilities.extend(self._scan_vulnerabilities(code, language, file_path))
        
        # Scan for secrets
        secrets.extend(self._scan_secrets(code, file_path))
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(vulnerabilities, secrets)
        
        # Generate summary
        summary = self._generate_summary(vulnerabilities, secrets, risk_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(vulnerabilities, secrets)
        
        # Calculate metrics
        metrics = self._calculate_metrics(vulnerabilities, secrets)
        
        logger.info(f"Scan completed. Risk score: {risk_score:.1f}/100")
        
        return ScanResult(
            vulnerabilities=vulnerabilities,
            secrets=secrets,
            risk_score=risk_score,
            summary=summary,
            recommendations=recommendations,
            metrics=metrics,
        )
    
    def _scan_vulnerabilities(
        self,
        code: str,
        language: str,
        file_path: Optional[str]
    ) -> List[SecurityVulnerability]:
        """Scan for security vulnerabilities."""
        vulnerabilities = []
        
        # Get rules for language
        rules = self.scan_rules.get(language, {})
        
        for vuln_type, patterns in rules.items():
            for pattern, description in patterns:
                for match in re.finditer(pattern, code, re.MULTILINE):
                    # Get line number
                    line_start = code[:match.start()].count('\n') + 1
                    line_content = code.split('\n')[line_start - 1].strip() if line_start <= len(code.split('\n')) else ""
                    
                    # Create vulnerability
                    vuln = SecurityVulnerability(
                        id=f"{vuln_type}_{line_start}_{hash(pattern)}",
                        type=self._map_vuln_type(vuln_type),
                        severity=self._get_vuln_severity(vuln_type),
                        title=self._get_vuln_title(vuln_type),
                        description=description,
                        file_path=file_path,
                        line_number=line_start,
                        code_snippet=line_content[:200],
                        recommendation=self._get_vuln_recommendation(vuln_type),
                        cwe_id=self._get_cwe_id(vuln_type),
                    )
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _scan_secrets(
        self,
        code: str,
        file_path: Optional[str]
    ) -> List[SecretFinding]:
        """Scan for hardcoded secrets."""
        secrets = []
        
        for i, line in enumerate(code.split('\n'), 1):
            for pattern, secret_type in self.secret_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Create hash of the secret
                    secret_value = match.group(1) if match.groups() else match.group(0)
                    secret_hash = hashlib.sha256(secret_value.encode()).hexdigest()[:16]
                    
                    secret = SecretFinding(
                        id=f"secret_{i}_{hash(pattern)}",
                        type=secret_type,
                        secret_hash=secret_hash,
                        file_path=file_path,
                        line_number=i,
                        line_content=line.strip()[:200],
                    )
                    secrets.append(secret)
        
        return secrets
    
    def _map_vuln_type(self, vuln_type: str) -> VulnerabilityType:
        """Map vulnerability type string to enum."""
        mapping = {
            "sql_injection": VulnerabilityType.SQL_INJECTION,
            "xss": VulnerabilityType.XSS,
            "command_injection": VulnerabilityType.COMMAND_INJECTION,
            "path_traversal": VulnerabilityType.PATH_TRAVERSAL,
            "insecure_deserialization": VulnerabilityType.INSECURE_DESERIALIZATION,
            "weak_cryptography": VulnerabilityType.WEAK_CRYPTOGRAPHY,
            "insecure_random": VulnerabilityType.INSECURE_RANDOM,
            "prototype_pollution": VulnerabilityType.XSS,  # Map to XSS
        }
        return mapping.get(vuln_type, VulnerabilityType.SENSITIVE_DATA_EXPOSURE)
    
    def _get_vuln_severity(self, vuln_type: str) -> VulnerabilitySeverity:
        """Get severity for vulnerability type."""
        severity_map = {
            "sql_injection": VulnerabilitySeverity.CRITICAL,
            "command_injection": VulnerabilitySeverity.CRITICAL,
            "insecure_deserialization": VulnerabilitySeverity.HIGH,
            "xss": VulnerabilitySeverity.HIGH,
            "path_traversal": VulnerabilitySeverity.HIGH,
            "weak_cryptography": VulnerabilitySeverity.MEDIUM,
            "insecure_random": VulnerabilitySeverity.LOW,
            "prototype_pollution": VulnerabilitySeverity.MEDIUM,
        }
        return severity_map.get(vuln_type, VulnerabilitySeverity.MEDIUM)
    
    def _get_vuln_title(self, vuln_type: str) -> str:
        """Get title for vulnerability type."""
        title_map = {
            "sql_injection": "SQL 注入漏洞",
            "command_injection": "命令注入漏洞",
            "xss": "跨站脚本攻击 (XSS)",
            "path_traversal": "路径遍历漏洞",
            "insecure_deserialization": "不安全的反序列化",
            "weak_cryptography": "弱加密算法",
            "insecure_random": "不安全的随机数生成",
            "prototype_pollution": "原型链污染",
        }
        return title_map.get(vuln_type, "安全漏洞")
    
    def _get_vuln_recommendation(self, vuln_type: str) -> str:
        """Get recommendation for vulnerability type."""
        rec_map = {
            "sql_injection": "使用参数化查询或 ORM，避免直接拼接 SQL",
            "command_injection": "避免使用系统命令，使用安全的替代方案",
            "xss": "对输出进行编码，使用内容安全策略 (CSP)",
            "path_traversal": "验证和清理文件路径，使用白名单",
            "insecure_deserialization": "避免反序列化不可信数据，使用安全的序列化格式",
            "weak_cryptography": "使用现代加密算法（如 AES-256、SHA-256）",
            "insecure_random": "使用加密安全的随机数生成器",
            "prototype_pollution": "避免使用不受信任的对象键，使用 Object.create(null)",
        }
        return rec_map.get(vuln_type, "遵循安全编码最佳实践")
    
    def _get_cwe_id(self, vuln_type: str) -> str:
        """Get CWE ID for vulnerability type."""
        cwe_map = {
            "sql_injection": "CWE-89",
            "command_injection": "CWE-78",
            "xss": "CWE-79",
            "path_traversal": "CWE-22",
            "insecure_deserialization": "CWE-502",
            "weak_cryptography": "CWE-327",
            "insecure_random": "CWE-330",
            "prototype_pollution": "CWE-1321",
        }
        return cwe_map.get(vuln_type, "CWE-0")
    
    def _calculate_risk_score(
        self,
        vulnerabilities: List[SecurityVulnerability],
        secrets: List[SecretFinding]
    ) -> float:
        """Calculate risk score (0-100)."""
        if not vulnerabilities and not secrets:
            return 0.0
        
        # Severity weights
        severity_weights = {
            VulnerabilitySeverity.CRITICAL: 25.0,
            VulnerabilitySeverity.HIGH: 15.0,
            VulnerabilitySeverity.MEDIUM: 8.0,
            VulnerabilitySeverity.LOW: 3.0,
            VulnerabilitySeverity.INFO: 1.0,
        }
        
        # Calculate vulnerability score
        vuln_score = sum(severity_weights.get(v.severity, 5.0) for v in vulnerabilities)
        
        # Add secret score
        secret_score = len(secrets) * 10.0
        
        # Normalize to 0-100
        total_score = vuln_score + secret_score
        normalized_score = min(100.0, total_score)
        
        return normalized_score
    
    def _generate_summary(
        self,
        vulnerabilities: List[SecurityVulnerability],
        secrets: List[SecretFinding],
        risk_score: float
    ) -> str:
        """Generate scan summary."""
        parts = []
        
        if vulnerabilities:
            parts.append(f"发现 {len(vulnerabilities)} 个安全漏洞")
        
        if secrets:
            parts.append(f"发现 {len(secrets)} 个硬编码密钥")
        
        if not parts:
            return "未发现安全问题"
        
        # Add risk level
        if risk_score >= 75:
            parts.append("风险等级: 高")
        elif risk_score >= 50:
            parts.append("风险等级: 中")
        elif risk_score >= 25:
            parts.append("风险等级: 低")
        else:
            parts.append("风险等级: 极低")
        
        return "。".join(parts)
    
    def _generate_recommendations(
        self,
        vulnerabilities: List[SecurityVulnerability],
        secrets: List[SecretFinding]
    ) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        # Group vulnerabilities by type
        vuln_types = set(v.type for v in vulnerabilities)
        
        for vuln_type in vuln_types:
            if vuln_type == VulnerabilityType.SQL_INJECTION:
                recommendations.append("使用参数化查询或 ORM 防止 SQL 注入")
            elif vuln_type == VulnerabilityType.COMMAND_INJECTION:
                recommendations.append("避免使用系统命令，使用安全的替代方案")
            elif vuln_type == VulnerabilityType.XSS:
                recommendations.append("对用户输入进行验证和编码，使用 CSP")
            elif vuln_type == VulnerabilityType.WEAK_CRYPTOGRAPHY:
                recommendations.append("升级到现代加密算法（AES-256、SHA-256）")
            elif vuln_type == VulnerabilityType.INSECURE_RANDOM:
                recommendations.append("使用 secrets 模块替代 random 模块")
        
        if secrets:
            recommendations.append("将敏感信息移至环境变量或密钥管理服务")
            recommendations.append("使用 .gitignore 排除包含敏感信息的文件")
        
        # General recommendations
        recommendations.append("定期进行安全审计和依赖更新")
        recommendations.append("实施输入验证和输出编码")
        
        return list(set(recommendations))
    
    def _calculate_metrics(
        self,
        vulnerabilities: List[SecurityVulnerability],
        secrets: List[SecretFinding]
    ) -> Dict[str, Any]:
        """Calculate security metrics."""
        # Count by severity
        severity_counts = {}
        for v in vulnerabilities:
            severity_counts[v.severity.value] = severity_counts.get(v.severity.value, 0) + 1
        
        # Count by type
        type_counts = {}
        for v in vulnerabilities:
            type_counts[v.type.value] = type_counts.get(v.type.value, 0) + 1
        
        return {
            "total_vulnerabilities": len(vulnerabilities),
            "total_secrets": len(secrets),
            "severity_distribution": severity_counts,
            "type_distribution": type_counts,
            "critical_count": severity_counts.get("critical", 0),
            "high_count": severity_counts.get("high", 0),
            "medium_count": severity_counts.get("medium", 0),
            "low_count": severity_counts.get("low", 0),
        }