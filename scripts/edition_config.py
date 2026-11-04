#!/usr/bin/env python3
"""Load language-owned settings used by the shared build scripts."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EDITION_CODES = ("zh-TW",)


@dataclass(frozen=True)
class SeoConfig:
    hreflang: str
    locale: str
    fallback_description: str
    redirect_title: str
    redirect_message: str
    redirect_link_text: str


@dataclass(frozen=True)
class EditionConfig:
    code: str
    seo: SeoConfig


def _read_toml(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("rb") as stream:
        return tomllib.load(stream)


def _table(
    document: dict[str, object],
    key: str,
    path: Path,
) -> dict[str, object]:
    value = document.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: [{key}] must be a TOML table")
    return value


def _string(table: dict[str, object], key: str, path: Path) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{path}: {key} must be a non-empty string")
    return value


def _validate_templates(config: EditionConfig, path: Path) -> None:
    try:
        config.seo.fallback_description.format(title="Example")
    except (IndexError, KeyError, ValueError) as error:
        raise ValueError(f"{path}: invalid format template: {error}") from error

    if config.seo.redirect_message.count("{link}") != 1:
        raise ValueError(
            f"{path}: seo.redirect_message must contain one {{link}} placeholder"
        )


@lru_cache(maxsize=None)
def load_edition_config(code: str) -> EditionConfig:
    if code not in EDITION_CODES:
        raise ValueError(f"Unknown edition: {code}")

    edition_root = REPOSITORY_ROOT / code
    book_path = edition_root / "book.toml"
    edition_path = edition_root / "edition.toml"
    book_document = _read_toml(book_path)
    edition_document = _read_toml(edition_path)

    book = _table(book_document, "book", book_path)
    language = _string(book, "language", book_path)
    if language != code:
        raise ValueError(
            f"{book_path}: book.language is {language!r}, expected {code!r}"
        )

    seo_table = _table(edition_document, "seo", edition_path)

    config = EditionConfig(
        code=code,
        seo=SeoConfig(
            hreflang=_string(seo_table, "hreflang", edition_path),
            locale=_string(seo_table, "locale", edition_path),
            fallback_description=_string(
                seo_table,
                "fallback_description",
                edition_path,
            ),
            redirect_title=_string(seo_table, "redirect_title", edition_path),
            redirect_message=_string(
                seo_table,
                "redirect_message",
                edition_path,
            ),
            redirect_link_text=_string(
                seo_table,
                "redirect_link_text",
                edition_path,
            ),
        ),
    )
    _validate_templates(config, edition_path)
    return config
