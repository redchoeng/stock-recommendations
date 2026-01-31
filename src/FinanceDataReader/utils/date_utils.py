"""날짜 처리 유틸리티 모듈"""

from datetime import datetime, timedelta
from typing import Optional, Tuple


def parse_date(date_str: Optional[str], default: Optional[datetime] = None) -> datetime:
    """
    날짜 문자열을 datetime 객체로 파싱

    Args:
        date_str: 날짜 문자열 (YYYY, YYYY-MM-DD, YYYY-MM-DD 형식)
        default: date_str이 None일 때 반환할 기본값

    Returns:
        datetime 객체

    Examples:
        >>> parse_date('2023')
        datetime.datetime(2023, 1, 1, 0, 0)
        >>> parse_date('2023-05-15')
        datetime.datetime(2023, 5, 15, 0, 0)
    """
    if date_str is None:
        if default is None:
            raise ValueError("date_str and default cannot both be None")
        return default

    date_str = date_str.strip()

    # YYYY 형식
    if len(date_str) == 4 and date_str.isdigit():
        return datetime(int(date_str), 1, 1)

    # YYYY-MM-DD 형식
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        pass

    # YYYY/MM/DD 형식
    try:
        return datetime.strptime(date_str, '%Y/%m/%d')
    except ValueError:
        pass

    # YYYYMMDD 형식
    if len(date_str) == 8 and date_str.isdigit():
        return datetime.strptime(date_str, '%Y%m%d')

    raise ValueError(f"Invalid date format: {date_str}. Use 'YYYY', 'YYYY-MM-DD', or 'YYYYMMDD'")


def validate_date_range(start: datetime, end: datetime) -> None:
    """
    날짜 범위 검증

    Args:
        start: 시작일
        end: 종료일

    Raises:
        ValueError: 시작일이 종료일보다 늦은 경우
    """
    if start > end:
        raise ValueError(f"Start date ({start}) must be before end date ({end})")


def get_default_dates(start: Optional[str] = None, end: Optional[str] = None) -> Tuple[datetime, datetime]:
    """
    기본 날짜 범위 반환

    Args:
        start: 시작일 문자열 (None이면 1년 전)
        end: 종료일 문자열 (None이면 오늘)

    Returns:
        (시작 datetime, 종료 datetime) 튜플
    """
    today = datetime.now()

    if end is None:
        end_date = today
    else:
        end_date = parse_date(end)

    if start is None:
        # 기본값: 1년 전
        start_date = end_date - timedelta(days=365)
    else:
        start_date = parse_date(start)

    validate_date_range(start_date, end_date)

    return start_date, end_date


def format_date(dt: datetime, format: str = '%Y-%m-%d') -> str:
    """
    datetime 객체를 문자열로 포맷팅

    Args:
        dt: datetime 객체
        format: 출력 형식 (기본값: 'YYYY-MM-DD')

    Returns:
        포맷팅된 날짜 문자열
    """
    return dt.strftime(format)


def date_to_str_krx(dt: datetime) -> str:
    """KRX API용 날짜 형식 (YYYYMMDD)"""
    return dt.strftime('%Y%m%d')


def date_to_str_yahoo(dt: datetime) -> str:
    """Yahoo Finance API용 날짜 형식 (YYYY-MM-DD)"""
    return dt.strftime('%Y-%m-%d')


def get_date_chunks(start: datetime, end: datetime, chunk_years: int = 2) -> list:
    """
    날짜 범위를 청크로 분할 (KRX는 2년 단위로 데이터 요청)

    Args:
        start: 시작일
        end: 종료일
        chunk_years: 청크 단위 (년)

    Returns:
        [(start1, end1), (start2, end2), ...] 리스트
    """
    chunks = []
    current_start = start

    while current_start < end:
        # 현재 청크의 종료일 계산
        chunk_end = datetime(
            current_start.year + chunk_years,
            current_start.month,
            current_start.day
        )

        # 마지막 청크는 end를 넘지 않도록
        if chunk_end > end:
            chunk_end = end

        chunks.append((current_start, chunk_end))

        # 다음 청크 시작일
        current_start = chunk_end + timedelta(days=1)

    return chunks
