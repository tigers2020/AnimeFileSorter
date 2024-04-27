import os
import shutil

class FileRemover:
    def __init__(self, root_dir, target_dir_name='1080p'):
        self.root_dir = root_dir
        self.target_dir_name = target_dir_name

    def remove_files_in_target(self):
        """Walks through the directory structure and removes files in directories named as target_dir_name."""
        for dirpath, dirnames, filenames in os.walk(self.root_dir, topdown=False):
            # Check if the current directory is the target directory
            if os.path.basename(dirpath) == self.target_dir_name:
                for file in filenames:
                    file_path = os.path.join(dirpath, file)
                    os.remove(file_path)
                    print(f"Removed file: {file_path}")
                # After removing files, check if directory is empty and remove it
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
                    print(f"Removed empty directory: {dirpath}")
            else:
                # For non-target directories, remove them if they are empty
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
                    print(f"Removed empty directory: {dirpath}")

if __name__ == "__main__":
    root_directory = "./organized"
    remover = FileRemover(root_directory)
    remover.remove_files_in_target()
