import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import time
import main
import cv2
import sys
import datetime
import sys
import os


# ================== LOGGING SUPPORT ==================
class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, text):
        for f in self.files:
            f.write(text)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()


original_stdout = sys.stdout
original_stderr = sys.stderr
current_log_file = None
# =====================================================


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS   # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("OMR Sheet Evaluator")
        self.root.geometry("600x600")
        self.root.config(bg="#add8e6")

        # ---- LOGO ----
        self.logo_img = tk.PhotoImage(file=resource_path("logo.png"))

        self.is_first_page = True
        self.certificate_var = tk.StringVar(value="A")

        self.reset_state()
        self.create_heading_label()
        self.display_authentication()




    # ---------------- STATE ----------------
    def reset_state(self):
        self.folder_path = ""
        self.answer_key_path = ""
        self.current_output_path = ""

    # ---------------- LOGGING PER BATCH ----------------
    def setup_batch_logging(self):
        global current_log_file

        logs_dir = os.path.join(self.current_output_path, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        log_path = os.path.join(
            logs_dir,
            f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        if current_log_file:
            current_log_file.close()

        current_log_file = open(log_path, "w")

        sys.stdout = Tee(original_stdout, current_log_file)
        sys.stderr = Tee(original_stderr, current_log_file)

        print("=== NEW BATCH STARTED ===")
        print("Output folder:", self.current_output_path)


    def reset_logging(self):
        global current_log_file
        if current_log_file:
            current_log_file.close()
            current_log_file = None
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    # ---------------- AUTH ----------------
    def display_authentication(self):
        self.btn_authenticate = tk.Button(
            self.root, text="Start", command=self.authenticate, width=10
        )
        self.btn_authenticate.pack(pady=10)

    def authenticate(self):
        self.clear_screen()
        self.is_first_page = False
        self.create_heading_label()
        self.initialize_app()

    # ---------------- CERTIFICATE ----------------
    def initialize_app(self):
        self.label = tk.Label(
            self.root, text="Select Certificate Type:",
            bg="#add8e6", font=("Arial", 11)
        )
        self.label.pack(pady=10)

        self.radio_a = tk.Radiobutton(
            self.root, text="A Certificate",
            variable=self.certificate_var, value="A",
            bg="#add8e6"
        )
        self.radio_b = tk.Radiobutton(
            self.root, text="B Certificate",
            variable=self.certificate_var, value="B",
            bg="#add8e6"
        )
        self.radio_c = tk.Radiobutton(
            self.root, text="C Certificate",
            variable=self.certificate_var, value="C",
            bg="#add8e6"
        )

        self.radio_a.pack()
        self.radio_b.pack()
        self.radio_c.pack()

        self.btn_start = tk.Button(
            self.root, text="Start", command=self.start, width=10
        )
        self.btn_start.pack(pady=15)

    # ---------------- MARKING ----------------
    def start(self):
        self.clear_screen()
        self.create_heading_label()

        self.label = tk.Label(
            self.root, text="Enter Marking Scheme for:",
            bg="#add8e6", font=("Arial", 11)
        )
        self.label.pack(pady=10)

        self.input_frame = ttk.LabelFrame(self.root)
        self.input_frame.pack(padx=10, pady=10)

        cert = self.certificate_var.get()
        default_correct = 2.5 if cert == "A" else 2.0

        self.create_entry("Correct Answers:", default_correct, 0)
        self.create_entry("Incorrect Answers:", -0.25, 1)
        self.create_entry("Unattempted:", 0, 2)

        ttk.Button(self.root, text="Submit", command=self.mark_scheme).pack(pady=10)

    def create_entry(self, label, default, row):
        ttk.Label(self.input_frame, text=label).grid(row=row, column=0, padx=5, pady=5)
        e = ttk.Entry(self.input_frame)
        e.insert(0, default)
        e.grid(row=row, column=1, padx=5, pady=5)
        setattr(self, f"text_field{row+1}", e)

    # ---------------- THRESHOLD ----------------
    def mark_scheme(self):
        self.input1 = float(self.text_field1.get())
        self.input2 = float(self.text_field2.get())
        self.input3 = float(self.text_field3.get())

        self.clear_screen()
        self.create_heading_label()

        self.label = tk.Label(
            self.root,
            text="Enter a threshold for response evaluation (30–50):",
            bg="#add8e6", font=("Arial", 11)
        )
        self.label.pack(pady=10)

        self.text_field = tk.Entry(self.root)
        self.text_field.insert(0, 35)
        self.text_field.pack()

        tk.Button(self.root, text="Next", command=self.threshold).pack(pady=10)

    def threshold(self):
        self.thresh = int(self.text_field.get())
        self.clear_screen()
        self.create_heading_label()
        self.output_folder_screen()

    # ---------------- OUTPUT FOLDER ----------------
    def output_folder_screen(self):
        self.label = tk.Label(
            self.root, text="Enter Output Folder Name:",
            bg="#add8e6", font=("Arial", 11)
        )
        self.label.pack(pady=10)

        self.output_name_entry = tk.Entry(self.root)
        self.output_name_entry.pack(pady=5)

        tk.Button(self.root, text="Next", command=self.set_output_folder).pack(pady=10)

    def set_output_folder(self):
        name = self.output_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Output folder name required")
            return

        base = os.path.join(os.getcwd(), "output")
        self.current_output_path = os.path.join(base, name)

        os.makedirs(self.current_output_path, exist_ok=True)
        os.makedirs(os.path.join(self.current_output_path, "evaluated"), exist_ok=True)
        os.makedirs(os.path.join(self.current_output_path, "non_evaluated"), exist_ok=True)

        self.setup_batch_logging()

        self.clear_screen()
        self.create_heading_label()
        self.file_selection()

    # ---------------- FILE SELECTION ----------------
    def file_selection(self):
        self.label = tk.Label(
            self.root,
            text="Select the desired Scanned OMRs and Answer Key Files to evaluate:",
            bg="#add8e6", font=("Arial", 11)
        )
        self.label.pack(pady=10)

        self.btn_browse1 = tk.Button(
            self.root, text="Upload OMRs Folder",
            command=self.browse_folder, width=15
        )
        self.btn_browse1.pack(pady=10)

        self.btn_browse2 = tk.Button(
            self.root, text="Upload Answer Key",
            command=self.browse_answerkey, width=15
        )
        self.btn_browse2.pack(pady=10)

        self.btn_next2 = tk.Button(
            self.root, text="Next",
            command=self.Next_Evaluate,
            state="disabled", width=12
        )
        self.btn_next2.pack(pady=10)

    def browse_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            count = len(os.listdir(self.folder_path))
            messagebox.showinfo("File Count", f"Number of files in folder: {count}")
            self.label.config(text=f"OMRs Folder: {self.folder_path}", fg="blue")
            self.check_next()

    def browse_answerkey(self):
        self.answer_key_path = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx;*.xls")]
        )
        if self.answer_key_path:
            self.label.config(text=f"Answer Key: {self.answer_key_path}", fg="blue")
            self.check_next()

    def check_next(self):
        if self.folder_path and self.answer_key_path:
            self.btn_next2.config(state="normal")

    # ---------------- MODES (UNCHANGED) ----------------
    def Next_Evaluate(self):
        self.clear_screen()
        self.create_heading_label()

        tk.Label(
            self.root, text="Select the Desired Mode of Evaluation:",
            bg="#add8e6", font=("Arial", 11)
        ).pack(pady=10)

        # tk.Button(self.root, text="Fast Mode", command=self.evaluate_fast).pack(pady=10)
        # tk.Button(self.root, text="Visibility Mode", command=self.evaluate_fast).pack(pady=10)
        # tk.Button(self.root, text="Correction Mode", command=self.evaluate_fast).pack(pady=10)

        tk.Button(self.root, text="Fast Mode", command=self.evaluate_fast).pack(pady=10)
        tk.Button(self.root, text="Visibility Mode", command=self.evaluate_visibility).pack(pady=10)
        tk.Button(self.root, text="Correction Mode", command=self.evaluate_correction).pack(pady=10)

    # ---------------- EVALUATION ----------------
    def evaluate_fast(self):
        print("Evaluation started")
        start = time.time()

        evaluated = os.path.join(self.current_output_path, "evaluated")
        non_eval = os.path.join(self.current_output_path, "non_evaluated")

        cert = self.certificate_var.get()
        num_q = 140 if cert == "A" else 175

        results1, results2 = [], []
        idx = 1

        for file in os.listdir(self.folder_path):
            if file.lower().endswith((".jpg", ".png", ".tif")):
                r1, r2, img_in, img_out = main.process_omr_sheet(
                    os.path.join(self.folder_path, file),
                    file, idx,
                    self.input1, self.input2, self.input3,
                    self.thresh,
                    self.answer_key_path,
                    num_q, cert
                )

                if not r1:
                    shutil.copy(os.path.join(self.folder_path, file), non_eval)
                    continue

                results1.append(r1)
                results2.append(r2)

                reg = r1[1]
                cv2.imwrite(os.path.join(evaluated, f"{reg}_inp.tif"), img_in)
                cv2.imwrite(os.path.join(evaluated, f"{reg}_out.tif"), img_out)
                idx += 1


        # pd.DataFrame(results1).to_excel(
        #     os.path.join(self.current_output_path, "abstract.xlsx"), index=False
        # )
        # pd.DataFrame(results2).to_excel(
        #     os.path.join(self.current_output_path, "detailed.xlsx"), index=False
        # )
        df1 = pd.DataFrame(results1, columns=["S.No","Enrollment No", "Set", "AdmitCard No", "CorrectAns", "IncorrectAns", "Left","paper1","paper2","paper3","paper4", "Score","Grade"])
        df2 = pd.DataFrame(results2)
        columns = ['S.No', 'Enrollment No','AdmitCard No','Set']
        
        columns.extend(['Q{}'.format(i) for i in range(1,num_q+1)])
        columns.extend(['Score','Grade'])
        df2.columns = columns
        # Write the DataFrame to an Excel file
        # output_file1 = os.path.join(output_folder, "output1.xlsx")
        # output_file2 = os.path.join(output_folder, "output2.xlsx")
        df1.to_excel(
            os.path.join(self.current_output_path, "abstract.xlsx"), index=False
        )
        df2.to_excel(
            os.path.join(self.current_output_path, "detailed.xlsx"), index=False
        )
        print("Time taken:", time.time() - start)
        self.finish()


    def evaluate_visibility(self):
        start_time = time.time()

        evaluated = os.path.join(self.current_output_path, "evaluated")
        non_eval = os.path.join(self.current_output_path, "non_evaluated")

        all_results1 = []
        all_results2 = []
        idx = 1

        selected_certificate = self.certificate_var.get()
        num_questions = 140 if selected_certificate == "A" else 175

        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith((".jpg", ".png", ".tif")):

                results1, results2, imgInput, imgOutput = main.process_omr_sheet(
                    os.path.join(self.folder_path, filename),
                    filename, idx,
                    self.input1, self.input2, self.input3,
                    self.thresh,
                    self.answer_key_path,
                    num_questions,
                    selected_certificate
                )

                if not results1:
                    shutil.copy(os.path.join(self.folder_path, filename), non_eval)
                    continue

                cv2.imshow("evaluated_image", imgOutput)
                cv2.waitKey(0)

                all_results1.append(results1)
                all_results2.append(results2)

                regno = results1[1]
                cv2.imwrite(os.path.join(evaluated, f"{regno}_inp.tif"), imgInput)
                cv2.imwrite(os.path.join(evaluated, f"{regno}_out.tif"), imgOutput)

                idx += 1

        # Save results
        df1 = pd.DataFrame(all_results1, columns=[
            "S.No","Enrollment No","Set","AdmitCard No",
            "CorrectAns","IncorrectAns","Left",
            "paper1","paper2","paper3","paper4",
            "Score","Grade"
        ])

        df2 = pd.DataFrame(all_results2)
        columns = ['S.No','Enrollment No','AdmitCard No','Set']
        columns.extend([f"Q{i}" for i in range(1, num_questions+1)])
        columns.extend(['Score','Grade'])
        df2.columns = columns

        df1.to_excel(os.path.join(self.current_output_path, "abstract.xlsx"), index=False)
        df2.to_excel(os.path.join(self.current_output_path, "detailed.xlsx"), index=False)

        print("Time Taken:", time.time() - start_time)

        self.finish()


    def evaluate_correction(self):
        start_time = time.time()

        evaluated = os.path.join(self.current_output_path, "evaluated")
        non_eval = os.path.join(self.current_output_path, "non_evaluated")

        all_results1 = []
        all_results2 = []
        idx = 1

        selected_certificate = self.certificate_var.get()
        num_questions = 140 if selected_certificate == "A" else 175

        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith((".jpg", ".png", ".tif")):

                self.root.iconify()

                results1, results2, imgInput, imgOutput = main.process_omr_sheet(
                    os.path.join(self.folder_path, filename),
                    filename, idx,
                    self.input1, self.input2, self.input3,
                    self.thresh,
                    self.answer_key_path,
                    num_questions,
                    selected_certificate
                )

                if not results1:
                    if imgInput is not None:
                        cv2.imshow("Original_Image", imgInput)
                        cv2.waitKey(0)

                    shutil.copy(os.path.join(self.folder_path, filename), non_eval)
                    self.root.deiconify()
                    continue

                cv2.imshow("Original_Image", imgInput)
                cv2.imshow("Evaluated_Image", imgOutput)

                confirm = messagebox.askokcancel(
                    "Confirmation",
                    "Are you sure you want to consider this Data?"
                )

                if confirm:
                    all_results1.append(results1)
                    all_results2.append(results2)

                    regno = results1[1]
                    cv2.imwrite(os.path.join(evaluated, f"{regno}_inp.tif"), imgInput)
                    cv2.imwrite(os.path.join(evaluated, f"{regno}_out.tif"), imgOutput)

                    idx += 1
                else:
                    regno = results1[1]
                    cv2.imwrite(os.path.join(non_eval, f"{regno}.tif"), imgInput)

                cv2.destroyAllWindows()
                self.root.deiconify()

        print("Time Taken:", time.time() - start_time)

        # Save results
        df1 = pd.DataFrame(all_results1, columns=[
            "S.No","Enrollment No","Set","AdmitCard No",
            "CorrectAns","IncorrectAns","Left",
            "paper1","paper2","paper3","paper4",
            "Score","Grade"
        ])

        df2 = pd.DataFrame(all_results2)
        columns = ['S.No','Enrollment No','AdmitCard No','Set']
        columns.extend([f"Q{i}" for i in range(1, num_questions+1)])
        columns.extend(['Score','Grade'])
        df2.columns = columns

        df1.to_excel(os.path.join(self.current_output_path, "abstract.xlsx"), index=False)
        df2.to_excel(os.path.join(self.current_output_path, "detailed.xlsx"), index=False)

        self.finish()
    # ---------------- FINISH ----------------
    def finish(self):
        proceed = messagebox.askyesno(
            "Completed",
            "Evaluation complete.\nDo you want to process more files?"
        )

        self.reset_logging()

        if proceed:
            self.clear_screen()
            self.reset_state()
            self.is_first_page = True
            self.create_heading_label()
            self.display_authentication()
        else:
            self.root.quit()

    # ---------------- UI HELPERS ----------------
    def clear_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

    def create_heading_label(self):
        logo_label = tk.Label(self.root, image=self.logo_img, bg="#add8e6")
        logo_label.pack(pady=15)

        heading_text = (
            "NCC OMR Sheet Evaluator\n"
            "GOI CopyRight No.: SW-17881/2023\n"
            "© MNNIT Allahabad\n\n"
            "Designed for: NCC GRP HQ PRAYAGRAJ"
        )

        if self.is_first_page:
            heading_text += (
                "\n\nDesigned at:\n"
                "1 UP CTR NCC, Prayagraj GRP, U.P.\n\n"
                "Contact Person:\n"
                "Lt (Dr) Divya Kumar\n"
                "+91 7905595695"
            )

        tk.Label(
            self.root, text=heading_text,
            font=("Arial", 11, "bold"),
            bg="#add8e6"
        ).pack(pady=10)


# ---------------- RUN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

