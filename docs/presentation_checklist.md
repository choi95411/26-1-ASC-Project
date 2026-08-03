# 최종 발표 체크리스트

## 발표 흐름

```text
프로젝트 목적
-> Rhysida 암호화 구조
-> 정적 분석 결과
-> 동적 분석/모니터링 계획
-> 안전한 복호화 demo 구조
-> SHA-256 검증 결과
-> 한계 및 결론
```

## demo 실행 명령

```bash
python3 -m pip install -r src/requirements.txt
python3 src/safe_test_encrypt.py tests/test_vectors/sample_plain.txt --force
python3 src/rhysida_file_parser.py tests/test_vectors/sample_plain.txt.rhysida --include-ciphertext -o tests/test_vectors/parser_result.json
python3 src/recovery_demo.py tests/test_vectors/sample_plain.txt.rhysida -o tests/test_vectors/recovered_demo.txt --json
```

## 발표에서 보여줄 핵심 결과

- `verified: true`
- 원본 SHA-256과 복구 결과 SHA-256 일치
- 암호화 본문과 footer metadata 분리 결과
- 실제 피해 파일 복구 보장이 아니라 dummy 파일 기반 검증임을 명시

## 준비할 자료

- 파이프라인 도식
- 실행 명령 캡처 또는 로그
- SHA-256 비교 결과
- 코드 파일 역할 표
- 한계 조건 슬라이드

## 시연 실패 대비

- `tests/test_vectors/expected_result.md`의 검증 결과를 캡처한다.
- `parser_result.json` 예시를 준비한다.
- 복구 성공 JSON 출력 예시를 발표 자료에 포함한다.
