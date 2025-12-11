import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_with_props(self):
        # test that props_to_html formats multiple properties correctly
        node = HTMLNode(
            tag="a",
            value="Click me",
            props={
                "href": "https://www.google.com",
                "target": "_blank",
            }
        )
        result = node.props_to_html()
        # Check that both properties are formatted correctly with leading space
        self.assertIn(' href="https://www.google.com"', result)
        self.assertIn(' target="_blank"', result)

    def test_props_to_html_empty(self):
        # test that props_to_html returns empty string when props is empty
        node = HTMLNode(tag="p", value="Text", props={})
        result = node.props_to_html()
        self.assertEqual(result, "")

    def test_props_to_html_none(self):
        # test that props_to_html returns empty string when props is None
        node = HTMLNode(tag="p", value="Text", props=None)
        result = node.props_to_html()
        self.assertEqual(result, "")

    def test_props_to_html_single_prop(self):
        # test that props_to_html works with a single property
        node = HTMLNode(
            tag="img",
            props={"src": "/path/to/image.png"}
        )
        result = node.props_to_html()
        self.assertEqual(result, ' src="/path/to/image.png"')

    def test_repr(self):
        # test that __repr__ outputs the node information
        node = HTMLNode(
            tag="div",
            value="Content",
            children=[],
            props={"class": "container"}
        )
        repr_str = repr(node)
        self.assertIn("tag=div", repr_str)
        self.assertIn("value=Content", repr_str)
        self.assertIn("class", repr_str)

    def test_to_html_raises(self):
        # test that to_html() raises NotImplementedError
        node = HTMLNode(tag="p")
        with self.assertRaises(NotImplementedError):
            node.to_html()


if __name__ == "__main__":
    unittest.main()
