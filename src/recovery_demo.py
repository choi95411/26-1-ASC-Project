from __future__ import annotations

import argparse
import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


MAGIC = b"ASC_RHYSIDA_TEST_FOOTER_V1\n"
LENGTH_SIZE = 8
DEFAULT_OUTPUT_PREFIX = "recovered_"


class RecoveryError(Exception):
    """Raised when the test recovery flow cannot continue safely."""


@dataclass(frozen=True)
class ParsedTestFile:
    ciphertext: bytes
    metadata: dict[str, Any]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_hex_or_b64(value: str, field_name: str, expected_len: int | None = None) -> bytes:
    text = value.strip()
    try:
        decoded = bytes.fromhex(text)
    except ValueError:
        try:
            decoded = base64.b64decode(text, validate=True)
        except Exception as exc:  # noqa: BLE001 - convert parser detail to a clear project error
            raise RecoveryError(f"{field_name} must be hex or base64") from exc

    if expected_len is not None and len(decoded) != expected_len:
        raise RecoveryError(f"{field_name} must be {expected_len} bytes, got {len(decoded)}")
    return decoded


def parse_embedded_footer(input_path: Path) -> ParsedTestFile:
    data = input_path.read_bytes()
    marker = data.rfind(MAGIC)
    if marker < 0:
        raise RecoveryError("test footer magic was not found")

    length_start = marker + len(MAGIC)
    length_end = length_start + LENGTH_SIZE
    if len(data) < length_end:
        raise RecoveryError("test footer is truncated before metadata length")

    metadata_len = int.from_bytes(data[length_start:length_end], "big")
    metadata_start = length_end
    metadata_end = metadata_start + metadata_len
    if metadata_len <= 0 or len(data) < metadata_end:
        raise RecoveryError("test footer metadata length is invalid")

    try:
        metadata = json.loads(data[metadata_start:metadata_end].decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RecoveryError("test footer metadata is not valid JSON") from exc

    ciphertext = data[:marker]
    return ParsedTestFile(ciphertext=ciphertext, metadata=metadata)


def load_parser_json(parser_json_path: Path, encrypted_path: Path) -> ParsedTestFile:
    try:
        parser_result = json.loads(parser_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RecoveryError("parser JSON is not valid JSON") from exc

    ciphertext_hex = parser_result.get("ciphertext_hex")
    if isinstance(ciphertext_hex, str):
        ciphertext = decode_hex_or_b64(ciphertext_hex, "ciphertext_hex")
    else:
        ciphertext_path = parser_result.get("ciphertext_path")
        if not isinstance(ciphertext_path, str):
            raise RecoveryError("parser JSON must include ciphertext_hex or ciphertext_path")
        candidate = Path(ciphertext_path)
        if not candidate.is_absolute():
            candidate = parser_json_path.parent / candidate
        ciphertext = candidate.read_bytes()

    metadata = parser_result.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {k: v for k, v in parser_result.items() if k != "ciphertext_hex"}
    metadata.setdefault("source_file", encrypted_path.name)
    return ParsedTestFile(ciphertext=ciphertext, metadata=metadata)


def aes_ctr_crypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    decryptor = cipher.decryptor()
    return decryptor.update(data) + decryptor.finalize()


def choose_output_path(encrypted_path: Path, output_path: Path | None) -> Path:
    if output_path is not None:
        return output_path

    name = encrypted_path.name
    if name.endswith(".rhysida"):
        name = name[: -len(".rhysida")]
    return encrypted_path.with_name(DEFAULT_OUTPUT_PREFIX + name)


def recover_file(
    encrypted_path: Path,
    output_path: Path | None = None,
    parser_json_path: Path | None = None,
) -> dict[str, Any]:
    if not encrypted_path.is_file():
        raise RecoveryError(f"input file not found: {encrypted_path}")

    parsed = (
        load_parser_json(parser_json_path, encrypted_path)
        if parser_json_path is not None
        else parse_embedded_footer(encrypted_path)
    )

    key_value = parsed.metadata.get("aes_key") or parsed.metadata.get("key")
    iv_value = parsed.metadata.get("aes_iv") or parsed.metadata.get("iv")
    if not isinstance(key_value, str) or not isinstance(iv_value, str):
        raise RecoveryError("metadata must include aes_key/key and aes_iv/iv")

    key = decode_hex_or_b64(key_value, "aes_key", expected_len=32)
    iv = decode_hex_or_b64(iv_value, "aes_iv", expected_len=16)
    plaintext = aes_ctr_crypt(parsed.ciphertext, key, iv)

    destination = choose_output_path(encrypted_path, output_path)
    if destination.exists():
        raise RecoveryError(f"output already exists, refusing to overwrite: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(plaintext)

    expected_sha256 = parsed.metadata.get("plaintext_sha256") or parsed.metadata.get("original_sha256")
    actual_sha256 = sha256_bytes(plaintext)
    verified = None
    if isinstance(expected_sha256, str):
        verified = expected_sha256.lower() == actual_sha256.lower()

    return {
        "input": str(encrypted_path),
        "output": str(destination),
        "ciphertext_sha256": sha256_bytes(parsed.ciphertext),
        "recovered_sha256": actual_sha256,
        "expected_sha256": expected_sha256,
        "verified": verified,
        "bytes_recovered": len(plaintext),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recover one dummy AES-CTR test file generated for the ASC project."
    )
    parser.add_argument("encrypted_file", type=Path, help="Dummy .rhysida test file")
    parser.add_argument("-o", "--output", type=Path, help="Recovered output file path")
    parser.add_argument(
        "--parser-json",
        type=Path,
        help="Optional JSON output from rhysida_file_parser.py",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    try:
        result = recover_file(args.encrypted_file, args.output, args.parser_json)
    except RecoveryError as exc:
        print(f"[FAIL] {exc}")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"[OK] recovered: {result['output']}")
        print(f"[OK] recovered_sha256: {result['recovered_sha256']}")
        if result["verified"] is not None:
            status = "match" if result["verified"] else "mismatch"
            print(f"[OK] sha256_check: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

