#!/usr/bin/env python3
import subprocess


def main():
    process = subprocess.run(['sphinx-build', 'docs/', 'public'])
    return process.returncode


if __name__ == '__main__':
    return_code = main()
    exit(return_code)
