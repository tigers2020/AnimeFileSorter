import os
import shutil
import logging

logging.basicConfig(filename='file-removal.log', level=logging.INFO)


class FileRemover:
    def __init__(self, root_dir, target_dir_name='1080p'):
        self.root_dir = root_dir
        self.target_dir_name = target_dir_name

    def remove_files_in_target(self):
        for dirpath, dirnames, filenames in os.walk(self.root_dir, topdown=False):
            if os.path.basename(dirpath) == self.target_dir_name:
                for file in filenames:
                    file_path = os.path.join(dirpath, file)
                    try:
                        os.remove(file_path)
                        logging.info(f"Removed file: {file_path}")
                    except Exception as e:
                        logging.error(f"Could not remove file: {file_path}. Error: {e}")
                if not os.listdir(dirpath):
                    try:
                        os.rmdir(dirpath)
                        logging.info(f"Removed empty directory: {dirpath}")
                    except Exception as e:
                        logging.error(f"Could not remove directory: {dirpath}. Error: {e}")


if __name__ == "__main__":
    root_directory = "./organized"
    remover = FileRemover(root_directory)
    remover.remove_files_in_target()
