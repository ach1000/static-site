import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    markdown_to_blocks,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)
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


class TestExtractMarkdownElements(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_markdown_images(self):
        text = (
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) "
            "and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            matches,
        )

    def test_extract_markdown_links(self):
        text = (
            "This is text with a link [to boot dev](https://www.boot.dev) "
            "and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            matches,
        )

    def test_extract_links_does_not_match_images(self):
        text = (
            "A link [site](https://example.com) and an "
            "![img](https://example.com/cat.png)"
        )
        matches = extract_markdown_links(text)
        self.assertListEqual([("site", "https://example.com")], matches)

    def test_extract_returns_empty_when_no_matches(self):
        text = "No markdown link or image here"
        self.assertListEqual([], extract_markdown_images(text))
        self.assertListEqual([], extract_markdown_links(text))


class TestSplitNodesImageAndLink(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ],
            new_nodes,
        )

    def test_split_image_at_start_and_end(self):
        node = TextNode(
            "![first](https://example.com/1.png) middle ![last](https://example.com/2.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("first", TextType.IMAGE, "https://example.com/1.png"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("last", TextType.IMAGE, "https://example.com/2.png"),
            ],
            new_nodes,
        )

    def test_split_link_at_start_and_end(self):
        node = TextNode(
            "[first](https://example.com/1) middle [last](https://example.com/2)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("first", TextType.LINK, "https://example.com/1"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("last", TextType.LINK, "https://example.com/2"),
            ],
            new_nodes,
        )

    def test_split_images_non_text_nodes_unchanged(self):
        old_nodes = [
            TextNode("already code", TextType.CODE),
            TextNode("before ![img](https://example.com/a.png) after", TextType.TEXT),
        ]
        new_nodes = split_nodes_image(old_nodes)
        self.assertListEqual(
            [
                TextNode("already code", TextType.CODE),
                TextNode("before ", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://example.com/a.png"),
                TextNode(" after", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_links_non_text_nodes_unchanged(self):
        old_nodes = [
            TextNode("already bold", TextType.BOLD),
            TextNode("before [site](https://example.com) after", TextType.TEXT),
        ]
        new_nodes = split_nodes_link(old_nodes)
        self.assertListEqual(
            [
                TextNode("already bold", TextType.BOLD),
                TextNode("before ", TextType.TEXT),
                TextNode("site", TextType.LINK, "https://example.com"),
                TextNode(" after", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_images_no_match_returns_original(self):
        node = TextNode("no images here", TextType.TEXT)
        self.assertListEqual([node], split_nodes_image([node]))

    def test_split_links_no_match_returns_original(self):
        node = TextNode("no links here", TextType.TEXT)
        self.assertListEqual([node], split_nodes_link([node]))

    def test_split_links_ignores_images(self):
        node = TextNode(
            "one ![img](https://example.com/i.png) and [site](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("one ![img](https://example.com/i.png) and ", TextType.TEXT),
                TextNode("site", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_split_images_ignores_links(self):
        node = TextNode(
            "one [site](https://example.com) and ![img](https://example.com/i.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("one [site](https://example.com) and ", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://example.com/i.png"),
            ],
            new_nodes,
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes_full_example(self):
        text = (
            "This is **text** with an _italic_ word and a `code block` and an "
            "![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a "
            "[link](https://boot.dev)"
        )
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

    def test_text_to_textnodes_plain_text(self):
        text = "Just plain text"
        nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("Just plain text", TextType.TEXT)], nodes)

    def test_text_to_textnodes_unmatched_delimiter_raises(self):
        text = "This has **broken bold"
        with self.assertRaises(ValueError):
            text_to_textnodes(text)


class TestMarkdownToBlocks(unittest.TestCase):
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

    def test_markdown_to_blocks_strips_whitespace(self):
        md = "  # Heading  \n\n   Paragraph text   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["# Heading", "Paragraph text"])

    def test_markdown_to_blocks_removes_empty_blocks(self):
        md = "\n\n# Heading\n\n\n\nParagraph\n\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["# Heading", "Paragraph"])

    def test_markdown_to_blocks_empty_input(self):
        self.assertEqual(markdown_to_blocks("   \n\n   \n"), [])


if __name__ == "__main__":
    unittest.main()