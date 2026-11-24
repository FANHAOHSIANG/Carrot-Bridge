"""Reconstruct the one exact original-certificate APK with a precomputed PUBLIC signature block.

No JKS, signing password or private key is committed or used by GitHub Actions.
Refuse any unsigned APK or signature block that does not match the pinned build.
The APK is verified independently by Android SDK apksigner in the publish workflow.
"""
import argparse
import base64
import hashlib
import mmap
import struct
from pathlib import Path

BASE_SHA = 'ffdc1ed539109c86422b95d9630a32603711a586b80ede1ab0c2f081b3064428'
SIGNED_SHA = '6241531d34fa45c8d73e1d44febb1bbd3eee893efd3dd14bb1dcc79eebfd4a3d'
BLOCK_SHA = None
APK_SIG_MAGIC = b'APK Sig Block 42'
APK_V2_ID = 0x7109871a


def sha256(path: Path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def eocd_offset(data):
    for i in range(len(data) - 22, max(0, len(data) - 22 - 0xffff) - 1, -1):
        if data[i:i + 4] == b'PK\x05\x06' and i + 22 + struct.unpack_from('<H', data, i + 20)[0] == len(data):
            return i
    raise ValueError('ZIP EOCD is missing or invalid')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('unsigned', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Refusing to overwrite an output file')
    if sha256(args.unsigned) != BASE_SHA:
        parser.error('Unsigned APK SHA-256 mismatch: signature is ONLY valid for the pinned build')
    block = base64.b64decode((Path(__file__).parent / 'signature-block.b64').read_text().strip(), validate=True)
    if (len(block) < 40 or block[-16:] != APK_SIG_MAGIC
            or struct.unpack_from('<Q', block, 0)[0] != len(block) - 8
            or struct.unpack_from('<Q', block, len(block) - 24)[0] != len(block) - 8
            or struct.unpack_from('<I', block, 16)[0] != APK_V2_ID):
        parser.error('Invalid APK v2 signature block')
    with args.unsigned.open('rb') as handle:
        with mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as data:
            eocd = eocd_offset(data)
            central = struct.unpack_from('<I', data, eocd + 16)[0]
            central_size = struct.unpack_from('<I', data, eocd + 12)[0]
            if central + central_size != eocd:
                parser.error('Unexpected ZIP central directory or multivolume ZIP')
            if central + len(block) > 0xffffffff:
                parser.error('ZIP64 APK is unsupported')
            with args.output.open('xb') as out:
                out.write(data[:central])
                out.write(block)
                out.write(data[central:eocd])
                end = bytearray(data[eocd:])
                struct.pack_into('<I', end, 16, central + len(block))
                out.write(end)
    result = sha256(args.output)
    if result != SIGNED_SHA:
        args.output.unlink(missing_ok=True)
        parser.error('Signed APK content hash mismatch; refusing to publish')
    print('PASS: signed APK matches original-certificate externally signed artifact SHA-256', result)


if __name__ == '__main__':
    main()
