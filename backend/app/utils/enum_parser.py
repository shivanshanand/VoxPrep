import re
from enum import Enum
from typing import Type, TypeVar

E = TypeVar("E", bound=Enum)

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def parse_enum(enum_cls: Type[E], raw: str) -> E:
    raw_norm = normalize(raw)

    for member in enum_cls:
        if (
            normalize(member.name) == raw_norm or
            normalize(member.value) == raw_norm
        ):
            return member

    raise ValueError(f"'{raw}' is not a valid {enum_cls.__name__}")
