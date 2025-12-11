import unittest

from leafnode import LeafNode
from parentnode import ParentNode


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_multiple_children(self):
        parent_node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            parent_node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_to_html_with_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "container"})
        self.assertEqual(
            parent_node.to_html(),
            '<div class="container"><span>child</span></div>',
        )

    def test_to_html_no_children_raises(self):
        with self.assertRaises(ValueError):
            ParentNode("div", None)

    def test_to_html_no_tag_raises(self):
        child_node = LeafNode("span", "child")
        with self.assertRaises(ValueError):
            ParentNode(None, [child_node])

    def test_to_html_nested_parents(self):
        grandchild = LeafNode("b", "bold")
        child = ParentNode("span", [grandchild])
        parent = ParentNode("div", [child, LeafNode(None, " text")])
        self.assertEqual(
            parent.to_html(),
            "<div><span><b>bold</b></span> text</div>",
        )

    def test_to_html_deep_nesting(self):
        node = LeafNode("b", "content")
        for tag in ["span", "div", "p", "section"]:
            node = ParentNode(tag, [node])
        self.assertEqual(
            node.to_html(),
            "<section><p><div><span><b>content</b></span></div></p></section>",
        )

    def test_to_html_multiple_props(self):
        child = LeafNode("a", "link")
        parent = ParentNode(
            "div",
            [child],
            {"class": "wrapper", "id": "main"},
        )
        result = parent.to_html()
        self.assertIn('class="wrapper"', result)
        self.assertIn('id="main"', result)
        self.assertIn("<a>link</a>", result)


if __name__ == "__main__":
    unittest.main()
