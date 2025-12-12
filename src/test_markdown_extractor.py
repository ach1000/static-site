import unittest

from markdown_extractor import extract_markdown_images, extract_markdown_links


class TestMarkdownExtractor(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        text = "Here ![one](https://a.png) and ![two](https://b.jpg)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("one", "https://a.png"), ("two", "https://b.jpg")], matches)

    def test_extract_images_empty_alt(self):
        text = "![ ](https://example.com/img.png)"
        # alt contains a space in this case
        matches = extract_markdown_images(text)
        self.assertEqual(len(matches), 1)

    def test_extract_no_images(self):
        self.assertEqual(extract_markdown_images("no images here"), [])

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev"),
        ], matches)

    def test_links_ignore_images(self):
        text = "An image ![img](https://i.imgur.com/x.png) and a link [site](https://example.com)"
        link_matches = extract_markdown_links(text)
        image_matches = extract_markdown_images(text)
        self.assertListEqual([("site", "https://example.com")], link_matches)
        self.assertListEqual([("img", "https://i.imgur.com/x.png")], image_matches)

    def test_links_none_or_empty(self):
        self.assertEqual(extract_markdown_links(""), [])
        self.assertEqual(extract_markdown_images(None), [])


if __name__ == "__main__":
    unittest.main()
