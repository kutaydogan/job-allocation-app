from __future__ import annotations

import re
from dataclasses import dataclass, field

AISLE_TOKEN_RE = re.compile(r"^[A-Za-z]\d{1,3}$")
NON_NEGATIVE_INTEGER_RE = re.compile(r"^\d+$")
NEGATIVE_NUMBER_RE = re.compile(r"^-\d+(?:[.,]\d+)?$")


@dataclass
class ParsedAisleVolumes:
    """Result for one pasted SD or ND volume input.

    Duplicate aisles are treated as validation warnings and the first value wins.
    This prevents accidental double counting when the same aisle appears twice in
    one pasted source while still allowing the rest of the input to be used.
    """

    volumes: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def parse_aisle_volume_input(raw_text: str, source_label: str = "Input") -> ParsedAisleVolumes:
    result = ParsedAisleVolumes()
    seen: set[str] = set()

    for line_number, line in enumerate((raw_text or "").splitlines(), start=1):
        clean = line.strip()
        if not clean:
            continue

        tokens = clean.split()
        if len(tokens) < 2 or not AISLE_TOKEN_RE.match(tokens[0]):
            result.warnings.append(f"{source_label} Zeile {line_number}: keine gültige Aisle mit folgendem Volume erkannt")
            continue

        aisle = tokens[0]
        volume_token = tokens[1]
        if NEGATIVE_NUMBER_RE.match(volume_token):
            result.warnings.append(f"{source_label} Zeile {line_number}: negatives Volume für {aisle} wird ignoriert")
            continue
        if not NON_NEGATIVE_INTEGER_RE.match(volume_token):
            result.warnings.append(f"{source_label} Zeile {line_number}: Volume für {aisle} muss eine nicht-negative ganze Zahl sein")
            continue

        match_key = aisle.upper()
        if match_key in seen:
            result.warnings.append(f"{source_label} Zeile {line_number}: doppelte Aisle {aisle}; erster Wert bleibt erhalten")
            continue

        seen.add(match_key)
        result.volumes[aisle] = int(volume_token)

    return result


def merge_sd_nd_volumes(sd: dict[str, int], nd: dict[str, int]) -> list[dict[str, int | str]]:
    """Merge separate SD and ND dictionaries by case-insensitive aisle key."""

    by_key = {a.upper(): a for a in list(sd.keys()) + list(nd.keys())}
    rows: list[dict[str, int | str]] = []
    for key in sorted(by_key):
        aisle = by_key[key]
        sd_volume = next((v for a, v in sd.items() if a.upper() == key), 0)
        nd_volume = next((v for a, v in nd.items() if a.upper() == key), 0)
        rows.append({
            "finger": aisle[0].upper(),
            "aisle": aisle,
            "sd_volume": sd_volume,
            "nd_volume": nd_volume,
            "total_volume": sd_volume + nd_volume,
        })
    return rows


def parse_aisle_volumes(raw_text: str) -> dict[str, int]:
    """Backward-compatible helper returning only parsed volumes."""

    return parse_aisle_volume_input(raw_text).volumes
