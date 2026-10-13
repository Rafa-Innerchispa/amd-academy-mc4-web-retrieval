import argparse
import json
import sys
from .agent import WebRetrievalAgent
from .models.schema import RetrievalRequest

def main():
    parser = argparse.ArgumentParser(description="AMD AI League Match 4 — Web Retrieval Agent CLI")
    parser.add_argument("--query", "-q", required=True, help="Natural language request or question")
    parser.add_argument("--url", "-u", default=None, help="Seed URL to start retrieval")
    parser.add_argument("--max-hops", type=int, default=5, help="Maximum navigation hops")
    parser.add_argument("--json", action="store_true", help="Output raw JSON response")

    args = parser.parse_args()

    agent = WebRetrievalAgent()
    request = RetrievalRequest(query=args.query, seed_url=args.url, max_hops=args.max_hops)
    response = agent.execute(request)

    if args.json:
        print(response.model_dump_json(indent=2))
    else:
        print(f"==================================================")
        print(f"Status: {response.status}")
        print(f"Verification: {response.verification_status.value}")
        print(f"Query: {response.query}")
        if response.answer:
            print(f"Answer: {response.answer}")
        if response.provenance:
            print(f"Evidence Source: {response.provenance.source_url}")
            print(f"Snapshot SHA-256: {response.provenance.snapshot_hash[:16]}...")
            print(f"Verbatim Span: \"{response.provenance.verbatim_text}\"")
        if response.failure_reason:
            print(f"Failure Reason: {response.failure_reason}")
        print(f"Navigation Steps: {len(response.navigation_trail)}")
        for step in response.navigation_trail:
            print(f"  [{step.step_number}] {step.action} -> {step.target_url} ({step.reason})")
        print(f"==================================================")

    if response.status == "SUCCESS":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
