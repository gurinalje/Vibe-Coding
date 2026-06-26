"""
Vibe Coding Web Dashboard - FastAPI-based visual analysis interface.
"""

import asyncio
import json
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi import FastAPI, UploadFile, File, Form, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from core.code_analyzer_v2 import CodeAnalyzer
from core.security_scanner import SecurityScanner
from agents.coordinator import AgentCoordinator


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vibe Coding - AI Code Analysis</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               background: #0d1117; color: #c9d1d9; min-height: 100vh; }
        .header { background: linear-gradient(135deg, #161b22, #0d1117);
                  padding: 2rem; border-bottom: 1px solid #30363d; }
        .header h1 { font-size: 2rem; color: #58a6ff; }
        .header p { color: #8b949e; margin-top: 0.5rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .upload-area { border: 2px dashed #30363d; border-radius: 12px;
                       padding: 3rem; text-align: center; margin: 2rem 0;
                       transition: all 0.3s; cursor: pointer; }
        .upload-area:hover { border-color: #58a6ff; background: rgba(88,166,255,0.05); }
        .upload-area.dragover { border-color: #58a6ff; background: rgba(88,166,255,0.1); }
        .upload-area input { display: none; }
        .upload-icon { font-size: 3rem; margin-bottom: 1rem; }
        .btn { background: #238636; color: white; border: none; padding: 0.75rem 1.5rem;
               border-radius: 6px; cursor: pointer; font-size: 1rem; transition: all 0.2s; }
        .btn:hover { background: #2ea043; }
        .btn:disabled { background: #21262d; color: #484f58; cursor: not-allowed; }
        .btn-secondary { background: #21262d; border: 1px solid #30363d; }
        .btn-secondary:hover { background: #30363d; }
        .results { display: none; margin-top: 2rem; }
        .results.show { display: block; }
        .score-card { background: #161b22; border: 1px solid #30363d; border-radius: 12px;
                      padding: 2rem; margin: 1rem 0; display: flex; align-items: center; gap: 2rem; }
        .score-circle { width: 120px; height: 120px; border-radius: 50%;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 2rem; font-weight: bold; flex-shrink: 0; }
        .score-good { background: rgba(46,160,67,0.15); color: #3fb950; border: 3px solid #3fb950; }
        .score-warn { background: rgba(210,153,34,0.15); color: #d29922; border: 3px solid #d29922; }
        .score-bad { background: rgba(248,81,73,0.15); color: #f85149; border: 3px solid #f85149; }
        .score-info { flex: 1; }
        .score-info h2 { font-size: 1.5rem; margin-bottom: 0.5rem; }
        .score-info p { color: #8b949e; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 1rem; margin: 1.5rem 0; }
        .metric-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px;
                       padding: 1.25rem; }
        .metric-card .label { color: #8b949e; font-size: 0.85rem; text-transform: uppercase; }
        .metric-card .value { font-size: 1.8rem; font-weight: bold; margin-top: 0.25rem; }
        .issues-table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
        .issues-table th { background: #161b22; padding: 0.75rem; text-align: left;
                           border-bottom: 2px solid #30363d; color: #8b949e; font-size: 0.85rem; }
        .issues-table td { padding: 0.75rem; border-bottom: 1px solid #21262d; }
        .issues-table tr:hover { background: rgba(88,166,255,0.05); }
        .badge { padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
        .badge-critical { background: rgba(248,81,73,0.15); color: #f85149; }
        .badge-error { background: rgba(248,81,73,0.1); color: #f85149; }
        .badge-warning { background: rgba(210,153,34,0.15); color: #d29922; }
        .badge-info { background: rgba(88,166,255,0.15); color: #58a6ff; }
        .tabs { display: flex; gap: 0; margin: 2rem 0 0; border-bottom: 1px solid #30363d; }
        .tab { padding: 0.75rem 1.5rem; cursor: pointer; color: #8b949e;
               border-bottom: 2px solid transparent; transition: all 0.2s; }
        .tab:hover { color: #c9d1d9; }
        .tab.active { color: #58a6ff; border-bottom-color: #58a6ff; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .loading { display: none; text-align: center; padding: 3rem; }
        .loading.show { display: block; }
        .spinner { width: 40px; height: 40px; border: 3px solid #30363d;
                   border-top-color: #58a6ff; border-radius: 50%;
                   animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .agents-section { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.5rem 0; }
        .agent-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem; }
        .agent-card h3 { margin-bottom: 0.75rem; }
        .agent-reviewer { border-top: 3px solid #58a6ff; }
        .agent-developer { border-top: 3px solid #3fb950; }
        .agent-critic { border-top: 3px solid #d29922; }
        .code-input { width: 100%; min-height: 200px; background: #0d1117; color: #c9d1d9;
                      border: 1px solid #30363d; border-radius: 8px; padding: 1rem;
                      font-family: 'Fira Code', 'Cascadia Code', monospace; font-size: 0.9rem;
                      resize: vertical; }
        .lang-select { background: #21262d; color: #c9d1d9; border: 1px solid #30363d;
                       border-radius: 6px; padding: 0.5rem 1rem; margin: 1rem 0; }
        @media (max-width: 768px) {
            .agents-section { grid-template-columns: 1fr; }
            .score-card { flex-direction: column; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>VIBE CODING</h1>
        <p>AI-Powered Multi-Agent Code Analysis System</p>
    </div>
    <div class="container">
        <div class="tabs">
            <div class="tab active" data-tab="upload">Upload File</div>
            <div class="tab" data-tab="paste">Paste Code</div>
            <div class="tab" data-tab="agents">Agent Analysis</div>
        </div>

        <div id="tab-upload" class="tab-content active">
            <div class="upload-area" id="dropZone">
                <div class="upload-icon">&#128196;</div>
                <h3>Drop your code file here</h3>
                <p style="color:#8b949e;margin:0.5rem 0">or click to browse</p>
                <p style="color:#484f58;font-size:0.85rem">Supports .py, .java, .js, .ts files</p>
                <input type="file" id="fileInput" accept=".py,.java,.js,.jsx,.ts,.tsx">
            </div>
        </div>

        <div id="tab-paste" class="tab-content">
            <select class="lang-select" id="langSelect">
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
            </select>
            <textarea class="code-input" id="codeInput" placeholder="Paste your code here..."></textarea>
            <div style="margin-top:1rem">
                <button class="btn" id="analyzeBtn" onclick="analyzeCode()">Analyze Code</button>
            </div>
        </div>

        <div id="tab-agents" class="tab-content">
            <select class="lang-select" id="agentLangSelect">
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="javascript">JavaScript</option>
            </select>
            <textarea class="code-input" id="agentCodeInput" placeholder="Paste code for multi-agent review..."></textarea>
            <div style="margin-top:1rem">
                <button class="btn" onclick="runAgentAnalysis()">Run Multi-Agent Review</button>
            </div>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Analyzing code...</p>
        </div>

        <div class="results" id="results">
            <div class="score-card" id="scoreCard">
                <div class="score-circle" id="scoreCircle">--</div>
                <div class="score-info">
                    <h2 id="scoreTitle">Quality Score</h2>
                    <p id="scoreDesc">Analyzing code quality...</p>
                </div>
            </div>

            <div class="metrics-grid" id="metricsGrid"></div>

            <table class="issues-table" id="issuesTable">
                <thead>
                    <tr><th>Severity</th><th>Category</th><th>Message</th><th>Line</th></tr>
                </thead>
                <tbody id="issuesBody"></tbody>
            </table>
        </div>

        <div id="agentResults" style="display:none">
            <div class="agents-section" id="agentsSection"></div>
            <div id="agentRecommendations" style="margin-top:1.5rem"></div>
        </div>
    </div>

    <script>
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
            });
        });

        // File upload
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', e => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
        });
        fileInput.addEventListener('change', e => { if (e.target.files.length) uploadFile(e.target.files[0]); });

        async function uploadFile(file) {
            showLoading();
            const formData = new FormData();
            formData.append('file', file);
            try {
                const resp = await fetch('/api/analyze', { method: 'POST', body: formData });
                const data = await resp.json();
                showResults(data);
            } catch (err) { showError(err.message); }
        }

        async function analyzeCode() {
            const code = document.getElementById('codeInput').value;
            const language = document.getElementById('langSelect').value;
            if (!code.trim()) return;
            showLoading();
            try {
                const resp = await fetch('/api/analyze-code', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code, language})
                });
                const data = await resp.json();
                showResults(data);
            } catch (err) { showError(err.message); }
        }

        async function runAgentAnalysis() {
            const code = document.getElementById('agentCodeInput').value;
            const language = document.getElementById('agentLangSelect').value;
            if (!code.trim()) return;
            showLoading();
            try {
                const resp = await fetch('/api/agent-review', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code, language})
                });
                const data = await resp.json();
                showAgentResults(data);
            } catch (err) { showError(err.message); }
        }

        function showLoading() {
            document.getElementById('loading').classList.add('show');
            document.getElementById('results').classList.remove('show');
            document.getElementById('agentResults').style.display = 'none';
        }

        function showResults(data) {
            document.getElementById('loading').classList.remove('show');
            document.getElementById('results').classList.add('show');
            document.getElementById('agentResults').style.display = 'none';

            const score = data.quality_score || 0;
            const circle = document.getElementById('scoreCircle');
            circle.textContent = score.toFixed(1);
            circle.className = 'score-circle ' + (score >= 80 ? 'score-good' : score >= 60 ? 'score-warn' : 'score-bad');
            document.getElementById('scoreTitle').textContent = 'Quality Score';
            document.getElementById('scoreDesc').textContent = data.summary || '';

            const metrics = data.metrics || {};
            const grid = document.getElementById('metricsGrid');
            grid.innerHTML = [
                {label: 'Code Lines', value: metrics.code_lines || 0},
                {label: 'Functions', value: metrics.functions || 0},
                {label: 'Complexity', value: metrics.cyclomatic_complexity || 0},
                {label: 'Issues', value: (data.issues || []).length},
            ].map(m => `<div class="metric-card"><div class="label">${m.label}</div><div class="value">${m.value}</div></div>`).join('');

            const tbody = document.getElementById('issuesBody');
            tbody.innerHTML = (data.issues || []).map(i => `
                <tr>
                    <td><span class="badge badge-${i.severity}">${i.severity.toUpperCase()}</span></td>
                    <td>${i.category}</td>
                    <td>${i.message}</td>
                    <td>${i.line_number || '-'}</td>
                </tr>`).join('');
        }

        function showAgentResults(data) {
            document.getElementById('loading').classList.remove('show');
            document.getElementById('results').classList.remove('show');
            document.getElementById('agentResults').style.display = 'block';

            const review = data.review || {};
            const refactor = data.refactor || {};
            const criticism = data.criticism || {};

            const section = document.getElementById('agentsSection');
            section.innerHTML = `
                <div class="agent-card agent-reviewer">
                    <h3>Reviewer Agent</h3>
                    <p>Score: <strong>${(review.score || 0).toFixed(1)}/100</strong></p>
                    <p>Issues: ${(review.issues || []).length}</p>
                    <p style="color:#8b949e;margin-top:0.5rem">${review.summary || ''}</p>
                </div>
                <div class="agent-card agent-developer">
                    <h3>Developer Agent</h3>
                    <p>Suggestions: ${(refactor.suggestions || []).length}</p>
                    <p>Changes: ${(refactor.changes_made || []).length}</p>
                    ${refactor.refactored_code ? '<p style="color:#3fb950">Refactored code available</p>' : ''}
                </div>
                <div class="agent-card agent-critic">
                    <h3>Critic Agent</h3>
                    <p>Review Quality: <strong>${(criticism.score || 0).toFixed(1)}/100</strong></p>
                    <p>Missed Issues: ${(criticism.missed_issues || []).length}</p>
                    <p>Evaluations: ${(criticism.evaluations || []).length}</p>
                </div>`;

            const recs = data.recommendations || [];
            document.getElementById('agentRecommendations').innerHTML = recs.length ?
                '<h3>Recommendations</h3><ul>' + recs.map(r => `<li>${r}</li>`).join('') + '</ul>' : '';
        }

        function showError(msg) {
            document.getElementById('loading').classList.remove('show');
            alert('Error: ' + msg);
        }
    </script>
</body>
</html>"""


def create_app():
    if not HAS_FASTAPI:
        raise ImportError("FastAPI is required for the web dashboard")

    app = FastAPI(title="Vibe Coding", description="AI-Powered Code Analysis")

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return DASHBOARD_HTML

    @app.post("/api/analyze")
    async def api_analyze(file: UploadFile = File(...)):
        content = await file.read()
        code = content.decode("utf-8", errors="ignore")
        ext_map = {".py": "python", ".java": "java", ".js": "javascript", ".ts": "typescript"}
        language = ext_map.get(os.path.splitext(file.filename or "")[1].lower(), "python")
        return await _analyze_code(code, language)

    @app.post("/api/analyze-code")
    async def api_analyze_code(body: dict):
        code = body.get("code", "")
        language = body.get("language", "python")
        return await _analyze_code(code, language)

    @app.post("/api/agent-review")
    async def api_agent_review(body: dict):
        code = body.get("code", "")
        language = body.get("language", "python")
        coordinator = AgentCoordinator()
        review = await coordinator.review_code(code, language)
        refactor = await coordinator.refactor_code(code, language)
        criticism = await coordinator.criticize_code(code, language, {"review_result": review})
        return {
            "review": review,
            "refactor": refactor,
            "criticism": criticism,
            "recommendations": review.get("recommendations", []),
        }

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    return app


async def _analyze_code(code: str, language: str):
    analyzer = CodeAnalyzer()
    scanner = SecurityScanner()
    result = await analyzer.analyze(code, language)
    security = await scanner.scan(code, language)
    return {
        "quality_score": result.quality_score,
        "summary": result.summary,
        "metrics": {
            "lines_of_code": result.metrics.lines_of_code,
            "code_lines": result.metrics.code_lines,
            "functions": result.metrics.functions,
            "classes": result.metrics.classes,
            "cyclomatic_complexity": result.metrics.cyclomatic_complexity,
            "maintainability_index": result.metrics.maintainability_index,
        },
        "issues": [
            {"severity": i.severity, "category": i.category, "message": i.message, "line_number": i.line_number}
            for i in result.issues
        ],
    }
