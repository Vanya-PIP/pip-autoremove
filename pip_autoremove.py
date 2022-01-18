#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
import sys
from typing import List


def get_requesters(package: str) -> List[str]:
    try:
        res = subprocess.run(["pip", "show", package], check=True, text=True,
                             capture_output=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.stderr)
    requesters = res.stdout.split("\n")[-2]
    requesters = [s for i in requesters[len("Required-by:"):].split(",")
                  if (s := i.strip())]

    return requesters


def get_requirements(package: str) -> List[str]:
    try:
        res = subprocess.run(["pip", "show", package], check=True, text=True,
                             capture_output=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.stderr)
    requirements = res.stdout.split("\n")[-3]
    requirements = [s for i in requirements[len("Requires:"):].split(",")
                    if (s := i.strip())]

    return requirements


def uninstall(package: str, yes: bool = False) -> bool:
    try:
        args = ["pip", "uninstall", package]
        if yes:
            args.append("-y")
        subprocess.run(args, check=True, text=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.stderr)

    try:
        subprocess.run(["pip", "show", package],
                       check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return True
    else:
        return False


def main():
    descr = "Remove python package and it's dependencies"

    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument("package")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="Don't ask for confirmation of uninstall deletions")
    args = parser.parse_args()

    requirements = get_requirements(args.package)

    if not uninstall(args.package, args.yes):
        sys.exit()

    requirements_to_uninstall = []
    for r in requirements:
        requesters = [i for i in get_requesters(r) if i != args.package and i not
                      in requirements]
        if not requesters:
            requirements_to_uninstall.append(r)

    if not requirements_to_uninstall:
        sys.exit(f"\nSuccessfully uninstalled {args.package}")

    print("\nNext dependencies can be removed:")
    print(*(f"  {i}" for i in requirements_to_uninstall), sep="\n", end="\n\n")

    for r in requirements_to_uninstall:
        uninstall(r, args.yes)

    print(f"\nSuccessfully uninstalled {args.package} and it's dependencies")


if __name__ == "__main__":
    main()
