from langflow.custom import Component
from langflow.io import DataInput, Output
from langflow.schema.message import Message


class WordSearchSolver(Component):
    display_name = "Word Search Solver"
    description = "Finds words in a letter grid in all 8 directions"
    icon = "search"
    name = "word_search_solver"

    inputs = [
        DataInput(
            name="grid_data",
            display_name="Grid Data",
            info="Parsed grid data from Grid Parser component",
        ),
    ]

    outputs = [
        Output(display_name="Search Results", name="search_results", method="solve"),
    ]

    def solve(self) -> Message:
        grid = self.grid_data.data["grid"]
        words = self.grid_data.data["words"]
        rows = len(grid)
        if rows == 0:
            return Message(text="ERROR: Empty grid received")
        cols = max(len(r) for r in grid)

        DIRS = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        DIR_NAMES = ["→","←","↓","↑","↘","↙","↗","↖"]
        COLORS = [
            "#e74c3c","#f39c12","#2ecc71","#3498db","#9b59b6",
            "#1abc9c","#e67e22","#e84393","#00cec9","#6c5ce7",
            "#fd79a8","#55efc4","#ffeaa7","#fab1a0","#74b9ff",
            "#a29bfe","#ff7675","#00b894","#fdcb6e","#e17055",
        ]

        def find_word(word):
            for r in range(rows):
                for c in range(len(grid[r])):
                    for d_idx, (dr, dc) in enumerate(DIRS):
                        found = True
                        cells = []
                        for i in range(len(word)):
                            nr, nc = r + dr * i, c + dc * i
                            if nr < 0 or nr >= rows or nc < 0 or nc >= len(grid[nr]):
                                found = False
                                break
                            if grid[nr][nc] != word[i]:
                                found = False
                                break
                            cells.append([nr, nc])
                        if found:
                            return {"word": word, "cells": cells, "direction": DIR_NAMES[d_idx]}
            return None

        found_words = []
        not_found_words = []
        for idx, word in enumerate(words):
            result = find_word(word)
            if result:
                result["color"] = COLORS[idx % len(COLORS)]
                found_words.append(result)
            else:
                not_found_words.append(word)

        lines = [f"GRID ({rows}x{cols}):"]
        lines.append("\n".join("  " + " ".join(r) for r in grid))
        lines.append(f"\nFOUND {len(found_words)} of {len(words)} WORDS:")
        for fw in found_words:
            lines.append(f"  {fw['word']} dir:{fw['direction']} color:{fw['color']} cells:{fw['cells']}")
        if not_found_words:
            lines.append(f"\nNOT FOUND: {', '.join(not_found_words)}")

        return Message(text="\n".join(lines))