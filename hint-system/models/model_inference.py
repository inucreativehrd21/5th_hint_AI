"""
다양한 모델로부터 힌트를 생성하는 백엔드
"""
import time
from typing import Dict, List, Optional
import requests
from openai import OpenAI


class ModelInference:
    """모델 추론 베이스 클래스"""

    def __init__(self, model_name: str, model_type: str):
        self.model_name = model_name
        self.model_type = model_type

    def generate_hint(self, prompt: str, max_tokens: int = 512) -> Dict:
        """
        힌트 생성

        Returns:
            {
                'hint': str,  # 생성된 힌트
                'time': float,  # 소요 시간 (초)
                'model': str,  # 모델 이름
                'error': str  # 에러 발생시
            }
        """
        raise NotImplementedError


class HuggingFaceInference(ModelInference):
    """HuggingFace Transformers 기반 추론 (순차 로드 + 양자화 지원)"""

    def __init__(self, model_name: str, use_quantization: bool = False):
        super().__init__(model_name, "huggingface")
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.use_quantization = use_quantization

    def load_model(self):
        """모델 로드 (지연 로딩)"""
        if self.loaded:
            return

        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
            import torch

            print(f"Loading {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )

            # 양자화 설정 (4-bit)
            if self.use_quantization:
                print(f"  → Using 4-bit quantization to save memory")
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )

                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=quantization_config,
                    device_map="auto",
                    low_cpu_mem_usage=True,
                    trust_remote_code=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else "cpu",
                    low_cpu_mem_usage=True,
                    trust_remote_code=True
                )

            self.loaded = True
            print(f"✓ {self.model_name} loaded")
        except Exception as e:
            print(f"✗ Failed to load {self.model_name}: {e}")
            import traceback
            traceback.print_exc()
            raise

    def unload_model(self):
        """모델 언로드 (메모리 해제)"""
        if self.model is not None:
            print(f"Unloading {self.model_name}...")
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            self.loaded = False

            # GPU 메모리 정리
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # 가비지 컬렉션
            import gc
            gc.collect()

            print(f"✓ {self.model_name} unloaded")

    def generate_hint(self, prompt: str, max_tokens: int = 150, temperature: float = 0.3) -> Dict:
        """힌트 생성 (temperature 조절 가능)"""
        try:
            self.load_model()

            start_time = time.time()

            # 프롬프트 토큰화
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            input_length = inputs['input_ids'].shape[1]

            # 생성 (temperature 조절)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,  # 150 토큰으로 제한 (1-2 문장)
                temperature=temperature,  # UI에서 조절 가능
                top_p=0.9,  # 안정적인 샘플링
                do_sample=True,
                repetition_penalty=1.2,  # 반복 억제
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )

            # 생성된 부분만 디코딩 (입력 프롬프트 제외)
            generated_ids = outputs[0][input_length:]
            raw_output = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

            # 깔끔한 힌트만 추출 (후처리)
            hint = self._extract_hint_from_output(raw_output)

            # 빈 응답 처리
            if not hint or len(hint) < 10:
                hint = "(모델이 적절한 응답을 생성하지 못했습니다)"

            elapsed = time.time() - start_time

            return {
                'hint': hint,
                'time': elapsed,
                'model': self.model_name,
                'error': None
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'hint': '',
                'time': 0,
                'model': self.model_name,
                'error': str(e)
            }

    def _extract_hint_from_output(self, raw_output: str) -> str:
        """생성된 출력에서 의미있는 힌트만 추출 (강화된 필터링)"""
        import re

        # 디버깅: 원본 출력 확인
        print(f"\n[DEBUG] 원본 출력: {raw_output[:200]}")

        clean = raw_output.strip()

        # 영어 출력 필터링 (한국어만 허용)
        korean_chars = len(re.findall(r'[가-힣]', clean))
        total_chars = len(clean.replace(' ', ''))
        if total_chars > 0 and korean_chars / total_chars < 0.3:
            # 한국어가 30% 미만이면 영어로 판단
            print(f"[DEBUG] 영어 출력 필터링: {clean[:50]}...")
            return "(모델이 한국어 힌트를 생성하지 못했습니다)"

        # 메타 표현 강력 필터링 (프롬프트 반복)
        meta_patterns = [
            r'^학생이.*질문.*작성',
            r'^위.*원칙.*따라',
            r'^위.*설명.*따라',
            r'^다음.*소크라테스',
            r'^최종.*답:',
            r'^답변:',
            r'^질문:',
            r'^\[.*\]',  # [힌트], [분석] 같은 태그
        ]

        for pattern in meta_patterns:
            if re.match(pattern, clean, re.IGNORECASE):
                # 메타 표현 발견 시 다음 문장부터 찾기
                sentences = re.split(r'[.!?\n]+', clean)
                for s in sentences[1:]:
                    s = s.strip()
                    if len(s) > 15 and not any(re.match(p, s, re.IGNORECASE) for p in meta_patterns):
                        clean = s
                        break

        # 엉뚱한 주제 필터링
        irrelevant_keywords = [
            '직각', '삼각형', '원', '면적', '둘레', '피타고라스',
            '제곱근', '루트', '각도', '라디안', '삼각함수',
        ]

        # 문장별로 체크
        sentences = re.split(r'[.!?\n]+', clean)
        valid_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 15:
                continue

            # 엉뚱한 키워드 체크
            if any(keyword in sentence for keyword in irrelevant_keywords):
                print(f"[DEBUG] 무관한 내용 필터링: {sentence[:50]}...")
                continue

            # 메타 언급 및 이상한 시작 제거
            bad_starts = [
                '어떤 점을', '따라서', '학생 코드', '정답 코드', '이 코드', '위 코드', '아래 코드',
                '학생이 다음', '위 원칙', '그러나', '결국', '그럼', '그래서', '하지만',
                '정답코드', '정답에서', '코드에서', '위의 설명', '위 설명', '위 내용'
            ]
            if any(sentence.startswith(bad) for bad in bad_starts):
                print(f"[DEBUG] 메타 언급/이상한 시작 필터링: {sentence[:50]}...")
                continue

            # 정답 코드 직접 언급 필터링 (강화)
            bad_references = ['정답', '정답코드', '완성된 코드', '완성 코드', '위 코드', '참고 코드']
            if any(ref in sentence for ref in bad_references):
                print(f"[DEBUG] 정답/완성 코드 언급 필터링: {sentence[:50]}...")
                continue

            # 직접 답 요구 필터링 (신규)
            direct_answer_patterns = ['설명해줘', '알려줘', '가르쳐줘', '말해줘', '어떻게 작동']
            if any(pattern in sentence for pattern in direct_answer_patterns):
                print(f"[DEBUG] 직접 답 요구 필터링: {sentence[:50]}...")
                continue

            # 함수명/변수명 언급 필터링 (신규 - 매우 중요!)
            # snake_case나 camelCase 패턴 감지 (일반 단어 제외)
            import re
            # 2개 이상의 단어가 _로 연결되거나, 소문자+대문자 조합
            function_name_pattern = r'\b[a-z]+_[a-z]+\b|[a-z]+[A-Z][a-z]+'
            if re.search(function_name_pattern, sentence):
                # 일반적인 단어 예외 처리
                common_words = ['input', 'print', 'range', 'split', 'append']
                suspicious_names = re.findall(function_name_pattern, sentence)
                if any(name not in common_words for name in suspicious_names):
                    print(f"[DEBUG] 함수명/변수명 언급 필터링: {sentence[:50]}...")
                    continue

            # 학생 코드 반복 필터링 (코드 자체를 그대로 출력)
            if 'int(input())' in sentence or 'print(' in sentence:
                # 단, 질문 형태는 허용
                if not sentence.endswith('?'):
                    print(f"[DEBUG] 코드 반복 필터링: {sentence[:50]}...")
                    continue

            # 막연한 지시문 및 이상한 표현 필터링 (강화)
            vague_patterns = [
                '확인하세요', '생각해보세요', '고려하세요', '검토하세요',
                '작성하세요', '구현하세요', '코드를 완성',
                '어떤 부분이 잘못', '무엇이 문제', '어디가 틀렸',
                '대화하기 위해', '요청하는지',
                '물으시죠', '물으세요', '해주세요', '해주시', '주세요',
                '다시 한번', '네, 이해', '그렇다면', '그럼 지금부터',
                '잘못했다고', '틀렸다고', '생각했습니다', '생각됩니다',
                '핵심적인 과정', '어떤 부분을'
            ]
            if any(pattern in sentence for pattern in vague_patterns):
                print(f"[DEBUG] 막연한 지시문 필터링: {sentence[:50]}...")
                continue

            # 너무 짧거나 의미없는 문장 필터링 (20 → 30자로 상향)
            if len(sentence) < 30:
                print(f"[DEBUG] 너무 짧은 문장 필터링: {sentence}")
                continue

            # 추상적인 표현만 있는 힌트 필터링 (신규)
            abstract_only = [
                '결과 출력', '코드 작성', '로직 구현', '알고리즘 작성',
                '문제 해결', '방법 찾기', '구조 만들기'
            ]
            # 질문에 구체적인 키워드가 없으면 거부
            has_concrete = any(keyword in sentence for keyword in [
                '함수', '반복문', 'for', 'while', 'def', '조건문', 'if',
                '변수', '리스트', '배열', '입력', 'input', '출력', 'print',
                'append', 'range', 'len', 'max', 'min', 'sum', 'sorted'
            ])
            if any(abstract in sentence for abstract in abstract_only) and not has_concrete:
                print(f"[DEBUG] 추상적 표현만 있는 힌트 필터링: {sentence[:50]}...")
                continue

            valid_sentences.append(sentence)

        # 유효한 문장 중에서 질문 우선 추출 (물음표로 끝나는 것)
        for sentence in valid_sentences:
            if sentence.endswith('?'):
                hint = sentence.strip()
                print(f"[DEBUG] 유효한 질문 발견: {hint}")
                return hint

        # 물음표가 중간에 있는 경우
        for sentence in valid_sentences:
            if '?' in sentence:
                hint = sentence.split('?')[0].strip() + '?'
                print(f"[DEBUG] 물음표 포함 문장: {hint}")
                return hint

        # 질문이 없으면 첫 번째 유효한 문장
        if valid_sentences:
            hint = valid_sentences[0].strip()
            print(f"[DEBUG] 첫 유효 문장: {hint}")
            return hint

        # 모든 필터링 실패 - 기본 메시지
        print(f"[DEBUG] 유효한 힌트 없음")
        return "(모델이 적절한 힌트를 생성하지 못했습니다)"


class VLLMInference(ModelInference):
    """
    vLLM OpenAI 호환 API 기반 추론

    특징:
    - 15-24배 빠른 추론 속도 (HuggingFace 대비)
    - Continuous batching으로 처리량 극대화
    - PagedAttention으로 메모리 효율성 향상
    - Retry 로직 및 connection pooling
    - Health check 및 timeout 설정
    """

    def __init__(
        self,
        model_name: str,
        base_url: str = "http://localhost:8000/v1",
        timeout: int = 60,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        super().__init__(model_name, "vllm")
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # OpenAI 클라이언트 초기화 (connection pooling 포함)
        self.client = OpenAI(
            base_url=base_url,
            api_key="dummy",  # vLLM은 API key가 필요없지만 클라이언트 초기화를 위해 필요
            timeout=timeout,
            max_retries=max_retries
        )

        # 서버 연결 확인
        self._check_server_health()

    def _check_server_health(self) -> bool:
        """vLLM 서버 health check"""
        try:
            # OpenAI API의 models 엔드포인트로 서버 상태 확인
            models = self.client.models.list()
            available_models = [model.id for model in models.data]

            if available_models:
                print(f"✓ vLLM server connected at {self.base_url}")
                print(f"  Available models: {', '.join(available_models)}")
                
                # 서버에 요청한 모델이 없으면 첫 번째 사용 가능한 모델로 자동 설정
                if self.model_name not in available_models:
                    old_name = self.model_name
                    self.model_name = available_models[0]
                    print(f"⚠ Model '{old_name}' not found. Using '{self.model_name}' instead.")
                
                return True
            else:
                print(f"⚠ vLLM server at {self.base_url} has no models loaded")
                return False

        except Exception as e:
            print(f"✗ vLLM server at {self.base_url} is not reachable: {e}")
            print(f"  Please ensure vLLM server is running:")
            print(f"    python vllm_server.py --model {self.model_name}")
            return False

    def generate_hint(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        system_prompt: Optional[str] = None
    ) -> Dict:
        """
        힌트 생성 (vLLM 서버 사용)

        Args:
            prompt: 사용자 프롬프트
            max_tokens: 최대 생성 토큰 수
            temperature: 샘플링 온도 (0.0-2.0, 높을수록 창의적)
            top_p: Nucleus sampling threshold
            frequency_penalty: 반복 억제 (-2.0 ~ 2.0)
            presence_penalty: 주제 다양성 (-2.0 ~ 2.0)
            system_prompt: 시스템 프롬프트 (None이면 기본값 사용)

        Returns:
            {
                'hint': str,  # 생성된 힌트
                'time': float,  # 소요 시간 (초)
                'model': str,  # 모델 이름
                'error': str,  # 에러 발생시
                'tokens': int,  # 생성된 토큰 수
                'finish_reason': str  # 완료 이유 (stop, length, etc.)
            }
        """
        if system_prompt is None:
            system_prompt = """당신은 소크라테스식 프로그래밍 멘토입니다.
학생에게 직접적인 답을 주지 말고, 스스로 생각하고 발견하도록 질문과 힌트를 제공하세요.
절대로 코드의 함수명, 변수명을 직접 언급하지 마세요."""

        try:
            start_time = time.time()

            # OpenAI Chat Completions API 호출 (vLLM이 호환 지원)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                n=1,  # 생성할 응답 개수
                stream=False  # Streaming 비활성화 (필요시 별도 메서드 구현 가능)
            )

            hint = response.choices[0].message.content.strip()
            elapsed = time.time() - start_time

            # 토큰 사용량 및 완료 이유 추출
            tokens_used = response.usage.completion_tokens if response.usage else 0
            finish_reason = response.choices[0].finish_reason

            return {
                'hint': hint,
                'time': elapsed,
                'model': self.model_name,
                'error': None,
                'tokens': tokens_used,
                'finish_reason': finish_reason
            }

        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = str(e)

            # 상세한 에러 메시지
            if "Connection" in error_msg or "timeout" in error_msg.lower():
                error_msg = f"vLLM 서버 연결 실패 ({self.base_url}). 서버가 실행 중인지 확인하세요."
            elif "model" in error_msg.lower():
                error_msg = f"모델 '{self.model_name}'를 찾을 수 없습니다. 서버에서 올바른 모델이 로드되었는지 확인하세요."

            print(f"✗ VLLMInference error: {error_msg}")

            return {
                'hint': '',
                'time': elapsed,
                'model': self.model_name,
                'error': error_msg,
                'tokens': 0,
                'finish_reason': 'error'
            }

    def generate_hint_stream(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        system_prompt: Optional[str] = None
    ):
        """
        스트리밍 방식으로 힌트 생성 (실시간 응답)

        Yields:
            str: 생성된 텍스트 청크
        """
        if system_prompt is None:
            system_prompt = "당신은 소크라테스식 프로그래밍 멘토입니다."

        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"\n[Error: {str(e)}]"


class OllamaInference(ModelInference):
    """Ollama API 기반 추론"""

    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        super().__init__(model_name, "ollama")
        self.base_url = base_url

    def generate_hint(self, prompt: str, max_tokens: int = 512) -> Dict:
        """힌트 생성"""
        try:
            start_time = time.time()

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": max_tokens
                    }
                },
                timeout=120
            )

            response.raise_for_status()
            hint = response.json()['response'].strip()
            elapsed = time.time() - start_time

            return {
                'hint': hint,
                'time': elapsed,
                'model': self.model_name,
                'error': None
            }

        except Exception as e:
            return {
                'hint': '',
                'time': 0,
                'model': self.model_name,
                'error': str(e)
            }


class ModelManager:
    """여러 모델을 관리하는 매니저 (순차 로드 지원)"""

    def __init__(self, sequential_load: bool = True):
        self.models: Dict[str, ModelInference] = {}
        self.sequential_load = sequential_load  # 순차 로드 여부

    def add_huggingface_model(self, name: str, model_path: str, use_quantization: bool = False):
        """HuggingFace 모델 추가"""
        self.models[name] = HuggingFaceInference(model_path, use_quantization)

    def add_vllm_model(self, name: str, model_path: str, base_url: str):
        """vLLM 모델 추가"""
        self.models[name] = VLLMInference(model_path, base_url)

    def add_ollama_model(self, name: str, model_name: str, base_url: str = "http://localhost:11434"):
        """Ollama 모델 추가"""
        self.models[name] = OllamaInference(model_name, base_url)

    def generate_hints_from_all(self, prompt: str) -> Dict[str, Dict]:
        """모든 모델로부터 힌트 생성 (캐시 유지 방식)"""
        results = {}

        for name, model in self.models.items():
            print(f"Generating hint from {name}...")

            # 힌트 생성 (모델은 자동으로 로드되고 캐시됨)
            results[name] = model.generate_hint(prompt)

            # 순차 로드 모드는 더 이상 사용하지 않음 (캐시 유지)
            # if self.sequential_load and isinstance(model, HuggingFaceInference):
            #     model.unload_model()
            #     print(f"  → Memory freed for next model\n")

        return results

    def generate_hints_from_selected(self, prompt: str, selected_names: List[str], temperature: float = 0.3) -> Dict[str, Dict]:
        """선택된 모델들로부터만 힌트 생성 (temperature 전달)"""
        results = {}

        for name in selected_names:
            if name in self.models:
                print(f"Generating hint from {name}... (temp={temperature})")
                model = self.models[name]
                results[name] = model.generate_hint(prompt, temperature=temperature)
            else:
                print(f"⚠️  Model {name} not found, skipping...")

        return results

    def get_available_models(self) -> List[str]:
        """사용 가능한 모델 목록"""
        return list(self.models.keys())
