"""
코드 진단 시스템 모듈 (리팩토링 v2)
- 난이도 자동 판정 제거 → 사용자 선택 방식
- 4가지 지표만 계산: 유사도, 문법 오류, 논리 오류, 개념 이해도
- 선택된 난이도에 맞는 부족한 영역 식별
"""
import ast
import difflib
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class CodeDiagnosis:
    """코드 진단 결과 (난이도 판정 제거)"""
    similarity: float  # 코드 유사도 (0-100%)
    syntax_errors: int  # 문법 오류 개수
    logic_errors: int  # 논리 오류 개수
    concept_level: int  # 개념 이해도 (1-5)
    missing_concepts: List[str]  # 누락된 개념
    error_details: List[str]  # 상세 오류 메시지
    
    def get_weak_areas_for_level(self, selected_level: str) -> List[str]:
        """선택된 난이도에서 부족한 영역 식별 (힌트 내용 구성용)"""
        weak_areas = []
        
        if selected_level == 'novice':
            # 초급 기준: 유사도 < 40% 또는 문법 오류 ≥ 6개 또는 논리 오류 ≥ 3개
            if self.similarity < 40:
                weak_areas.append('기본 코드 구조 이해')
            if self.syntax_errors >= 6:
                weak_areas.append('문법 기초 학습 필요')
            if self.logic_errors >= 3:
                weak_areas.append('논리 구조 설계')
            if self.concept_level <= 2:
                weak_areas.append('핵심 개념 이해')
            if self.missing_concepts:
                weak_areas.append(f"누락된 개념: {', '.join(self.missing_concepts[:3])}")
                
        elif selected_level == 'intermediate':
            # 중급 기준: 유사도 40-75% 또는 문법 오류 2-5개 또는 논리 오류 1-2개
            if 40 <= self.similarity < 75:
                weak_areas.append('알고리즘 구현 완성도')
            if 2 <= self.syntax_errors <= 5:
                weak_areas.append('세부 문법 정확도')
            if 1 <= self.logic_errors <= 2:
                weak_areas.append('로직 최적화')
            if self.concept_level == 3:
                weak_areas.append('응용 능력 향상')
            if self.missing_concepts:
                weak_areas.append(f"개선 필요: {', '.join(self.missing_concepts[:2])}")
                
        elif selected_level == 'advanced':
            # 고급 기준: 유사도 ≥ 76% 또는 문법 오류 ≤ 1개 + 논리 오류 = 0
            if self.similarity >= 76:
                weak_areas.append('코드 완성도 (거의 완성)')
            if self.syntax_errors <= 1:
                weak_areas.append('최종 미세 조정')
            if self.logic_errors == 0:
                weak_areas.append('로직 완성 (효율성 개선)')
            if self.concept_level >= 4:
                weak_areas.append('심화 개념 적용')
        
        return weak_areas if weak_areas else ['전반적 코드 개선']
    
    def is_suitable_for_level(self, selected_level: str) -> Tuple[bool, str]:
        """사용자가 선택한 난이도가 적절한지 판단"""
        if selected_level == 'novice':
            # 초급 적합: 문법 오류 많거나 유사도 매우 낮음
            if self.syntax_errors >= 3 or self.similarity < 30:
                return True, "초급 힌트가 적절합니다."
            elif self.similarity >= 76 and self.syntax_errors <= 1:
                return False, "⚠️ 코드가 거의 완성되었습니다. 고급 힌트를 추천합니다!"
            else:
                return True, "초급 힌트를 제공합니다."
                
        elif selected_level == 'intermediate':
            # 중급 적합: 어느 정도 진행했지만 완성 안됨
            if 30 <= self.similarity < 76 or 1 <= self.syntax_errors <= 5:
                return True, "중급 힌트가 적절합니다."
            elif self.similarity < 30 and self.syntax_errors >= 6:
                return False, "⚠️ 기초 문법 학습이 필요합니다. 초급 힌트를 추천합니다!"
            else:
                return True, "중급 힌트를 제공합니다."
                
        elif selected_level == 'advanced':
            # 고급 적합: 거의 완성 단계
            if self.similarity >= 60 and self.syntax_errors <= 2:
                return True, "고급 힌트가 적절합니다."
            elif self.similarity < 40 or self.syntax_errors >= 5:
                return False, "⚠️ 기본 구조가 부족합니다. 초급 또는 중급 힌트를 추천합니다!"
            else:
                return True, "고급 힌트를 제공합니다."
        
        return True, "힌트를 제공합니다."


class CodeAnalyzer:
    """코드 분석 및 진단 클래스"""
    
    def __init__(self):
        pass
    
    def diagnose(self, student_code: str, solution_code: str, 
                 problem_description: str) -> CodeDiagnosis:
        """종합 진단 수행"""
        similarity = self.calculate_similarity(student_code, solution_code)
        syntax_errors = self.count_syntax_errors(student_code)
        logic_errors = self.count_logic_errors(student_code, solution_code)
        concept_level, missing = self.assess_concepts(student_code, problem_description)
        error_details = self.get_error_details(student_code)
        
        return CodeDiagnosis(
            similarity=similarity,
            syntax_errors=syntax_errors,
            logic_errors=logic_errors,
            concept_level=concept_level,
            missing_concepts=missing,
            error_details=error_details
        )
    
    def calculate_similarity(self, student_code: str, solution_code: str) -> float:
        """코드 유사도 계산 (0-100%)"""
        if not student_code.strip() or not solution_code.strip():
            return 0.0
        
        # 정규화: 공백/주석 제거
        student_normalized = self._normalize_code(student_code)
        solution_normalized = self._normalize_code(solution_code)
        
        # SequenceMatcher 사용
        matcher = difflib.SequenceMatcher(None, student_normalized, solution_normalized)
        ratio = matcher.ratio() * 100
        
        # AST 구조 유사도도 고려
        ast_similarity = self._compare_ast_structure(student_code, solution_code)
        
        # 가중 평균 (텍스트 60%, 구조 40%)
        return ratio * 0.6 + ast_similarity * 0.4
    
    def _normalize_code(self, code: str) -> str:
        """코드 정규화: 공백, 주석 제거"""
        # 주석 제거
        code = re.sub(r'#.*', '', code)
        # 여러 공백을 하나로
        code = re.sub(r'\s+', ' ', code)
        return code.strip()
    
    def _compare_ast_structure(self, code1: str, code2: str) -> float:
        """AST 구조 유사도 (0-100%)"""
        try:
            tree1 = ast.parse(code1)
            tree2 = ast.parse(code2)
            
            # 각 AST 노드 타입 추출
            nodes1 = [type(node).__name__ for node in ast.walk(tree1)]
            nodes2 = [type(node).__name__ for node in ast.walk(tree2)]
            
            # 노드 타입 유사도
            common = len(set(nodes1) & set(nodes2))
            total = len(set(nodes1) | set(nodes2))
            
            return (common / total * 100) if total > 0 else 0.0
        except SyntaxError:
            return 0.0
    
    def count_syntax_errors(self, code: str) -> int:
        """문법 오류 개수"""
        if not code.strip():
            return 0
        
        errors = 0
        
        # Python 문법 검사
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            errors += 1
            # 추가 문법 오류 찾기
            lines = code.split('\n')
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    try:
                        compile(line, '<string>', 'exec')
                    except:
                        errors += 0.5  # 줄 단위 오류는 가중치 낮게
        
        return int(errors)
    
    def count_logic_errors(self, student_code: str, solution_code: str) -> int:
        """논리 오류 개수 추정"""
        errors = 0
        
        try:
            student_ast = ast.parse(student_code)
            solution_ast = ast.parse(solution_code)
            
            # 반복문 개수 비교
            student_loops = sum(1 for _ in ast.walk(student_ast) 
                               if isinstance(_, (ast.For, ast.While)))
            solution_loops = sum(1 for _ in ast.walk(solution_ast) 
                                if isinstance(_, (ast.For, ast.While)))
            
            # 조건문 개수 비교
            student_ifs = sum(1 for _ in ast.walk(student_ast) 
                             if isinstance(_, ast.If))
            solution_ifs = sum(1 for _ in ast.walk(solution_ast) 
                              if isinstance(_, ast.If))
            
            # 함수 호출 비교
            student_calls = sum(1 for _ in ast.walk(student_ast) 
                               if isinstance(_, ast.Call))
            solution_calls = sum(1 for _ in ast.walk(solution_ast) 
                                if isinstance(_, ast.Call))
            
            # 차이가 크면 논리 오류로 간주
            if abs(student_loops - solution_loops) > 1:
                errors += abs(student_loops - solution_loops) - 1
            if abs(student_ifs - solution_ifs) > 1:
                errors += abs(student_ifs - solution_ifs) - 1
            if abs(student_calls - solution_calls) > 2:
                errors += (abs(student_calls - solution_calls) - 2) // 2
                
        except SyntaxError:
            # 문법 오류가 있으면 논리 분석 불가
            errors = 0
        
        return errors
    
    def assess_concepts(self, student_code: str, problem_description: str) -> Tuple[int, List[str]]:
        """개념 이해도 평가 (1-5점) 및 누락된 개념"""
        score = 1
        missing = []
        
        # 문제에서 핵심 개념 추출
        concepts = self._extract_key_concepts(problem_description)
        
        # 코드에서 개념 확인
        for concept in concepts:
            if self._check_concept_in_code(concept, student_code):
                score += 1
            else:
                missing.append(concept)
        
        return min(score, 5), missing
    
    def _extract_key_concepts(self, description: str) -> List[str]:
        """문제 설명에서 핵심 개념 추출"""
        concepts = []
        
        # 키워드 기반 개념 추출
        if '반복' in description or '여러' in description or 'N번' in description:
            concepts.append('반복문')
        if '조건' in description or '만약' in description or '경우' in description:
            concepts.append('조건문')
        if '입력' in description:
            concepts.append('입력처리')
        if '출력' in description:
            concepts.append('출력')
        if '정렬' in description or '순서' in description:
            concepts.append('정렬')
        if '찾' in description or '검색' in description:
            concepts.append('탐색')
        if '합' in description or '곱' in description or '계산' in description:
            concepts.append('연산')
        
        return concepts
    
    def _check_concept_in_code(self, concept: str, code: str) -> bool:
        """코드에서 개념 구현 여부 확인"""
        try:
            tree = ast.parse(code)
            
            if concept == '반복문':
                return any(isinstance(node, (ast.For, ast.While)) for node in ast.walk(tree))
            elif concept == '조건문':
                return any(isinstance(node, ast.If) for node in ast.walk(tree))
            elif concept == '입력처리':
                return 'input' in code
            elif concept == '출력':
                return 'print' in code
            elif concept == '정렬':
                return 'sort' in code or 'sorted' in code
            elif concept == '탐색':
                return 'in ' in code or 'find' in code or 'index' in code
            elif concept == '연산':
                return any(isinstance(node, ast.BinOp) for node in ast.walk(tree))
        except:
            return False
        
        return False
    
    def get_error_details(self, code: str) -> List[str]:
        """상세 오류 메시지"""
        details = []
        
        if not code.strip():
            details.append("코드가 비어있습니다")
            return details
        
        # 문법 오류
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            details.append(f"문법 오류: {e.msg} (줄 {e.lineno})")
        except Exception as e:
            details.append(f"오류: {str(e)}")
        
        # 일반적인 실수 패턴 체크
        if code.count('(') != code.count(')'):
            details.append("괄호 개수가 맞지 않습니다")
        if code.count('[') != code.count(']'):
            details.append("대괄호 개수가 맞지 않습니다")
        if code.count('{') != code.count('}'):
            details.append("중괄호 개수가 맞지 않습니다")
        
        # 들여쓰기 체크
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if line and not line[0].isspace() and line[0] not in ['#', '\n']:
                # 이전 줄이 콜론으로 끝나는지 확인
                if i > 1 and lines[i-2].rstrip().endswith(':'):
                    if not line.startswith('    '):
                        details.append(f"들여쓰기 오류 가능성 (줄 {i})")
        
        return details
