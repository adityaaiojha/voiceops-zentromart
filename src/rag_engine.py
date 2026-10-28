import os
import glob
import re

def retrieve_context(query: str, kb_dir="kb", n_results=3):
    """Simple keyword & section matching over Markdown documents in kb/."""
    query_tokens = set(re.findall(r'\w+', query.lower()))
    chunks = []

    if not os.path.exists(kb_dir):
        return []

    # Prioritize v4 over superseded files
    md_files = glob.glob(os.path.join(kb_dir, "*.md"))
    sorted_files = sorted(md_files, key=lambda f: "superseded" in f)

    for fpath in sorted_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            
            sections = content.split("## ")
            for sec in sections:
                sec_text = sec.strip()
                if not sec_text:
                    continue
                tokens = set(re.findall(r'\w+', sec_text.lower()))
                overlap = len(query_tokens.intersection(tokens))
                if overlap > 0:
                    chunks.append((overlap, f"{os.path.basename(fpath)}: {sec_text[:350]}"))
        except Exception:
            continue

    # Sort by keyword match score
    chunks.sort(key=lambda x: x[0], reverse=True)
    return [c[1] for c in chunks[:n_results]]