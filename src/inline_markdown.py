import re

from textnode import TextNode, TextType


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