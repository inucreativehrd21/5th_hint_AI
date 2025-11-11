"""
vLLM Docker 기반 적응형 힌트 생성 시스템 (리팩토링 V3)
- 교육학적 프롬프트 엔진 통합
- 보안 가드 시스템
- 프롬프트 엔지니어링 + 에듀테크 박사 관점
"""
import argparse
import gradio as gr
import json
import os
import sys
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from config import Config
from models.model_inference import VLLMInference
from models.code_analyzer import CodeAnalyzer, CodeDiagnosis
from models.adaptive_prompt import AdaptivePromptGenerator
from models.hint_validator import HintValidator
from models.security_guard import get_security_guard


class VLLMHintApp:
    """vLLM 전용 적응형 힌트 생성 애플리케이션"""

    def __init__(self, data_path: str, vllm_url: str = None):
        self.data_path = data_path
        self.problems = self.load_problems()
        
        # vLLM 서버 URL 설정
        self.vllm_url = vllm_url or os.getenv('VLLM_SERVER_URL', 'http://localhost:8000/v1')
        
        self.current_problem = None
        self.current_model = None
        self.current_problem_id = None
        
        # 새로운 모듈 초기화
        self.analyzer = CodeAnalyzer()
        self.prompt_generator = AdaptivePromptGenerator()
        self.validator = HintValidator()
        self.security_guard = get_security_guard()  # 보안 가드

        # vLLM 서버 연결 체크
        self.check_vllm_connection()

    def check_vllm_connection(self):
        """vLLM 서버 연결 확인 (강화된 에러 핸들링)"""
        try:
            # 환경변수 또는 기본값에서 모델 이름 읽기
            model_name = os.getenv('VLLM_MODEL', 'Qwen/Qwen2.5-Coder-7B-Instruct')
            
            print(f"🔗 vLLM 서버 연결 시도: {self.vllm_url}")
            print(f"📦 사용 모델: {model_name}")
            
            self.current_model = VLLMInference(
                model_name=model_name,
                base_url=self.vllm_url,
                timeout=60
            )
            
            # 간단한 연결 테스트 (health endpoint)
            try:
                health_url = self.vllm_url.replace('/v1', '/health')
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ vLLM 서버 연결 성공: {self.vllm_url}")
                else:
                    print(f"⚠️  vLLM 서버 응답 이상: HTTP {response.status_code}")
            except requests.exceptions.RequestException:
                # health 엔드포인트가 없을 수 있으므로 경고만 출력
                print(f"⚠️  vLLM 서버 헬스체크 실패 (모델은 정상 로드됨)")
                
        except Exception as e:
            print(f"❌ vLLM 서버 연결 실패: {e}")
            print(f"   서버 URL: {self.vllm_url}")
            print(f"   확인사항:")
            print(f"   1. vLLM 서버가 실행 중인지 확인")
            print(f"   2. 환경 변수 VLLM_SERVER_URL 확인")
            print(f"   3. Docker Compose 사용 시: docker-compose logs vllm-server")
            self.current_model = None

    def load_problems(self) -> List[Dict]:
        """문제 데이터 로드 (에러 핸들링 강화)"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                problems = json.load(f)
            print(f"✅ 문제 데이터 로드 성공: {len(problems)}개")
            return problems
        except FileNotFoundError:
            print(f"❌ 데이터 파일을 찾을 수 없습니다: {self.data_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 데이터 로드 중 오류: {e}")
            sys.exit(1)

    def get_problem_list(self) -> List[str]:
        """문제 목록"""
        return [
            f"#{p['problem_id']} - {p['title']} (Level {p['level']})"
            for p in self.problems
        ]

    def load_problem(self, problem_selection: str):
        """선택된 문제 로드 (인스턴스 변수에도 저장)"""
        if not problem_selection:
            print("⚠️ [load_problem] 문제가 선택되지 않음")
            self.current_problem = None
            self.current_problem_id = None
            return "문제를 선택하세요.", "", None, "⚠️ **현재 선택된 문제:** 없음"

        try:
            # 문자열로 파싱 (JSON에서 problem_id가 문자열로 저장됨)
            problem_id_str = problem_selection.split('#')[1].split(' -')[0].strip()
            print(f"✅ [load_problem] 문제 ID 파싱 성공: {problem_id_str} (문자열)")

            self.current_problem = None
            for p in self.problems:
                # 문자열 비교 (JSON의 problem_id가 문자열)
                if str(p['problem_id']) == problem_id_str:
                    self.current_problem = p
                    break

            if not self.current_problem:
                print(f"❌ [load_problem] 문제를 찾을 수 없음: {problem_id_str}")
                print(f"   JSON의 첫 번째 문제 ID: {self.problems[0]['problem_id']} (타입: {type(self.problems[0]['problem_id']).__name__})")
                self.current_problem_id = None
                return "❌ 문제를 찾을 수 없습니다.", "", None, "❌ 문제를 찾을 수 없습니다."

            # 인스턴스 변수에 저장 (문자열로 저장)
            self.current_problem_id = problem_id_str
            
            print(f"✅ [load_problem] 문제 로드 완료: {self.current_problem['title']}")
            print(f"✅ [load_problem] 인스턴스 변수 저장: self.current_problem_id = {self.current_problem_id}")
            
            problem_md = self._format_problem_display()
            debug_msg = f"✅ **현재 선택된 문제 ID:** `{problem_id_str}` (타입: `str`)"
            
            # 4개 값 반환: 문제, 코드 템플릿, State용 problem_id, 디버그 메시지
            return problem_md, "# 여기에 코드를 작성하세요\n", problem_id_str, debug_msg

        except Exception as e:
            print(f"❌ [load_problem] 예외 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            self.current_problem_id = None
            return f"❌ 오류: {str(e)}", "", None, f"❌ 오류: {str(e)}"

    def _format_problem_display(self) -> str:
        """문제 표시 포맷"""
        p = self.current_problem
        md = f"""# {p['title']}

**난이도:** Level {p['level']} | **태그:** {', '.join(p['tags'])}

---

## 📋 문제 설명
{p['description']}

## 📥 입력
{p['input_description']}

## 📤 출력
{p['output_description']}

## 💡 예제
"""
        for i, example in enumerate(p['examples'], 1):
            input_txt = example.get('input', '') if example.get('input') else '(없음)'
            output_txt = example.get('output', '') if example.get('output') else '(없음)'
            md += f"\n**예제 {i}**\n```\n입력: {input_txt}\n출력: {output_txt}\n```\n"

        return md

    def generate_hint(self, user_code: str, temperature: float, problem_id, selected_level: str, user_id: str = "anonymous"):
        """
        힌트 내용 자동 구성 (리팩토링 V3 - 교육학적 + 보안)
        - 보안 가드: 악질 사용자 필터링
        - 교육학적 프롬프트 엔진: ZPD, Scaffolding, Metacognition
        - 4가지 지표 진단 → 부족한 영역 맞춤 힌트
        - Chain-of-Hints (COT 누적 학습)
        """
        print(f"\n🔍 [generate_hint] 힌트 생성 시작 (사용자: {user_id})")
        print(f"   선택된 난이도: {selected_level.upper()}")
        
        # === 보안 검증 (STEP 0) ===
        print("🛡️ [STEP 0] 보안 검증 중...")
        is_valid, validation_msg = self.security_guard.validate_hint_request(
            code=user_code,
            problem_id=problem_id,
            selected_level=selected_level,
            user_id=user_id
        )
        
        if not is_valid:
            print(f"❌ 보안 검증 실패: {validation_msg}")
            return self._error_response(validation_msg)
        
        if "⚠️ 경고" in validation_msg:
            print(f"{validation_msg}")
        
        # 사용량 통계
        usage_stats = self.security_guard.get_usage_stats(user_id)
        print(f"   사용량: {usage_stats['requests_last_minute']}/{self.security_guard.max_requests_per_minute} (분), "
              f"{usage_stats['requests_last_hour']}/{self.security_guard.max_requests_per_hour} (시간)")
        
        # problem_id 검증
        if problem_id is None:
            problem_id = self.current_problem_id
            
        if problem_id is None:
            return self._error_response("❌ 먼저 문제를 선택해주세요.")
        
        # 문제 찾기
        self.current_problem = self._find_problem(problem_id)
        if not self.current_problem:
            return self._error_response(f"❌ 문제를 찾을 수 없습니다. (ID: {problem_id})")
        
        # vLLM 모델 검증
        if not self.current_model:
            return self._error_response("❌ vLLM 서버에 연결되지 않았습니다.")
        
        try:
            # === 단계 1: 4가지 지표 진단 ===
            print("📊 [단계 1] 코드 4가지 지표 진단 중...")
            solution_code = self._get_solution_code()
            problem_desc = self.current_problem.get('description', '')
            
            diagnosis = self.analyzer.diagnose(
                student_code=user_code,
                solution_code=solution_code,
                problem_description=problem_desc
            )
            
            print(f"   유사도: {diagnosis.similarity:.1f}%")
            print(f"   문법 오류: {diagnosis.syntax_errors}개")
            print(f"   논리 오류: {diagnosis.logic_errors}개")
            print(f"   개념 이해도: {diagnosis.concept_level}/5")
            
            # 난이도 적합성 체크
            is_suitable, suitability_msg = diagnosis.is_suitable_for_level(selected_level)
            print(f"   난이도 적합성: {suitability_msg}")
            
            # === 단계 2: 교육학적 프롬프트 생성 ===
            print(f"✍️  [단계 2] {selected_level.upper()} 교육학적 힌트 프롬프트 생성 중...")
            weak_areas = diagnosis.get_weak_areas_for_level(selected_level)
            print(f"   부족한 영역: {', '.join(weak_areas)}")
            
            prompt = self.prompt_generator.generate_prompt(
                problem_id=problem_id,
                student_code=user_code,
                solution_code=solution_code,
                problem_info=self.current_problem,
                diagnosis=diagnosis,
                selected_level=selected_level
            )
            
            print(f"   프롬프트 길이: {len(prompt)} 글자")
            print(f"   프롬프트 첫 500자: {prompt[:500]}...")
            
            # === 단계 3: vLLM 추론 ===
            print("🤖 [단계 3] vLLM 추론 중...")
            start_time = time.time()
            
            result = self.current_model.generate_hint(
                prompt=prompt,
                max_tokens=512,
                temperature=temperature
            )
            
            elapsed_time = time.time() - start_time
            
            if result.get('error'):
                return self._error_response(f"❌ 생성 실패: {result['error']}")
            
            raw_hint = result.get('hint', '(빈 응답)')
            
            # === 단계 4: 힌트 품질 검증 ===
            print("🔍 [단계 4] 힌트 품질 검증 중...")
            validation = self.validator.validate_hint(raw_hint, selected_level)
            
            # 자동 수정 시도
            if not validation.is_valid:
                print("⚠️  품질 검증 실패, 자동 수정 시도...")
                raw_hint = self.validator.auto_fix_hint(raw_hint, selected_level)
                validation = self.validator.validate_hint(raw_hint, selected_level)
            
            # === 단계 5: 힌트 기록 (Chain-of-Hints) ===
            self.prompt_generator.record_hint(
                problem_id=problem_id,
                hint=raw_hint,
                level=selected_level,
                student_code=user_code
            )
            
            # === 최종 출력 포맷팅 ===
            hint_output = self._format_hint_output(
                hint=raw_hint,
                selected_level=selected_level,
                diagnosis=diagnosis,
                validation=validation,
                elapsed_time=elapsed_time,
                temperature=temperature,
                suitability_msg=suitability_msg
            )
            
            metrics_output = self._format_metrics(
                diagnosis=diagnosis,
                selected_level=selected_level,
                validation=validation,
                elapsed_time=elapsed_time,
                temperature=temperature,
                weak_areas=weak_areas
            )
            
            print(f"✅ [완료] 힌트 생성 성공 ({elapsed_time:.2f}초)")
            
            # 힌트 히스토리 생성
            history_output = self._format_hint_history(problem_id)
            
            return hint_output, metrics_output, history_output
            
        except Exception as e:
            print(f"❌ [오류] {str(e)}")
            import traceback
            traceback.print_exc()
            return self._error_response(f"❌ 오류 발생: {str(e)}"), "", ""
    
    def _format_hint_history(self, problem_id: str) -> str:
        """힌트 히스토리 포맷팅"""
        chain = self.prompt_generator.hint_chains.get(problem_id)
        
        if not chain or not chain.hints:
            return """# 📚 힌트 히스토리

아직 힌트가 생성되지 않았습니다. 첫 힌트를 요청해보세요!
"""
        
        level_emoji = {
            'novice': '🔰',
            'intermediate': '📚',
            'advanced': '🎓'
        }
        
        level_name = {
            'novice': '초급',
            'intermediate': '중급',
            'advanced': '고급'
        }
        
        output = f"""# 📚 힌트 히스토리 (Chain-of-Hints)

총 **{len(chain.hints)}개**의 힌트가 제공되었습니다.

---

"""
        
        for i, record in enumerate(chain.hints, 1):
            emoji = level_emoji.get(record.level, '💡')
            name = level_name.get(record.level, record.level)
            
            output += f"""### {i}. {emoji} {name} 힌트
**생성 시각:** {record.timestamp}

<details>
<summary>힌트 내용 보기</summary>

{record.hint_text}

</details>

---

"""
        
        # 에스컬레이션 경고 (실제 데이터로 계산)
        if len(chain.hints) >= 2:
            # 마지막 2개 힌트의 레벨 확인
            recent_levels = [h.level for h in chain.hints[-2:]]
            if len(set(recent_levels)) == 1:  # 모두 같은 레벨
                current_level = recent_levels[0]
                same_count = sum(1 for h in chain.hints if h.level == current_level)
                output += f"""
⚠️ **알림:** 동일 난이도({level_name.get(current_level, current_level)})에서 {same_count}회 힌트를 요청했습니다.
다음 힌트 요청 시 자동으로 다음 단계로 상승합니다! 💪
"""
        
        return output
    
    def _find_problem(self, problem_id: str):
        """문제 ID로 문제 찾기"""
        for p in self.problems:
            if str(p['problem_id']) == str(problem_id):
                return p
        return None
    
    def _get_solution_code(self) -> str:
        """해결 코드 추출"""
        solutions = self.current_problem.get('solutions', [])
        if solutions and solutions[0].get('solution_code'):
            return solutions[0]['solution_code']
        return ""
    
    def _error_response(self, message: str):
        """오류 응답 (3개 출력)"""
        return message, "", ""
    
    def _format_hint_output(self, hint: str, selected_level: str, 
                           diagnosis: CodeDiagnosis, validation,
                           elapsed_time: float, temperature: float,
                           suitability_msg: str) -> str:
        """힌트 출력 포맷팅 (리팩토링 v2)"""
        level_emoji = {
            'novice': '🔰',
            'intermediate': '📚',
            'advanced': '🎓'
        }
        
        level_name = {
            'novice': '초급',
            'intermediate': '중급',
            'advanced': '고급'
        }
        
        emoji = level_emoji.get(selected_level, '💡')
        name = level_name.get(selected_level, selected_level)
        
        output = f"""# {emoji} {name} 힌트 (사용자 선택)

{hint}

---

### 💬 난이도 적합성
{suitability_msg}

### 💪 격려 메시지
{"🌱 기초부터 차근차근 배워가세요! 작은 진전도 큰 성장의 시작입니다." if selected_level == 'novice' else 
 "📈 점점 나아지고 있습니다! 조금만 더 노력하면 완성할 수 있어요." if selected_level == 'intermediate' else
 "🏆 거의 다 왔습니다! 마지막 단계를 넘어서세요!"}

계속 도전하세요! 🚀
"""
        
        if not validation.is_valid:
            output += f"\n\n⚠️ **품질 검증:** 일부 기준 미달 (점수: {validation.score:.1f}/100)"
        
        return output
    
    def _format_metrics(self, diagnosis: CodeDiagnosis, selected_level: str,
                       validation, elapsed_time: float, temperature: float,
                       weak_areas: List[str]) -> str:
        """메트릭스 출력 포맷팅 (리팩토링 v2)"""
        level_name = {
            'novice': '초급 (Novice)',
            'intermediate': '중급 (Intermediate)',
            'advanced': '고급 (Advanced)'
        }
        
        return f"""## 📊 코드 4가지 지표 진단

### 정량적 분석:
- **코드 유사도:** {diagnosis.similarity:.1f}% {'✅' if diagnosis.similarity >= 60 else '⚠️'}
- **문법 오류:** {diagnosis.syntax_errors}개 {'✅' if diagnosis.syntax_errors == 0 else '⚠️'}
- **논리 오류:** {diagnosis.logic_errors}개 {'✅' if diagnosis.logic_errors == 0 else '⚠️'}
- **개념 이해도:** {diagnosis.concept_level}/5점 {'✅' if diagnosis.concept_level >= 4 else '⚠️'}

### 사용자 선택 난이도:
**{level_name.get(selected_level, selected_level)}**

### 부족한 영역 (힌트 집중 포인트):
{chr(10).join(f"- {area}" for area in weak_areas)}

### 누락된 개념:
{', '.join(diagnosis.missing_concepts) if diagnosis.missing_concepts else '✅ 모든 핵심 개념 포함'}

---

## ⚡ 추론 성능
- **소요 시간:** {elapsed_time:.3f}초
- **Temperature:** {temperature}
- **Model:** {self.current_model.model_name}

---

## 🎯 힌트 품질
- **검증 점수:** {validation.score:.1f}/100점
- **상태:** {'✅ 통과' if validation.is_valid else '⚠️ 개선 필요'}
"""

    def _create_hint_prompt(self, user_code: str) -> str:
        """Socratic V6 프롬프트 생성"""
        p = self.current_problem

        # 첫 번째 solution 사용
        solutions = p.get('solutions', [])
        if not solutions:
            next_step = "문제 해결"
        else:
            solution = solutions[0]
            logic_steps = solution.get('logic_steps', [])
            if logic_steps:
                next_step = logic_steps[0].get('goal', '문제 해결')
            else:
                next_step = "문제 해결"

        prompt = f"""당신은 학생의 호기심을 자극하고 스스로 발견하게 만드는 창의적 멘토입니다.

### 학생의 현재 코드:
```python
{user_code}
```

### 핵심 미션:
학생이 다음 단계인 "{next_step}"의 필요성을 **스스로 깨닫고 열망하도록** 만드세요.
직접 답을 주지 말고, 학생의 상상력과 호기심을 폭발시키는 질문을 던지세요.

### 동기 유발 전략 (반드시 적용):

1. **규모 확장 시나리오**
   - 지금은 작동하지만, 데이터가 1000배 늘어나면?
   - 사용자가 100만 명이 되면?

2. **실생활 연결**
   - 유튜브는 수백만 영상을 어떻게 관리할까?
   - 게임에서 아이템이 수천 개면 어떻게 처리할까?

3. **불편함 자극**
   - 같은 코드를 100번 복사해야 한다면?
   - 매번 손으로 하나씩 확인해야 한다면?

4. **호기심 유발**
   - 왜 프로 개발자들은 항상 이 패턴을 사용할까?
   - 더 똑똑한 방법이 있다면 어떻게 보일까?

5. **성취감 예고**
   - 이것만 해결하면 훨씬 강력해질 텐데
   - 한 줄만 바꾸면 모든 걸 자동화할 수 있는데

### 절대 금지 사항:
❌ 함수명, 변수명, 코드 키워드 직접 언급
❌ "for 반복문", "if 조건문" 같은 기술 용어
❌ "~를 사용하세요", "~를 추가하세요" 같은 직접 지시
❌ 정답의 힌트가 되는 구체적 표현
❌ 예시 코드 조각

### 출력 형식:
단 1개의 질문만 작성하세요. 설명, 답변, 추가 힌트 일체 금지.
질문은 30-50단어 이내로 간결하면서도 강렬하게.

질문:"""
        return prompt


def create_vllm_ui(app: VLLMHintApp):
    """vLLM 전용 단순화 UI"""

    with gr.Blocks(title="vLLM 고속 힌트 생성", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# ⚡ vLLM 고속 힌트 생성 시스템")
        gr.Markdown("vLLM 서버를 통한 15-24배 빠른 추론 테스트")

        # vLLM 연결 상태
        if app.current_model:
            gr.Markdown(f"✅ **vLLM 서버 연결됨:** `{app.vllm_url}`")
        else:
            gr.Markdown(f"⚠️ **vLLM 서버 미연결:** `{app.vllm_url}` - 서버를 시작하세요!")

        gr.Markdown("---")

        # 문제 선택
        with gr.Row():
            problem_dropdown = gr.Dropdown(
                choices=app.get_problem_list(),
                label="📚 문제 선택",
                interactive=True,
                value=None,
                scale=3
            )
            load_btn = gr.Button("📂 불러오기", variant="primary", scale=1)

        problem_display = gr.Markdown("")
        
        # 문제 ID를 저장하는 State (숨겨진 상태)
        current_problem_id = gr.State(value=None)
        
        # 디버깅: 현재 선택된 문제 ID 표시
        debug_info = gr.Markdown("⚠️ **현재 선택된 문제:** 없음 (문제를 선택하세요)", visible=True)

        gr.Markdown("---")

        # 코드 입력
        gr.Markdown("## 💻 코드 작성")
        user_code = gr.Code(
            label="Python 코드",
            language="python",
            lines=12,
            value="# 여기에 코드를 작성하세요\n"
        )

        # Temperature 조절
        gr.Markdown("### 🌡️ Temperature (창의성 조절)")
        temperature_slider = gr.Slider(
            minimum=0.1,
            maximum=1.0,
            value=0.75,
            step=0.05,
            label="Temperature",
            info="낮을수록 일관적, 높을수록 창의적",
            interactive=True
        )

        # 난이도 선택 (리팩토링 v2 - 사용자 직접 선택)
        gr.Markdown("---")
        gr.Markdown("## 💡 힌트 난이도 선택")
        gr.Markdown("""
**자신에게 필요한 힌트 수준을 선택하세요:**
- 🔰 **초급**: 기초적인 힌트와 함수명, 코드 예시 제공 (처음 시작하거나 막막할 때)
- 📚 **중급**: 추상적 힌트와 개념 설명 (어느 정도 진행했지만 막힌 부분이 있을 때)
- 🎓 **고급**: 소크라테스식 질문과 사고 유도 (거의 완성했거나 스스로 해결하고 싶을 때)
        """)
        
        with gr.Row():
            hint_btn_novice = gr.Button("� 초급 힌트", variant="secondary", scale=1)
            hint_btn_intermediate = gr.Button("📚 중급 힌트", variant="secondary", scale=1)
            hint_btn_advanced = gr.Button("🎓 고급 힌트", variant="primary", scale=1)

        gr.Markdown("---")

        # 결과 탭 (개선된 UI)
        with gr.Tabs() as result_tabs:
            # 탭 1: 생성된 힌트
            with gr.Tab("🎯 생성된 힌트"):
                hint_output = gr.Markdown(
                    "_힌트가 여기에 표시됩니다_\n\n"
                    "💡 **사용 방법:**\n"
                    "1. 위에서 문제를 선택하고 '불러오기'를 클릭하세요.\n"
                    "2. 코드를 작성한 후 '힌트 생성' 버튼을 클릭하세요.\n"
                    "3. AI가 자동으로 코드를 진단하고 적절한 난이도의 힌트를 제공합니다!"
                )
            
            # 탭 2: 코드 진단 & 성능
            with gr.Tab("📊 진단 결과"):
                metrics_output = gr.Markdown(
                    "_코드 진단 결과가 여기에 표시됩니다_\n\n"
                    "진단 항목:\n"
                    "- 코드 유사도 (AST 기반)\n"
                    "- 문법/논리 오류 분석\n"
                    "- 개념 이해도 평가\n"
                    "- 자동 난이도 판정\n"
                    "- 누락된 개념 식별\n\n"
                    "추론 성능:\n"
                    "- vLLM 응답 시간\n"
                    "- 모델 정보\n\n"
                    "힌트 품질:\n"
                    "- 자동 품질 검증 점수\n"
                    "- 규약 준수 여부"
                )
            
            # 탭 3: 힌트 히스토리 (Chain-of-Hints)
            with gr.Tab("� 힌트 히스토리"):
                history_output = gr.Markdown(
                    "_이 문제에 대한 이전 힌트가 여기에 표시됩니다_\n\n"
                    "Chain-of-Hints:\n"
                    "- 이전에 제공된 힌트 목록\n"
                    "- 난이도 변화 추적\n"
                    "- 학습 진행도 확인\n\n"
                    "💡 동일한 난이도에서 3회 힌트 요청 시 자동으로 다음 단계로 상승합니다!"
                )

        # 이벤트 핸들러
        # 1. 불러오기 버튼 클릭 시 문제 로드
        load_btn.click(
            fn=app.load_problem,
            inputs=[problem_dropdown],
            outputs=[problem_display, user_code, current_problem_id, debug_info]
        )
        
        # 2. 드롭다운에서 문제 선택 시에도 자동 로드 (편의 기능)
        problem_dropdown.select(
            fn=app.load_problem,
            inputs=[problem_dropdown],
            outputs=[problem_display, user_code, current_problem_id, debug_info]
        )

        # 3. 난이도별 힌트 생성 버튼 (리팩토링 V3 - 교육학적 + 보안)
        # 초급 힌트
        hint_btn_novice.click(
            fn=lambda code, temp, pid: app.generate_hint(code, temp, pid, 'novice', user_id="anonymous"),
            inputs=[user_code, temperature_slider, current_problem_id],
            outputs=[hint_output, metrics_output, history_output]
        )
        
        # 중급 힌트
        hint_btn_intermediate.click(
            fn=lambda code, temp, pid: app.generate_hint(code, temp, pid, 'intermediate', user_id="anonymous"),
            inputs=[user_code, temperature_slider, current_problem_id],
            outputs=[hint_output, metrics_output, history_output]
        )
        
        # 고급 힌트
        hint_btn_advanced.click(
            fn=lambda code, temp, pid: app.generate_hint(code, temp, pid, 'advanced', user_id="anonymous"),
            inputs=[user_code, temperature_slider, current_problem_id],
            outputs=[hint_output, metrics_output, history_output]
        )

    return demo


if __name__ == "__main__":
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description="vLLM Docker 기반 힌트 생성 시스템")
    parser.add_argument("--server-name", type=str, default=None,
                       help="Server host (default: 127.0.0.1, use 0.0.0.0 for Docker)")
    parser.add_argument("--server-port", type=int, default=None,
                       help="Server port (default: 7860)")
    parser.add_argument("--share", action="store_true",
                       help="Create public share link")
    parser.add_argument("--no-browser", action="store_true",
                       help="Don't auto-open browser")
    parser.add_argument("--vllm-url", type=str, default=None,
                       help="vLLM server URL (default: from .env or http://localhost:8000/v1)")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("⚡ vLLM Docker 기반 힌트 생성 시스템")
    print("=" * 60 + "\n")

    # 환경 감지 (Docker, RunPod 등)
    is_docker = os.getenv("DOCKER_CONTAINER") is not None or os.path.exists('/.dockerenv')
    is_runpod = os.getenv("RUNPOD_POD_ID") is not None or os.getenv("PUBLIC_URL") is not None

    # 서버 설정 자동 조정
    if is_docker or is_runpod:
        if args.server_name is None:
            args.server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
        args.no_browser = True
        print("🐳 Docker/RunPod 환경 감지됨")
        if is_runpod:
            args.share = False  # RunPod proxy 사용, share 터널 비활성화
            print("🚀 RunPod 환경: RunPod proxy 사용 (share 비활성화)")

    # 포트 설정
    if args.server_port is None:
        args.server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

    # vLLM URL 설정 (우선순위: CLI > 환경변수 > 기본값)
    vllm_url = args.vllm_url or os.getenv('VLLM_SERVER_URL', 'http://localhost:8000/v1')
    print(f"🔗 vLLM 서버 URL: {vllm_url}")

    # 데이터 경로 확인
    DATA_PATH = Config.DATA_FILE_PATH
    if not DATA_PATH.exists():
        # 대체 경로 시도
        alt_paths = [
            Path("data/problems_multi_solution.json"),
            Path("/app/data/problems_multi_solution.json"),
            Path(os.getenv("DATA_FILE_PATH", ""))
        ]
        
        for alt_path in alt_paths:
            if alt_path.exists():
                DATA_PATH = alt_path
                break
        else:
            print(f"❌ 데이터 파일을 찾을 수 없습니다:")
            print(f"   기본 경로: {Config.DATA_FILE_PATH}")
            print(f"   대체 경로 시도:")
            for p in alt_paths:
                print(f"     - {p}")
            print(f"\n   해결 방법:")
            print(f"   1. 환경 변수 DATA_FILE_PATH 설정")
            print(f"   2. Docker 볼륨 마운트 확인: -v ./data:/app/data")
            sys.exit(1)

    # 앱 초기화
    print(f"📚 문제 데이터 로딩: {DATA_PATH}")
    try:
        app = VLLMHintApp(str(DATA_PATH), vllm_url=vllm_url)
        print(f"✅ {len(app.problems)}개 문제 로드 완료!\n")
    except Exception as e:
        print(f"❌ 앱 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # UI 생성 및 실행
    print("🌐 Gradio UI 시작...\n")
    demo = create_vllm_ui(app)

    # Launch 설정
    launch_kwargs = {
        "server_port": args.server_port,
        "share": args.share,
        "inbrowser": not args.no_browser
    }

    if args.server_name:
        launch_kwargs["server_name"] = args.server_name

    print(f"🚀 서버 시작:")
    print(f"   - Host: {args.server_name or '127.0.0.1'}")
    print(f"   - Port: {args.server_port}")
    print(f"   - Share: {args.share}")
    print(f"\n" + "=" * 60 + "\n")

    try:
        demo.launch(**launch_kwargs)
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
