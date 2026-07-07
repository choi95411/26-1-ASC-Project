# 실행 행위 모니터링 및 분석 계획서 (monitoring_plan.md)

## 1. 문서 목적

본 문서는 Rhysida 랜섬웨어 분석 및 복호화 툴 제작 프로젝트에서 **동적 분석 및 실행 행위 모니터링**을 수행하기 위한 구체적인 방법론과 분석 절차를 규정한다. 복호화 팀의 가설(시간 기반 시드 추정 및 AES-CTR key/IV 재구성)을 검증하고, 복호화 파이프라인에 필요한 핵심 데이터를 적시에 제공하는 것을 목적으로 한다.

---

## 2. 모니터링 및 분석 방법

### 2.1 분석 환경 구성 (인프라 격리)

* **네트워크 격리:** 가상머신(VM) 환경의 네트워크 카드를 `Host-Only` 모드로 고정하여 샘플 유출 및 외부 C2 통신을 차단한다.
* **시간 동기화 해제:** 윈도우 시간 동기화(NTP) 서비스를 중단하고 분석 장비 고유의 타임스탬프를 로깅한다.
* **롤백 시스템:** 샘플 실행 직전의 클린 상태를 가상머신의 스냅샷(Snapshot)으로 저장하여 상시 초기화가 가능하도록 대기한다.

### 2.2 실시간 행위 모니터링 (도구 세팅)

* **Process Monitor (Procmon) 필터 정의:**
* `Process Name` IS `[Rhysida_Sample_Name].exe`
* `Operation` CONTAINS `File` (생성, 수정, 변조 확인)
* `Operation` CONTAINS `Reg` (레지스트리 영속성 및 설정 변조 확인)


* **Process Hacker / Explorer:** Rhysida 프로세스의 스레드 변화와 메모리 공간(상태 변화)을 실시간 관찰한다.
* **x64dbg 디버거:** 바이너리를 로드하고 심볼(Symbol) 또는 주요 API 진입점에 브레이크포인트(BP)를 미리 배치한다.

---

## 3. 핵심 분석 내용 및 절차

### 3.1 PRNG 시드(Seed) 및 시간 정보 분석

복호화 팀의 `srand(time(NULL))` 기반 시드 설정 및 ChaCha20 PRNG 초기화 가설을 검증하기 위한 단계이다.

1. **시간 API 추적:** 디버거에서 `GetSystemTime`, `GetLocalTime`, `GetTickCount`, `QueryPerformanceCounter`에 하드웨어 BP를 설정한다.
2. **시드값 포착:** `srand` 함수 또는 LibTomCrypt 내부 함수가 호출되는 순간의 인자값(RCX/RDI 레지스터 또는 스택)을 캡처하여 당시 시스템 시간(Unix Timestamp)과 대조한다.
3. **로그화:** 호출된 시점의 타임스탬프 값을 밀리초(ms) 단위까지 정밀 기록하여 복호화 팀의 시드 후보 범위를 축소한다.

### 3.2 메모리 내 AES-CTR Key / IV 추출

Rhysida가 ChaCha20 PRNG를 통해 생성한 80바이트 난수 중 앞 48바이트(Key 32바이트 + IV 16바이트)를 메모리에서 직접 확보하는 단계이다.

1. **암호화 중단:** 파일 시스템 변조 함수(`WriteFile`) 또는 암호화 라이브러리(`crypt_encrypt` 등) 호출 직전에 디버거를 일시정지(Suspend) 시킨다.
2. **메모리 스캔 및 덤프:** * ChaCha20 내부 상태 구조체가 담긴 메모리 주소(상수 영역 `expand 32-byte k` 패턴 근처)를 추적한다.
* 해당 시점의 프로세스 메모리를 전체 덤프(.dmp)하여 평문 상태의 Key와 IV를 바이너리 형태로 추출한다.


3. **검증 데이터 제공:** 확보한 키셋을 복호화 팀에 전달하여 `safe_test_encrypt.py` 및 `recovery_demo.py` 모듈이 해당 키로 정상 복호화되는지 교차 검증한다.

### 3.3 파일 행위 및 변조 아티팩트 분석

1. **암호화 메커니즘 검증:** Rhysida가 대용량 파일을 전체 암호화하는지, 혹은 속도 향상을 위해 특정 블록만 건너뛰는 간헐적 암호화(Intermittent Encryption)를 수행하는지 파일 크기별 `WriteFile` 바이트 수를 모니터링한다.
2. **타임스톰핑(Timestomping) 검증:** 확장자가 `.rhysida`로 변경될 때 NTFS `$MFT`상의 파일 수정/액세스 시간이 의도적으로 변조되는지 파악한다. (변조가 없다면 파일 메타데이터의 수정 시간이 암호화 시점 추정의 결정적 단서가 됨).
3. **볼륨 섀도 복사본(VSS) 무력화 로깅:** `vssadmin.exe delete shadows` 프로세스 생성 행위를 모니터링하고 쉘 명령어 인자값을 백업 무력화 IOC 지표로 기록한다.

---

## 4. 최종 결과물 산출 계획

동적 분석 완료 후 복호화 팀원에게 최종 제공할 산출물은 다음과 같다.

| 산출물 파일명 | 포함 데이터 및 역할 | 관련 모듈 (복호화 팀) |
| --- | --- | --- |
| `time_seed_analysis.log` | 최초 실행 타임스탬프 및 PRNG API 리턴값 리스트 | `recovery_demo.py` (시드 범위 축소) |
| `rhysida_key_iv.bin` | x64dbg를 통해 추출한 ChaCha20 PRNG 출력 48바이트 Key/IV 평문 덤프 | `recovery_demo.py` (복호화 파이프라인 검증용) |
| `encryption_policy.json` | 간헐적 암호화 블록 사이즈 및 대상 확장자 필터링 규칙 | `rhysida_file_parser.py` (구조 분석 알고리즘 반영) |
| `rhysida_ioc_sheet.csv` | 생성 레지스트리 경로, 랜섬노트 명명 규칙, Mutex 값 등 | 프로젝트 최종 침해 지표 보고서 |
