# 📚 JLPT Grammar of the Day — Mastodon Bot

A Python bot that posts one JLPT grammar point (N3–N1) per day to Mastodon,
powered by the Anthropic Claude API and automated via GitHub Actions.

---

## Project Structure

```
jlpt-bot/
├── bot.py                        # Main bot script
├── grammar.json                  # Grammar point database (120 entries)
├── requirements.txt
└── .github/
    └── workflows/
        └── daily-post.yml        # GitHub Actions schedule
```

---

## Setup

### 1. Fork / clone this repo to your GitHub account

### 2. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions → New repository secret**
and add:

| Secret name            | Value                                      |
|------------------------|--------------------------------------------|
| `ANTHROPIC_API_KEY`    | Your Anthropic API key                     |
| `MASTODON_ACCESS_TOKEN`| Your Mastodon bot account's access token   |
| `MASTODON_INSTANCE`    | e.g. `https://mastodon.social`             |

### 3. Get a Mastodon Access Token

1. Log into your Mastodon bot account
2. Go to **Preferences → Development → New Application**
3. Name it (e.g. "JLPT Bot"), enable the `write:statuses` scope
4. Copy the **Access Token**

### 4. Enable GitHub Actions

Make sure Actions are enabled in your repo (**Settings → Actions → Allow all actions**).

---

## Schedule

The bot runs at **00:00 UTC (09:00 JST)** every day via the cron schedule in
`.github/workflows/daily-post.yml`.

To change the time, edit the cron expression:
```yaml
- cron: '0 0 * * *'   # min hour day month weekday (UTC)
```

---

## Manual Trigger

You can trigger a post manually at any time:
**GitHub → Actions → JLPT Grammar of the Day → Run workflow**

---

## Extending the Grammar List

Add entries to `grammar.json` following this format:
```json
{ "id": 121, "level": "N2", "grammar": "〜に反して" }
```

Supported levels: `N3`, `N2`, `N1`

---

## Local Testing

```bash
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...
export MASTODON_ACCESS_TOKEN=your_token
export MASTODON_INSTANCE=https://mastodon.social

python bot.py
```

To preview without posting, comment out the `post_to_mastodon(content)` line in `main()`.

---

## Cost

One Claude API call per day ≈ **$0.01 or less**. GitHub Actions on a public
repo is free.
