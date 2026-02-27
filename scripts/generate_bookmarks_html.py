#!/usr/bin/env python3
"""
Generate a beautiful, searchable HTML archive of X.com bookmarks.

Usage:
    python generate_bookmarks_html.py <bookmarks.json> <output.html>

The JSON file should contain a list of bookmark objects with these fields:
    - date: "YYYY-MM-DD"
    - name: "Display Name"
    - handle: "username" (without @)
    - text: "Tweet content"
    - tags: ["ai", "dev", ...] (from: ai, dev, marketing, business, content, design)
    - likes: "1.2K" (as displayed on X)
    - rt: "234" (reposts as displayed)
    - views: "45K" (impressions as displayed)
    - type: "tweet" | "thread" | "article"
"""

import json
import sys
from collections import OrderedDict
from datetime import datetime


def get_tag_color(tag):
    colors = {
        "ai": "#1d9bf0",
        "dev": "#00ba7c",
        "marketing": "#f91880",
        "business": "#ffd700",
        "content": "#7856ff",
        "design": "#ff6b35",
    }
    return colors.get(tag, "#8899a6")


def get_type_icon(t):
    icons = {"tweet": "&#128172;", "thread": "&#129525;", "article": "&#128240;"}
    return icons.get(t, "&#128172;")


def group_by_month(bookmarks):
    groups = OrderedDict()
    for b in bookmarks:
        try:
            dt = datetime.strptime(b["date"], "%Y-%m-%d")
            key = dt.strftime("%B %Y")
        except ValueError:
            key = "Unknown"
        groups.setdefault(key, []).append(b)
    return groups


def generate_html(bookmarks, output_path):
    if not bookmarks:
        print("No bookmarks to process.")
        sys.exit(1)

    # Sort by date descending
    bookmarks.sort(key=lambda x: x.get("date", ""), reverse=True)

    # Compute stats
    total = len(bookmarks)
    dates = [b["date"] for b in bookmarks if b.get("date")]
    earliest = min(dates) if dates else "N/A"
    latest = max(dates) if dates else "N/A"

    all_tags = set()
    for b in bookmarks:
        all_tags.update(b.get("tags", []))
    num_categories = len(all_tags)

    try:
        d1 = datetime.strptime(earliest, "%Y-%m-%d")
        d2 = datetime.strptime(latest, "%Y-%m-%d")
        days_covered = (d2 - d1).days + 1
    except ValueError:
        days_covered = "N/A"

    # Format date range for display
    try:
        start_display = datetime.strptime(earliest, "%Y-%m-%d").strftime("%B %d, %Y")
        end_display = datetime.strptime(latest, "%Y-%m-%d").strftime("%B %d, %Y")
    except ValueError:
        start_display = earliest
        end_display = latest

    month_groups = group_by_month(bookmarks)

    # Build bookmark cards HTML
    cards_html = ""
    for month, items in month_groups.items():
        cards_html += f"""
        <div class="month-divider">
            <span class="month-label">{month}</span>
            <span class="month-count">{len(items)} bookmarks</span>
        </div>
"""
        for b in items:
            tags_html = ""
            tag_classes = []
            for tag in b.get("tags", []):
                color = get_tag_color(tag)
                tags_html += f'<span class="tag" style="background:{color}20;color:{color};border:1px solid {color}40">{tag}</span>'
                tag_classes.append(f"tag-{tag}")

            icon = get_type_icon(b.get("type", "tweet"))
            tweet_url = f"https://x.com/{b.get('handle', '')}"
            tag_class_str = " ".join(tag_classes)

            try:
                date_display = datetime.strptime(b["date"], "%Y-%m-%d").strftime(
                    "%b %d, %Y"
                )
            except ValueError:
                date_display = b.get("date", "")

            cards_html += f"""
        <div class="bookmark-card {tag_class_str}" data-tags="{','.join(b.get('tags', []))}">
            <div class="card-header">
                <div class="author-info">
                    <span class="author-name">{b.get('name', 'Unknown')}</span>
                    <span class="author-handle">@{b.get('handle', '')}</span>
                </div>
                <div class="card-meta">
                    <span class="bookmark-type">{icon} {b.get('type', 'tweet')}</span>
                    <span class="bookmark-date">{date_display}</span>
                </div>
            </div>
            <div class="card-content">{b.get('text', '')}</div>
            <div class="card-footer">
                <div class="tags-container">{tags_html}</div>
                <div class="engagement">
                    <span title="Likes">&#10084;&#65039; {b.get('likes', '0')}</span>
                    <span title="Reposts">&#128257; {b.get('rt', '0')}</span>
                    <span title="Views">&#128065; {b.get('views', '0')}</span>
                </div>
                <a href="{tweet_url}" target="_blank" class="view-link">View on X &#8599;</a>
            </div>
        </div>
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>X Bookmarks Archive | {start_display} - {end_display}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
    --bg-primary: #000000;
    --bg-secondary: #16181c;
    --bg-card: #1d1f23;
    --text-primary: #e7e9ea;
    --text-secondary: #71767b;
    --accent-blue: #1d9bf0;
    --accent-green: #00ba7c;
    --accent-pink: #f91880;
    --border-color: #2f3336;
    --hover-bg: #1e2024;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter',sans-serif; background:var(--bg-primary); color:var(--text-primary); line-height:1.6; }}
.header {{
    background: linear-gradient(135deg, #0a1628 0%, #1a1a2e 30%, #16213e 60%, #0f3460 100%);
    padding: 40px 20px; text-align: center; border-bottom: 1px solid var(--border-color);
    position: relative; overflow: hidden;
}}
.header::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(circle at 30% 50%, rgba(29,155,240,0.1) 0%, transparent 50%),
                radial-gradient(circle at 70% 50%, rgba(249,24,128,0.08) 0%, transparent 50%);
}}
.header h1 {{ font-size:2.2em; font-weight:700; margin-bottom:8px; position:relative; }}
.header p {{ color:var(--text-secondary); font-size:1.05em; position:relative; }}
.stats-bar {{
    display:flex; justify-content:center; gap:30px; padding:20px;
    background:var(--bg-secondary); border-bottom:1px solid var(--border-color); flex-wrap:wrap;
}}
.stat {{ text-align:center; }}
.stat-value {{ font-size:1.5em; font-weight:700; color:var(--accent-blue); }}
.stat-label {{ font-size:0.8em; color:var(--text-secondary); text-transform:uppercase; letter-spacing:1px; }}
.controls {{ padding:20px; max-width:900px; margin:0 auto; }}
.search-box {{
    width:100%; padding:12px 16px; background:var(--bg-secondary); border:1px solid var(--border-color);
    border-radius:25px; color:var(--text-primary); font-size:1em; outline:none; font-family:inherit;
}}
.search-box:focus {{ border-color:var(--accent-blue); }}
.filter-bar {{ display:flex; gap:8px; margin-top:12px; flex-wrap:wrap; justify-content:center; }}
.filter-btn {{
    padding:8px 16px; border-radius:20px; border:1px solid var(--border-color);
    background:var(--bg-secondary); color:var(--text-secondary); cursor:pointer;
    font-size:0.9em; transition:all 0.2s; font-family:inherit;
}}
.filter-btn:hover {{ border-color:var(--accent-blue); color:var(--text-primary); }}
.filter-btn.active {{ background:var(--accent-blue); color:white; border-color:var(--accent-blue); }}
.bookmarks-container {{ max-width:900px; margin:0 auto; padding:20px; }}
.month-divider {{
    display:flex; align-items:center; justify-content:space-between; padding:16px 0 8px;
    border-bottom:2px solid var(--accent-blue); margin:24px 0 16px;
}}
.month-label {{ font-size:1.3em; font-weight:700; color:var(--accent-blue); }}
.month-count {{ color:var(--text-secondary); font-size:0.9em; }}
.bookmark-card {{
    background:var(--bg-card); border:1px solid var(--border-color); border-radius:12px;
    padding:16px; margin-bottom:12px; transition:all 0.2s;
}}
.bookmark-card:hover {{ border-color:var(--accent-blue); background:var(--hover-bg); }}
.card-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; flex-wrap:wrap; gap:8px; }}
.author-info {{ display:flex; align-items:center; gap:8px; }}
.author-name {{ font-weight:600; font-size:1em; }}
.author-handle {{ color:var(--text-secondary); font-size:0.9em; }}
.card-meta {{ display:flex; gap:12px; align-items:center; }}
.bookmark-type {{ color:var(--text-secondary); font-size:0.85em; }}
.bookmark-date {{ color:var(--text-secondary); font-size:0.85em; }}
.card-content {{ font-size:0.95em; line-height:1.5; margin-bottom:12px; color:var(--text-primary); }}
.card-footer {{ display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; }}
.tags-container {{ display:flex; gap:6px; flex-wrap:wrap; }}
.tag {{ padding:3px 10px; border-radius:12px; font-size:0.75em; font-weight:500; text-transform:uppercase; letter-spacing:0.5px; }}
.engagement {{ display:flex; gap:14px; color:var(--text-secondary); font-size:0.85em; }}
.view-link {{ color:var(--accent-blue); text-decoration:none; font-size:0.85em; font-weight:500; }}
.view-link:hover {{ text-decoration:underline; }}
.footer {{
    text-align:center; padding:30px; color:var(--text-secondary); font-size:0.85em;
    border-top:1px solid var(--border-color); margin-top:30px;
}}
@media(max-width:600px) {{
    .header h1 {{ font-size:1.5em; }}
    .stats-bar {{ gap:15px; }}
    .stat-value {{ font-size:1.2em; }}
    .card-header {{ flex-direction:column; align-items:flex-start; }}
    .card-footer {{ flex-direction:column; align-items:flex-start; }}
}}
</style>
</head>
<body>
<div class="header">
    <h1>X Bookmarks Archive</h1>
    <p>{start_display} &mdash; {end_display}</p>
</div>
<div class="stats-bar">
    <div class="stat"><div class="stat-value">{total}</div><div class="stat-label">Total Bookmarks</div></div>
    <div class="stat"><div class="stat-value">{start_display.split(',')[0] if ',' in start_display else start_display} - {end_display.split(',')[0] if ',' in end_display else end_display}</div><div class="stat-label">Date Range</div></div>
    <div class="stat"><div class="stat-value">{num_categories}</div><div class="stat-label">Categories</div></div>
    <div class="stat"><div class="stat-value">{days_covered}</div><div class="stat-label">Days Covered</div></div>
</div>
<div class="controls">
    <input type="text" class="search-box" placeholder="Search bookmarks by content, author, or tag..." oninput="filterBookmarks()">
    <div class="filter-bar">
        <button class="filter-btn active" onclick="setFilter('all')">All</button>
        <button class="filter-btn" onclick="setFilter('ai')">AI</button>
        <button class="filter-btn" onclick="setFilter('dev')">Dev</button>
        <button class="filter-btn" onclick="setFilter('marketing')">Marketing</button>
        <button class="filter-btn" onclick="setFilter('business')">Business</button>
        <button class="filter-btn" onclick="setFilter('content')">Content</button>
        <button class="filter-btn" onclick="setFilter('design')">Design</button>
    </div>
</div>
<div class="bookmarks-container">
{cards_html}
</div>
<div class="footer">
    <p>X Bookmarks Archive &bull; {total} bookmarks across {days_covered} days</p>
    <p>Generated with Claude &bull; {datetime.now().strftime('%B %d, %Y')}</p>
</div>
<script>
let currentFilter = 'all';
function setFilter(tag) {{
    currentFilter = tag;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    filterBookmarks();
}}
function filterBookmarks() {{
    const query = document.querySelector('.search-box').value.toLowerCase();
    const cards = document.querySelectorAll('.bookmark-card');
    const months = document.querySelectorAll('.month-divider');
    cards.forEach(card => {{
        const text = card.textContent.toLowerCase();
        const tags = card.dataset.tags || '';
        const matchSearch = !query || text.includes(query);
        const matchFilter = currentFilter === 'all' || tags.includes(currentFilter);
        card.style.display = (matchSearch && matchFilter) ? '' : 'none';
    }});
    months.forEach(div => {{
        let next = div.nextElementSibling;
        let hasVisible = false;
        while(next && !next.classList.contains('month-divider')) {{
            if(next.classList.contains('bookmark-card') && next.style.display !== 'none') hasVisible = true;
            next = next.nextElementSibling;
        }}
        div.style.display = hasVisible ? '' : 'none';
    }});
}}
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {output_path} with {total} bookmarks")


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_bookmarks_html.py <bookmarks.json> <output.html>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, "r", encoding="utf-8") as f:
        bookmarks = json.load(f)

    generate_html(bookmarks, output_path)


if __name__ == "__main__":
    main()
