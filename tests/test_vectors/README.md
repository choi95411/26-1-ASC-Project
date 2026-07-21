# 테스트 벡터 설명

## 목적

이 디렉토리는 안전한 dummy 파일 기반 AES-CTR 암호화/복호화 파이프라인을 검증하기 위한 테스트 파일을 보관한다. 실제 악성 샘플이나 실제 피해 파일이 아니다.

## 파일 목록

| 파일 | 설명 |
| --- | --- |
| `sample_plain.txt` | 안전한 dummy 원본 파일 |
| `sample_plain.txt.rhysida` | `safe_test_encrypt.py`로 생성한 dummy 암호화 파일 |
| `parser_result.json` | `rhysida_file_parser.py`가 추출한 본문/footer 분석 결과 |
| `recovered_5th.txt` | `recovery_demo.py`로 생성한 5차 검증용 복구 결과 |
| `expected_result.md` | SHA-256 검증 결과 문서 |

## 실행 순서

```bash
python3 src/safe_test_encrypt.py tests/test_vectors/sample_plain.txt --force
python3 src/rhysida_file_parser.py tests/test_vectors/sample_plain.txt.rhysida --include-ciphertext -o tests/test_vectors/parser_result.json
python3 src/recovery_demo.py tests/test_vectors/sample_plain.txt.rhysida -o tests/test_vectors/recovered_5th.txt --json
```

## 성공 기준

복구 결과의 `verified` 값이 `true`이고, 원본 파일 SHA-256과 복구 결과 SHA-256이 일치하면 성공으로 판단한다.
