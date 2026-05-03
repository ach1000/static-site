import re
from enum import Enum

from textnode import TextNode, TextType


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        split_text = old_node.text.split(delimiter)
        if len(split_text) == 1:
            new_nodes.append(old_node)
            continue

        if len(split_text) % 2 == 0:
            raise ValueError(
                f"Invalid markdown syntax: missing closing delimiter '{delimiter}' in '{old_node.text}'"
            )

        for i, text_part in enumerate(split_text):
            if text_part == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(text_part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(text_part, text_type))

    return new_nodes


def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def split_nodes_image(old_nodes):
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        text_to_parse = old_node.text
        image_matches = extract_markdown_images(text_to_parse)
        if len(image_matches) == 0:
            new_nodes.append(old_node)
            continue

        for alt_text, url in image_matches:
            markdown_image = f"![{alt_text}]({url})"
            split_sections = text_to_parse.split(markdown_image, 1)
            if len(split_sections) != 2:
                raise ValueError(f"Invalid markdown image syntax in '{old_node.text}'")

            if split_sections[0] != "":
                new_nodes.append(TextNode(split_sections[0], TextType.TEXT))
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            text_to_parse = split_sections[1]

        if text_to_parse != "":
            new_nodes.append(TextNode(text_to_parse, TextType.TEXT))

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        text_to_parse = old_node.text
        link_matches = extract_markdown_links(text_to_parse)
        if len(link_matches) == 0:
            new_nodes.append(old_node)
            continue

        for anchor_text, url in link_matches:
            markdown_link = f"[{anchor_text}]({url})"
            split_sections = text_to_parse.split(markdown_link, 1)
            if len(split_sections) != 2:
                raise ValueError(f"Invalid markdown link syntax in '{old_node.text}'")

            if split_sections[0] != "":
                new_nodes.append(TextNode(split_sections[0], TextType.TEXT))
            new_nodes.append(TextNode(anchor_text, TextType.LINK, url))
            text_to_parse = split_sections[1]

        if text_to_parse != "":
            new_nodes.append(TextNode(text_to_parse, TextType.TEXT))

    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    return nodes


def markdown_to_blocks(markdown):
    raw_blocks = markdown.split("\n\n")
    blocks = []

    for block in raw_blocks:
        stripped = block.strip()
        if stripped != "":
            blocks.append(stripped)

    return blocks


def block_to_block_type(block):
    if re.fullmatch(r"#{1,6} .+", block):
        return BlockType.HEADING

    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    lines = block.split("\n")

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    is_ordered_list = True
    for i, line in enumerate(lines, start=1):
        if not line.startswith(f"{i}. "):
            is_ordered_list = False
            break
    if is_ordered_list:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH