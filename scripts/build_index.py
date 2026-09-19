#!/usr/bin/env python3
"""Scan logs/, minutes/ and docs/ and write content/index.json.

No dependencies beyond the standard library so it runs anywhere: on the
GitHub Actions runner, or locally with `python3 scripts/build_index.py`.
"""

import json
import os
import re
import subprocess
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTIONS = [("logs", "log"), ("minutes", "minutes"), ("ideas", "idea")]
IDEA_STATUSES = ("selected", "shortlisted", "considering", "rejected")
DOCS_DIR = "docs"
OUT = os.path.join(ROOT, "content", "index.json")

DATE_IN_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})[-_]?")
FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
HEADING = re.compile(r"^#\s+(.+)$", re.MULTILINE)
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)")


def parse_front_matter(text):
    """Parse the small YAML subset we actually use: scalars, inline lists, dash lists."""
    match = FRONT_MATTER.match(text)
    if not match:
        return {}, text
    body = text[match.end():]
    data, key = {}, None
    for raw in match.group(1).splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- ") and key:
            data.setdefault(key, [])
            if isinstance(data[key], list):
                data[key].append(unquote(line.lstrip()[2:].strip()))
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not value:
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [unquote(p.strip()) for p in inner.split(",") if p.strip()]
        else:
            data[key] = unquote(value)
    return data, body


def unquote(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def idea_status(value):
    value = str(value or "").strip().lower()
    return value if value in IDEA_STATUSES else "considering"


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v]
    return [value] if value else []


def summarize(body, limit=220):
    """First substantial paragraph. A short line such as "**Time.** 14:00-14:35"
    is metadata rather than a summary, so it is only used as a last resort."""
    candidates = []
    for block in body.split("\n\n"):
        block = block.strip()
        if not block or block.startswith(("#", ">", "|", "---", "!", "- ", "* ")):
            continue
        flat = " ".join(block.split())
        flat = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", flat)
        flat = re.sub(r"[*_`]", "", flat).strip()
        if flat:
            candidates.append(flat)
    if not candidates:
        return ""
    pick = next((c for c in candidates if len(c) >= 60), candidates[0])
    return pick if len(pick) <= limit else pick[:limit].rsplit(" ", 1)[0] + "…"


def git_dates(path):
    """First and last commit dates for a file, so 'updated' is accurate for free."""
    try:
        out = subprocess.run(
            ["git", "log", "--follow", "--format=%cI", "--", path],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
        ).stdout.split()
    except Exception:
        return None, None
    return (out[-1][:10], out[0][:10]) if out else (None, None)


def human_size(nbytes):
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024 or unit == "GB":
            return f"{nbytes:.0f} {unit}" if unit == "B" else f"{nbytes:.1f} {unit}"
        nbytes /= 1024.0


def collect_entries():
    entries = []
    for folder, kind in SECTIONS:
        directory = os.path.join(ROOT, folder)
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            if not name.endswith(".md") or name.startswith("_"):
                continue
            rel = f"{folder}/{name}"
            with open(os.path.join(directory, name), encoding="utf-8") as fh:
                raw = fh.read()
            meta, body = parse_front_matter(raw)
            if str(meta.get("draft", "")).strip().lower() in ("true", "yes"):
                continue  # still being written; kept off the site until draft is removed

            in_name = DATE_IN_NAME.match(name)
            created, changed = git_dates(rel)
            date = meta.get("date") or (in_name.group(1) if in_name else None) or created
            if not date:
                date = datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(directory, name)), timezone.utc
                ).strftime("%Y-%m-%d")

            heading = HEADING.search(body)
            title = meta.get("title") or (heading.group(1).strip() if heading else
                                          re.sub(r"[-_]", " ", DATE_IN_NAME.sub("", name[:-3])).strip().title())

            updated = meta.get("updated") or changed
            if updated and updated <= str(date):
                updated = None

            attachments = []
            cited = as_list(meta.get("attachments")) + MD_LINK.findall(body)
            for ref in dict.fromkeys(cited):
                if ref.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                path = ref.lstrip("./")
                full = os.path.join(ROOT, path)
                if os.path.isfile(full):
                    attachments.append({
                        "path": path,
                        "name": os.path.basename(path),
                        "ext": os.path.splitext(path)[1].lstrip(".").upper() or "FILE",
                        "size": human_size(os.path.getsize(full)),
                    })

            entries.append({
                "id": f"{folder}/{name[:-3]}",
                "kind": meta.get("type") or kind,
                "title": title,
                "date": str(date),
                "updated": updated,
                "authors": as_list(meta.get("author") or meta.get("authors")),
                "tags": as_list(meta.get("tags")),
                "attendees": as_list(meta.get("attendees")),
                "status": idea_status(meta.get("status")) if kind == "idea" else None,
                "summary": meta.get("summary") or summarize(body),
                "source": rel,
                "attachments": attachments,
                "body": body.strip(),
            })
    entries.sort(key=lambda e: (e["date"], e["id"]), reverse=True)
    return entries


def collect_documents(entries):
    cited_by = {}
    for entry in entries:
        for att in entry["attachments"]:
            cited_by.setdefault(att["path"], []).append(
                {"id": entry["id"], "title": entry["title"]}
            )

    documents = []
    base = os.path.join(ROOT, DOCS_DIR)
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in sorted(filenames):
            if name.startswith(".") or name == ".gitkeep":
                continue
            full = os.path.join(dirpath, name)
            path = os.path.relpath(full, ROOT).replace(os.sep, "/")
            _, changed = git_dates(path)
            documents.append({
                "path": path,
                "name": name,
                "ext": os.path.splitext(name)[1].lstrip(".").upper() or "FILE",
                "size": human_size(os.path.getsize(full)),
                "updated": changed or datetime.fromtimestamp(
                    os.path.getmtime(full), timezone.utc).strftime("%Y-%m-%d"),
                "citedBy": cited_by.get(path, []),
            })
    documents.sort(key=lambda d: d["updated"], reverse=True)
    return documents


def main():
    entries = collect_entries()
    documents = collect_documents(entries)
    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {
            "log": sum(1 for e in entries if e["kind"] == "log"),
            "minutes": sum(1 for e in entries if e["kind"] == "minutes"),
            "idea": sum(1 for e in entries if e["kind"] == "idea"),
            "documents": len(documents),
        },
        "entries": entries,
        "documents": documents,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    c = payload["counts"]
    print(f"content/index.json: {c['log']} logs, {c['minutes']} minutes, "
          f"{c['idea']} ideas, {len(documents)} documents")


if __name__ == "__main__":
    main()
