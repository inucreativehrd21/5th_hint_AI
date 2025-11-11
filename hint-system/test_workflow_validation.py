"""
워크플로우 전체 검증 스크립트
- 임포트 체크
- 파라미터 전달 체크
- 메서드 시그니처 일치 확인
"""
import sys
import inspect


def test_imports():
    """임포트 검증"""
    print("=" * 60)
    print("🔍 Step 1: 임포트 검증")
    print("=" * 60)
    
    try:
        from models.educational_prompts import EducationalPromptEngine
        print("✅ EducationalPromptEngine 임포트 성공")
        
        from models.adaptive_prompt import AdaptivePromptGenerator
        print("✅ AdaptivePromptGenerator 임포트 성공")
        
        from models.model_inference import VLLMInference
        print("✅ VLLMInference 임포트 성공")
        
        return True, {
            'EducationalPromptEngine': EducationalPromptEngine,
            'AdaptivePromptGenerator': AdaptivePromptGenerator,
            'VLLMInference': VLLMInference
        }
    except Exception as e:
        print(f"❌ 임포트 실패: {e}")
        return False, {}


def test_method_signatures(classes):
    """메서드 시그니처 검증"""
    print("\n" + "=" * 60)
    print("🔍 Step 2: 메서드 시그니처 검증")
    print("=" * 60)
    
    # EducationalPromptEngine 메서드 확인
    edu_engine = classes['EducationalPromptEngine']
    
    print("\n📝 EducationalPromptEngine 메서드:")
    for method_name in ['generate_novice_prompt', 'generate_intermediate_prompt', 'generate_advanced_prompt']:
        method = getattr(edu_engine, method_name)
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        print(f"  - {method_name}({', '.join(params)})")
        
        # student_code 파라미터 확인
        if 'student_code' in params:
            print(f"    ✅ student_code 파라미터 존재 (위치: {params.index('student_code')})")
        else:
            print(f"    ❌ student_code 파라미터 없음!")
            return False
    
    # AdaptivePromptGenerator 메서드 확인
    print("\n📝 AdaptivePromptGenerator 메서드:")
    adaptive_gen = classes['AdaptivePromptGenerator']
    method = getattr(adaptive_gen, 'generate_prompt')
    sig = inspect.signature(method)
    params = list(sig.parameters.keys())
    print(f"  - generate_prompt({', '.join(params)})")
    
    if 'student_code' in params:
        print(f"    ✅ student_code 파라미터 존재 (위치: {params.index('student_code')})")
    else:
        print(f"    ❌ student_code 파라미터 없음!")
        return False
    
    return True


def test_parameter_passing():
    """파라미터 전달 로직 검증"""
    print("\n" + "=" * 60)
    print("🔍 Step 3: 파라미터 전달 로직 검증")
    print("=" * 60)
    
    # adaptive_prompt.py 파일 읽기
    with open('models/adaptive_prompt.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # student_code 전달 확인
    checks = [
        ('generate_novice_prompt', 'problem_info, diagnosis, weak_areas, chain_context, student_code'),
        ('generate_intermediate_prompt', 'problem_info, diagnosis, weak_areas, chain_context, student_code'),
        ('generate_advanced_prompt', 'problem_info, diagnosis, weak_areas, chain_context, student_code')
    ]
    
    all_passed = True
    for method_name, expected_params in checks:
        if expected_params in content:
            print(f"  ✅ {method_name}: student_code 전달 확인")
        else:
            print(f"  ❌ {method_name}: student_code 전달 확인 실패")
            all_passed = False
    
    return all_passed


def test_cot_parsing():
    """CoT 파싱 로직 검증"""
    print("\n" + "=" * 60)
    print("🔍 Step 4: CoT 파싱 로직 검증")
    print("=" * 60)
    
    # model_inference.py 파일 읽기
    with open('models/model_inference.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('import re', 're 임포트'),
        ('_extract_output_from_cot', 'CoT 파싱 메서드'),
        ('<output>', 'output 태그 파싱'),
        ('<thinking>', 'thinking 태그 파싱'),
        ('re.DOTALL', '멀티라인 지원')
    ]
    
    all_passed = True
    for check_string, description in checks:
        if check_string in content:
            print(f"  ✅ {description} 확인")
        else:
            print(f"  ❌ {description} 없음")
            all_passed = False
    
    return all_passed


def test_prompt_content():
    """프롬프트 내용 검증"""
    print("\n" + "=" * 60)
    print("🔍 Step 5: 프롬프트 내용 검증")
    print("=" * 60)
    
    # educational_prompts.py 파일 읽기
    with open('models/educational_prompts.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('{student_code}', '학생 코드 f-string 삽입'),
        ('<thinking>', 'CoT thinking 섹션'),
        ('<output>', 'CoT output 섹션'),
        ('1단계:', '단계별 사고 과정'),
        ('💡', 'Novice 이모지'),
        ('🧠', 'Intermediate 이모지'),
        ('🔍', 'Advanced 이모지')
    ]
    
    all_passed = True
    for check_string, description in checks:
        count = content.count(check_string)
        if count > 0:
            print(f"  ✅ {description} 확인 (발견 {count}회)")
        else:
            print(f"  ❌ {description} 없음")
            all_passed = False
    
    return all_passed


def main():
    print("\n🚀 힌트 시스템 워크플로우 전체 검증 시작\n")
    
    results = []
    
    # 1. 임포트 검증
    success, classes = test_imports()
    results.append(('임포트', success))
    
    if not success:
        print("\n❌ 임포트 실패로 검증 중단")
        return
    
    # 2. 메서드 시그니처 검증
    success = test_method_signatures(classes)
    results.append(('메서드 시그니처', success))
    
    # 3. 파라미터 전달 검증
    success = test_parameter_passing()
    results.append(('파라미터 전달', success))
    
    # 4. CoT 파싱 검증
    success = test_cot_parsing()
    results.append(('CoT 파싱', success))
    
    # 5. 프롬프트 내용 검증
    success = test_prompt_content()
    results.append(('프롬프트 내용', success))
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("📊 최종 검증 결과")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"  {test_name:20s}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 모든 검증 통과! 워크플로우가 올바르게 구성되었습니다.")
    else:
        print("⚠️  일부 검증 실패. 위의 내용을 확인하세요.")
    print("=" * 60)


if __name__ == '__main__':
    main()
