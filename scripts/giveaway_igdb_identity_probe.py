from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import duration_enrichment as igdb

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT = ROOT / "data" / "production" / "giveaways" / "v1" / "current.json"
DEFAULT_LIMIT = 10
SUPPORTED_PROVIDERS = {"epic", "gog"}


class ProbeInputError(ValueError):
    pass


def load_snapshot(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ProbeInputError("giveaway snapshot must be a JSON object")
    if data.get("contract") != "CROSS-PLATFORM-GIVEAWAY-V1":
        raise ProbeInputError("unexpected giveaway contract")
    if not isinstance(data.get("games"), list):
        raise ProbeInputError("giveaway games must be a list")
    return data


def _epic_tokens(source_product_id: str) -> list[dict[str, str]]:
    # giveaway_epic.py defines the exact persisted product identity as
    # "<namespace>:<offer_id>". Splitting that adapter-owned format does not
    # assert which (if any) token IGDB uses as External Game uid.
    if source_product_id.count(":") != 1:
        raise ProbeInputError("Epic source_product_id does not match the canonical adapter format")
    namespace, offer_id = (part.strip() for part in source_product_id.split(":", 1))
    if not namespace or not offer_id:
        raise ProbeInputError("Epic source_product_id contains an empty identity component")
    return [
        {"kind": "epic_source_product_id", "uid": source_product_id},
        {"kind": "epic_namespace", "uid": namespace},
        {"kind": "epic_offer_id", "uid": offer_id},
    ]


def provider_uid_candidates(source_id: str, source_product_id: str) -> list[dict[str, str]]:
    source_id = str(source_id or "").strip().casefold()
    source_product_id = str(source_product_id or "").strip()
    if source_id not in SUPPORTED_PROVIDERS:
        return []
    if not source_product_id:
        raise ProbeInputError(f"{source_id} offer is missing exact source_product_id")
    if source_id == "epic":
        return _epic_tokens(source_product_id)
    return [{"kind": "gog_catalog_product_id", "uid": source_product_id}]


def exact_provider_identities(snapshot: dict[str, Any], limit: int = DEFAULT_LIMIT) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if limit <= 0:
        raise ProbeInputError("probe limit must be positive")
    all_rows: list[dict[str, Any]] = []
    for game in snapshot.get("games") or []:
        if not isinstance(game, dict):
            raise ProbeInputError("giveaway game row must be an object")
        for offer in game.get("offers") or []:
            if not isinstance(offer, dict):
                raise ProbeInputError("giveaway offer row must be an object")
            source_id = str(offer.get("source_id") or "").strip().casefold()
            if source_id not in SUPPORTED_PROVIDERS:
                continue
            source_product_id = str(offer.get("source_product_id") or "").strip()
            tokens = provider_uid_candidates(source_id, source_product_id)
            all_rows.append({
                # canonical_game_key is only a correlation key for the report. It
                # is never sent to IGDB and never authorizes a semantic binding.
                "giveaway_game_key": game.get("canonical_game_key"),
                "source_id": source_id,
                "source_product_id": source_product_id,
                "uid_candidates": tokens,
            })
    selected = all_rows[:limit]
    return selected, {
        "eligible_offer_count": len(all_rows),
        "probed_offer_count": len(selected),
        "truncated": len(all_rows) > len(selected),
        "limit": limit,
    }


def unique_candidate_uids(identities: list[dict[str, Any]]) -> list[str]:
    values = {
        str(token.get("uid"))
        for identity in identities
        for token in (identity.get("uid_candidates") or [])
        if str(token.get("uid") or "").strip()
    }
    return sorted(values)


def build_uid_probe_query(uids: list[str]) -> str:
    clean = sorted({str(value).strip() for value in uids if str(value).strip()})
    if not clean:
        raise ProbeInputError("external game probe requires at least one exact uid candidate")
    quoted = ",".join(json.dumps(value) for value in clean)
    return (
        "fields game,uid,external_game_source; "
        f"where uid = ({quoted}); limit 500;"
    )


def build_steam_backmap_query(game_ids: list[int], steam_source_id: int) -> str:
    clean = sorted({value for value in game_ids if isinstance(value, int) and not isinstance(value, bool) and value > 0})
    if not clean:
        raise ProbeInputError("Steam back-map requires at least one positive IGDB game id")
    ids = ",".join(str(value) for value in clean)
    return (
        "fields game,uid,external_game_source; "
        f"where external_game_source = {int(steam_source_id)} & game = ({ids}); limit 500;"
    )


def source_names_by_id(rows: list[dict[str, Any]]) -> dict[int, str]:
    result: dict[int, str] = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        source_id = row.get("id")
        name = str(row.get("name") or "").strip()
        if not isinstance(source_id, int) or isinstance(source_id, bool) or source_id <= 0 or not name:
            continue
        previous = result.get(source_id)
        if previous is not None and previous != name:
            raise ProbeInputError(f"IGDB External Game Source id {source_id} has conflicting names")
        result[source_id] = name
    return result


def observed_provider_matches(
    identities: list[dict[str, Any]],
    external_rows: list[dict[str, Any]],
    source_names: dict[int, str],
) -> list[dict[str, Any]]:
    rows_by_uid: dict[str, list[dict[str, Any]]] = {}
    for row in external_rows or []:
        if not isinstance(row, dict):
            continue
        uid = str(row.get("uid") or "").strip()
        if uid:
            rows_by_uid.setdefault(uid, []).append(row)

    output: list[dict[str, Any]] = []
    for identity in identities:
        matches: list[dict[str, Any]] = []
        for token in identity.get("uid_candidates") or []:
            uid = str(token.get("uid") or "").strip()
            for row in rows_by_uid.get(uid, []):
                source_id = row.get("external_game_source")
                game_id = row.get("game")
                if not isinstance(source_id, int) or isinstance(source_id, bool) or source_id <= 0:
                    continue
                if not isinstance(game_id, int) or isinstance(game_id, bool) or game_id <= 0:
                    continue
                matches.append({
                    "token_kind": token.get("kind"),
                    "uid": uid,
                    "external_game_source_id": source_id,
                    "external_game_source_name": source_names.get(source_id),
                    "igdb_game_id": game_id,
                })
        matches.sort(key=lambda row: (str(row.get("token_kind")), str(row.get("uid")), int(row.get("external_game_source_id") or 0), int(row.get("igdb_game_id") or 0)))
        output.append({
            **identity,
            "probe_status": "candidate_rows_observed" if matches else "no_candidate_rows",
            "observed_matches": matches,
            # Deliberately false until provider source + uid semantics are
            # accepted against live IGDB and the Steam reverse mapping is exact.
            "production_binding_authorized": False,
        })
    return output


def classify_steam_backmap(game_ids: list[int], rows: list[dict[str, Any]], steam_source_id: int) -> dict[int, dict[str, Any]]:
    requested = set(game_ids)
    appids_by_game = {game_id: set() for game_id in game_ids}
    invalid = set()
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        game_id = row.get("game")
        if game_id not in requested:
            continue
        if row.get("external_game_source") != steam_source_id:
            invalid.add(game_id)
            continue
        appid = igdb.canonical_appid(row.get("uid"))
        if appid is None:
            invalid.add(game_id)
            continue
        appids_by_game[game_id].add(appid)

    result: dict[int, dict[str, Any]] = {}
    for game_id in game_ids:
        appids = sorted(appids_by_game[game_id], key=int)
        if len(appids) == 1 and game_id not in invalid:
            result[game_id] = {"status": "mapped", "steam_appid": appids[0]}
        elif len(appids) > 1:
            result[game_id] = {"status": "steam_mapping_ambiguous", "steam_appids": appids}
        elif game_id in invalid:
            result[game_id] = {"status": "invalid_values"}
        else:
            result[game_id] = {"status": "steam_mapping_missing"}
    return result


def run_probe(snapshot: dict[str, Any], client_id: str, client_secret: str, limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    identities, scope = exact_provider_identities(snapshot, limit=limit)
    result: dict[str, Any] = {
        "probe_contract": "GIVEAWAY-IGDB-IDENTITY-PROBE-V1",
        "mode": "read_only_probe",
        "production_binding_authorized": False,
        "scope": scope,
        "identities": identities,
    }
    if not identities:
        result["status"] = "no_epic_or_gog_offers_in_scope"
        return result

    client = igdb.IgdbClient(client_id, client_secret)
    client.authenticate()
    source_rows = client.api_post("external_game_sources", igdb.build_external_game_sources_query())
    steam_source_id = igdb.resolve_steam_source_id(source_rows)
    source_names = source_names_by_id(source_rows)

    uid_rows = client.api_post("external_games", build_uid_probe_query(unique_candidate_uids(identities)))
    observed = observed_provider_matches(identities, uid_rows, source_names)
    game_ids = sorted({
        int(match["igdb_game_id"])
        for identity in observed
        for match in identity.get("observed_matches") or []
        if isinstance(match.get("igdb_game_id"), int) and not isinstance(match.get("igdb_game_id"), bool)
    })

    steam_backmap: dict[int, dict[str, Any]] = {}
    if game_ids:
        steam_rows = client.api_post("external_games", build_steam_backmap_query(game_ids, steam_source_id))
        steam_backmap = classify_steam_backmap(game_ids, steam_rows, steam_source_id)

    for identity in observed:
        for match in identity.get("observed_matches") or []:
            match["steam_backmap"] = steam_backmap.get(match["igdb_game_id"], {"status": "not_queried"})

    result.update({
        "status": "probe_complete",
        "steam_external_game_source_id": steam_source_id,
        "identities": observed,
        "acceptance_rule": (
            "Do not persist a binding from this probe alone. Accept a provider source/uid semantic only after the bounded live "
            "sample proves an exact provider External Game row and an exact, unambiguous Steam appid reverse mapping."
        ),
    })
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only IGDB identity probe for Epic/GOG giveaway provider IDs")
    parser.add_argument("--snapshot", default=str(DEFAULT_SNAPSHOT))
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client_id = os.environ.get(igdb.CLIENT_ID_ENV, "").strip()
    client_secret = os.environ.get(igdb.CLIENT_SECRET_ENV, "").strip()
    if not client_id or not client_secret:
        print(
            "GIVEAWAY_IGDB_PROVISIONING=missing_credentials "
            f"expected_secrets={igdb.CLIENT_ID_ENV},{igdb.CLIENT_SECRET_ENV}"
        )
        return 2

    try:
        snapshot = load_snapshot(args.snapshot)
        result = run_probe(snapshot, client_id, client_secret, limit=args.limit)
    except igdb.AuthError as exc:
        print(f"GIVEAWAY_IGDB_AUTH=FAIL reason={exc}")
        return 3
    except igdb.TransportError as exc:
        print(f"GIVEAWAY_IGDB_TRANSPORT=FAIL reason={exc}")
        return 4
    except (ProbeInputError, ValueError, json.JSONDecodeError, OSError) as exc:
        print(f"GIVEAWAY_IGDB_PROBE=FAIL reason={exc}")
        return 5

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
