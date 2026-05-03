import re

from htmlnode import ParentNode
from inline_markdown import BlockType, block_to_block_type, markdown_to_blocks, text_to_textnodes
from textnode import TextNode, TextType
from htmlnode import LeafNode


def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
        case _:
            raise ValueError(f"Unknown TextType: {text_node.text_type}")


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(node) for node in text_nodes]


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.PARAGRAPH:
            paragraph_text = " ".join(block.split("\n"))
            children.append(ParentNode("p", text_to_children(paragraph_text)))
            continue

        if block_type == BlockType.HEADING:
            heading_level = len(block) - len(block.lstrip("#"))
            heading_text = block[heading_level + 1 :]
            children.append(ParentNode(f"h{heading_level}", text_to_children(heading_text)))
            continue

        if block_type == BlockType.CODE:
            code_text = block[4:-3]
            code_node = text_node_to_html_node(TextNode(code_text, TextType.CODE))
            children.append(ParentNode("pre", [code_node]))
            continue

        if block_type == BlockType.QUOTE:
            quote_lines = []
            for line in block.split("\n"):
                line_content = line[1:]
                if line_content.startswith(" "):
                    line_content = line_content[1:]
                quote_lines.append(line_content)
            children.append(ParentNode("blockquote", text_to_children(" ".join(quote_lines))))
            continue

        if block_type == BlockType.UNORDERED_LIST:
            list_items = []
            for line in block.split("\n"):
                list_items.append(ParentNode("li", text_to_children(line[2:])))
            children.append(ParentNode("ul", list_items))
            continue

        if block_type == BlockType.ORDERED_LIST:
            list_items = []
            for line in block.split("\n"):
                line_text = re.sub(r"^\d+\. ", "", line)
                list_items.append(ParentNode("li", text_to_children(line_text)))
            children.append(ParentNode("ol", list_items))
            continue

    return ParentNode("div", children)
