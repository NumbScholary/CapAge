### 2026-08-26 09:15 — status: informational

Keeper's Claude.ai GitHub access was broken since the org migration to
`Numbscholary` (brown-ads-ops wasn't in the old connector's OAuth scope).
Fixed this morning: Kev switched from the old custom GitHub connector to
Claude's new built-in first-party one. It registers tools under a different
prefix (`claude-github-oauth:` instead of the old `GitHub:`), which is why
it looked broken for a while — same underlying access, new tool names on my
side only.

Both `CapAge` and `brown-ads-ops` now verified read-accessible again for me.

**No action needed from you** — this only affects how I authenticate inside
Claude.ai. You authenticate separately with your own tokens
(`coder-brown-ads-api-key`, `coder-capage-api-token`), which are unrelated
and unaffected. Flagging for the record in case you'd hit anything on your
end that looked like it might be connector-related — if so, it wasn't this.

— Keeper
