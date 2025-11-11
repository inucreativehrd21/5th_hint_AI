"""
교육학적 프롬프트 시스템 (극단적 단순화 버전)
- 학생 코드를 반드시 포함
- 프롬프트 길이 최소화
- 명확한 출력 형식 지시
"""
from typing import Dict, List


class EducationalPromptEngine:
    """교육학 기반 프롬프트 생성 엔진 (단순화 버전)"""
    
    def __init__(self):
        pass
    
    def generate_novice_prompt(self, problem_info: Dict, diagnosis: 'CodeDiagnosis',
                               weak_areas: List[str], chain_context: str, student_code: str) -> str:
        """초급 프롬프트"""
        
        print(f"\n[EducationalPromptEngine] 초급(Novice) 프롬프트 생성")
        print(f"  학생 코드 길이: {len(student_code)} chars")
        print(f"  부족한 영역: {weak_areas}")
        
        return f"""당신은 Python 코딩 교육 전문가입니다. 학생이 코드를 완성할 수 있도록 구체적인 도움을 제공하세요.

## 학생의 현재 코드:
```python
{student_code}
```

## 문제: {problem_info.get('title', 'N/A')}

## 진단 결과:
- 코드 유사도: {diagnosis.similarity:.1f}%
- 문법 오류: {diagnosis.syntax_errors}개
- 논리 오류: {diagnosis.logic_errors}개
- 부족한 영역: {', '.join(weak_areas)}

## 이전 힌트:
{chain_context}

---
## ⚠️ 중요한 규칙:

1. **반드시 아래 형식대로만 출력하세요** (설명, 분석, thinking 등 절대 금지)
2. **구체적인 함수명**을 명시하세요 (예: `input()`, `int()`, `list.append()`)
3. **실행 가능한 코드 예시**를 제공하세요 (1-3줄)
4. **다음 단계**를 명확히 알려주세요

---
## 출력 형식 (이 형식만 출력!):

💡 **핵심**: (한 줄로 무엇을 해야 하는지 - 20자 이내)

📝 **필요한 도구**:
- 함수명1 (예: `input()` - 사용자 입력받기)
- 함수명2 (예: `int()` - 문자열을 정수로 변환)

💻 **코드 예시**:
```python
# 실제 실행 가능한 코드 (1-3줄)
변수명 = 함수명(인자)
```

🎯 **다음 단계**: (이 코드를 어디에 어떻게 사용할지 - 한 줄)

---
## 나쁜 예시 (절대 금지):
❌ "학생은 ~하고 있습니다" (분석 금지)
❌ "진단 결과에서 가장 심각한 문제는" (진단 설명 금지)
❌ "1단계:", "2단계:" (단계별 설명 금지)
❌ "DFS 알고리즘을 사용해" (추상적 개념만 금지)

## 좋은 예시:
✅ 💡 **핵심**: 입력을 받아 리스트에 저장

✅ 📝 **필요한 도구**:
- `input()` - 사용자로부터 한 줄 입력받기
- `int()` - 문자열을 정수로 변환
- `list.append()` - 리스트에 값 추가

✅ 💻 **코드 예시**:
```python
n = int(input())  # 입력 개수
numbers = []  # 빈 리스트 생성
numbers.append(n)  # 리스트에 추가
```

✅ 🎯 **다음 단계**: 이 패턴을 반복문 안에서 사용하세요
"""
    
    def generate_intermediate_prompt(self, problem_info: Dict, diagnosis: 'CodeDiagnosis',
                                    weak_areas: List[str], chain_context: str, student_code: str) -> str:
        """중급 프롬프트"""
        
        print(f"\n[EducationalPromptEngine] 중급(Intermediate) 프롬프트 생성")
        print(f"  학생 코드 길이: {len(student_code)} chars")
        print(f"  부족한 영역: {weak_areas}")
        
        return f"""당신은 Python 코딩 교육 전문가입니다. 학생이 알고리즘을 이해하고 구현할 수 있도록 도와주세요.

## 학생의 현재 코드:
```python
{student_code}
```

## 문제: {problem_info.get('title', 'N/A')}

## 진단 결과:
- 코드 유사도: {diagnosis.similarity:.1f}%
- 문법 오류: {diagnosis.syntax_errors}개
- 논리 오류: {diagnosis.logic_errors}개
- 부족한 영역: {', '.join(weak_areas)}

## 이전 힌트:
{chain_context}

---
## ⚠️ 중요한 규칙:

1. **반드시 아래 형식대로만 출력하세요** (분석, 설명 등 절대 금지)
2. **알고리즘/자료구조 개념**을 명시하세요 (예: DFS, BFS, 스택, 큐)
3. **구체적인 단계**를 제시하세요 (각 단계에서 무엇을 해야 하는지)
4. **초기화 방법**을 알려주세요 (어떤 변수/배열이 필요한지)

---
## 출력 형식 (이 형식만 출력!):

🧠 **개념**: (필요한 알고리즘/자료구조 - 명확하게)

📊 **접근 방법**:
1단계: (무엇을 초기화하는지 - 구체적으로)
2단계: (어떤 작업을 수행하는지 - 명확하게)
3단계: (결과를 어떻게 처리하는지)
4단계: (최종 출력 또는 반환)

💾 **필요한 자료구조**:
- 자료구조1 (예: praise 배열 - 각 직원의 칭찬 점수 저장)
- 자료구조2 (필요시)

---
## 나쁜 예시 (절대 금지):
❌ "학생은 ~하고 있습니다" (분석 금지)
❌ "진단 결과에서" (진단 설명 금지)
❌ "~을 할 수 있는 방법" (모호한 표현 금지)
❌ 구체적 단계 없이 개념만 설명

## 좋은 예시:
✅ 🧠 **개념**: 깊이 우선 탐색 (DFS) 알고리즘

✅ 📊 **접근 방법**:
1단계: 각 직원에게 받은 칭찬 점수를 저장하는 praise 배열을 0으로 초기화합니다
2단계: 각 직원의 칭찬 점수를 상사에게 전파하기 위해 DFS 알고리즘을 적용합니다
3단계: 부하 직원의 칭찬 점수를 모두 합산하여 상사에게 전달합니다
4단계: 모든 직원의 최종 칭찬 점수를 출력합니다

✅ 💾 **필요한 자료구조**:
- praise 배열 - 각 직원이 받은 총 칭찬 점수
- graph - 상사-부하 관계를 나타내는 트리 구조
"""
    
    def generate_advanced_prompt(self, problem_info: Dict, diagnosis: 'CodeDiagnosis',
                                weak_areas: List[str], chain_context: str, student_code: str) -> str:
        """고급 프롬프트"""
        
        print(f"\n[EducationalPromptEngine] 고급(Advanced) 프롬프트 생성")
        print(f"  학생 코드 길이: {len(student_code)} chars")
        print(f"  부족한 영역: {weak_areas}")
        
        return f"""당신은 Python 코딩 교육 전문가입니다. 소크라테스식 질문으로 학생 스스로 깨닫게 하세요.

## 학생의 현재 코드:
```python
{student_code}
```

## 문제: {problem_info.get('title', 'N/A')}

## 진단 결과:
- 코드 유사도: {diagnosis.similarity:.1f}%
- 문법 오류: {diagnosis.syntax_errors}개
- 논리 오류: {diagnosis.logic_errors}개
- 부족한 영역: {', '.join(weak_areas)}

## 이전 힌트:
{chain_context}

---
## ⚠️ 중요한 규칙:

1. **반드시 아래 형식대로만 출력하세요** (분석, 설명 절대 금지)
2. **중립적으로 관찰**하세요 (평가 금지)
3. **열린 질문**을 하세요 (정답 암시 금지)
4. **함수명/코드 예시 절대 금지**

---
## 출력 형식 (이 형식만 출력!):

🔍 **관찰**: (학생 코드의 패턴을 중립적으로 1문장 - 평가 금지)

❓ **질문**: (스스로 생각하게 만드는 열린 질문 - 1개만)

---
## 나쁜 예시 (절대 금지):
❌ "학생은 ~하고 있습니다" (분석 금지)
❌ "진단 결과에서" (진단 설명 금지)
❌ "DFS를 사용하면" (함수/알고리즘명 암시 금지)
❌ "for문을 쓰는 게 어떨까요?" (정답 암시 금지)

## 좋은 예시:
✅ 🔍 **관찰**: 현재 코드는 각 경우를 개별적으로 처리하고 있습니다

✅ ❓ **질문**: 만약 처리해야 할 경우가 1000개라면, 지금 방식으로 계속 진행하시겠습니까?
"""
