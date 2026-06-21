from dataclasses import dataclass


@dataclass(frozen=True)
class MarkdownDocument:
    filename: str
    markdown: str
    characters: int
