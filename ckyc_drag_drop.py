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

            z.write(
                file,
                os.path.basename(file)
            )

    return zip_path


# -------- CORE PROCESS --------
def process_ckyc(txt_file, images_folder, output_folder):

    # ZIP name from TXT filename
    base_name = os.path.splitext(
        os.path.basename(txt_file)
    )[0]

    temp_dir = os.path.join(
        output_folder,
        "temp_ckyc"
    )

    os.makedirs(temp_dir, exist_ok=True)

    log = []
    lrn_zips = []

    # -------- SCAN LRN FOLDERS --------
    for folder_name in os.listdir(images_folder):

        folder_path = os.path.join(
            images_folder,
            folder_name
        )

        # Process only folders
        if os.path.isdir(folder_path):

            lrn = folder_name
            files_list = []

            # Read all files inside LRN folder
            for file in os.listdir(folder_path):

                full_path = os.path.join(
                    folder_path,
                    file
                )

                if os.path.isfile(full_path):
                    files_list.append(full_path)

            # Skip empty folders
            if not files_list:
                continue

            # -------- VALIDATE POA --------
            has_poa = any(
                "POA" in file.upper()
                for file in os.listdir(folder_path)
            )

            if not has_poa:
                log.append(f"{lrn} - Missing POA")

            # -------- CREATE LRN ZIP --------
            zip_file = create_lrn_zip(
                lrn,
                files_list,
                temp_dir
            )

            lrn_zips.append(zip_file)

    # -------- CREATE MAIN FOLDER --------
    main_folder = os.path.join(
        temp_dir,
        base_name
    )

    os.makedirs(main_folder, exist_ok=True)

    # Copy TXT file
    shutil.copy(
        txt_file,
        os.path.join(
            main_folder,
            f"{base_name}.txt"
        )
    )

    # Move all LRN ZIPs
    for z in lrn_zips:

        shutil.move(
            z,
            os.path.join(
                main_folder,
                os.path.basename(z)
            )
        )

    # -------- CREATE FINAL ZIP --------
    final_zip = os.path.join(
        output_folder,
        f"{base_name}.zip"
    )

    with zipfile.ZipFile(
        final_zip,
        'w',
        zipfile.ZIP_DEFLATED
    ) as z:

        for root, dirs, files in os.walk(main_folder):

            for f in files:

                full_path = os.path.join(root, f)

                rel_path = os.path.relpath(
                    full_path,
                    temp_dir
                )

                z.write(
                    full_path,
                    rel_path
                )

    # -------- CLEAN TEMP --------
    shutil.rmtree(temp_dir)

    # -------- WRITE ERROR LOG --------
    log_file = None

    if log:
        log_file = write_log(
            output_folder,
            log
        )

    return final_zip, log_file


# -------- GUI --------
class CKYCApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "CKYC ZIP Tool PRO"
        )

        self.root.geometry("450x350")

        self.txt_file = ""
        self.img_folder = ""
        self.output_folder = ""

        # -------- TITLE --------
        tk.Label(
            root,
            text="CKYC ZIP TOOL PRO",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        # -------- TXT BUTTON --------
        tk.Button(
            root,
            text="Select TXT File",
            width=30,
            command=self.select_txt
        ).pack(pady=10)

        # -------- IMAGE FOLDER BUTTON --------
        tk.Button(
            root,
            text="Select Main Images Folder",
            width=30,
            command=self.select_img
        ).pack(pady=10)

        # -------- OUTPUT BUTTON --------
        tk.Button(
            root,
            text="Select Output Folder",
            width=30,
            command=self.select_output
        ).pack(pady=10)

        # -------- STATUS --------
        self.status = tk.Label(
            root,
            text="",
            fg="blue"
        )

        self.status.pack(pady=15)

        # -------- CREATE ZIP BUTTON --------
        tk.Button(
            root,
            text="GENERATE ZIP FILE",
            width=25,
            height=2,
            bg="green",
            fg="white",
            command=self.run
        ).pack(pady=20)

    # -------- SELECT TXT --------
    def select_txt(self):

        self.txt_file = filedialog.askopenfilename(
            filetypes=[
                ("Text Files", "*.txt")
            ]
        )

    # -------- SELECT IMAGE FOLDER --------
    def select_img(self):

        self.img_folder = filedialog.askdirectory()

    # -------- SELECT OUTPUT --------
    def select_output(self):

        self.output_folder = filedialog.askdirectory()

    # -------- RUN --------
    def run(self):

        if not all([
            self.txt_file,
            self.img_folder,
            self.output_folder
        ]):

            messagebox.showerror(
                "Error",
                "Please select all required fields"
            )

            return

        self.status.config(
            text="Processing..."
        )

        try:

            zip_path, log_file = process_ckyc(
                self.txt_file,
                self.img_folder,
                self.output_folder
            )

            msg = (
                f"ZIP Created Successfully\n\n"
                f"{zip_path}"
            )

            if log_file:

                msg += (
                    f"\n\nPOA Errors Found:\n"
                    f"{log_file}"
                )

            self.status.config(
                text="Done"
            )

            messagebox.showinfo(
                "Completed",
                msg
            )

        except Exception as e:

            self.status.config(
                text="Failed"
            )

            messagebox.showerror(
                "Error",
                str(e)
            )


# -------- START APP --------
if __name__ == "__main__":

    root = tk.Tk()

    app = CKYCApp(root)

    root.mainloop()
