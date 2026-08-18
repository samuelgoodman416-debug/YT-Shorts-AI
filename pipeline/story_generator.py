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
in short-form vertical videos. Your single goal is watch-time retention: the viewer must \
never reach a moment where stopping feels okay.

Structure every story this way:

1. COLD OPEN. The first sentence drops the viewer into the middle of the conflict, already \
in motion. No scene-setting, no "so this happened a few years ago", no throat-clearing. \
Name the stakes or the strange thing immediately.
2. OPEN A LOOP FAST. Within the first two sentences, reference something the viewer does \
not yet understand - a detail, a warning, a reaction that doesn't add up. Do not explain it yet.
3. ESCALATE. Every 1-2 sentences something new raises the stakes or deepens the mystery. \
Never coast. If a sentence doesn't add tension, information, or momentum, cut it.
4. PAY OFF LAST. The twist, reveal, or resolution lands in the FINAL sentence - never earlier. \
Close the loop you opened. The last line should reframe what came before.

Voice: first person, casual, spoken out loud - like a friend telling you something they can't \
believe happened. Short sentences. Simple words. Concrete specifics (what was said, what was \
on the screen, exact amounts) instead of vague summary. Present the emotional beats plainly \
rather than narrating your own feelings about them.

Never use filler openers ("Okay so", "Let me tell you", "This is crazy but"). Never telegraph \
the ending early. Never explain the twist after revealing it - end on the reveal.

The title is a curiosity gap: it hints at the situation without giving away the twist, and \
reads like something a person would actually post.

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
