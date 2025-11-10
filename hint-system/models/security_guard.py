"""
보안 필터링 시스템
- 악질 사용자 공격 방어
- 프롬프트 인젝션 방지
- 토큰 낭비 공격 방어
- Rate Limiting
"""
import re
import time
from typing import Dict, Tuple, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SecurityCheckResult:
    """보안 검사 결과"""
    is_safe: bool
    risk_level: str  # 'safe', 'warning', 'danger'
    blocked_reasons: List[str]
    sanitized_input: str


class SecurityGuard:
    """보안 가드 시스템"""
    
    def __init__(self):
        # Rate Limiting: 사용자별 요청 기록
        self.request_history: Dict[str, List[datetime]] = {}
        
        # 악질 패턴 데이터베이스
        self.malicious_patterns = self._load_malicious_patterns()
        
        # 설정
        self.max_requests_per_minute = 10
        self.max_requests_per_hour = 50
        self.max_code_length = 5000
        self.max_prompt_length = 2000
    
    def _load_malicious_patterns(self) -> Dict[str, List[str]]:
        """악질 공격 패턴 로드"""
        return {
            # 프롬프트 인젝션 공격
            'prompt_injection': [
                r'ignore\s+(previous|all|above)\s+instructions?',
                r'forget\s+(everything|all|previous)',
                r'you\s+are\s+now',
                r'new\s+instructions?:',
                r'system\s*:\s*',
                r'<\|im_start\|>',
                r'<\|im_end\|>',
                r'\[INST\]',
                r'\[/INST\]',
                r'###\s*System',
                r'###\s*Human',
                r'###\s*Assistant',
                r'</s>',
                r'<s>',
            ],
            
            # Jailbreak 시도
            'jailbreak': [
                r'DAN\s+mode',
                r'developer\s+mode',
                r'unrestricted\s+mode',
                r'bypass\s+(safety|filter|restriction)',
                r'ignore\s+(ethics|safety|policy)',
                r'roleplay\s+as\s+(evil|hacker|malicious)',
                r'pretend\s+you\s+are',
            ],
            
            # 토큰 낭비 공격
            'token_waste': [
                r'(.)\1{50,}',  # 같은 문자 50회 이상 반복
                r'[\w\s]{10000,}',  # 10000자 이상 텍스트
                r'(print|echo|output).*\*\s*\d{4,}',  # 엄청난 반복 요청
            ],
            
            # 코드 실행 공격
            'code_injection': [
                r'__import__\s*\(',
                r'eval\s*\(',
                r'exec\s*\(',
                r'compile\s*\(',
                r'os\.(system|popen|spawn)',
                r'subprocess\.',
                r'open\s*\(.*(w|a)\+?',  # 파일 쓰기
                r'requests?\.(get|post|put|delete)',  # 외부 요청
                r'socket\.',
            ],
            
            # 민감 정보 요청
            'sensitive_info': [
                r'(api|secret|password|token|key)\s*[:=]',
                r'\.env',
                r'config\.(json|yaml|yml|ini)',
                r'/etc/(passwd|shadow)',
                r'database\s+credentials?',
            ],
        }
    
    def check_input_safety(self, user_code: str, user_id: str = "anonymous") -> SecurityCheckResult:
        """입력 안전성 종합 검사"""
        blocked_reasons = []
        risk_level = 'safe'
        
        # 1. Rate Limiting 체크
        if not self._check_rate_limit(user_id):
            blocked_reasons.append("⏱️ 요청 속도 제한 초과 (Rate Limit)")
            risk_level = 'danger'
        
        # 2. 입력 길이 체크
        if len(user_code) > self.max_code_length:
            blocked_reasons.append(f"📏 코드 길이 초과 (최대 {self.max_code_length}자)")
            risk_level = 'danger'
        
        # 3. 악질 패턴 탐지
        detected_attacks = self._detect_malicious_patterns(user_code)
        if detected_attacks:
            blocked_reasons.extend(detected_attacks)
            risk_level = 'danger'
        
        # 4. 코드 구조 검증
        structure_issues = self._validate_code_structure(user_code)
        if structure_issues:
            blocked_reasons.extend(structure_issues)
            if risk_level == 'safe':
                risk_level = 'warning'
        
        # 5. 입력 정제
        sanitized_input = self._sanitize_input(user_code)
        
        is_safe = risk_level != 'danger'
        
        return SecurityCheckResult(
            is_safe=is_safe,
            risk_level=risk_level,
            blocked_reasons=blocked_reasons,
            sanitized_input=sanitized_input
        )
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Rate Limiting 검사"""
        now = datetime.now()
        
        # 사용자 이력 초기화
        if user_id not in self.request_history:
            self.request_history[user_id] = []
        
        # 오래된 기록 정리 (1시간 이상)
        self.request_history[user_id] = [
            req_time for req_time in self.request_history[user_id]
            if now - req_time < timedelta(hours=1)
        ]
        
        # 분당 요청 체크
        recent_requests = [
            req_time for req_time in self.request_history[user_id]
            if now - req_time < timedelta(minutes=1)
        ]
        
        if len(recent_requests) >= self.max_requests_per_minute:
            return False
        
        # 시간당 요청 체크
        if len(self.request_history[user_id]) >= self.max_requests_per_hour:
            return False
        
        # 요청 기록
        self.request_history[user_id].append(now)
        return True
    
    def _detect_malicious_patterns(self, text: str) -> List[str]:
        """악질 패턴 탐지"""
        detected = []
        
        text_lower = text.lower()
        
        for attack_type, patterns in self.malicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected.append(f"🚨 {attack_type.upper()} 공격 감지: {pattern[:50]}")
                    break  # 각 공격 타입당 1회만 보고
        
        return detected
    
    def _validate_code_structure(self, code: str) -> List[str]:
        """코드 구조 검증"""
        issues = []
        
        # 빈 코드
        if not code.strip():
            return issues
        
        # 비정상적인 반복
        lines = code.split('\n')
        if len(lines) > 500:
            issues.append("⚠️ 비정상적으로 긴 코드 (500줄 초과)")
        
        # 동일 줄 반복
        unique_lines = set(line.strip() for line in lines if line.strip())
        if len(lines) > 50 and len(unique_lines) < len(lines) * 0.3:
            issues.append("⚠️ 의심스러운 코드 반복 패턴")
        
        # 주석만 있는 코드
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        if len(code_lines) == 0 and len(lines) > 10:
            issues.append("⚠️ 실행 가능한 코드 없음 (주석만 존재)")
        
        return issues
    
    def _sanitize_input(self, text: str) -> str:
        """입력 정제"""
        # 길이 제한
        if len(text) > self.max_code_length:
            text = text[:self.max_code_length]
        
        # 위험한 특수문자 제거
        text = re.sub(r'[<>]', '', text)
        
        # 연속 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def validate_hint_request(self, code: str, problem_id: str, 
                             selected_level: str, user_id: str = "anonymous") -> Tuple[bool, str]:
        """힌트 요청 전체 검증"""
        # 1. 보안 검사
        security_result = self.check_input_safety(code, user_id)
        
        if not security_result.is_safe:
            reasons = '\n'.join(security_result.blocked_reasons)
            return False, f"❌ 보안 검증 실패:\n{reasons}"
        
        # 2. 입력 유효성
        if not code.strip():
            return False, "❌ 코드를 입력해주세요."
        
        if not problem_id:
            return False, "❌ 문제를 선택해주세요."
        
        if selected_level not in ['novice', 'intermediate', 'advanced']:
            return False, "❌ 유효하지 않은 난이도입니다."
        
        # 3. 경고 메시지
        if security_result.risk_level == 'warning':
            warnings = '\n'.join(security_result.blocked_reasons)
            return True, f"⚠️ 경고:\n{warnings}\n\n계속 진행합니다."
        
        return True, "✅ 검증 통과"
    
    def get_usage_stats(self, user_id: str) -> Dict:
        """사용자 사용량 통계"""
        if user_id not in self.request_history:
            return {
                'total_requests': 0,
                'requests_last_minute': 0,
                'requests_last_hour': 0,
                'remaining_minute': self.max_requests_per_minute,
                'remaining_hour': self.max_requests_per_hour
            }
        
        now = datetime.now()
        history = self.request_history[user_id]
        
        recent_minute = [
            req for req in history 
            if now - req < timedelta(minutes=1)
        ]
        
        recent_hour = [
            req for req in history 
            if now - req < timedelta(hours=1)
        ]
        
        return {
            'total_requests': len(history),
            'requests_last_minute': len(recent_minute),
            'requests_last_hour': len(recent_hour),
            'remaining_minute': max(0, self.max_requests_per_minute - len(recent_minute)),
            'remaining_hour': max(0, self.max_requests_per_hour - len(recent_hour))
        }


# 글로벌 인스턴스
_security_guard = None

def get_security_guard() -> SecurityGuard:
    """싱글톤 SecurityGuard 인스턴스"""
    global _security_guard
    if _security_guard is None:
        _security_guard = SecurityGuard()
    return _security_guard
