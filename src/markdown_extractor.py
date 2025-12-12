import re


def extract_markdown_images(text):
    """Return list of (alt, url) tuples for markdown images in text.
    Matches patterns like: ![alt text](url)
    """
    if text is None:
        return []
    pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    return [(m.group(1), m.group(2)) for m in pattern.finditer(text)]


def extract_markdown_links(text):
    """Return list of (anchor, url) tuples for markdown links in text.
    Matches patterns like: [anchor](url) but ignores images (which start with '!').
    """
    if text is None:
        return []
    # Use negative lookbehind to avoid matching images
    pattern = re.compile(r'(?<!\!)\[([^\]]+)\]\(([^)]+)\)')
    return [(m.group(1), m.group(2)) for m in pattern.finditer(text)]
