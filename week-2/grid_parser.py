from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Data


class GridParser(Component):
    display_name = "Grid Parser"
    description = "Parses raw OCR text into a structured 2D letter grid"
    icon = "grid-3x3"
    name = "grid_parser"

    inputs = [
        MessageTextInput(
            name="raw_grid_text",
            display_name="Raw Grid Text",
            info="The raw grid text from Gemini vision output",
        ),
        MessageTextInput(
            name="words_to_find",
            display_name="Words to Find (comma-separated)",
            info="Comma-separated list of words to search for",
            value="IRONMAN,THOR,HULK,SPIDERMAN,THANOS,VISION,WANDA,LOKI,GROOT,ROCKET,GAMORA,DRAX,ANTMAN,WASP,FALCON,PANTHER,NEBULA,HAWKEYE,BLACKWIDOW,STARLORD,MANTIS,SHURI,PEPPER,FURY,STARK,ROGERS,MARVEL,AVENGERS",
        ),
    ]

    outputs = [
        Output(display_name="Parsed Grid Data", name="parsed_grid", method="parse_grid"),
    ]

    def parse_grid(self) -> Data:
        raw = self.raw_grid_text
        lines = [line.strip() for line in raw.strip().split("\n") if line.strip()]
        grid = []
        for line in lines:
            if " " in line:
                row = [ch.upper() for ch in line.split() if ch.isalpha()]
            else:
                row = [ch.upper() for ch in line if ch.isalpha()]
            if row:
                grid.append(row)
        words = [w.strip().upper() for w in self.words_to_find.split(",") if w.strip()]
        return Data(data={
            "grid": grid,
            "rows": len(grid),
            "cols": len(grid[0]) if grid else 0,
            "words": words,
        })