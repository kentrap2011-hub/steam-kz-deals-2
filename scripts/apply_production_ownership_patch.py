from pathlib import Path


def replace_once(path, old, new):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Expected snippet not found in {path}: {old[:160]!r}')
    if text.count(old) != 1:
        raise SystemExit(f'Expected exactly one occurrence in {path}, found {text.count(old)}')
    p.write_text(text.replace(old, new), encoding='utf-8')


helper = '''import shutil\nfrom pathlib import Path\n\n\nOWNED_DIRECTORIES = (\"shortlist\",)\nOWNED_FILES = (\n    \"manifest.json\",\n    \"freebies.tsv\",\n    \"freebies_index.json\",\n)\n\n\ndef reset_steam_collector_outputs(production_root):\n    \"\"\"Remove only artifacts owned by the Steam catalog collector.\n\n    Downstream artifacts such as mailing/, pre_ai/ and daily_ready/ must survive\n    a commercial refresh until their own producers replace them.\n    \"\"\"\n    root = Path(production_root)\n    root.mkdir(parents=True, exist_ok=True)\n\n    for relative in OWNED_DIRECTORIES:\n        target = root / relative\n        if target.is_symlink() or target.is_file():\n            target.unlink()\n        elif target.exists():\n            shutil.rmtree(target)\n\n    for relative in OWNED_FILES:\n        target = root / relative\n        if target.exists() or target.is_symlink():\n            target.unlink()\n'''
Path('scripts/production_output_ownership.py').write_text(helper, encoding='utf-8')

test = '''from pathlib import Path\nfrom tempfile import TemporaryDirectory\n\nfrom production_output_ownership import reset_steam_collector_outputs\n\n\ndef write(path, text=\"sentinel\"):\n    path.parent.mkdir(parents=True, exist_ok=True)\n    path.write_text(text, encoding=\"utf-8\")\n\n\ndef main():\n    with TemporaryDirectory() as temporary:\n        root = Path(temporary) / \"data\" / \"production\"\n\n        # Collector-owned stale outputs must disappear.\n        write(root / \"shortlist\" / \"chunk_001.tsv\", \"old chunk\")\n        write(root / \"shortlist\" / \"chunk_999.tsv\", \"stale chunk\")\n        write(root / \"manifest.json\", \"old manifest\")\n        write(root / \"freebies.tsv\", \"old freebies\")\n        write(root / \"freebies_index.json\", \"old freebies index\")\n\n        # Downstream and unrelated production artifacts must survive untouched.\n        protected = [\n            root / \"mailing\" / \"index.json\",\n            root / \"pre_ai\" / \"chatgpt_payload.json\",\n            root / \"daily_ready\" / \"latest.json\",\n            root / \"other_producer\" / \"sentinel.txt\",\n        ]\n        for path in protected:\n            write(path)\n\n        reset_steam_collector_outputs(root)\n\n        assert not (root / \"shortlist\").exists(), \"stale shortlist survived reset\"\n        assert not (root / \"manifest.json\").exists(), \"old manifest survived reset\"\n        assert not (root / \"freebies.tsv\").exists(), \"old freebies survived reset\"\n        assert not (root / \"freebies_index.json\").exists(), \"old freebies index survived reset\"\n\n        for path in protected:\n            assert path.read_text(encoding=\"utf-8\") == \"sentinel\", f\"foreign artifact changed: {path}\"\n\n    print(\"Production output ownership regression test passed\")\n\n\nif __name__ == \"__main__\":\n    main()\n'''
Path('scripts/test_production_output_ownership.py').write_text(test, encoding='utf-8')

# Collector no longer owns the whole data/production tree.
replace_once(
    'scripts/steam_production.py',
    'import shutil\n',
    '',
)
replace_once(
    'scripts/steam_production.py',
    'from bs4 import BeautifulSoup\n',
    'from bs4 import BeautifulSoup\n\nfrom production_output_ownership import reset_steam_collector_outputs\n',
)
replace_once(
    'scripts/steam_production.py',
    '''if OUT.exists():\n    shutil.rmtree(OUT)\n\nSHORT.mkdir(\n''',
    '''# Replace only artifacts owned by this collector.  Downstream production\n# state (mailing/pre_ai/daily_ready) remains available until its own producer\n# atomically replaces it.\nreset_steam_collector_outputs(OUT)\n\nSHORT.mkdir(\n''',
)

workflow = Path('.github/workflows/steam-test.yml')
text = workflow.read_text(encoding='utf-8')
text = text.replace(
    '      - "scripts/steam_production_cached.py"\n',
    '      - "scripts/steam_production_cached.py"\n      - "scripts/production_output_ownership.py"\n      - "scripts/test_production_output_ownership.py"\n',
    1,
)
text = text.replace(
    '''      - name: Collect full Steam KZ catalog and build production shortlist\n        run: python scripts/steam_production_cached.py\n\n      - name: Commit production feed and review cache\n''',
    '''      - name: Regression test production output ownership\n        run: python scripts/test_production_output_ownership.py\n\n      - name: Collect full Steam KZ catalog and build production shortlist\n        run: python scripts/steam_production_cached.py\n\n      - name: Verify collector touched only owned production paths\n        shell: bash\n        run: |\n          set -euo pipefail\n          allowed='^data/production/(manifest\\.json|freebies\\.tsv|freebies_index\\.json|shortlist/)'\n\n          foreign_tracked=\"$(git diff --name-only -- data/production | grep -Ev \"$allowed\" || true)\"\n          foreign_untracked=\"$(git ls-files --others --exclude-standard -- data/production | grep -Ev \"$allowed\" || true)\"\n\n          if [[ -n \"$foreign_tracked\" || -n \"$foreign_untracked\" ]]; then\n            echo \"Steam collector modified production artifacts owned by another stage.\"\n            printf '%s\\n' \"$foreign_tracked\" \"$foreign_untracked\"\n            exit 1\n          fi\n\n      - name: Commit production feed and review cache\n''',
    1,
)
text = text.replace(
    '''          git add -A data/production/\n          git add data/cache/steam_review_http_cache.json\n''',
    '''          # Stage only the Steam collector's own outputs.  Never stage\n          # downstream mailing/pre_ai/daily_ready artifacts from this workflow.\n          git add -A -- \\\n            data/production/shortlist \\\n            data/production/manifest.json \\\n            data/production/freebies.tsv \\\n            data/production/freebies_index.json\n          git add data/cache/steam_review_http_cache.json\n''',
    1,
)
workflow.write_text(text, encoding='utf-8')

rules_path = Path('PROJECT_RULES.md')
rules = rules_path.read_text(encoding='utf-8')
anchor = '## Роль ChatGPT\n'
section = '''## Владение production-артефактами\n\nРазные этапы пайплайна не должны удалять или перезаписывать артефакты друг друга. Основной Steam-сборщик владеет только `data/production/manifest.json`, `data/production/shortlist/`, `data/production/freebies.tsv` и `data/production/freebies_index.json`. Он не должен удалять или коммитить `mailing/`, `pre_ai/`, `daily_ready/` и другие downstream-артефакты.\n\nWorkflow Steam-сборщика должен коммитить только принадлежащие ему production-пути и падать с ошибкой, если сборщик неожиданно изменил чужой production-артефакт. Это постоянный инвариант надёжности, защищающий ночную цепочку от modify/delete-конфликтов и временного исчезновения подготовленных данных.\n\n'''
if section not in rules:
    if anchor not in rules:
        raise SystemExit('PROJECT_RULES anchor not found')
    rules = rules.replace(anchor, section + anchor, 1)
    rules_path.write_text(rules, encoding='utf-8')

print('Production ownership patch applied')
