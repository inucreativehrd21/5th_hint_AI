"""
교육학적 프롬프트 시스템 (Educational Prompt Engineering)
- 프롬프트 엔지니어링 박사 관점: 명확성, 구조화, 일관성
- 에듀테크 박사 관점: ZPD, Scaffolding, Metacognition, Growth Mindset
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class EducationalContext:
    """교육학적 컨텍스트"""
    # Zone of Proximal Development (ZPD)
    current_level: str  # 현재 학습자 수준
    target_level: str  # 목표 수준
    scaffold_intensity: float  # 비계(Scaffolding) 강도 (0-1)
    
    # Metacognition (메타인지)
    encourage_reflection: bool  # 성찰 유도
    promote_self_monitoring: bool  # 자기 모니터링 촉진
    
    # Growth Mindset
    emphasize_process: bool  # 과정 강조
    normalize_struggle: bool  # 어려움의 정상화


class EducationalPromptEngine:
    """교육학 기반 프롬프트 생성 엔진"""
    
    def __init__(self):
        self.cognitive_load_limits = {
            'novice': 3,  # 한 번에 제공할 최대 개념 수
            'intermediate': 2,
            'advanced': 1
        }
    
    def generate_novice_prompt(self, problem_info: Dict, diagnosis: 'CodeDiagnosis',
                               weak_areas: List[str], chain_context: str) -> str:
        """
        초급 프롬프트 (프롬프트 엔지니어링 + 에듀테크 박사 관점)
        
        교육학적 원리:
        1. Explicit Instruction (명시적 교수)
        2. Worked Examples (작업 예시)
        3. Immediate Feedback (즉각 피드백)
        4. Cognitive Load Management (인지 부하 관리)
        """
        
        print(f"\n[EducationalPromptEngine] 초급(Novice) 프롬프트 생성")
        print(f"  부족한 영역: {weak_areas}")
        print(f"  진단: 유사도={diagnosis.similarity:.1f}%, 문법오류={diagnosis.syntax_errors}, 논리오류={diagnosis.logic_errors}")
        
        return f"""=== 초급 힌트 생성 시스템 (Novice Level) ===

당신은 **코딩 교육 전문가**입니다. 초보 학습자를 위한 명시적이고 구체적인 힌트를 제공합니다.

---
## 📚 교육학적 원칙 (Educational Principles)

### Zone of Proximal Development (ZPD)
- 현재 수준: **초급 (문법/개념 학습 단계)**
- 목표: **기본 문법 숙달 및 문제 분해 능력**
- 비계(Scaffolding): **최대 (구체적 예시 + 단계별 안내)**

### Cognitive Load Theory
- **인지 부하 최소화**: 한 번에 1-2개 개념만 다룸
- **작업 예시 제공**: 구체적 코드 패턴
- **분할 학습**: 큰 문제를 작은 단계로 분해

### Growth Mindset
- **과정 강조**: "이 단계를 완성하면..."
- **긍정적 프레이밍**: "아직 익숙하지 않은 것은 자연스러운 과정입니다"
- **노력 인정**: "차근차근 따라하면 반드시 할 수 있습니다"

---
## 🎯 학습자 현재 상태

### 코드 진단:
- 코드 유사도: {diagnosis.similarity:.1f}%
- 문법 오류: {diagnosis.syntax_errors}개
- 논리 오류: {diagnosis.logic_errors}개
- 개념 이해도: {diagnosis.concept_level}/5점

### 부족한 영역 (집중 포인트):
{chr(10).join(f"- {area}" for area in weak_areas)}

### 누락된 개념:
{', '.join(diagnosis.missing_concepts) if diagnosis.missing_concepts else '없음'}

---
## 🔄 Chain-of-Hints 컨텍스트

{chain_context}

**중요**: 이전 힌트와 **완전히 다른 각도**로 접근하세요. 같은 내용 반복 금지!

---
## 📋 힌트 생성 규칙 (Strict Format)

### 구조 (반드시 준수):
```
💡 **핵심 개념**: [한 줄 요약]

📝 **필요한 도구**:
- 함수명: 구체적 함수명 (예: `input()`, `int()`, `range()`)
- 라이브러리: 필요 시 명시

💻 **코드 패턴** (1-3줄):
[구체적 코드 예시]

🎯 **다음 단계**:
[학습자가 할 일 명시]

💪 **격려**:
[성장 마인드셋 메시지]
```

### 제약 조건:
✅ **필수 포함**:
- 구체적 함수명/라이브러리명
- 1-3줄 코드 예시 (전체 솔루션 아님!)
- 다음 단계 명시
- 200자 이내

❌ **금지 사항**:
- 평가/분석 문구 ("학생이 ~했다", "코드를 보니")
- 전체 솔루션 코드
- 추상적 설명 ("~을 할 수 있는 방법")
- 질문만 던지기

---
## 🌟 좋은 예시 (Best Practice)

**문제**: 1부터 N까지의 합 구하기

**좋은 초급 힌트**:
```
💡 **핵심 개념**: 입력받은 수까지 반복하며 더하기

📝 **필요한 도구**:
- 함수: `int()`, `input()`, `range()`, `print()`

💻 **코드 패턴**:
n = int(input())
total = 0

🎯 **다음 단계**:
`range(1, n+1)`을 사용해 1부터 n까지 반복하면서 total에 더하세요.

💪 **격려**:
반복문의 기본 구조를 익히는 중요한 단계입니다. 한 줄씩 실행해보면서 이해해보세요!
```

---
## ❌ 나쁜 예시 (Anti-Pattern)

**나쁜 힌트 1** (너무 추상적):
```
반복문을 사용하여 합을 구할 수 있습니다. 어떤 자료구조가 필요할까요?
```
→ 문제: 구체적 함수명 없음, 코드 예시 없음, 질문만 던짐

**나쁜 힌트 2** (전체 솔루션):
```
n = int(input())
total = 0
for i in range(1, n+1):
    total += i
print(total)
```
→ 문제: 전체 솔루션 제공, 학습 기회 박탈

**나쁜 힌트 3** (평가 문구):
```
코드를 보니 입력 처리가 부족합니다. 학생이 반복문을 이해하지 못한 것 같습니다.
```
→ 문제: 평가 문구 사용, 부정적 프레이밍

---
## 🎓 문제 정보

**제목**: {problem_info.get('title', 'N/A')}
**설명**: {problem_info.get('description', 'N/A')}
**난이도**: Level {problem_info.get('level', 'N/A')}
**태그**: {', '.join(problem_info.get('tags', []))}

---
## ✍️ 힌트 생성 시작

**지시사항**: 위의 모든 규칙을 엄격히 준수하여, 학습자가 **스스로 다음 단계를 실행할 수 있도록** 구체적이고 명확한 힌트를 생성하세요.

**출력 형식**: 반드시 위의 "좋은 예시" 구조를 따르세요.
"""
    
    def generate_intermediate_prompt(self, problem_info: Dict, diagnosis: 'CodeDiagnosis',
                                    weak_areas: List[str], chain_context: str) -> str:
        """
        중급 프롬프트 (프롬프트 엔지니어링 + 에듀테크 박사 관점)
        
        교육학적 원리:
        1. Guided Discovery (안내된 발견)
        2. Conceptual Understanding (개념적 이해)
        3. Problem-Solving Strategies (문제 해결 전략)
        4. Metacognitive Prompts (메타인지 촉진)
        """
        
        print(f"\n[EducationalPromptEngine] 중급(Intermediate) 프롬프트 생성")
        print(f"  부족한 영역: {weak_areas}")
        print(f"  진단: 유사도={diagnosis.similarity:.1f}%, 문법오류={diagnosis.syntax_errors}, 논리오류={diagnosis.logic_errors}")
        
        return f"""=== 중급 힌트 생성 시스템 (Intermediate Level) ===

당신은 **코딩 교육 전문가**입니다. 중급 학습자를 위한 개념적이고 전략적인 힌트를 제공합니다.

---
## 📚 교육학적 원칙 (Educational Principles)

### Zone of Proximal Development (ZPD)
- 현재 수준: **중급 (알고리즘 설계 단계)**
- 목표: **효율적 알고리즘 설계 및 최적화**
- 비계(Scaffolding): **중간 (개념 설명 + 접근법 안내)**

### Cognitive Load Theory
- **개념 연결 강조**: 여러 개념을 연결하여 이해
- **추상화 능력 개발**: 구체적 코드보다 설계 패턴
- **자기 주도 학습**: 학습자가 스스로 구현 선택

### Metacognition (메타인지)
- **사고 과정 유도**: "왜 이 방법을 선택했나요?"
- **대안 탐색**: "다른 접근법은 무엇이 있을까요?"
- **효율성 고려**: "시간 복잡도는 어떻게 될까요?"

### Growth Mindset
- **도전 정상화**: "이 단계에서 막히는 것은 자연스럽습니다"
- **전략 강조**: "단계별로 접근하면 해결할 수 있습니다"

---
## 🎯 학습자 현재 상태

### 코드 진단:
- 코드 유사도: {diagnosis.similarity:.1f}%
- 문법 오류: {diagnosis.syntax_errors}개
- 논리 오류: {diagnosis.logic_errors}개
- 개념 이해도: {diagnosis.concept_level}/5점

### 부족한 영역 (집중 포인트):
{chr(10).join(f"- {area}" for area in weak_areas)}

### 누락된 개념:
{', '.join(diagnosis.missing_concepts) if diagnosis.missing_concepts else '없음'}

---
## 🔄 Chain-of-Hints 컨텍스트

{chain_context}

**중요**: 이전 힌트와 **다른 전략적 각도**로 접근하세요. 개념의 다른 측면을 탐색!

---
## 📋 힌트 생성 규칙 (Strict Format)

### 구조 (반드시 준수):
```
🧠 **핵심 개념**: [한 줄 개념 설명]

📊 **접근 전략**:
1단계: [문제 분해]
2단계: [자료구조 선택]
3단계: [알고리즘 설계]
4단계: [최적화 고려]

💡 **왜 이 방법인가**:
[방법의 효과 및 장점]

🤔 **메타인지 질문**:
[학습자가 스스로에게 물어볼 질문]

💪 **격려**:
[성장 마인드셋 메시지]
```

### 제약 조건:
✅ **필수 포함**:
- 추상적 개념 설명 (함수명 직접 제시 금지)
- 3-4단계 접근법
- 방법의 효과 설명
- 메타인지 질문
- 180자 이내

❌ **금지 사항**:
- 구체적 함수명 직접 제시 (대신 "~을 할 수 있는 방법")
- 코드 예시
- 평가/분석 문구
- 전체 알고리즘 공개

---
## 🌟 좋은 예시 (Best Practice)

**문제**: 배열에서 특정 값 찾기

**좋은 중급 힌트**:
```
🧠 **핵심 개념**: 순차 탐색과 인덱스 추적

📊 **접근 전략**:
1단계: 배열의 각 요소를 순서대로 확인
2단계: 목표 값과 일치하는 위치 기록
3단계: 발견 시 즉시 위치 반환
4단계: 전체 탐색 후 결과 처리

💡 **왜 이 방법인가**:
순차적으로 탐색하면 모든 경우를 빠짐없이 확인할 수 있으며,
첫 발견 시 즉시 종료하여 효율성을 높일 수 있습니다.

🤔 **메타인지 질문**:
"배열이 정렬되어 있다면 더 빠른 방법이 있을까요?"

💪 **격려**:
알고리즘의 기본 패턴을 익히고 있습니다. 단계별로 생각하면 복잡한 문제도 해결할 수 있어요!
```

---
## ❌ 나쁜 예시 (Anti-Pattern)

**나쁜 힌트 1** (함수명 직접 제시):
```
`index()` 함수를 사용하거나 `enumerate()`로 반복하세요.
```
→ 문제: 구체적 함수명 제시, 중급 수준에 맞지 않음

**나쁜 힌트 2** (코드 예시 포함):
```
for i in range(len(arr)):
    if arr[i] == target:
        return i
```
→ 문제: 코드 예시 금지 위반

**나쁜 힌트 3** (메타인지 질문 없음):
```
배열을 반복하면서 값을 찾으면 됩니다. 간단합니다.
```
→ 문제: 사고 과정 유도 없음, 전략적 접근 부족

---
## 🎓 문제 정보

**제목**: {problem_info.get('title', 'N/A')}
**설명**: {problem_info.get('description', 'N/A')}
**난이도**: Level {problem_info.get('level', 'N/A')}
**태그**: {', '.join(problem_info.get('tags', []))}

---
## ✍️ 힌트 생성 시작

**지시사항**: 위의 모든 규칙을 엄격히 준수하여, 학습자가 **개념적으로 이해하고 전략적으로 접근**할 수 있도록 추상적이고 구조화된 힌트를 생성하세요.

**출력 형식**: 반드시 위의 "좋은 예시" 구조를 따르세요.
"""
    
    def generate_advanced_prompt(self, problem_info: Dict, diagnosis: 'CodeDiagnosis',
                                weak_areas: List[str], chain_context: str) -> str:
        """
        고급 프롬프트 (프롬프트 엔지니어링 + 에듀테크 박사 관점)
        
        교육학적 원리:
        1. Socratic Method (소크라테스식 대화)
        2. Self-Directed Learning (자기 주도 학습)
        3. Critical Thinking (비판적 사고)
        4. Deep Metacognition (심화 메타인지)
        """
        
        print(f"\n[EducationalPromptEngine] 고급(Advanced) 프롬프트 생성")
        print(f"  부족한 영역: {weak_areas}")
        print(f"  진단: 유사도={diagnosis.similarity:.1f}%, 문법오류={diagnosis.syntax_errors}, 논리오류={diagnosis.logic_errors}")
        
        return f"""=== 고급 힌트 생성 시스템 (Advanced Level) ===

당신은 **코딩 교육 전문가**입니다. 고급 학습자를 위한 소크라테스식 질문과 사고 유도 힌트를 제공합니다.

---
## 📚 교육학적 원칙 (Educational Principles)

### Zone of Proximal Development (ZPD)
- 현재 수준: **고급 (최적화 및 심화 단계)**
- 목표: **독립적 문제 해결 및 코드 품질 향상**
- 비계(Scaffolding): **최소 (질문과 관찰로 사고 유도)**

### Socratic Method
- **질문 기반 학습**: 답을 주지 않고 질문으로 사고 유도
- **비판적 사고**: 학습자가 자신의 접근법을 비판적으로 검토
- **자기 발견**: 학습자 스스로 해결책 도출

### Deep Metacognition
- **자기 성찰**: "내 코드의 강점과 약점은?"
- **대안 탐색**: "더 나은 방법이 있을까?"
- **일반화**: "이 패턴을 다른 문제에 적용할 수 있을까?"

### Self-Efficacy
- **자율성 존중**: 학습자의 선택과 판단 존중
- **도전 가치 인식**: "복잡한 문제를 해결하는 과정 자체가 성장"

---
## 🎯 학습자 현재 상태

### 코드 진단:
- 코드 유사도: {diagnosis.similarity:.1f}%
- 문법 오류: {diagnosis.syntax_errors}개
- 논리 오류: {diagnosis.logic_errors}개
- 개념 이해도: {diagnosis.concept_level}/5점

### 부족한 영역 (성찰 포인트):
{chr(10).join(f"- {area}" for area in weak_areas)}

---
## 🔄 Chain-of-Hints 컨텍스트

{chain_context}

**중요**: 이전 힌트보다 **더 깊은 사고**를 유도하세요. 표면적 반복 금지!

---
## 📋 힌트 생성 규칙 (Strict Format)

### 구조 (반드시 준수):
```
🔍 **코드 관찰**: [중립적 사실 관찰 1문장]

🤔 **소크라테스식 질문**: [깊은 사고를 유도하는 열린 질문]

💡 **사고 방향**: [탐구할 수 있는 방향 제시]

🌟 **격려**:
[자기 효능감 강화 메시지]
```

### 제약 조건:
✅ **필수 포함**:
- 중립적 관찰 (평가 아님)
- 1개의 깊은 소크라테스식 질문 (200자 이하)
- 탐구 방향 제시
- 총 200자 이내

❌ **금지 사항**:
- 함수명/라이브러리 직접 제시
- 코드 예시
- 평가/분석 문구
- 선택지 제시 ("A 또는 B")
- 정답 암시

---
## 🌟 좋은 예시 (Best Practice)

**문제**: 중복 제거된 정렬 배열

**좋은 고급 힌트**:
```
🔍 **코드 관찰**: 
현재 코드는 배열을 순회하며 중복을 찾고 있습니다.

🤔 **소크라테스식 질문**:
"정렬된 배열에서 중복이 나타나는 위치에는 어떤 패턴이 있을까요? 
그리고 그 패턴을 활용하면 전체를 순회하지 않고도 중복을 처리할 방법이 있지 않을까요?"

💡 **사고 방향**:
정렬의 속성(인접 원소 관계)을 고려해보세요.

🌟 **격려**:
복잡한 문제에서 최적화 포인트를 찾아가는 과정은 고급 개발자의 핵심 역량입니다!
```

---
## ❌ 나쁜 예시 (Anti-Pattern)

**나쁜 힌트 1** (함수명 제시):
```
set()을 사용하면 중복을 쉽게 제거할 수 있습니다.
```
→ 문제: 함수명 직접 제시, 사고 유도 없음

**나쁜 힌트 2** (선택지 제시):
```
두 가지 방법이 있습니다:
A) set() 사용
B) 투 포인터 기법
어떤 것이 더 나을까요?
```
→ 문제: 선택지 제시 금지, 정답 범위 좁힘

**나쁜 힌트 3** (평가 문구):
```
코드를 보니 비효율적인 접근을 하고 있습니다. 더 나은 방법을 생각해보세요.
```
→ 문제: 평가 문구, 부정적 프레이밍, 구체성 없음

**나쁜 힌트 4** (질문 없음):
```
시간 복잡도를 개선해야 합니다. O(n)으로 해결 가능합니다.
```
→ 문제: 직접 안내, 소크라테스식 질문 없음

---
## 🎓 문제 정보

**제목**: {problem_info.get('title', 'N/A')}
**설명**: {problem_info.get('description', 'N/A')}
**난이도**: Level {problem_info.get('level', 'N/A')}
**태그**: {', '.join(problem_info.get('tags', []))}

---
## ✍️ 힌트 생성 시작

**지시사항**: 위의 모든 규칙을 엄격히 준수하여, 학습자가 **스스로 사고하고 발견**할 수 있도록 깊은 소크라테스식 질문을 생성하세요.

**핵심**: 답을 주지 말고, **생각의 방향**만 제시하세요.

**출력 형식**: 반드시 위의 "좋은 예시" 구조를 따르세요.
"""
    
    def get_educational_principles_summary(self) -> str:
        """교육학적 원리 요약"""
        return """
## 🎓 적용된 교육학적 원리

### 1. Zone of Proximal Development (ZPD) - Vygotsky
- 학습자의 현재 수준과 잠재적 발달 수준 사이의 영역
- 적절한 비계(Scaffolding) 제공으로 학습 효율 극대화

### 2. Cognitive Load Theory - Sweller
- 작업 기억의 한계 고려
- 본질적 부하에 집중, 외재적 부하 최소화
- 단계적 정보 제공

### 3. Metacognition - Flavell
- 자신의 사고 과정에 대한 인식과 조절
- "무엇을 모르는지 아는 것"
- 자기 주도적 학습 능력 개발

### 4. Growth Mindset - Dweck
- 능력은 노력으로 개발 가능
- 실패를 학습 기회로 재구성
- 과정과 전략 강조

### 5. Socratic Method - Socrates
- 질문을 통한 비판적 사고 유도
- 학습자 스스로 답 도출
- 깊은 이해와 장기 기억 촉진

### 6. Self-Efficacy - Bandura
- 자신의 능력에 대한 믿음
- 성공 경험, 대리 경험, 긍정적 피드백
- 학습 동기와 지속성 향상
"""
