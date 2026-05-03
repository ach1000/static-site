# Project Memory

> **Note:** This file should be updated whenever significant changes are made to the project, so that future agents and contributors have an accurate picture of the codebase.

## Project Overview

This is a static site generator written in Python. It parses Markdown text and outputs HTML.

## Project Structure

```
static-site/
├── src/
│   ├── main.py              # Entry point; run via main.sh or `make run`
│   ├── textnode.py          # Inline text representation (TextNode + TextType)
│   ├── htmlnode.py          # HTML node representation (HTMLNode, LeafNode, ParentNode)
│   ├── converters.py        # text_node_to_html_node() conversion function
│   ├── inline_markdown.py   # split_nodes_delimiter() for inline markdown parsing
│   ├── test_textnode.py     # Unit tests for TextNode
│   ├── test_htmlnode.py     # Unit tests for HTMLNode / LeafNode / ParentNode
│   ├── test_converters.py   # Unit tests for text_node_to_html_node
│   ├── test_inline_markdown.py # Unit tests for split_nodes_delimiter
│   └── test_main.py         # Unit tests for extract_title and generate_page
├── .gitignore               # Ignores __pycache__/
├── main.sh                  # Runs `python3 src/main.py`
├── test.sh                  # Runs `python3 -m unittest discover -s src`
├── Makefile                 # `make run` / `make test` / `make clean`
├── template.html            # Page template containing {{ Title }} and {{ Content }}
├── content/
│   ├── index.md             # Markdown source for main page
│   ├── blog/
│   │   ├── glorfindel/index.md
│   │   ├── tom/index.md
│   │   └── majesty/index.md
│   └── contact/
│       └── index.md
└── MEMORY.md                # This file
```

## How to Run

```bash
./main.sh   # or: make run
./test.sh   # or: make test
make clean  # removes generated site output and Python __pycache__ folders
```

`main.sh` now changes into the repository root before running `python3 src/main.py`, so it can be invoked from outside the project root.

## Unit Tests — `src/test_textnode.py`

Tests use Python's built-in `unittest` module. Discovered automatically via:

```bash
python3 -m unittest discover -s src
```

Tests are methods on `TestTextNode(unittest.TestCase)`. Current coverage:

| Test | What it checks |
|------|---------------|
| `test_eq` | Two identical nodes (no URL) are equal |
| `test_eq_with_url` | Two identical LINK nodes with the same URL are equal |
| `test_not_eq_different_text` | Different `text` → not equal |
| `test_not_eq_different_text_type` | Different `text_type` → not equal |
| `test_not_eq_different_url` | Different `url` → not equal |
| `test_url_defaults_to_none` | Omitting `url` sets it to `None` |
| `test_eq_url_none_vs_none` | Explicit `None` and omitted `url` are equivalent |
| `test_repr` | `__repr__` output matches expected format |

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
- The pipeline so far is: Markdown text → `TextNode` (intermediate repr) → `LeafNode` (HTML repr) → rendered HTML string.
- As of the end of this session, `make test` runs 87 tests, all passing.

## HTMLNode — `src/htmlnode.py`
Represents a node in an HTML document tree. All constructor arguments are optional (default `None`):

| Property   | Type              | Description                                      |
|------------|-------------------|--------------------------------------------------|
| `tag`      | `str|None`        | HTML tag name, e.g. `"p"`, `"a"`, `"h1"`        |
| `value`    | `str|None`        | Text content of the tag                          |
| `children` | `list[HTMLNode]|None` | Child nodes                                 |
| `props`    | `dict|None`       | HTML attributes, e.g. `{"href": "https://..."}` |

**Methods:**
- `to_html()` — raises `NotImplementedError`; child classes must override
- `props_to_html()` — returns attributes as a string with leading spaces, e.g. ` href="..." target="_blank"`; returns `""` if `props` is `None` or empty
- `__repr__()` — returns `HTMLNode(tag, value, children, props)`

`HTMLNode` is a base class. Concrete subclasses will override `to_html()` to render HTML.

## LeafNode — `src/htmlnode.py`

A subclass of `HTMLNode` representing an HTML tag with no children (a leaf in the tree).

**Constructor:** `LeafNode(tag, value, props=None)`
- `tag` and `value` are required positional arguments (though `tag` may be `None`)
- `children` is always `None` (not accepted)

**`to_html()` behaviour:**
- Raises `ValueError` if `value` is `None`
- Returns raw text if `tag` is `None`
- Otherwise returns `<tag props>value</tag>`, e.g. `<a href="...">Click me!</a>`

**`__repr__()`** returns `LeafNode(tag, value, props)` (no children field).

## ParentNode — `src/htmlnode.py`

A subclass of `HTMLNode` representing an HTML tag that contains child nodes.

**Constructor:** `ParentNode(tag, children, props=None)`
- `tag` and `children` are required positional arguments
- `value` is always `None` (not accepted)
- `children` must be a non-empty list of `HTMLNode` instances

**`to_html()` behaviour:**
- Raises `ValueError` if `tag` is `None`
- Raises `ValueError` if `children` is missing or empty
- Recursively calls `to_html()` on each child, concatenating results between the opening and closing tags
- e.g. `<p><b>Bold</b>Normal text</p>`

**`__repr__()`** returns `ParentNode(tag, children, props)`.

## text_node_to_html_node — `src/converters.py`

Converts a `TextNode` to a `LeafNode`. Raises `ValueError` for unknown `TextType` values.

| TextType  | LeafNode tag | value        | props                          |
|-----------|-------------|--------------|--------------------------------|
| TEXT      | `None`      | `text`       | —                              |
| BOLD      | `"b"`       | `text`       | —                              |
| ITALIC    | `"i"`       | `text`       | —                              |
| CODE      | `"code"`    | `text`       | —                              |
| LINK      | `"a"`       | `text`       | `{"href": url}`                |
| IMAGE     | `"img"`     | `""`         | `{"src": url, "alt": text}`    |

Note: `LeafNode` renders images as `<img src="..." alt="..."></img>` (not self-closing) since `to_html()` always wraps value in open/close tags.

Also in `src/converters.py`:
- `text_to_children(text)` converts inline markdown text into a list of child HTML nodes by using `text_to_textnodes` then `text_node_to_html_node`.
- `markdown_to_html_node(markdown)` renders a full markdown document to a single `ParentNode("div", ...)`, mapping block types to HTML tags:
	- paragraph -> `p`
	- heading -> `h1`-`h6`
	- code -> `pre > code` (no inline parsing inside code)
	- quote -> `blockquote`
	- unordered list -> `ul > li`
	- ordered list -> `ol > li`

## Static Asset Copying — `src/main.py`

- `copy_static_to_public()` builds repo-root-relative paths, verifies required assets exist (`static/index.css` and `static/images/tolkien.png`), deletes `public/` if it exists, and recursively copies all static files/directories.
- `copy_dir_recursive(src, dst)` handles nested directory traversal and logs each copied file path.
- `public/` is git-ignored as generated output.
- Current static image set includes `tolkien.png`, `glorfindel.png`, `tom.png`, and `rivendell.png` in `static/images/`.

Also in `src/main.py`:
- `extract_title(markdown)` returns the first h1 (`# `) title text and raises `ValueError` if none exists.
- `generate_page(from_path, template_path, dest_path)` converts markdown to HTML using `markdown_to_html_node`, injects values into `template.html` placeholders, and writes output HTML, creating destination directories as needed.
- `main()` now copies static assets and generates `public/index.html` from `content/index.md` and `template.html`.

Note: Additional markdown pages under `content/blog/*/index.md` and `content/contact/index.md` are present, but current `main()` only generates the home page (`public/index.html`).

`main.sh` now runs the generator and then starts a local server with `cd public && python3 -m http.server 8888`.

## split_nodes_delimiter — `src/inline_markdown.py`

`split_nodes_delimiter(old_nodes, delimiter, text_type)` transforms a list of `TextNode`s by splitting only `TextType.TEXT` nodes on an inline markdown delimiter.

Behavior:
- Non-`TEXT` nodes are passed through unchanged.
- `TEXT` nodes without the delimiter are passed through unchanged.
- Delimited segments alternate between plain `TextType.TEXT` and the provided `text_type`.
- Raises `ValueError` if a closing delimiter is missing (invalid markdown syntax).

This is the shared parser primitive for inline code, bold, and italic handling by varying only `delimiter` and `text_type`.

Also in `src/inline_markdown.py`:
- `extract_markdown_images(text)` uses regex to return image tuples as `(alt_text, url)` for markdown image syntax `![alt](url)`.
- `extract_markdown_links(text)` uses regex to return link tuples as `(anchor_text, url)` for markdown link syntax `[text](url)` and excludes image syntax.
- `split_nodes_image(old_nodes)` splits only `TextType.TEXT` nodes into a sequence of `TextType.TEXT` and `TextType.IMAGE` nodes.
- `split_nodes_link(old_nodes)` splits only `TextType.TEXT` nodes into a sequence of `TextType.TEXT` and `TextType.LINK` nodes.
- `text_to_textnodes(text)` converts raw inline markdown text into `TextNode` objects by chaining the splitters in order: images, links, code, bold, italic.
- `markdown_to_blocks(markdown)` splits a full markdown document into block strings by double newlines, strips each block, and removes empty blocks.
- `BlockType` enum classifies block markdown into paragraph, heading, code, quote, unordered_list, and ordered_list.
- `block_to_block_type(block)` detects the block type using markdown syntax rules (heading markers, fenced code, quote/list line prefixes, and ordered list sequence validation).
