import os
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox

# -------- VALIDATION LOG --------
def write_log(output_folder, log_data):
    log_path = os.path.join(output_folder, "CKYC_ERROR_LOG.txt")
    with open(log_path, "w") as f:
        for line in log_data:
            f.write(line + "\n")
    return log_path


# -------- CREATE LRN ZIP --------
def create_lrn_zip(lrn, files, temp_dir):
    zip_path = os.path.join(temp_dir, f"{lrn}.zip")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in files:
            z.write(file, os.path.basename(file))

    return zip_path


# -------- CORE PROCESS --------
def process_ckyc(base_name, txt_file, images_folder, output_folder):

    temp_dir = os.path.join(output_folder, "temp_ckyc")
    os.makedirs(temp_dir, exist_ok=True)

    lrn_map = {}
    log = []

    # Group files by LRN
    for file in os.listdir(images_folder):
        if "_" in file:
            lrn = file.split("_")[0]
            full_path = os.path.join(images_folder, file)
            lrn_map.setdefault(lrn, []).append(full_path)

    lrn_zips = []

    # Validate POA/POI
    for lrn, files in lrn_map.items():
        has_poa = any("_POA" in f for f in files)
        has_poi = any("_POI" in f for f in files)

        if not has_poa:
            log.append(f"{lrn} - Missing POA")
        if not has_poi:
            log.append(f"{lrn} - Missing POI")

        zip_file = create_lrn_zip(lrn, files, temp_dir)
        lrn_zips.append(zip_file)

    # Main folder
    main_folder = os.path.join(temp_dir, base_name)
    os.makedirs(main_folder, exist_ok=True)

    shutil.copy(txt_file, os.path.join(main_folder, f"{base_name}.txt"))

    # Move LRN ZIPs
    for z in lrn_zips:
        shutil.move(z, os.path.join(main_folder, os.path.basename(z)))

    # Final ZIP
    final_zip = os.path.join(output_folder, f"{base_name}.zip")

    with zipfile.ZipFile(final_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(main_folder):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, temp_dir)
                z.write(full_path, rel_path)

    # Cleanup TEMP
    shutil.rmtree(temp_dir)

    # Write error log if any
    log_file = None
    if log:
        log_file = write_log(output_folder, log)

    return final_zip, log_file


# -------- GUI --------
class CKYCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CKYC ZIP Tool PRO")

        self.txt_file = ""
        self.img_folder = ""
        self.output_folder = ""

        tk.Label(root, text="CKYC ZIP TOOL PRO", font=("Arial", 14)).pack(pady=10)

        tk.Button(root, text="Select TXT File", command=self.select_txt).pack(pady=5)
        tk.Button(root, text="Select Images Folder", command=self.select_img).pack(pady=5)
        tk.Button(root, text="Select Output Folder", command=self.select_output).pack(pady=5)

        tk.Label(root, text="ZIP Name").pack()
        self.name_entry = tk.Entry(root)
        self.name_entry.pack(pady=5)

        self.status = tk.Label(root, text="", fg="blue")
        self.status.pack(pady=5)

        tk.Button(root, text="CREATE ZIP", bg="green", fg="white", command=self.run).pack(pady=15)

    def select_txt(self):
        self.txt_file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])

    def select_img(self):
        self.img_folder = filedialog.askdirectory()

    def select_output(self):
        self.output_folder = filedialog.askdirectory()

    def run(self):

        name = self.name_entry.get()

        if not all([self.txt_file, self.img_folder, self.output_folder, name]):
            messagebox.showerror("Error", "All fields required")
            return

        self.status.config(text="Processing...")

        zip_path, log_file = process_ckyc(
            name,
            self.txt_file,
            self.img_folder,
            self.output_folder
        )

        msg = f"ZIP Created:\n{zip_path}"

        if log_file:
            msg += f"\n\nErrors found:\n{log_file}"

        self.status.config(text="Done")
        messagebox.showinfo("Completed", msg)


# -------- RUN APP --------
if __name__ == "__main__":
    root = tk.Tk()
    app = CKYCApp(root)
    root.mainloop()
