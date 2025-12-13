import unittest

from textnode import TextNode, TextType
from node_splitter import split_nodes_delimiter, markdown_to_blocks, block_to_block_type, BlockType


class TestNodeSplitter(unittest.TestCase):
    def test_split_backtick_single(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        texts = [n.text for n in new_nodes]
        types = [n.text_type for n in new_nodes]
        self.assertEqual(texts, ["This is text with a ", "code block", " word"])
        self.assertEqual(types, [TextType.TEXT, TextType.CODE, TextType.TEXT])

    def test_split_multiple(self):
        node = TextNode("a `b` c `d` e", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        texts = [n.text for n in new_nodes]
        types = [n.text_type for n in new_nodes]
        self.assertEqual(texts, ["a ", "b", " c ", "d", " e"])
        self.assertEqual(types, [TextType.TEXT, TextType.CODE, TextType.TEXT, TextType.CODE, TextType.TEXT])

    def test_unmatched_raises(self):
        node = TextNode("Unmatched `code here", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_non_text_pass_through(self):
        node = TextNode("bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [node])

    def test_bold_delimiter_double_star(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual([n.text for n in new_nodes], ["This is ", "bold", " text"])        

    def test_underscore_italic(self):
        node = TextNode("This _is_ italic", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual([n.text for n in new_nodes], ["This ", "is", " italic"])        

    def test_multiple_input_nodes(self):
        nodes = [
            TextNode("First `a` end", TextType.TEXT),
            TextNode("No delimiter here", TextType.TEXT),
            TextNode("**B**", TextType.TEXT),
        ]
        # first, split backticks
        nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        # then, split bold markers
        nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        texts = [n.text for n in nodes]
        types = [n.text_type for n in nodes]
        self.assertIn("a", texts)
        self.assertIn("B", texts)

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_empty_document(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_single_newline(self):
        md = "\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_complex(self):
        md = """# Heading 1

This is a paragraph with **bold** and _italic_.

## Heading 2

Another paragraph here.

```
code block
with multiple lines
```

Final paragraph with a [link](https://example.com).
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# Heading 1",
                "This is a paragraph with **bold** and _italic_.",
                "## Heading 2",
                "Another paragraph here.",
                "```\ncode block\nwith multiple lines\n```",
                "Final paragraph with a [link](https://example.com).",
            ],
        )

    def test_block_to_block_type_paragraph(self):
        block = "This is a normal paragraph with some text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_heading_h1(self):
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_block_to_block_type_heading_h6(self):
        block = "###### This is an h6 heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_block_to_block_type_heading_no_space(self):
        # Should be paragraph if no space after hashes
        block = "###No space here"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_heading_too_many_hashes(self):
        # Should be paragraph if more than 6 hashes
        block = "####### Too many hashes"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_code_block(self):
        block = "```\nprint('hello')\nprint('world')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_block_to_block_type_code_block_single_line(self):
        block = "```code```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_block_to_block_type_code_block_unclosed(self):
        # Should be paragraph if not closed with 3 backticks
        block = "```\ncode here"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote_single_line(self):
        block = "> This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_quote_multiple_lines(self):
        block = "> This is a quote\n> with multiple lines\n> of text"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_quote_partial(self):
        # Should be paragraph if not all lines start with >
        block = "> This is a quote\nBut this is not"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_unordered_list_single(self):
        block = "- Item one"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_unordered_list_multiple(self):
        block = "- Item one\n- Item two\n- Item three"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_unordered_list_no_space(self):
        # Should be paragraph if no space after dash
        block = "-Item with no space"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_unordered_list_partial(self):
        # Should be paragraph if not all lines start with "- "
        block = "- Item one\n- Item two\nItem three"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_single(self):
        block = "1. First item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ordered_list_multiple(self):
        block = "1. First item\n2. Second item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ordered_list_wrong_sequence(self):
        # Should be paragraph if numbers don't increment correctly
        block = "1. First\n3. Third"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_no_dot(self):
        # Should be paragraph if missing dot
        block = "1 First item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_no_space(self):
        # Should be paragraph if no space after dot
        block = "1.First item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_starts_at_zero(self):
        # Should be paragraph if doesn't start at 1
        block = "0. Zero\n1. One"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


if __name__ == "__main__":
    unittest.main()
