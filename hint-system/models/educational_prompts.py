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
        
        return f"""당신은 Python 코딩 교육 전문가입니다.

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
## [분석 단계] 단계별로 생각하세요:

<thinking>
1단계: 학생 코드를 읽고 무엇을 하려는지 파악
2단계: 진단 결과에서 가장 심각한 문제 식별 (유사도, 오류, 부족한 영역)
3단계: 이전 힌트 확인 - 다른 각도로 접근할 방법 찾기
4단계: 구체적인 함수명과 코드 예시로 힌트 작성
</thinking>

## [출력 단계] 초급 힌트 형식:

<output>
💡 **핵심**: (한 줄로 무엇을 해야 하는지)

📝 **필요한 도구**:
- 함수명 또는 라이브러리 (구체적으로!)

💻 **코드 예시** (1-2줄):
```python
(구체적 코드 패턴)
```
</output>

**중요: <output> 태그 안의 내용만 학생에게 전달됩니다. <thinking>은 내부 분석용입니다.**
"""
    
    def generate_intermediate_prompt(self, problem_info: Dict, diagnosis: 'CodeDiagnosis',
                                    weak_areas: List[str], chain_context: str, student_code: str) -> str:
        """중급 프롬프트"""
        
        print(f"\n[EducationalPromptEngine] 중급(Intermediate) 프롬프트 생성")
        print(f"  학생 코드 길이: {len(student_code)} chars")
        print(f"  부족한 영역: {weak_areas}")
        
        return f"""당신은 Python 코딩 교육 전문가입니다.

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
## [분석 단계] 단계별로 생각하세요:

<thinking>
1단계: 학생이 사용한 자료구조와 알고리즘 파악
2단계: 더 효율적이거나 명확한 접근법이 있는지 검토
3단계: 이전 힌트와 다른 개념적 각도 선택
4단계: 함수명 없이 개념으로 설명하는 방법 구상
</thinking>

## [출력 단계] 중급 힌트 형식:

<output>
🧠 **개념**: (필요한 자료구조나 알고리즘 개념 - 함수명 직접 언급 금지)

📊 **접근 방법**:
1단계: (어떻게 시작할지)
2단계: (다음에 무엇을 할지)
3단계: (마지막 단계)
</output>

**중요: 함수명/변수명 직접 언급 금지. <output> 태그 안의 내용만 전달됩니다.**
"""
    
    def generate_advanced_prompt(self, problem_info: Dict, diagnosis: 'CodeDiagnosis',
                                weak_areas: List[str], chain_context: str, student_code: str) -> str:
        """고급 프롬프트"""
        
        print(f"\n[EducationalPromptEngine] 고급(Advanced) 프롬프트 생성")
        print(f"  학생 코드 길이: {len(student_code)} chars")
        print(f"  부족한 영역: {weak_areas}")
        
        return f"""당신은 Python 코딩 교육 전문가입니다.

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
## [분석 단계] 단계별로 생각하세요:

<thinking>
1단계: 학생 코드의 장단점 객관적으로 분석
2단계: 최적화 가능 지점이나 다른 접근법 고려
3단계: 이전 힌트보다 더 깊은 질문 찾기
4단계: 답을 암시하지 않으면서 사고를 유도하는 질문 구성
</thinking>

## [출력 단계] 고급 힌트 형식:

<output>
🔍 **관찰**: (학생 코드에서 발견한 패턴을 중립적으로 서술)

❓ **질문**: (학생이 스스로 생각하게 만드는 열린 질문 1개)
</output>

**중요: 함수명/코드 예시 절대 금지. 질문으로만 사고를 유도하세요. <output> 태그 안의 내용만 전달됩니다.**
"""
