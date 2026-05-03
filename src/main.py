import os
import re
import shutil

from converters import markdown_to_html_node


def copy_dir_recursive(src, dst):
    if not os.path.exists(dst):
        os.mkdir(dst)

    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isfile(src_path):
            shutil.copy(src_path, dst_path)
            print(f"Copied file: {src_path} -> {dst_path}")
        else:
            copy_dir_recursive(src_path, dst_path)


def copy_static_to_public():
    project_root = os.path.dirname(os.path.dirname(__file__))
    source_dir = os.path.join(project_root, "static")
    dest_dir = os.path.join(project_root, "public")

    required_files = [
        os.path.join(source_dir, "index.css"),
        os.path.join(source_dir, "images", "tolkien.png"),
    ]
    for file_path in required_files:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Missing required static asset: {file_path}")

    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    copy_dir_recursive(source_dir, dest_dir)


def extract_title(markdown):
    for line in markdown.split("\n"):
        match = re.match(r"^#\s+(.+)$", line.strip())
        if match:
            return match.group(1).strip()
    raise ValueError("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r", encoding="utf-8") as markdown_file:
        markdown_content = markdown_file.read()

    with open(template_path, "r", encoding="utf-8") as template_file:
        template_content = template_file.read()

    html_content = markdown_to_html_node(markdown_content).to_html()
    title = extract_title(markdown_content)
    page_content = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as output_file:
        output_file.write(page_content)


def main():
    project_root = os.path.dirname(os.path.dirname(__file__))

    copy_static_to_public()
    generate_page(
        os.path.join(project_root, "content", "index.md"),
        os.path.join(project_root, "template.html"),
        os.path.join(project_root, "public", "index.html"),
    )


if __name__ == "__main__":
    main()
