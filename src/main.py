import os
import shutil
import sys


def copy_dir_recursive(src, dst):
    """Recursively copy all contents from src to dst.

    If dst exists it will be removed first to ensure a clean copy.
    """
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source directory does not exist: {src}")

    # Remove destination if it exists to ensure a clean copy
    if os.path.exists(dst):
        if os.path.isfile(dst):
            os.remove(dst)
        else:
            shutil.rmtree(dst)

    os.makedirs(dst, exist_ok=True)

    for entry in os.listdir(src):
        path_src = os.path.join(src, entry)
        path_dst = os.path.join(dst, entry)

        if os.path.isdir(path_src):
            os.makedirs(path_dst, exist_ok=True)
            copy_dir_recursive(path_src, path_dst)
        elif os.path.isfile(path_src):
            shutil.copy2(path_src, path_dst)
            print(f"Copied file: {path_dst}")


def main():
    # Determine project root (parent of src/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(project_root, "static")
    public_dir = os.path.join(project_root, "public")

    try:
        copy_dir_recursive(static_dir, public_dir)
        print(f"Static site copied from {static_dir} -> {public_dir}")
    except Exception as e:
        print(f"Error copying site: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

