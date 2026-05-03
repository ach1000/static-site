import os
import shutil


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


def main():
    copy_static_to_public()


if __name__ == "__main__":
    main()
