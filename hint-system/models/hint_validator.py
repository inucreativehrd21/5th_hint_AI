"""
힌트 품질 검증 시스템
자동 규칙 검증 및 품질 보증
"""
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """검증 결과"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    score: float  # 0-100점
    
    def __str__(self):
        status = "✅ 통과" if self.is_valid else "❌ 실패"
        return f"""{status} (점수: {self.score:.1f}/100)
오류: {len(self.errors)}개
경고: {len(self.warnings)}개
"""


class HintValidator:
    """힌트 품질 검증기"""
    
    # 금지 패턴 (함수명, 키워드 등)
    FORBIDDEN_PATTERNS = {
        'novice': [],  # 초급은 함수명 허용
        'intermediate': [
            r'\b(def|for|while|if|elif|else|input|print|int|str|list|dict|append|len)\b',
            r'```python',  # 코드 블록 금지
        ],
        'advanced': [
            r'\b(def|for|while|if|elif|else|input|print|int|str|list|dict|append|len|range|enumerate)\b',
            r'```python',  # 코드 블록 금지
            r'~(을|를) 사용',  # 직접 지시 금지
            r'~(하세요|해보세요|추가하세요)',  # 명령형 금지
        ]
    }
    
    # 금지 문구 (평가, 분석)
    EVALUATION_PHRASES = [
        '학생이',
        '코드를 보니',
        '작성하지 않았',
        '~했네요',
        '~하지 않았',
        '~가 없',
    ]
    
    def validate_hint(self, hint: str, level: str) -> ValidationResult:
        """종합 검증"""
        errors = []
        warnings = []
        score = 100.0
        
        # 1. 구조 검증
        structure_ok, structure_errors = self._check_structure(hint, level)
        if not structure_ok:
            errors.extend(structure_errors)
            score -= 20
        
        # 2. 길이 검증
        length_ok, length_errors = self._check_length(hint, level)
        if not length_ok:
            errors.extend(length_errors)
            score -= 15
        
        # 3. 금지 패턴 검증
        pattern_ok, pattern_errors = self._check_forbidden_patterns(hint, level)
        if not pattern_ok:
            errors.extend(pattern_errors)
            score -= 25
        
        # 4. 평가 문구 검증
        eval_ok, eval_warnings = self._check_evaluation_phrases(hint)
        if not eval_ok:
            warnings.extend(eval_warnings)
            score -= 10
        
        # 5. 코드 예시 검증
        code_ok, code_errors = self._check_code_examples(hint, level)
        if not code_ok:
            if level in ['intermediate', 'advanced']:
                errors.extend(code_errors)
                score -= 20
            else:
                warnings.extend(code_errors)
        
        # 6. 질문 형식 검증 (고급)
        if level == 'advanced':
            question_ok, question_errors = self._check_question_format(hint)
            if not question_ok:
                errors.extend(question_errors)
                score -= 15
        
        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            score=max(0, score)
        )
    
    def _check_structure(self, hint: str, level: str) -> Tuple[bool, List[str]]:
        """구조 검증"""
        errors = []
        
        if not hint.strip():
            errors.append("힌트가 비어있습니다")
            return False, errors
        
        lines = hint.strip().split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        if level == 'novice':
            # 초급: 4개 요소 필요
            if len(non_empty_lines) < 3:
                errors.append("초급 힌트는 최소 3줄 이상이어야 합니다 (요약, 함수명, 예시, 다음단계)")
        
        elif level == 'intermediate':
            # 중급: 4개 요소 필요
            if len(non_empty_lines) < 3:
                errors.append("중급 힌트는 최소 3줄 이상이어야 합니다 (개념, 설명, 접근법, 효과)")
        
        elif level == 'advanced':
            # 고급: 관찰 + 질문
            if '?' not in hint:
                errors.append("고급 힌트는 소크라테스식 질문을 포함해야 합니다")
        
        return len(errors) == 0, errors
    
    def _check_length(self, hint: str, level: str) -> Tuple[bool, List[str]]:
        """길이 검증"""
        errors = []
        length = len(hint)
        
        limits = {
            'novice': 200,
            'intermediate': 180,
            'advanced': 200
        }
        
        limit = limits.get(level, 200)
        
        if length > limit:
            errors.append(f"힌트가 너무 깁니다 ({length}자 > {limit}자 제한)")
        
        if length < 20:
            errors.append(f"힌트가 너무 짧습니다 ({length}자)")
        
        return len(errors) == 0, errors
    
    def _check_forbidden_patterns(self, hint: str, level: str) -> Tuple[bool, List[str]]:
        """금지 패턴 검증"""
        errors = []
        
        patterns = self.FORBIDDEN_PATTERNS.get(level, [])
        
        for pattern in patterns:
            matches = re.findall(pattern, hint, re.IGNORECASE)
            if matches:
                errors.append(f"금지된 패턴 발견 ({level}): {', '.join(set(matches))}")
        
        return len(errors) == 0, errors
    
    def _check_evaluation_phrases(self, hint: str) -> Tuple[bool, List[str]]:
        """평가 문구 검증"""
        warnings = []
        
        for phrase in self.EVALUATION_PHRASES:
            if phrase in hint:
                warnings.append(f"평가 문구 발견: '{phrase}' → 제거 권장")
        
        return len(warnings) == 0, warnings
    
    def _check_code_examples(self, hint: str, level: str) -> Tuple[bool, List[str]]:
        """코드 예시 검증"""
        errors = []
        
        # 코드 블록 검출
        has_code_block = '```' in hint or '    ' in hint  # 들여쓰기 4칸도 코드
        
        if level == 'intermediate' and has_code_block:
            errors.append("중급 힌트는 코드 예시를 포함하면 안됩니다")
        
        if level == 'advanced' and has_code_block:
            errors.append("고급 힌트는 코드 예시를 포함하면 안됩니다")
        
        return len(errors) == 0, errors
    
    def _check_question_format(self, hint: str) -> Tuple[bool, List[str]]:
        """질문 형식 검증 (고급 전용)"""
        errors = []
        
        # 질문이 있는지
        if '?' not in hint:
            errors.append("소크라테스식 질문(?)이 없습니다")
        
        # 열린 질문인지 (예/아니오 답변 불가)
        closed_questions = [
            '~인가요?',
            '~입니까?',
            '~나요?',
            '맞나요?',
            '그렇죠?',
        ]
        
        for cq in closed_questions:
            if cq in hint:
                errors.append(f"닫힌 질문 발견: '{cq}' → 열린 질문으로 변경")
        
        # 선택지 제시하는지
        choice_patterns = [
            r'(A|B|가|나)와 (B|C|나|다)',
            r'~거나 ~',
            r'~이나 ~',
        ]
        
        for pattern in choice_patterns:
            if re.search(pattern, hint):
                errors.append("선택지 제시 발견 → 열린 질문으로 변경")
        
        return len(errors) == 0, errors
    
    def auto_fix_hint(self, hint: str, level: str) -> str:
        """자동 수정 (가능한 경우)"""
        fixed = hint
        
        # 1. 평가 문구 제거
        for phrase in self.EVALUATION_PHRASES:
            if phrase in fixed:
                # 해당 문장 전체 제거
                lines = fixed.split('\n')
                lines = [l for l in lines if phrase not in l]
                fixed = '\n'.join(lines)
        
        # 2. 과도한 공백 제거
        fixed = re.sub(r'\n{3,}', '\n\n', fixed)
        fixed = fixed.strip()
        
        # 3. 길이 제한 (자르기)
        limits = {'novice': 200, 'intermediate': 180, 'advanced': 200}
        limit = limits.get(level, 200)
        
        if len(fixed) > limit:
            # 마지막 완전한 문장까지만
            sentences = fixed.split('.')
            result = []
            current_length = 0
            
            for sent in sentences:
                if current_length + len(sent) + 1 <= limit:
                    result.append(sent)
                    current_length += len(sent) + 1
                else:
                    break
            
            fixed = '.'.join(result)
            if fixed and not fixed.endswith('.'):
                fixed += '.'
        
        return fixed
    
    def generate_feedback(self, result: ValidationResult) -> str:
        """검증 결과 피드백 생성"""
        feedback = [f"검증 결과: {result}"]
        
        if result.errors:
            feedback.append("\n❌ 오류:")
            for i, err in enumerate(result.errors, 1):
                feedback.append(f"  {i}. {err}")
        
        if result.warnings:
            feedback.append("\n⚠️ 경고:")
            for i, warn in enumerate(result.warnings, 1):
                feedback.append(f"  {i}. {warn}")
        
        if result.is_valid:
            feedback.append("\n✅ 힌트가 품질 기준을 만족합니다!")
        else:
            feedback.append("\n💡 위 문제를 수정 후 다시 생성해주세요.")
        
        return '\n'.join(feedback)


# 사용 예시
if __name__ == '__main__':
    validator = HintValidator()
    
    # 테스트 케이스
    test_hints = {
        'novice_good': """다음 단계는 입력을 받는 것입니다.

input() 함수를 사용하세요:
```python
n = int(input())
```

이제 변수 n에 값이 저장되었습니다.""",
        
        'intermediate_bad': """list를 사용하세요. 
numbers = []
for i in range(n):
    numbers.append(int(input()))
이렇게 하면 됩니다.""",
        
        'advanced_good': """현재 코드는 각 값을 개별 변수에 저장하고 있습니다.

만약 값이 1000개라면, 변수를 1000개 만드시겠습니까?""",
    }
    
    for name, hint in test_hints.items():
        level = name.split('_')[0]
        print(f"\n{'='*60}")
        print(f"테스트: {name}")
        print(f"{'='*60}")
        result = validator.validate_hint(hint, level)
        print(validator.generate_feedback(result))
