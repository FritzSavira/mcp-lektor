from mcp_lektor.utils.bible_patterns import extract_references

text = "Epheser 5, 8"
refs = extract_references(text)
print(f"Text: '{text}'")
for r in refs:
    print(f"Match: {r}")
