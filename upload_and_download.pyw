#Author: Marc Steger
#
# This is a simple SSH Controller in order to make up and download faster and more comfortable.
# Tested and works for windows and linux based systems.
#

import os
import platform
from pprint import pprint
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def getSSHConfigs():
    ssh_config_path = ""
    if platform.system() == "Windows":
      ssh_config_path = os.path.join(os.environ["USERPROFILE"], ".ssh", "config")
    else:  # Linux / macOS
      ssh_config_path = os.path.expanduser("~/.ssh/config")
    hosts = []

    if not os.path.exists(ssh_config_path):
        return hosts
    
    with open(ssh_config_path, "r") as f:
      for line in f:
        line = line.strip()
        if line.startswith("Host "):
          hostnames = line[5:].strip().split()  # can be multiple aliases
          hosts.extend(hostnames)
    return hosts

class UploadDownloadApp:
  def __init__(self, root):
    self.root = root
    self.root.title("File Transfer")

    width = 620
    height = 600
    self.center_window(width, height)

    self.filenames = []

    # Container for pages
    self.container = tk.Frame(root)
    self.container.grid(row=0, column=0, sticky="nsew")

    # Make the root resizable and the container expand
    self.root.grid_rowconfigure(0, weight=1)
    self.root.grid_columnconfigure(0, weight=1)

    self.pages = {}
    for P in (UploadPage, DownloadPage):
      page = P(self.container, self)
      self.pages[P] = page
      page.grid(row=0, column=0, sticky="nsew")

    self.show_page(UploadPage)

  def show_page(self, page_class):
    page = self.pages[page_class]
    page.tkraise()

  def center_window(self, width, height):
    self.root.update_idletasks()
    x = (self.root.winfo_screenwidth() // 2) - (width // 2)
    y = (self.root.winfo_screenheight() // 2) - (height // 2)
    self.root.geometry(f"{width}x{height}+{x}+{y}")

class UploadPage(tk.Frame):
  def __init__(self, parent, controller):
    super().__init__(parent)
    self.controller = controller
    font = ("Arial", 14)

    # Make this page fill container
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)

    # Main frame centered
    main_frame = tk.Frame(self)
    main_frame.grid(row=0, column=0)
    
    tk.Label(main_frame, text="Upload Files", font=("Arial", 18)).pack(pady=10, padx=10)

    #Get file button
    self.get_file_button = tk.Button(main_frame, text="Select Files", command=self.get_files, font=font)
    self.get_file_button.pack(pady=10)

    self.form_frame = tk.Frame(main_frame)
    self.form_frame.pack(pady=10)

    # Scrollable Text widget to display selected files
    self.files_text_frame = tk.Frame(main_frame)
    self.files_text_frame.pack(pady=5, fill="both", expand=False)

    self.files_scrollbar = tk.Scrollbar(self.files_text_frame, orient="vertical")
    self.files_scrollbar.pack(side="right", fill="y")

    self.files_text = tk.Text(
      self.files_text_frame,
      height=6,  # fixed height
      width=60,
      font=("Arial", 12),
      yscrollcommand=self.files_scrollbar.set,
      wrap="none"
    )
    self.files_text.pack(side="left", fill="both", expand=True)
    self.files_text.insert("1.0", "No files selected")
    self.files_text.config(state="disabled")  # make read-only

    self.files_scrollbar.config(command=self.files_text.yview)

    # Grid columns for centering
    self.form_frame.grid_columnconfigure(0, weight=1)
    self.form_frame.grid_columnconfigure(1, weight=1)

    # SSH Config Checkbox
    self.ssh_boolean = tk.BooleanVar(value=True)
    self.config_checkbox = tk.Checkbutton(
    self.form_frame,
    text="Use SSH Config",
    variable=self.ssh_boolean,
    command=self.on_toggle_ssh,
    font=font
    )
    self.config_checkbox.grid(row=0, column=1, padx=5, pady=5)

    # Username
    tk.Label(self.form_frame, text="User:", font=font).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    self.username_entry = tk.Entry(self.form_frame, width=40, font=font)
    self.username_entry.insert(0, "marcy")
    self.username_entry.grid(row=1, column=1, padx=5, pady=5)

    # Server IP
    tk.Label(self.form_frame, text="Server-Ip:", font=font).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    self.server_entry = tk.Entry(self.form_frame, width=40, font=font)
    self.server_entry.insert(0, "192.168.1.33")
    self.server_entry.grid(row=2, column=1, padx=5, pady=5)

    # SSH Config Dropdown
    options = getSSHConfigs()
    if not options:
      options = ["No SSH Configs Found"]
    
    self.selected_host = tk.StringVar(value=options[0])
    tk.Label(self.form_frame, text="SSH Host:", font=font).grid(row=3, column=0, sticky="e", padx=5, pady=5)
    self.ssh_dropdown = tk.OptionMenu(self.form_frame, self.selected_host, *options)
    self.ssh_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    # File Path
    tk.Label(self.form_frame, text="File-Path:", font=font).grid(row=4, column=0, sticky="e", padx=5, pady=5)
    self.filepath_entry = tk.Entry(self.form_frame, width=40, font=font)
    self.filepath_entry.insert(0, "/home/marcy/main_dir/")
    self.filepath_entry.grid(row=4, column=1, padx=5, pady=5)

    # Upload Button
    self.upload_file_button = tk.Button(main_frame, text="Upload Files", command=self.upload_files, font=font, state="disabled")
    self.upload_file_button.pack(pady=20)

    # Switch to Download Page
    tk.Button(main_frame, text="Go to Download Page", font=font, command=lambda: controller.show_page(DownloadPage)).pack(pady=10)

    self.username_entry.bind("<KeyRelease>", self.check_entries)
    self.server_entry.bind("<KeyRelease>", self.check_entries)
    self.filepath_entry.bind("<KeyRelease>", self.check_entries)

    # Initialize SSH toggle state
    self.on_toggle_ssh()

  def get_files(self):
    self.controller.filenames = list(filedialog.askopenfilenames())
    self.files_text.config(state="normal")
    self.files_text.delete("1.0", "end")  # clear old text
    if self.controller.filenames:
      display_text = "\n".join(self.controller.filenames)
      self.files_text.insert("1.0", display_text)
      self.check_entries()
    else:
      self.files_text.insert("1.0", "No files selected")
      self.check_entries()
    self.files_text.config(state="disabled")  # read-only

  def upload_files(self):
    if not self.controller.filenames:
      return

    files_string = " ".join(f'"{f}"' for f in self.controller.filenames)

    # If SSH checkbox is checked, use selected SSH host from dropdown
    if self.ssh_boolean.get():
      target_folder = f"{self.selected_host.get()}:{self.filepath_entry.get()}"
    else:
      target_folder = f"{self.username_entry.get()}@{self.server_entry.get()}:{self.filepath_entry.get()}"

    pprint(files_string)
    returnvalue = os.system(f"scp {files_string} {target_folder}")
    if returnvalue == 0:
      messagebox.showinfo("Upload Complete", "Files have been successfully uploaded.")
      print("Finished uploading.")
    else:
      messagebox.showerror("Upload Failed", f"SCP returned error code {returnvalue}")
      print(f"SCP returned error code {returnvalue}")


  def check_entries(self, *args):
    if self.username_entry.get() and self.server_entry.get() and self.filepath_entry.get() and self.controller.filenames:
      self.upload_file_button.config(state="normal")
    else:
      self.upload_file_button.config(state="disabled")
  
  def on_toggle_ssh(self):
    if self.ssh_boolean.get():
      # Disable fields you don’t want editable
      self.username_entry.config(state="disabled")
      self.server_entry.config(state="disabled")
      
      # Enable dropdown if needed
      self.ssh_dropdown.config(state="normal")
    else:
      # Re-enable normal fields
      self.username_entry.config(state="normal")
      self.server_entry.config(state="normal")
      
      # Optionally disable dropdown
      self.ssh_dropdown.config(state="disabled")

class DownloadPage(tk.Frame):
  def __init__(self, parent, controller):
    super().__init__(parent)
    self.controller = controller
    font = ("Arial", 14)

    # Make this page fill container
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)

    # Main frame centered
    main_frame = tk.Frame(self)
    main_frame.grid(row=0, column=0)

    tk.Label(main_frame, text="Download Files", font=("Arial", 18)).pack(pady=10)

    #Get file button
    self.get_file_button = tk.Button(main_frame, text="Select Folder", command=self.get_folder, font=font)
    self.get_file_button.pack(pady=10)

    # Form frame for entries
    self.form_frame = tk.Frame(main_frame)
    self.form_frame.pack(pady=10)

    # Grid columns for centering
    self.form_frame.grid_columnconfigure(0, weight=1)
    self.form_frame.grid_columnconfigure(1, weight=1)

    # SSH Config Checkbox
    self.ssh_boolean = tk.BooleanVar(value=True)
    self.config_checkbox = tk.Checkbutton(
      self.form_frame,
      text="Use SSH Config",
      variable=self.ssh_boolean,
      command=self.on_toggle_ssh,
      font=font
    )
    self.config_checkbox.grid(row=0, column=0, columnspan=2, pady=5)

    # Username
    tk.Label(self.form_frame, text="User:", font=font).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    self.username_entry = tk.Entry(self.form_frame, width=40, font=font)
    self.username_entry.insert(0, "marcy")
    self.username_entry.grid(row=1, column=1, padx=5, pady=5)

    # Server IP
    tk.Label(self.form_frame, text="Server-Ip:", font=font).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    self.server_entry = tk.Entry(self.form_frame, width=40, font=font)
    self.server_entry.insert(0, "192.168.1.33")
    self.server_entry.grid(row=2, column=1, padx=5, pady=5)

    # SSH Config Dropdown
    options = getSSHConfigs()
    if not options:
      options = ["No SSH Configs Found"]
    self.selected_host = tk.StringVar(value=options[0])
    tk.Label(self.form_frame, text="SSH Host:", font=font).grid(row=3, column=0, sticky="e", padx=5, pady=5)
    self.ssh_dropdown = tk.OptionMenu(self.form_frame, self.selected_host, *options)
    self.ssh_dropdown.grid(row=3, column=1, padx=5, pady=5)
    self.ssh_dropdown.config(state="disabled")  # disabled by default

    # Remote File Path
    tk.Label(self.form_frame, text="Remote File-Path:", font=font).grid(row=4, column=0, sticky="e", padx=5, pady=5)
    self.remote_path_entry = tk.Entry(self.form_frame, width=40, font=font)
    self.remote_path_entry.insert(0, "/home/marcy/main_dir/")
    self.remote_path_entry.grid(row=4, column=1, padx=5, pady=5)

    # Local Save Path
    tk.Label(self.form_frame, text="Local Save Path:", font=font).grid(row=5, column=0, sticky="e", padx=5, pady=5)
    self.local_path_entry = tk.Entry(self.form_frame, width=40, font=font)
    self.local_path_entry.insert(0, os.getcwd())
    self.local_path_entry.grid(row=5, column=1, padx=5, pady=5)

    # Download Button
    self.download_button = tk.Button(main_frame, text="Download File", command=self.download_files, font=font)
    self.download_button.pack(pady=20)

    # Switch to Upload Page
    tk.Button(main_frame, text="Go to Upload Page", font=font, command=lambda: controller.show_page(UploadPage)).pack(pady=10)

    # Bind entries to check changes if needed
    self.username_entry.bind("<KeyRelease>", self.check_entries)
    self.server_entry.bind("<KeyRelease>", self.check_entries)
    self.remote_path_entry.bind("<KeyRelease>", self.check_entries)
    self.local_path_entry.bind("<KeyRelease>", self.check_entries)

    # Initialize SSH toggle state
    self.on_toggle_ssh()

  # Toggle fields depending on SSH checkbox
  def on_toggle_ssh(self):
    if self.ssh_boolean.get():
      self.username_entry.config(state="disabled")
      self.server_entry.config(state="disabled")
      self.ssh_dropdown.config(state="normal")
    else:
      self.username_entry.config(state="normal")
      self.server_entry.config(state="normal")
      self.ssh_dropdown.config(state="disabled")

  # Placeholder for download function
  def download_files(self):
    files = self.remote_path_entry.get()
    if self.ssh_boolean.get():
      target = f"{self.selected_host.get()}:{files}"
    else:
      target = f"{self.username_entry.get()}@{self.server_entry.get()}:{files}"
    local_path = self.local_path_entry.get()


    returnvalue = os.system(f"scp {target} {local_path}")
    if returnvalue == 0:
      messagebox.showinfo("Download Complete", "Files have been successfully downloaded.")
      print("Finished downloading.")
    else:
      messagebox.showerror("Download Failed", f"SCP returned error code {returnvalue}")
      print(f"SCP returned error code {returnvalue}")

  # Optional entry check function
  def check_entries(self, *args):
    if (self.username_entry.get() and self.server_entry.get() and
      self.remote_path_entry.get() and self.local_path_entry.get()):
      self.download_button.config(state="normal")
    else:
      self.download_button.config(state="disabled")

  def get_folder(self):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
      self.local_path_entry.delete(0, tk.END)
      self.local_path_entry.insert(0, folder_selected)

if __name__ == "__main__":
  root = tk.Tk()
  app = UploadDownloadApp(root)
  root.mainloop()
