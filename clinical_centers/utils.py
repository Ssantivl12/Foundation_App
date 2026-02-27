from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional

from django.utils import timezone

DAYS_OF_WEEK: List[tuple[int, str]] = [
    (0, "Lunes"),
    (1, "Martes"),
    (2, "Miércoles"),
    (3, "Jueves"),
    (4, "Viernes"),
    (5, "Sábado"),
    (6, "Domingo"),
]

_DAY_ALIAS_MAP = {
    "0": 0,
    "lunes": 0,
    "lun": 0,
    "1": 1,
    "martes": 1,
    "mar": 1,
    "2": 2,
    "miercoles": 2,
    "miércoles": 2,
    "mie": 2,
    "mié": 2,
    "3": 3,
    "jueves": 3,
    "jue": 3,
    "4": 4,
    "viernes": 4,
    "vie": 4,
    "5": 5,
    "sabado": 5,
    "sábado": 5,
    "sab": 5,
    "sáb": 5,
    "6": 6,
    "domingo": 6,
    "dom": 6,
}

_TIME_RANGE_RE = re.compile(
    r"^(?P<open>([01]\d|2[0-3]):[0-5]\d)\s*-\s*(?P<close>([01]\d|2[0-3]):[0-5]\d)$"
)


def prepare_default_operating_hours() -> Dict[str, List[Dict[str, str]]]:
    """Return an empty schedule dict with all week days."""
    return {str(day): [] for day, _ in DAYS_OF_WEEK}


def parse_services(value: Optional[str | Iterable[str]]) -> List[str]:
    """Convert user input into a list of services."""
    if value is None:
        return []

    if isinstance(value, (list, tuple)):
        return [item.strip() for item in value if item and str(item).strip()]

    if not isinstance(value, str):
        return []

    raw_items = re.split(r"[\n,;]+", value)
    return [item.strip() for item in raw_items if item and item.strip()]


def format_services(services: Optional[Iterable[str]]) -> str:
    """Render stored services as newline separated text."""
    if not services:
        return ""
    return "\n".join(str(item) for item in services if str(item).strip())


def parse_operating_hours(raw_value: Optional[str | Dict[str, List[Dict[str, str]]]]) -> Dict[str, List[Dict[str, str]]]:
    """Parse a human friendly schedule representation into the JSON structure."""
    if raw_value is None:
        return prepare_default_operating_hours()

    if isinstance(raw_value, dict):
        parsed = prepare_default_operating_hours()
        for key, segments in raw_value.items():
            if not isinstance(segments, list):
                continue
            cleaned_segments: List[Dict[str, str]] = []
            for segment in segments:
                if not isinstance(segment, dict):
                    continue
                open_time = str(segment.get("open", "")).strip()
                close_time = str(segment.get("close", "")).strip()
                if _is_valid_time_range(open_time, close_time):
                    cleaned_segments.append({"open": open_time, "close": close_time})
            parsed[str(key)] = cleaned_segments
        return parsed

    if not isinstance(raw_value, str):
        return prepare_default_operating_hours()

    parsed_hours = prepare_default_operating_hours()
    lines = [line.strip() for line in raw_value.splitlines() if line.strip()]

    for line in lines:
        if ":" not in line:
            raise ValueError(f"Línea inválida (faltan ':' separador día/horas): {line}")

        day_label, ranges_blob = line.split(":", 1)
        normalized_day = _normalize_day_label(day_label.strip())

        time_segments: List[Dict[str, str]] = []
        for chunk in [item.strip() for item in ranges_blob.split(",") if item.strip()]:
            match = _TIME_RANGE_RE.match(chunk)
            if not match:
                raise ValueError(f"Rango horario inválido: {chunk}")
            open_time = match.group("open")
            close_time = match.group("close")
            if open_time >= close_time:
                raise ValueError(f"El horario debe tener inicio menor al fin: {chunk}")
            time_segments.append({"open": open_time, "close": close_time})

        parsed_hours[str(normalized_day)] = time_segments

    return parsed_hours


def format_operating_hours(operating_hours: Optional[Dict[str, List[Dict[str, str]]]]) -> str:
    """Render stored schedule as multi-line instructions."""
    normalized = parse_operating_hours(operating_hours)
    lines: List[str] = []
    for day, label in DAYS_OF_WEEK:
        segments = normalized.get(str(day), [])
        if segments:
            ranges = ", ".join(f"{segment['open']}-{segment['close']}" for segment in segments)
            lines.append(f"{label}: {ranges}")
        else:
            lines.append(f"{label}:")
    return "\n".join(lines)


def is_open_now(operating_hours: Optional[Dict[str, List[Dict[str, str]]]], when=None, tz=None) -> bool:
    """Return True if the schedule is currently open for the provided datetime."""
    normalized = parse_operating_hours(operating_hours)

    if when is None:
        if tz is None:
            when = timezone.localtime()
        else:
            when = timezone.localtime(timezone.now(), timezone=tz)
    elif tz is not None:
        when = timezone.localtime(when, timezone=tz)

    day_key = str(when.weekday())
    current_time = when.strftime("%H:%M")

    for segment in normalized.get(day_key, []):
        open_time = segment.get("open")
        close_time = segment.get("close")
        if not open_time or not close_time:
            continue
        if open_time <= current_time < close_time:
            return True
    return False


def _normalize_day_label(label: str) -> int:
    normalized = label.lower()
    if normalized not in _DAY_ALIAS_MAP:
        raise ValueError(f"Día inválido: {label}")
    return _DAY_ALIAS_MAP[normalized]


def _is_valid_time_range(start: str, end: str) -> bool:
    if not start or not end:
        return False
    if not _TIME_RANGE_RE.match(f"{start}-{end}"):
        return False
    return start < end
