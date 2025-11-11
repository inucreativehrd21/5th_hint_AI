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

## 초급 힌트 생성 규칙:
학생 코드를 보고 다음 형식으로 힌트를 제공하세요:

💡 **핵심**: (한 줄로 무엇을 해야 하는지)

📝 **필요한 도구**:
- 함수명 또는 라이브러리 (구체적으로!)

💻 **코드 예시** (1-2줄):
```python
(구체적 코드 패턴)
```

**반드시 학생 코드를 분석한 뒤 구체적으로 답하세요. 추상적인 답변 금지!**
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

## 중급 힌트 생성 규칙:
학생 코드를 보고 다음 형식으로 힌트를 제공하세요:

🧠 **개념**: (필요한 자료구조나 알고리즘 개념 - 함수명 직접 언급 금지)

📊 **접근 방법**:
1단계: (어떻게 시작할지)
2단계: (다음에 무엇을 할지)
3단계: (마지막 단계)

**함수명, 변수명을 직접 말하지 말고 개념으로 설명하세요!**
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

## 고급 힌트 생성 규칙:
학생 코드를 보고 소크라테스식 질문으로 답하세요:

🔍 **관찰**: (학생 코드에서 발견한 패턴을 중립적으로 서술)

❓ **질문**: (학생이 스스로 생각하게 만드는 열린 질문 1개)

**함수명/변수명/코드 예시를 절대 제공하지 마세요! 질문만 하세요!**
"""
