import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import json
from typing import List
#pip install tkinterdnd2
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog

class FileCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Files Combiner")
        self.root.geometry("600x400")

        # Config file path
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        
        # Load save location from config or use default
        self.save_location = self.load_save_location()
        self.paths: List[str] = []
        self.empty_text = "Drag and drop files or folders here"

        # Create main frame with proper padding
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create save location frame with improved spacing
        self.save_location_frame = ttk.Frame(self.main_frame)
        self.save_location_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        self.save_location_label = ttk.Label(self.save_location_frame, text="Save Location:")
        self.save_location_label.grid(row=0, column=0, padx=(0, 10), pady=5)

        self.save_location_path = ttk.Label(self.save_location_frame, text=self.save_location)
        self.save_location_path.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.browse_btn = ttk.Button(
            self.save_location_frame,
            text="Browse",
            command=self.browse_save_location
        )
        self.browse_btn.grid(row=0, column=2, padx=(10, 0), pady=5)

        # Configure save location frame grid weights
        self.save_location_frame.columnconfigure(1, weight=1)

        # Create listbox with scrollbar and improved spacing
        self.listbox_frame = ttk.Frame(self.main_frame)
        self.listbox_frame.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=(0, 15)
        )

        self.listbox = tk.Listbox(self.listbox_frame, selectmode=tk.EXTENDED)
        self.scrollbar = ttk.Scrollbar(
            self.listbox_frame, orient=tk.VERTICAL, command=self.listbox.yview
        )
        self.listbox.configure(yscrollcommand=self.scrollbar.set)

        self.listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(5, 0))

        # Show empty state text
        self.listbox.insert(tk.END, self.empty_text)
        self.listbox.configure(fg='gray')

        # Bind selection event
        self.listbox.bind('<<ListboxSelect>>', self.on_selection_change)

        # Create button frame for better organization
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E))

        # Create buttons with improved spacing
        self.remove_selected_btn = ttk.Button(
            self.button_frame, text="Remove Selected", command=self.remove_selected
        )
        self.remove_selected_btn.grid(row=0, column=0, padx=(0, 10))

        self.clear_all_btn = ttk.Button(
            self.button_frame, text="Clear All", command=self.clear_all
        )
        self.clear_all_btn.grid(row=0, column=1, padx=10)

        self.create_btn = ttk.Button(
            self.button_frame,
            text="Create Combined File",
            command=self.create_combined_file,
        )
        self.create_btn.grid(row=0, column=2, padx=(10, 0))

        # Center the button frame
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)

        # Configure main grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.listbox_frame.columnconfigure(0, weight=1)
        self.listbox_frame.rowconfigure(0, weight=1)

        # Enable drag and drop
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind("<<Drop>>", self.handle_drop)

        # Update button states
        self.update_button_states()

    def load_save_location(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('save_location', os.getcwd())
        except Exception as e:
            print(f"Error loading config: {e}")
        return os.getcwd()

    def save_config(self):
        try:
            config = {'save_location': self.save_location}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def handle_drop(self, event):
        try:
            files = event.data
            # Clean up the file paths
            if isinstance(files, str):
                # Remove curly braces and quotes if present
                files = files.strip('{}').replace('"', '')
                files = files.split("\n")

            # Clear empty state if this is the first item
            if len(self.paths) == 0:
                self.listbox.delete(0, tk.END)
                self.listbox.configure(fg='black')

            for file_path in files:
                file_path = file_path.strip()
                if os.path.exists(file_path):
                    if file_path not in self.paths:
                        self.paths.append(file_path)
                        self.listbox.insert(tk.END, file_path)

            self.update_button_states()
        except Exception as e:
            messagebox.showerror("Error", f"Error handling drop: {str(e)}")

    def remove_selected(self):
        try:
            selected_indices = self.listbox.curselection()
            for index in reversed(selected_indices):
                self.listbox.delete(index)
                self.paths.pop(index)

            # Show empty state if no items left
            if len(self.paths) == 0:
                self.listbox.insert(tk.END, self.empty_text)
                self.listbox.configure(fg='gray')

            self.update_button_states()
        except Exception as e:
            messagebox.showerror("Error", f"Error removing selected items: {str(e)}")

    def clear_all(self):
        self.listbox.delete(0, tk.END)
        self.paths.clear()
        
        # Show empty state
        self.listbox.insert(tk.END, self.empty_text)
        self.listbox.configure(fg='gray')
        self.update_button_states()

    def browse_save_location(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_location = directory
            self.save_location_path.config(text=directory)
            self.save_config()

    def create_combined_file(self):
        if not self.paths:
            messagebox.showwarning("Warning", "No files or folders selected!")
            return

        try:
            output_path = os.path.join(self.save_location, "combined_output.txt")
            with open(output_path, "w", encoding="utf-8") as outfile:
                for path in self.paths:
                    if os.path.isfile(path):
                        self._process_file(path, outfile)
                    elif os.path.isdir(path):
                        self._process_directory(path, outfile)

            messagebox.showinfo(
                "Success",
                f"Files combined successfully!\nOutput saved to: {output_path}",
            )

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def _process_file(self, file_path: str, outfile):
        try:
            # Normalize path separators
            normalized_path = os.path.normpath(file_path)
            
            with open(file_path, "r", encoding="utf-8") as infile:
                outfile.write(f"\n{'='*50}\n")
                outfile.write(f"Content from: {normalized_path}\n")
                outfile.write(f"{'='*50}\n\n")
                outfile.write(infile.read())
                outfile.write("\n")
        except Exception as e:
            outfile.write(f"Error reading {file_path}: {str(e)}\n")

    def _process_directory(self, dir_path: str, outfile):
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                self._process_file(file_path, outfile)

    def update_button_states(self):
        has_items = len(self.paths) > 0
        has_selection = len(self.listbox.curselection()) > 0

        self.create_btn.configure(state='normal' if has_items else 'disabled')
        self.remove_selected_btn.configure(state='normal' if has_selection else 'disabled')
        self.clear_all_btn.configure(state='normal' if has_items else 'disabled')

    def on_selection_change(self, event):
        self.update_button_states()


def main():
    root = TkinterDnD.Tk()
    app = FileCombinerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
