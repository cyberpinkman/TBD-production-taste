#!/usr/bin/env python3
"""Copy the bundled TBD skills without overwriting existing installations."""
import argparse
import os
from pathlib import Path
import shutil
import sys


def install(destination):
    source = Path(__file__).resolve().parents[1] / "skills"
    skills = sorted(p for p in source.glob("tbd-*") if (p / "SKILL.md").is_file())
    if len(skills) != 6:
        raise ValueError("Expected all six bundled TBD skills; use a complete checkout.")
    conflicts = [destination / p.name for p in skills
                 if (destination / p.name).exists() or (destination / p.name).is_symlink()]
    if conflicts:
        raise ValueError("Existing skill directories; nothing installed: "
                         + ", ".join(str(p) for p in conflicts))
    for skill in skills:
        if any(p.is_symlink() for p in skill.rglob("*")):
            raise ValueError(f"Symlinks are not supported in bundled skills: {skill.name}")
    destination.mkdir(parents=True, exist_ok=True)
    for skill in skills:
        shutil.copytree(skill, destination / skill.name)
        print(f"Installed {skill.name} -> {destination / skill.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills"
    parser.add_argument("--dest", type=Path, default=default,
                        help="skill directory (default: $CODEX_HOME/skills or ~/.codex/skills)")
    args = parser.parse_args()
    try:
        install(args.dest.expanduser().resolve())
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
