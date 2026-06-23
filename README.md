# 26-1-ASC-Project

## 1. Project Overview

본 프로젝트는 ASC 26-1 프로젝트로, Rhysida 랜섬웨어의 암호화 구조를 리버싱 관점에서 분석하고, 공개 연구 및 KISA 복구 원리에서 설명된 아이디어를 바탕으로 안전한 테스트 파일 환경에서 복호화 파이프라인을 재현하는 것을 목표로 한다.

본 프로젝트의 핵심은 실제 피해 파일 복구를 보장하는 완성형 복구도구를 만드는 것이 아니라, Rhysida의 암호화 흐름을 분석하고 복호화가 가능해지는 조건과 한계를 교육용/분석용 관점에서 정리하는 것이다.

## 2. Project Goal

본 프로젝트의 최종 목표는 다음과 같다.

1. Rhysida 랜섬웨어의 암호화 구조를 리버싱 관점에서 분석한다.
2. 파일 암호화 과정에서 사용되는 PRNG, AES-CTR, RSA-4096의 역할을 정리한다.
3. 안전한 테스트 파일 환경에서 파일 구조 분석 도구와 복호화 재현 demo를 구현한다.
4. 복구 가능 조건과 한계를 문서화한다.
5. 최종 보고서 형태로 정적 분석, 동적 분석, 암호화 분석, 복호화 로직 설계, IOC, 한계를 통합한다.

## 3. Project Scope

본 프로젝트는 다음 범위 안에서 수행한다.

* Rhysida 암호화 구조 분석
* 정적 분석 기반 바이너리 구조 및 암호화 루틴 분석
* 동적 분석 기반 파일 행위, 프로세스 행위, 확장자 변경, 로그 관찰
* 안전한 테스트 파일 기반 복호화 파이프라인 재현
* 복구 가능 조건 및 한계 정리
* IOC 및 행위 기반 특징 정리

본 프로젝트는 다음 작업을 목표로 하지 않는다.

* 실제 피해 파일 복구 보장
* KISA 공식 복구도구 복제
* 실제 운영 환경에서 악성코드 실행
* 악성코드 배포 또는 악용 가능한 형태의 공격 도구 제작
* 랜섬웨어 감염 기능 구현

## 4. Rhysida Encryption Model

본 프로젝트에서 정리하는 Rhysida의 암호화 흐름은 다음과 같다.

```text
srand(time(NULL))
→ LibTomCrypt ChaCha20 PRNG 초기화
→ 80바이트 난수 생성
→ 앞 32바이트를 AES-CTR key로 사용
→ 다음 16바이트를 AES-CTR IV로 사용
→ 파일 본문을 AES-CTR로 암호화
→ AES key와 IV를 RSA-4096으로 암호화
→ 암호화된 key/IV 데이터를 파일 끝에 append
→ 파일 확장자를 .rhysida로 변경
```

이 구조에서 중요한 점은 ChaCha20이 파일 본문을 직접 암호화하는 용도가 아니라는 것이다. ChaCha20은 PRNG 역할로 사용되어 AES-CTR에 필요한 key와 IV를 생성하는 데 관여한다. 실제 파일 본문 암호화는 AES-CTR 방식으로 수행되며, AES key와 IV는 RSA-4096으로 보호되어 파일 끝부분에 저장된다.

## 5. Team Roles

| 이름  | 역할                                                | 담당 산출물                                                                                |
| --- | ------------------------------------------------- | ------------------------------------------------------------------------------------- |
| 최민혁 | 팀장, 암호화 알고리즘 분석, 복호화 로직 설계, 최종 보고서 통합, WBS 관리     | `crypto_analysis.md`, `decrypt_logic_design.md`, 최종 보고서                               |
| 이지원 | Rhysida 정적 분석, 바이너리 구조 분석, 암호화 루틴 위치 및 흐름 정리      | `static_analysis.md`, `binary_structure_notes.md`                                     |
| 안시후 | 안전한 테스트 파일 환경 구성, 파일 구조 parser, 복호화 재현 demo 코드 작성 | `rhysida_file_parser.py`, `safe_test_encrypt.py`, `recovery_demo.py`, `src/README.md` |
| 최지우 | 동적 분석 계획 수립, 격리 환경 실행 모니터링, 파일/프로세스/확장자/행위 관찰 정리  | `dynamic_analysis.md`, `monitoring_plan.md`                                           |

## 6. Deliverables

최종 산출물은 다음과 같다.

```text
README.md
docs/project_scope.md
docs/static_analysis.md
docs/binary_structure_notes.md
docs/dynamic_analysis.md
docs/monitoring_plan.md
docs/crypto_analysis.md
docs/parser_design.md
docs/decrypt_logic_design.md
docs/decrypt_pipeline.md
docs/recovery_demo_design.md
docs/limitations.md
docs/ioc.md
docs/final_report_outline.md
src/README.md
src/rhysida_file_parser.py
src/safe_test_encrypt.py
src/recovery_demo.py
```

## 7. Current Document Structure

현재 문서 구조는 다음과 같이 구성한다.

```text
docs/
├── crypto_analysis.md
├── decrypt_logic_design.md
├── decrypt_pipeline.md
├── dynamic_analysis.md
├── ioc.md
├── limitations.md
└── static_analysis.md
```

향후 코드 산출물은 다음 구조로 정리하는 것을 목표로 한다.

```text
src/
├── README.md
├── rhysida_file_parser.py
├── safe_test_encrypt.py
└── recovery_demo.py
```

## 8. Safety Policy

본 프로젝트는 교육용/분석용 프로젝트이며, 실제 악성 행위를 수행하지 않는다.

분석 및 demo 구현 시 다음 원칙을 지킨다.

1. 실제 피해 파일을 대상으로 복구를 보장하지 않는다.
2. 실제 악성코드를 실행 가능한 형태로 배포하지 않는다.
3. 테스트 파일은 안전한 샘플 파일만 사용한다.
4. 복호화 demo는 공개 원리 기반의 재현 구조로만 작성한다.
5. 원본 파일을 덮어쓰지 않고 별도 출력 경로를 사용한다.
6. KISA 공식 복구도구를 복제하지 않는다.

## 9. Expected Final Result

최종적으로 본 프로젝트는 다음 결과물을 제시한다.

1. Rhysida 암호화 구조 분석 문서
2. 정적 분석 및 동적 분석 결과 문서
3. 파일 구조 parser 설계 및 구현
4. 안전한 테스트 파일 기반 복호화 재현 demo
5. 복구 가능 조건 및 한계 문서
6. IOC 및 행위 기반 특징 정리
7. 최종 발표 및 보고서

## 10. Summary

본 프로젝트는 Rhysida 랜섬웨어의 암호화 구조를 분석하고, ChaCha20 PRNG, AES-CTR, RSA-4096의 역할을 구분하여 복호화 가능 조건을 정리하는 것을 목표로 한다. 최종 산출물은 실제 피해 복구도구가 아니라, 안전한 테스트 파일 환경에서 복호화 파이프라인을 재현하고 그 조건과 한계를 설명하는 교육용/분석용 결과물이다.
