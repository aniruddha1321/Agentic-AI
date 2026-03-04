DEFAULT_WORDS = (
    "IRONMAN,THOR,HULK,SPIDERMAN,THANOS,VISION,WANDA,LOKI,GROOT,"
    "ROCKET,GAMORA,DRAX,ANTMAN,WASP,FALCON,PANTHER,NEBULA,HAWKEYE,"
    "BLACKWIDOW,STARLORD,MANTIS,SHURI,PEPPER,FURY,STARK,ROGERS,MARVEL,AVENGERS"
)

DIRS      = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
COLORS    = [
    "#e74c3c","#f39c12","#2ecc71","#3498db","#9b59b6","#1abc9c",
    "#e67e22","#e84393","#00cec9","#6c5ce7","#fd79a8","#55efc4",
    "#ffeaa7","#fab1a0","#74b9ff","#a29bfe","#ff7675","#00b894",
]


def parse_grid(text):
    if "GRID:" in text:
        text = text.split("GRID:", 1)[1].strip()
    if " | " in text:
        lines = text.split(" | ")
    else:
        lines = text.strip().split("\n")
    grid = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        row = [c.upper() for c in (line.split() if " " in line else line) if c.isalpha()]
        if row:
            grid.append(row)
    return grid


def find_word(grid, rows, word):
    for r in range(rows):
        for c in range(len(grid[r])):
            for di, (dr, dc) in enumerate(DIRS):
                cells, ok = [], True
                for i in range(len(word)):
                    nr, nc = r + dr*i, c + dc*i
                    if nr < 0 or nr >= rows or nc < 0 or nc >= len(grid[nr]) or grid[nr][nc] != word[i]:
                        ok = False; break
                    cells.append((nr, nc))
                if ok:
                    return {"word": word, "cells": cells}
    return None


def solve(raw_grid_text, words_to_find):
    grid  = parse_grid(raw_grid_text)
    if not grid:
        return "ERROR: Could not parse grid from OCR text."

    rows  = len(grid)
    cols  = max(len(r) for r in grid)
    words = [w.strip().upper() for w in words_to_find.split(",") if w.strip()]

    found, missing = [], []
    for i, word in enumerate(words):
        res = find_word(grid, rows, word)
        if res:
            res["color"] = COLORS[i % len(COLORS)]
            found.append(res)
        else:
            missing.append(word)

    cell_color = {}
    for fw in found:
        for (r, c) in fw["cells"]:
            cell_color[(r, c)] = fw["color"]

    pills = "".join(
        f'<span style="background:{fw["color"]};color:#fff;padding:4px 12px;'
        f'border-radius:20px;margin:3px;font-weight:bold;display:inline-block">'
        f'{fw["word"]}</span>'
        for fw in found
    )
    if missing:
        pills += "".join(
            f'<span style="background:#ccc;color:#555;padding:4px 12px;'
            f'border-radius:20px;margin:3px;display:inline-block">'
            f'{w}</span>'
            for w in missing
        )

    cells_html = ""
    for r in range(rows):
        cells_html += "<tr>"
        for c in range(cols):
            letter = grid[r][c] if c < len(grid[r]) else ""
            bg     = cell_color.get((r, c), "")
            style  = f' style="background:{bg};color:#fff"' if bg else ""
            cells_html += f"<td{style}>{letter}</td>"
        cells_html += "</tr>"

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
body{{font-family:Arial,sans-serif;background:#fff;color:#222;padding:20px}}
h2{{margin-bottom:6px}}
.pills{{margin:8px 0 14px}}
table{{border-collapse:collapse;margin-top:10px}}
table td{{width:26px;height:26px;text-align:center;vertical-align:middle;font-weight:bold;font-size:13px;border:1px solid #ddd}}
.nf{{color:#999;margin-top:10px;font-size:13px}}
</style></head>
<body>
<h2>Word Search Solution</h2>
<div>Found words: <strong>{len(found)} of {len(words)}</strong></div>
<div class="pills">{pills}</div>
<table>{cells_html}</table>
{('<div class="nf">Not found: ' + ', '.join(missing) + '</div>') if missing else ''}
</body></html>"""
    return html


def lambda_handler(event, context):
    is_agent = "actionGroup" in event

    if is_agent:
        params        = {p["name"]: p["value"] for p in event.get("parameters", [])}
        raw_grid_text = params.get("raw_grid_text", "").strip()
        words_to_find = params.get("words_to_find", DEFAULT_WORDS).strip()
        # If Agent passed full OCR output (both WORDS: and GRID: in raw_grid_text)
        if "WORDS:" in raw_grid_text and "GRID:" in raw_grid_text:
            lines_parts = raw_grid_text.split("\n", 1)
            words_to_find = lines_parts[0].replace("WORDS:", "").strip()
    else:
        raw_grid_text = event.get("raw_grid_text", "").strip()
        words_to_find = event.get("words_to_find", DEFAULT_WORDS).strip()

    result = solve(raw_grid_text, words_to_find)

    if is_agent:
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event["actionGroup"],
                "function":    event["function"],
                "functionResponse": {
                    "responseBody": {"TEXT": {"body": result}}
                }
            }
        }
    return {"statusCode": 200, "result": result}
