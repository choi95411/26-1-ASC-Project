# 테스트 예상 결과

## 1. 테스트 개요

이 문서는 안전한 복호화 demo의 현재 dummy 테스트 벡터 검증 결과를 정리한다.

이번 테스트는 AES-CTR로 암호화한 dummy 파일을 `recovery_demo.py`로 복호화할 수 있는지 확인하는 것을 목적으로 한다. 복호화에 필요한 AES key, IV, 원본 SHA-256은 테스트 전용 footer metadata에 저장되어 있다.

## 2. 테스트 파일

| 항목 | 파일 |
| --- | --- |
| 원본 dummy 파일 | `docs/tests/test_vectors/sample_plain.txt` |
| dummy 암호화 파일 | `docs/tests/test_vectors/sample_plain.txt.rhysida` |
| 복구 결과 파일 | `docs/tests/test_vectors/recovered_sample_plain.txt` |
| 복호화 모듈 | `docs/src/recovery_demo.py` |

## 3. SHA-256 값

| 항목 | SHA-256 |
| --- | --- |
| 원본 파일 | `f2ae3733f6cc2d29ca43ab2ffaf50eb38a461ff31015a703f310a8a97bf7a429` |
| 복구 결과 파일 | `f2ae3733f6cc2d29ca43ab2ffaf50eb38a461ff31015a703f310a8a97bf7a429` |
| footer가 포함된 dummy 암호화 파일 | `3d17081ba1c8db0b0eb53b793c7477f8f33e64699274efd4b61c8119c3b86352` |
| footer를 제외한 암호화 본문 | `431795363a665756b4b7dbf231b0c83019d96e005f4faa5cc04d1fe61892480e` |

## 4. 실행 명령

프로젝트 루트에서 다음 명령을 실행한다.

```bash
python3 docs/src/recovery_demo.py docs/tests/test_vectors/sample_plain.txt.rhysida --json
```

기본 출력 파일이 이미 존재하면 다음처럼 다른 출력 경로를 지정한다.

```bash
python3 docs/src/recovery_demo.py docs/tests/test_vectors/sample_plain.txt.rhysida -o docs/tests/test_vectors/recovered_wsl_test.txt --json
```

## 5. 확인된 결과

`recovery_demo.py` 실행 결과 다음 검증 결과를 확인하였다.

```json
{
  "recovered_sha256": "f2ae3733f6cc2d29ca43ab2ffaf50eb38a461ff31015a703f310a8a97bf7a429",
  "expected_sha256": "f2ae3733f6cc2d29ca43ab2ffaf50eb38a461ff31015a703f310a8a97bf7a429",
  "verified": true,
  "bytes_recovered": 111
}
```

## 6. 해석

현재 dummy 테스트 벡터를 통해 다음 사항을 확인하였다.

- 프로젝트 전용 테스트 footer를 읽을 수 있다.
- footer metadata에서 AES key와 IV를 추출할 수 있다.
- 암호화된 본문을 AES-CTR로 복호화할 수 있다.
- 복구 결과를 별도 파일로 저장할 수 있다.
- 원본 SHA-256과 복구 결과 SHA-256을 비교해 복호화 성공 여부를 검증할 수 있다.

## 7. 남은 작업

이번 결과는 `recovery_demo.py`의 단독 검증 결과이다. `safe_test_encrypt.py`, `rhysida_file_parser.py`와 연결한 전체 파이프라인 통합 검증은 아직 완료되지 않았다. 해당 모듈이 준비되면 동일한 SHA-256 기준으로 end-to-end 검증을 수행할 예정이다.

