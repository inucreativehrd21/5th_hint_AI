"""
적응형 힌트 생성 시스템 (리팩토링 V3)
- Chain-of-Hints 구조
- 교육학적 프롬프트 엔진 통합
- 프롬프트 엔지니어링 + 에듀테크 박사 관점
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

from models.educational_prompts import EducationalPromptEngine


@dataclass
class HintRecord:
    """힌트 기록"""
    hint_text: str
    level: str  # novice, intermediate, advanced
    timestamp: datetime
    student_reaction: Optional[str] = None  # 학생의 다음 코드
    was_helpful: Optional[bool] = None


@dataclass
class HintChain:
    """힌트 체인 (누적 힌트 관리)"""
    problem_id: str
    hints: List[HintRecord] = field(default_factory=list)
    
    def add_hint(self, hint: str, level: str, student_reaction: str = None):
        """새 힌트 추가"""
        record = HintRecord(
            hint_text=hint,
            level=level,
            timestamp=datetime.now(),
            student_reaction=student_reaction
        )
        self.hints.append(record)
    
    def get_history_context(self) -> str:
        """이전 힌트 히스토리 문자열"""
        if not self.hints:
            return "없음"
        
        history = []
        for i, h in enumerate(self.hints, 1):
            history.append(f"힌트 {i} ({h.level}): {h.hint_text[:50]}...")
            if h.student_reaction:
                history.append(f"  → 학생 반응: 코드 수정함")
        
        return "\n".join(history)
    
    def should_escalate_level(self) -> bool:
        """난이도 상승 필요 여부"""
        # 3번 이상 같은 난이도 힌트 → 상승 고려
        if len(self.hints) >= 3:
            recent_levels = [h.level for h in self.hints[-3:]]
            if len(set(recent_levels)) == 1:  # 모두 같은 난이도
                return True
        return False


class AdaptivePromptGenerator:
    """적응형 프롬프트 생성기 (리팩토링 V3 - 교육학적 엔진 통합)"""
    
    def __init__(self):
        self.hint_chains: Dict[str, HintChain] = {}
        self.edu_engine = EducationalPromptEngine()  # 교육학적 프롬프트 엔진
    
    def generate_prompt(self, problem_id: str, student_code: str, 
                       solution_code: str, problem_info: Dict,
                       diagnosis: 'CodeDiagnosis', selected_level: str) -> str:
        """
        힌트 내용 자동 구성 (교육학적 프롬프트 엔진 사용)
        - 사용자 선택 난이도 기반
        - 4가지 지표 분석 → 부족한 영역 맞춤 힌트
        - 교육학적 원리 적용 (ZPD, Scaffolding, Metacognition)
        - Chain-of-Hints 컨텍스트
        """
        # Chain 가져오기 또는 생성
        if problem_id not in self.hint_chains:
            self.hint_chains[problem_id] = HintChain(problem_id=problem_id)
        
        chain = self.hint_chains[problem_id]
        
        # 부족한 영역 식별
        weak_areas = diagnosis.get_weak_areas_for_level(selected_level)
        
        # Chain 컨텍스트
        chain_context = chain.get_history_context()
        
        print(f"[AdaptivePromptGenerator] student_code 길이: {len(student_code)} chars")
        print(f"[AdaptivePromptGenerator] student_code preview: {student_code[:200]}")
        
        # 교육학적 프롬프트 생성 (학생 코드 포함!)
        if selected_level == 'novice':
            prompt = self.edu_engine.generate_novice_prompt(
                problem_info, diagnosis, weak_areas, chain_context, student_code
            )
        elif selected_level == 'intermediate':
            prompt = self.edu_engine.generate_intermediate_prompt(
                problem_info, diagnosis, weak_areas, chain_context, student_code
            )
        else:  # advanced
            prompt = self.edu_engine.generate_advanced_prompt(
                problem_info, diagnosis, weak_areas, chain_context, student_code
            )
        
        return prompt
    
    def _build_base_prompt(self, student_code: str, solution_code: str,
                           problem_info: Dict, diagnosis: 'CodeDiagnosis',
                           chain: HintChain, selected_level: str, 
                           weak_areas: List[str], suitability_msg: str) -> str:
        """기본 프롬프트 구조 (리팩토링 v2 - 사용자 선택 방식)"""
        return f"""=== 코딩 교육 AI: 힌트 내용 자동 구성 시스템 ===
당신은 Python 코딩 교육 전문가입니다. 학생이 선택한 난이도에 맞춰
4가지 지표를 분석하여 부족한 영역에 특화된 힌트를 생성합니다.

---
## 단계 1: 학생 코드 4가지 지표 분석

### 정량적 지표:
- **코드 유사도:** {diagnosis.similarity:.1f}%
- **문법 오류:** {diagnosis.syntax_errors}개
- **논리 오류:** {diagnosis.logic_errors}개
- **개념 이해도:** {diagnosis.concept_level}/5점

### 누락된 개념:
{', '.join(diagnosis.missing_concepts) if diagnosis.missing_concepts else '✅ 모든 핵심 개념 포함'}

### 오류 상세:
{chr(10).join(diagnosis.error_details) if diagnosis.error_details else '✅ 문법 오류 없음'}

---
## 단계 2: 사용자 선택 난이도 & 부족한 영역

**사용자 선택:** {selected_level.upper()} 힌트

**적합성 판단:** {suitability_msg}

**부족한 영역 (힌트 집중 포인트):**
{chr(10).join(f"- {area}" for area in weak_areas)}

### 난이도별 기준:
- **고급(Advanced):** 코드 유사도 ≥ 76% or 문법 오류 ≤1개 + 논리 오류 = 0
- **중급(Intermediate):** 코드 유사도 40-75% or 문법 오류 2-5개 or 논리 오류 1-2개
- **초급(Novice):** 코드 유사도 < 40% or 문법 오류 ≥6개 or 논리 오류 ≥3개

---
## 단계 3: Chain-of-Hints 컨텍스트 (COT 누적 학습)

### 이전 힌트 이력:
{chain.get_history_context()}

### 중요 규칙:
- 이전 힌트와 **다른 각도**에서 접근하세요
- 정보량을 **점진적으로 증가**시키세요
- **같은 내용 반복 금지**
- **부족한 영역**에 집중하세요

---
## 문제 정보

**제목:** {problem_info.get('title', 'N/A')}
**난이도:** Level {problem_info.get('level', 'N/A')}
**태그:** {', '.join(problem_info.get('tags', []))}

### 학생의 현재 코드:
```python
{student_code}
```

---"""
    
    def _get_level_specific_prompt(self, level: str, problem_info: Dict) -> str:
        """난이도별 특화 프롬프트"""
        if level == "novice":
            return self._novice_prompt(problem_info)
        elif level == "intermediate":
            return self._intermediate_prompt(problem_info)
        else:  # advanced
            return self._advanced_prompt(problem_info)
    
    def _novice_prompt(self, problem_info: Dict) -> str:
        """초급 프롬프트"""
        next_step = self._get_next_step(problem_info)
        
        return f"""## 단계 4: 초급(Novice) 힌트 생성 규약

### 목표:
학생이 "{next_step}"을 구현하도록 **구체적으로 안내**

### 출력 구조 (반드시 준수):
1. **한 줄 핵심 요약** (무엇을 해야 하는지)
2. **필요한 함수/라이브러리명 명시**
3. **1~3줄 코드 예시 제공**
4. **다음 단계 안내**

### 규칙:
- **문자 제한:** 200자 이내
- **필수 포함:** 함수명, 라이브러리, 코드 패턴, 다음 단계
- **금지:** 평가/분석 문구 ("학생이 ~했다"), 전체 솔루션 코드

### 좋은 예시:
```
다음 단계는 입력을 받아 정수로 변환하는 것입니다.

input() 함수로 입력받고, int()로 정수 변환:
```python
n = int(input())
```

이제 이 값을 사용해 다음 작업을 진행하세요.
```

### 나쁜 예시 (금지):
```
학생이 입력을 받지 않았네요. 입력을 받아보세요.
(평가 문구, 구체적 안내 없음)
```"""
    
    def _intermediate_prompt(self, problem_info: Dict) -> str:
        """중급 프롬프트"""
        return f"""## 단계 4: 중급(Intermediate) 힌트 생성 규약

### 목표:
**추상적 개념**과 **접근 방법**을 제시하여 스스로 구현하게 유도

### 출력 구조 (반드시 준수):
1. **한 줄 개념 설명** (어떤 개념이 필요한지)
2. **자료구조/알고리즘 설명** (왜 필요한지)
3. **3-4단계 접근법** (어떻게 진행할지)
4. **방법의 효과 설명** (이렇게 하면 어떤 이점이 있는지)

### 규칙:
- **문자 제한:** 180자 이내
- **함수명 직접 제시 금지** (대신 "~을 할 수 있는 자료구조", "~을 처리하는 방법" 등 추상적 표현)
- **코드 예시 금지**
- **개념적 이해** 중심

### 좋은 예시:
```
여러 값을 효율적으로 저장하려면 순서가 있는 자료구조가 필요합니다.

접근법:
1. 빈 컨테이너 준비
2. 반복하며 값 추가
3. 필요할 때 인덱스로 접근
4. 저장된 값들을 순서대로 처리

이 방법을 사용하면 모든 값을 한 곳에 모아 관리할 수 있습니다.
```

### 나쁜 예시 (금지):
```
list를 사용하세요. 
numbers = []
for i in range(n):
    numbers.append(int(input()))
(함수명 명시, 코드 제공)
```"""
    
    def _advanced_prompt(self, problem_info: Dict) -> str:
        """고급 프롬프트"""
        return f"""## 단계 4: 고급(Advanced) 힌트 생성 규약

### 목표:
**소크라테스식 질문**으로 학생 스스로 깨닫게 만들기

### 출력 구조 (반드시 준수):
1. **중립적 코드 관찰 문장** (사실만 진술, 평가 금지)
2. **한 개의 소크라테스식 질문** (열린 질문, 200자 이하)

### 규칙:
- **함수명/코드 예시 금지**
- **열린 질문** (답이 하나가 아닌)
- **안내·유도 지양** (선택지·정답 암시 금지)
- **추상적 사고** 유도

### 좋은 예시:
```
현재 코드는 각 경우를 개별적으로 처리하고 있습니다.

만약 처리해야 할 경우가 1000개라면, 지금 방식으로 계속 진행하시겠습니까?
```

### 나쁜 예시 (금지):
```
반복문을 사용하지 않았네요. for나 while을 사용해보는 게 어떨까요?
(함수명 명시, 선택지 제시)
```"""
    
    def _get_quality_rules(self, level: str) -> str:
        """품질 검증 규칙"""
        return f"""---
## 단계 5: 출력 검증 규칙

### 자동 검증 항목:
1. ✅ 구조 준수 (단계별 형식)
2. ✅ 문자 수 제한
3. ✅ 금지 패턴 미포함
4. ✅ 필수 요소 포함

### 출력 전 자가 검증:
- [ ] 이전 힌트와 다른 접근인가?
- [ ] 난이도 규약을 준수했는가?
- [ ] 금지 사항을 어기지 않았는가?
- [ ] 학생이 이해하고 실행할 수 있는가?

### 최종 출력 형식:
**명확하고 간결한 한국어로 힌트만 출력하세요.**
(프롬프트 분석, 메타 설명 등 불필요한 내용 제외)
"""
    
    def _get_next_step(self, problem_info: Dict) -> str:
        """다음 단계 추출"""
        solutions = problem_info.get('solutions', [])
        if solutions and solutions[0].get('logic_steps'):
            return solutions[0]['logic_steps'][0].get('goal', '문제 해결')
        return "문제 해결"
    
    def _escalate_level(self, current_level: str) -> str:
        """난이도 상승"""
        if current_level == "novice":
            return "intermediate"
        elif current_level == "intermediate":
            return "advanced"
        return "advanced"  # 이미 최고 난이도
    
    def record_hint(self, problem_id: str, hint: str, level: str, 
                   student_code: str = None):
        """힌트 기록 (Chain에 추가)"""
        if problem_id not in self.hint_chains:
            self.hint_chains[problem_id] = HintChain(problem_id=problem_id)
        
        self.hint_chains[problem_id].add_hint(hint, level, student_code)
