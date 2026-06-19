"""
Vibe Coding CLI - Beautiful terminal interface for AI-powered code analysis.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.rule import Rule
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.code_analyzer_v2 import CodeAnalyzer
from core.security_scanner import SecurityScanner
from core.refactoring_engine import RefactoringEngine
from agents.coordinator import AgentCoordinator

console = Console() if HAS_RICH else None


def print_banner():
    if HAS_RICH:
        console.print(Panel(
            "[bold cyan]VIBE CODING[/bold cyan]\n[dim]  AI-Powered Multi-Agent Code Analysis System[/dim]",
            border_style="cyan", padding=(0, 2)))
    else:
        print("=" * 50)
        print("  Vibe Coding - AI Code Analysis")
        print("=" * 50)


def detect_language(file_path: str) -> Optional[str]:
    ext_map = {
        ".py": "python", ".java": "java", ".js": "javascript",
        ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript",
    }
    return ext_map.get(Path(file_path).suffix.lower())


def get_source_files(target, language=None):
    if os.path.isfile(target):
        return [target] if (language or detect_language(target)) else []
    files = []
    for root, dirs, filenames in os.walk(target):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", "node_modules", ".venv", "venv", "dist", "build", ".tox"}]
        for fname in filenames:
            fpath = os.path.join(root, fname)
            if detect_language(fpath):
                files.append(fpath)
    return files


async def analyze_files(files, language=None):
    analyzer = CodeAnalyzer()
    scanner = SecurityScanner()
    results = []
    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
            lang = language or detect_language(fpath)
            if not lang:
                continue
            result = await analyzer.analyze(code, lang, fpath)
            security = await scanner.scan(code, lang)
            issues = result.issues
            results.append({
                "path": fpath, "language": lang, "score": result.quality_score,
                "issues": len(issues), "metrics": result.metrics, "issue_list": issues,
                "critical": sum(1 for i in issues if i.severity == "critical"),
                "warnings": sum(1 for i in issues if i.severity == "warning"),
                "security": security,
            })
        except Exception as e:
            if HAS_RICH:
                console.print(f"[red]  Error: {fpath}: {e}[/red]")
    return results


def display_results(file_results, total_issues):
    if not HAS_RICH:
        for r in file_results:
            print(f"  {r['path']}: score={r['score']:.1f}, issues={r['issues']}")
        return

    console.print()
    console.print(Rule("[bold]Analysis Results[/bold]"))
    console.print()

    summary = Table(show_header=False, box=box.SIMPLE)
    summary.add_column("Metric", style="bold")
    summary.add_column("Value", justify="right")
    summary.add_row("Files Analyzed", str(len(file_results)))
    summary.add_row("Total Issues", f"[red]{total_issues}[/red]" if total_issues else "0")
    avg_score = sum(r["score"] for r in file_results) / max(1, len(file_results))
    sc = "green" if avg_score >= 80 else "yellow" if avg_score >= 60 else "red"
    summary.add_row("Avg Quality", f"[{sc}]{avg_score:.1f}/100[/{sc}]")
    console.print(Panel(summary, title="Summary", border_style="cyan"))

    if file_results:
        table = Table(title="File Analysis", box=box.ROUNDED)
        table.add_column("File", style="cyan", max_width=40)
        table.add_column("Lang", style="dim")
        table.add_column("Score", justify="right")
        table.add_column("Issues", justify="right")
        table.add_column("Critical", justify="right")
        for r in sorted(file_results, key=lambda x: x["score"]):
            sc = "green" if r["score"] >= 80 else "yellow" if r["score"] >= 60 else "red"
            table.add_row(
                os.path.basename(r["path"]), r["language"],
                f"[{sc}]{r['score']:.1f}[/{sc}]", str(r["issues"]),
                f"[red]{r['critical']}[/red]" if r["critical"] else "0")
        console.print(table)

    all_issues = []
    for r in file_results:
        for issue in r["issue_list"]:
            all_issues.append({"file": os.path.basename(r["path"]), "severity": issue.severity,
                               "category": issue.category, "message": issue.message, "line": issue.line_number})
    if all_issues:
        severity_order = {"critical": 0, "error": 1, "warning": 2, "info": 3}
        all_issues.sort(key=lambda x: severity_order.get(x["severity"], 4))
        console.print()
        it = Table(title="Top Issues", box=box.ROUNDED)
        it.add_column("Severity", width=10)
        it.add_column("File", style="cyan", max_width=25)
        it.add_column("Category", style="dim")
        it.add_column("Message", max_width=50)
        styles = {"critical": "red bold", "error": "red", "warning": "yellow", "info": "blue"}
        for issue in all_issues[:15]:
            s = styles.get(issue["severity"], "dim")
            it.add_row(f"[{s}]{issue['severity'].upper()}[/{s}]", issue["file"], issue["category"],
                       issue["message"], str(issue["line"]) if issue["line"] else "-")
        console.print(it)


async def cmd_analyze(args):
    files = get_source_files(args.path, args.language)
    if not files:
        print("No supported source files found")
        return
    results = await analyze_files(files, args.language)
    total_issues = sum(r["issues"] for r in results)
    display_results(results, total_issues)
    if args.json:
        output = {"files": len(results), "total_issues": total_issues,
                  "results": [{"path": r["path"], "score": r["score"], "issues": r["issues"]} for r in results]}
        json_path = args.json if isinstance(args.json, str) and args.json != "True" else "analysis_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        if HAS_RICH:
            console.print(f"\n[green]Report saved to {json_path}[/green]")


async def cmd_review(args):
    target = args.path
    if not os.path.exists(target):
        print(f"Error: {target} not found")
        return
    language = args.language or detect_language(target)
    if not language:
        print("Cannot detect language. Use --language.")
        return
    with open(target, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    coordinator = AgentCoordinator()
    if HAS_RICH:
        console.print(Rule(f"[bold]Reviewing {os.path.basename(target)}[/bold]"))
        console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Running multi-agent review...", total=3)
        progress.update(task, description="[Reviewer] Analyzing code quality...")
        review_result = await coordinator.review_code(code, language, target)
        progress.advance(task)
        progress.update(task, description="[Developer] Generating refactoring suggestions...")
        refactor_result = await coordinator.refactor_code(code, language, target)
        progress.advance(task)
        progress.update(task, description="[Critic] Evaluating review quality...")
        criticism_result = await coordinator.criticize_code(code, language, {"review_result": review_result})
        progress.advance(task)

    if HAS_RICH:
        score = review_result.get("score", 0)
        sc = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        console.print(Panel(
            f"Quality Score: [{sc}]{score:.1f}/100[/{sc}]\n"
            f"Issues: {len(review_result.get('issues', []))}\n"
            f"{review_result.get('summary', '')}",
            title="[bold blue]Reviewer Agent[/bold blue]", border_style="blue"))

        suggestions = refactor_result.get("suggestions", [])
        console.print(Panel(
            f"Suggestions: {len(suggestions)}" +
            ("\nRefactored code available" if refactor_result.get("refactored_code") else ""),
            title="[bold green]Developer Agent[/bold green]", border_style="green"))

        crit_score = criticism_result.get("score", 0)
        console.print(Panel(
            f"Review Quality: {crit_score:.1f}/100\n"
            f"Missed Issues: {len(criticism_result.get('missed_issues', []))}",
            title="[bold yellow]Critic Agent[/bold yellow]", border_style="yellow"))

        recs = review_result.get("recommendations", [])
        if recs:
            console.print("\n[bold]Recommendations:[/bold]")
            for i, rec in enumerate(recs, 1):
                console.print(f"  {i}. {rec}")
    else:
        print(f"Score: {review_result.get('score', 0):.1f}")
        print(f"Issues: {len(review_result.get('issues', []))}")


async def cmd_fix(args):
    target = args.path
    if not os.path.exists(target):
        print(f"Error: {target} not found")
        return
    language = args.language or detect_language(target)
    if not language:
        print("Cannot detect language.")
        return
    with open(target, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    coordinator = AgentCoordinator()
    if HAS_RICH:
        console.print(Rule(f"[bold]Auto-Fix: {os.path.basename(target)}[/bold]"))
        console.print()

    refactor_result = await coordinator.refactor_code(code, language, target)
    refactored = refactor_result.get("refactored_code")
    changes = refactor_result.get("changes_made", [])

    if not refactored or not changes:
        msg = "[green]No fixes needed! Code looks good.[/green]" if HAS_RICH else "No fixes needed."
        if HAS_RICH:
            console.print(msg)
        else:
            print(msg)
        return

    if HAS_RICH:
        console.print(f"[bold]Found {len(changes)} fix(es):[/bold]")
        for c in changes[:5]:
            console.print(f"  - {c}")

    if args.dry_run:
        if HAS_RICH:
            console.print("\n[yellow]Dry run - showing refactored code:[/yellow]")
            syntax = Syntax(refactored, language, theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Refactored Code"))
    else:
        backup_path = target + ".bak"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(code)
        with open(target, "w", encoding="utf-8") as f:
            f.write(refactored)
        if HAS_RICH:
            console.print(f"\n[green]Fixes applied![/green]")
            console.print(f"[dim]Backup: {backup_path}[/dim]")
        else:
            print(f"Fixes applied. Backup: {backup_path}")


async def cmd_watch(args):
    target = args.path
    if not os.path.exists(target):
        print(f"Error: {target} not found")
        return
    analyzer = CodeAnalyzer()
    file_mtimes = {}
    if os.path.isdir(target):
        for root, dirs, filenames in os.walk(target):
            dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", "node_modules"}]
            for fname in filenames:
                fpath = os.path.join(root, fname)
                if detect_language(fpath):
                    file_mtimes[fpath] = os.path.getmtime(fpath)

    msg = f"Watching {len(file_mtimes)} files... (Ctrl+C to stop)"
    if HAS_RICH:
        console.print(f"[green]{msg}[/green]")
    else:
        print(msg)

    try:
        while True:
            await asyncio.sleep(2)
            for fpath in list(file_mtimes.keys()):
                try:
                    mtime = os.path.getmtime(fpath)
                    if mtime > file_mtimes[fpath]:
                        file_mtimes[fpath] = mtime
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            code = f.read()
                        lang = detect_language(fpath)
                        result = await analyzer.analyze(code, lang)
                        score = result.quality_score
                        if HAS_RICH:
                            sc = "green" if score >= 80 else "yellow" if score >= 60 else "red"
                            console.print(f"  [{sc}]{os.path.basename(fpath)}[/{sc}] Score: {score:.1f} | Issues: {len(result.issues)}")
                        else:
                            print(f"  {fpath}: score={score:.1f}, issues={len(result.issues)}")
                except Exception:
                    pass
    except KeyboardInterrupt:
        if HAS_RICH:
            console.print("\n[yellow]Stopped watching.[/yellow]")


async def cmd_git(args):
    from utils.git_utils import GitUtils
    git = GitUtils(args.repo or ".")
    if not git.is_git_repo():
        print("Not a git repository")
        return

    diff = git.get_staged_diff() if args.staged else git.get_diff(args.branch)
    if not diff:
        if HAS_RICH:
            console.print("[green]No changes found[/green]")
        return

    changed_files = git.get_changed_files(args.branch)
    if HAS_RICH:
        repo_info = git.get_repo_info()
        console.print(Rule("[bold]Git Analysis[/bold]"))
        console.print(f"  Branch: {repo_info.get('branch', 'unknown')}")
        console.print(f"  Changed Files: {len(changed_files)}")
        console.print()
        if changed_files:
            table = Table(title="Changed Files", box=box.ROUNDED)
            table.add_column("File", style="cyan")
            table.add_column("Language")
            for fpath in changed_files:
                table.add_row(fpath, detect_language(fpath) or "unknown")
            console.print(table)
        analyzer = CodeAnalyzer()
        for fpath in changed_files:
            content = git.get_file_content(fpath)
            if content:
                lang = detect_language(fpath)
                if lang:
                    result = await analyzer.analyze(content, lang)
                    score = result.quality_score
                    sc = "green" if score >= 80 else "yellow" if score >= 60 else "red"
                    console.print(f"  [{sc}]{fpath}[/{sc}] Score: {score:.1f} | Issues: {len(result.issues)}")
    else:
        print(f"Changed files: {len(changed_files)}")
        for f in changed_files:
            print(f"  {f}")


async def cmd_dashboard(args):
    try:
        from web.app import create_app
        import uvicorn
    except ImportError:
        print("Web dashboard requires: pip install fastapi uvicorn")
        return
    app = create_app()
    port = args.port or 8080
    if HAS_RICH:
        console.print(f"[green]Starting dashboard at http://localhost:{port}[/green]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()


def main():
    parser = argparse.ArgumentParser(prog="vibe", description="Vibe Coding - AI Code Analysis")
    subparsers = parser.add_subparsers(dest="command")

    ap = subparsers.add_parser("analyze", help="Analyze code files")
    ap.add_argument("path")
    ap.add_argument("--language", "-l")
    ap.add_argument("--json", "-j", nargs="?", const=True)

    rp = subparsers.add_parser("review", help="Multi-agent code review")
    rp.add_argument("path")
    rp.add_argument("--language", "-l")

    fp = subparsers.add_parser("fix", help="Auto-fix issues")
    fp.add_argument("path")
    fp.add_argument("--language", "-l")
    fp.add_argument("--dry-run", "-d", action="store_true")

    wp = subparsers.add_parser("watch", help="Watch for changes")
    wp.add_argument("path")

    gp = subparsers.add_parser("git", help="Analyze git diffs")
    gp.add_argument("--repo", "-r", default=".")
    gp.add_argument("--branch", "-b")
    gp.add_argument("--staged", "-s", action="store_true")

    dp = subparsers.add_parser("dashboard", help="Web dashboard")
    dp.add_argument("--port", "-p", type=int, default=8080)

    args = parser.parse_args()
    if not args.command:
        print_banner()
        parser.print_help()
        return
    print_banner()
    cmd_map = {"analyze": cmd_analyze, "review": cmd_review, "fix": cmd_fix,
               "watch": cmd_watch, "git": cmd_git, "dashboard": cmd_dashboard}
    if args.command in cmd_map:
        asyncio.run(cmd_map[args.command](args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
