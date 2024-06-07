#!/usr/bin/env python3
import sys
import subprocess

# The building system have changed, thus the old versions are not buildable with this system
MIN_SUPPORTED_TAG = '1.2.0'

def version(tag):
    return tuple( int(number) for number in tag.split('.') )

def filter_buildable_tags(all_tags):
    min_version = version(MIN_SUPPORTED_TAG)
    return {tag for tag in all_tags if version(tag) >= min_version}

def build_versioned(main_branch, dest_dir):
    subprocess.run(['git', 'fetch', '--tags'])
    process = subprocess.run(['git', 'fetch', '--tags', 'git', 'tags'], capture_output=True, encoding='utf-8')

    buildable_tags = filter_buildable_tags(process.stdout.splitlines())
    buildable_tags.add(main_branch)

    command_args = ['sphinx-versioned']
    command_args += ['--branches', ','.join(buildable_tags)]
    command_args += ['--main-branch', main_branch]
    command_args += ['--output', dest_dir]

    print(' '.join(command_args))
    subprocess.run(command_args)


def main():
    trigger_branch = sys.argv[1]
    dest_dir = sys.argv[2]
    build_versioned(trigger_branch, dest_dir)


if __name__ == '__main__':
    main()
