"""
적응형 힌트 시스템 통합 테스트
- 코드 진단
- 적응형 프롬프트
- 힌트 검증
"""

import sys
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent))

from models.code_analyzer import CodeAnalyzer
from models.adaptive_prompt import AdaptivePromptGenerator
from models.hint_validator import HintValidator


def test_code_diagnosis():
    """코드 진단 테스트"""
    print("\n" + "=" * 60)
    print("📊 테스트 1: 코드 진단")
    print("=" * 60)
    
    analyzer = CodeAnalyzer()
    
    # 테스트 케이스 1: 거의 완성된 코드 (고급)
    student_code_1 = """
n = int(input())
result = 0
for i in range(1, n+1):
    result += i
print(result)
"""
    
    solution_code = """
n = int(input())
total = 0
for i in range(1, n+1):
    total += i
print(total)
"""
    
    problem_desc = "1부터 N까지의 합을 구하는 프로그램"
    
    diagnosis_1 = analyzer.diagnose(student_code_1, solution_code, problem_desc)
    
    print(f"\n✅ 테스트 케이스 1: 거의 완성된 코드")
    print(f"   유사도: {diagnosis_1.similarity:.1f}%")
    print(f"   문법 오류: {diagnosis_1.syntax_errors}개")
    print(f"   논리 오류: {diagnosis_1.logic_errors}개")
    print(f"   개념 이해도: {diagnosis_1.concept_level}/5")
    print(f"   판정 난이도: {diagnosis_1.level.upper()}")
    
    assert diagnosis_1.level == 'advanced', f"Expected 'advanced', got '{diagnosis_1.level}'"
    
    # 테스트 케이스 2: 문법 오류 많은 코드 (초급)
    student_code_2 = """
n = int(input(
result = 0
for i in range(1 n+1)
    result += i
print(result
"""
    
    diagnosis_2 = analyzer.diagnose(student_code_2, solution_code, problem_desc)
    
    print(f"\n✅ 테스트 케이스 2: 문법 오류 많음")
    print(f"   유사도: {diagnosis_2.similarity:.1f}%")
    print(f"   문법 오류: {diagnosis_2.syntax_errors}개")
    print(f"   논리 오류: {diagnosis_2.logic_errors}개")
    print(f"   개념 이해도: {diagnosis_2.concept_level}/5")
    print(f"   판정 난이도: {diagnosis_2.level.upper()}")
    
    assert diagnosis_2.level == 'novice', f"Expected 'novice', got '{diagnosis_2.level}'"
    
    # 테스트 케이스 3: 논리는 맞지만 구현 부족 (중급)
    student_code_3 = """
n = int(input())
# TODO: 합 계산
print("?")
"""
    
    diagnosis_3 = analyzer.diagnose(student_code_3, solution_code, problem_desc)
    
    print(f"\n✅ 테스트 케이스 3: 논리는 맞지만 구현 부족")
    print(f"   유사도: {diagnosis_3.similarity:.1f}%")
    print(f"   문법 오류: {diagnosis_3.syntax_errors}개")
    print(f"   논리 오류: {diagnosis_3.logic_errors}개")
    print(f"   개념 이해도: {diagnosis_3.concept_level}/5")
    print(f"   판정 난이도: {diagnosis_3.level.upper()}")
    
    assert diagnosis_3.level == 'intermediate' or diagnosis_3.level == 'novice', \
        f"Expected 'intermediate' or 'novice', got '{diagnosis_3.level}'"
    
    print("\n✅ 코드 진단 테스트 통과!")


def test_adaptive_prompt():
    """적응형 프롬프트 생성 테스트"""
    print("\n" + "=" * 60)
    print("✍️  테스트 2: 적응형 프롬프트 생성")
    print("=" * 60)
    
    from models.code_analyzer import CodeDiagnosis
    
    generator = AdaptivePromptGenerator()
    
    # Mock 진단 결과 (고급)
    diagnosis_adv = CodeDiagnosis(
        similarity=85.0,
        syntax_errors=0,
        logic_errors=0,
        concept_level=5,
        level='advanced',
        missing_concepts=[]
    )
    
    student_code = "n = int(input())\nprint(sum(range(1, n+1)))"
    solution_code = "n = int(input())\ntotal = sum(range(1, n+1))\nprint(total)"
    
    problem_info = {
        'problem_id': '1000',
        'title': '합 구하기',
        'description': '1부터 N까지의 합',
        'solutions': [{
            'logic_steps': [
                {'goal': '변수 초기화', 'code': 'total = 0'},
                {'goal': '반복문으로 합 계산', 'code': 'for i in range(1, n+1): total += i'}
            ]
        }]
    }
    
    prompt = generator.generate_prompt(
        problem_id='1000',
        student_code=student_code,
        solution_code=solution_code,
        problem_info=problem_info,
        diagnosis=diagnosis_adv
    )
    
    print(f"\n✅ 고급 레벨 프롬프트 생성 완료")
    print(f"   프롬프트 길이: {len(prompt)} 글자")
    print(f"   '열린 질문' 포함 여부: {'열린 질문' in prompt}")
    
    assert len(prompt) > 100, "프롬프트가 너무 짧습니다"
    assert '열린 질문' in prompt or '질문' in prompt, "질문 형식이 포함되지 않았습니다"
    
    print("\n✅ 적응형 프롬프트 생성 테스트 통과!")


def test_hint_validation():
    """힌트 검증 테스트"""
    print("\n" + "=" * 60)
    print("🔍 테스트 3: 힌트 품질 검증")
    print("=" * 60)
    
    validator = HintValidator()
    
    # 테스트 케이스 1: 유효한 초급 힌트
    valid_novice_hint = """
💡 힌트:
먼저 입력을 받아야 합니다. input() 함수를 사용하세요.

📝 함수명: int(), input()

💻 코드 예시:
n = int(input())
"""
    
    validation_1 = validator.validate_hint(valid_novice_hint, 'novice')
    
    print(f"\n✅ 테스트 케이스 1: 유효한 초급 힌트")
    print(f"   검증 통과: {validation_1.is_valid}")
    print(f"   점수: {validation_1.score:.1f}/100")
    print(f"   통과 항목: {len(validation_1.passed_checks)}개")
    print(f"   실패 항목: {len(validation_1.failed_checks)}개")
    
    # 테스트 케이스 2: 규약 위반 중급 힌트 (함수명 포함 금지)
    invalid_intermediate_hint = """
💡 힌트:
range() 함수를 사용하여 반복문을 만드세요.

📝 함수명: range(), sum()

💻 코드 예시:
for i in range(1, n+1):
    total += i
"""
    
    validation_2 = validator.validate_hint(invalid_intermediate_hint, 'intermediate')
    
    print(f"\n✅ 테스트 케이스 2: 규약 위반 중급 힌트")
    print(f"   검증 통과: {validation_2.is_valid}")
    print(f"   점수: {validation_2.score:.1f}/100")
    print(f"   실패 항목: {validation_2.failed_checks}")
    
    assert not validation_2.is_valid, "중급 힌트에 함수명이 포함되어야 실패해야 함"
    
    # 자동 수정 테스트
    print(f"\n🔧 자동 수정 시도 중...")
    fixed_hint = validator.auto_fix_hint(invalid_intermediate_hint, 'intermediate')
    validation_fixed = validator.validate_hint(fixed_hint, 'intermediate')
    
    print(f"   수정 후 검증: {validation_fixed.is_valid}")
    print(f"   수정 후 점수: {validation_fixed.score:.1f}/100")
    
    print("\n✅ 힌트 품질 검증 테스트 통과!")


def test_chain_of_hints():
    """Chain-of-Hints 테스트"""
    print("\n" + "=" * 60)
    print("🔗 테스트 4: Chain-of-Hints")
    print("=" * 60)
    
    from models.code_analyzer import CodeDiagnosis
    
    generator = AdaptivePromptGenerator()
    
    # 같은 문제에 대해 여러 번 힌트 생성
    problem_id = '1000'
    
    diagnosis = CodeDiagnosis(
        similarity=30.0,
        syntax_errors=5,
        logic_errors=3,
        concept_level=2,
        level='novice',
        missing_concepts=['반복문', '변수']
    )
    
    print(f"\n📝 1차 힌트 생성 (novice)")
    generator.record_hint(
        problem_id=problem_id,
        hint="첫 번째 초급 힌트",
        level='novice',
        student_code="# 코드 1"
    )
    
    chain = generator.chains[problem_id]
    print(f"   현재 레벨: {chain.current_level}")
    print(f"   동일 레벨 카운트: {chain.same_level_count}")
    
    print(f"\n📝 2차 힌트 생성 (novice)")
    generator.record_hint(
        problem_id=problem_id,
        hint="두 번째 초급 힌트",
        level='novice',
        student_code="# 코드 2"
    )
    
    print(f"   현재 레벨: {chain.current_level}")
    print(f"   동일 레벨 카운트: {chain.same_level_count}")
    
    print(f"\n📝 3차 힌트 생성 (novice → intermediate 자동 상승 예상)")
    generator.record_hint(
        problem_id=problem_id,
        hint="세 번째 힌트",
        level='novice',
        student_code="# 코드 3"
    )
    
    print(f"   현재 레벨: {chain.current_level}")
    print(f"   동일 레벨 카운트: {chain.same_level_count}")
    
    # 에스컬레이션 확인
    should_escalate = generator.should_escalate_level(problem_id, 'intermediate')
    print(f"\n🔝 에스컬레이션 필요 여부: {should_escalate}")
    
    assert len(chain.hints) == 3, f"Expected 3 hints, got {len(chain.hints)}"
    
    print("\n✅ Chain-of-Hints 테스트 통과!")


def main():
    """전체 통합 테스트 실행"""
    print("\n" + "=" * 60)
    print("🚀 적응형 힌트 시스템 통합 테스트 시작")
    print("=" * 60)
    
    try:
        test_code_diagnosis()
        test_adaptive_prompt()
        test_hint_validation()
        test_chain_of_hints()
        
        print("\n" + "=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)
        print("\n시스템이 정상적으로 작동합니다. 🎉")
        print("\n다음 단계:")
        print("1. vLLM 서버 시작: docker-compose up -d")
        print("2. Gradio UI 실행: python app.py")
        print("3. 웹 브라우저에서 http://localhost:7860 접속")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
