"""
vLLM Docker 기반 힌트 생성 시스템
vLLM 공식 Docker 이미지를 활용한 고속 추론 시스템
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


class VLLMHintApp:
    """vLLM 전용 힌트 생성 애플리케이션"""

    def __init__(self, data_path: str, vllm_url: str = None):
        self.data_path = data_path
        self.problems = self.load_problems()
        
        # vLLM 서버 URL 설정 (우선순위: 파라미터 > 환경변수 > 기본값)
        self.vllm_url = vllm_url or os.getenv('VLLM_SERVER_URL', 'http://localhost:8000/v1')
        
        self.current_problem = None
        self.current_model = None
        self.current_problem_id = None  # 인스턴스 변수로 명시적 관리

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

    def generate_hint(self, user_code: str, temperature: float, problem_id):
        """힌트 생성 (vLLM 사용)"""
        print(f"\n🔍 [generate_hint] 호출됨")
        print(f"   - user_code 길이: {len(user_code.strip())} 글자")
        print(f"   - temperature: {temperature}")
        print(f"   - problem_id 매개변수: {problem_id} (타입: {type(problem_id).__name__})")
        print(f"   - self.current_problem_id: {self.current_problem_id}")
        
        # problem_id가 None이면 인스턴스 변수 사용 (폴백)
        if problem_id is None:
            print("⚠️ [generate_hint] State의 problem_id가 None, 인스턴스 변수 사용")
            problem_id = self.current_problem_id
            
        if problem_id is None:
            print("❌ [generate_hint] 인스턴스 변수도 None임 - 문제 선택 안됨")
            return "❌ 먼저 문제를 선택해주세요.", ""
        
        print(f"✅ [generate_hint] 최종 사용할 problem_id: {problem_id}")
        
        # problem_id로 문제 찾기 (문자열 비교 - JSON에서 문자열로 저장됨)
        self.current_problem = None
        for p in self.problems:
            if str(p['problem_id']) == str(problem_id):
                self.current_problem = p
                break
        
        if not self.current_problem:
            print(f"❌ [generate_hint] 문제를 찾을 수 없음 (ID: {problem_id})")
            print(f"   사용 가능한 문제 ID 목록: {[p['problem_id'] for p in self.problems[:5]]}...")
            return f"❌ 문제를 찾을 수 없습니다. (ID: {problem_id})", ""

        print(f"✅ [generate_hint] 문제 찾음: {self.current_problem['title']}")

        if not user_code.strip():
            print("❌ [generate_hint] 코드가 비어있음")
            return "❌ 코드를 입력해주세요.", ""

        if not self.current_model:
            print("❌ [generate_hint] vLLM 모델 연결 안됨")
            return "❌ vLLM 서버에 연결되지 않았습니다. 서버를 시작하세요.", ""

        print("✅ [generate_hint] 모든 검증 통과, 프롬프트 생성 중...")
        # 프롬프트 생성
        prompt = self._create_hint_prompt(user_code)

        # vLLM으로 힌트 생성 (시간 측정)
        start_time = time.time()

        try:
            result = self.current_model.generate_hint(
                prompt=prompt,
                max_tokens=512,
                temperature=temperature
            )

            elapsed_time = time.time() - start_time

            if result.get('error'):
                return f"❌ 생성 실패: {result['error']}", ""

            hint = result.get('hint', '(빈 응답)')

            # 성능 메트릭 포맷팅
            metrics = f"""
## ⚡ 추론 성능
- **소요 시간:** {elapsed_time:.3f}초
- **Temperature:** {temperature}
- **Model:** {self.current_model.model_name}
"""

            return hint, metrics

        except Exception as e:
            return f"❌ 오류 발생: {str(e)}", ""

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

        hint_btn = gr.Button("💡 힌트 생성 (vLLM)", variant="primary", size="lg")

        gr.Markdown("---")

        # 힌트 결과
        gr.Markdown("## 🎯 생성된 힌트")
        hint_output = gr.Markdown("_힌트가 여기에 표시됩니다_")

        gr.Markdown("---")

        # 성능 메트릭
        gr.Markdown("## 📊 성능 메트릭")
        metrics_output = gr.Markdown("_추론 성능이 여기에 표시됩니다_")

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

        # 3. 힌트 생성 버튼 - State 직접 참조
        hint_btn.click(
            fn=app.generate_hint,
            inputs=[user_code, temperature_slider, current_problem_id],
            outputs=[hint_output, metrics_output]
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
            args.share = True
            print("🚀 RunPod 환경: 공개 링크 생성")

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
