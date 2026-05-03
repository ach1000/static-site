# Project Memory

> **Note:** This file should be updated whenever significant changes are made to the project, so that future agents and contributors have an accurate picture of the codebase.

## Project Overview

This is a static site generator written in Python. It parses Markdown text and outputs HTML. Development is ongoing; only inline text parsing has been implemented so far.

## Project Structure

```
static-site/
├── public/              # Output / served HTML and CSS
│   ├── index.html
│   └── styles.css
├── src/
│   ├── main.py          # Entry point; run via main.sh or `make run`
│   └── textnode.py      # Inline text representation (TextNode + TextType)
├── .gitignore           # Ignores __pycache__/
├── main.sh              # Runs `python3 src/main.py`
├── Makefile             # `make run` executes main.sh; test target to be added
└── PROJECT.md            # This file
```

## How to Run

```bash
./main.sh
# or
make run
```

## Core Concepts

### Inline vs Block Elements

Markdown content is split into two levels:

- **Inline** — text within a block (implemented in `textnode.py`)
- **Block** — headings, paragraphs, bullet lists (not yet implemented)

### TextType (enum) — `src/textnode.py`

Represents every supported inline text type:

| Member   | Value      | Markdown syntax              |
|----------|------------|------------------------------|
| TEXT     | `"text"`   | Plain text                   |
| BOLD     | `"bold"`   | `**bold**`                   |
| ITALIC   | `"italic"` | `_italic_`                   |
| CODE     | `"code"`   | `` `code` ``                 |
| LINK     | `"link"`   | `[anchor text](url)`         |
| IMAGE    | `"image"`  | `![alt text](url)`           |

### TextNode (class) — `src/textnode.py`

Intermediate representation of a piece of inline text.

**Constructor:** `TextNode(text, text_type, url=None)`

| Property    | Type       | Description                                      |
|-------------|------------|--------------------------------------------------|
| `text`      | `str`      | The text content of the node                     |
| `text_type` | `TextType` | The inline type (member of `TextType` enum)      |
| `url`       | `str|None` | URL for LINK or IMAGE nodes; `None` otherwise    |

**Methods:**
- `__eq__(other)` — returns `True` if `text`, `text_type`, and `url` are all equal (used by unit tests)
- `__repr__()` — returns `TextNode(TEXT, TEXT_TYPE_VALUE, URL)`

## Assumptions & Decisions

- `src/main.py` imports from `textnode` using a bare module name; Python must be invoked from within the `src/` directory, or the script must be run via `main.sh` / `make run` (both of which call `python3 src/main.py` from the project root, which adds `src/` to `sys.path` implicitly via the working directory).
- `__pycache__/` is git-ignored.
- Block-level elements (headings, paragraphs, lists) are deferred to a later implementation phase.
- A `test` target in the `Makefile` is planned but not yet implemented.
