import os
import shutil
import sys
from generate_page import generate_pages_recursive


def copy_dir_recursive(src, dst):
    """Recursively copy all contents from src to dst.

    If dst exists it will be removed first to ensure a clean copy.
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


def main():
    # Get basepath from CLI arguments, default to /
    basepath = "/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]

    # Normalize basepath: ensure it starts and ends with a slash,
    # but keep root "/" as-is.
    if basepath != "/":
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

