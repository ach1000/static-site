import unittest

from textnode import TextNode, TextType
from node_splitter import text_to_textnodes


class TestTextToTextnodes(unittest.TestCase):
    def test_markdown_example(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_plain_text(self):
        text = "This is plain text"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("This is plain text", TextType.TEXT)], nodes)

    def test_bold_only(self):
        text = "**bold**"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("bold", TextType.BOLD)], nodes)

    def test_italic_only(self):
        text = "_italic_"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("italic", TextType.ITALIC)], nodes)

    def test_code_only(self):
        text = "`code`"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("code", TextType.CODE)], nodes)

    def test_image_only(self):
        text = "![alt](https://i.example.com/img.png)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("alt", TextType.IMAGE, "https://i.example.com/img.png")],
            nodes,
        )

    def test_link_only(self):
        text = "[link text](https://example.com)"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("link text", TextType.LINK, "https://example.com")], nodes)

    def test_mixed_bold_and_italic(self):
        text = "**bold** and _italic_"
        nodes = text_to_textnodes(text)
        texts = [n.text for n in nodes]
        types = [n.text_type for n in nodes]
        self.assertIn("bold", texts)
        self.assertIn("italic", texts)
        self.assertEqual(types.count(TextType.BOLD), 1)
        self.assertEqual(types.count(TextType.ITALIC), 1)

    def test_code_with_special_chars(self):
        text = "Use `code_with_underscores` here"
        nodes = text_to_textnodes(text)
        code_nodes = [n for n in nodes if n.text_type == TextType.CODE]
        self.assertEqual(len(code_nodes), 1)
        self.assertEqual(code_nodes[0].text, "code_with_underscores")

    def test_multiple_bold_sections(self):
        text = "**first** and **second**"
        nodes = text_to_textnodes(text)
        bold_nodes = [n for n in nodes if n.text_type == TextType.BOLD]
        self.assertEqual(len(bold_nodes), 2)
        self.assertEqual(bold_nodes[0].text, "first")
        self.assertEqual(bold_nodes[1].text, "second")

    def test_multiple_links(self):
        text = "[link1](https://a.com) and [link2](https://b.com)"
        nodes = text_to_textnodes(text)
        link_nodes = [n for n in nodes if n.text_type == TextType.LINK]
        self.assertEqual(len(link_nodes), 2)
        self.assertEqual(link_nodes[0].text, "link1")
        self.assertEqual(link_nodes[1].text, "link2")

    def test_nested_markdown_syntax(self):
        # Bold containing underscores (but not italic)
        text = "**bold_text**"
        nodes = text_to_textnodes(text)
        # Should be one bold node
        bold_nodes = [n for n in nodes if n.text_type == TextType.BOLD]
        self.assertEqual(len(bold_nodes), 1)

    def test_empty_text(self):
        text = ""
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("", TextType.TEXT)], nodes)


if __name__ == "__main__":
    unittest.main()
