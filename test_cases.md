# 6차 성공/실패 케이스 테스트 결과

## 테스트 개요

5차에서 연결한 `safe_test_encrypt.py` → `rhysida_file_parser.py` → `recovery_demo.py` 파이프라인을 대상으로,
정상 입력뿐 아니라 잘못된 입력·손상된 파일·조작된 metadata를 넣었을 때 각 스크립트가 어떻게 동작하는지 검증하였다.
5차 보고서의 다음 회차 목표(footer 손상, key/IV 불일치, 잘못된 입력 파일 등 실패 케이스 테스트)에 따른 작업이다.

모든 테스트는 `tests/test_vectors/sample_plain.txt`를 원본으로 사용하는 안전한 dummy 파일 기반이며,
실제 악성 샘플이나 피해 파일은 사용하지 않았다.

## 테스트 결과 요약

| # | 케이스 | 실행 스크립트 | 결과 | exit code |
| --- | --- | --- | --- | --- |
| 1 | 정상 흐름 (암호화 → 파싱 → 복호화 → 검증) | `safe_test_encrypt.py` → `rhysida_file_parser.py` → `recovery_demo.py` | `verified: true` | 0 |
| 2 | 존재하지 않는 입력 파일 | `safe_test_encrypt.py nonexistent.txt` | `[FAIL] input file not found` | 1 |
| 3 | 출력 파일이 이미 존재 (`--force` 미사용) | `safe_test_encrypt.py sample_plain.txt -o case1.rhysida` | `[FAIL] output already exists` | 1 |
| 4 | footer(magic) 손상 — 파일 뒷부분 절단 | `rhysida_file_parser.py case4_corrupted.rhysida` | `[FAIL] test footer magic not found` | 1 |
| 5 | metadata의 `aes_key`를 다른 값으로 조작 | `recovery_demo.py case5_wrongkey.rhysida` | 에러 없이 실행, `verified: false` | 0 |
| 6 | `aes_key` 길이 자체가 잘못됨 (3바이트) | `recovery_demo.py case6_shortkey.rhysida` | `[FAIL] aes_key must be 32 bytes, got 3` | 1 |

## 케이스별 상세

### Case 1. 정상 성공 케이스

```bash
python3 src/safe_test_encrypt.py tests/test_vectors/sample_plain.txt -o case1.rhysida --force
python3 src/rhysida_file_parser.py case1.rhysida -o case1_parsed.json
python3 src/recovery_demo.py case1.rhysida -o case1_recovered.txt --json
```

```json
{
  "recovered_sha256": "aa0ca76da0b2cb4a23a7f432d5a28635fe0cfa251934e65ff5568c7e4616af7a",
  "expected_sha256": "aa0ca76da0b2cb4a23a7f432d5a28635fe0cfa251934e65ff5568c7e4616af7a",
  "verified": true
}
```

원본 SHA-256과 복구 결과 SHA-256이 일치하여 파이프라인 전 구간이 정상 연결됨을 확인하였다.

### Case 2. 존재하지 않는 입력 파일

```bash
python3 src/safe_test_encrypt.py tests/test_vectors/nonexistent.txt -o case2.rhysida --force
```

```
[FAIL] input file not found: tests/test_vectors/nonexistent.txt
```

입력 파일 존재 여부를 실행 초기에 검사하여, 이후 단계로 진행하지 않고 즉시 실패 처리함을 확인하였다.

### Case 3. 출력 파일 덮어쓰기 방지

```bash
python3 src/safe_test_encrypt.py tests/test_vectors/sample_plain.txt -o case1.rhysida
```

```
[FAIL] output already exists: case1.rhysida
```

`--force` 옵션 없이는 기존 결과 파일을 덮어쓰지 않도록 방어 로직이 동작함을 확인하였다.

### Case 4. footer(magic) 손상

정상 파일(606 bytes)을 120 bytes로 절단하여 footer의 magic 마커가 잘려나가도록 손상시킨 뒤 파싱을 시도하였다.

```bash
python3 src/rhysida_file_parser.py case4_corrupted.rhysida
```

```
[FAIL] test footer magic not found
```

`rfind`로 magic을 찾지 못하면 즉시 파싱을 중단하여, 손상된 파일을 잘못된 위치에서 파싱하는 것을 방지함을 확인하였다.

### Case 5. key 불일치 (조용한 실패)

metadata 안의 `aes_key` 값만 다른 32바이트 값(`ff`×32)으로 바꿔치기한 뒤 복구를 시도하였다.

```bash
python3 src/recovery_demo.py case5_wrongkey.rhysida -o case5_recovered.txt --json
```

```json
{
  "recovered_sha256": "334b11be5698013d0f34593a350a20c419a9b9d48c56cbf381edde27b0b51276",
  "expected_sha256": "aa0ca76da0b2cb4a23a7f432d5a28635fe0cfa251934e65ff5568c7e4616af7a",
  "verified": false
}
```

**이 케이스는 exit code 0으로 정상 종료되며 예외도 발생하지 않는다.** key 길이 조건(32바이트)은 만족하지만 값이 틀렸기 때문에,
AES-CTR 복호화 자체는 "성공"하지만 전혀 다른 바이트가 나온다. 프로그램은 이를 에러로 취급하지 않고 `verified: false` 필드로만 알려준다.
즉 SHA-256 검증 단계를 확인하지 않고 출력 파일만 저장했다면, 손상된 결과를 정상 복구본으로 오인할 수 있었다.
이는 파이프라인에서 SHA-256 대조 검증이 왜 필수 단계인지 실제로 보여주는 사례다.

### Case 6. key 길이 자체가 잘못됨

metadata의 `aes_key`를 3바이트(`aabbcc`)짜리 값으로 바꾼 뒤 복구를 시도하였다.

```bash
python3 src/recovery_demo.py case6_shortkey.rhysida -o case6_recovered.txt --json
```

```
[FAIL] aes_key must be 32 bytes, got 3
```

`decode_hex_or_b64`의 길이 검증 로직이 AES-256 key 규격(32바이트)에 맞지 않는 값을 미리 걸러내어,
Cipher 객체 생성 단계까지 가지 않고 안전하게 실패함을 확인하였다.

## 결론

- **입력 검증 단계(파일 존재 여부, 출력 덮어쓰기, key/IV 길이)는 모두 명시적인 에러 메시지와 함께 exit code 1로 실패한다.**
- **footer 구조 손상은 magic 탐색 실패로 조기에 걸러진다.**
- **key 값 자체가 틀린 경우(길이는 맞지만 내용이 다른 경우)는 프로그램 레벨에서 에러가 발생하지 않고, 오직 SHA-256 검증(`verified` 필드)으로만 감지된다.** 이는 파이프라인의 유일한 무결성 검증 지점이 SHA-256 대조라는 뜻이며, 향후 개선 시 이 부분에 대한 강조나 이중 검증 로직 추가를 고려할 수 있다.

## 참고

- 테스트에 사용한 조작 파일(`case4_corrupted.rhysida`, `case5_wrongkey.rhysida`, `case6_shortkey.rhysida`)은 모두 `tests/test_vectors/sample_plain.txt.rhysida`를 스크립트로 직접 변형해 생성한 안전한 테스트용 파일이며, 실제 악성 샘플이 아니다.
- 실행 환경: Python 3, `cryptography` 라이브러리
