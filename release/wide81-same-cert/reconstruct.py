"""Rebuild one exact original-signer wide.81 APK from its pinned unsigned build.

The repository contains only a historical PUBLIC certificate block and the
PUBLIC signature for this exact wide.81 digest, never a private signing key.
The official Android apksigner independently verifies this output in CI.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import mmap
import struct

ROOT = Path(__file__).resolve().parent
SHARED_BLOCK = ROOT.parent / "wide80-same-cert/signature-block.b64"
SIGNATURE = ROOT / "signature-only.b64"
APK_MAGIC = b"APK Sig Block 42"
BASE_SHA = "3fd547142dd6cd7a89cddd79d9b1f7f5cc93668e7e941dc4c180db718e300d2a"
SIGNED_SHA = "801d804a8281e776deb0a983f126594a35ccb200a8ff14e9d72f36b25f549d31"
BLOCK_SHA = "ee9eb073468fdb67fb9e45789b7098c6bb47d937bccf332a330ed9c528576a5d"
DIGEST = bytes.fromhex("5b750c5ec34cf13f0fa4f98a67198ba5868c30a52cfdc883651794bc94b1cd3c")


def hash_file(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def u32(data, i):
    return struct.unpack_from("<I", data, i)[0]


def u64(data, i):
    return struct.unpack_from("<Q", data, i)[0]


def signing_block():
    base = bytearray(base64.b64decode(SHARED_BLOCK.read_text().strip(), validate=True))
    if not (len(base) == 2011 and base[-16:] == APK_MAGIC and u64(base, 0) == 2003
            and u64(base, len(base) - 24) == 2003 and u32(base, 16) == 0x7109871a):
        raise ValueError("Unexpected public APK v2 certificate block")
    val = 20
    signer_start = val + 4
    assert val + 4 + u32(base, val) == len(base) - 24
    assert signer_start + 4 + u32(base, signer_start) == len(base) - 24
    data_start = signer_start + 4
    data_length = u32(base, data_start)
    sd_start = data_start + 4
    signatures_length_at = sd_start + data_length
    digests_len_at = sd_start
    record_len_at = digests_len_at + 4
    assert record_len_at + 4 + u32(base, record_len_at) == digests_len_at + 4 + u32(base, digests_len_at)
    assert u32(base, record_len_at + 4) == 0x103
    digest_len_at = record_len_at + 8
    assert u32(base, digest_len_at) == 32
    digest_at = digest_len_at + 4
    sigs_length = u32(base, signatures_length_at)
    signature_record = signatures_length_at + 4
    assert u32(base, signature_record) + 4 == sigs_length
    assert u32(base, signature_record + 4) == 0x103
    assert u32(base, signature_record + 8) == 384
    signature_at = signature_record + 12
    signature = base64.b64decode(SIGNATURE.read_text().strip(), validate=True)
    if len(signature) != 384:
        raise ValueError("Invalid signature length")
    base[digest_at:digest_at + 32] = DIGEST
    base[signature_at:signature_at + 384] = signature
    if hashlib.sha256(base).hexdigest() != BLOCK_SHA:
        raise ValueError("Public signature block hash mismatch")
    return base


def locate_eocd(data):
    for i in range(len(data) - 22, max(-1, len(data) - 22 - 65535), -1):
        if data[i:i+4] == b"PK\\x05\\x06" and i + 22 + u32(data, i + 20) == len(data):
            return i
    raise ValueError("ZIP EOCD missing")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unsigned", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Will not overwrite existing output")
    if hash_file(args.unsigned) != BASE_SHA:
        parser.error("Unsigned APK SHA-256 mismatch")
    block = signing_block()
    with args.unsigned.open("rb") as source:
        with mmap.mmap(source.fileno(), 0, access=mmap.ACCESS_READ) as data:
            eocd = locate_eocd(data)
            central = u32(data, eocd + 16)
            central_size = u32(data, eocd + 12)
            if central + central_size != eocd or central + len(block) > 0xffffffff:
                parser.error("Unsupported ZIP central directory")
            with args.output.open("xb") as out:
                out.write(data[:central])
                out.write(block)
                out.write(data[central:eocd])
                tail = bytearray(data[eocd:])
                struct.pack_into("<I", tail, 16, central + len(block))
                out.write(tail)
    digest = hash_file(args.output)
    if digest != SIGNED_SHA:
        args.output.unlink(missing_ok=True)
        parser.error("Reconstructed signed APK hash mismatch")
    print("PASS original-certificate signed APK", digest)


if __name__ == "__main__":
    main()
