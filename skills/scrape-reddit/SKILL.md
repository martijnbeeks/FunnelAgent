---
name: scrape-reddit
description: Scrapes Reddit posts, comments, and search results using the PRAW-based reddit_scraper package.
---

# Scrape Reddit Skill

You scrape Reddit content using the project's PRAW-based scraper. This skill supports three modes: fetching a single post with its full comment tree, browsing a subreddit, or searching Reddit for posts matching a query.

## PREREQUISITES

- Python 3.8+ with packages from `reddit_scraper/requirements.txt` installed (`praw`, `python-dotenv`)
- `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` set in `.env`

If credentials are missing, guide the user:

> **Reddit API credentials required.** To set them up:
> 1. Go to https://www.reddit.com/prefs/apps
> 2. Click **"create another app..."** at the bottom
> 3. Select **"script"** as the app type
> 4. Fill in a name (e.g. "FunnelAgent") and set redirect URI to `http://localhost:8080`
> 5. Click **Create app**
> 6. Copy the **client ID** (string under the app name) and **secret**
> 7. Add to your `.env` file:
>    ```
>    REDDIT_CLIENT_ID=your-client-id
>    REDDIT_CLIENT_SECRET=your-client-secret
>    ```

## INPUT

Determine the scrape mode from what the user provides:

| User provides | Mode | CLI subcommand |
|---------------|------|----------------|
| A Reddit post URL (contains `/comments/`) | **Single post** | `post` |
| A subreddit name (e.g. "supplements", "r/supplements") | **Subreddit browse** | `subreddit` |
| A search query (e.g. "AG1 greens supplement") | **Search** | `search` |

Plus optional parameters the user may specify:
- **output** — custom output file path (default: auto-generated in `reddit_scraper/output/`)
- **limit** — max posts to fetch for subreddit/search (default: 25)
- **sort** — sort order (varies by mode, see below)
- **time_filter** — time window for top/controversial sorts (default: `all`)
- **comments** — whether to include comment trees for subreddit/search (always included for single post)
- **comment_depth** — max comment nesting depth (default: 10)
- **comment_sort** — comment sort order: `best`, `top`, `new`, `controversial`, `old`, `q&a` (default: `best`)

## STEP 1: PARSE INPUT AND DETERMINE MODE

Analyze the user's input to determine which mode to use:

### Single post mode
If the input contains `/comments/` or looks like a Reddit post URL:
```
Extract the URL as-is — the scraper handles URL parsing internally.
```

### Subreddit mode
If the input is a subreddit name:
```
Strip any leading "r/" prefix to get the bare subreddit name.
```

### Search mode
If the input is a search query or the user explicitly asks to search:
```
Use the query string as-is. Optionally scope to specific subreddits if the user specifies them.
```

## STEP 2: CHECK CREDENTIALS

Before running the scraper, verify the `.env` file has the required credentials:

```bash
grep -q "REDDIT_CLIENT_ID" .env && grep -q "REDDIT_CLIENT_SECRET" .env && echo "OK" || echo "MISSING"
```

If missing, display the setup instructions from the PREREQUISITES section and wait for the user to confirm they've added the credentials.

## STEP 3: BUILD AND RUN THE COMMAND

Build the appropriate command based on the mode:

### Single post
```bash
python -m reddit_scraper.scrape post --url "{URL}" [--comment-depth {N}] [--comment-sort {sort}] [--output {path}]
```

### Subreddit browse
```bash
python -m reddit_scraper.scrape subreddit --name {name} [--sort {hot|new|top|rising|controversial}] [--time-filter {all|day|hour|month|week|year}] [--limit {N}] [--comments] [--comment-depth {N}] [--comment-sort {sort}] [--output {path}]
```

### Search
```bash
python -m reddit_scraper.scrape search --query "{query}" [--subreddits {sub1} {sub2}] [--sort {relevance|hot|top|new|comments}] [--time-filter {all|day|hour|month|week|year}] [--limit {N}] [--comments] [--comment-depth {N}] [--comment-sort {sort}] [--output {path}]
```

Execute the command using the Bash tool. The scraper prints the output file path on success.

## STEP 4: READ AND PRESENT RESULTS

After the scraper completes, read the output JSON file and present a summary to the user.

### For a single post:
```
Post: {title}
Author: u/{author} | Score: {score} | Upvote ratio: {upvote_ratio}
Subreddit: r/{subreddit} | Comments: {num_comments}
Posted: {created_utc}
URL: {permalink}

Body preview: {first 300 chars of selftext, if any}

Comment tree: {number of top-level comments} top-level comments, {total flat comments} total
Top comments:
1. u/{author} ({score} pts): {first 150 chars of body}...
2. u/{author} ({score} pts): {first 150 chars of body}...
3. u/{author} ({score} pts): {first 150 chars of body}...
```

### For subreddit/search results:
```
{scrape_type}: {subreddit or query}
Posts found: {total_posts} | Sort: {sort} | Time filter: {time_filter}

Top posts:
1. [{score}] {title} — u/{author} ({num_comments} comments)
2. [{score}] {title} — u/{author} ({num_comments} comments)
3. [{score}] {title} — u/{author} ({num_comments} comments)
...

Output saved to: {output_path}
```

## STEP 5: OFFER NEXT STEPS

After presenting the summary, ask the user what they'd like to do:

> **What would you like to do next?**
> 1. **View full JSON** — display the raw scraped data
> 2. **Filter/analyze** — filter comments by keyword, sentiment, or score threshold
> 3. **Scrape another** — fetch a different post, subreddit, or search query
> 4. **Feed into funnel** — use this data as research input for the FunnelAgent pipeline

## OUTPUT

- Output JSON file at the path printed by the scraper (default: `reddit_scraper/output/{slug}_{timestamp}.json`)

### Output JSON structure:
```json
{
  "scrape_type": "post|subreddit|search",
  "scraped_at": "2024-01-15T12:00:00+00:00",
  "total_posts": 1,
  "posts": [
    {
      "id": "abc123",
      "title": "Post title",
      "author": "username",
      "score": 150,
      "upvote_ratio": 0.95,
      "num_comments": 42,
      "selftext": "Post body text...",
      "url": "https://...",
      "permalink": "https://www.reddit.com/r/...",
      "subreddit": "supplements",
      "created_utc": "2024-01-15T10:00:00+00:00",
      "is_self": true,
      "link_flair_text": "Discussion",
      "comments": [ { "id": "...", "author": "...", "body": "...", "score": 10, "depth": 0, "replies": [...] } ],
      "comments_flat": [ { "id": "...", "author": "...", "body": "...", "score": 10, "depth": 0 } ]
    }
  ]
}
```

## INTEGRATION WITH FUNNEL PIPELINE

When used as part of the FunnelAgent pipeline, this skill feeds Reddit discussion data into the Deep Research step. The orchestrator can spawn this skill to collect real customer language from Reddit threads.

```
Use the Task tool with:
  subagent_type: "general-purpose"
  mode: "bypassPermissions"
  prompt: "You are executing Reddit Scraping for the FunnelAgent pipeline.

    FIRST: Read skills/scrape-reddit/SKILL.md for your complete instructions.

    RUN_DIR: {RUN_DIR}

    Scrape the following Reddit post: {url}
    Save output to {RUN_DIR}/reddit/.

    After scraping, read the JSON and produce a brief summary:
    - Post title, score, and comment count
    - Top 5 themes from the comment discussion
    - 10 verbatim user quotes that capture strong opinions or emotions
    Save the summary to {RUN_DIR}/00_reddit_summary.md"
```
