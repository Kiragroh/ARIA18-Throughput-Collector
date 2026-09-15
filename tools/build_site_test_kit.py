"""Compatibility entry point for the execution-only participant bundle."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.package_v2 import manifest, package

FILES = manifest(analysis=False)


def build():
    return package(analysis=False)


if __name__ == '__main__':
    build()
