"""Local Bible knowledge base for validation and citation."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Standard Internal Book IDs (compatible with OSIS/Zefania)
# Mapping is stored lowercase for case-insensitive lookup
_BOOK_ID_MAP: dict[str, str] = {
    k.lower(): v for k, v in {
        "1. Mose": "GEN", "1.Mose": "GEN", "Gen": "GEN", "Genesis": "GEN",
        "2. Mose": "EXO", "2.Mose": "EXO", "Ex": "EXO", "Exodus": "EXO",
        "3. Mose": "LEV", "3.Mose": "LEV", "Lev": "LEV", "Levitikus": "LEV",
        "4. Mose": "NUM", "4.Mose": "NUM", "Num": "NUM", "Numeri": "LEV",
        "5. Mose": "DTN", "5.Mose": "DTN", "Dtn": "DTN", "Deuteronomium": "DTN",
        "Jos": "JOS", "Josua": "JOS",
        "Ri": "JDG", "Richter": "JDG",
        "Rut": "RUT",
        "1. Sam": "1SA", "1.Samuel": "1SA", "1. Samuel": "1SA",
        "2. Sam": "2SA", "2.Samuel": "2SA", "2. Samuel": "2SA",
        "1. Kön": "1KI", "1. Koenige": "1KI", "1.Kön": "1KI", "1.Koenige": "1KI",
        "2. Kön": "2KI", "2. Koenige": "2KI", "2.Kön": "2KI", "2.Koenige": "2KI",
        "1. Chr": "1CH", "1. Chronik": "1CH", "1.Chr": "1CH",
        "2. Chr": "2CH", "2. Chronik": "2CH", "2.Chr": "2CH",
        "Esr": "EZR", "Esra": "EZR",
        "Neh": "NEH", "Nehemia": "NEH",
        "Est": "EST", "Ester": "EST",
        "Ijob": "JOB", "Hiob": "JOB", "Hi": "JOB",
        "Ps": "PSA", "Psalm": "PSA", "Psalmen": "PSA",
        "Spr": "PRO", "Sprueche": "PRO", "Sprüche": "PRO",
        "Koh": "ECC", "Pred": "ECC", "Prediger": "ECC",
        "Hld": "SNG", "Hohelied": "SNG",
        "Jes": "ISA", "Jesaja": "ISA",
        "Jer": "JER", "Jeremia": "JER",
        "Klgl": "LAM", "Klagelieder": "LAM",
        "Ez": "EZK", "Hes": "EZK", "Hesekiel": "EZK",
        "Dan": "DAN", "Daniel": "DAN",
        "Hos": "HOS", "Hosea": "HOS",
        "Joel": "JOL", "Am": "AMO", "Obd": "OBA", "Jona": "JON",
        "Mi": "MIC", "Micha": "MIC",
        "Nah": "NAM", "Nahum": "NAM",
        "Hab": "HAB", "Habakuk": "HAB",
        "Zef": "ZEP", "Zefanja": "ZEP",
        "Hag": "HAG", "Haggai": "HAG",
        "Sach": "ZEC", "Sacharja": "ZEC",
        "Mal": "MAL", "Maleachi": "MAL",
        "Mt": "MAT", "Matthaeus": "MAT", "Markus": "MAT", "Mk": "MRK",
        "Lk": "LUK", "Lukas": "LUK", "Joh": "JHN", "Johannes": "JHN",
        "Apg": "ACT", "Apostelgeschichte": "ACT",
        "Röm": "ROM", "Roem": "ROM", "Römer": "ROM", "Roemer": "ROM",
        "1. Kor": "1CO", "1. Korinther": "1CO", "1.Kor": "1CO",
        "2. Kor": "2CO", "2. Korinther": "2CO", "2.Kor": "2CO",
        "Gal": "GAL", "Galater": "GAL",
        "Eph": "EPH", "Epheser": "EPH",
        "Phil": "PHP", "Philipper": "PHP",
        "Kol": "COL", "Kolosser": "COL",
        "1. Thess": "1TH", "1. Thessalonicher": "1TH", "1.Thess": "1TH",
        "2. Thess": "2TH", "2. Thessalonicher": "2TH", "2.Thess": "2TH",
        "1. Tim": "1TI", "1. Timotheus": "1TI", "1.Tim": "1TI",
        "2. Tim": "2TI", "2. Timotheus": "2TI", "2.Tim": "2TI",
        "Tit": "TIT", "Titus": "TIT",
        "Phlm": "PHM", "Philemon": "PHM",
        "Hebr": "HEB", "Hebreaer": "HEB", "Hebräer": "HEB",
        "Jak": "JAS", "Jakobus": "JAS",
        "1. Petr": "1PE", "1. Petrus": "1PE", "1.Petr": "1PE",
        "2. Petr": "2PE", "2. Petrus": "2PE", "2.Petr": "2PE",
        "1. Joh": "1JN", "1. Johannes": "1JN", "1.Joh": "1JN",
        "2. Joh": "2JN", "2. Johannes": "2JN", "2.Joh": "2JN",
        "3. Joh": "3JN", "3. Johannes": "3JN", "3.Joh": "3JN",
        "Jud": "JUD", "Judas": "JUD",
        "Offb": "REV", "Offenbarung": "REV",
    }.items()
}


class BibleProvider:
    """Provides local access to Bible translations for validation and text retrieval."""

    def __init__(self, data_dir: str | Path = "data/bibles") -> None:
        self.data_dir = Path(data_dir).absolute()
        self._data: dict[str, dict[str, Any]] = {}  # {translation: {book: {chapter: {verse: text}}}}
        self._is_loaded = False

    def normalize_book_name(self, name: str) -> str | None:
        """Map common German book names/abbreviations to standard IDs."""
        clean_name = name.strip().lower()
        # Handle cases like "1. Mose" vs "1.Mose"
        clean_name = clean_name.replace(". ", ".")
        book_id = _BOOK_ID_MAP.get(clean_name)
        if not book_id:
            # Try without dot as well
            book_id = _BOOK_ID_MAP.get(clean_name.replace(".", ""))
        return book_id

    def load_all(self) -> None:
        """Load all JSON files from the data directory into memory."""
        if self._is_loaded:
            return

        if not self.data_dir.exists():
            logger.error("Bible data directory not found: %s", self.data_dir)
            return

        json_files = list(self.data_dir.glob("*.json"))
        if not json_files:
            logger.warning("No .json files found in %s", self.data_dir)

        for file_path in json_files:
            translation_name = file_path.stem.lower()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self._data[translation_name] = json.load(f)
                logger.info("Loaded Bible translation: %s (Books: %d)", 
                            translation_name, len(self._data[translation_name]))
            except Exception as e:
                logger.error("Failed to load Bible translation %s: %s", translation_name, e)

        self._is_loaded = True

    def exists(
        self,
        book: str,
        chapter: int,
        verse: int,
        master_translation: str = "menge"
    ) -> bool:
        """Check if a specific verse exists in the master translation."""
        if not self._is_loaded:
            self.load_all()

        book_id = self.normalize_book_name(book)
        if not book_id:
            logger.debug("Exists check failed: Unknown book name '%s'", book)
            return False

        trans_data = self._data.get(master_translation.lower())
        if not trans_data:
            logger.debug("Exists check failed: Master translation '%s' not loaded", master_translation)
            return False

        # Nested lookup: book -> chapter -> verse
        book_data = trans_data.get(book_id)
        if not book_data:
            logger.debug("Exists check failed: Book ID '%s' not in '%s'", book_id, master_translation)
            return False

        chapter_data = book_data.get(str(chapter))
        if not chapter_data:
            logger.debug("Exists check failed: Chapter %d not in %s", chapter, book_id)
            return False

        found = str(verse) in chapter_data
        if not found:
            logger.debug("Exists check failed: Verse %d not in %s %d", verse, book_id, chapter)
        
        return found

    def get_verse_text(
        self,
        translation: str,
        book: str,
        chapter: int,
        verse: int
    ) -> str | None:
        """Retrieve the text of a specific verse from a translation."""
        if not self._is_loaded:
            self.load_all()

        book_id = self.normalize_book_name(book)
        if not book_id:
            return None

        trans_data = self._data.get(translation.lower())
        if not trans_data:
            return None

        return trans_data.get(book_id, {}).get(str(chapter), {}).get(str(verse))

    def get_texts(
        self,
        book: str,
        chapter: int,
        verse_start: int,
        verse_end: int | None = None
    ) -> dict[str, str]:
        """Retrieve texts for a verse range from all loaded translations."""
        if not self._is_loaded:
            self.load_all()

        results: dict[str, str] = {}
        for trans_name in self._data:
            texts = []
            end = verse_end if verse_end is not None else verse_start
            for v in range(verse_start, end + 1):
                text = self.get_verse_text(trans_name, book, chapter, v)
                if text:
                    texts.append(text)
            
            if texts:
                results[trans_name] = " ".join(texts)
        
        return results
