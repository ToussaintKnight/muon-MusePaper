"""Accessibility tree parsers for each source.

Each parser takes the snapshot text from Camofox and returns a list of ``NewsItem``.
Parsers are the most source-specific part — tuned to each site's DOM/aria structure.

NewsNow has 44 sources × myFetch + cheerio.
We have ~6 Camofox sources × snapshot parser.

The pattern is always:
  1. Split snapshot into lines
  2. Find the "article" / "heading" / "row" markers
  3. Extract title, url, metadata (points, author, etc.)
"""

import re
from typing import Callable, Optional

from muse.types import NewsItem

# ---------------------------------------------------------------------------
# Hacker News
# Structure (every story is 2 rows + 1 empty separator):
#   Title row:    row "N. upvote TITLE (domain)"
#     cell "N."
#     cell "upvote":
#       link "upvote" [eN]: /url: vote?id=...
#     cell "TITLE (domain)":
#       link "TITLE" [eN]: <-- actual title text
#         /url: https://... <-- actual URL
#   Meta row:     row "P points by author X ago | hide | C comments"
#     cell
#     cell "P points by author X ago | hide | C comments":
#       text: P points by
#       link "author" [eN]: /url: user?id=author
#       ...
#       link "C comments" [eN]: /url: item?id=XXXXX
# ---------------------------------------------------------------------------

def parse_hackernews(snapshot: str) -> list[NewsItem]:
    items: list[NewsItem] = []
    lines = snapshot.split("\n")

    for i, line in enumerate(lines):
        # Match title row: row "N. upvote TITLE (domain)"
        m = re.search(r'row "(\d+)\.\s*upvote\s+.+?"', line)
        if not m:
            continue

        rank = int(m.group(1))

        # Title and URL are in the nested link element
        title = ""
        url = ""
        for j in range(i, min(i + 8, len(lines))):
            lk = lines[j]
            # Look for a link whose next line has /url: starting with http
            link_m = re.search(r'^\s*- link "(.+?)"\s+\[e\d+\]', lk)
            if link_m:
                # Check the next non-blank line for the URL
                for k in range(1, 3):
                    if j + k < len(lines):
                        url_m = re.search(r'/url: (https?://.+)', lines[j + k])
                        if url_m:
                            candidate_title = link_m.group(1)
                            # Skip "upvote", domain links (from?site=...), and very short titles
                            if (candidate_title.lower() not in ("upvote",) 
                                    and len(candidate_title) > 3
                                    and "/vote?" not in url_m.group(1)
                                    and "/from?" not in url_m.group(1)):
                                title = candidate_title
                                url = url_m.group(1).strip()
                                break
                if title:
                    break

        if not title or not url:
            continue

        # Meta data in the next row (meta row comes right after)
        points = 0
        author = ""
        comments = 0
        for j in range(i + 1, min(i + 6, len(lines))):
            meta_m = re.search(r'(\d+)\s+points by\s+(\S+)', lines[j])
            if meta_m:
                points = int(meta_m.group(1))
                author = meta_m.group(2)
                comm_m = re.search(r'(\d+)\s+comments?', lines[j])
                if comm_m:
                    comments = int(comm_m.group(1))
                break

        items.append(NewsItem(
            id=url.rstrip("/").split("/")[-1] if "/" in url else url,
            title=title,
            url=url,
            source="hackernews",
            extra={"points": points, "author": author, "comments": comments, "rank": rank},
        ))

    return items


# ---------------------------------------------------------------------------
# GitHub Trending
# Pattern:
#   article:
#     heading "owner / repo" [level=2]:
#       link "owner / repo" [eN]: /url: /owner/repo
#     paragraph: description
#     text: Language
#     link "star N" [eN]:
# ---------------------------------------------------------------------------

def parse_github_trending(snapshot: str) -> list[NewsItem]:
    items: list[NewsItem] = []
    lines = snapshot.split("\n")

    # State machine for each article block
    current: dict = {}
    in_article = False

    for line in lines:
        stripped = line.strip()

        # Detect article boundary — "article:" at any indentation
        if stripped.startswith("- article:"):
            # Save previous article
            if current.get("title") and current.get("url"):
                items.append(NewsItem(
                    id=current["url"],
                    title=current["title"],
                    url=f"https://github.com{current['url']}",
                    source="github-trending",
                    extra={
                        "description": current.get("desc", ""),
                        "language": current.get("lang", ""),
                        "stars": current.get("stars", 0),
                    },
                ))
            current = {}
            in_article = True
            continue

        if not in_article:
            continue

        # heading "owner / repo" [level=2]:
        m = re.search(r'heading "([^"]+)"\s+\[level=2\]', stripped)
        if m and "/" in m.group(1):
            current["title"] = m.group(1).strip()
            # Next non-blank line should be the link
            continue

        # If we have a title, look for /url: on the next lines
        if current.get("title") and not current.get("url"):
            m = re.search(r'/url:\s*(/\S+)', stripped)
            if m:
                url_path = m.group(1).strip()
                if not url_path.startswith("/login") and not url_path.startswith("/sponsors"):
                    current["url"] = url_path
            continue

        # paragraph: description
        if stripped.startswith("- paragraph:"):
            desc = stripped.split("paragraph:", 1)[1].strip().strip('"')
            if desc:
                current["desc"] = desc
            continue

        # text: Language (not "star", not a number, not a URL)
        if stripped.startswith("- text:"):
            val = stripped.split("text:", 1)[1].strip().strip('"')
            if val and not val.replace(",", "").isdigit() and not val.startswith("http"):
                current["lang"] = val
            continue

        # link "star N" [eN]:
        m = re.search(r'link "star\s+([\d,]+)"', stripped)
        if m:
            current["stars"] = int(m.group(1).replace(",", ""))
            continue

        # Reset on non-indented or less-indented lines that aren't continuation
        if stripped and not stripped.startswith("- ") and not stripped.startswith("  "):
            in_article = False

    # Last article
    if current.get("title") and current.get("url"):
        items.append(NewsItem(
            id=current["url"],
            title=current["title"],
            url=f"https://github.com{current['url']}",
            source="github-trending",
            extra={
                "description": current.get("desc", ""),
                "language": current.get("lang", ""),
                "stars": current.get("stars", 0),
            },
        ))

    return items


# ---------------------------------------------------------------------------
# Product Hunt
# Pattern:
#   heading "Top Products Launching Today" [level=1]
#     img "Name"
#     link "N. Name" [eN]: /url: /products/name
# ---------------------------------------------------------------------------

def parse_producthunt(snapshot: str) -> list[NewsItem]:
    items: list[NewsItem] = []
    lines = snapshot.split("\n")
    
    for i, line in enumerate(lines):
        # Match product rows: link "N. ProductName" [eN]:
        m = re.search(r'link "(\d+\.\s*.+?)"\s+\[e\d+\]', line)
        if not m:
            continue
        title = m.group(1).strip()
        # Remove numbering "1. " or "2. "
        clean_title = re.sub(r'^\d+\.\s*', '', title)
        
        # Get URL from next line
        url = ""
        if i + 1 < len(lines):
            url_m = re.search(r'/url: (.+)', lines[i + 1])
            if url_m:
                url = f"https://www.producthunt.com{url_m.group(1).strip()}"
        
        # Get description from nearby
        desc = ""
        for j in range(i - 3, i):
            if 0 <= j < len(lines) and "text: " in lines[j]:
                t = lines[j].split("text:", 1)[1].strip().strip('"')
                if len(t) > 20 and not t.startswith("star"):
                    desc = t
                    break
        
        if clean_title and url:
            items.append(NewsItem(
                id=url.rstrip("/").split("/")[-1],
                title=clean_title,
                url=url,
                source="producthunt",
                extra={"description": desc},
            ))
    
    return items


# ---------------------------------------------------------------------------
# TechCrunch
# Pattern:
#   heading "Title" [level=3]:
#     link "Title" [eN]: /url: https://techcrunch.com/...
#   time: "- N hours ago"
#   list → link "Author"
# ---------------------------------------------------------------------------

def parse_techcrunch(snapshot: str) -> list[NewsItem]:
    items: list[NewsItem] = []
    lines = snapshot.split("\n")
    
    current = {"title": "", "url": "", "author": "", "time": ""}
    
    for i, line in enumerate(lines):
        # heading "Title" [level=3]:
        m = re.search(r'heading "(.+?)"\s+\[level=3\]', line)
        if m:
            # Save previous
            if current["title"] and current["url"]:
                items.append(NewsItem(
                    id=current["url"].rstrip("/").split("/")[-1],
                    title=current["title"],
                    url=current["url"],
                    source="techcrunch",
                    extra={"author": current["author"], "time_ago": current["time"]},
                ))
            current = {"title": "", "url": "", "author": "", "time": ""}
            current["title"] = m.group(1).strip()
            
            # Look ahead for URL
            for j in range(1, 4):
                if i + j < len(lines):
                    url_m = re.search(r'/url: (.+)', lines[i + j])
                    if url_m:
                        current["url"] = url_m.group(1).strip()
                        break
            continue
        
        # time: "N hours/minutes ago"
        if "time:" in line:
            t = line.split("time:", 1)[1].strip().strip('"').strip("- ")
            current["time"] = t
            continue

        # link "Author" [eN]: /url: /author/...
        m = re.search(r'link "(?!logo|Gadgets|AI|Apps|Security|Startups)(.+?)"\s+\[e\d+\]', line)
        if m and '/author/' in lines[i+1] if i+1 < len(lines) else False:
            current["author"] = m.group(1).strip()
            continue

    # Last item
    if current["title"] and current["url"]:
        items.append(NewsItem(
            id=current["url"].rstrip("/").split("/")[-1],
            title=current["title"],
            url=current["url"],
            source="techcrunch",
            extra={"author": current["author"], "time_ago": current["time"]},
        ))
    
    return items


# ---------------------------------------------------------------------------
# Reddit (r/all top-24h)
# Pattern:
#   article "Title":
#     link "Title" [eN]: /url: /r/subreddit/comments/...
#     link "r/subreddit" [eN]: /url: /r/subreddit/
# ---------------------------------------------------------------------------

def parse_reddit(snapshot: str) -> list[NewsItem]:
    items: list[NewsItem] = []
    lines = snapshot.split("\n")
    
    for i, line in enumerate(lines):
        # article "Title":
        m = re.search(r'article "(.+)"', line)
        if not m:
            continue
        title = m.group(1).strip()
        if len(title) < 5:
            continue
        
        url = ""
        subreddit = ""
        for j in range(i, min(i + 5, len(lines))):
            url_m = re.search(r'/url: (/r/\w+/comments/\w+)', lines[j])
            if url_m:
                url = f"https://www.reddit.com{url_m.group(1)}"
                continue
            sub_m = re.search(r'link "(r/\w+)"', lines[j])
            if sub_m:
                subreddit = sub_m.group(1)
                continue
        
        if title and url:
            items.append(NewsItem(
                id=url.rstrip("/").split("/")[-1],
                title=title,
                url=url,
                source="reddit",
                extra={"subreddit": subreddit},
            ))
    
    return items


# ---------------------------------------------------------------------------
# Parser registry
# ---------------------------------------------------------------------------

PARSER_REGISTRY: dict[str, Callable[[str], list[NewsItem]]] = {
    "hackernews": parse_hackernews,
    "github-trending": parse_github_trending,
    "producthunt": parse_producthunt,
    "techcrunch": parse_techcrunch,
    "reddit": parse_reddit,
}


def get_parser(name: str) -> Callable[[str], list[NewsItem]]:
    parser = PARSER_REGISTRY.get(name)
    if not parser:
        raise ValueError(f"Unknown parser: {name}. Available: {list(PARSER_REGISTRY.keys())}")
    return parser
