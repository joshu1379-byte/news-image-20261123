# Entry notes — news-image-20261123

- Slug: `news-image-20261123` — "Sum up 23 November's world news in one image"
- Prize: $100 USDC total (1st $20, 2nd $12, 3rd $6, 4th–10th $2, 11th–50th $1.20)
- Deadline: 2026-11-25T00:00:00Z. Result due by 2026-12-09T08:00:00Z.
- Blind rounds (no scores visible): rounds at 2026-11-23T12:00Z,
  2026-11-24T00:00Z, 2026-11-24T12:00Z, 2026-11-25T00:00Z (final).
  Field (2026-11-23 ~09:10 UTC): 7,107 entries and growing (the
  22 Nov contest reached 18,634).

## The image

`main.py` (Python 3.13, stdlib only) draws a 1024×1024 newspaper front
page: masthead "MONDAY 23 NOVEMBER 2026", lead "Ukraine sinks Russian
warship" (corvette Merkury at Benghazi), 6 cards (Russian strike kills
10 in Dymer; Democrats win 258 House seats; Nikkei −5.06% as the AI
sell-off spreads; Iran claims a US MQ-9A Reaper downed; Indonesia
seizes a ship carrying 405 t of sodium perchlorate; Riemann Hypothesis
proof claimed by Levent Alpoge and Claude), and an "also today" strip
(penny ends — Common Cents Act; South Korea exports top $1T; Belgian
airport strike; Delta outage resolved). 11 stories total, verified
against AP / BBC / France 24 and wire reporting.

IMPORTANT LIMIT: this covers news reported by late morning of 23 Nov
2026 (UTC) — refreshed ~11:00 UTC with two major stories the morning
build missed (COP31 climate talks collapsing in Antalya over fossil
fuels; Trump calling Putin "my friend" after the Shenzhen summit),
replacing the Belgian airport strike and the Delta outage in the
"also today" strip. The day was still in progress when the entry was
built. US daytime news (afternoon/evening UTC) is not in it yet. For
the best result, refresh the news data in `main.py` with the full day's
news after 23 Nov ends (in a fresh agent session, so the transcripts
cover the change), re-render, re-verify, and resubmit before the
deadline.
Blind round 1 closes 2026-11-23T12:00Z; submitting the current version
before then still banks a round-1 entry, and a refreshed version can
replace it in a later round (last submission before the deadline is
the final entry).

## Local verification (2026-11-23)

- Ran twice: identical sha256
  `4671c23c0d8202315d764b9273572bc1201962cd4155c6f49f7b3a8069e3bdb5`
  (after the ~11:00 UTC refresh; 23,138 bytes). Previous version (morning
  build): `08ab679e2a38f1188259e34867514330bb8f9f82761207059c10b53570fd40e9`
  (23,161 bytes).
- PNG valid (all chunk CRCs pass), 1024×1024, 23,138 bytes ≤ 1 MiB.
- Visually inspected at full size and at 300 px wide: date, lead
  headline and card headlines stay legible; no text overflows any card;
  the refreshed "also today" strip (COP31, Trump/Putin) fits in two
  lines per item with no overlap.
- Kit `grade-local`: NOT available — program/v1 is graded on the
  server only ("its scorer and reference data are not published").
- Kit `check --worktree`: 4 passed (competition_open, snapshot,
  license_osi, entrypoint); 1 failed: transcripts_present (no bundle
  yet — expected, bundle is made at submit time); 5 checks deferred to
  submission (repo_public, repo_owner, repo_created_after_open,
  commit_in_repo, duplicate_snapshot — no GitHub repo exists yet).

## Honest rank estimate

- Top 50: possible but less likely than the 22 Nov entry as it stands
  (roughly 10–20%), because it only covers the morning's news while
  rival entries built later in the day will cover the full day. Top 10:
  unlikely (<5%). #1: no evidence for it; not claimed.
- If refreshed with the full day's news before the deadline, treat its
  odds like the 22 Nov entry's (top 50 plausible, roughly 15–25%).
- No local score exists to compare against the board (blind rounds
  hide all scores, and grading is server-only), so this is a
  qualitative judgement, not a measured rate.

## Remaining steps before submit (NOT done)

1. Optional but recommended: refresh the news data for the full day
   of 23 Nov (see above), re-render and re-verify.
2. Create a public GitHub repo (after 2026-11-23T00:00:00Z opening)
   and push these files; or submit as a source bundle.
3. README.md: replace GITHUB-OWNER / GITHUB-REPO in the rank and
   reward badge URLs with the real owner/repo. Also set the repo's
   About (description/homepage/topics) per the requirements'
   repo_about template.
4. Bundle the transcripts of the sessions that built this entry
   (parent agent, from the top-level session once subagents finish),
   with system prompt + run record; re-run `check` with the bundle.
5. Submit with the kit CLI before 2026-11-25T00:00:00Z (and before
   2026-11-23T12:00Z to make blind round 1):
   `node cli/makefun.mjs submit --competition news-image-20261123
   --repo-url <url> --commit <sha> --title <name> --bundle <file>
   --keypair <file>` (entry is signed with Gregory's wallet).
6. Do NOT submit without Gregory's explicit confirmation.
