import unittest

from textnode import TextNode, TextType
from node_splitter import split_nodes_image, split_nodes_link


class TestSplitNodesImageLink(unittest.TestCase):
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
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
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
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_split_images_no_images(self):
        node = TextNode("This is text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links_no_links(self):
        node = TextNode("This is text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_images_non_text_nodes_passthrough(self):
        node = TextNode("bold", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links_non_text_nodes_passthrough(self):
        node = TextNode("link text", TextType.LINK, "https://example.com")
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_images_single(self):
        node = TextNode("![single](https://single.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [TextNode("single", TextType.IMAGE, "https://single.png")],
            new_nodes,
        )

    def test_split_links_single(self):
        node = TextNode("[link](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [TextNode("link", TextType.LINK, "https://example.com")],
            new_nodes,
        )

    def test_split_images_leading_text(self):
        node = TextNode("Start ![img](https://i.png) end", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "Start ")
        self.assertEqual(new_nodes[1].text, "img")
        self.assertEqual(new_nodes[2].text, " end")

    def test_split_links_leading_text(self):
        node = TextNode("Start [link](https://x.com) end", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "Start ")
        self.assertEqual(new_nodes[1].text, "link")
        self.assertEqual(new_nodes[2].text, " end")

    def test_split_images_multiple_nodes(self):
        nodes = [
            TextNode("First ![a](https://a.png)", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode("Second ![b](https://b.png)", TextType.TEXT),
        ]
        new_nodes = split_nodes_image(nodes)
        # Should split first and third, passthrough bold
        self.assertGreater(len(new_nodes), 3)

    def test_split_links_multiple_nodes(self):
        nodes = [
            TextNode("First [a](https://a.com)", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode("Second [b](https://b.com)", TextType.TEXT),
        ]
        new_nodes = split_nodes_link(nodes)
        self.assertGreater(len(new_nodes), 3)


if __name__ == "__main__":
    unittest.main()
