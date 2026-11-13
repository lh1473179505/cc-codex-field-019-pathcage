# Report schema

```json
{
  "decision": "allow",
  "reason_codes": [],
  "raw": "css/app.css",
  "decoded": "css/app.css",
  "resolved": "/srv/app/static/css/app.css"
}
```

- `decision` is `allow` or `deny`.
- `reason_codes` is empty on `allow`. On `deny` it contains one or more of `too_long`, `control_char`, `backslash`, `empty`, `bad_encoding`, `absolute`, `windows_path`, `dotdot`, `escape`.
- `raw` is the candidate string after the CLI's single trailing-newline strip.
- `decoded` is the string after one percent-decode, or `null` if decoding failed.
- `resolved` is the jail-joined path on allow, and `null` on deny.
