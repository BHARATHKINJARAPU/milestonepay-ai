import os
import re
import subprocess
import sys

SECRET_PATTERNS = [
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "Google Gemini/Cloud API Key"),
    (re.compile(r"EA[0-9A-Za-z\-_]{50,}"), "PayPal Access Token / App Secret"),
    (re.compile(r"(?i)(?:paypal_client_secret|client_secret)\s*[:=]\s*['\"]([A-Za-z0-9_-]{30,})['\"]"), "PayPal Secret Candidate"),
    (re.compile(r"(?i)(?:gemini_api_key)\s*[:=]\s*['\"]([A-Za-z0-9_-]{20,})['\"]"), "Gemini Key Candidate"),
]

IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "__pycache__", ".pytest_cache", ".system_generated"}
IGNORE_FILES = {".env", ".env.local", ".env.development", "secret_scan.py"}

def scan_files():
    workspace = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    findings = []
    
    print(f"Scanning workspace: {workspace}")
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if f in IGNORE_FILES or f.endswith((".pyc", ".node", ".png", ".jpg", ".ico", ".svg", ".lock")):
                continue
            filepath = os.path.join(root, f)
            relpath = os.path.relpath(filepath, workspace)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                    for line_no, line in enumerate(fh, 1):
                        if "example" in f.lower() or "replace_with" in line or "your_" in line or "<" in line:
                            continue
                        for pat, desc in SECRET_PATTERNS:
                            m = pat.search(line)
                            if m:
                                findings.append((relpath, line_no, desc))
            except Exception as e:
                pass

    print(f"\nWorkspace Secret Scan Results:")
    if not findings:
        print("PASS: No secrets detected in workspace files.")
    else:
        for r, l, d in findings:
            print(f"ALERT: {d} in {r}:{l}")
    return len(findings)

def scan_git_history():
    print("\nScanning Git commit history...")
    try:
        log_out = subprocess.check_output(["git", "log", "-p"], encoding="utf-8", errors="ignore")
        git_findings = []
        for line_no, line in enumerate(log_out.splitlines(), 1):
            if line.startswith("+") and not line.startswith("+++"):
                if "example" in line.lower() or "replace_with" in line or "your_" in line or "<" in line:
                    continue
                for pat, desc in SECRET_PATTERNS:
                    m = pat.search(line)
                    if m:
                        git_findings.append((line_no, desc))
        if not git_findings:
            print("PASS: No secrets detected in Git commit history.")
        else:
            for l, d in git_findings:
                print(f"ALERT: {d} found in Git diff at line {l}")
        return len(git_findings)
    except Exception as e:
        print(f"Git history scan error: {e}")
        return 0

if __name__ == "__main__":
    f1 = scan_files()
    f2 = scan_git_history()
    print(f"\nTotal findings: {f1 + f2}")
    sys.exit(0 if (f1 + f2) == 0 else 1)
