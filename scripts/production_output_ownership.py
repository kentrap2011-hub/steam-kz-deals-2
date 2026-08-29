import shutil
from pathlib import Path


OWNED_DIRECTORIES = ("shortlist",)
OWNED_FILES = (
    "manifest.json",
    "freebies.tsv",
    "freebies_index.json",
)


def reset_steam_collector_outputs(production_root):
    """Remove only artifacts owned by the Steam catalog collector.

    Downstream artifacts such as mailing/, pre_ai/ and daily_ready/ must survive
    a commercial refresh until their own producers replace them.
    """
    root = Path(production_root)
    root.mkdir(parents=True, exist_ok=True)

    for relative in OWNED_DIRECTORIES:
        target = root / relative
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.exists():
            shutil.rmtree(target)

    for relative in OWNED_FILES:
        target = root / relative
        if target.exists() or target.is_symlink():
            target.unlink()
