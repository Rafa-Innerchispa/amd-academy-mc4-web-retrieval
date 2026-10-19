# Provisional Match 4 grader adapter

This directory contains a **thin compatibility adapter**, not a claim about the final official Match 4 contract.

Why it exists now:

- the official MC3 starter kit established the programme's `/app/app.py` execution pattern;
- multiple public Match 4 submissions describe one query per invocation and one JSON output file per question;
- the public Match 4 starter kit/detail link is still unavailable from the League page.

The adapter therefore accepts several harmless aliases while keeping the retrieval core independent.

Supported query aliases:

- `--query`
- `--question`
- `--task`
- `--prompt`
- one positional query

Supported ID aliases:

- `--query-id`
- `--id`
- `--task-id`

Supported start-page aliases:

- `--url`
- `--start-url`
- `--website`
- `--site`

It also supports a JSON batch file through `--input`.

Default output path:

`/app/output/<query-id>_output.json`

The provisional payload includes:

```json
{
  "answer": "...",
  "sources": ["https://..."],
  "citations": ["https://..."],
  "source_url": "https://...",
  "confidence": 1.0
}
```

On failure it writes an empty valid result rather than invented content.

## Important

Once the official Match 4 starter kit is released:

1. remove unsupported aliases if the contract is strict;
2. reduce the output schema to the exact allowed keys;
3. replace no-op startup hooks with the exact official startup behavior;
4. lock the network policy to the official target-site topology;
5. rerun all official examples/selfchecks before building `mc4-final`.
