# User–System Interaction Document

## Word Search Puzzle Solver — DataStax Langflow

---

## 1. Overview

This document describes how users (staff) interact with the Word Search Solver system built on DataStax Langflow. The system accepts an image of a word search puzzle, extracts the letter grid using AI vision, solves it algorithmically, and returns highlighted results.

---

## 2. Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| **User (Staff)** | Uploads word search puzzle image | Provides input via Langflow Playground chat |
| **System (Langflow Flow)** | Processes image, solves puzzle | Returns found words with positions and directions |

---

## 3. Interaction Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: User opens Langflow Playground                        │
│          └── Clicks on the flow "Word Search Solver"           │
│                                                                 │
│  Step 2: User uploads puzzle image                             │
│          └── Supported formats: JPG, PNG, JPEG                 │
│          └── Image should clearly show the letter grid         │
│                                                                 │
│  Step 3: System processes the image                            │
│          ├── Agent (Gemini Vision) extracts letter grid (OCR)  │
│          ├── Grid Parser structures the raw text into 2D array │
│          └── Word Search Solver finds all target words         │
│                                                                 │
│  Step 4: System returns results                                │
│          ├── Grid displayed as HTML table                      │
│          ├── Found words highlighted with unique colors        │
│          ├── Legend showing found words with directions        │
│          └── List of words not found (if any)                  │
│                                                                 │
│  Step 5: User reviews output                                  │
│          └── Can re-upload different image for new puzzle      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Input Specification

### Image Requirements
| Parameter | Requirement |
|-----------|-------------|
| **Format** | JPG, PNG, JPEG |
| **Content** | Clear photo/scan of a word search grid |
| **Grid visibility** | Letters must be legible; avoid obstructions |
| **Orientation** | Upright preferred for best OCR accuracy |

### Words to Find
Pre-configured in the Grid Parser component. Default list (Marvel Avengers theme):
> IRONMAN, THOR, HULK, SPIDERMAN, THANOS, VISION, WANDA, LOKI, GROOT, ROCKET, GAMORA, DRAX, ANTMAN, WASP, FALCON, PANTHER, NEBULA, HAWKEYE, BLACKWIDOW, STARLORD, MANTIS, SHURI, PEPPER, FURY, STARK, ROGERS, MARVEL, AVENGERS

Users can modify this list in the Grid Parser component's "Words to Find" field.

---

## 5. Output Specification

### Successful Response
The system returns a formatted message containing:

1. **Header**: "Word Search Solution" with count of found words
2. **Word Labels**: Color-coded badges for each found word
3. **Grid Table**: Letter grid with highlighted cells for found words
4. **Not Found List**: Words that could not be located in the grid

### Error Scenarios

| Error | Cause | User Action |
|-------|-------|-------------|
| Image not readable | Poor quality / blurry image | Re-upload a clearer image |
| Empty grid | OCR failed to extract letters | Crop image to show only the grid |
| API quota exceeded | Free tier limit reached | Wait for quota reset or switch API key |
| Partial results | Grid partially obscured | Crop obstructions (decorations, images) |

---

## 6. Sample Interaction

### User Input
> *Uploads image: `ThanosBlinkit.jpeg` — a Marvel Avengers word search puzzle*

### System Output
```
Word Search Solution
Found 6 of 28 words

[THOR ↓] [HULK ↘] [SPIDERMAN ↓] [PANTHER ↘] [HAWKEYE ↓] [BLACKWIDOW ↘]

K  J  C  Q  U  G  M  S  C  T  T  H  B  G  K  S  L  E  B  P
C  T  N  D  V  I  E  S  R  F  S  T  U  Y  L  J  G  I  O  M
...
(grid with highlighted cells)

Not found: IRONMAN, THANOS, VISION, WANDA, LOKI, GROOT, ...
```

---

## 7. System Boundaries

- The system processes **one image per request**
- OCR accuracy depends on image clarity and the vision model used
- The word list is configurable but must be set before running the flow
- The system does **not** store results — each run is independent
