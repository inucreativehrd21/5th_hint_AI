"""
vLLM 고속 힌트 생성 시스템 - 단순화 버전
단일 vLLM 모델로 빠른 추론 테스트에 집중
"""
import argparse
import gradio as gr
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from config import Config
from models.model_config import VLLM_MODELS
from models.model_inference import VLLMInference


class VLLMHintApp:
    """vLLM 전용 힌트 생성 애플리케이션"""

    def __init__(self, data_path: str, vllm_url: str = "http://localhost:8000/v1"):
        self.data_path = data_path
        self.problems = self.load_problems()
        self.vllm_url = vllm_url
        self.current_problem = None
        self.current_model = None

        # vLLM 서버 연결 체크
        self.check_vllm_connection()

    def check_vllm_connection(self):
        """vLLM 서버 연결 확인"""
        try:
            # 환경변수에서 모델 이름 읽기 (기본값은 서버에서 자동 감지)
            model_name = os.getenv('VLLM_MODEL', 'Qwen/Qwen2.5-Coder-7B-Instruct')
            
            self.current_model = VLLMInference(
                model_name=model_name,
                base_url=self.vllm_url,
                timeout=60
            )
            print(f"✅ vLLM 서버 연결 성공: {self.vllm_url}")
        except Exception as e:
            print(f"⚠️  vLLM 서버 연결 실패: {e}")
            print(f"    {self.vllm_url}에 vLLM 서버가 실행 중인지 확인하세요.")
            self.current_model = None

    def load_problems(self) -> List[Dict]:
        """문제 데이터 로드"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_problem_list(self) -> List[str]:
        """문제 목록"""
        return [
            f"#{p['problem_id']} - {p['title']} (Level {p['level']})"
            for p in self.problems
        ]

    def load_problem(self, problem_selection: str):
        """선택된 문제 로드"""
        if not problem_selection:
            return "문제를 선택하세요.", "", None

        try:
            problem_id = int(problem_selection.split('#')[1].split(' -')[0].strip())

            self.current_problem = None
            for p in self.problems:
                if p['problem_id'] == problem_id:
                    self.current_problem = p
                    break

            if not self.current_problem:
                return "❌ 문제를 찾을 수 없습니다.", "", None

            problem_md = self._format_problem_display()
            # 문제 ID를 정수로 State에 저장
            return problem_md, "# 여기에 코드를 작성하세요\n", problem_id

        except Exception as e:
            return f"❌ 오류: {str(e)}", "", None

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
        # problem_id 검증 (None 또는 빈 값 체크)
        if problem_id is None:
            return "❌ 먼저 문제를 선택해주세요.", ""
        
        # problem_id로 문제 찾기 (정수 비교)
        self.current_problem = None
        for p in self.problems:
            if p['problem_id'] == problem_id:
                self.current_problem = p
                break
        
        if not self.current_problem:
            return f"❌ 문제를 찾을 수 없습니다. (ID: {problem_id})", ""

        if not user_code.strip():
            return "❌ 코드를 입력해주세요.", ""

        if not self.current_model:
            return "❌ vLLM 서버에 연결되지 않았습니다. 서버를 시작하세요.", ""

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
                scale=3
            )
            load_btn = gr.Button("📂 불러오기", variant="primary", scale=1)

        problem_display = gr.Markdown("")
        
        # 문제 ID를 저장하는 State (숨겨진 상태)
        current_problem_id = gr.State(value=None)

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
        load_btn.click(
            fn=app.load_problem,
            inputs=[problem_dropdown],
            outputs=[problem_display, user_code, current_problem_id]
        )

        hint_btn.click(
            fn=app.generate_hint,
            inputs=[user_code, temperature_slider, current_problem_id],
            outputs=[hint_output, metrics_output]
        )

    return demo


if __name__ == "__main__":
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description="vLLM Hint Generation System")
    parser.add_argument("--server-name", type=str, default=None,
                       help="Server host (default: 127.0.0.1, use 0.0.0.0 for RunPod)")
    parser.add_argument("--server-port", type=int, default=7860,
                       help="Server port (default: 7860)")
    parser.add_argument("--share", action="store_true",
                       help="Create public share link")
    parser.add_argument("--no-browser", action="store_true",
                       help="Don't auto-open browser")
    parser.add_argument("--vllm-url", type=str, default=None,
                       help="vLLM server URL (default: from .env)")
    args = parser.parse_args()

    print("\n" + "⚡" * 30)
    print("vLLM 고속 힌트 생성 시스템")
    print("⚡" * 30 + "\n")

    # RunPod 환경 자동 감지
    is_runpod = os.getenv("RUNPOD_POD_ID") is not None or os.getenv("PUBLIC_URL") is not None

    if is_runpod and args.server_name is None:
        args.server_name = "0.0.0.0"
        args.share = True
        args.no_browser = True
        print("🚀 RunPod 환경 감지됨!")

    # vLLM URL 설정
    vllm_url = args.vllm_url or Config.VLLM_SERVER_URL or "http://localhost:8000/v1"

    # 데이터 경로 확인
    DATA_PATH = Config.DATA_FILE_PATH
    if not DATA_PATH.exists():
        print(f"❌ 데이터 파일을 찾을 수 없습니다: {DATA_PATH}")
        exit(1)

    # 앱 초기화
    print(f"📚 문제 데이터 로딩: {DATA_PATH}")
    app = VLLMHintApp(str(DATA_PATH), vllm_url=vllm_url)
    print(f"✅ {len(app.problems)}개 문제 로드 완료!\n")

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

    demo.launch(**launch_kwargs)
