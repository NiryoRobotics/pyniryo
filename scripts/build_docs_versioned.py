#!/usr/bin/env python3
import sys
import subprocess
import os
from pathlib import Path
from typing import Tuple, Set, List


def get_version_from_tag(tag: str) -> Tuple[int, ...]:
    return tuple(map(int, tag.lstrip('v').split('.')))


def get_already_built_versions(dest_dir: str) -> Set[str]:
    """
    Check which versions already have built documentation in the destination directory.
    Returns a set of version names (e.g., 'v1.2.0', 'v1.2.1')
    """
    dest_path = Path(dest_dir)
    if not dest_path.exists():
        print(f"Destination directory '{dest_dir}' does not exist yet. Will build all versions.")
        return set()

    # sphinx-versioned creates subdirectories for each version
    # We need to check for directories that contain built docs
    existing_versions = set()
    for item in dest_path.iterdir():
        if item.is_dir() and item.name not in ['.git', '.buildinfo', '_static', '_sources']:
            # Check if it contains index.html to verify it's a built version
            index_file = item / 'index.html'
            if index_file.exists():
                existing_versions.add(item.name)
                print(f"Found already-built version: {item.name}")

    return existing_versions


def build_versioned(main_ref: str, tags: List[str], dest_dir: str):
    """
    Build documentation for versions that don't already exist in the cache.
    This implements incremental builds to avoid rebuilding all versions every time.
    """
    # Check which versions are already built
    already_built = get_already_built_versions(dest_dir)

    # Filter out already-built versions
    refs_to_build = {main_ref}
    for tag in tags:
        if tag not in already_built:
            refs_to_build.add(tag)
        else:
            print(f"Skipping already-built version: {tag}")

    print(f"\nBuilding {len(refs_to_build)} version(s): {refs_to_build}")

    from sphinx_versioned._version import __version_tuple__ as sphinx_versioned_version

    command_args = ['sphinx-versioned']
    if sphinx_versioned_version < (1, 4):
        command_args += ['--branches', ','.join(refs_to_build)]
    else:
        command_args += ['--branch', ','.join(refs_to_build)]
    command_args += ['--main-branch', main_ref]
    command_args += ['--output', dest_dir]

    print(f"\nRunning command: {' '.join(command_args)}\n")

    process = subprocess.Popen(command_args,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               encoding='utf-8',
                               text=True)
    error_occurred = False
    for line in process.stdout:
        print(line, end='')
        if '| CRITICAL | ' in line or '| ERROR | ' in line:
            error_occurred = True
    process.wait()
    if error_occurred:
        raise RuntimeError("Documentation build failed with errors. Check the output above for details.")


def main():
    dest_dir = sys.argv[1]
    main_ref = sys.argv[2]
    tags = sys.argv[3:]

    print("=" * 60)
    print("INCREMENTAL DOCUMENTATION BUILD")
    print("=" * 60)
    print(f"Destination: {dest_dir}")
    print(f"Main ref: {main_ref}")
    print(f"Total tags: {len(tags)}")
    print("=" * 60 + "\n")

    try:
        build_versioned(main_ref, tags, dest_dir)
        print("\n" + "=" * 60)
        print("BUILD COMPLETED SUCCESSFULLY")
        print("=" * 60)
    except RuntimeError as e:
        print("\n" + "=" * 60)
        print("BUILD FAILED")
        print("=" * 60)
        print(str(e))
        return 1
    return 0


if __name__ == '__main__':
    exit(main())
