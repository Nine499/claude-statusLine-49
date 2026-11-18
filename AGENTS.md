# AGENTS.md

## What this is

A two-line status line renderer for Claude Code. It reads Claude Code's status JSON from stdin and writes exactly two lines to stdout: model/context/cache, then directory/git/code churn.

It is not a TUI, a daemon, or a library. It has no CLI flags, reads no config files, makes no network requests, and has zero runtime third-party dependencies.

## Stack & Run

- Python `>=3.11` (see `pyproject.toml` `requires-python`).
- Build backend: hatchling. Source layout: `src/`. Console script `claude-statusLine-49` → `claude_statusline.cli:main`.
- Dependency management: uv; `uv.lock` is committed. Dev dependency: `pytest>=9.2.0` (dependency group `dev`).
- Lint/format: ruff, `line-length = 88`, `target-version = "py311"`.

```bash
uv sync                              # install project + dev deps into .venv
uv run pytest                        # run tests (testpaths = tests)
ruff check src tests                 # lint
ruff format --check src tests        # format check
echo '{}' | uv run python -m claude_statusline   # manual render
uv tool install --force .            # install/refresh the global command (user action)
```

## Layout

```
src/claude_statusline/
  cli.py             entry point: read stdin JSON, render, print, return 0
  model_line.py      line 1: model id, effort level, context window, cache hit
  workspace_line.py  line 2: current dir basename, git segment, code churn
  git.py             run `git status --porcelain=v2` and parse it
  values.py          tolerant getters (as_mapping, as_int) and text helpers
  __main__.py        `python -m claude_statusline`
tests/               one test module per source module
legacy/              pre-rewrite 3-line single-file version; not built or tested
```

## Conventions

- One rendering concern per module. `model_line()` / `workspace_line()` compose segments; `join_segments()` joins non-empty ones with `" | "`.
- Input is untrusted. All JSON access goes through `values.as_mapping` / `as_int`; never let a missing or wrongly-typed field raise.
- Output contract: stdout contains the two rendered lines and nothing else; no logging, no stderr output, exit code always 0 (`main()` returns 0).
- Function names are specific, single-purpose. Private-ish helpers stay in their module. No abstraction until a third repetition.
- Type hints on functions. `GitStatus` uses `@dataclass(slots=True)`.
- Tests use plain pytest functions; git access is isolated in `git.py` and stubbed with `monkeypatch` in `workspace_line` tests.
- No runtime third-party dependencies may be added.
- Version is time-based (`YYYYMMDD.HHMM.SSMS`) in `pyproject.toml` `[project].version`. After any change, per root `CLAUDE.md`: generate a new version with the `time-version-49` skill, write it to `pyproject.toml`, run `uv sync`, and append a row to the update log in `CLAUDE.md`. Never hand-write the version.
- Project rules in `CLAUDE.md` override this file where they are more specific.

## Tasks

**Add or change a segment on line 1 / line 2**
Edit `model_line.py` or `workspace_line.py`, add a `*_segment()` returning `""` when there is nothing to show, pass it to `join_segments`, and cover it in the matching `tests/test_*.py`. Then run `uv run pytest`, `ruff check src tests`, `ruff format --check src tests`.

**Change git parsing**
Edit `git.py`. The parser consumes porcelain v2 `--branch --untracked-files=normal` output: `# branch.head|oid|upstream|ab`, `u ` conflict lines, `? ` untracked lines, and `1 `/`2 ` changed lines whose `xy` field is index/worktree status. Extend `GitStatus` and `parse_git_status` together, and update `tests/test_git.py`.

**Change input tolerance**
Edit `values.py` and extend `tests/test_values.py`. Degradation must stay silent: bad JSON or a non-object payload becomes `{}` in `cli.read_input()`.

**Change the installed command**
Update `[project.scripts]` in `pyproject.toml`, then tell the user to run `uv tool install --force .`; do not run global installs yourself.

## Traps

- **Output contract:** exactly two lines on stdout (`render()` drops empty lines defensively, but line 1 always has model/context/cache and line 2 always has `code:`), nothing on stderr, exit code 0. Do not add debug prints — they break the status line.
- **git timeout is 0.15 s** (`GIT_TIMEOUT_SECONDS`). A slow repo, missing `git`, a non-repo directory, or a nonzero exit silently yields an empty git segment. Do not raise the timeout without measuring status line refresh cost.
- **`prompt_cache.hit_ratio` has two accepted formats.** `ratio <= 1` is treated as a fraction (multiplied by 100, so `1` means 100%); larger numbers are treated as an already-percent value. Non-numeric values render `0%`.
- **Token counts truncate, not round:** `1_500` → `1K`, `2_500_000` → `2M`, values under 1000 print as-is.
- **Branch names longer than 32 chars** are cut to 31 chars plus `…` via `shorten`.
- **`head` values `(detached)` and `(unknown)` are not branch names.** Render `@<first 7 oid chars>` when possible, else `unknown`.
- **`count_change` only reads porcelain v2 `1 ` / `2 ` lines.** `D` in either status column increments `deleted` and excludes that column from staged/modified counts; malformed short lines are ignored.
- **`legacy/claude_statusLine.py` is reference only.** It is the old 3-line version with TTFT/TPOT/TPS and transcript tail-reading. Do not import, test, or "fix" it unless explicitly asked.
- **Do not run `uv tool install` or other global installs during routine development** (repo `CLAUDE.md` forbids it); ask the user to run it.
- **Do not add runtime dependencies.** If a new dependency seems necessary, stop and ask; the zero-dependency constraint is intentional.
- **README.md is user-facing Chinese; this file is agent-facing English.** Keep them separate.

## See also

- `CLAUDE.md` — project-specific rules: version workflow, uv/ruff commands, status line protocol constraints.
- `README.md` — user-facing setup, output fields, FAQ.
