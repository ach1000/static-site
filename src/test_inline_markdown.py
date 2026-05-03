import unittest

from inline_markdown import split_nodes_delimiter
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_code_delimiter(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_split_bold_delimiter(self):
        node = TextNode("This is text with a **bolded phrase** in the middle", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bolded phrase", TextType.BOLD),
            TextNode(" in the middle", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_split_italic_delimiter(self):
        node = TextNode("This has _italic_ text", TextType.TEXT)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_non_text_nodes_are_unchanged(self):
        old_nodes = [
            TextNode("already bold", TextType.BOLD),
            TextNode(" and plain `code`", TextType.TEXT),
        ]
        result = split_nodes_delimiter(old_nodes, "`", TextType.CODE)
        expected = [
            TextNode("already bold", TextType.BOLD),
            TextNode(" and plain ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(result, expected)

    def test_no_delimiter_returns_original_text_node(self):
        node = TextNode("plain text only", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [node])

    def test_unmatched_delimiter_raises(self):
        node = TextNode("This has `unclosed code", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_multiple_formatted_sections_in_single_node(self):
        node = TextNode("One `two` three `four` five", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("One ", TextType.TEXT),
            TextNode("two", TextType.CODE),
            TextNode(" three ", TextType.TEXT),
            TextNode("four", TextType.CODE),
            TextNode(" five", TextType.TEXT),
        ]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()