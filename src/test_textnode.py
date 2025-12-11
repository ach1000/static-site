import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq_self(self):
        # a text noide should be equal to itself
        node = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node)

    def test_eq_identical(self):
        # text nodes with identical fields should not be equal
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq_text(self):
        # text nodes with different text fields should not be equal
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a different node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_type(self):
        # nodes with the same text but different types should not be equal
        node = TextNode("Same text", TextType.BOLD)
        node2 = TextNode("Same text", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_eq_url(self):
        # URL nodes with different urls should not be equal
        node = TextNode("Link text", TextType.LINK, url="https://example.com/a")
        node2 = TextNode("Link text", TextType.LINK, url="https://example.com/b")
        self.assertNotEqual(node, node2)

if __name__ == "__main__":
    unittest.main()
