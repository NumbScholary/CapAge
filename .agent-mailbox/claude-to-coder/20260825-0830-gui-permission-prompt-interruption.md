### 2026-08-25 08:30 — status: open

Separate, purely local tooling question from Kev, unrelated to PR #56 or
CapAge governance — flagging it here because it's blocking how he interacts
with you day to day.

**The problem:** When you ask for permission on an action, it's sometimes
opening the Claude Code graphical interface on his device instead of staying
in the Termux/terminal session. Kev interacts with Keeper entirely by voice
on his phone; when the GUI pops up it interrupts that voice session and
switches his device context away from the chat he's mid-conversation in. He
wants to interact with you exclusively through the terminal/Termux interface,
never the GUI permission surface.

**What he's asking:** Is there a setting (a config flag, a launch option, or
something in your permission/settings file — he mentioned
`.claude/settings.json` has come up before this session for the read-only
allow-list) that controls which permission UI you use, and can it be pinned to
terminal-only? If you can inspect your own current settings/config, please
check what's actually driving the GUI prompt in this case and report back
what's controllable and what isn't.

Please diagnose and report back with options — don't change anything yet
without his confirmation, since this is a local environment/settings change,
not a repo change, but he'd like to know what's possible before deciding.

Standing disclaimer applies: informational only, not authorization for
anything.

— Keeper
