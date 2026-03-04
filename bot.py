"""
JLPT Grammar of the Day — Mastodon Bot
Posts one N3–N1 grammar point per day using the Anthropic API.
"""

import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path


# ── Config ────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY    = os.environ["ANTHROPIC_API_KEY"]
MASTODON_ACCESS_TOKEN = os.environ["MASTODON_ACCESS_TOKEN"]
MASTODON_INSTANCE    = os.environ.get("MASTODON_INSTANCE", "https://mastodon.social")

GRAMMAR_FILE = Path(__file__).parent / "grammar.json"
MAX_CHARS    = 480   # Mastodon limit is 500; leave a small buffer


# ── Grammar Picker ────────────────────────────────────────────────────────────

def get_todays_grammar() -> dict:
    """Deterministically pick today's grammar point using day-of-year."""
    grammar_list = json.loads(GRAMMAR_FILE.read_text(encoding="utf-8"))
    day_of_year  = datetime.now().timetuple().tm_yday
    return grammar_list[day_of_year % len(grammar_list)]


# ── Content Generator ─────────────────────────────────────────────────────────

def generate_post(grammar_point: dict) -> str:
    """Call Claude to generate the grammar explanation post."""
    level   = grammar_point["level"]
    grammar = grammar_point["grammar"]

    prompt = f"""You are a Japanese language teacher creating a daily Mastodon post.
Write a post about the JLPT {level} grammar point: {grammar}

Use EXACTLY this format (keep each section tight and clear):

📚 JLPT {level} Grammar of the Day
✏️ {grammar}

📖 Usage:
[1–2 sentences on how to attach/conjugate this grammar pattern]

💡 Nuance:
[1–2 sentences on the feeling, connotation, register, or common mistakes]

📝 Examples:
1. [Japanese sentence]
   → [English translation]

2. [Japanese sentence]
   → [English translation]

3. [Japanese sentence]
   → [English translation]

#JLPT #日本語 #LearnJapanese #{level} #Japanese

Rules:
- Japanese only in examples (no romaji)
- Keep the total post under 480 characters
- Be concise — every word counts
- Do not add anything outside the format above"""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["content"][0]["text"].strip()


# ── Mastodon Poster ───────────────────────────────────────────────────────────

def split_post(text: str, max_len: int = MAX_CHARS) -> list[str]:
    """Split a long post into threaded chunks, breaking on newlines."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    remaining = text
    while len(remaining) > max_len:
        split_at = remaining.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


def post_to_mastodon(content: str) -> None:
    """Post content to Mastodon, threading if it exceeds the character limit."""
    chunks   = split_post(content)
    reply_id = None
    headers  = {
        "Authorization": f"Bearer {MASTODON_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    for i, chunk in enumerate(chunks):
        payload = {
            "status": chunk,
            "visibility": "public",
            "language": "ja",
        }
        if reply_id:
            payload["in_reply_to_id"] = reply_id

        response = requests.post(
            f"{MASTODON_INSTANCE}/api/v1/statuses",
            headers=headers,
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        reply_id = response.json()["id"]
        print(f"  ✅ Chunk {i + 1}/{len(chunks)} posted (id={reply_id})")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"🗓  {datetime.now().strftime('%Y-%m-%d')} — JLPT Bot starting")

    grammar_point = get_todays_grammar()
    print(f"📖 Today's grammar: {grammar_point['grammar']} ({grammar_point['level']})")

    print("🤖 Generating post with Claude...")
    content = generate_post(grammar_point)
    print(f"\n--- Preview ({len(content)} chars) ---\n{content}\n---\n")

    print("📡 Posting to Mastodon...")
    post_to_mastodon(content)
    print("🎉 Done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)
    except Exception as exc:
        print(f"❌ Fatal error: {exc}", file=sys.stderr)
        sys.exit(1)
