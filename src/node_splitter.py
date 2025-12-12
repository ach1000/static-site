from textnode import TextNode, TextType
from markdown_extractor import extract_markdown_images, extract_markdown_links


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Split TextType.TEXT nodes in `old_nodes` by `delimiter` and convert
    the delimited segments into nodes of `text_type`.

    - Non-Text nodes are copied through unchanged.
    - If a node has an odd number of delimiters, raises ValueError.
    - Empty text segments are skipped (no zero-length TextNode for text).
    """
    if delimiter == "":
        raise ValueError("delimiter must not be empty")

    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode):
            new_nodes.append(node)
            continue

        # Only attempt to split plain/text nodes
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        count = text.count(delimiter)
        if count == 0:
            new_nodes.append(node)
            continue
        if count % 2 != 0:
            raise ValueError(f"Unmatched delimiter '{delimiter}' in text: {text!r}")

        parts = text.split(delimiter)
        # parts alternates: text, matched, text, matched, ...
        for idx, part in enumerate(parts):
            if idx % 2 == 0:
                # plain text segment
                if part != "":
                    new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                # delimited segment -> new node with the requested type
                new_nodes.append(TextNode(part, text_type))

    return new_nodes


def split_nodes_image(old_nodes):
    """Split markdown image syntax ![alt](url) into Image TextNodes."""
    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode):
            new_nodes.append(node)
            continue
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        images = extract_markdown_images(text)
        
        if not images:
            new_nodes.append(node)
            continue
        
        remaining_text = text
        for alt, url in images:
            # Find the image markdown syntax
            image_md = f"![{alt}]({url})"
            # Split on this image, max 1 split
            parts = remaining_text.split(image_md, 1)
            
            # Add text before image
            if parts[0] != "":
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            
            # Add the image node
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))
            
            # Update remaining text
            remaining_text = parts[1] if len(parts) > 1 else ""
        
        # Add any remaining text
        if remaining_text != "":
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))

    return new_nodes


def split_nodes_link(old_nodes):
    """Split markdown link syntax [text](url) into Link TextNodes."""
    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode):
            new_nodes.append(node)
            continue
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        links = extract_markdown_links(text)
        
        if not links:
            new_nodes.append(node)
            continue
        
        remaining_text = text
        for anchor, url in links:
            # Find the link markdown syntax
            link_md = f"[{anchor}]({url})"
            # Split on this link, max 1 split
            parts = remaining_text.split(link_md, 1)
            
            # Add text before link
            if parts[0] != "":
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            
            # Add the link node
            new_nodes.append(TextNode(anchor, TextType.LINK, url))
            
            # Update remaining text
            remaining_text = parts[1] if len(parts) > 1 else ""
        
        # Add any remaining text
        if remaining_text != "":
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))

    return new_nodes
