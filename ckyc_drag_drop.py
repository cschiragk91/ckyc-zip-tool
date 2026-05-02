import os
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox

# -------- CORE LOGIC --------
def create_lrn_zip(lrn, files, temp_dir):
    zip_path = os.path.join(temp_dir, f"{lrn}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in files:
            z.write(file, os.path.basename(file))
    return zip_path


def process_ckyc(base_name, txt_file, images_folder, output_folder):
    temp_dir = os.path.join(output_folder, "temp_ckyc")
    os.makedirs(temp_dir, exist_ok=True)

    lrn_map = {}

    for file in os.listdir(images_folder):
        if "_" in file:
            lrn = file.split("_")[0]
            full_path = os.path.join(images_folder, file)
            lrn_map.setdefault(lrn, []).append(full_path)

    lrn_zips = []
    for lrn, files in lrn_map.items():
        zip_file = create_lrn_zip(lrn, files, temp_dir)
        lrn_zips.append(zip_file)

    main_folder = os.path.join(temp_dir, base_name)
    os.makedirs(main_folder, exist_ok=True)

    shutil.copy(txt_file, os.path.join(main_folder, f"{base_name}.txt"))

    for z in lrn_zips:
        shutil.move(z, os.path.join(main_folder, os.path.basename(z)))

    final_zip = os.path.join(output_folder, f"{base_name}.zip")
    with zipfile.ZipFile(final_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(main_folder):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, temp_dir)
                z.write(full_path, rel_path)

    shutil.rmtree(temp_dir)
    return final_zip


# -------- GUI --------
class CKYCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CKYC ZIP Creator")

        self.txt_file = ""
        self.img_folder = ""
        self.output_folder = ""

        tk.Label(root, text="CKYC ZIP Tool", font=("Arial", 14)).pack(pady=10)

        tk.Button(root, text="Select TXT File", command=self.select_txt).pack(pady=5)
        tk.Button(root, text="Select Images Folder", command=self.select_img).pack(pady=5)
        tk.Button(root, text="Select Output Folder", command=self.select_output).pack(pady=5)

        tk.Label(root, text="ZIP Name").pack()
        self.name_entry = tk.Entry(root)
        self.name_entry.pack(pady=5)

        tk.Button(root, text="Create ZIP", bg="green", fg="white", command=self.run).pack(pady=15)

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

        zip_path = process_ckyc(name, self.txt_file, self.img_folder, self.output_folder)
        messagebox.showinfo("Success", f"ZIP Created:\n{zip_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CKYCApp(root)
    root.mainloop()
