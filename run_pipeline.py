"""CLI entrypoint: generates one or more finished short-form videos end-to-end."""

import os
import sys

from dotenv import load_dotenv

from pipeline.pipeline import run

if __name__ == "__main__":
    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set. Add it to your .env file first.")
        sys.exit(1)

    for path in run():
        print(f"Wrote {path}")
