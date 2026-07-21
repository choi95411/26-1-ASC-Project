# 🚨 Rhysida Ransomware - Indicators of Compromise (IoC)

> **Document:** Indicators of Compromise Specification (`ioc.md`)  
> **Source:** Static Analysis & Binary Artifact Extraction

---

## 1. 개요 (Overview)

본 문서는 Rhysida 랜섬웨어 바이너리 정적 분석 과정에서 추출된 **침해 지표(Indicators of Compromise, IoC)**를 정리한다. 해당 지표들은 정적 식별, YARA 탐지 룰 작성 및 피해 시스템 검증 용도로 활용된다.

---

## 2. 파일 지표 (File Indicators)

| 항목 | 상세 정보 / 값 | 비고 |
| :--- | :--- | :--- |
| **Target OS** | Windows (x86-64 / PE32+) | 64-bit Executable |
| **MD5 Hash** | `(분석 대상 샘플 MD5 해시값)` | 바이너리 고유 식별자 |
| **SHA-256 Hash** | `(분석 대상 샘플 SHA-256 해시값)` | 무결성 검증 및 샘플 특정 |
| **Encrypted Extension** | `.rhysida` | 암호화 완료 후 변경되는 확장자 |
| **Ransom Note File** | `Rhysida-ReadMe.txt` (또는 `.html`) | 각 디렉토리에 생성되는 랜섬노트 |

---

## 3. 호스트 지표 (Host-based Artifacts)

### 하드코딩 뮤텍스 (Mutex)
Rhysida 바이너리는 중복 실행을 방지하기 위해 정적 코드 내에 특정 뮤텍스 문자열을 포함함.
* **Mutex Name:** `(바이너리 정적 추출 뮤텍스명)`
* **관련 API:** `CreateMutexW`

### 감염 제외 대상 (Exclusion Targets)
바이너리 내 `.data` 섹션에서 하드코딩 형태로 추출된 예외 처리 경로 및 확장자.
* **Excluded Directories:** `\Windows`, `\Program Files`, `\ProgramData`
* **Excluded Extensions:** `.exe`, `.dll`, `.sys`, `.iso`

---

## 4. 네트워크 및 C2 지표 (Network Artifacts)

정적 문자열(Strings) 스캔을 통해 추출된 공격자 관련 주소 및 안내 흔적.

* **Tor Negotiation Site:** `(랜섬노트에 포함된 .onion 주소)`
* **C2 / Contact Email:** `(바이너리 내 추출된 대화용 이메일/주소)`

---

## 5. YARA 탐지 룰 (Static Detection Rule)

정적 분석 지표(하드코딩 문자열 및 PE 헤더 특성)를 기반으로 작성한 YARA 탐지 규칙 예시.

```yara
rule Rhysida_Ransomware_Static {
    meta:
        description = "Detects Rhysida Ransomware based on static string artifacts"
        author = "Security Analysis Team"
        date = "2026-05"
    strings:
        $s1 = ".rhysida" ascii wide
        $s2 = "Rhysida-ReadMe" ascii wide
        $s3 = "LibTomCrypt" ascii wide
    condition:
        uint16(0) == 0x5A4D and all of ($s*)
}
