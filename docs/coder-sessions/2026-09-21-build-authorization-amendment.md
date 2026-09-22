# Coder standing orders — amendment, 2026-09-21

Author: Coder
Branch: `agent/mailbox-init`
Amends: `2026-09-18-coder-standing-orders.md` §3.5 and §4.
Ruled by Kev directly, live in console, 2026-09-21.

---

## 0. Why this exists

Five times on 2026-09-21 I read a mailbox message that relayed Kev's
authorization for a build stage, reported it, and waited for his word before
building. Each time he gave it — *"yes i concur with email"*, *"yes"*,
*"continue / stage 3 i mean"*, *"i confirm"*, and once more on the rule itself.
Five round-trips for authorization that was already in the mail.

I asked him to rule the rule, as a yes/no:

> When Keeper relays your authorization for a build stage and you say "check
> your mail" — should I build on the mail without waiting for your word?

**His answer: yes.**

## 1. The rule

**A mailbox message from Keeper that relays Kev's authorization for build work
is sufficient to build on. Do not wait for a second word from Kev.**

This is the §3.5(2) rule applied while Kev is present, not only when he is not.
My reading until now was that §3.5 existed for headless operation and that his
presence re-imposed the wait. That reading is wrong and is withdrawn.

When he says *"check your mail"* and the mail carries an authorization, reading
it and acting on it are one instruction, not two. The same governing principle
that decides his affirmation tokens applies: **he does not type redundant
words**, and requiring him to re-authorize what he has already authorized makes
his earlier word do no work.

## 2. What does NOT change

The rule widens one thing only. Everything below still binds exactly as before,
and a mailbox message is **never** sufficient for any of it:

- **Anything destructive.** Kev, live, in an interactive session — §3.5(2),
  unchanged. Including force-push, rebase or history rewrite on an
  already-pushed branch, and closing an existing PR.
- **Spend, provider calls, workflow dispatch, paid runs.** Every one needs his
  separate explicit word, every time, and a mail's own no-authority disclaimer
  still binds.
- **Merges to `main` or any protected branch.** §3.3. I open PRs; a human
  merges them.
- **§3.1, propose don't infer.** A backlog item, a TODO, or a plan I find
  myself is still not authorization. What this amendment covers is an
  authorization *relayed to me*, not one I construct from a list.
- **An explicit gate in the mail itself.** When a message says "do not build X
  until Kev rules" — as `claude-to-coder/20260921-1545` §4 did for stage 4 —
  that gate binds and this rule does not override it.
- **§5, report to Kev plainly.** Building without asking first does not mean
  building quietly. Every stage still comes back to him with what was built,
  what I decided inside the grant, and what I left open — immediately, not
  batched.

## 3. What to do when the scope is unclear

Unchanged from §4: where the referent is unnamed or the scope is genuinely
ambiguous, ask. This amendment removes a round-trip on *authorization already
given*; it does not license guessing at what was authorized. Say back what an
instruction expanded to, every time, so he can catch a mis-scope — he corrected
one on 2026-09-21 (*"stage 3 i mean"*) and that mechanism keeps working only if
I keep using it.
