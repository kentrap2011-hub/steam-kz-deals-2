#!/usr/bin/env python3
"""PR-only negative/positive staging regressions with isolated Git fixtures."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

MODULE = Path(__file__).with_name("stage_site_optional_sections.py")
spec = importlib.util.spec_from_file_location("site_deploy_optional", MODULE)
isolation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(isolation)

VISUAL = "data/production/visual/current.json"
GOOD = {
    "production_contract": {
        "mode": "daily_precomputed_read_only_for_ui",
        "external_lookup_allowed_in_ui": False,
        "heavy_calculation_allowed_in_ui": False,
    },
    "schema_version": 5,
    "items": [{
        "id": "fixture-101", "title": "Verified paid game",
        "current_price_rub": 249, "discount_percent": 80,
    }],
    "giveaways": {"schema_version": 1, "source_contract": "CROSS-PLATFORM-GIVEAWAY-V1",
                  "state": "empty", "games": [], "accepted_offer_count_at_build": 0},
}


def command(repo, *args):
    return subprocess.check_output(list(args), cwd=repo, text=True).strip()


def write(repo, path, content):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def fake_executable(repo, name, lines):
    write(repo, "scripts/" + name, "import sys\nfrom pathlib import Path\nROOT=Path(__file__).resolve().parents[1]\n" + lines)


def make_repo(root):
    repo = root / "repo"
    repo.mkdir()
    command(repo, "git", "init", "-q", "-b", "main")
    command(repo, "git", "config", "user.name", "unit")
    command(repo, "git", "config", "user.email", "unit@example.com")
    command(repo, "git", "config", "gc.auto", "0")
    command(repo, "git", "config", "maintenance.auto", "false")
    text = json.dumps(GOOD, ensure_ascii=False, separators=(",", ":")) + "\n"
    write(repo, VISUAL, text)
    write(repo, "data/production/site/current_status.json", '{"schema_version":1}\n')
    write(repo, "web/index.html", '<html>\n<a class="statistics-entry tasks-entry" href="tasks.html">Задачи</a>\n'
          '<script src="app.js?v=deep-history-site-01"></script>\n</html>\n')
    for name in ("tasks.html", "tasks.js", "tasks.css"):
        write(repo, "web/" + name, name + "\n")
    write(repo, "web/data/current.json", text)
    fake_executable(repo, "build_site_tasks.py", """
import json
output=ROOT/"web/data/tasks.json"
if (ROOT/"flags/task_generator_crash").exists():
    raise RuntimeError("simulated task generator crash")
if (ROOT/"flags/registry.json").exists():
    registry=json.loads((ROOT/"flags/registry.json").read_text(encoding="utf-8"))
    if "recent_completion" not in registry:
        raise KeyError("recent_completion")
if "--output" in sys.argv:
    output=ROOT/sys.argv[sys.argv.index("--output")+1]
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text('{"schema_version":1,"contract":"SITE-DIRECTOR-TASKS-PUBLIC-V1"}')
if "--validate-current" in sys.argv and (ROOT/"flags/task_invalid").exists():
    raise SystemExit("stale task output")
""")
    fake_executable(repo, "build_site_status.py", """
if (ROOT/"flags/status_invalid").exists():
    raise SystemExit("invalid status source bindings")
if not (ROOT/"data/production/site/current_status.json").exists():
    raise SystemExit("missing status artifact")
""")
    fake_executable(repo, "validate_giveaway_visual_payload.py", """
if (ROOT/"flags/giveaway_invalid").exists():
    raise SystemExit("invalid optional giveaway offer")
""")
    command(repo, "git", "add", ".")
    command(repo, "git", "commit", "-qm", "source fixture")
    return repo


def flag(repo, key):
    write(repo, "flags/" + key, "1")


def expect_rejected(fun, *matches):
    try:
        fun()
    except (ValueError, json.JSONDecodeError) as exc:
        message = str(exc)
        assert any(fragment in message for fragment in matches), message
    else:
        raise AssertionError("mandatory rejection silently bypassed: " + repr(matches))


def test_valid_paid_publication(repo):
    expected = (repo / "web/data/current.json").read_bytes()
    out = isolation.stage(repo, "general")
    assert out["sections"]["tasks"]["disposition"] == "fresh"
    assert out["sections"]["status"]["disposition"] == "fresh"
    assert out["sections"]["giveaways"]["disposition"] == "fresh"
    assert out["source_visual_sha256"] == out["staged_visual_sha256"]
    assert out["published_visual_sha256"] is None
    assert (repo / "web/data/current.json").read_bytes() == expected
    assert 'href="tasks.html"' in (repo / "web/index.html").read_text()
    assert json.loads((repo / "web/data/publication-disposition.json").read_text()) == out


def test_registry_missing_recent_completion(repo):
    write(repo, "flags/registry.json", '{"id":"site-tasks"}\n')
    out = isolation.stage(repo, "general")
    assert out["sections"]["tasks"]["disposition"] == "omitted"
    assert out["sections"]["status"]["disposition"] == "fresh"
    assert not (repo / "web/tasks.html").exists()
    assert 'href="tasks.html"' not in (repo / "web/index.html").read_text()
    assert not (repo / "web/data/tasks.json").exists()


def test_bad_registry_tests_and_generator_crash(repo):
    flag(repo, "task_invalid")
    out = isolation.stage(repo, "general")
    assert out["sections"]["tasks"]["disposition"] == "omitted"
    assert out["sections"]["giveaways"]["disposition"] == "fresh"


def test_crashed_generator(repo):
    flag(repo, "task_generator_crash")
    out = isolation.stage(repo, "general")
    assert out["sections"]["tasks"]["disposition"] == "omitted"
    assert "generator" in out["sections"]["tasks"]["reason"]


def test_optional_status_and_status_only_gate(repo):
    flag(repo, "status_invalid")
    out = isolation.stage(repo, "general")
    assert out["sections"]["status"]["disposition"] == "omitted"
    assert not (repo / "web/data/status.json").exists()
    assert out["sections"]["tasks"]["disposition"] == "fresh"


def test_status_only_fails_closed(repo):
    flag(repo, "status_invalid")
    expect_rejected(lambda: isolation.stage(repo, "status_only"), "Status-only")


def test_optional_giveaway_isolation(repo):
    flag(repo, "giveaway_invalid")
    original = (repo / "web/data/current.json").read_bytes()
    out = isolation.stage(repo, "commercial_only")
    assert out["sections"]["giveaways"]["disposition"] == "omitted"
    html = (repo / "web/index.html").read_text()
    assert "window.SITE_GIVEAWAY_ENABLED=false;" in html
    assert (repo / "web/data/current.json").read_bytes() == original
    assert out["sections"]["tasks"]["disposition"] == "fresh"


def test_giveaway_only_fails_closed(repo):
    flag(repo, "giveaway_invalid")
    expect_rejected(lambda: isolation.stage(repo, "giveaway_only"), "Giveaway-only")


def test_paid_corruption_rejected(repo):
    path = repo / "web/data/current.json"
    value = json.loads(path.read_text())
    value["items"][0]["current_price_rub"] = 1
    path.write_text(json.dumps(value), encoding="utf-8")
    expect_rejected(lambda: isolation.stage(repo, "general"), "Staged paid bytes differ")


def test_missing_canonical_source_rejected(repo):
    (repo / VISUAL).unlink()
    expect_rejected(lambda: isolation.stage(repo, "general"), "Missing canonical")


def test_noncanonical_uncommitted_material_rejected(repo):
    path = repo / VISUAL
    value = json.loads(path.read_text())
    value["items"][0]["discount_percent"] = 99
    content = json.dumps(value) + "\n"
    path.write_text(content, encoding="utf-8")
    (repo / "web/data/current.json").write_text(content, encoding="utf-8")
    expect_rejected(lambda: isolation.stage(repo, "general"), "Git material SHA")


def test_invalid_core_scope_and_safety(repo):
    source = repo / VISUAL
    obj = json.loads(source.read_text())
    obj["production_contract"]["external_lookup_allowed_in_ui"] = True
    content = json.dumps(obj)
    source.write_text(content)
    (repo / "web/data/current.json").write_text(content)
    expect_rejected(lambda: isolation.stage(repo, "general"), "recalculation")
    expect_rejected(lambda: isolation.stage(repo, "wrong_scope"), "Invalid deploy scope")


def test_omission_must_not_leave_broken_navigation(repo):
    flag(repo, "task_invalid")
    path = repo / "web/index.html"
    path.write_text(path.read_text().replace('href="tasks.html"', 'href="tasks-elsewhere.html"'))
    expect_rejected(lambda: isolation.stage(repo, "general"), "Cannot omit task section safely")


def main():
    tests = [obj for key, obj in globals().items() if key.startswith("test_") and callable(obj)]
    for fn in tests:
        with tempfile.TemporaryDirectory(prefix="site-deploy-pr-") as tmp:
            fn(make_repo(Path(tmp)))
        print("PASS", fn.__name__)
    print("SITE_DEPLOY_OPTIONAL_ISOLATION_TESTS=PASS", len(tests))


if __name__ == "__main__":
    main()
