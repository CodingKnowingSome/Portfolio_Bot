from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PromotionLogs:
    usernames: list[str]
    lessons: list[str]
    stage: int | None = None


def get_names(line: str) -> list[str]:
    try:
        start_index = line.index("username:") + len("username:")
        end_index = line.index("action:")
        return line[start_index:end_index].strip().split()
    except ValueError as e:
        logger.warning(f"Failed to parse {line}: {e}")
        return []


def parse_promotion_log(content: str) -> PromotionLogs:
    stage = None
    usernames = []
    lessons = []

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("Type:"):
            try:
                stage = int(line.removeprefix("Type:").strip())
            except ValueError as e:
                logger.warning(f"Failed to parse stage {line}: {e}")
                raise ValueError(f"Failed to parse stage {line}: {e}") from e
        elif "/xp username:" in line and "action:" in line:
            usernames = get_names(line)
        elif "/lessons username:" in line and "action:" in line:
            lessons = get_names(line)
    if stage is None:
        raise ValueError("Invalid type on lesson log")
    return PromotionLogs(stage=stage, usernames=usernames, lessons=lessons)
