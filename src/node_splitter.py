from enum import Enum
from textnode import TextNode, TextType, text_node_to_html_node
from markdown_extractor import extract_markdown_images, extract_markdown_links
from parentnode import ParentNode
from leafnode import LeafNode


class BlockType(Enum):
    """Enum for markdown block types."""
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


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


def text_to_textnodes(text):
    """
    Convert raw markdown text to a list of TextNode objects.
    
    Handles bold (**), italic (_), code (`), images (![alt](url)), and links ([text](url)).
    """
    # Start with a single TEXT node
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Apply splitting functions in order
    # Order: code, bold, italic (inline syntax), then images and links
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    
    return nodes


def markdown_to_blocks(markdown):
    """
    Split a raw markdown string into blocks separated by double newlines.
    
    Returns a list of block strings with leading/trailing whitespace removed
    and empty blocks filtered out.
    """
    # Split on double newlines
    blocks = markdown.split("\n\n")
    
    # Strip each block and filter out empty ones
    return [block.strip() for block in blocks if block.strip()]


def block_to_block_type(block):
    """
    Determine the type of a markdown block.
    
    Args:
        block: A single block of markdown text (whitespace already stripped)
    
    Returns:
        BlockType enum value representing the type of block
    """
    lines = block.split("\n")
    
    # Check for heading: 1-6 # followed by space
    if lines[0].startswith("#"):
        hashes = 0
        for char in lines[0]:
            if char == "#":
                hashes += 1
            else:
                break
        if 1 <= hashes <= 6 and (hashes < len(lines[0]) and lines[0][hashes] == " "):
            return BlockType.HEADING
    
    # Check for code block: starts and ends with 3 backticks
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    
    # Check for quote: every line starts with >
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    
    # Check for unordered list: every line starts with - followed by space
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list: every line starts with number. space, incrementing from 1
    is_ordered_list = True
    for i, line in enumerate(lines, 1):
        # Check if line starts with number
        if not line or not line[0].isdigit():
            is_ordered_list = False
            break
        # Extract the number
        num_str = ""
        for char in line:
            if char.isdigit():
                num_str += char
            else:
                break
        try:
            num = int(num_str)
            # Check if number matches expected sequence (1, 2, 3, ...)
            if num != i:
                is_ordered_list = False
                break
            # Check if followed by . and space
            if not (len(line) > len(num_str) and line[len(num_str)] == "." and line[len(num_str) + 1] == " "):
                is_ordered_list = False
                break
        except (ValueError, IndexError):
            is_ordered_list = False
            break
    
    if is_ordered_list:
        return BlockType.ORDERED_LIST
    
    # Default to paragraph
    return BlockType.PARAGRAPH


def text_to_children(text):
    """
    Convert inline markdown text to a list of HTMLNode children.
    
    Uses text_to_textnodes to parse inline markdown and text_node_to_html_node
    to convert each TextNode to an HTMLNode.
    """
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(node) for node in text_nodes]


def markdown_to_html_node(markdown):
    """
    Convert a full markdown document to a single parent HTMLNode.
    
    The parent node is a div containing all block-level HTMLNodes.
    """
    blocks = markdown_to_blocks(markdown)
    children = []
    
    for block in blocks:
        block_type = block_to_block_type(block)
        
        if block_type == BlockType.PARAGRAPH:
            # Paragraph: normalize newlines to spaces and parse inline markdown
            normalized_block = " ".join(block.split())
            children_nodes = text_to_children(normalized_block)
            children.append(ParentNode("p", children_nodes))
        
        elif block_type == BlockType.HEADING:
            # Heading: extract level and content
            level = 0
            for char in block:
                if char == "#":
                    level += 1
                else:
                    break
            # Content is after the hashes and space
            content = block[level + 1:]
            children_nodes = text_to_children(content)
            children.append(ParentNode(f"h{level}", children_nodes))
        
        elif block_type == BlockType.CODE:
            # Code block: don't parse inline markdown
            # Remove the triple backticks
            code_content = block[3:-3]
            # Strip leading newline if present
            if code_content.startswith("\n"):
                code_content = code_content[1:]
            children.append(ParentNode("pre", [ParentNode("code", [LeafNode(None, code_content)])]))
        
        elif block_type == BlockType.QUOTE:
            # Quote: process each line (remove > prefix) and parse inline markdown
            lines = block.split("\n")
            quote_lines = []
            for line in lines:
                # Remove leading > and space
                if line.startswith("> "):
                    quote_lines.append(line[2:])
                elif line.startswith(">"):
                    quote_lines.append(line[1:])
            quote_text = "\n".join(quote_lines)
            children_nodes = text_to_children(quote_text)
            children.append(ParentNode("blockquote", children_nodes))
        
        elif block_type == BlockType.UNORDERED_LIST:
            # Unordered list: process each line (remove - prefix) and parse inline markdown
            lines = block.split("\n")
            list_items = []
            for line in lines:
                # Remove leading "- "
                item_content = line[2:]
                children_nodes = text_to_children(item_content)
                list_items.append(ParentNode("li", children_nodes))
            children.append(ParentNode("ul", list_items))
        
        elif block_type == BlockType.ORDERED_LIST:
            # Ordered list: process each line (remove number. prefix) and parse inline markdown
            lines = block.split("\n")
            list_items = []
            for line in lines:
                # Find where the text starts (after "N. ")
                dot_idx = line.index(".")
                item_content = line[dot_idx + 2:]
                children_nodes = text_to_children(item_content)
                list_items.append(ParentNode("li", children_nodes))
            children.append(ParentNode("ol", list_items))
    
    return ParentNode("div", children)
