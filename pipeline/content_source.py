"""Fetches a single text story from Reddit to narrate."""

import os
import random
from dataclasses import dataclass

import praw
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Story:
    id: str
    title: str
    text: str
    subreddit: str
    url: str


def _get_reddit_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ["REDDIT_USER_AGENT"],
    )


def fetch_story(
    subreddits: list[str],
    min_upvotes: int = 500,
    exclude_ids: set[str] | None = None,
    limit: int = 50,
) -> Story | None:
    """Return one eligible text story from a random subreddit in the list, or None if none qualify."""
    exclude_ids = exclude_ids or set()
    reddit = _get_reddit_client()

    subreddit_name = random.choice(subreddits)
    subreddit = reddit.subreddit(subreddit_name)

    candidates = []
    for post in subreddit.top(time_filter="week", limit=limit):
        if post.id in exclude_ids:
            continue
        if post.over_18 or post.stickied:
            continue
        if not post.is_self or not post.selftext:
            continue
        if post.score < min_upvotes:
            continue
        if len(post.selftext) < 200:
            continue
        candidates.append(post)

    if not candidates:
        return None

    post = random.choice(candidates)
    return Story(
        id=post.id,
        title=post.title,
        text=post.selftext,
        subreddit=subreddit_name,
        url=f"https://reddit.com{post.permalink}",
    )


if __name__ == "__main__":
    story = fetch_story(subreddits=["AskReddit", "tifu"], min_upvotes=500)
    if story is None:
        print("No eligible story found. Try lowering min_upvotes or adding subreddits.")
    else:
        print(f"[{story.subreddit}] {story.title}\n")
        print(story.text)
        print(f"\nSource: {story.url}")
