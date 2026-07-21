from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MAGIC = b"ASC_RHYSIDA_TEST_FOOTER_V1\n"
LENGTH_SIZE = 8


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_test_file(path: Path, include_ciphertext: bool = False) -> dict:
    data = path.read_bytes()
    marker = data.rfind(MAGIC)
    if marker < 0:
        raise ValueError("test footer magic not found")

    length_start = marker + len(MAGIC)
    length_end = length_start + LENGTH_SIZE
    if len(data) < length_end:
        raise ValueError("footer length field is truncated")

    metadata_len = int.from_bytes(data[length_start:length_end], "big")
    metadata_start = length_end
    metadata_end = metadata_start + metadata_len
    if metadata_len <= 0 or len(data) < metadata_end:
        raise ValueError("metadata length is invalid")

    metadata = json.loads(data[metadata_start:metadata_end].decode("utf-8"))
    ciphertext = data[:marker]
    result = {
        "input": str(path),
        "file_size": len(data),
        "ciphertext_offset": 0,
        "ciphertext_size": len(ciphertext),
        "footer_offset": marker,
        "footer_size": len(data) - marker,
        "metadata": metadata,
        "ciphertext_sha256": sha256_bytes(ciphertext),
    }
    if include_ciphertext:
        result["ciphertext_hex"] = ciphertext.hex()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse one safe dummy .rhysida test file.")
    parser.add_argument("encrypted_file", type=Path)
    parser.add_argument("--include-ciphertext", action="store_true")
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    try:
        result = parse_test_file(args.encrypted_file, args.include_ciphertext)
    except Exception as exc:
        print(f"[FAIL] {exc}")
        return 1

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
