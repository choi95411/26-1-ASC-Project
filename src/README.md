# 안전한 복호화 demo 소스 설명

## 1. 목적

이 디렉토리는 ASC Rhysida 분석 프로젝트의 안전한 복호화 demo 소스코드를 정리하는 공간이다.

현재 구현된 핵심 파일은 `recovery_demo.py`이다. 이 코드는 실제 피해 파일 복구를 보장하는 복구도구가 아니라, 직접 만든 dummy 테스트 파일을 대상으로 AES-CTR 복호화 흐름을 확인하기 위한 교육용/분석용 demo이다.

## 2. 안전 범위

`recovery_demo.py`는 다음 안전 범위 안에서만 동작한다.

- 사용자가 명시한 단일 파일만 처리한다.
- 디렉토리 전체를 순회하지 않는다.
- 파일을 삭제하지 않는다.
- 입력 파일을 덮어쓰지 않는다.
- 출력 파일이 이미 있으면 덮어쓰지 않고 중단한다.
- 프로젝트에서 직접 만든 dummy 테스트 벡터만 대상으로 한다.
- 감염, 지속성 유지, 전파, 백업 삭제, 랜섬노트 생성 기능을 구현하지 않는다.

## 3. 현재 소스 파일

| 파일 | 역할 |
| --- | --- |
| `recovery_demo.py` | dummy `.rhysida` 테스트 파일을 읽고, 테스트 metadata에서 AES key/IV를 추출한 뒤 AES-CTR로 암호화 본문을 복호화한다. metadata에 원본 SHA-256이 있으면 복구 결과와 비교한다. |

추후 연결 예정인 파일은 다음과 같다.

| 예정 파일 | 역할 |
| --- | --- |
| `safe_test_encrypt.py` | 안전한 dummy 원본 파일을 AES-CTR로 암호화하고 테스트용 `.rhysida` 파일을 생성한다. |
| `rhysida_file_parser.py` | 암호화된 본문 영역과 테스트 footer metadata 영역을 분리한다. |

## 4. 입력 테스트 파일 구조

`recovery_demo.py`는 다음과 같은 테스트 전용 파일 구조를 입력으로 사용한다.

```text
ciphertext
+ ASC_RHYSIDA_TEST_FOOTER_V1\n
+ metadata 길이, 8바이트, big endian
+ metadata JSON, UTF-8
```

metadata JSON에는 최소한 AES key와 IV가 포함되어야 한다.

```json
{
  "aes_key": "32바이트 AES key, hex 또는 base64",
  "aes_iv": "16바이트 AES IV, hex 또는 base64",
  "plaintext_sha256": "원본 dummy 파일의 SHA-256",
  "original_name": "sample_plain.txt"
}
```

## 5. 실행 방법

프로젝트 루트에서 다음 명령을 실행한다.

```bash
python3 docs/src/recovery_demo.py docs/tests/test_vectors/sample_plain.txt.rhysida --json
```

기본 출력 파일이 이미 존재하면 다른 출력 경로를 지정한다.

```bash
python3 docs/src/recovery_demo.py docs/tests/test_vectors/sample_plain.txt.rhysida -o docs/tests/test_vectors/recovered_wsl_test.txt --json
```

## 6. 성공 조건

복호화 demo 실행 결과 JSON에 다음 값이 포함되면 성공으로 판단한다.

```json
{
  "verified": true
}
```

이는 복구 결과 파일의 SHA-256이 테스트 metadata에 저장된 원본 SHA-256과 일치한다는 의미이다.

## 7. 현재 한계

현재 단계에서는 `recovery_demo.py`의 복호화 기능을 단독으로 검증하였다. `safe_test_encrypt.py`, `rhysida_file_parser.py`와 연결한 전체 파이프라인 통합 검증은 아직 완료되지 않았으며, 다음 차수 작업으로 남겨둔다.

