from mcp_lektor.core.bible_provider import BibleProvider
import json

p = BibleProvider(data_dir="data/bibles")
p.load_all()

book = "Epheser"
chapter = 5
verse = 8

print(f"Testing: {book} {chapter}:{verse}")
norm = p.normalize_book_name(book)
print(f"Normalized name: '{norm}'")

exists = p.exists(book, chapter, verse)
print(f"Exists in Menge: {exists}")

if not exists:
    # Debug: Check if EPH exists in data
    menge_data = p._data.get("menge", {})
    print(f"Key 'EPH' in Menge keys: {'EPH' in menge_data}")
    if 'EPH' in menge_data:
        eph_data = menge_data['EPH']
        print(f"Chapter '5' in EPH keys: {'5' in eph_data}")
        if '5' in eph_data:
            print(f"Verse '8' in Chapter 5 keys: {'8' in eph_data['5']}")
            print(f"All verses in EPH 5: {list(eph_data['5'].keys())}")
