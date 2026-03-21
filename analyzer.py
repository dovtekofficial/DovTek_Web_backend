from dotenv import load_dotenv
load_dotenv()

import json
import os
from anthropic import AsyncAnthropic, APIStatusError
from prompts import PASS1_SYSTEM, PASS2_SYSTEM
from models import ScanResult

client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


async def analyze_message(message: str) -> ScanResult:
    try:
        # ── Pass 1: Prompt Injection Guard ──────────────────────────────
        pass1 = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            system=PASS1_SYSTEM,
            messages=[{"role": "user", "content": f"Message to check:\n\n{message}"}],
        )
        verdict = pass1.content[0].text.strip().upper()

        if verdict == "BLOCK":
            return ScanResult(
                risk_score=100,
                risk_level="HIGH",
                summary="This message contains hidden instructions designed to manipulate AI systems.",
                reasons=[
                    "The message contains text trying to override AI safety rules",
                    "This is a prompt injection attack — used by advanced fraudsters to fool AI tools",
                    "No legitimate message would contain instructions telling an AI to ignore its rules",
                ],
                action="BLOCK",
                what_to_do="Do not interact with this message or whoever sent it. Block the sender immediately.",
                pass1_blocked=True,
            )

        # ── Pass 2: Deep Fraud Analysis ──────────────────────────────────
        pass2 = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=PASS2_SYSTEM,
            messages=[{"role": "user", "content": f"Analyse this message for fraud:\n\n{message}"}],
        )
        raw = pass2.content[0].text.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        data = json.loads(raw.strip())
        data["pass1_blocked"] = False
        return ScanResult(**data)

    except APIStatusError as e:
        # ← catches Anthropic-specific errors (low credits, invalid key, etc.)
        # and surfaces the exact message to the frontend
        raise ValueError(e.message)