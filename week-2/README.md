# Word Search Puzzle Solver

**Week 2 Project** — Agentic AI with DataStax Langflow

A multi-agent system that reads a word search puzzle from an image, extracts the letter grid using AI vision, solves it algorithmically, and returns color-highlighted results.

## Problem Statement

Given a word search puzzle image, build an agentic system that:
1. Reads the letter grid from the image using AI vision (OCR)
2. Searches for all target words across 8 directions
3. Returns solved results with highlighted positions

## Architecture

```
Chat Input (Image)
  -> OCR Agent (Gemini Vision) — Extracts letter grid from image
  -> Grid Parser (Custom) — Structures text into 2D array
  -> Word Search Solver (Custom) — Finds words in all 8 directions
  -> Chat Output — Returns solved grid with highlights
```

## Project Files

| File | Description |
|------|-------------|
| `grid_parser.py` | Custom component — parses OCR text into structured grid |
| `word_search_solver.py` | Custom component — word search in 8 directions |
| `agent_prompt.txt` | System prompt for Gemini Vision OCR agent |
| `Interaction.md` | User-System interaction document |
| `AgentSpec.md` | Agent specification document |

## Setup

### Prerequisites
- DataStax Langflow account
- Google Gemini API key

### Step 1: Create the Flow

Add these components in Langflow and connect them in order:

| # | Component | Type | Configuration |
|---|-----------|------|---------------|
| 1 | Chat Input | Built-in | Default |
| 2 | Agent | Built-in | Provider: Google Generative AI, Model: `gemini-2.0-flash-001` |
| 3 | Grid Parser | Custom | Paste code from `grid_parser.py` |
| 4 | Word Search Solver | Custom | Paste code from `word_search_solver.py` |
| 5 | Chat Output | Built-in | Default |

### Step 2: Configure the Agent
- Set Agent Instructions to the content of `agent_prompt.txt`
- Add your Google API Key

### Step 3: Add Custom Components
- Use Langflow's Custom Component node for Grid Parser and Word Search Solver
- Open the code editor and paste the respective Python code

### Step 4: Wire the Flow
```
Chat Input -> Agent (Response) -> Grid Parser (Raw Grid Text)
Grid Parser (Parsed Grid Data) -> Word Search Solver (Grid Data)
Word Search Solver (Search Results) -> Chat Output
```

### Step 5: Run
- Open the Playground
- Upload a word search puzzle image
- View the solved results

## How It Works

**OCR (Gemini Vision):** The Agent uses Gemini 2.0 Flash to read the image and extract the letter grid as plain text.

**Grid Parsing:** The Grid Parser splits OCR output into rows, extracts letters, and creates a 2D array along with the target word list.

**Word Search Algorithm:** The solver scans every cell in all 8 directions (horizontal, vertical, diagonal, and reverses). Each found word gets a unique color. Positions, directions, and unfound words are reported.

## Target Words

Default list (Marvel Avengers theme, 28 words):

IRONMAN, THOR, HULK, SPIDERMAN, THANOS, VISION, WANDA, LOKI, GROOT, ROCKET, GAMORA, DRAX, ANTMAN, WASP, FALCON, PANTHER, NEBULA, HAWKEYE, BLACKWIDOW, STARLORD, MANTIS, SHURI, PEPPER, FURY, STARK, ROGERS, MARVEL, AVENGERS

Modify the list in the Grid Parser component's "Words to Find" field.

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| DataStax Langflow | Agent orchestration and flow builder |
| Google Gemini 2.0 Flash | Vision/OCR |
| Python | Custom components for parsing and solving |

## Documentation

- [Interaction.md](./Interaction.md) — User-System interaction flow
- [AgentSpec.md](./AgentSpec.md) — Agent specifications and architecture

## Notes

- Custom components are used for solving instead of LLMs because LLMs hallucinate grid positions. The deterministic algorithm guarantees accuracy.
- Crop the image to show only the grid for best OCR results. Decorative elements can confuse the vision model.
- Gemini free tier allows 15 requests/minute. If quota is exceeded, wait or use a different API key.
