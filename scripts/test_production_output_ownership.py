from pathlib import Path
from tempfile import TemporaryDirectory

from production_output_ownership import reset_steam_collector_outputs


def write(path, text="sentinel"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    with TemporaryDirectory() as temporary:
        root = Path(temporary) / "data" / "production"

        # Collector-owned stale outputs must disappear.
        write(root / "shortlist" / "chunk_001.tsv", "old chunk")
        write(root / "shortlist" / "chunk_999.tsv", "stale chunk")
        write(root / "manifest.json", "old manifest")
        write(root / "freebies.tsv", "old freebies")
        write(root / "freebies_index.json", "old freebies index")

        # Downstream and unrelated production artifacts must survive untouched.
        # Cross-platform giveaways are deliberately a separate single-writer
        # family and therefore must also survive the Steam collector reset.
        protected = [
            root / "mailing" / "index.json",
            root / "pre_ai" / "chatgpt_payload.json",
            root / "daily_ready" / "latest.json",
            root / "giveaways" / "index.json",
            root / "giveaways" / "v1" / "current.json",
            root / "giveaways" / "v1" / "audit.jsonl",
            root / "other_producer" / "sentinel.txt",
        ]
        for path in protected:
            write(path)

        reset_steam_collector_outputs(root)

        assert not (root / "shortlist").exists(), "stale shortlist survived reset"
        assert not (root / "manifest.json").exists(), "old manifest survived reset"
        assert not (root / "freebies.tsv").exists(), "old freebies survived reset"
        assert not (root / "freebies_index.json").exists(), "old freebies index survived reset"

        for path in protected:
            assert path.read_text(encoding="utf-8") == "sentinel", f"foreign artifact changed: {path}"

    print("Production output ownership regression test passed")


if __name__ == "__main__":
    main()
