import re
from app.models import AisleVolume

AISLE_RE = re.compile(r"(?P<label>(?:aisle|finger)?\s*[A-Za-z]{0,2}\d{1,3}|[A-Za-z]\d{1,3})", re.IGNORECASE)
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")

def parse_aisle_volumes(raw_text: str) -> list[AisleVolume]:
    rows: list[AisleVolume] = []
    for line in raw_text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        label_match = AISLE_RE.search(clean)
        numbers = NUMBER_RE.findall(clean)
        if not label_match or not numbers:
            continue
        label = re.sub(r"^(aisle|finger)\s*", "", label_match.group("label"), flags=re.IGNORECASE).upper()
        volume = int(float(numbers[-1].replace(",", ".")))
        rows.append(AisleVolume(aisle=label, volume=volume))
    return rows
