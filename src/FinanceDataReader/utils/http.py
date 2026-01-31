"""HTTP 요청 유틸리티 모듈"""

import time
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}


def create_session(max_retries: int = 3, backoff_factor: float = 0.3) -> requests.Session:
    """
    재시도 로직이 포함된 requests Session 생성

    Args:
        max_retries: 최대 재시도 횟수
        backoff_factor: 재시도 간격 계산 인자

    Returns:
        설정된 requests.Session 객체
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST", "OPTIONS"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update(DEFAULT_HEADERS)

    return session


def get_request(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    session: Optional[requests.Session] = None
) -> requests.Response:
    """
    HTTP GET 요청

    Args:
        url: 요청 URL
        params: 쿼리 파라미터
        headers: 추가 헤더
        timeout: 타임아웃 (초)
        session: 재사용할 Session 객체 (None이면 새로 생성)

    Returns:
        requests.Response 객체

    Raises:
        requests.RequestException: 요청 실패 시
    """
    if session is None:
        session = create_session()

    if headers:
        request_headers = {**DEFAULT_HEADERS, **headers}
    else:
        request_headers = DEFAULT_HEADERS

    try:
        response = session.get(
            url,
            params=params,
            headers=request_headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to GET {url}: {e}")


def post_request(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    session: Optional[requests.Session] = None
) -> requests.Response:
    """
    HTTP POST 요청

    Args:
        url: 요청 URL
        data: form 데이터
        json: JSON 데이터
        headers: 추가 헤더
        timeout: 타임아웃 (초)
        session: 재사용할 Session 객체

    Returns:
        requests.Response 객체

    Raises:
        requests.RequestException: 요청 실패 시
    """
    if session is None:
        session = create_session()

    if headers:
        request_headers = {**DEFAULT_HEADERS, **headers}
    else:
        request_headers = DEFAULT_HEADERS

    try:
        response = session.post(
            url,
            data=data,
            json=json,
            headers=request_headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to POST {url}: {e}")


def rate_limited_request(func, *args, delay: float = 0.1, **kwargs):
    """
    요청 속도 제한을 위한 래퍼

    Args:
        func: 요청 함수 (get_request 또는 post_request)
        delay: 요청 후 대기 시간 (초)
        *args, **kwargs: func에 전달할 인자

    Returns:
        func의 반환값
    """
    result = func(*args, **kwargs)
    time.sleep(delay)
    return result
