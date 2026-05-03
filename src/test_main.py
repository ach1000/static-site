import os
import tempfile
import unittest

from main import extract_title, generate_page


class TestMainHelpers(unittest.TestCase):
    def test_extract_title(self):
        markdown = "# Hello"
        self.assertEqual(extract_title(markdown), "Hello")

    def test_extract_title_strips_whitespace(self):
        markdown = "\n  #   Tolkien Fan Club   \nSome text\n"
        self.assertEqual(extract_title(markdown), "Tolkien Fan Club")

    def test_extract_title_raises_without_h1(self):
        markdown = "## Not h1\nParagraph"
        with self.assertRaises(ValueError):
            extract_title(markdown)

    def test_generate_page(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_path = os.path.join(temp_dir, "index.md")
            template_path = os.path.join(temp_dir, "template.html")
            output_path = os.path.join(temp_dir, "nested", "index.html")

            with open(markdown_path, "w", encoding="utf-8") as markdown_file:
                markdown_file.write("# Hello\n\nThis is **bold** text.")

            with open(template_path, "w", encoding="utf-8") as template_file:
                template_file.write(
                    "<html><head><title>{{ Title }}</title></head><body>{{ Content }}</body></html>"
                )

            generate_page(markdown_path, template_path, output_path)

            with open(output_path, "r", encoding="utf-8") as output_file:
                generated = output_file.read()

            self.assertIn("<title>Hello</title>", generated)
            self.assertIn("<div><h1>Hello</h1><p>This is <b>bold</b> text.</p></div>", generated)


if __name__ == "__main__":
    unittest.main()
