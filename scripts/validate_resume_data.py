#!/usr/bin/env python3
"""Validate normalized bilingual resume JSON without inventing missing facts."""

import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(r"\b(?:todo|tbd|n/?a|xxx|placeholder)\b|\{\{.+?\}\}|\[.+?\]", re.I)


def check_bilingual(value, path, errors, required=True):
    if not isinstance(value, dict):
        errors.append(f"{path} must contain ar and en")
        return
    for lang in ("ar", "en"):
        text = str(value.get(lang, "")).strip()
        if required and not text:
            errors.append(f"{path}.{lang} is required")
        if text and PLACEHOLDER.search(text):
            errors.append(f"{path}.{lang} contains an unresolved placeholder")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    errors = []
    person = data.get("person") or {}
    check_bilingual(person.get("name"), "person.name", errors)
    check_bilingual(person.get("headline"), "person.headline", errors)
    check_bilingual(data.get("summary"), "summary", errors)
    for field in ("phone", "email"):
        if not str(person.get(field, "")).strip():
            errors.append(f"person.{field} is required")
    email = str(person.get("email", ""))
    if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors.append("person.email does not look valid")
    if not data.get("experience") and not data.get("education"):
        errors.append("at least one experience or education entry is required")

    def scan(value, path="root"):
        if isinstance(value, dict):
            for key, child in value.items():
                scan(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                scan(child, f"{path}[{index}]")
        elif isinstance(value, str) and PLACEHOLDER.search(value):
            errors.append(f"{path} contains an unresolved placeholder")

    scan(data)
    report = {"valid": not errors, "errors": sorted(set(errors))}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
