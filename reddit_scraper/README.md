# Reddit Scraper

Scrape Reddit posts and comments using [PRAW](https://praw.readthedocs.io/) (Python Reddit API Wrapper).

## Setup

### 1. Install dependencies

```bash
pip install -r reddit_scraper/requirements.txt
```

### 2. Create a Reddit app

1. Go to https://www.reddit.com/prefs/apps
2. Click **"create another app..."**
3. Fill in:
   - **name**: anything (e.g. `funnel-agent-scraper`)
   - **type**: select **script**
   - **redirect uri**: `http://localhost:8080` (required but unused)
4. Click **"create app"**
5. Copy the **client ID** (string under the app name) and **secret**

### 3. Add credentials to `.env`

```
REDDIT_CLIENT_ID=your-app-id
REDDIT_CLIENT_SECRET=your-app-secret
REDDIT_USER_AGENT=FunnelAgent/1.0 (research scraper)
```

## Usage

### Scrape a subreddit

```bash
# Hot posts from r/supplements
python -m reddit_scraper.scrape subreddit --name supplements --limit 25

# Top posts from the last month with comments
python -m reddit_scraper.scrape subreddit --name supplements --sort top --time-filter month --limit 25 --comments

# New posts, deeper comment trees
python -m reddit_scraper.scrape subreddit --name Nootropics --sort new --limit 10 --comments --comment-depth 5
```

### Search Reddit

```bash
# Search all of Reddit
python -m reddit_scraper.scrape search --query "AG1 greens supplement" --limit 50

# Search specific subreddits with comments
python -m reddit_scraper.scrape search --query "AG1" --subreddits supplements Nootropics --limit 20 --comments

# Top results from the past year
python -m reddit_scraper.scrape search --query "best greens powder" --sort top --time-filter year --limit 30
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--comments` | Fetch comment trees | off |
| `--comment-depth N` | Max nesting depth | 10 |
| `--comment-sort` | best/top/new/controversial/old/q&a | best |
| `--output PATH` | Custom output file | auto-generated |
| `--time-filter` | all/day/hour/month/week/year | all |

## Output

JSON files are saved to `reddit_scraper/output/` by default. Each file contains:

```json
{
  "scrape_type": "search",
  "query": "AG1 greens",
  "scraped_at": "2026-03-09T12:00:00+00:00",
  "total_posts": 42,
  "posts": [
    {
      "id": "abc123",
      "title": "...",
      "author": "...",
      "score": 156,
      "selftext": "...",
      "subreddit": "supplements",
      "comments": [{"body": "...", "score": 45, "replies": [...]}],
      "comments_flat": [{"body": "...", "score": 45, "depth": 0}],
      "comment_warnings": ["MoreComments skipped at depth 3 (12 hidden)"]
    }
  ]
}
```

## Rate Limits

PRAW handles Reddit's rate limiting automatically (100 requests/minute for OAuth apps). No custom throttling needed.
