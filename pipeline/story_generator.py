"""Generates an original short story script for narration, using a cheap Claude model."""

import json
import os
from dataclasses import dataclass

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You write short, original stories in the style of viral Reddit story \
posts (r/AskReddit confessions, r/tifu, r/relationships, r/pettyrevenge) for narration \
in short-form vertical videos.

Write in first person, casual conversational tone, like someone telling a story out loud. \
Open with a hook in the first sentence that makes someone want to keep watching. Build to a \
clear twist, payoff, or resolution by the end. Keep sentences short and easy to follow when \
heard rather than read.

Invent a new premise, characters, and setting each time. Never repeat a story you've told \
before in this conversation. Avoid real people, real brands, illegal content, and anything \
sexually explicit."""


@dataclass
class Story:
    title: str
    text: str


def generate_story(topic_hint: str | None = None, target_words: int = 150) -> Story:
    client = anthropic.Anthropic()

    user_prompt = (
        f"Write a new original story now. Target length: about {target_words} words "
        f"of narration (roughly {int(target_words / 5.6)} seconds spoken aloud)."
    )
    if topic_hint:
        user_prompt += f" Theme/topic hint: {topic_hint}."

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "story": {"type": "string"},
                    },
                    "required": ["title", "story"],
                    "additionalProperties": False,
                },
            }
        },
    )

    text = next(block.text for block in response.content if block.type == "text")
    data = json.loads(text)
    return Story(title=data["title"], text=data["story"])


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY in your .env file first.")
    else:
        story = generate_story()
        print(f"{story.title}\n\n{story.text}")
