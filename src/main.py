import os
import re
import shutil
import sys

from converters import markdown_to_html_node


def copy_dir_recursive(src, dst):
    """Recursively copy all contents from src to dst.

    If dst exists it will be removed first to ensure a clean copy.
    
    Args:
        src: Source directory path.
        dst: Destination directory path.
        
    Raises:
        FileNotFoundError: If source directory does not exist.
    """
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source directory does not exist: {src}")

    # Remove destination if it exists to ensure a clean copy
    if os.path.exists(dst):
        try:
            if os.path.isfile(dst):
                os.remove(dst)
            else:
                shutil.rmtree(dst)
        except Exception as e:
            print(f"Warning: Could not remove {dst}: {e}")
            import time
            time.sleep(0.1)
            try:
                shutil.rmtree(dst, ignore_errors=True)
            except:
                pass

    os.makedirs(dst, exist_ok=True)

    for entry in os.listdir(src):
        path_src = os.path.join(src, entry)
        path_dst = os.path.join(dst, entry)

        if os.path.isdir(path_src):
            os.makedirs(path_dst, exist_ok=True)
            copy_dir_recursive(path_src, path_dst)
        elif os.path.isfile(path_src):
            try:
                shutil.copy(path_src, path_dst)
                print(f"Copied file: {path_dst}")
            except Exception as e:
                print(f"Error copying {path_src}: {e}")


def extract_title(markdown):
    """Extract the h1 title from markdown content.
    
    Args:
        markdown: Markdown text content.
        
    Returns:
        The title text from the first h1 header.
        
    Raises:
        ValueError: If no h1 header is found.
    """
    for line in markdown.split("\n"):
        match = re.match(r"^#\s+(.+)$", line.strip())
        if match:
            return match.group(1).strip()
    raise ValueError("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path, basepath="/"):
    """Generate an HTML page from markdown and template.
    
    Args:
        from_path: Path to the source markdown file.
        template_path: Path to the HTML template file.
        dest_path: Path where the generated HTML should be written.
        basepath: Base path for the site (default "/").
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r", encoding="utf-8") as markdown_file:
        markdown_content = markdown_file.read()

    with open(template_path, "r", encoding="utf-8") as template_file:
        template_content = template_file.read()

    html_content = markdown_to_html_node(markdown_content).to_html()
    title = extract_title(markdown_content)
    page_content = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    
    # Replace root-relative paths with basepath
    page_content = page_content.replace('href="/', f'href="{basepath}')
    page_content = page_content.replace("src=\"/", f"src=\"{basepath}")

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as output_file:
        output_file.write(page_content)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    """Recursively generate HTML pages from all markdown files in content directory.
    
    Crawls the content directory structure and generates corresponding HTML files
    in the destination directory, maintaining the same directory structure.
    
    Args:
        dir_path_content: Root path to the content directory (containing markdown files).
        template_path: Path to the HTML template file.
        dest_dir_path: Root path where generated HTML files should be written.
        basepath: Base path for the site (default "/").
    """
    for entry in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content, entry)
        dest_path = os.path.join(dest_dir_path, entry)

        if os.path.isfile(from_path) and from_path.endswith(".md"):
            dest_file_path = f"{os.path.splitext(dest_path)[0]}.html"
            generate_page(from_path, template_path, dest_file_path, basepath)
            continue

        if os.path.isdir(from_path):
            generate_pages_recursive(from_path, template_path, dest_path, basepath)


def main():
    """Main entry point for the site generator.
    
    Reads basepath from CLI argument (default "/"), normalizes it appropriately
    for path-style basepaths, then generates the complete site from markdown.
    """
    # Get basepath from CLI arguments, default to "/"
    basepath = "/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]

    # Normalize basepath: ensure it starts and ends with a slash for
    # path-style basepaths (e.g. "mysite" -> "/mysite/") but do NOT
    # prepend a slash for full URLs (e.g. "https://..." should remain
    # as-is, only ensure a trailing slash).
    if basepath != "/":
        if basepath.startswith("http://") or basepath.startswith("https://"):
            if not basepath.endswith("/"):
                basepath = basepath + "/"
        else:
            if not basepath.startswith("/"):
                basepath = "/" + basepath
            if not basepath.endswith("/"):
                basepath = basepath + "/"
    
    # Determine project root (parent of src/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(project_root, "static")
    docs_dir = os.path.join(project_root, "docs")
    template_path = os.path.join(project_root, "template.html")
    content_dir = os.path.join(project_root, "content")

    try:
        # Copy static files to docs directory
        copy_dir_recursive(static_dir, docs_dir)
        print(f"Static files copied to {docs_dir}")
        
        # Generate all pages from content directory
        generate_pages_recursive(content_dir, template_path, docs_dir, basepath)
        print(f"All pages generated successfully in {docs_dir}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
