---
name: claude-cowork-x-twitter-bookmarks-skill
description: "Scrape and archive X.com (Twitter) bookmarks into a beautiful, searchable HTML document. Use this skill whenever the user mentions X bookmarks, Twitter bookmarks, saving bookmarks, archiving tweets, exporting bookmarks from X, organizing saved tweets, or wants to create a browsable archive of their bookmarked posts. Also trigger when the user says things like 'go through my bookmarks', 'save my bookmarks', 'export my X saves', or 'make a document of my bookmarks'."
compatibility: "Requires Claude in Chrome (browser automation) and Bash (for running Python scripts)"
---

# X Bookmarks Scraper

Scrape a user's X.com bookmarks by scrolling through their bookmarks page in the browser, capturing tweet details from screenshots, and generating a polished, searchable HTML archive.

## Prerequisites

- The user must be **logged into X.com** in their browser
- Claude in Chrome browser automation tools must be available
- Python 3 must be available for HTML generation

## High-Level Workflow

1. **Ask the user** how far back they want to go (e.g., "last 30 days", "back to January 2025", "all of them")
2. **Navigate** to `https://x.com/i/bookmarks`
3. **Scroll and capture** bookmarks by taking screenshots, extracting tweet details
4. **Generate HTML** using the bundled script at `scripts/generate_bookmarks_html.py`
5. **Deliver** the final HTML file to the user

## Step 1: Setup

Get the browser tab context and navigate to the bookmarks page:

```
1. Use tabs_context_mcp to get available tabs
2. Navigate to https://x.com/i/bookmarks in a tab
3. Take a screenshot to confirm the page loaded and the user is logged in
```

If the user is not logged in, stop and ask them to log in first.

## Step 2: Scroll and Capture Bookmarks

This is the core of the skill. X.com bookmarks load dynamically as you scroll, showing tweets in reverse chronological order (newest first).

### Reading a screenshot

Each bookmark card on X.com contains:
- **Author name and handle** (e.g., "Pieter Levels @levelsio")
- **Date** (relative like "2h" for recent, or absolute like "Feb 14" or "Oct 7, 2025" for older)
- **Tweet text** (the main content)
- **Engagement stats** at the bottom: replies, reposts, likes, views/impressions
- **Media** (images, links) — note the presence but don't need to capture

### Extraction format

For each bookmark, extract a dictionary:

```python
{
    "date": "YYYY-MM-DD",         # Convert relative dates using today's date
    "name": "Display Name",       # Author's display name
    "handle": "username",         # Without the @ symbol
    "text": "Tweet content...",   # Main text, truncated to ~200 chars if very long
    "tags": ["ai", "dev"],        # Categorize (see categories below)
    "likes": "1.2K",              # As displayed
    "rt": "234",                  # Reposts/retweets as displayed
    "views": "45K",               # Views/impressions as displayed
    "type": "tweet"               # "tweet", "thread", or "article"
}
```

### Categories for tagging

Assign 1-2 tags based on tweet content:
- **ai** — AI, machine learning, LLMs, GPT, Claude, models, prompts
- **dev** — Programming, coding, software engineering, frameworks, tools
- **marketing** — Marketing, growth, SEO, content strategy, social media
- **business** — Startups, entrepreneurship, revenue, funding, business strategy
- **content** — Writing, creativity, content creation, media, design tips
- **design** — UI/UX, visual design, product design, CSS, frontend aesthetics

### Scrolling strategy

1. Take a screenshot of the current view
2. Read all visible bookmark cards and extract their data
3. Scroll down 3-5 ticks using the `scroll` action
4. Wait briefly for content to load (0.5-1s)
5. Take another screenshot
6. Continue until you've reached the user's target date or the end of bookmarks
7. Keep a running list of all extracted bookmarks

**Tips for reliable scrolling:**
- X.com dynamically loads content, so scroll in moderate increments (3-5 ticks)
- After scrolling, wait a moment before screenshotting to let content render
- Watch for the "end of bookmarks" indicator or repeated content
- If the page jumps or navigates away accidentally (clicking a tweet), navigate back to `https://x.com/i/bookmarks` — note this reloads from the top, so you'll need to scroll back down
- Keep track of the last date you captured to know where to resume after any interruptions
- Some tweets may span multiple scroll positions — capture what's visible and avoid duplicates by checking handles + dates

### Handling dates

- Recent bookmarks show relative dates ("2h", "14h", "Feb 24")
- Older bookmarks show "Mon DD, YYYY" format
- Convert all dates to YYYY-MM-DD format using today's date as reference
- If a date says just "Feb 14" without a year, infer the year from context (most recent occurrence)

## Step 3: Generate the HTML

Once all bookmarks are captured, use the bundled Python script to generate the HTML:

```bash
python /path/to/skill/scripts/generate_bookmarks_html.py
```

But first, you need to create a JSON data file that the script reads. Save the bookmarks list as JSON:

```python
# Save to bookmarks_data.json in your working directory
import json
bookmarks = [
    # ... all your extracted bookmarks
]
with open("bookmarks_data.json", "w") as f:
    json.dump(bookmarks, f, indent=2)
```

Then run the generation script, passing the JSON file and output path:

```bash
python /path/to/skill/scripts/generate_bookmarks_html.py \
    bookmarks_data.json \
    /path/to/output/x_bookmarks.html
```

The script generates a fully self-contained HTML file with:
- Dark theme with gradient header
- Stats bar (total bookmarks, date range, categories, days covered)
- Live search filtering
- Category filter buttons (All / AI / Dev / Marketing / Business / Content / Design)
- Bookmarks grouped by month with dividers
- Each bookmark as a card with author, text, tags, engagement stats, and "View on X" link
- Responsive design that works on mobile

## Step 4: Deliver

Save the HTML file to the user's workspace folder and provide a link:

```
[View your X Bookmarks Archive](computer:///path/to/output/x_bookmarks.html)
```

## Handling Large Bookmark Collections

For users with hundreds of bookmarks going back many months:
- Process in batches — scroll and capture ~20-30 bookmarks at a time
- Periodically save progress (write intermediate JSON) in case of interruptions
- If the browser tab crashes or navigates away, you can resume by loading saved data and scrolling back to where you left off

## Example Interaction

**User:** "Go through my X bookmarks and save them. I want everything from the last 3 months."

**Claude:**
1. Opens X.com bookmarks page
2. Scrolls through, capturing ~10-15 bookmarks per screenshot
3. Continues until reaching bookmarks from 3 months ago
4. Generates HTML with all captured bookmarks
5. Delivers the file to the user

## Edge Cases

- **Private/protected tweets**: These still appear in bookmarks. Capture them normally.
- **Deleted tweets**: May show as unavailable. Skip these.
- **Quote tweets**: Capture the outer tweet's content; note it's a quote tweet in the text if visible.
- **Threads**: If a bookmarked tweet is clearly part of a thread (shows "Show this thread"), mark `type` as "thread".
- **Non-English tweets**: Capture the text as-is in whatever language it's in.
