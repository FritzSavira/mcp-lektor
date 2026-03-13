"""Validate Bible references via local data and provide rich citations."""

from __future__ import annotations

import logging

from mcp_lektor.config.models import ProofreadingConfig
from mcp_lektor.core.bible_provider import BibleProvider
from mcp_lektor.core.models import (
    BibleReference,
    BibleValidationResult,
    DocumentStructure,
)
from mcp_lektor.utils.bible_patterns import extract_references

logger = logging.getLogger(__name__)

# Bibelserver slug mapping for link generation
# Should cover all common variants to ensure functional links
_BIBELSERVER_SLUG_MAP: dict[str, str] = {
    "1. Mose": "1-mose", "1.Mose": "1-mose", "Gen": "1-mose", "Genesis": "1-mose",
    "2. Mose": "2-mose", "2.Mose": "2-mose", "Ex": "2-mose", "Exodus": "2-mose",
    "3. Mose": "3-mose", "3.Mose": "3-mose", "Lev": "3-mose", "Levitikus": "3-mose",
    "4. Mose": "4-mose", "4.Mose": "4-mose", "Num": "4-mose", "Numeri": "4-mose",
    "5. Mose": "5-mose", "5.Mose": "5-mose", "Dtn": "5-mose", "Deuteronomium": "5-mose",
    "Jos": "josua", "Josua": "josua",
    "Ri": "richter", "Richter": "richter",
    "Rut": "rut",
    "1. Sam": "1-samuel", "1.Samuel": "1-samuel", "1. Samuel": "1-samuel",
    "2. Sam": "2-samuel", "2.Samuel": "2-samuel", "2. Samuel": "2-samuel",
    "1. Kön": "1-koenige", "1. Koenige": "1-koenige", "1.Kön": "1-koenige", "1.Koenige": "1-koenige",
    "2. Kön": "2-koenige", "2. Koenige": "2-koenige", "2.Kön": "2-koenige", "2.Koenige": "2-koenige",
    "1. Chr": "1-chronik", "1. Chronik": "1-chronik", "1.Chr": "1-chronik",
    "2. Chr": "2-chronik", "2. Chronik": "2-chronik", "2.Chr": "2-chronik",
    "Esr": "esra", "Esra": "esra",
    "Neh": "nehemia", "Nehemia": "nehemia",
    "Est": "ester", "Ester": "ester",
    "Ijob": "hiob", "Hiob": "hiob", "Hi": "hiob",
    "Ps": "psalm", "Psalm": "psalm", "Psalmen": "psalm",
    "Spr": "sprueche", "Sprüche": "sprueche",
    "Koh": "prediger", "Pred": "prediger", "Prediger": "prediger",
    "Hld": "hohelied", "Hohelied": "hohelied",
    "Jes": "jesaja", "Jesaja": "jesaja",
    "Jer": "jeremia", "Jeremia": "jeremia",
    "Klgl": "klagelieder", "Klagelieder": "klagelieder",
    "Ez": "hesekiel", "Hes": "hesekiel", "Hesekiel": "hesekiel",
    "Dan": "daniel", "Daniel": "daniel",
    "Hos": "hosea", "Hosea": "hosea",
    "Joel": "joel",
    "Am": "amos", "Amos": "amos",
    "Obd": "obadja", "Obadja": "obadja",
    "Jona": "jona",
    "Mi": "micha", "Micha": "micha",
    "Nah": "nahum", "Nahum": "nahum",
    "Hab": "habakuk", "Habakuk": "habakuk",
    "Zef": "zefanja", "Zefanja": "zefanja",
    "Hag": "haggai", "Haggai": "haggai",
    "Sach": "sacharja", "Sacharja": "sacharja",
    "Mal": "maleachi", "Maleachi": "maleachi",
    "Mt": "matthaeus", "Matthäus": "matthaeus", "Matthaeus": "matthaeus",
    "Mk": "markus", "Markus": "markus",
    "Lk": "lukas", "Lukas": "lukas",
    "Joh": "johannes", "Johannes": "johannes",
    "Apg": "apostelgeschichte", "Apostelgeschichte": "apostelgeschichte",
    "Röm": "roemer", "Roem": "roemer", "Römer": "roemer", "Roemer": "roemer",
    "1. Kor": "1-korinther", "1. Korinther": "1-korinther", "1.Kor": "1-korinther",
    "2. Kor": "2-korinther", "2. Korinther": "2-korinther", "2.Kor": "2-korinther",
    "Gal": "galater", "Galater": "galater",
    "Eph": "epheser", "Epheser": "epheser",
    "Phil": "philipper", "Philipper": "philipper",
    "Kol": "kolosser", "Kolosser": "kolosser",
    "1. Thess": "1-thessalonicher", "1. Thessalonicher": "1-thessalonicher", "1.Thess": "1-thessalonicher",
    "2. Thess": "2-thessalonicher", "2. Thessalonicher": "2-thessalonicher", "2.Thess": "2-thessalonicher",
    "1. Tim": "1-timotheus", "1. Timotheus": "1-timotheus", "1.Tim": "1-timotheus",
    "2. Tim": "2-timotheus", "2. Timotheus": "2-timotheus", "2.Tim": "2-timotheus",
    "Tit": "titus", "Titus": "titus",
    "Phlm": "philemon", "Philemon": "philemon",
    "Hebr": "hebraeer", "Hebreaer": "hebraeer", "Hebräer": "hebraeer",
    "Jak": "jakobus", "Jakobus": "jakobus",
    "1. Petr": "1-petrus", "1. Petrus": "1-petrus", "1.Petr": "1-petrus",
    "2. Petr": "2-petrus", "2. Petrus": "2-petrus", "2.Petr": "2-petrus",
    "1. Joh": "1-johannes", "1. Johannes": "1-johannes", "1.Joh": "1-johannes",
    "2. Joh": "2-johannes", "2. Johannes": "2-johannes", "2.Joh": "2-johannes",
    "3. Joh": "3-johannes", "3. Johannes": "3-johannes", "3.Joh": "3-johannes",
    "Jud": "judas", "Judas": "judas",
    "Offb": "offenbarung", "Offenbarung": "offenbarung",
}


class BibleValidator:
    """Extract and validate Bible references using a local BibleProvider."""

    def __init__(
        self,
        config: ProofreadingConfig | None = None,
        provider: BibleProvider | None = None,
    ) -> None:
        from mcp_lektor.config.settings import load_config

        self.config = config or load_config()
        self.provider = provider or BibleProvider(self.config.local_bible_data_dir)
        self._base_url = self.config.bible_validation_base_url.rstrip("/")

    def extract_refs(self, structure: DocumentStructure) -> list[BibleReference]:
        """Extract all Bible references from paragraphs."""
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
                        char_offset_start=raw["match_start"],
                        char_offset_end=raw["match_end"],
                    )
                )
        return refs

    def get_bibelserver_url(self, ref: BibleReference, translation: str) -> str | None:
        """Generate a bibleserver.com URL for a given reference and translation."""
        # Use lowercase for robust lookup in slug map
        book_slug = _BIBELSERVER_SLUG_MAP.get(ref.book) or _BIBELSERVER_SLUG_MAP.get(ref.book.strip())
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
        """Extract and validate all Bible references via local provider."""
        refs = self.extract_refs(structure)
        if not refs:
            return []

        results: list[BibleValidationResult] = []
        self.provider.load_all()

        for ref in refs:
            # Check existence (against master translation)
            is_valid = self.provider.exists(ref.book, ref.chapter, ref.verse_start or 1)
            
            error_message = None
            if not is_valid:
                if not self.provider._data:
                    error_message = "KEINE BIBELTEXTE GELADEN. Bitte Verzeichnis 'data/bibles' prüfen."
                else:
                    error_message = f"Stelle existiert nicht in der Menge-Bibel: {ref.book} {ref.chapter}"
                    if ref.verse_start:
                        error_message += f":{ref.verse_start}"

            # Get local texts if valid
            local_texts = {}
            if is_valid:
                local_texts = self.provider.get_texts(
                    ref.book, ref.chapter, ref.verse_start or 1, ref.verse_end
                )

            # Generate comparison links
            links = {}
            if self.config.enable_bible_links:
                for slug, entry in self.config.bible_translations.items():
                    if entry.enabled:
                        url = self.get_bibelserver_url(ref, slug)
                        if url:
                            links[slug] = url

            results.append(
                BibleValidationResult(
                    reference=ref,
                    is_valid=is_valid,
                    error_message=error_message,
                    local_texts=local_texts,
                    comparison_links=links,
                )
            )

        return results
