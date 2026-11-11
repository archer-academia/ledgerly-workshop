# Keeping coding agents from drifting

*Archer · AI Coding Agents workshop · hands-on companion to the Fundamentals & Advanced decks*

Coding agents don't fail loudly. They drift: they follow a stale README, reuse the legacy
helper, "fix" a test so it passes, declare done without running your gates. Each run looks fine
in isolation, and the tests are often green.

This workshop teaches students to **see drift, measure it, and close it**, one mechanism at a
time, on a sample codebase built to drift.

| | |
|---|---|
| 🎯 **Goal** | students leave able to protect an agent's work from drift: they can name the drift, measure it as a rate, and close it with the right mechanism |
| 👥 **Who** | developers who already use a coding agent (Claude Code primary, Cursor sidebars) |
| 📅 **Format** | 2 days · Day 1 the harness (Ex 0–5) · Day 2 process on top (Ex 6–8) |
| 🧪 **Sample app** | [Ledgerly](#-ledgerly-the-sample-app-and-its-landmines): Python, FastAPI, uv |
| 🚀 **Start here** | [Ex 0 · Orientation](exercises/ex00-orientation/): the app, the tools, the drill loop |

## 🔁 The method: TDD for agent behaviour

![See the drift fail, add one mechanism, watch it go green](assets/method.png)

Every exercise is a **drill** (a fixed prompt) plus a **drift check** (a deterministic script
that grades what the agent did and left behind).

```
🔴 RED       run the drill without the mechanism → watch the drift check fail
🟢 GREEN     add exactly one mechanism → same drill → green
🔵 REFACTOR  make it smaller / better placed → still green, cheaper
→ LEFTOVER   the red this mechanism can't fix motivates the next exercise
```

Two rules hold throughout:

1. **Loaded ≠ obeyed.** Every cycle has a *load check* (did it enter the context?) and a
   *behavior check* (did it change what happened?).
2. **Measure in rates.** Agents are nondeterministic. A drill runs 3–5 times per variant, and
   "2/3" counts as a result. The course's through-line is moving rules from *advisory*
   (a rate) to *enforced* (always):

![From advisory (a rate) to deterministic (always)](assets/spectrum.png)

## 🛡️ What we protect against

| drift | example in Ledgerly | first caught by |
|---|---|---|
| Knowledge the code can't show | splits installments its own way: tests green, says "done", wrong by a cent (0/4 → 3/3 with CLAUDE.md) | Ex 1 · CLAUDE.md |
| Wrong source of truth | trusts the 2021 README: `make test`, Flask, dollars | Ex 1 Part 2 (guard check) |
| False "done" | stops after pytest; never runs ruff / import-linter | Ex 1 → Ex 3 `Stop` hook |
| Architecture | builds on float `legacy_fx`; API imports the DB | Ex 1 → import-linter gate |
| Convention / scope | team rule in one person's `~/.claude` | Ex 1 (going further, LED-112) |
| House style the code doesn't show | `frozen + slots + kw_only` value objects, no tuples/dicts from services | Ex 1 Part 2 · rules (RED 5/5 → GREEN 5/5) |
| Grader tampering | edits a test to make the suite pass | Ex 1 (measured) → Ex 3 hook |
| Outdated libraries | deprecated FastAPI / Pydantic APIs from training data | Ex 4 · MCP (Context7) |
| Tests that check nothing | mirror tests on refunds; skipping a flaky test | Ex 5 · mutation judge |
| Unchecked procedure | PR note in the wrong format, gates claimed but never run | Ex 2 · skills |
| Security | reads `.env`, edits `generated/`, destructive migrations | Ex 3 PreToolUse |
| Spec drift | builds what it *thought* you meant | Day 2 · Ex 8 Spec Kit |

## 🗂️ Repo map

```
ledgerly-workshop/
├── README.md            ← you are here
├── ledgerly/            ← the sample app. Open Claude Code HERE. Plain files in this repo; tools/setup.sh
│                          also makes it a local git repo with tag `baseline` (see below).
├── exercises/           ← one folder per exercise
│   ├── ex00-orientation/  ← start here: the app, the tools, the loop
│   └── ex01-claude-md/
│       ├── exercise.html  ← the student page: steps, prompts, hints, timer, reference
│       ├── README.md      ← goal, flow, how it's judged, facilitator notes
│       ├── LESSONS.md     ← takeaways + a table for your own numbers
│       ├── img/           ← the exercise's diagram
│       ├── drills/        ← tickets the agent runs + what the drift checker looks for
│       └── reference/     ← reference implementation as real files (mirrors ledgerly/)
├── tools/               ← drill runner, drift checker, observers, doctor
├── assets/              ← diagrams for the READMEs
├── runs/                ← created by the tools: transcripts + results (git-ignored)
└── my-variants/         ← your saved CLAUDE.md attempts (tools/snapshot.sh)
```

![The doer never sees the judge](assets/drill-loop.png)

**Why are the exercises outside the app?** Because the agent runs inside `ledgerly/` and reads
whatever it finds. Answer keys next to the code would leak into its context. Keeping the grader
where the doer can't see it is itself a lesson (LED-103, Ex 3).

## ⚙️ Setup (10 min, before class)

🩺 Shortcut: `tools/doctor.sh` checks all of this and tells you what's missing. [Ex 0](exercises/ex00-orientation/exercise.html) walks through it.

Requirements: [Claude Code](https://code.claude.com), [uv](https://docs.astral.sh/uv/), git,
python3. Optional: Cursor.

**First run:** any tool (or `tools/setup.sh`) turns `ledgerly/` into a local git repo with a
`baseline` tag. It's tracked here as plain files, so it's on GitHub; the local `.git` inside it
makes the agent see `ledgerly/` as its own project, so `git status`, `git log` and `git ls-files`
never reveal `exercises/`. Your memory files in `ledgerly/` (CLAUDE.md, `.claude/`…) are
git-ignored by the workshop repo.

Run everything from the **workshop root** (`ledgerly-workshop/`). The Python project lives in
`ledgerly/`, so point uv at it with `--directory` instead of `cd`-ing back and forth:

```bash
cd ledgerly-workshop
uv --directory ledgerly sync                  # creates ledgerly/.venv
uv --directory ledgerly run pytest -q         # 21 passed, 1 deselected
uv --directory ledgerly run ruff check . && uv --directory ledgerly run lint-imports
tools/reset.sh                                # puts ledgerly/ back to the `baseline` tag at any time
```

`uv sync` in the workshop root fails with "No `pyproject.toml` found": that's the reminder to add
`--directory ledgerly`. The `tools/` scripts already run uv inside `ledgerly/` for you. Inside a
Claude Code session started in `ledgerly/`, plain `uv run pytest -q` is correct (that's what the
project's CLAUDE.md says).

> ⚠️ `tools/reset.sh` deletes untracked files in `ledgerly/`, including your CLAUDE.md.
> Save attempts first with `tools/snapshot.sh <name>`.

## 💣 Ledgerly: the sample app and its landmines

![Ledgerly: it works, its tests pass, and it's built to drift](assets/ledgerly.png)

An invoicing & refunds API: FastAPI, SQLite, integer-cent `Money`, three layers
(`api → services → repo`, enforced by import-linter), four ADRs. It works and its tests pass.
It also contains what real repos contain:

| landmine | where | used in |
|---|---|---|
| Stale README (Flask, Postgres, `make test`, decimal dollars) | `README.md` | Ex 1 (Part 2, LED-105), Ex 4 |
| Float-based legacy FX + a legacy report built on it | `payments/legacy_fx.py`, `services/reports.py` | Ex 1 (Part 2, LED-105) |
| Legacy route that bypasses the service layer | `api/routes_refunds.py` (+ an `ignore_imports` exception) | Ex 5 (refund mutants), Ex 7 (LED-101) |
| No error convention in code (it lives in people's heads) | API errors | Ex 1 (going further, LED-112) |
| VAT rounding that surprises customers (by design, ADR-0004) | `services/tax.py` | Ex 1 close (step 10, LED-103), Ex 3 |
| Fake secrets, not git-ignored | `.env` | Ex 3 |
| Generated code: "DO NOT EDIT" | `generated/tracker_client.py` | Ex 3 |
| Applied, destructive migration | `migrations/003_drop_audit_log_old.sql` | Ex 3 |
| Lint & architecture config an agent could "relax" | `ruff.toml`, `.importlinter` | Ex 3 |
| Flaky test (~10%: random invoice numbers collide) | `tests/test_invoices.py` `-m landmine` | Ex 5 (LED-118 trap) |

## 🧰 Tools

| command | what it does |
|---|---|
| `tools/setup.sh` | first run only (automatic): make `ledgerly/` a local repo with tag `baseline` |
| `tools/doctor.sh [--quick]` | is this machine ready? tools, the `baseline` tag, `uv sync`, and green gates (Ex 0) |
| `tools/reset.sh [--keep-memory]` | `ledgerly/` → `baseline`. `--keep-memory` undoes the agent's code but keeps your CLAUDE.md files |
| `tools/start.sh <drill>` | ready `ledgerly/` for a drill: keep your memory files, apply the drill's start state (e.g. LED-105 already implemented for `led-120`) |
| `tools/check.sh <drill>` | grade `ledgerly/` + your newest Claude Code session, e.g. `tools/check.sh led-105` |
| `tools/run_drill.sh <drill> <none\|current\|folder> [N]` | N × (reset → apply memory files → `claude -p` headless → drift check), then a pass-rate table |
| `tools/apply_variant.sh <folder>` | copy a set of memory files (e.g. `exercises/ex01-claude-md/reference`) into `ledgerly/` |
| `tools/snapshot.sh <name>` | save your memory files as `my-variants/<name>` |
| `python3 tools/drift_check.py --summary runs/<drill>` | pass rates per variant, plus avg tool calls / tokens / cost |
| `tools/observe.sh on\|tail\|off` | log every CLAUDE.md / rule load (`InstructionsLoaded` hook) to `runs/loads.log` |
| `python3 tools/memory_size.py [file]` | approximate token cost of memory files, following `@imports` |
| `python3 tools/skill_lint.py <skill> [--profile …]` | static skill checks from the Skills lecture (frontmatter, triggers, sandbox, fork) |
| `python3 tools/skill_eval.py <evals.json> [--runs N] [--baseline]` | evaluate a skill like a feature: trigger recall, false fires, quality with vs without it (Ex 2 Step 5) |
| `python3 tools/hook_test.py [fence\|lint\|finish]` | run the hook test suites (JSON on stdin → expected allow/ask/deny/block) against `ledgerly/.claude/hooks/` (Ex 3) |
| `tools/demo_reference.sh <drill> red\|green` | facilitator fallback: apply the hand-written reference patch and check it |

Drills can be named by prefix: `led-100` (warm-up, Ex 0), `led-107` (installments, Ex 1), `led-105` (revenue endpoint), `led-112` (404 errors), `led-103` (impossible VAT ticket),
`led-120` (PR note), `trigger-implicit`, `trigger-quiet`, `led-132` (relax the lint), `led-141` (seed data,
deprecated APIs), `led-150` / `led-151` (refund tests, weak vs contract), `led-118` (the flaky test). An ambiguous prefix is refused, never guessed.

`run_drill.sh` runs Claude Code headless with `--permission-mode acceptEdits` and an allowlist of
project commands (`uv run`, `git diff`, …). Everything else is denied. Set `MODEL=…` to pin a model.

## 🗺️ Exercise map

![Two days, one gated repo](assets/path.png)

Timings and agenda slots for every exercise: [PLAN.md](PLAN.md).

### 📅 Day 1: the harness, one building block at a time (Fundamentals deck)

| # | exercise | 🔴 red that opens it | time | status |
|---|---|---|---|---|
| 0 | [Orientation](exercises/ex00-orientation/) · [open the page](exercises/ex00-orientation/exercise.html) | no red: machine check, a tour of Ledgerly and its landmines, the anatomy of an exercise (drills, checks, judges, reference, LESSONS), the tools, and one warm-up drill (LED-100) through the loop | 10 · 18 full | ✅ ready |
| 1 | [CLAUDE.md](exercises/ex01-claude-md/) · [open the page](exercises/ex01-claude-md/exercise.html) | check red first → LED-107 installments with no CLAUDE.md: tests green, "done", hidden check red (Haiku 0/4) → one team rule in CLAUDE.md → green (3/3). Going further: rules, directory files, the `~/.claude` trap | 20 | ✅ ready |
| 2 | [Skills](exercises/ex02-skills/) · [open the page](exercises/ex02-skills/exercise.html) | a generic PR note (wrong format, no ADRs, unverified gates); then author `ship-check`, prove it fires implicitly and stays quiet, and build a forked, read-only `adr-audit` worker | 25 | ✅ ready |
| 3 | [Hooks](exercises/ex03-hooks/) · [open the page](exercises/ex03-hooks/exercise.html) | LED-103 tampering *rate* from Ex 1 → `PreToolUse` fence (tests append-only, protected configs, `.env`), `PostToolUse` lint, `Stop` finish line with a stop rule → **0/3**; LED-132 "relax the lint" | 25 | ✅ ready |
| 4 | [MCP + Context7](exercises/ex04-mcp/) · [open the page](exercises/ex04-mcp/exercise.html) | LED-141: green tests on a deprecated FastAPI API (`on_event`) → Context7 + a rule → `lifespan`; then deprecations become failing tests; MCP cost in `/context` | 4 demo · 20 homework | ✅ ready |
| 5 | [Tests: green is not correct](exercises/ex05-tests/) · [open the page](exercises/ex05-tests/exercise.html) | LED-150 weak tests survive a hidden mutation judge (7 mutants); LED-151 contract tests from ADR-0003 kill them; LED-118 trap: skip the flaky test or fix the bug? | 25 | ✅ ready |

### 📅 Day 2: process on top of the gates (Advanced decks)

| # | exercise | idea | time | status |
|---|---|---|---|---|
| 6 | Subagents: doer ≠ judge | explorer / implementer / independent reviewer; **only the test-writer agent may edit tests** (the Ex 3 hook checks `agent_type`) | 25 | planned |
| 7 | Parallel tickets in worktrees | LED-101 + LED-112 at once; the Day 1 gates run in both | 30 | planned |
| 8 | Spec Kit capstone | LED-201 multi-currency refunds; constitution from Ex 1's rules + ADRs; `/analyze` gates `/implement`; FR-IDs ↔ tagged tests; holdout tests | 40 | planned |

## 🖱️ Cursor

Every exercise has a short **Cursor sidebar** mapping the mechanism (`AGENTS.md`,
`.cursor/rules/*.mdc`, `.cursor/hooks.json`, `.cursor/mcp.json`). The drift checker is
tool-agnostic: it grades the repo state and works with any agent. Only the transcript-based
checks need a Claude Code session file. Mechanism details differ between Cursor versions, so
check your version's docs.

## 🤝 A note on honesty

Agents are nondeterministic, and a live demo can come back green when you wanted red. Don't fake
it: show the multi-run rate you recorded before class, or the clearly labelled hand-written
reference patch. "It worked this time" is exactly the kind of evidence this workshop teaches
people not to trust.
