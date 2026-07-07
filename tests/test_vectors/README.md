# 테스트 벡터 설명

## 1. 목적

이 디렉토리는 AES-CTR 복호화 demo 검증을 위한 안전한 dummy 테스트 파일을 보관한다.

여기에 포함된 파일은 실제 악성 샘플이나 실제 피해 파일이 아니다. 프로젝트 파이프라인을 검증하기 위해 직접 생성한 테스트 파일이다.

## 2. 현재 파일 목록

| 파일 | 설명 |
| --- | --- |
| `sample_plain.txt` | 안전한 dummy 원본 파일 |
| `sample_plain.txt.rhysida` | AES-CTR로 암호화하고 프로젝트 전용 테스트 footer를 붙인 dummy 암호화 파일 |
| `recovered_sample_plain.txt` | `recovery_demo.py`로 생성한 복구 결과 파일 |
| `expected_result.md` | SHA-256 검증 결과와 예상 동작을 정리한 문서 |

## 3. 테스트 footer 구조

dummy 암호화 파일은 다음과 같은 테스트 전용 구조를 사용한다.

```text
ciphertext
+ ASC_RHYSIDA_TEST_FOOTER_V1\n
+ metadata 길이, 8바이트, big endian
+ metadata JSON, UTF-8
```

이 footer는 실제 암호화 파일의 정확한 구조를 그대로 복제했다는 의미가 아니다. 본 프로젝트에서 안전한 테스트용 암호화 코드, parser, 복호화 demo를 연결하기 위해 정의한 통제된 테스트 형식이다.

## 4. metadata 필드

현재 metadata JSON은 다음 필드를 사용한다.

| 필드 | 의미 |
| --- | --- |
| `format` | 테스트 footer 형식 식별자 |
| `aes_key` | hex로 인코딩한 AES-CTR key |
| `aes_iv` | hex로 인코딩한 AES-CTR IV |
| `plaintext_sha256` | 원본 dummy 파일의 SHA-256 |
| `ciphertext_sha256` | footer를 제외한 암호화 본문 영역의 SHA-256 |
| `original_name` | 원본 dummy 파일명 |
| `note` | 교육용 dummy 테스트 벡터임을 설명하는 안전성 메모 |

## 5. 검증 명령

프로젝트 루트에서 다음 명령을 실행한다.

```bash
python3 docs/src/recovery_demo.py docs/tests/test_vectors/sample_plain.txt.rhysida --json
```

`recovered_sample_plain.txt`가 이미 존재하면 다른 출력 경로를 지정한다.

```bash
python3 docs/src/recovery_demo.py docs/tests/test_vectors/sample_plain.txt.rhysida -o docs/tests/test_vectors/recovered_wsl_test.txt --json
```

## 6. 예상 결과

원본 dummy 파일과 복구 결과 파일의 SHA-256이 일치해야 한다.

```text
원본 SHA-256 == 복구 결과 SHA-256
```

현재 dummy 원본 파일의 SHA-256은 다음과 같다.

```text
f2ae3733f6cc2d29ca43ab2ffaf50eb38a461ff31015a703f310a8a97bf7a429
```

## 7. 남은 통합 작업

현재 테스트 벡터는 `recovery_demo.py`의 footer 형식에 맞춰 직접 생성하였다. `safe_test_encrypt.py`, `rhysida_file_parser.py`가 준비되면 세 모듈을 연결해 전체 파이프라인 통합 검증을 수행해야 한다.

