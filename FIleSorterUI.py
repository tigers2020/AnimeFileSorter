import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from threading import Thread, Event
from src.file_organizer import FileOrganizer
from src.log import logger

LAST_SORTED_DIR_FILE = 'last_sorted_directory.json'


class FileSorterUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Sorter")
        self.root.geometry("800x600")
        self.config_path = "src/config.json"
        self.file_organizer = None
        self.processing = False
        self.stop_event = Event()
        self.pause_event = Event()
        self.create_widgets()
        self.load_config()
        self.load_last_sorted_directory()

    def create_widgets(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(4, weight=1)

        self.dir_label = tk.Label(self.root, text="Directory to Sort:")
        self.dir_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.dir_entry = tk.Entry(self.root)
        self.dir_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.output_dir_label = tk.Label(self.root, text="Output Directory:")
        self.output_dir_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.output_dir_entry = tk.Entry(self.root)
        self.output_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.output_dir_entry.config(state='readonly')

        self.process_button = tk.Button(self.root, text="Process Files", command=self.start_process_files)
        self.process_button.grid(row=2, column=0, padx=10, pady=10)

        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_resume_processing, state=tk.DISABLED)
        self.pause_button.grid(row=2, column=1, padx=10, pady=10)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=2, padx=10, pady=10)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.log_text = scrolledtext.ScrolledText(self.root, state='disabled', wrap='word')
        self.log_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    def load_config(self):
        if not os.path.exists(self.config_path):
            messagebox.showerror("Error", f"Config file {self.config_path} not found.")
            return
        try:
            with open(self.config_path, 'r') as file:
                config = json.load(file)
            self.file_organizer = FileOrganizer(config)
            self.log_message("Config loaded successfully.", "green")
        except Exception as e:
            self.log_message(f"Failed to load config: {e}", "red")
            logger.error("Failed to load config", exc_info=True)

    def load_last_sorted_directory(self):
        if os.path.exists(LAST_SORTED_DIR_FILE):
            with open(LAST_SORTED_DIR_FILE, 'r') as file:
                data = json.load(file)
                last_sorted_dir = data.get('last_sorted_directory', '')
                if last_sorted_dir:
                    self.update_directory_entries(last_sorted_dir)

    def update_directory_entries(self, directory):
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, directory)
        self.output_dir_entry.config(state='normal')
        self.output_dir_entry.delete(0, tk.END)
        parent_dir = os.path.dirname(directory)
        self.output_dir_entry.insert(0, os.path.join(parent_dir, "organized"))
        self.output_dir_entry.config(state='readonly')

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.update_directory_entries(directory)

    def start_process_files(self):
        self.processing = True
        self.process_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.stop_event.clear()
        self.pause_event.clear()
        Thread(target=self.process_files).start()

    def pause_resume_processing(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.pause_button.config(text="Pause")
        else:
            self.pause_event.set()
            self.pause_button.config(text="Resume")

    def stop_processing(self):
        self.stop_event.set()
        self.pause_event.clear()
        self.processing = False
        self.process_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)

    def process_files(self):
        directory = self.dir_entry.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory to process.")
            self.stop_processing()
            return

        output_dir = self.output_dir_entry.get()
        self.file_organizer.set_directories(directory, output_dir)

        file_list = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_list.append(os.path.join(root, file))

        total_files = len(file_list)
        if total_files == 0:
            self.log_message("No files to process in the selected directory.", "red")
            self.stop_processing()
            return

        self.progress['maximum'] = total_files
        self.progress['value'] = 0

        try:
            for idx, file_path in enumerate(file_list):
                if self.stop_event.is_set():
                    break
                while self.pause_event.is_set():
                    if self.stop_event.is_set():
                        break
                try:
                    self.file_organizer.process_file(file_path)
                    self.progress['value'] = idx + 1
                    self.root.update_idletasks()
                    self.log_message(f"Processed file: {file_path}", "blue")
                except Exception as e:
                    self.log_message(f"Error processing {file_path}: {str(e)}", "red")
                    logger.error(f"Error processing {file_path}", exc_info=True)

            if not self.stop_event.is_set():
                self.log_message("All files processed successfully.", "green")
                messagebox.showinfo("Success", "Files processed successfully.")
        except Exception as e:
            error_msg = f"Failed to process files: {str(e)}"
            self.log_message(error_msg, "red")
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", error_msg)
        finally:
            self.stop_processing()

    def log_message(self, message, color):
        self.log_text.config(state='normal')
        self.log_text.tag_config(color, foreground=color)
        self.log_text.insert(tk.END, message + "\n", color)
        self.log_text.config(state='disabled')
        self.log_text.yview(tk.END)


def main():
    root = tk.Tk()
    FileSorterUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
