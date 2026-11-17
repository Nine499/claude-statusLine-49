from claude_statusline.git import (
    GitStatus,
    change_parts,
    count_change,
    git_ref,
    parse_git_status,
    sync_parts,
)


def test_parse_git_status_collects_branch_and_counts():
    status = parse_git_status(
        """\
# branch.oid 1234567890abcdef
# branch.head main
# branch.upstream origin/main
# branch.ab +2 -1
1 .M N... 100644 100644 100644 aaa bbb modified.py
1 M. N... 100644 100644 100644 aaa bbb staged.py
1 MM N... 100644 100644 100644 aaa bbb both.py
1 D. N... 100644 100644 100644 aaa bbb deleted.py
2 R. N... 100644 100644 100644 aaa bbb R100 new.py old.py
? untracked.py
u UU N... 100644 100644 100644 100644 aaa bbb ccc conflict.py
"""
    )
    assert status.head == "main"
    assert status.oid == "1234567890abcdef"
    assert status.upstream == "origin/main"
    assert status.has_ahead_behind is True
    assert status.ahead == 2
    assert status.behind == 1
    assert status.staged == 3
    assert status.modified == 2
    assert status.deleted == 1
    assert status.untracked == 1
    assert status.conflicts == 1


def test_git_ref_prefers_named_head_and_falls_back_to_oid():
    assert git_ref(GitStatus(head="feature/x")) == "feature/x"
    assert git_ref(GitStatus(head="(detached)", oid="1234567890abcdef")) == "@1234567"
    assert git_ref(GitStatus(head="(unknown)", oid="(initial)")) == "unknown"
    assert git_ref(GitStatus(head="x" * 40)) == "x" * 31 + "…"


def test_sync_parts_reports_upstream_states():
    synced = GitStatus(
        head="main", upstream="origin/main", has_ahead_behind=True, ahead=2, behind=1
    )
    assert sync_parts(synced) == ["↑2", "↓1"]
    both_zero = GitStatus(head="main", upstream="origin/main", has_ahead_behind=True)
    assert sync_parts(both_zero) == ["sync"]
    assert sync_parts(GitStatus(head="main", upstream="origin/main")) == ["no-ab"]
    assert sync_parts(GitStatus(head="main")) == ["no-up"]
    assert sync_parts(GitStatus(head="(detached)")) == []


def test_change_parts_uses_fixed_order_and_clean_fallback():
    status = GitStatus(conflicts=1, staged=2, modified=3, deleted=4, untracked=5)
    assert change_parts(status) == ["!1", "+2", "~3", "-4", "?5"]
    assert change_parts(GitStatus()) == ["clean"]


def test_count_change_ignores_malformed_lines():
    status = GitStatus()
    count_change("1 X", status)
    assert status.staged == 0
    assert status.modified == 0
    assert status.deleted == 0
