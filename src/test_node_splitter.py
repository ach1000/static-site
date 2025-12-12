import unittest

from textnode import TextNode, TextType
from node_splitter import split_nodes_delimiter


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


if __name__ == "__main__":
    unittest.main()
