# pathcage

A small fail-closed lexical path admission tool. Path probing already works. `inspect` can print the raw bytes, decoded segments, and jail-relative join. `admit` is still a stub in this snapshot.

A static-file handler that concatenates a user path onto a jail root can be walked out with `..` or `%2e%2e`. This tool must keep the resolved path inside the jail after a single percent-decode.

## Requirements

- Python 3.11+
- Standard library only
- No containers. Do not follow real symlinks and do not touch the host filesystem beyond reading the candidate path file and the policy.

## Already working

```bash
python -m pathcage inspect --path fixtures/paths/ok-rel.txt
```

## Intended CLI

```bash
python -m pathcage admit \
  --path fixtures/paths/ok-rel.txt \
  --policy fixtures/policy.json \
  --report /tmp/pathcage-report.json
```

`--path` is a file whose entire contents (minus one trailing newline, if present) is the candidate path string. Parameter names are fixed in `pathcage/__main__.py`. Keep them.
