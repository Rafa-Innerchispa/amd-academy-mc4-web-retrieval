# Match 4 demo UI

Presentation layer for the Match 4 web-retrieval core.

This UI is intentionally isolated from the future official grader adapter. It makes the capability usable without contaminating the minimal submission contract.

Run from the repository root:

```bash
python -m demo.server
```

Open `http://127.0.0.1:8787`.

Endpoints:

- `GET /health`
- `POST /api/retrieve`
- static demo UI

The API accepts:

```json
{
  "query": "What is the current price?",
  "url": "https://example.com/product",
  "max_hops": 5
}
```

The response is the internal `RetrievalResponse` schema. This is **not** claimed to be the official AMD/LabLab grader contract.
