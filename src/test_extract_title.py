import unittest
from extract_title import extract_title


class TestExtractTitle(unittest.TestCase):
    def test_extract_title_simple(self):
        """Test extracting a simple h1 title."""
        markdown = "# Hello"
        self.assertEqual(extract_title(markdown), "Hello")

    def test_extract_title_with_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        markdown = "#   Hello World   "
        self.assertEqual(extract_title(markdown), "Hello World")

    def test_extract_title_with_content_after(self):
        """Test extracting title from markdown with content after."""
        markdown = "# My Title\n\nSome content here."
        self.assertEqual(extract_title(markdown), "My Title")

    def test_extract_title_ignores_h2(self):
        """Test that h2 headers are ignored."""
        markdown = "## Not a title\n# The Real Title"
        self.assertEqual(extract_title(markdown), "The Real Title")

    def test_extract_title_ignores_h3_and_higher(self):
        """Test that h3+ headers are ignored."""
        markdown = "### Not a title\n#### Also not\n# Correct Title"
        self.assertEqual(extract_title(markdown), "Correct Title")

    def test_extract_title_no_h1_raises_exception(self):
        """Test that ValueError is raised when no h1 is found."""
        markdown = "## Only h2\n### Only h3\nSome content"
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertIn("No h1 header", str(context.exception))

    def test_extract_title_empty_markdown_raises_exception(self):
        """Test that ValueError is raised for empty markdown."""
        markdown = ""
        with self.assertRaises(ValueError):
            extract_title(markdown)

    def test_extract_title_only_hash_raises_exception(self):
        """Test that a lone # without text raises an exception."""
        markdown = "#\n\nSome content"
        with self.assertRaises(ValueError):
            extract_title(markdown)

    def test_extract_title_multiline_markdown(self):
        """Test extracting title from complex markdown."""
        markdown = """# The Hobbit

This is a story about hobbits.

## Chapter 1

Once upon a time...
"""
        self.assertEqual(extract_title(markdown), "The Hobbit")


if __name__ == "__main__":
    unittest.main()
