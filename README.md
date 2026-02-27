# claude-cowork-x-twitter-bookmarks-skill

A Claude skill that scrapes your X.com (Twitter) bookmarks and generates a beautiful, searchable HTML archive.

## What it does

1. Opens your X.com bookmarks page (you must be logged in)
2. Scrolls through and captures every bookmark — author, text, engagement stats, date
3. Auto-categorizes each bookmark (AI, Dev, Marketing, Business, Content, Design)
4. Generates a self-contained HTML file with dark theme, live search, category filters, and month groupings

## Requirements

- [Claude Desktop](https://claude.ai/download) with Cowork mode
- Python 3
- You must be logged into X.com in your browser

## Installation

Drop the skill folder into your Claude skills directory:

```
~/.claude/skills/claude-cowork-x-twitter-bookmarks-skill/
├── SKILL.md
└── scripts/
    └── generate_bookmarks_html.py
```

Or if using Cowork, place it in your workspace's `.skills/skills/` folder.

## Usage

Just ask Claude something like:

- "Go through my X bookmarks and save them"
- "Export my Twitter bookmarks from the last 3 months"
- "Archive all my X bookmarks into a document"

Claude will handle the rest — scrolling, extracting, categorizing, and generating the HTML.

## Output

The generated HTML archive includes:

- Dark theme with gradient header
- Stats bar showing total bookmarks, date range, categories, and days covered
- Live search that filters by content, author, or tag
- Category filter buttons (All / AI / Dev / Marketing / Business / Content / Design)
- Bookmarks grouped by month
- Each bookmark displayed as a card with author info, tweet text, tags, engagement stats, and a link back to X

## License

MIT
