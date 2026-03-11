"""Validate Bible references via regex extraction and scraping bibleserver.com."""

from __future__ import annotations

import asyncio
import logging
import re

import httpx

from mcp_lektor.config.models import ProofreadingConfig
from mcp_lektor.core.models import (
    BibleReference,
    BibleValidationResult,
    DocumentStructure,
)
from mcp_lektor.utils.bible_patterns import extract_references

logger = logging.getLogger(__name__)

# Book-name → bibleserver.com slug mapping
_BIBELSERVER_BOOK_MAP: dict[str, str] = {
    "1. Mose": "1-mose",
    "1.Mose": "1-mose",
    "Gen": "1-mose",
    "2. Mose": "2-mose",
    "2.Mose": "2-mose",
    "Ex": "2-mose",
    "3. Mose": "3-mose",
    "3.Mose": "3-mose",
    "Lev": "3-mose",
    "4. Mose": "4-mose",
    "4.Mose": "4-mose",
    "Num": "4-mose",
    "5. Mose": "5-mose",
    "5.Mose": "5-mose",
    "Dtn": "5-mose",
    "Jos": "josua",
    "Ri": "richter",
    "Rut": "rut",
    "1. Sam": "1-samuel",
    "1.Samuel": "1-samuel",
    "1. Samuel": "1-samuel",
    "2. Sam": "2-samuel",
    "2.Samuel": "2-samuel",
    "2. Samuel": "2-samuel",
    "1. Kön": "1-koenige",
    "1. Koenige": "1-koenige",
    "1.Kön": "1-koenige",
    "1.Koenige": "1-koenige",
    "2. Kön": "2-koenige",
    "2. Koenige": "2-koenige",
    "2.Kön": "2-koenige",
    "2.Koenige": "2-koenige",
    "1. Chr": "1-chronik",
    "1. Chronik": "1-chronik",
    "1.Chr": "1-chronik",
    "2. Chr": "2-chronik",
    "2. Chronik": "2-chronik",
    "2.Chr": "2-chronik",
    "Esr": "esra",
    "Neh": "nehemia",
    "Est": "ester",
    "Ijob": "hiob",
    "Hiob": "hiob",
    "Hi": "hiob",
    "Ps": "psalm",
    "Spr": "sprueche",
    "Koh": "prediger",
    "Pred": "prediger",
    "Hld": "hohelied",
    "Jes": "jesaja",
    "Jer": "jeremia",
    "Klgl": "klagelieder",
    "Ez": "hesekiel",
    "Hes": "hesekiel",
    "Dan": "daniel",
    "Hos": "hosea",
    "Joel": "joel",
    "Am": "amos",
    "Obd": "obadja",
    "Jona": "jona",
    "Mi": "micha",
    "Nah": "nahum",
    "Hab": "habakuk",
    "Zef": "zefanja",
    "Hag": "haggai",
    "Sach": "sacharja",
    "Mal": "maleachi",
    "Mt": "matthaeus",
    "Mk": "markus",
    "Lk": "lukas",
    "Joh": "johannes",
    "Apg": "apostelgeschichte",
    "Röm": "roemer",
    "Roem": "roemer",
    "Römer": "roemer",
    "Roemer": "roemer",
    "1. Kor": "1-korinther",
    "1. Korinther": "1-korinther",
    "1.Kor": "1-korinther",
    "2. Kor": "2-korinther",
    "2. Korinther": "2-korinther",
    "2.Kor": "2-korinther",
    "Gal": "galater",
    "Galater": "galater",
    "Eph": "epheser",
    "Epheser": "epheser",
    "Phil": "philipper",
    "Philipper": "philipper",
    "Kol": "kolosser",
    "Kolosser": "kolosser",
    "1. Thess": "1-thessalonicher",
    "1. Thessalonicher": "1-thessalonicher",
    "1.Thess": "1-thessalonicher",
    "2. Thess": "2-thessalonicher",
    "2. Thessalonicher": "2-thessalonicher",
    "2.Thess": "2-thessalonicher",
    "1. Tim": "1-timotheus",
    "1. Timotheus": "1-timotheus",
    "1.Tim": "1-timotheus",
    "2. Tim": "2-timotheus",
    "2. Timotheus": "2-timotheus",
    "2.Tim": "2-timotheus",
    "Tit": "titus",
    "Phlm": "philemon",
    "Hebr": "hebraeer",
    "Hebreaer": "hebraeer",
    "Hebräer": "hebraeer",
    "Jak": "jakobus",
    "1. Petr": "1-petrus",
    "1. Petrus": "1-petrus",
    "1.Petr": "1-petrus",
    "2. Petr": "2-petrus",
    "2. Petrus": "2-petrus",
    "2.Petr": "2-petrus",
    "1. Joh": "1-johannes",
    "1. Johannes": "1-johannes",
    "1.Joh": "1-johannes",
    "2. Joh": "2-johannes",
    "2. Johannes": "2-johannes",
    "2.Joh": "2-johannes",
    "3. Joh": "3-johannes",
    "3. Johannes": "3-johannes",
    "3.Joh": "3-johannes",
    "Jud": "judas",
    "Offb": "offenbarung",
    "Offenbarung": "offenbarung",
}


def _normalise_book(raw_book: str) -> str:
    """Normalise spacing: '1. Mose' and '1.Mose' both match."""
    return raw_book.strip()


def _extract_title(html: str) -> str | None:
    """Extract the content of the <title> tag from HTML."""
    match = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    if match:
        return match.group(1).strip()
    return None


def _clean_ref_for_comparison(text: str) -> str:
    """Remove dots, dashes and spaces, lowercase for robust comparison."""
    return re.sub(r"[.\-\s]", "", text).lower()


async def _validate_via_bibleserver(
    ref: BibleReference,
    *,
    base_url: str,
    client: httpx.AsyncClient,
    timeout: float = 10.0,
    translation: str = "SLT",
) -> BibleValidationResult:
    """Validate a single reference by scraping bibleserver.com.

    It checks if the resulting page title matches the requested reference.
    Bibleserver auto-corrects invalid refs (e.g. Gen 60 -> Gen 50),
    so a title mismatch indicates an invalid reference.
    """
    book_slug = _BIBELSERVER_BOOK_MAP.get(ref.book)
    if not book_slug:
        return BibleValidationResult(
            reference=ref,
            is_valid=False,
            error_message=f"Unbekanntes Buch: {ref.book}",
        )

    # Build URL (similar to get_bibelserver_url)
    url = f"{base_url.rstrip('/')}/{translation}/{book_slug}{ref.chapter}"
    if ref.verse_start is not None:
        url += f",{ref.verse_start}"
        if ref.verse_end is not None:
            url += f"-{ref.verse_end}"

    try:
        resp = await client.get(url, timeout=timeout, follow_redirects=True)
        resp.raise_for_status()

        title = _extract_title(resp.text)
        if not title:
            return BibleValidationResult(
                reference=ref,
                is_valid=False,
                error_message="Seitentitel konnte nicht gelesen werden.",
                source_url=url,
            )

        # The title usually starts with the reference, e.g. "1.Mose 1,1 | ..."
        # Extract the part before the first pipe
        title_ref_part = title.split("|")[0].strip()

        # Comparison logic: normalize both and check if they are effectively the same.
        # "1-mose 1,1" (requested via slug) should match "1.Mose 1,1" (title)
        requested_clean = _clean_ref_for_comparison(f"{book_slug}{ref.chapter}")
        if ref.verse_start is not None:
            requested_clean += f",{ref.verse_start}"
            if ref.verse_end is not None:
                requested_clean += f"-{ref.verse_end}"

        title_clean = _clean_ref_for_comparison(title_ref_part)

        if requested_clean != title_clean:
            return BibleValidationResult(
                reference=ref,
                is_valid=False,
                error_message=f"Bibelstelle existiert nicht (Bibelserver zeigt stattdessen: {title_ref_part})",
                source_url=url,
            )

        return BibleValidationResult(
            reference=ref,
            is_valid=True,
            source_url=url,
        )

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            return BibleValidationResult(
                reference=ref,
                is_valid=False,
                error_message="Bibelstelle nicht gefunden (404).",
                source_url=url,
            )
        return BibleValidationResult(
            reference=ref,
            is_valid=False,
            error_message=f"Bibelserver-Fehler: {exc.response.status_code}",
            source_url=url,
        )
    except (httpx.HTTPError, httpx.TimeoutException) as exc:
        logger.warning("Bibelserver request failed for %s: %s", ref.raw_text, exc)
        return BibleValidationResult(
            reference=ref,
            is_valid=False,
            error_message=f"Bibelserver nicht erreichbar: {exc}",
        )


class BibleValidator:
    """Extract and validate Bible references from a DocumentStructure."""

    def __init__(
        self,
        config: ProofreadingConfig | None = None,
        *,
        use_online: bool = True,
    ) -> None:
        from mcp_lektor.config.settings import load_config

        self.config = config or load_config()
        self._base_url = self.config.bible_validation_base_url.rstrip("/")
        self._use_online = use_online and bool(self.config.bible_validation_base_url)
        self._timeout = self.config.bible_validation_timeout_seconds
        self._validation_translation = self.config.bible_validation_translation

    def extract_refs(self, structure: DocumentStructure) -> list[BibleReference]:
        """Extract all Bible references from paragraphs (skipping placeholders)."""
        refs: list[BibleReference] = []
        for para in structure.paragraphs:
            if para.is_placeholder_paragraph:
                continue
            text = para.proofreadable_text
            if not text.strip():
                continue
            for raw in extract_references(text, paragraph_index=para.index):
                refs.append(
                    BibleReference(
                        paragraph_index=raw["paragraph_index"],
                        raw_text=raw["raw_text"],
                        book=raw["book"],
                        chapter=raw["chapter"],
                        verse_start=raw["verse_start"],
                        verse_end=raw["verse_end"],
                    )
                )
        return refs

    def get_bibelserver_url(self, ref: BibleReference, translation: str) -> str | None:
        """Generate a bibleserver.com URL for a given reference and translation."""
        book_slug = _BIBELSERVER_BOOK_MAP.get(ref.book)
        if not book_slug:
            return None

        url = f"{self._base_url}/{translation}/{book_slug}{ref.chapter}"
        if ref.verse_start is not None:
            url += f",{ref.verse_start}"
            if ref.verse_end is not None:
                url += f"-{ref.verse_end}"
        return url

    async def validate(
        self,
        structure: DocumentStructure,
    ) -> list[BibleValidationResult]:
        """Extract and validate all Bible references.

        Returns one BibleValidationResult per detected reference.
        """
        refs = self.extract_refs(structure)
        if not refs:
            return []

        results: list[BibleValidationResult] = []
        if not self._use_online:
            # If online check is disabled, return explicit error results
            results = [
                BibleValidationResult(
                    reference=r,
                    is_valid=False,
                    error_message="Bibel-Validierung (online) ist deaktiviert.",
                )
                for r in refs
            ]
        else:
            async with httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                }
            ) as client:
                tasks = [
                    _validate_via_bibleserver(
                        r,
                        base_url=self._base_url,
                        client=client,
                        timeout=self._timeout,
                        translation=self._validation_translation,
                    )
                    for r in refs
                ]
                results = list(await asyncio.gather(*tasks))

        # Add comparison links to results
        translation_config = self.config.bible_translations
        for res in results:
            links = {}
            for slug, entry in translation_config.items():
                if entry.enabled:
                    url = self.get_bibelserver_url(res.reference, slug)
                    if url:
                        links[slug] = url
            res.comparison_links = links

        return results
