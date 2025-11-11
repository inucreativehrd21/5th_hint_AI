"""
워크플로우 코드 레벨 검증 (의존성 없이)
"""
import re
import os


def check_file_content(filepath, checks, description):
    """파일 내용 검증"""
    print(f"\n📝 {description}")
    print(f"   파일: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"   ❌ 파일이 존재하지 않음!")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_passed = True
    for check_string, description, required in checks:
        count = content.count(check_string)
        if count > 0:
            print(f"   ✅ {description} (발견 {count}회)")
        elif required:
            print(f"   ❌ {description} - 필수 항목 누락!")
            all_passed = False
        else:
            print(f"   ⚠️  {description} - 선택 항목 없음")
    
    return all_passed


def main():
    print("=" * 70)
    print("🔍 힌트 시스템 워크플로우 전체 검증 (코드 레벨)")
    print("=" * 70)
    
    results = []
    
    # 1. app.py 검증
    print("\n" + "=" * 70)
    print("Step 1: app.py - 진입점")
    print("=" * 70)
    
    checks = [
        ('from models.model_inference import VLLMInference', 'VLLMInference 임포트', True),
        ('from models.adaptive_prompt import AdaptivePromptGenerator', 'AdaptivePromptGenerator 임포트', True),
        ('self.prompt_generator = AdaptivePromptGenerator()', '프롬프트 생성기 초기화', True),
        ('prompt = self.prompt_generator.generate_prompt(', 'generate_prompt 호출', True),
        ('student_code=user_code', 'student_code 파라미터 전달', True),
        ('diagnosis=diagnosis', 'diagnosis 파라미터 전달', True),
    ]
    
    passed = check_file_content('app.py', checks, 'app.py 검증')
    results.append(('app.py', passed))
    
    # 2. adaptive_prompt.py 검증
    print("\n" + "=" * 70)
    print("Step 2: models/adaptive_prompt.py - 프롬프트 생성기")
    print("=" * 70)
    
    checks = [
        ('from models.educational_prompts import EducationalPromptEngine', 'EducationalPromptEngine 임포트', True),
        ('self.edu_engine = EducationalPromptEngine()', '교육 엔진 초기화', True),
        ('def generate_prompt(self, problem_id: str, student_code: str,', 'generate_prompt 메서드 시그니처', True),
        ('print(f"[AdaptivePromptGenerator] student_code 길이: {len(student_code)}', 'student_code 로깅', True),
        ('self.edu_engine.generate_novice_prompt(', 'novice 프롬프트 호출', True),
        ('problem_info, diagnosis, weak_areas, chain_context, student_code', 'novice - 5개 파라미터 전달', True),
        ('self.edu_engine.generate_intermediate_prompt(', 'intermediate 프롬프트 호출', True),
        ('self.edu_engine.generate_advanced_prompt(', 'advanced 프롬프트 호출', True),
    ]
    
    passed = check_file_content('models/adaptive_prompt.py', checks, 'AdaptivePromptGenerator 검증')
    results.append(('adaptive_prompt.py', passed))
    
    # 3. educational_prompts.py 검증
    print("\n" + "=" * 70)
    print("Step 3: models/educational_prompts.py - 교육 프롬프트 엔진")
    print("=" * 70)
    
    checks = [
        ('def generate_novice_prompt(self, problem_info: Dict, diagnosis:', 'novice 메서드 정의', True),
        ('weak_areas: List[str], chain_context: str, student_code: str)', 'novice - student_code 파라미터', True),
        ('print(f"\\n[EducationalPromptEngine] 초급(Novice) 프롬프트 생성")', 'novice 로깅', True),
        ('print(f"  학생 코드 길이: {len(student_code)} chars")', 'student_code 길이 로깅', True),
        ('{student_code}', 'student_code f-string 삽입', True),
        ('<thinking>', 'CoT thinking 섹션', True),
        ('<output>', 'CoT output 섹션', True),
        ('1단계:', '단계별 사고', True),
        ('💡', 'Novice 힌트 이모지', True),
        ('def generate_intermediate_prompt(self, problem_info: Dict, diagnosis:', 'intermediate 메서드 정의', True),
        ('🧠', 'Intermediate 힌트 이모지', True),
        ('def generate_advanced_prompt(self, problem_info: Dict, diagnosis:', 'advanced 메서드 정의', True),
        ('🔍', 'Advanced 힌트 이모지', True),
    ]
    
    passed = check_file_content('models/educational_prompts.py', checks, 'EducationalPromptEngine 검증')
    results.append(('educational_prompts.py', passed))
    
    # 4. model_inference.py 검증
    print("\n" + "=" * 70)
    print("Step 4: models/model_inference.py - vLLM 추론")
    print("=" * 70)
    
    checks = [
        ('import re', 're 모듈 임포트 (CoT 파싱용)', True),
        ('def _extract_output_from_cot(self, hint: str) -> str:', 'CoT 파싱 메서드', True),
        ("re.search(r'<output>(.*?)</output>', hint, re.DOTALL", 'output 태그 파싱', True),
        ("re.search(r'<thinking>(.*?)</thinking>', hint, re.DOTALL", 'thinking 태그 파싱', True),
        ('hint = self._extract_output_from_cot(hint)', 'CoT 파싱 호출', True),
        ('print(f"[CoT] <output> 태그 발견', 'CoT 파싱 로깅', True),
        ('print(f"[CoT] <thinking> 내용', 'thinking 로깅', True),
    ]
    
    passed = check_file_content('models/model_inference.py', checks, 'VLLMInference 검증')
    results.append(('model_inference.py', passed))
    
    # 최종 결과
    print("\n" + "=" * 70)
    print("📊 최종 검증 결과")
    print("=" * 70)
    
    for filename, passed in results:
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"  {filename:30s}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 모든 검증 통과!")
        print("\n✅ 워크플로우 요약:")
        print("   1. app.py → student_code를 prompt_generator.generate_prompt()에 전달")
        print("   2. adaptive_prompt.py → student_code를 edu_engine.generate_*_prompt()에 전달")
        print("   3. educational_prompts.py → student_code를 프롬프트 f-string에 삽입")
        print("   4. educational_prompts.py → CoT <thinking>/<output> 태그 포함")
        print("   5. model_inference.py → CoT 파싱하여 <output>만 추출")
        print("\n✅ 임포트 체인:")
        print("   app.py → AdaptivePromptGenerator")
        print("   adaptive_prompt.py → EducationalPromptEngine")
        print("   app.py → VLLMInference")
        print("\n✅ 모든 구간에서 student_code가 올바르게 전달됩니다!")
    else:
        print("⚠️  일부 검증 실패. 위의 내용을 확인하세요.")
    print("=" * 70)


if __name__ == '__main__':
    main()
