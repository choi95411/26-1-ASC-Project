from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MAGIC = b"ASC_RHYSIDA_TEST_FOOTER_V1\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def aes_ctr_crypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    encryptor = cipher.encryptor()
    return encryptor.update(data) + encryptor.finalize()


def build_footer(metadata: dict) -> bytes:
    metadata_bytes = json.dumps(metadata, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return MAGIC + len(metadata_bytes).to_bytes(8, "big") + metadata_bytes


def encrypt_dummy_file(input_path: Path, output_path: Path | None, force: bool) -> dict:
    if not input_path.is_file():
        raise FileNotFoundError(f"input file not found: {input_path}")

    destination = output_path or input_path.with_name(input_path.name + ".rhysida")
    if destination.exists() and not force:
        raise FileExistsError(f"output already exists: {destination}")

    plaintext = input_path.read_bytes()
    key = os.urandom(32)
    iv = os.urandom(16)
    ciphertext = aes_ctr_crypt(plaintext, key, iv)

    metadata = {
        "format": "ASC_RHYSIDA_TEST_FOOTER_V1",
        "aes_key": key.hex(),
        "aes_iv": iv.hex(),
        "original_name": input_path.name,
        "plaintext_size": len(plaintext),
        "plaintext_sha256": sha256_bytes(plaintext),
        "ciphertext_sha256": sha256_bytes(ciphertext),
        "note": "safe dummy AES-CTR test vector for ASC project only",
    }

    destination.write_bytes(ciphertext + build_footer(metadata))
    return {
        "input": str(input_path),
        "output": str(destination),
        "plaintext_sha256": metadata["plaintext_sha256"],
        "ciphertext_sha256": metadata["ciphertext_sha256"],
        "footer_format": metadata["format"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create one safe dummy .rhysida test file.")
    parser.add_argument("input_file", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    try:
        result = encrypt_dummy_file(args.input_file, args.output, args.force)
    except Exception as exc:
        print(f"[FAIL] {exc}")
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
