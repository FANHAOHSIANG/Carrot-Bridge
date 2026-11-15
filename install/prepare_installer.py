#!/usr/bin/env python3
"""Prepare a C4 test installer using a verified comma installer, without executing it."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

SOURCE_URL = "https://installer.comma.ai/commaai/nightly-dev"
SOURCE_HEADERS = {"User-Agent": "AGNOSSetup-19.8", "X-openpilot-device-type": "mici"}
SOURCE_SHA256 = "8e44055e93f01b0ecca8eaf47c50f2dec993ace2c291907a6ee941a62bf28997"
REPOSITORY = "https://github.com/FANHAOHSIANG/openpilot-carrot.git"
BRANCH = "test/carrot-wip-upstream-20261104"
CHECKED_HEAD = "796633626c61ef0fa9486ba0898a970b99f2d31a"


def prepare(source: bytes):
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError("Unexpected upstream installer. Review a new base before updating its hash.")
    if source[:6] != b"\x7fELF\x02\x01" or struct.unpack_from("<H", source, 18)[0] != 183:
        raise ValueError("Expected a little-endian ELF64 AArch64 installer")
    result = bytearray(source)
    changes = []

    def replace(pattern, value, padding):
        hits = list(re.finditer(pattern, source))
        if len(hits) != 1:
            raise ValueError(f"Expected one literal for {pattern!r}")
        hit = hits[0]
        if len(value) > len(hit[0]):
            raise ValueError("Replacement exceeds its reserved slot")
        replacement = value.ljust(len(hit[0]), padding)
        result[hit.start():hit.end()] = replacement
        changes.append({"offset": hit.start(), "size": len(hit[0]),
                        "before": hit[0].rstrip(b"\0").decode(),
                        "after": replacement.rstrip(b"\0").decode()})

    replace(rb"https://github\.com/commaai/openpilot\.git\? +", REPOSITORY.encode() + b"?", b" ")
    replace(rb"nightly-dev\? +", BRANCH.encode() + b"?", b" ")
    # The stock cache may have an origin pointing at a different repository.
    # Use a private, never-created cache marker, so normal installs clone the
    # specified repository instead of fetching from a retained stock origin.
    replace(rb"/data/\.openpilot_cache\x00", b"/data/.cb1104_no_cache\x00", b"\0")
    replace(rb"(?<![A-Za-z])installing\.\.\.\x00", b"TEST BRANCH\x00", b"\0")

    output = bytes(result)
    assert len(output) == len(source)
    # The upstream ELF maps .text and .rodata in one load segment. Check the
    # section flags instead, and preserve every executable section byte.
    shoff = struct.unpack_from("<Q", source, 40)[0]
    shsize, count = struct.unpack_from("<HH", source, 58)
    sections = [struct.unpack_from("<IIQQQQIIQQ", source, shoff + i * shsize) for i in range(count)]
    for change in changes:
        start, end = change["offset"], change["offset"] + change["size"]
        assert any(kind == 1 and flags == 2 and offset <= start and end <= offset + size
                   for _, kind, flags, _, offset, size, *_ in sections), "Change outside read-only data"
    for _, _, flags, _, offset, size, *_ in sections:
        if flags & 4:
            assert source[offset:offset + size] == output[offset:offset + size]
    for i, (before, after) in enumerate(zip(source, output)):
        assert before == after or any(c["offset"] <= i < c["offset"] + c["size"] for c in changes)
    return output, {
        "device": "comma four / MICI", "source_url": SOURCE_URL,
        "source_headers": SOURCE_HEADERS, "source_sha256": SOURCE_SHA256,
        "repository": REPOSITORY, "branch": BRANCH,
        "branch_head_at_verification": CHECKED_HEAD,
        "tracks_branch": True, "size_bytes": len(output),
        "sha256": hashlib.sha256(output).hexdigest(), "literal_changes": changes,
        "validation": "ELF and read-only literal changes checked offline; not installed or boot-tested on C4",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data, manifest = prepare(args.source.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    args.output.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
    args.output.with_suffix(".sha256").write_text(manifest["sha256"] + "  " + args.output.name + "\n")
    print(json.dumps({key: manifest[key] for key in ("repository", "branch", "sha256", "size_bytes", "validation")}))


if __name__ == "__main__":
    main()
