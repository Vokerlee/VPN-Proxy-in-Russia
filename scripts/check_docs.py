#!/usr/bin/env python3
"""Check local Markdown links, heading anchors, SVGs and accidental live profiles.

No network access. See docs/automation.md#maintain-the-guide-itself.
Run: python3 -B scripts/check_docs.py
"""
import argparse
from collections import Counter
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


def strip_fences(text):
    output=[]
    fence=None
    for line in text.splitlines():
        match=re.match(r"^\s*(`{3,}|~{3,})",line)
        if match:
            marker=match.group(1)
            if fence is None:
                fence=marker[0]
            elif marker[0]==fence:
                fence=None
            continue
        if fence is None:
            output.append(line)
    return "\n".join(output), fence is not None


def anchors(text):
    visible,_=strip_fences(text)
    found=set()
    counts=Counter()
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$",visible,re.M):
        heading=re.sub(r"<[^>]+>","",heading).lower()
        slug="".join(c for c in heading if c.isalnum() or c in " _-").replace(" ","-")
        count=counts[slug]
        counts[slug]+=1
        found.add(slug if count==0 else f"{slug}-{count}")
    return found


def check_repo(root):
    root=Path(root).resolve()
    docs=[p for p in root.rglob("*.md") if not any(x.startswith(".") for x in p.relative_to(root).parts)]
    errors=[]
    contents={p:p.read_text(encoding="utf-8") for p in docs}
    for path,text in contents.items():
        rel=path.relative_to(root)
        visible,unclosed=strip_fences(text)
        if unclosed:
            errors.append(f"{rel}: unclosed fenced code block")
        if re.search(r"vless://[0-9a-fA-F-]{36}@",text):
            errors.append(f"{rel}: looks like a live VLESS account; use placeholders")
        for match in re.finditer(r"!?\[[^\]\n]*\]\(([^\)\n]+)\)",visible):
            target=match.group(1).strip()
            if target.startswith("<") and ">" in target:
                target=target[1:target.index(">")]
            else:
                target=target.split(' "',1)[0]
            u=urlsplit(target)
            if u.scheme or u.netloc:
                continue
            dest=(path.parent/unquote(u.path)).resolve() if u.path else path
            try:
                dest.relative_to(root)
            except ValueError:
                errors.append(f"{rel}: link escapes repository: {target}")
                continue
            if not dest.exists():
                errors.append(f"{rel}: missing link target: {target}")
            elif u.fragment and dest.suffix.lower()==".md":
                body=contents.get(dest)
                if body is None:
                    body=dest.read_text(encoding="utf-8")
                if unquote(u.fragment) not in anchors(body):
                    errors.append(f"{rel}: missing heading anchor: {target}")
    svgs=list((root/"images").glob("*.svg")) if (root/"images").exists() else []
    for path in svgs:
        try:
            tree=ET.parse(path)
            if tree.getroot().tag!="{http://www.w3.org/2000/svg}svg":
                raise ValueError("not an SVG root")
            if tree.getroot().find("{http://www.w3.org/2000/svg}title") is None:
                errors.append(f"{path.relative_to(root)}: missing accessible image title")
        except (ET.ParseError,ValueError) as error:
            errors.append(f"{path.relative_to(root)}: invalid SVG: {error}")
    return docs,svgs,errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    docs,svgs,errors=check_repo(args.root)
    for error in errors:
        print("ERROR:",error)
    if errors:
        return 1
    print(f"Checked {len(docs)} Markdown files and {len(svgs)} SVGs: local links, anchors and examples are consistent.")
    print("External URLs, live UI screenshots and VPN reachability are not tested by this offline check.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
