import os

def delete_empty_folders(root_path):
    # topdown=False is critical to delete nested empty folders
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
        # If the current folder has no files and no sub-folders
        if not dirnames and not filenames:
            try:
                os.rmdir(dirpath)
                print(f"Deleted: {dirpath}")
            except OSError as e:
                print(f"Error deleting {dirpath}: {e}")

# Replace with your target directory path
target_directory = r"C:\Users\Yanet\OneDrive\Documents\assignments\scanner\.git"
delete_empty_folders(target_directory)
