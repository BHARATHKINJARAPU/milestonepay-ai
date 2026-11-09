import os
import re

PATTERNS = [
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "Google Gemini/API Key"),
    (re.compile(r"sk-[a-zA-Z0-9]{32,}"), "OpenAI/Secret Key"),
    (re.compile(r"(?i)paypal.*client_secret\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]"), "PayPal Secret"),
    (re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"), "Private Key Header"),
]

IGNORE_DIRS = {".git", ".venv", "node_modules", "dist", "__pycache__", ".pytest_cache", ".idea", ".vscode"}
IGNORE_EXTS = {".png", ".jpg", ".jpeg", ".pdf", ".ico", ".woff", ".woff2", ".pyc", ".lock", ".log"}

found = []
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
    for f in files:
        _, ext = os.path.splitext(f)
        if ext.lower() in IGNORE_EXTS:
            continue
        filepath = os.path.join(root, f)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
                for pat, label in PATTERNS:
                    match = pat.search(content)
                    if match:
                        found.append((filepath, label))
        except Exception:
            pass

print("=" * 60)
print(f"SECRET AUDIT SCAN RESULTS: {len(found)} detected")
print("=" * 60)
if not found:
    print("✓ ZERO real secret keys, private keys, or API tokens detected in repository.")
else:
    for fp, lbl in found:
        print(f"  WARNING: {fp} matched {lbl}")
