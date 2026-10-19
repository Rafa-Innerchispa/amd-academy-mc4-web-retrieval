from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable, Optional

from src.agent import WebRetrievalAgent
from src.config import AgentConfig
from src.io.atomic_output import initialize_empty_output, write_json_atomic
from src.models.schema import RetrievalRequest


DEFAULT_OUTPUT_DIR = Path(os.getenv("AGENT_OUTPUT", "/app/output"))


def first_nonempty(values: Iterable[Optional[str]]) -> Optional[str]:
    for value in values:
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Provisional AMD AI League Match 4 grader adapter",
        add_help=True,
    )
    parser.add_argument("positional_query", nargs="?")
    parser.add_argument("--query", "-q")
    parser.add_argument("--question")
    parser.add_argument("--task")
    parser.add_argument("--prompt")
    parser.add_argument("--query-id")
    parser.add_argument("--id")
    parser.add_argument("--task-id")
    parser.add_argument("--url")
    parser.add_argument("--start-url")
    parser.add_argument("--website")
    parser.add_argument("--site")
    parser.add_argument("--output-dir")
    parser.add_argument("--max-hops", type=int, default=5)
    parser.add_argument("--allow-private-host", action="append", default=[])
    parser.add_argument("--input", "--input-file", "--tasks", dest="input")
    parser.add_argument("--warmup", action="store_true")
    parser.add_argument("--index", nargs="?")
    parser.add_argument("--corpus", nargs="?")
    return parser


def render_payload(response) -> dict:
    if response.status != "SUCCESS" or not response.answer or not response.provenance:
        return {
            "answer": "",
            "sources": [],
            "citations": [],
            "source_url": "",
            "confidence": 0.0,
        }

    source = response.provenance.source_url
    return {
        "answer": response.answer,
        "sources": [source],
        "citations": [source],
        "source_url": source,
        "confidence": 1.0,
    }


def execute_one(
    *,
    query_id: str,
    query: str,
    url: Optional[str],
    output_dir: Path,
    max_hops: int,
    allowed_private_hosts: list[str],
) -> dict:
    output_path = output_dir / f"{query_id}_output.json"
    initialize_empty_output(output_path)

    config = AgentConfig(
        allowed_private_hosts=allowed_private_hosts,
        allow_private_network_targets=False,
    )
    agent = WebRetrievalAgent(config=config)
    response = agent.execute(
        RetrievalRequest(
            query=query,
            seed_url=url,
            max_hops=max_hops,
        )
    )
    payload = render_payload(response)
    write_json_atomic(output_path, payload)
    return payload


def load_batch(path: str) -> list[dict]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("tasks", "queries", "items"):
            if isinstance(raw.get(key), list):
                return raw[key]
    raise ValueError("unsupported_batch_shape")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args, _unknown = parser.parse_known_args(argv)

    # MC3-style startup hooks are accepted as harmless no-ops until the
    # official Match 4 kit defines whether startup/indexing is required.
    if args.warmup or args.index is not None:
        return 0

    output_dir = Path(args.output_dir or DEFAULT_OUTPUT_DIR)

    if args.input:
        for index, item in enumerate(load_batch(args.input), start=1):
            query = first_nonempty([
                item.get("query"),
                item.get("question"),
                item.get("task"),
                item.get("prompt"),
            ])
            query_id = first_nonempty([
                item.get("query_id"),
                item.get("id"),
                item.get("task_id"),
                f"q{index:03d}",
            ])
            url = first_nonempty([
                item.get("url"),
                item.get("start_url"),
                item.get("website"),
                item.get("site"),
            ])
            if not query:
                continue
            execute_one(
                query_id=query_id or f"q{index:03d}",
                query=query,
                url=url,
                output_dir=output_dir,
                max_hops=args.max_hops,
                allowed_private_hosts=args.allow_private_host,
            )
        return 0

    query = first_nonempty([
        args.query,
        args.question,
        args.task,
        args.prompt,
        args.positional_query,
        os.getenv("AGENT_QUERY"),
        os.getenv("QUERY"),
    ])
    query_id = first_nonempty([
        args.query_id,
        args.id,
        args.task_id,
        os.getenv("AGENT_QUERY_ID"),
        os.getenv("QUERY_ID"),
        "query",
    ])
    url = first_nonempty([
        args.url,
        args.start_url,
        args.website,
        args.site,
        os.getenv("AGENT_URL"),
        os.getenv("START_URL"),
        os.getenv("URL"),
    ])

    if not query:
        parser.error("query is required")

    execute_one(
        query_id=query_id or "query",
        query=query,
        url=url,
        output_dir=output_dir,
        max_hops=args.max_hops,
        allowed_private_hosts=args.allow_private_host,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
