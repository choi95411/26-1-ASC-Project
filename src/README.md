# 안전한 복호화 파이프라인 소스 설명

## 목적

`src` 디렉토리는 안전한 dummy 파일 기반 복호화 파이프라인을 검증하기 위한 코드로 구성된다. 실제 피해 파일 복구도구가 아니며, 단일 테스트 파일만 처리한다.

## 파일 역할

| 파일 | 역할 |
| --- | --- |
| `safe_test_encrypt.py` | dummy 원본 파일을 AES-CTR로 암호화하고 테스트용 `.rhysida` 파일을 생성한다. |
| `rhysida_file_parser.py` | dummy `.rhysida` 파일에서 암호화 본문과 footer metadata를 분리한다. |
| `recovery_demo.py` | footer 또는 parser JSON에서 AES key/IV를 읽어 AES-CTR 복호화를 수행하고 SHA-256을 검증한다. |
| `requirements.txt` | 실행에 필요한 Python 패키지를 정리한다. |

## 테스트 footer 구조

```text
ciphertext
+ ASC_RHYSIDA_TEST_FOOTER_V1\n
+ metadata 길이, 8바이트, big endian
+ metadata JSON, UTF-8
```

metadata에는 `aes_key`, `aes_iv`, `plaintext_sha256`, `ciphertext_sha256`, `original_name`이 포함된다.

## 실행 순서

```bash
python3 -m pip install -r src/requirements.txt
python3 src/safe_test_encrypt.py tests/test_vectors/sample_plain.txt --force
python3 src/rhysida_file_parser.py tests/test_vectors/sample_plain.txt.rhysida --include-ciphertext -o tests/test_vectors/parser_result.json
python3 src/recovery_demo.py tests/test_vectors/sample_plain.txt.rhysida -o tests/test_vectors/recovered_5th.txt --json
```

성공 기준은 복구 결과의 `verified` 값이 `true`이고, 원본 SHA-256과 복구 결과 SHA-256이 일치하는 것이다.

## 안전 범위

- 단일 파일만 처리한다.
- 디렉토리 순회 기능은 없다.
- 입력 파일을 삭제하거나 덮어쓰지 않는다.
- 감염, 전파, 지속성 유지, 백업 삭제 기능은 구현하지 않는다.
