import os
import tempfile
import unittest

from main import extract_title, generate_page
from main import generate_pages_recursive


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

    def test_generate_pages_recursive(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            content_dir = os.path.join(temp_dir, "content")
            template_path = os.path.join(temp_dir, "template.html")
            output_dir = os.path.join(temp_dir, "public")

            os.makedirs(os.path.join(content_dir, "blog", "post"), exist_ok=True)

            with open(os.path.join(content_dir, "index.md"), "w", encoding="utf-8") as file:
                file.write("# Home\n\nRoot page")

            with open(os.path.join(content_dir, "blog", "post", "index.md"), "w", encoding="utf-8") as file:
                file.write("# Post\n\nNested page")

            with open(template_path, "w", encoding="utf-8") as template_file:
                template_file.write("<html><head><title>{{ Title }}</title></head><body>{{ Content }}</body></html>")

            generate_pages_recursive(content_dir, template_path, output_dir)

            root_output = os.path.join(output_dir, "index.html")
            nested_output = os.path.join(output_dir, "blog", "post", "index.html")

            self.assertTrue(os.path.exists(root_output))
            self.assertTrue(os.path.exists(nested_output))

            with open(nested_output, "r", encoding="utf-8") as output_file:
                nested_generated = output_file.read()

            self.assertIn("<title>Post</title>", nested_generated)
            self.assertIn("<div><h1>Post</h1><p>Nested page</p></div>", nested_generated)


if __name__ == "__main__":
    unittest.main()
