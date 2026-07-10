from app.parsers.aisle_parser import parse_aisle_volume_input
from app.parsers.aisle_parser import merge_sd_nd_volumes


def test_real_world_table_format_uses_first_numeric_token_only():
    raw = """C5	442	2 	12 	55 	371 	18	18	0	0	96.87%	0	-
C6	619	1 	20 	62 	508 	24	25	0	18	96.21%	1	0
C7	520	2 	19 	83 	399 	24	24	0	138	95.45%	2	1
C8	395	3 	7 	44 	330 	21	21	0	66	97.92%	0	1
C9	421	1 	10 	75 	344 	18	18	0	0	97.18%	0	-
C10	417	4 	10 	65 	333 	15	15	0	0	97.08%	0	-"""
    result = parse_aisle_volume_input(raw, "SD")
    assert result.volumes == {"C5": 442, "C6": 619, "C7": 520, "C8": 395, "C9": 421, "C10": 417}
    assert result.warnings == []


def test_accepts_tabs_spaces_empty_lines_and_supported_aisle_shapes():
    raw = "\nC5\t442\t2\nC05    443    9\nC10 417 4\nB9\t1250\t4\nB09    1251    5\nA01 99 1\n"
    result = parse_aisle_volume_input(raw)
    assert result.volumes == {"C5": 442, "C05": 443, "C10": 417, "B9": 1250, "B09": 1251, "A01": 99}


def test_invalid_lines_missing_volume_and_negative_values_warn_and_are_ignored():
    raw = "noise text\nC5\nC6 -10 2\nC7 abc 2\nC8 395 99"
    result = parse_aisle_volume_input(raw, "ND")
    assert result.volumes == {"C8": 395}
    assert len(result.warnings) == 4
    assert any("negatives Volume" in warning for warning in result.warnings)


def test_duplicate_aisles_warn_and_first_value_wins():
    result = parse_aisle_volume_input("C5 442 2\nC5 999 3", "SD")
    assert result.volumes == {"C5": 442}
    assert any("doppelte Aisle C5" in warning for warning in result.warnings)


def test_sd_and_nd_are_merged_by_aisle_with_missing_side_as_zero():
    rows = merge_sd_nd_volumes({"C5": 442, "C6": 619}, {"C5": 100, "C7": 150})
    by_aisle = {str(row["aisle"]): row for row in rows}
    assert by_aisle["C5"]["sd_volume"] == 442
    assert by_aisle["C5"]["nd_volume"] == 100
    assert by_aisle["C5"]["total_volume"] == 542
    assert by_aisle["C6"]["nd_volume"] == 0
    assert by_aisle["C7"]["sd_volume"] == 0
    assert sum(int(row["sd_volume"]) for row in rows) == 1061
    assert sum(int(row["nd_volume"]) for row in rows) == 250
    assert sum(int(row["total_volume"]) for row in rows) == 1311
    assert len(rows) == 3
    assert sorted({row["finger"] for row in rows}) == ["C"]
