def extract_title(markdown):
    """Extract the h1 title from markdown content.
    
    Looks for a line starting with a single # and returns the text after it,
    stripped of whitespace.
    
    Args:
        markdown: A string containing markdown content.
        
    Returns:
        The title text without the # and whitespace.
        
    Raises:
        ValueError: If no h1 header is found in the markdown.
    """
    lines = markdown.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            # Found h1 header, extract the text after the #
            return stripped[2:].strip()
    
    raise ValueError("No h1 header found in markdown")
