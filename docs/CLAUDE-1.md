@AGENTS.md

# Claude Code startup

1. Read the most recent dated handoff ledger (`docs/CLAUDE_CODE_HANDOFF_*.md`)
   on the branch you are working from before proposing work. If none is present,
   or you cannot determine which is current, say so and ask before proposing
   work that touches code, Git history, spending, or governance.
2. Run `/context` and confirm both `CLAUDE.md` and `AGENTS.md` are loaded.
3. Verify the repository, branch, clean/dirty state, current commit, and remote
   PR state. Do not assume `main` contains the current experiment code.
4. Use plan mode before touching governance, provider workflows, spending
   gates, authorization paths, frozen inputs, or preregistered analysis.
5. Treat Claude Code auto memory as a convenience, not a project record. Put
   durable decisions and run state in the dated handoff ledger and Git history.
6. Do not run `/init` over these files. Suggest reviewed edits instead.

Claude Code is the engineering tool. The frozen CapAge experiment model remains
`claude-sonnet-5` at medium effort until a separately versioned experiment says
otherwise. Switching coding tools does not change CapAge's model, authority,
tariff, preregistration, or evidence.

To avoid charging CapAge's experimental API balance for coding sessions, do not
start Claude Code from a shell that exports `ANTHROPIC_API_KEY`. Authenticate
Claude Code separately. Repository workflows may reference that GitHub secret,
but cloning the repository does not reveal its value.
