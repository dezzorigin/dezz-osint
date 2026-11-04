#!/usr/bin/env python3
"""Backward-compat launcher. Preferred: `pip install .` then run `dezz`,
or `python -m dezz.cli`."""
from dezz.cli import main

if __name__ == "__main__":
    main()
