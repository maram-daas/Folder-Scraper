import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import platform
from pathlib import Path
import threading
import time
from collections import defaultdict


class FolderScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Scraper")
        self.root.geometry("1000x700")

        # User-defined classification categories
        self.classification_categories = []

        # Variables
        self.selected_folder = tk.StringVar()
        self.search_keyword = tk.StringVar()
        self.max_depth = tk.IntVar(value=10)  # Limit search depth
        self.max_results = tk.IntVar(value=1000)  # Limit results

        # Thread control
        self.search_thread = None
        self.stop_search = False
        self.current_results = defaultdict(list)

        # Settings file path
        self.settings_file = os.path.join(
            os.path.expanduser("~"), ".folder_scraper_settings.txt")

        # Load saved default folder or set initial default
        self.load_default_folder()

        self.setup_ui()

    def load_default_folder(self):
        """Load the saved default folder from settings file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        saved_folder = lines[0].strip()
                        if saved_folder and os.path.exists(saved_folder):
                            self.selected_folder.set(saved_folder)
                        
                        # Load classification categories if they exist
                        if len(lines) > 1:
                            categories_line = lines[1].strip()
                            if categories_line:
                                self.classification_categories = [cat.strip() for cat in categories_line.split(',') if cat.strip()]
                        return
        except:
            pass

        # If no saved folder or file doesn't exist, use default
        default_folder = r"C:\Users\kayo\OneDrive\Documents"  # Change this line
        if os.path.exists(default_folder):
            self.selected_folder.set(default_folder)
        
        # No default categories - start with empty list

    def save_settings(self):
        """Save the selected folder and classification categories for future use"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                f.write(self.selected_folder.get() + '\n')
                f.write(','.join(self.classification_categories) + '\n')
        except:
            pass  # Silently ignore save errors

    def setup_ui(self):
        # Set theme
        style = ttk.Style()
        style.theme_use('vista')  # or 'vista', 'xpnative', 'winnative'

        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)

        # Folder selection
        ttk.Label(main_frame, text="Select Folder:", font=("Arial", 14)).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))

        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_frame.columnconfigure(0, weight=1)

        self.folder_entry = ttk.Entry(
            folder_frame, textvariable=self.selected_folder, font=("Arial", 12), state="readonly")
        self.folder_entry.grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(folder_frame, text="Browse",
                   command=self.browse_folder).grid(row=0, column=1)

        # Classification categories management
        categories_frame = ttk.LabelFrame(main_frame, text="Classification Categories (Optional)", padding="10")
        categories_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        categories_frame.columnconfigure(1, weight=1)

        # Current categories display
        ttk.Label(categories_frame, text="Current Categories:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.categories_var = tk.StringVar()
        self.update_categories_display()
        categories_display = ttk.Entry(categories_frame, textvariable=self.categories_var, 
                                     font=("Arial", 10), state="readonly")
        categories_display.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        # Add category section
        add_frame = ttk.Frame(categories_frame)
        add_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        add_frame.columnconfigure(1, weight=1)

        ttk.Label(add_frame, text="Add Category:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.new_category_var = tk.StringVar()
        self.category_entry = ttk.Entry(add_frame, textvariable=self.new_category_var, font=("Arial", 10))
        self.category_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.category_entry.bind('<Return>', lambda e: self.add_category())

        ttk.Button(add_frame, text="Add", command=self.add_category).grid(row=0, column=2, padx=(5, 10))
        ttk.Button(add_frame, text="Clear All", command=self.clear_categories).grid(row=0, column=3, padx=(5, 0))

        # Remove category section
        remove_frame = ttk.Frame(categories_frame)
        remove_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        remove_frame.columnconfigure(1, weight=1)

        ttk.Label(remove_frame, text="Remove Category:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.remove_category_var = tk.StringVar()
        self.remove_combobox = ttk.Combobox(remove_frame, textvariable=self.remove_category_var, 
                                          font=("Arial", 10), state="readonly")
        self.remove_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.update_remove_combobox()

        ttk.Button(remove_frame, text="Remove", command=self.remove_category).grid(row=0, column=2)

        # Search keyword
        ttk.Label(main_frame, text="Search Keyword:", font=("Arial", 14)).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 10))

        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(0, weight=1)

        self.search_entry = ttk.Entry(
            search_frame, textvariable=self.search_keyword, font=("Arial", 12))
        self.search_entry.grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.search_folders())

        self.search_button = ttk.Button(search_frame, text="Search",
                                       command=self.search_folders)
        self.search_button.grid(row=0, column=1, padx=(10, 0))

        self.stop_button = ttk.Button(search_frame, text="Stop",
                                     command=self.stop_search_process, state="disabled")
        self.stop_button.grid(row=0, column=2, padx=(5, 0))

        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Search Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(2, weight=1)

        ttk.Label(settings_frame, text="Max Depth:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        depth_spinbox = ttk.Spinbox(settings_frame, from_=1, to=20, width=10, textvariable=self.max_depth)
        depth_spinbox.grid(row=0, column=1, padx=(0, 20))

        ttk.Label(settings_frame, text="Max Results:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        results_spinbox = ttk.Spinbox(settings_frame, from_=100, to=10000, width=10, textvariable=self.max_results, increment=100)
        results_spinbox.grid(row=0, column=3)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2,
                           sticky=(tk.W, tk.E), pady=(0, 10))

        # Status label
        self.status_label = ttk.Label(
            main_frame, text="Ready", font=("Arial", 11))
        self.status_label.grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Real-time results counter
        self.results_counter = ttk.Label(
            main_frame, text="Results found: 0", font=("Arial", 10), foreground="blue")
        self.results_counter.grid(
            row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Results area
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=7, column=0, columnspan=2,
                           sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Create treeview for results
        self.tree = ttk.Treeview(results_frame)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure treeview font
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        # Configure big titles for classification groups
        self.tree.tag_configure("classification", font=(
            "Arial", 16, "bold"), foreground="green")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            results_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(
            results_frame, orient="horizontal", command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=h_scrollbar.set)

        # Configure treeview
        self.tree.heading('#0', text='Search Results', anchor=tk.W)
        self.tree.bind('<Double-1>', self.on_item_double_click)

    def update_categories_display(self):
        """Update the display of current categories"""
        categories_text = ", ".join(self.classification_categories) if self.classification_categories else "No categories defined"
        self.categories_var.set(categories_text)

    def update_remove_combobox(self):
        """Update the remove category combobox"""
        self.remove_combobox['values'] = self.classification_categories
        if self.classification_categories:
            self.remove_combobox.set('')

    def add_category(self):
        """Add a new classification category"""
        category = self.new_category_var.get().strip()
        if not category:
            messagebox.showwarning("Warning", "Please enter a category name.")
            return
        
        if category in self.classification_categories:
            messagebox.showwarning("Warning", f"Category '{category}' already exists.")
            return
        
        self.classification_categories.append(category)
        self.new_category_var.set("")
        self.update_categories_display()
        self.update_remove_combobox()
        self.save_settings()

    def remove_category(self):
        """Remove a classification category"""
        category = self.remove_category_var.get()
        if not category:
            messagebox.showwarning("Warning", "Please select a category to remove.")
            return
        
        if category in self.classification_categories:
            self.classification_categories.remove(category)
            self.update_categories_display()
            self.update_remove_combobox()
            self.save_settings()

    def clear_categories(self):
        """Clear all classification categories"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all categories?"):
            self.classification_categories.clear()
            self.update_categories_display()
            self.update_remove_combobox()
            self.save_settings()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
            # Save settings when folder changes
            self.save_settings()

    def search_folders(self):
        if not self.selected_folder.get():
            messagebox.showwarning("Warning", "Please select a folder first.")
            return

        if not self.search_keyword.get().strip():
            messagebox.showwarning("Warning", "Please enter a search keyword.")
            return

        # Removed the check for classification categories - search can work without them

        # Check if search is already running
        if self.search_thread and self.search_thread.is_alive():
            messagebox.showinfo("Info", "Search is already running. Please wait or stop the current search.")
            return

        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Reset search state
        self.stop_search = False
        self.current_results = defaultdict(list)

        # Update UI state
        self.search_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress.start()
        self.status_label.config(text="Searching...")
        self.results_counter.config(text="Results found: 0")

        # Start search in a separate thread
        self.search_thread = threading.Thread(target=self.perform_search_threaded, daemon=True)
        self.search_thread.start()

        # Start periodic UI updates
        self.update_ui_periodically()

    def stop_search_process(self):
        """Stop the current search"""
        self.stop_search = True
        self.search_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress.stop()
        self.status_label.config(text="Search stopped by user.")

    def perform_search_threaded(self):
        """Perform search in a separate thread"""
        try:
            self.perform_search()
        except Exception as e:
            # Schedule error display in main thread
            self.root.after(0, lambda: self.handle_search_error(str(e)))
        finally:
            # Schedule UI cleanup in main thread
            self.root.after(0, self.search_completed)

    def handle_search_error(self, error_msg):
        """Handle search errors in the main thread"""
        messagebox.showerror("Error", f"An error occurred during search: {error_msg}")
        self.status_label.config(text="Search failed.")
        self.search_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress.stop()

    def search_completed(self):
        """Handle search completion in the main thread"""
        # Final update of results display
        self.display_results(dict(self.current_results))
        
        if not self.stop_search:
            total_results = sum(len(matches) for matches in self.current_results.values())
            self.status_label.config(text=f"Search completed. Found {total_results} matches.")
            self.results_counter.config(text=f"Results found: {total_results}")
        
        self.search_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress.stop()

    def perform_search(self):
        base_folder = self.selected_folder.get()
        keyword = self.search_keyword.get().strip().lower()
        max_depth = self.max_depth.get()
        max_results = self.max_results.get()
        
        total_found = 0
        processed_count = 0

        def search_recursive(current_path, current_depth=0, visited_paths=None):
            nonlocal total_found, processed_count
            
            # Check if we should stop
            if self.stop_search or total_found >= max_results:
                return
            
            # Check depth limit
            if current_depth > max_depth:
                return

            if visited_paths is None:
                visited_paths = set()

            # Avoid infinite loops with symlinks
            try:
                real_path = os.path.realpath(current_path)
                if real_path in visited_paths:
                    return
                visited_paths.add(real_path)
            except (OSError, ValueError):
                return

            try:
                # Use os.scandir for better performance
                with os.scandir(current_path) as entries:
                    for entry in entries:
                        if self.stop_search or total_found >= max_results:
                            break
                        
                        processed_count += 1
                        
                        # Update status periodically (every 100 items)
                        if processed_count % 100 == 0:
                            self.update_status_async(f"Processed {processed_count} items...")

                        try:
                            # Check if item name contains keyword (case-insensitive)
                            if keyword in entry.name.lower():
                                # Found a match - classify (or put in "All Results" if no categories defined)
                                classification = self.classify_path(entry.path, base_folder)
                                self.current_results[classification].append(entry.path)
                                total_found += 1
                                
                                # Don't search inside matched directories to improve performance
                                continue

                            # If no match and it's a directory, continue searching inside
                            if entry.is_dir(follow_symlinks=False):
                                search_recursive(entry.path, current_depth + 1, visited_paths.copy())
                        
                        except (PermissionError, OSError, FileNotFoundError):
                            # Skip files/folders we can't access
                            continue

            except (PermissionError, OSError, FileNotFoundError):
                return

        search_recursive(base_folder)

    def update_status_async(self, message):
        """Update status label from background thread"""
        self.root.after(0, lambda: self.status_label.config(text=message))

    def update_ui_periodically(self):
        """Update UI with current results periodically"""
        if self.search_thread and self.search_thread.is_alive():
            # Update results display if we have results
            if self.current_results:
                self.display_results(dict(self.current_results))
            
            # Update counter
            total_results = sum(len(matches) for matches in self.current_results.values())
            self.results_counter.config(text=f"Results found: {total_results}")
            
            # Schedule next update
            self.root.after(1000, self.update_ui_periodically)  # Increased to 1 second for better performance

    def classify_path(self, item_path, base_folder):
        # If no categories defined, put everything in "All Results"
        if not self.classification_categories:
            return "All Results"
        
        # Get relative path from base folder
        try:
            rel_path = os.path.relpath(item_path, base_folder)
            path_parts = Path(rel_path).parts

            # Check if any parent folder contains classification categories
            for part in path_parts:
                for category in self.classification_categories:
                    if category.lower() in part.lower():
                        return category

            return "Other"
        except:
            return "Other"

    def display_results(self, results):
        # Clear existing results
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Determine which classifications to show
        if self.classification_categories:
            classifications_to_show = self.classification_categories + ["Other"]
        else:
            classifications_to_show = ["All Results"]

        for i, classification in enumerate(classifications_to_show):
            matches = results.get(classification, [])
            if matches:
                # Add spacing between sections (except for the first one)
                if i > 0 and any(results.get(prev_class, []) for prev_class in classifications_to_show[:i]):
                    self.tree.insert('', 'end', text="", values=("spacer",))

                # Create parent node for each classification with big title styling
                parent = self.tree.insert('', 'end', text=f"📁 {classification} ({len(matches)} matches)",
                                          values=(classification,), open=True, tags=("classification",))

                # Add each match as a child (limit display for performance)
                display_limit = min(len(matches), 100)  # Only show first 100 matches per category
                for j, match in enumerate(matches[:display_limit]):
                    # Show relative path for cleaner display
                    try:
                        display_path = os.path.relpath(match, self.selected_folder.get())
                    except:
                        display_path = match

                    self.tree.insert(parent, 'end', text=f"  📄 {display_path}", values=(match,))
                
                # Add note if there are more results
                if len(matches) > display_limit:
                    self.tree.insert(parent, 'end', 
                                   text=f"  ... and {len(matches) - display_limit} more results", 
                                   values=("more",))

    def on_item_double_click(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            if values and len(values) > 0:
                path = values[0]
                # Don't open classification headers or spacers
                valid_categories = self.classification_categories + ["Other", "All Results"] if self.classification_categories else ["All Results"]
                if (path not in valid_categories + ["spacer", "more", "search_results"] 
                    and os.path.exists(path)):
                    self.open_in_explorer(path)

    def open_in_explorer(self, path):
        try:
            if platform.system() == "Windows":
                # If it's a file, select it in explorer, otherwise open the folder
                if os.path.isfile(path):
                    subprocess.run(['explorer', '/select,', os.path.normpath(path)], check=True)
                else:
                    subprocess.run(['explorer', os.path.normpath(path)], check=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', path], check=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open path: {path}\nError: {str(e)}")


def main():
    root = tk.Tk()
    app = FolderScraperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
