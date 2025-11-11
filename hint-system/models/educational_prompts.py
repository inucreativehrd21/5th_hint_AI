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
        
        # 문제 설명 간소화
        problem_desc = problem_info.get('description', '')
        if problem_desc and problem_desc != 'N/A':
            desc_short = problem_desc[:100] + '...' if len(problem_desc) > 100 else problem_desc
        else:
            desc_short = '(설명 없음)'
        
        return f"""Generate NOVICE hint in this EXACT format:

💡 **핵심**: [one-line: what to do]
📝 **필요한 도구**: `func1()`, `func2()`, `func3()`
💻 **코드 예시**:
```python
# 2-4 lines of runnable code
```
🎯 **다음 단계**: [where to use this]

---
CONTEXT (for analysis - DO NOT output):
Problem: {problem_info.get('title', 'N/A')}
{desc_short}

Student code:
```python
{student_code[:400]}{'...' if len(student_code) > 400 else ''}
```

Diagnosis: similarity={diagnosis.similarity:.0f}%, syntax_errors={diagnosis.syntax_errors}, logic_errors={diagnosis.logic_errors}
Weak areas: {', '.join(weak_areas[:3])}
Previous hints: {len(chain_context.split(chr(10))) if chain_context != '없음' else 0} hints

---
RULES:
1. START with 💡 immediately
2. List 3-5 function names with () - be specific
3. Show runnable code (2-4 lines with comments)
4. END with 🎯

NEVER: Don't analyze student ("학생은~"), don't use 🔍/❓/🧠 (wrong level), don't explain steps (1단계)

Example:
💡 **핵심**: 입력받아 리스트에 저장
📝 **필요한 도구**: `input()`, `int()`, `list.append()`
💻 **코드 예시**:
```python
n = int(input())
numbers = []
numbers.append(n)
```
🎯 **다음 단계**: 반복문으로 여러 값 입력받기

NOW GENERATE:
"""
    
    def generate_intermediate_prompt(self, problem_info: Dict, diagnosis: 'CodeDiagnosis',
                                    weak_areas: List[str], chain_context: str, student_code: str) -> str:
        """중급 프롬프트"""
        
        print(f"\n[EducationalPromptEngine] 중급(Intermediate) 프롬프트 생성")
        print(f"  학생 코드 길이: {len(student_code)} chars")
        print(f"  부족한 영역: {weak_areas}")
        
        # 문제 설명 간소화
        problem_desc = problem_info.get('description', '')
        if problem_desc and problem_desc != 'N/A':
            desc_short = problem_desc[:100] + '...' if len(problem_desc) > 100 else problem_desc
        else:
            desc_short = '(설명 없음)'
        
        return f"""Generate INTERMEDIATE hint in this EXACT format:

🧠 **개념**: [algorithm/data structure name]
📊 **접근 방법**:
1단계: [initialize what]
2단계: [perform what operation]
3단계: [process result]
4단계: [final output]
💾 **필요한 자료구조**: [list specific data structures]

---
CONTEXT (for analysis - DO NOT output):
Problem: {problem_info.get('title', 'N/A')}
{desc_short}

Student code:
```python
{student_code[:400]}{'...' if len(student_code) > 400 else ''}
```

Diagnosis: similarity={diagnosis.similarity:.0f}%, syntax_errors={diagnosis.syntax_errors}, logic_errors={diagnosis.logic_errors}
Weak areas: {', '.join(weak_areas[:3])}

---
RULES:
1. START with 🧠
2. Use 4-step approach (초기화 → 수행 → 처리 → 출력)
3. List concrete data structures with roles
4. NO code examples (wrong level)

NEVER: 💡/📝/💻/🎯 (novice), 🔍/❓ (advanced), code snippets

Example:
🧠 **개념**: 깊이 우선 탐색 (DFS)
📊 **접근 방법**:
1단계: praise 배열을 0으로 초기화
2단계: DFS로 칭찬 점수 전파
3단계: 부하 점수를 상사에게 합산
4단계: 모든 직원 점수 출력
💾 **필요한 자료구조**: praise 배열, graph 트리

NOW GENERATE:
"""
    
    def generate_advanced_prompt(self, problem_info: Dict, diagnosis: 'CodeDiagnosis',
                                weak_areas: List[str], chain_context: str, student_code: str) -> str:
        """고급 프롬프트"""
        
        print(f"\n[EducationalPromptEngine] 고급(Advanced) 프롬프트 생성")
        print(f"  학생 코드 길이: {len(student_code)} chars")
        print(f"  부족한 영역: {weak_areas}")
        
        # 문제 설명 간소화
        problem_desc = problem_info.get('description', '')
        if problem_desc and problem_desc != 'N/A':
            desc_short = problem_desc[:100] + '...' if len(problem_desc) > 100 else problem_desc
        else:
            desc_short = '(설명 없음)'
        
        return f"""Generate ADVANCED hint in this EXACT format:

🔍 **관찰**: [neutral observation about code pattern - 1 sentence]
❓ **질문**: [open-ended question to make student think]

---
CONTEXT (for analysis - DO NOT output):
Problem: {problem_info.get('title', 'N/A')}
{desc_short}

Student code:
```python
{student_code[:400]}{'...' if len(student_code) > 400 else ''}
```

Diagnosis: similarity={diagnosis.similarity:.0f}%, syntax_errors={diagnosis.syntax_errors}, logic_errors={diagnosis.logic_errors}
Weak areas: {', '.join(weak_areas[:3])}

---
RULES:
1. Observe neutrally (NO judgment: "잘못", "부족")
2. Ask ONE open question only
3. NO function names, algorithm names, code hints
4. NO answer hints ("~하면 어떨까요?")

NEVER: 💡/📝/💻/🎯 (novice), 🧠/📊/💾 (intermediate), function names, code snippets

Example:
🔍 **관찰**: 현재 코드는 각 경우를 개별적으로 처리하고 있습니다
❓ **질문**: 만약 처리해야 할 경우가 1000개라면, 지금 방식으로 계속 진행하시겠습니까?

NOW GENERATE:
"""
