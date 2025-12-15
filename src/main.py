import os
import shutil
import sys
from generate_page import generate_page


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
    # Determine project root (parent of src/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(project_root, "static")
    public_dir = os.path.join(project_root, "public")
    template_path = os.path.join(project_root, "template.html")
    content_path = os.path.join(project_root, "content", "index.md")
    dest_path = os.path.join(public_dir, "index.html")

    try:
        # Copy static files to public directory
        copy_dir_recursive(static_dir, public_dir)
        print(f"Static files copied to {public_dir}")
        
        # Generate the index page from markdown
        generate_page(content_path, template_path, dest_path)
        print(f"Page generated successfully at {dest_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

