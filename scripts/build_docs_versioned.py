#!/usr/bin/env python3
import sys
import subprocess
from typing import Tuple, Set, List

# The building system have changed, thus the old versions are not buildable with this system
MIN_SUPPORTED_TAG = '1.2.0'


def get_version_from_tag(tag: str) -> Tuple[int, ...]:
    return tuple(map(int, tag.lstrip('v').split('.')))


def filter_git_tags(tags) -> Set[str]:
    min_version = get_version_from_tag(MIN_SUPPORTED_TAG)
    buildable_tags = filter(lambda tag: get_version_from_tag(tag) >= min_version, tags)
    return set(buildable_tags)


def build_versioned(main_ref: str, tags: List[str], dest_dir: str):
    refs_to_build = filter_git_tags(tags)
    refs_to_build.add(main_ref)

    command_args = ['sphinx-versioned']
    command_args += ['--branches', ','.join(refs_to_build)]
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
