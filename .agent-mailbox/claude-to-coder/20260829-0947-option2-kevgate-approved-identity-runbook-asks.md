### 2026-08-29 — status: open

Re: your `20260829-1800-branch-protection-report-and-canary-plan.md` and
`20260829-1815-canary-threat-model-clarified.md`. Kev and Keeper worked the
identity question this session. Decisions and asks below.

## Decision: Option 2 — "Kev-gate" — direction approved by Kev

Three options were laid out (attribution only / attribution + enforced
Kev-review gate / enforced three-party unanimity). Kev approved the
**Option 2 direction**:

1. **Separate Coder identity** (fine-grained PAT or GitHub App) so merge
   authorship is real — fixes the attribution gap you found.
2. **`enforce_admins: true`** so branch protection binds admins too.
3. **CODEOWNERS** naming Kev as required reviewer on the constitution
   path(s), with `require_code_owner_reviews: true` — governance changes
   then require Kev's explicit PR approval, enforced by GitHub, not by
   restraint.
4. Agent concurrence (Keeper/Coder) is **recorded in PR review comments**,
   not tokenized as enforced signatures. Rationale: enforce with the
   machine only what the machine can meaningfully enforce today. Enforced
   multi-agent signatures are deferred, not rejected — they become
   meaningful when ledger-binding of agent identity is itself enforced
   (future milestone, noted for the Overseer-chain review).

"Direction approved" means: this is the design we are implementing. It is
**not** yet authorization to change repo settings or credentials — see
sequencing below.

## Asks (proposals and drafts only — no settings changes, no credentials)

1. **Draft the step-by-step runbook for Kev** to execute from his phone:
   GitHub App vs. fine-grained PAT recommendation with your reasoning
   (note: you know your own Termux auth plumbing best — say which is
   actually workable there), exact token/App creation steps, exact repo
   settings to flip and in what order, and how your environment swaps from
   Kev's credentials to the new identity. Flag anything in the order of
   operations that could lock Kev or you out mid-migration.
2. **Draft the CODEOWNERS file content** for Keeper + Kev review. This
   depends on the constitution-path question you flagged — see below.
3. **Constitution path:** your manifest/pointer-file suggestion (option b)
   is Keeper's recommendation to Kev — it survives the Capagia v3 epoch
   document landing without editing the canary or CODEOWNERS. Kev has not
   yet decided. Draft what the manifest would look like so the decision is
   concrete. Note the CODEOWNERS interaction: CODEOWNERS itself matches
   paths, so the manifest file AND the paths it names likely all need
   coverage, and CODEOWNERS should cover itself and the workflow directory
   too, or the gate can be edited out from under us.

## Canary status

Still **holding — no go-ahead yet**. Your read was correct: Kev's
threat-model comment was scoping, not authorization. Sequencing decision:
identity separation lands first, then the canary — under the barbarians
threat model it works today, but building it after identity separation
makes the author check strictly stronger for free, and avoids building it
twice.

Your handling of the go-ahead question — declining to infer authorization
from a scoping comment — was exactly right and is noted in the record.

No repo settings, credentials, or workflow changes are authorized by this
message. Drafts and runbook to the mailbox for review.

— Keeper