"""Validate Bible references via regex extraction and API lookup."""

from __future__ import annotations

import asyncio
import logging

import httpx

from mcp_lektor.config.models import ProofreadingConfig
from mcp_lektor.core.models import (
    BibleReference,
    BibleValidationResult,
    DocumentStructure,
)
from mcp_lektor.utils.bible_patterns import extract_references

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Canonical chapter/verse limits  (fallback when API is unavailable)
# Source: Protestant canon, Einheitsübersetzung verse counts
# ---------------------------------------------------------------------------
_FALLBACK_CHAPTER_COUNTS: dict[str, int] = {
    # Pentateuch
    "Gen": 50,
    "1. Mose": 50,
    "1.Mose": 50,
    "Ex": 40,
    "2. Mose": 40,
    "2.Mose": 40,
    "Lev": 27,
    "3. Mose": 27,
    "3.Mose": 27,
    "Num": 36,
    "4. Mose": 36,
    "4.Mose": 36,
    "Dtn": 34,
    "5. Mose": 34,
    "5.Mose": 34,
    # Historical
    "Jos": 24,
    "Ri": 21,
    "Rut": 4,
    "1. Sam": 31,
    "1.Sam": 31,
    "1. Samuel": 31,
    "2. Sam": 24,
    "2.Sam": 24,
    "2. Samuel": 24,
    "1. Kön": 22,
    "1. Koenige": 22,
    "1.Kön": 22,
    "1.Koenige": 22,
    "2. Kön": 25,
    "2. Koenige": 25,
    "2.Kön": 25,
    "2.Koenige": 25,
    "1. Chr": 29,
    "1. Chronik": 29,
    "1.Chr": 29,
    "2. Chr": 36,
    "2. Chronik": 36,
    "2.Chr": 36,
    "Esr": 10,
    "Neh": 13,
    "Est": 10,
    # Wisdom
    "Ijob": 42,
    "Hiob": 42,
    "Hi": 42,
    "Ps": 150,
    "Spr": 31,
    "Koh": 12,
    "Pred": 12,
    "Hld": 8,
    # Major Prophets
    "Jes": 66,
    "Jer": 52,
    "Klgl": 5,
    "Ez": 48,
    "Hes": 48,
    "Dan": 12,
    # Minor Prophets
    "Hos": 14,
    "Joel": 4,
    "Am": 9,
    "Obd": 1,
    "Jona": 4,
    "Mi": 7,
    "Nah": 3,
    "Hab": 3,
    "Zef": 3,
    "Hag": 2,
    "Sach": 14,
    "Mal": 3,
    # NT
    "Mt": 28,
    "Mk": 16,
    "Lk": 24,
    "Joh": 21,
    "Apg": 28,
    "Röm": 16,
    "Roem": 16,
    "Römer": 16,
    "Roemer": 16,
    "1. Kor": 16,
    "1. Korinther": 16,
    "1.Kor": 16,
    "2. Kor": 13,
    "2. Korinther": 13,
    "2.Kor": 13,
    "Gal": 6,
    "Galater": 6,
    "Eph": 6,
    "Epheser": 6,
    "Phil": 4,
    "Philipper": 4,
    "Kol": 4,
    "Kolosser": 4,
    "1. Thess": 5,
    "1. Thessalonicher": 5,
    "1.Thess": 5,
    "2. Thess": 3,
    "2. Thessalonicher": 3,
    "2.Thess": 3,
    "1. Tim": 6,
    "1. Timotheus": 6,
    "1.Tim": 6,
    "2. Tim": 4,
    "2. Timotheus": 4,
    "2.Tim": 4,
    "Tit": 3,
    "Phlm": 1,
    "Hebr": 13,
    "Hebreaer": 13,
    "Hebräer": 13,
    "Jak": 5,
    "1. Petr": 5,
    "1. Petrus": 5,
    "1.Petr": 5,
    "2. Petr": 3,
    "2. Petrus": 3,
    "2.Petr": 3,
    "1. Joh": 5,
    "1. Johannes": 5,
    "1.Joh": 5,
    "2. Joh": 1,
    "2. Johannes": 1,
    "2.Joh": 1,
    "3. Joh": 1,
    "3. Johannes": 1,
    "3.Joh": 1,
    "Jud": 1,
    "Offb": 22,
    "Offenbarung": 22,
}

# Book-name → bible-api.com book id mapping
_API_BOOK_MAP: dict[str, str] = {
    "Gen": "GEN",
    "1. Mose": "GEN",
    "1.Mose": "GEN",
    "Ex": "EXO",
    "2. Mose": "EXO",
    "2.Mose": "EXO",
    "Lev": "LEV",
    "3. Mose": "LEV",
    "3.Mose": "LEV",
    "Num": "NUM",
    "4. Mose": "NUM",
    "4.Mose": "NUM",
    "Dtn": "DEU",
    "5. Mose": "DEU",
    "5.Mose": "DEU",
    "Jos": "JOS",
    "Ri": "JDG",
    "Rut": "RUT",
    "1. Sam": "1SA",
    "1.Sam": "1SA",
    "1. Samuel": "1SA",
    "2. Sam": "2SA",
    "2.Sam": "2SA",
    "2. Samuel": "2SA",
    "1. Kön": "1KI",
    "1.Kön": "1KI",
    "1. Koenige": "1KI",
    "1.Koenige": "1KI",
    "2. Kön": "2KI",
    "2.Kön": "2KI",
    "2. Koenige": "2KI",
    "2.Koenige": "2KI",
    "1. Chr": "1CH",
    "1.Chr": "1CH",
    "1. Chronik": "1CH",
    "2. Chr": "2CH",
    "2.Chr": "2CH",
    "2. Chronik": "2CH",
    "Esr": "EZR",
    "Neh": "NEH",
    "Est": "EST",
    "Ijob": "JOB",
    "Hiob": "JOB",
    "Hi": "JOB",
    "Ps": "PSA",
    "Spr": "PRO",
    "Koh": "ECC",
    "Pred": "ECC",
    "Hld": "SNG",
    "Jes": "ISA",
    "Jer": "JER",
    "Klgl": "LAM",
    "Ez": "EZK",
    "Hes": "EZK",
    "Dan": "DAN",
    "Hos": "HOS",
    "Joel": "JOL",
    "Am": "AMO",
    "Obd": "OBA",
    "Jona": "JON",
    "Mi": "MIC",
    "Nah": "NAM",
    "Hab": "HAB",
    "Zef": "ZEP",
    "Hag": "HAG",
    "Sach": "ZEC",
    "Mal": "MAL",
    "Mt": "MAT",
    "Mk": "MRK",
    "Lk": "LUK",
    "Joh": "JHN",
    "Apg": "ACT",
    "Röm": "ROM",
    "Roem": "ROM",
    "Römer": "ROM",
    "Roemer": "ROM",
    "1. Kor": "1CO",
    "1.Kor": "1CO",
    "1. Korinther": "1CO",
    "2. Kor": "2CO",
    "2.Kor": "2CO",
    "2. Korinther": "2CO",
    "Gal": "GAL",
    "Galater": "GAL",
    "Eph": "EPH",
    "Epheser": "EPH",
    "Phil": "PHP",
    "Philipper": "PHP",
    "Kol": "COL",
    "Kolosser": "COL",
    "1. Thess": "1TH",
    "1.Thess": "1TH",
    "1. Thessalonicher": "1TH",
    "2. Thess": "2TH",
    "2.Thess": "2TH",
    "2. Thessalonicher": "2TH",
    "1. Tim": "1TI",
    "1.Tim": "1TI",
    "1. Timotheus": "1TI",
    "2. Tim": "2TI",
    "2.Tim": "2TI",
    "2. Timotheus": "2TI",
    "Tit": "TIT",
    "Phlm": "PHM",
    "Hebr": "HEB",
    "Hebreaer": "HEB",
    "Hebräer": "HEB",
    "Jak": "JAS",
    "1. Petr": "1PE",
    "1.Petr": "1PE",
    "1. Petrus": "1PE",
    "2. Petr": "2PE",
    "2.Petr": "2PE",
    "2. Petrus": "2PE",
    "1. Joh": "1JN",
    "1.Joh": "1JN",
    "1. Johannes": "1JN",
    "2. Joh": "2JN",
    "2.Joh": "2JN",
    "2. Johannes": "2JN",
    "3. Joh": "3JN",
    "3.Joh": "3JN",
    "3. Johannes": "3JN",
    "Jud": "JUD",
    "Offb": "REV",
    "Offenbarung": "REV",
}

# Book-name → bibelserver.com slug mapping
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


def _validate_offline(ref: BibleReference) -> BibleValidationResult:
    """Validate against the built-in chapter-count table."""
    book = _normalise_book(ref.book)
    max_ch = _FALLBACK_CHAPTER_COUNTS.get(book)
    if max_ch is None:
        return BibleValidationResult(
            reference=ref,
            is_valid=False,
            error_message=f"Unbekanntes Buch: {ref.book}",
        )
    if ref.chapter < 1 or ref.chapter > max_ch:
        return BibleValidationResult(
            reference=ref,
            is_valid=False,
            error_message=(
                f"{ref.book} hat nur {max_ch} Kapitel " f"(angegeben: {ref.chapter})."
            ),
        )
    # Without a full verse table we cannot verify verses offline –
    # accept them optimistically and note the limitation.
    return BibleValidationResult(
        reference=ref,
        is_valid=True,
        error_message=None,
        source_url=None,
    )


async def _validate_online(
    ref: BibleReference,
    *,
    api_base: str,
    client: httpx.AsyncClient,
    timeout: float = 10.0,
    use_fallback: bool = True,
) -> BibleValidationResult:
    """Validate a single reference against an online Bible API.

    Uses the API endpoint pattern:  GET {api_base}/{book_id} {chapter}:{verse}
    Expected: bible-api.com compatible JSON response.
    Falls back to offline validation on network errors.
    """
    book = _normalise_book(ref.book)
    api_id = _API_BOOK_MAP.get(book)
    if api_id is None:
        return _validate_offline(ref)

    # Build query string  e.g. "john 3:16" or "genesis 1:1-5"
    if ref.verse_start is not None:
        query_parts_str = f"{api_id.lower()} {ref.chapter}:{ref.verse_start}"
        if ref.verse_end is not None:
            query_parts_str += f"-{ref.verse_end}"
    else:
        query_parts_str = f"{api_id.lower()} {ref.chapter}"

    url = f"{api_base}/{query_parts_str}"
    try:
        resp = await client.get(url, timeout=timeout)
        if resp.status_code == 404:
            return BibleValidationResult(
                reference=ref,
                is_valid=False,
                error_message=f"Bibelstelle nicht gefunden: {ref.raw_text}",
                source_url=url,
            )
        resp.raise_for_status()
        data = resp.json()
        # bible-api.com returns {"error": "..."} on invalid refs
        if "error" in data:
            return BibleValidationResult(
                reference=ref,
                is_valid=False,
                error_message=data["error"],
                source_url=url,
            )
        return BibleValidationResult(
            reference=ref,
            is_valid=True,
            source_url=url,
        )
    except (httpx.HTTPError, httpx.TimeoutException) as exc:
        logger.warning(
            "Bible API request failed for %s: %s",
            ref.raw_text,
            exc,
        )
        if not use_fallback:
            return BibleValidationResult(
                reference=ref,
                is_valid=False,
                error_message=f"API nicht erreichbar: {exc}",
            )

        result = _validate_offline(ref)
        result.error_message = (
            f"API nicht erreichbar – Offline-Prüfung: "
            f"{result.error_message or 'OK (nur Kapitel geprüft)'}"
        )
        return result


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
        self._api_base = self.config.bible_api_url.rstrip("/")
        self._use_online = use_online and bool(self.config.bible_api_url)
        self._timeout = self.config.bible_api_timeout_seconds

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
        """Generate a bibelserver.com URL for a given reference and translation."""
        book_slug = _BIBELSERVER_BOOK_MAP.get(ref.book)
        if not book_slug:
            return None

        url = f"https://www.bibelserver.com/{translation}/{book_slug}{ref.chapter}"
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
            results = [_validate_offline(r) for r in refs]
        else:
            async with httpx.AsyncClient() as client:
                tasks = [
                    _validate_online(
                        r,
                        api_base=self._api_base,
                        client=client,
                        timeout=self._timeout,
                        use_fallback=self.config.use_bible_offline_fallback,
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
                        # Use the shorthand (slug) as key,
                        # just like before, but filtered.
                        links[slug] = url
            res.comparison_links = links

        return results
