# Admit rules

`admit` is fail-closed lexical admission of a user-supplied path against `jail_root`. An unreadable path file or policy is a process error (exit 2). A candidate string that can be read must produce an allow or deny report.

Reuse `load_path`, `probe_path`, and `load_policy`. Do not call `os.path.realpath`, do not walk the filesystem, and do not follow symbolic links. Work on POSIX-style strings even when this machine is Linux.

## Raw string

- After the CLI strips at most one trailing `\n` (not `\r\n` as a pair unless the file ended in a lone `\n`), if the raw string is longer than `max_bytes` (default 256) counted in UTF-8 bytes, `too_long`.
- A NUL, CR, LF, other C0 byte, or DEL in the raw string is `control_char`.
- A backslash in the raw string is `backslash`.
- An empty string is `empty`.

## Decode and segments

- Perform exactly one percent-decode of the raw string: `%HH` with hexadecimal `HH` becomes that byte, then decode the result as UTF-8. A lone `%`, a `%` not followed by two hex digits, or a UTF-8 decode failure is `bad_encoding`.
- Do not decode a second time. `%252e%252e` must remain the literal segments `%2e` `%2e`, which are ordinary names, not `..`.
- If the decoded string starts with `/`, or starts with `//`, it is `absolute` (`allow_absolute` is false in the public policy).
- A Windows drive prefix such as `C:` or `C|` at the start of the decoded string is `windows_path`.
- Split the decoded string on `/`. Empty segments from a trailing slash are allowed and ignored. A segment that is `.` is ignored. A segment that is `..` (after the single decode) is `dotdot`.
- A segment of `.` or `..` produced only after a forbidden second decode must not be treated as `dotdot`. `fixtures/paths/encoded-dotdot.txt` contains `%2e%2e/secret` and must be `dotdot`. `fixtures/paths/double-encoded.txt` contains `%252e%252e/secret` and must be allow (it is not `dotdot`).

## Jail join

- Let `jail_root` be an absolute POSIX path with no trailing slash except the root `/`. The public policy uses `/srv/app/static`.
- Join remaining segments under `jail_root` using POSIX rules (`/srv/app/static` + `css/app.css` → `/srv/app/static/css/app.css`).
- The resolved path must equal `jail_root` or start with `jail_root + "/"`. Otherwise `escape`. This should already be guaranteed if `..` was rejected, but still check.
- Do not consult the real filesystem to answer this.

## Public fixtures (`fixtures/policy.json`)

- `fixtures/paths/ok-rel.txt` (`css/app.css`) → allow, resolved `/srv/app/static/css/app.css`
- `fixtures/paths/ok-nested.txt` (`img/icons/ok.png`) → allow
- `fixtures/paths/dotdot.txt` (`../etc/passwd`) → deny / `dotdot`
- `fixtures/paths/encoded-dotdot.txt` (`%2e%2e/secret`) → deny / `dotdot`
- `fixtures/paths/double-encoded.txt` (`%252e%252e/secret`) → allow
- `fixtures/paths/absolute.txt` (`/etc/passwd`) → deny / `absolute`
- `fixtures/paths/backslash.txt` (`css\\app.css`) → deny / `backslash`
- `fixtures/paths/nul.txt` (contains a NUL) → deny / `control_char`

## Exit status

- `allow` → exit 0
- `deny` → exit 1
- Path file or policy load errors → exit 2, and do not write a report that claims `allow`.
