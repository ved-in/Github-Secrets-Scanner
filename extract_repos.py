import os
import zipfile
import json
import re

ZIP_DIR = "downloads"
SIG_P = "signatures.json"
MAX_SZ = 10 * 1024 * 1024

# Whitelisted file extensions to scan
WL_EXT = (
    ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".yml", ".yaml", ".xml",
    ".txt", ".env", ".ini", ".conf", ".config", ".sh", ".bash", ".php",
    ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rb", ".swift",
    ".kt", ".kts", ".rs", ".sql", ".md", ".toml", ".properties", "tfvars",
    ".tf", ".hcl", ".gradle", ".plist", ".cfg", ".envrc", ".lua", ".dart",
    ".zsh", ".fish", ".bat", ".cmd", ".psm1", "ps1"
)
WL_NAMES = ("dockerfile", "makefile", "gemfile")

with open(SIG_P, "r", encoding="utf-8") as f:
    sigs = json.load(f).get("signatures", [])
SIGS = [(s.get("name", ""), re.compile(s.get("pattern", ""))) for s in sigs if s.get("name") and s.get("pattern")]


def scan_zip(zp):
    zp_p = os.path.join(ZIP_DIR, zp)
    hits = []

    try:
        zf = zipfile.ZipFile(zp_p, "r")
    except Exception:
        print(f"Bad zip: {zp}")
        return

    with zf:
        for zi in zf.infolist():
            if zi.is_dir() or zi.file_size > MAX_SZ:
                continue

            fp = zi.filename
            low = fp.lower()
            base = os.path.basename(low)
            if not (low.endswith(WL_EXT) or base in WL_NAMES):
                continue

            try:
                raw = zf.read(zi).decode("utf-8", errors="ignore")
            except Exception:
                continue

            for ln, line in enumerate(raw.splitlines(), 1):
                for nm, rgx in SIGS:
                    for hit in rgx.finditer(line):
                        hits.append({
                            "file": fp,
                            "line": ln,
                            "type": nm,
                            "secret": hit.group(0),
                        })

    if not hits:
        print(f"[-] {zp} -> clean")
        return

    print(f"[+] {zp} -> {len(hits)} hits")
    for h in hits:
        print(f"    {h['type']} | {h['file']}:{h['line']}")


def scan_all():
    if not os.path.isdir(ZIP_DIR):
        print("downloads folder not found")
        return

    zps = [f for f in os.listdir(ZIP_DIR) if f.endswith(".zip")]

    if not zps:
        print("No zip files found to scan")
        return

    for zp in zps:
        scan_zip(zp)


if __name__ == "__main__":
    print("Scanning downloaded GitHub repo zips")
    scan_all()