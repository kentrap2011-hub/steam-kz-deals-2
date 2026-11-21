"""Offline no-DLC preview from the pinned complete 2026-11-09 Steam KZ snapshot.

Uses only existing checked-in GitHub artifacts. No HTTP, Steam requests,
collector execution, cache modification, or production writes.
This is a functional safety test, not a live cutover or new scope contract.
"""
import json
from pathlib import Path

import build_pre_ai_family_graph as family

ROOT = Path(__file__).resolve().parents[1]
STAMP = "2026-11-09T11:20:25.250256+00:00"


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read_rows(index_path):
    index = read_json(index_path)
    columns = index["columns"]
    assert len(columns) == len(set(columns))
    result = []
    for n in range(1, index["chunk_count"] + 1):
        path = ROOT / index["chunk_pattern"].replace("NNN", f"{n:03d}")
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            cells = line.split("\t")
            assert len(cells) == len(columns), (path, cells)
            result.append(dict(zip(columns, cells)))
    assert len(result) == index["item_count"], index_path
    assert len({r["key"] for r in result}) == len(result)
    return index, result


def main():
    manifest = read_json("data/production/manifest.json")
    source_index, source_rows = read_rows("data/production/shortlist/index.json")
    mailing_index, mailing_rows = read_rows("data/production/mailing/index.json")
    assert manifest["complete"] is True and manifest["source_status"] == "complete"
    assert manifest["updated_at_utc"] == STAMP
    assert source_index["source_updated_at_utc"] == STAMP
    assert mailing_index["source_updated_at_utc"] == STAMP
    assert manifest["source_scope_contract"] == source_index["source_scope_contract"]
    assert len(source_rows) == len(mailing_rows) == 907
    assert len({r["key"] for r in source_rows}) == 907

    # Re-run the EXACT source -> mailing column projection from the existing
    # build-mailing-feed.yml. This checks integrity of today's reusable data.
    expected_cols = [name for name in source_index["columns"]
                     if name not in {"review_positive", "review_count"}]
    assert expected_cols == mailing_index["columns"]
    projected = [
        "\t".join(r[name] for name in expected_cols)
        for r in source_rows
    ]
    actual = [
        "\t".join(r[name] for name in mailing_index["columns"])
        for r in mailing_rows
    ]
    assert projected == actual, "Today's source/mailing content projection drifted"

    def is_targeted_dlc(row):
        return "verified_relevant_dlc" in row["reasons"].split("|")

    excluded = [r for r in source_rows if is_targeted_dlc(r)]
    retained = [r for r in source_rows if not is_targeted_dlc(r)]
    retained_keys = {r["key"] for r in retained}
    removed_keys = {r["key"] for r in excluded}
    assert len(excluded) == len(removed_keys) == 528
    assert len(retained) == len(retained_keys) == 379
    assert not (retained_keys & removed_keys)
    assert len([r for r in retained if r["key"].startswith("App_")]) == 365
    assert len([r for r in retained if r["key"].startswith("Sub_")]) == 14
    assert all(r["key"].startswith("App_") for r in excluded)
    assert manifest["filtering_funnel"]["dlc_admitted_after_price_discount"] == 528
    assert manifest["filtering_funnel"]["bundle_offers_admitted"] == 14

    # Every retained row, including KZT price/discount, survives unchanged.
    source_by_key = {r["key"]: r for r in source_rows}
    mailing_by_key = {r["key"]: r for r in mailing_rows}
    mail_retained = [r for r in mailing_rows if not is_targeted_dlc(r)]
    assert {r["key"] for r in mail_retained} == retained_keys
    for row in retained:
        assert row == source_by_key[row["key"]]
        mail_row = mailing_by_key[row["key"]]
        assert all(mail_row[field] == row[field]
                   for field in mailing_index["columns"])
        assert int(row["discount_percent"]) >= 50
        assert 0 < float(row["final_kzt"]) <= 4500

    # Simulate the existing prepared mailing *in memory*, rather than
    # modifying any canonical chunks or invoking any GitHub workflow.
    simulated_mailing_chunks = [
        mail_retained[i:i + 150] for i in range(0, len(mail_retained), 150)
    ]
    assert len(simulated_mailing_chunks) == 3
    assert [len(chunk) for chunk in simulated_mailing_chunks] == [150, 150, 79]

    metadata = read_json("data/production/pre_ai/content_metadata.json")
    rules_doc = read_json("data/production/pre_ai/content_rules.json")
    store_doc = read_json("data/production/pre_ai/store_snapshot.json")
    package_doc = read_json("data/production/pre_ai/fixed_package_options.json")
    contract = read_json("config/offer_family_contract.json")
    for obj in (metadata, rules_doc):
        assert obj["status"] == "complete"
        assert obj["source_updated_at_utc"] == STAMP
    assert store_doc["status"] == "complete"
    assert store_doc["discovery_source_updated_at_utc"] == STAMP
    assert store_doc["classification_complete"] is True
    assert package_doc["source_mailing_updated_at_utc"] == STAMP
    assert metadata["entry_count"] == 907
    assert rules_doc["rule_count"] == 907
    assert store_doc["classified_source_candidate_count"] == 907

    # Run the real production family resolver on a scratch-scoped subset of
    # actual stored metadata, rule decisions and price snapshots.
    feed = family.load_feed(mailing_index)
    assert set(feed) == {r["key"] for r in mailing_rows}
    filtered_feed = {k: v for k, v in feed.items() if k in retained_keys}
    filtered_meta = {k: v for k, v in metadata["entries"].items()
                     if k in retained_keys}
    filtered_rules = {k: v for k, v in rules_doc["rules"].items()
                      if k in retained_keys}
    filtered_store = {k: v for k, v in store_doc["entries"].items()
                      if k in retained_keys}
    assert set(filtered_feed) == set(filtered_meta) == set(filtered_rules) == retained_keys
    assert set(filtered_store) <= retained_keys

    allowed = {
        key for key, rule in filtered_rules.items()
        if key in filtered_store
        and rule.get("mechanical_action") in
        {"keep_for_ai", "keep_for_ai_then_resolve_condition"}
    }
    resolved = family.resolve(
        allowed, filtered_feed, filtered_store, filtered_meta,
        filtered_rules, contract
    )
    assigned = [key for fam in resolved for key in fam["all_member_keys"]]
    assert len(assigned) == len(set(assigned))
    assert set(assigned) == allowed
    assert all(not fam["addon_keys"] for fam in resolved)
    assert all(fam["primary_key"] in allowed for fam in resolved)
    assert all(fam["taste_subject_key"] in allowed for fam in resolved)
    assert all(fam["family_type"] != "external_base_addon" for fam in resolved)
    allowed_packages = {k for k in allowed if k.startswith("Sub_")}
    assert allowed_packages <= set(assigned)
    assert len([k for k in retained_keys if k.startswith("Sub_")]) == 14

    # The independent purchase-package source remains available and is
    # NOT replaced by the obsolete "find DLC from eligible parent" traversal.
    assert package_doc["status"] == "complete"
    assert package_doc["package_content_source_does_not_imply_member_taste_fit"] is True
    assert len(package_doc["packages"]) >= 14

    # No network was used. Existing Deep/Dossier results and all 907-key
    # pre-AI docs remain untouched, so production must rebuild its current
    # scope bindings before publishing a no-DLC catalogue.
    print(
        "NO_DLC_SAVED_SNAPSHOT_PASS",
        "source=907", "source_dlc_excluded=528", "games=365",
        "packages=14", "retained=379",
        "simulated_mailing_chunks=3",
        f"store_active_retained={len(filtered_store)}",
        f"family_allowed={len(allowed)}",
        f"family_count={len(resolved)}",
        f"allowed_packages={len(allowed_packages)}",
        "source_mailing_projection=exact",
        "retained_price_discount=unchanged",
        "family_assignment=complete",
        "network=0", "production_writes=0",
        "downstream_rebinding_required=true",
    )


if __name__ == "__main__":
    main()
