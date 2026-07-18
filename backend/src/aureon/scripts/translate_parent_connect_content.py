"""One-time seed-content translation script for Parent Connect.

Translates every ``ParentCareerGuide`` (27) and ``ParentQuestion`` (150)
English seed entry into Hindi and Telugu, using the existing
``get_llm_client()``/Groq abstraction — the only reusable building block
for this, since no i18n/translation infrastructure exists anywhere else
in this codebase. This is a one-time OFFLINE generation step producing
new seeded rows (``language="hi"``/``"te"``, new ids), never a runtime
translation call — same "precomputed, honestly-labeled content"
philosophy as every other seed script. English originals are never
touched.

Run via: python -m aureon.scripts.translate_parent_connect_content
"""

import asyncio
import json
import os
import re
import sys

from groq import RateLimitError

from aureon.domain.models.parent_connect import ParentCareerGuide, ParentQuestion
from aureon.scripts.seed_parent_connect import GUIDES
from aureon.scripts.seed_parent_questions import QUESTIONS
from aureon.services.llm.factory import get_llm_client
from aureon.services.llm.schemas import LLMMessage
from aureon.services.supabase.client import get_supabase_client

LANGUAGES: dict[str, str] = {"hi": "Hindi", "te": "Telugu"}
BACKUP_PATH = os.path.join(os.path.dirname(__file__), "_translated_parent_connect_content.json")


async def _complete_with_retry(llm, messages, *, temperature, max_retries=5):
    """Groq's free/on-demand tier has a real tokens-per-minute cap —
    retrying with backoff on 429 is the correct response, not a bug
    workaround; the API's own error message tells us how long to wait."""
    for attempt in range(max_retries):
        try:
            return await llm.complete(messages, temperature=temperature)
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait_seconds = 3 * (attempt + 1)
            print(f"    rate limited, waiting {wait_seconds}s...")
            await asyncio.sleep(wait_seconds)


def _save_backup(guide_rows: list[ParentCareerGuide], question_rows: list[ParentQuestion]) -> None:
    with open(BACKUP_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "guides": [g.model_dump(mode="json") for g in guide_rows],
                "questions": [q.model_dump(mode="json") for q in question_rows],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

GUIDE_TRANSLATABLE_FIELDS = [
    "common_misconceptions",
    "earning_reality",
    "career_stability",
    "work_life_balance",
    "growth_opportunities",
    "educational_pathways",
    "alternative_routes",
    "global_demand",
    "risks",
    "opportunities",
]

QUESTION_BATCH_SIZE = 10


def _extract_json_object(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(match.group(0) if match else text)


def _extract_json_array(text: str) -> list:
    text = text.strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    return json.loads(match.group(0) if match else text)


async def _translate_guide_fields(llm, guide: dict, language_name: str) -> dict:
    payload = {k: guide[k] for k in GUIDE_TRANSLATABLE_FIELDS if k in guide}
    prompt = (
        f"Translate the string and list-of-string values in this JSON object into natural, warm, "
        f"parent-friendly {language_name}, written for a parent in India who may be more comfortable "
        f"in {language_name} than English. Keep the exact same JSON keys and structure. Keep numbers, "
        f"currency figures, and career/field names' meaning intact. Respond with ONLY the translated "
        f"JSON object — no explanation, no markdown code fences.\n\n{json.dumps(payload, ensure_ascii=False)}"
    )
    response = await _complete_with_retry(llm, [LLMMessage(role="user", content=prompt)], temperature=0.3)
    return _extract_json_object(response.content or "{}")


async def _translate_question_batch(llm, batch: list[dict], language_name: str) -> list[dict]:
    payload = [
        {"index": i, "question": q["question"], "expert_response": q.get("expert_response", "")}
        for i, q in enumerate(batch)
    ]
    prompt = (
        f"Translate the 'question' and 'expert_response' fields of each item below into natural, warm, "
        f"parent-friendly {language_name}, written for a parent in India who may be more comfortable in "
        f"{language_name} than English. Keep the same 'index' values unchanged and the same array order. "
        f"Respond with ONLY a JSON array of objects with keys index/question/expert_response — no "
        f"explanation, no markdown code fences.\n\n{json.dumps(payload, ensure_ascii=False)}"
    )
    response = await _complete_with_retry(llm, [LLMMessage(role="user", content=prompt)], temperature=0.3)
    return _extract_json_array(response.content or "[]")


async def translate() -> None:
    """Resumable: if a prior run was interrupted (e.g. by a rate limit),
    already-translated rows in the backup file are kept and only the
    missing ones are generated — real LLM output is never silently
    redone or discarded."""
    llm = get_llm_client()
    client = get_supabase_client()

    guide_rows: list[ParentCareerGuide] = []
    question_rows: list[ParentQuestion] = []
    if os.path.exists(BACKUP_PATH):
        with open(BACKUP_PATH, encoding="utf-8") as f:
            existing = json.load(f)
        guide_rows = [ParentCareerGuide.model_validate(g) for g in existing.get("guides", [])]
        question_rows = [ParentQuestion.model_validate(q) for q in existing.get("questions", [])]
        print(f"Resuming from backup: {len(guide_rows)} guides, {len(question_rows)} questions already done.")

    for lang_code, lang_name in LANGUAGES.items():
        done_guide_ids = {g.id for g in guide_rows if g.language == lang_code}
        remaining_guides = [g for g in GUIDES if f"{g['id']}_{lang_code}" not in done_guide_ids]
        print(f"Translating {len(remaining_guides)} guides into {lang_name} ({len(done_guide_ids)} already done)...")
        for guide in remaining_guides:
            translated = await _translate_guide_fields(llm, guide, lang_name)
            row = {**guide, **translated, "id": f"{guide['id']}_{lang_code}", "language": lang_code}
            guide_rows.append(ParentCareerGuide.model_validate(row))
            _save_backup(guide_rows, question_rows)
        print(f"  done: {sum(1 for g in guide_rows if g.language == lang_code)} {lang_name} guides")

        done_question_ids = {q.id for q in question_rows if q.language == lang_code}
        enumerated = [{"id": f"pq_{i:04d}", **q} for i, q in enumerate(QUESTIONS, start=1)]
        remaining_questions = [q for q in enumerated if f"{q['id']}_{lang_code}" not in done_question_ids]
        print(f"Translating {len(remaining_questions)} questions into {lang_name} ({len(done_question_ids)} already done)...")
        for start in range(0, len(remaining_questions), QUESTION_BATCH_SIZE):
            batch = remaining_questions[start : start + QUESTION_BATCH_SIZE]
            translated_batch = await _translate_question_batch(llm, batch, lang_name)
            translated_by_index = {t["index"]: t for t in translated_batch}
            for i, q in enumerate(batch):
                t = translated_by_index.get(i, {})
                row = {
                    **q,
                    "question": t.get("question", q["question"]),
                    "expert_response": t.get("expert_response", q.get("expert_response", "")),
                    "id": f"{q['id']}_{lang_code}",
                    "language": lang_code,
                }
                question_rows.append(ParentQuestion.model_validate(row))
            _save_backup(guide_rows, question_rows)
        print(f"  done: {sum(1 for q in question_rows if q.language == lang_code)} {lang_name} questions")

    print(f"Backed up {len(guide_rows)} guides + {len(question_rows)} questions to {BACKUP_PATH}")

    def _upsert() -> None:
        client.table("parent_career_guides").upsert(
            [g.model_dump(mode="json") for g in guide_rows]
        ).execute()
        client.table("parent_questions").upsert(
            [q.model_dump(mode="json") for q in question_rows]
        ).execute()

    await asyncio.to_thread(_upsert)
    print(f"Seeded {len(guide_rows)} translated guides and {len(question_rows)} translated questions.")


async def upsert_from_backup() -> None:
    """Re-run only the upsert half from the cached backup file — use
    this once migration 0023 has been applied, instead of re-spending
    real LLM calls on content that's already been generated."""
    with open(BACKUP_PATH, encoding="utf-8") as f:
        data = json.load(f)
    guide_rows = [ParentCareerGuide.model_validate(g) for g in data["guides"]]
    question_rows = [ParentQuestion.model_validate(q) for q in data["questions"]]
    client = get_supabase_client()

    def _upsert() -> None:
        client.table("parent_career_guides").upsert(
            [g.model_dump(mode="json") for g in guide_rows]
        ).execute()
        client.table("parent_questions").upsert(
            [q.model_dump(mode="json") for q in question_rows]
        ).execute()

    await asyncio.to_thread(_upsert)
    print(f"Seeded {len(guide_rows)} translated guides and {len(question_rows)} translated questions from backup.")


if __name__ == "__main__":
    if "--from-backup" in sys.argv:
        asyncio.run(upsert_from_backup())
    else:
        asyncio.run(translate())
