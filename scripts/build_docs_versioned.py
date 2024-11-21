#!/usr/bin/env python3
import sys
import subprocess
from typing import Tuple, Set, List


def get_version_from_tag(tag: str) -> Tuple[int, ...]:
    return tuple(map(int, tag.lstrip('v').split('.')))


def build_versioned(main_ref: str, tags: List[str], dest_dir: str):
    refs_to_build = {main_ref, *tags}

    from sphinx_versioned._version import __version_tuple__ as sphinx_versioned_version

    command_args = ['sphinx-versioned']
    if sphinx_versioned_version < (1, 4):
        command_args += ['--branches', ','.join(refs_to_build)]
    else:
        command_args += ['--branch', ','.join(refs_to_build)]
    command_args += ['--main-branch', main_ref]
    command_args += ['--output', dest_dir]

    process = subprocess.run(command_args, capture_output=True, encoding='utf-8')
    print(process.stdout)
    print(process.stderr)
    for line in process.stdout.splitlines():
        if '| CRITICAL | ' in line or '| ERROR | ' in line:
            raise RuntimeError(process.stdout)


def main():
    dest_dir = sys.argv[1]
    main_ref = sys.argv[2]
    tags = sys.argv[3:]

    try:
        build_versioned(main_ref, tags, dest_dir)
    except RuntimeError:
        return 1
    return 0


if __name__ == '__main__':
    exit(main())
