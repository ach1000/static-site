import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_single(self):
        node = HTMLNode("a", "click", props={"href": "https://example.com"})
        self.assertEqual(node.props_to_html(), ' href="https://example.com"')

    def test_props_to_html_multiple(self):
        node = HTMLNode("a", "click", props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')

    def test_props_to_html_none(self):
        node = HTMLNode("p", "hello")
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_empty_dict(self):
        node = HTMLNode("p", "hello", props={})
        self.assertEqual(node.props_to_html(), "")

    def test_to_html_raises(self):
        node = HTMLNode("p", "text")
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_repr(self):
        node = HTMLNode("p", "hello", None, {"class": "main"})
        self.assertEqual(repr(node), "HTMLNode(p, hello, None, {'class': 'main'})")

    def test_defaults_all_none(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_to_html_b(self):
        node = LeafNode("b", "Bold text")
        self.assertEqual(node.to_html(), "<b>Bold text</b>")

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Raw text")
        self.assertEqual(node.to_html(), "Raw text")

    def test_leaf_no_value_raises(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_no_children(self):
        node = LeafNode("span", "text")
        self.assertIsNone(node.children)

    def test_leaf_repr(self):
        node = LeafNode("a", "click", {"href": "https://example.com"})
        self.assertEqual(repr(node), "LeafNode(a, click, {'href': 'https://example.com'})")


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span><b>grandchild</b></span></div>")

    def test_to_html_multiple_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(node.to_html(), "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>")

    def test_to_html_with_props(self):
        node = ParentNode("div", [LeafNode("p", "text")], {"class": "container"})
        self.assertEqual(node.to_html(), '<div class="container"><p>text</p></div>')

    def test_no_tag_raises(self):
        node = ParentNode(None, [LeafNode("p", "text")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_no_children_raises(self):
        node = ParentNode("div", [])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_deeply_nested(self):
        node = ParentNode(
            "div",
            [ParentNode("section", [ParentNode("p", [LeafNode("b", "deep")])])]
        )
        self.assertEqual(node.to_html(), "<div><section><p><b>deep</b></p></section></div>")

    def test_mixed_parent_and_leaf_children(self):
        node = ParentNode(
            "ul",
            [
                ParentNode("li", [LeafNode("b", "item 1")]),
                LeafNode("li", "item 2"),
            ],
        )
        self.assertEqual(node.to_html(), "<ul><li><b>item 1</b></li><li>item 2</li></ul>")


if __name__ == "__main__":
    unittest.main()
