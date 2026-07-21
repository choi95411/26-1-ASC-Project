# 5차 테스트 검증 결과

## 테스트 개요

5차 작업에서는 `safe_test_encrypt.py`, `rhysida_file_parser.py`, `recovery_demo.py`를 연결하여 안전한 dummy 파일 기반 암호화/복호화 파이프라인을 검증하였다.

## 실행 명령

```bash
python3 src/safe_test_encrypt.py tests/test_vectors/sample_plain.txt --force
python3 src/rhysida_file_parser.py tests/test_vectors/sample_plain.txt.rhysida --include-ciphertext -o tests/test_vectors/parser_result.json
python3 src/recovery_demo.py tests/test_vectors/sample_plain.txt.rhysida -o tests/test_vectors/recovered_5th.txt --json
```

## 파일별 역할

| 파일 | 역할 |
| --- | --- |
| `tests/test_vectors/sample_plain.txt` | 원본 dummy 파일 |
| `tests/test_vectors/sample_plain.txt.rhysida` | 테스트용 AES-CTR 암호화 파일 |
| `tests/test_vectors/parser_result.json` | parser가 추출한 footer metadata 및 본문 정보 |
| `tests/test_vectors/recovered_5th.txt` | 복호화 결과 파일 |

## SHA-256 검증 결과

| 항목 | SHA-256 |
| --- | --- |
| 원본 파일 | `aa0ca76da0b2cb4a23a7f432d5a28635fe0cfa251934e65ff5568c7e4616af7a` |
| 암호화 본문 | `2f3c932527a58793032d595289d77d247672d77646bf60adad07e4a3edf02a7e` |
| 복구 결과 파일 | `aa0ca76da0b2cb4a23a7f432d5a28635fe0cfa251934e65ff5568c7e4616af7a` |

## 확인 결과

`recovery_demo.py` 실행 결과 `verified: true`를 확인하였다. 따라서 현재 dummy 테스트 벡터 기준으로 AES-CTR 암호화, footer parsing, AES-CTR 복호화, SHA-256 검증 흐름이 정상적으로 연결되었다.

## 한계

이 결과는 프로젝트에서 직접 만든 dummy 파일과 테스트용 footer 구조를 대상으로 한 검증이다. 실제 피해 파일 복구를 보장하지 않으며, 실제 악성 행위나 디렉토리 순회 기능은 포함하지 않는다.
