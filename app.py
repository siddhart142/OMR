import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import pandas as pd
import time
import main
import cv2
import math
import uuid
import datetime
import sys

output_log_path = "output_log.txt"

# Save the original standard output and error streams
original_stdout = sys.stdout
original_stderr = sys.stderr

# Open a new file for writing
log_file = open(output_log_path, "w")

# Redirect standard output and error to the file
# sys.stdout = log_file
# sys.stderr = log_file



output_file1 = "abstract.xlsx"
output_file2 = 'detailed.xlsx'

# Get the parent directory
parent_dir = os.getcwd()

output_folder = "output"
output_path = os.path.join(parent_dir, output_folder)

# Create the "output" folder
os.makedirs(output_path, exist_ok=True)

# Create the "evaluated" and "non_evaluated" folders inside the "output" folder
evaluated_folder = os.path.join(output_path, "evaluated")
non_evaluated_folder = os.path.join(output_path, "non_evaluated")

os.makedirs(evaluated_folder, exist_ok=True)
os.makedirs(non_evaluated_folder, exist_ok=True)

# Create folders
# Define a Tee class to duplicate the output to both the terminal and a file
class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, text):
        for file in self.files:
            file.write(str(text))

    def flush(self):
        for file in self.files:
            file.flush()

sys.stdout = Tee(sys.stdout, log_file)
sys.stderr = Tee(sys.stderr, log_file)

class App:
    def __init__(self, root):
        self.root = root
        self.logo_img = tk.PhotoImage(file="logo.png")
        self.is_first_page = True
        self.create_heading_label()
        # NCC OMR Sheet Evaluator
        self.root.title("OMR Sheet Evaluator")
        self.root.geometry("600x600")
        self.folder_path = ""
        self.answer_key_path = ""
        self.certificate_var = tk.StringVar()  # Variable to store the selected certificate
        self.certificate_var.set("A")  # Default certificate selection

        # Set the background color to a calm blue
        self.root.config(bg="#add8e6")

        # Get the MAC address of the user's device
        # datee = self.check_execution_date()
        # if datee:
        # self.user_mac = self.get_mac_address()

            # Display authentication screen
        self.display_authentication()

    def get_mac_address(self):
        mac_address = hex(uuid.getnode())[2:]  # Get MAC address as hex string, remove '0x' prefix
        mac_address = mac_address.zfill(12)  # Ensure MAC address has 12 digits
        extracted_part = mac_address[4:6].upper() + mac_address[10:].upper()  # Extract 'a6' and '17', convert to uppercase
        # print(extracted_part)
        return extracted_part

    def display_authentication(self):
        # self.label_auth = tk.Label(self.root, text="Enter The PassKey:")
        # self.label_auth.pack(pady=10)

        # self.entry_mac = tk.Entry(self.root)
        # self.entry_mac.pack(pady=5)

        self.btn_authenticate = tk.Button(self.root, text="Start", command=self.authenticate, width=10)
        self.btn_authenticate.pack(pady=10)

    def authenticate(self):
        # user_mac = self.entry_mac.get()
        # if user_mac == self.user_mac:
        #     # If the entered MAC address matches the user's and is authorized, proceed to the main app
        self.set_subsequent_pages()
        self.initialize_app()
        # else:
        #     messagebox.showerror("Authentication Failed", "Invalid Password.")

    def check_execution_date(self):
        current_date = datetime.date.today()
        specified_date = datetime.date(2024, 5, 1)  # April 1st, 2024

        if current_date > specified_date:
            error_label = tk.Label(
                self.root,
                text="Fatal Error: Contact the above details for assistance.",
                font=("Arial", 12),
                fg="red"
            )
            error_label.pack(pady=50)
            return False
        return True

    def initialize_app(self):
        # Clear authentication widgets
        # self.label_auth.pack_forget()
        # self.entry_mac.pack_forget()
        self.btn_authenticate.pack_forget()

        # Create the rest of your application here
        self.label = tk.Label(self.root, text="Select Certificate Type:")
        self.label.pack(pady=10)

        # Create radio buttons for A certificate and B certificate
        self.radio_a = tk.Radiobutton(self.root, text="A Certificate", variable=self.certificate_var, value="A")
        self.radio_b = tk.Radiobutton(self.root, text="B Certificate", variable=self.certificate_var, value="B")
        self.radio_c = tk.Radiobutton(self.root, text="C Certificate", variable=self.certificate_var, value="C")
        self.radio_a.pack(pady=5)
        self.radio_b.pack(pady=5)
        self.radio_c.pack(pady=5)


        self.btn_start = tk.Button(self.root, text="Start", command=self.start, width=10)
        self.btn_start.pack(pady=15)

    def start(self):
        # destroy start button and radio buttons
        self.btn_start.destroy()
        self.radio_a.destroy()
        self.radio_b.destroy()
        self.radio_c.destroy()
        self.label.config(text="Enter Marking Scheme for:")

        # Create a label frame to group the input fields
        self.input_frame = ttk.LabelFrame(root, text="")
        self.input_frame.pack(padx=10, pady=10)
        
        # Create labels and text fields for each input
        selected_certificate = self.certificate_var.get()
        if selected_certificate == "A":
            default_correct = 2.5
        elif selected_certificate == "B" or selected_certificate == "C":
            default_correct = 2.0
        else:
            # Default to 175 questions for any other certificate type
            default_correct = 2.5

        self.label1 = ttk.Label(self.input_frame, text="Correct Answers:")
        self.label1.grid(row=0, column=0, padx=5, pady=5)
        self.text_field1 = ttk.Entry(self.input_frame)
        self.text_field1.insert(0, default_correct)
        self.text_field1.grid(row=0, column=1, padx=5, pady=5)

        default_incorrect = 0
        self.label2 = ttk.Label(self.input_frame, text="Incorrect Answers:")
        self.label2.grid(row=1, column=0, padx=5, pady=5)
        self.text_field2 = ttk.Entry(self.input_frame)
        self.text_field2.insert(0, default_incorrect)
        self.text_field2.grid(row=1, column=1, padx=5, pady=5)

        default_left = 0
        self.label3 = ttk.Label(self.input_frame, text="Unattemped:")
        self.label3.grid(row=2, column=0, padx=5, pady=5)
        self.text_field3 = ttk.Entry(self.input_frame)
        self.text_field3.insert(0, default_left)
        self.text_field3.grid(row=2, column=1, padx=5, pady=5)

        # Create the submit button widget and bind it to the handle_click function
        self.btn_submit = ttk.Button(root, text="Submit", command=self.mark_scheme)
        self.btn_submit.pack(pady=10)
        
    def mark_scheme(self):
        try:
            # Try to get the input values from the text fields as floats
            self.input1 = float(self.text_field1.get())
            self.input2 = float(self.text_field2.get())
            self.input3 = float(self.text_field3.get())
        except ValueError:
            # If any input can't be converted to a float, show an error message
            tk.messagebox.showerror("Error", "Please enter valid numbers for all inputs.")

        # destroy submit button
        self.btn_submit.destroy()
        self.input_frame.destroy()

        # Default Threshold for response evaluation
        default_threshold = 35 # Use float here
        self.label.config(text="Enter a threshold for response evaluation (30-50):")
        self.text_field = tk.Entry(root)
        self.text_field.insert(0, default_threshold)
        self.text_field.pack()

        self.btn_next1 = tk.Button(self.root, text="Next", command=self.threshold, width=10)
        self.btn_next1.pack(pady=10)


    def threshold(self):
        try:
            # Try to convert the input to an integer
            self.thresh = int(self.text_field.get())

        except ValueError:
            # If the input can't be converted to an integer, show an error message
            tk.messagebox.showerror("Error", "Please enter an integer.")
        
        # Destroy next button
        self.btn_next1.destroy()
        self.text_field.destroy()

        self.label.config(text="Select the desired Scanned OMRs and Answer Key Files to evaluate:")
        self.btn_browse1 = tk.Button(self.root, text="Upload OMRs Folder", command=self.browse_folder, width=15)
        self.btn_browse1.pack(pady=10)
        
        self.btn_browse2 = tk.Button(self.root, text="Upload Answer Key", command=self.browse_answerkey, width=15)
        self.btn_browse2.pack(pady=10)

        self.btn_next2 = tk.Button(self.root, text="Next", command=self.Next_Evaluate, state="disabled", width=12)
        self.btn_next2.pack(pady=10)

    def browse_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            file_count = len(os.listdir(self.folder_path))
            messagebox.showinfo("File Count", f"Number of files in folder: {file_count}")
            self.label.config(text=f"OMRs Folder: {self.folder_path}", fg="blue")
            self.check_next_button_state()

    def browse_answerkey(self):
        self.answer_key_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
        if self.answer_key_path:
            self.label.config(text=f"Answer Key: {self.answer_key_path}", fg="blue")
            self.check_next_button_state()
            
# for reading csv file
    # def browse_answerkey(self):
    #     self.answer_key_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    #     if self.answer_key_path:
    #         self.label.config(text=f"Answer Key: {self.answer_key_path}", fg="blue")
    #         self.check_next_button_state()

    def check_next_button_state(self):
        if self.folder_path and self.answer_key_path:
            self.btn_next2["state"] = "normal"
        else:
            self.btn_next2["state"] = "disabled"
            
    def Next_Evaluate(self):

        #destroy next button
        self.btn_browse1.destroy()
        self.btn_browse2.destroy()
        self.btn_next2.destroy()

        self.label.config(text="Select the Desired Mode of Evaluation:")
        
        self.btn_fast = tk.Button(self.root, text="Fast Mode", command=self.evaluate_fast, width=10)
        self.btn_fast.pack(pady=10)

        self.btn_visibility = tk.Button(self.root, text="Visibility Mode", command=self.evaluate_visibility, width=12)
        self.btn_visibility.pack(pady=10)

        self.btn_correction = tk.Button(self.root, text="Correction Mode", command=self.evaluate_correction, width=12)
        self.btn_correction.pack(pady=10)        
    
    def evaluate_fast(self):
        start_time=time.time()
        all_results1 = []
        all_results2 = []
        idx=1

        #Clear folders
        shutil.rmtree(os.path.join(output_path, "evaluated"))

        # Create folders
        os.makedirs(os.path.join(output_path, "evaluated"), exist_ok=True)
        
        selected_certificate = self.certificate_var.get()
        if selected_certificate == "A":
            num_questions = 140
        elif selected_certificate == "B" or selected_certificate == "C":
            num_questions = 175
        else:
            # Default to 175 questions for any other certificate type
            num_questions = 140

        for filename in os.listdir(self.folder_path):
            if filename.endswith(".jpg") or filename.endswith(".JPG") or filename.endswith(".png") or filename.endswith(".tif"):
                # Process the OMR sheet
                
                results1,results2,imgInput,imgOutput = main.process_omr_sheet(os.path.join(self.folder_path, filename),filename,idx, self.input1, self.input2, self.input3, self.thresh, self.answer_key_path,num_questions,selected_certificate)
                # Add the results to the list of all results
                if not results1 or not results2:
                    shutil.copy(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))

                        # Move the file to the non-evaluated folder
                    # shutil.move(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))
                    continue
                all_results1.append([*results1])
                all_results2.append([*results2])
                # all_results1.append([*papers])
                idx+=1

                # Move the input and output images to the evaluated folder
                regno = results1[1]  # Assuming "RegNo" is the second item in results1
                
                cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_inp.tif"), imgInput)
                cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_out.tif"), imgOutput)
        # print("hello",all_results2)
        # Convert the list of results to a pandas DataFrame
        df1 = pd.DataFrame(all_results1, columns=["S.No","Enrollment No", "Set", "AdmitCard No", "CorrectAns", "IncorrectAns", "Left","paper1","paper2","paper3","paper4", "Score","Grade"])
        df2 = pd.DataFrame(all_results2)
        columns = ['S.No', 'Enrollment No','AdmitCard No','Set']
        
        columns.extend(['Q{}'.format(i) for i in range(1,num_questions+1)])
        columns.extend(['Score','Grade'])
        df2.columns = columns
        # Write the DataFrame to an Excel file
        # output_file1 = os.path.join(output_folder, "output1.xlsx")
        # output_file2 = os.path.join(output_folder, "output2.xlsx")
        df1.to_excel(output_file1, index=False)
        df2.to_excel(output_file2,index=False)

        shutil.move(output_file1, os.path.join(output_path, output_file1))
        shutil.move(output_file2, os.path.join(output_path, output_file2))
        self.download()
        end_time=time.time()
        print("Time Taken : ")
        print(end_time-start_time)

    def evaluate_visibility(self):
        start_time=time.time()
        all_results1 = []
        all_results2 = []
        idx=1

        #Clear folders
        shutil.rmtree(os.path.join(output_path, "evaluated"))

        # Create folders
        os.makedirs(os.path.join(output_path, "evaluated"), exist_ok=True)
        
        selected_certificate = self.certificate_var.get()
        if selected_certificate == "A":
            num_questions = 140
        elif selected_certificate == "B":
            num_questions = 175
        else:
            # Default to 175 questions for any other certificate type
            num_questions = 140

        for filename in os.listdir(self.folder_path):
            if filename.endswith(".jpg") or filename.endswith(".JPG") or filename.endswith(".png") or filename.endswith(".tif"):
                # Process the OMR sheet
                results1,results2,imgInput,imgOutput= main.process_omr_sheet(os.path.join(self.folder_path, filename),filename,idx, self.input1, self.input2, self.input3, self.thresh, self.answer_key_path,num_questions,selected_certificate)

                if not results1 or not results2:
                        # Move the file to the non-evaluated folder
                    # shutil.move(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))
                    shutil.copy(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))

                    continue

                cv2.imshow("evaluated_image", imgOutput)
                cv2.waitKey(0)
                # Add the results to the list of all results

                all_results1.append([*results1])
                all_results2.append([*results2])
                idx+=1

                # Move the input and output images to the evaluated folder
                regno = results1[1]  # Assuming "RegNo" is the second item in results1
                cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_inp.tif"), imgInput)
                cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_out.tif"), imgOutput)

        # Convert the list of results to a pandas DataFrame
        df1 = pd.DataFrame(all_results1, columns=["S.No","Enrollment No", "Set", "AdmitCard No", "CorrectAns", "IncorrectAns", "Left","paper1","paper2","paper3","paper4", "Score","Grade"])
        df2 = pd.DataFrame(all_results2)
        columns = ['S.No', 'Enrollment No','AdmitCard No','Set']
        
        columns.extend(['Q{}'.format(i) for i in range(1,num_questions+1)])
        columns.extend(['Score','Grade'])
        df2.columns = columns

        # Write the DataFrame to an Excel file
        df1.to_excel(output_file1, index=False)
        df2.to_excel(output_file2,index=False)
        shutil.move(output_file1, os.path.join(output_path, output_file1))
        shutil.move(output_file2, os.path.join(output_path, output_file2))
        self.download()
        end_time=time.time()
        print("Time Taken : ")
        print(end_time-start_time)

    def evaluate_correction(self):
        start_time=time.time()
        all_results1 = []
        all_results2 = []
        idx=1

        #Clear folders
        shutil.rmtree(os.path.join(output_path, "evaluated"))
        shutil.rmtree(os.path.join(output_path, "non_evaluated"))

        # Create folders
        os.makedirs(os.path.join(output_path, "non_evaluated"), exist_ok=True)
        os.makedirs(os.path.join(output_path, "evaluated"), exist_ok=True)

        selected_certificate = self.certificate_var.get()
        if selected_certificate == "A":
            num_questions = 140
        elif selected_certificate == "B":
            num_questions = 175
        else:
            # Default to 140 questions for any other certificate type
            num_questions = 140

        for filename in os.listdir(self.folder_path):
            if filename.endswith(".jpg") or filename.endswith(".JPG") or filename.endswith(".png") or filename.endswith(".tif"):
                # Process the OMR sheet
                self.root.iconify()
                results1,results2,imgInput,imgOutput= main.process_omr_sheet(os.path.join(self.folder_path, filename),filename,idx, self.input1, self.input2, self.input3, self.thresh, self.answer_key_path,num_questions,selected_certificate)
                if not results1 or not results2:
                    # Move the file to the non-evaluated folder
                    # shutil.move(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))
                    if  imgInput is not None and imgInput.any():
                        cv2.imshow("Original_Image", imgInput)
                        cv2.waitKey(0)
                    shutil.copy(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))
                    continue
                cv2.imshow("Orignal_Image", imgInput)
                cv2.imshow("Evaluated_Image", imgOutput)
                
                #cv2.waitKey(0)
                confirmation = messagebox.askokcancel("Confirmation", "Are you sure you want to consider this Data?")
                if confirmation :
                    # Add the results to the list of all results
                   

                    all_results1.append([*results1])
                    all_results2.append([*results2])
                    idx+=1

                    # Move the input and output images to the evaluated folder
                    regno = results1[1]  # Assuming "RegNo" is the second item in results1
                    cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_inp.tif"), imgInput)
                    cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_out.tif"), imgOutput)
                else:
                    # Move the file to the non_evaluated folder
                    regno = results1[1]
                    cv2.imwrite(os.path.join(output_path, "non_evaluated", f"{regno}.tif"), imgInput)
                    
                cv2.destroyAllWindows()
                self.root.deiconify()
        end_time=time.time()
        print("Time Taken : ")
        print(end_time-start_time)

        # Convert the list of results to a pandas DataFrame
        df1 = pd.DataFrame(all_results1, columns=["S.No","Enrollment No", "Set", "Gender", "Category", "CorrectAns", "IncorrectAns", "Left", "Score"])
        df2 = pd.DataFrame(all_results2)
        columns = ['S.No', 'Enrollment No','AdmitCard No','Set']
        # num_questions = 100
        columns.extend(['Q{}'.format(i) for i in range(1,num_questions+1)]) 
        columns.extend(['Score','Grade'])
        # df2.columns = columns
        df2.columns = columns
        # Write the DataFrame to an Excel file
        df1.to_excel(output_file1, index=False)
        df2.to_excel(output_file2,index=False)
        shutil.move(output_file1, os.path.join(output_path, output_file1))
        shutil.move(output_file2, os.path.join(output_path, output_file2))
        self.download()
       

    def download(self):
        # destroy browse and evaluate
        self.btn_fast.destroy()
        self.btn_visibility.destroy()
        self.btn_correction.destroy()
        
        self.label.config(text="Evaluation complete. Download the desired results file.", fg="green")
        output_file1 = os.path.join("output", "abstract.xlsx")
        self.btn_download1 = tk.Button(self.root, text="Abstract Result", command=lambda: os.startfile(output_file1), width=15)
        self.btn_download1.pack(pady=10)
        output_file2 = os.path.join("output", "detailed.xlsx")
        self.btn_download2 = tk.Button(self.root, text="Detailed Result", command=lambda: os.startfile(output_file2), width=15)
        self.btn_download2.pack(pady=10)
        end_time=time.time()

    def create_heading_label(self):
            # Create a label with the logo image
        # logo_img = tk.PhotoImage(file="logo.png")
        logo_label = tk.Label(self.root, image=self.logo_img, bg="#add8e6")
        logo_label.pack(pady=20)
        # Col. Sunir Khatri
        # Brig. Neeraj Punetha
        heading_text = "NCC OMR Sheet Evaluator\nGOI CopyRight No.: SW-17881/2023\n© MNNIT Allahabad\n\nDesigned for: NCC GRP HQ PRAYAGRAJ\n"
        if self.is_first_page:
            # For the first page, include additional details
            heading_text += "\n\nDesigned at:\n1 UP CTR NCC, Prayagraj GRP, U.P.\n\nContact Person:\nLt (Dr) Divya Kumar\n+91 7905595695"
        heading_label = tk.Label(self.root, text=heading_text, font=("Arial", 11, "bold"), bg="#add8e6")
        heading_label.pack(pady=10)

    def set_subsequent_pages(self):
        self.is_first_page = False
        # Clear the existing heading label
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()
        # Call the create_heading_label method again to update the heading
        self.create_heading_label()

        
root = tk.Tk()

# Create a label with the logo image

# logo_img = tk.PhotoImage(file="logo.png")
# logo_label = tk.Label(root, image=logo_img, bg="#add8e6")
# logo_label.pack(pady=20)
# Create a label with the heading text
    
app = App(root)
root.mainloop()

# Restore the original standard output and error streams
sys.stdout = original_stdout
sys.stderr = original_stderr

# Close the log file
log_file.close()


# import os
# import shutil
# import tkinter as tk
# from tkinter import ttk
# from tkinter import filedialog, messagebox
# import pandas as pd
# import time
# import main
# import cv2
# import math
# import uuid
# import datetime
# import sys

# output_log_path = "output_log.txt"

# # Save the original standard output and error streams
# original_stdout = sys.stdout
# original_stderr = sys.stderr

# # Open a new file for writing
# log_file = open(output_log_path, "w")

# # Redirect standard output and error to the file
# # sys.stdout = log_file
# # sys.stderr = log_file



# output_file1 = "abstract.xlsx"
# output_file2 = 'detailed.xlsx'

# # Get the parent directory
# parent_dir = os.getcwd()

# output_folder = "output"
# output_path = os.path.join(parent_dir, output_folder)

# # Create the "output" folder
# os.makedirs(output_path, exist_ok=True)

# # Create the "evaluated" and "non_evaluated" folders inside the "output" folder
# evaluated_folder = os.path.join(output_path, "evaluated")
# non_evaluated_folder = os.path.join(output_path, "non_evaluated")

# os.makedirs(evaluated_folder, exist_ok=True)
# os.makedirs(non_evaluated_folder, exist_ok=True)

# # Create folders
# # Define a Tee class to duplicate the output to both the terminal and a file
# class Tee:
#     def __init__(self, *files):
#         self.files = files

#     def write(self, text):
#         for file in self.files:
#             file.write(str(text))

#     def flush(self):
#         for file in self.files:
#             file.flush()

# sys.stdout = Tee(sys.stdout, log_file)
# sys.stderr = Tee(sys.stderr, log_file)
# class App:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("OMR Sheet Evaluator")
#         self.root.geometry("600x600")
#         self.folder_path = ""
#         self.answer_key_path = ""
        
#         # Set the background color to a calm blue
#                 # self.root.config(bg="#add8e6")

#         self.root.config(bg="#F9CEC8")


#         self.label = tk.Label(self.root, text="Click on the Start Button to Begin!")
#         self.label.pack(pady=10)

#         self.btn_start = tk.Button(self.root, text="Start", command=self.start, width=10)
#         self.btn_start.pack(pady=15)

#     def start(self):
#         # destroy start button
#         self.btn_start.destroy()

#         self.label.config(text="Enter Marking Scheme for:")
#         # Create a label frame to group the input fields
#         self.input_frame = ttk.LabelFrame(root, text="")
#         self.input_frame.pack(padx=10, pady=10)
        
#         # Create labels and text fields for each input
#         default_correct = 4
#         self.label1 = ttk.Label(self.input_frame, text="Correct Answers:")
#         self.label1.grid(row=0, column=0, padx=5, pady=5)
#         self.text_field1 = ttk.Entry(self.input_frame)
#         self.text_field1.insert(0, default_correct)
#         self.text_field1.grid(row=0, column=1, padx=5, pady=5)

#         default_incorrect = -1
#         self.label2 = ttk.Label(self.input_frame, text="Incorrect Answers:")
#         self.label2.grid(row=1, column=0, padx=5, pady=5)
#         self.text_field2 = ttk.Entry(self.input_frame)
#         self.text_field2.insert(0, default_incorrect)
#         self.text_field2.grid(row=1, column=1, padx=5, pady=5)

#         default_left = 0
#         self.label3 = ttk.Label(self.input_frame, text="Unattemped:")
#         self.label3.grid(row=2, column=0, padx=5, pady=5)
#         self.text_field3 = ttk.Entry(self.input_frame)
#         self.text_field3.insert(0, default_left)
#         self.text_field3.grid(row=2, column=1, padx=5, pady=5)

#         # Create the submit button widget and bind it to the handle_click function
#         self.btn_submit = ttk.Button(root, text="Submit", command=self.mark_scheme)
#         self.btn_submit.pack(pady=10)
        

#     def mark_scheme(self):

#         try:
#             # Try to get the input values from the text fields
#             self.input1 = int(self.text_field1.get())
#             self.input2 = int(self.text_field2.get())
#             self.input3 = int(self.text_field3.get())
           
#         except ValueError:
#             # If any input can't be converted to an integer, show an error message
#             tk.messagebox.showerror("Error", "Please enter integers for all inputs.")
                                
#         # destroy submit button
#         self.btn_submit.destroy()
#         self.input_frame.destroy()

#         # Default Threshold for response evaluation
#         default_threshold = 35
#         self.label.config(text="Enter a threshold for response evaluation (30-50):")
#         self.text_field = tk.Entry(root)
#         self.text_field.insert(0, default_threshold)
#         self.text_field.pack()

#         self.btn_next1 = tk.Button(self.root, text="Next", command=self.threshold, width=10)
#         self.btn_next1.pack(pady=10)


#     def threshold(self):
#         try:
#             # Try to convert the input to an integer
#             self.thresh = int(self.text_field.get())

#         except ValueError:
#             # If the input can't be converted to an integer, show an error message
#             tk.messagebox.showerror("Error", "Please enter an integer.")
        
#         # Destroy next button
#         self.btn_next1.destroy()
#         self.text_field.destroy()

#         self.label.config(text="Select the desired Scanned OMRs and Answer Key Files to evaluate:")
#         self.btn_browse1 = tk.Button(self.root, text="Upload OMRs Folder", command=self.browse_folder, width=15)
#         self.btn_browse1.pack(pady=10)
        
#         self.btn_browse2 = tk.Button(self.root, text="Upload Answer Key", command=self.browse_answerkey, width=15)
#         self.btn_browse2.pack(pady=10)

#         self.btn_next2 = tk.Button(self.root, text="Next", command=self.Next_Evaluate, state="disabled", width=12)
#         self.btn_next2.pack(pady=10)

#     def browse_folder(self):
#         self.folder_path = filedialog.askdirectory()
#         if self.folder_path:
#             file_count = len(os.listdir(self.folder_path))
#             messagebox.showinfo("File Count", f"Number of files in folder: {file_count}")
#             self.label.config(text=f"OMRs Folder: {self.folder_path}", fg="blue")
#             self.check_next_button_state()

#     def browse_answerkey(self):
#         self.answer_key_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
#         if self.answer_key_path:
#             self.label.config(text=f"Answer Key: {self.answer_key_path}", fg="blue")
#             self.check_next_button_state()

#     def check_next_button_state(self):
#         if self.folder_path and self.answer_key_path:
#             self.btn_next2["state"] = "normal"
#         else:
#             self.btn_next2["state"] = "disabled"
            
#     def Next_Evaluate(self):

#         #destroy next button
#         self.btn_browse1.destroy()
#         self.btn_browse2.destroy()
#         self.btn_next2.destroy()

#         self.label.config(text="Select the Desired Mode of Evaluation:")
        
#         self.btn_fast = tk.Button(self.root, text="Fast Mode", command=self.evaluate_fast, width=10)
#         self.btn_fast.pack(pady=10)

#         self.btn_visibility = tk.Button(self.root, text="Visibility Mode", command=self.evaluate_visibility, width=12)
#         self.btn_visibility.pack(pady=10)

#         self.btn_correction = tk.Button(self.root, text="Correction Mode", command=self.evaluate_correction, width=12)
#         self.btn_correction.pack(pady=10)        
    
#     def evaluate_fast(self):
#         start_time=time.time()
#         all_results1 = []
#         all_results2 = []
#         idx=1

#         #Clear folders
#         shutil.rmtree(os.path.join(output_path, "evaluated"))

#         # Create folders
#         os.makedirs(os.path.join(output_path, "evaluated"), exist_ok=True)
        
#         # selected_certificate = self.certificate_var.get()
#         # if selected_certificate == "A":
#         #     num_questions = 140
#         # elif selected_certificate == "B":
#         #     num_questions = 175
#         # else:
#         #     # Default to 175 questions for any other certificate type
#         #     num_questions = 140

#         for filename in os.listdir(self.folder_path):
#             if filename.endswith(".jpg") or filename.endswith(".JPG") or filename.endswith(".png") or filename.endswith(".tif"):
#                 # Process the OMR sheet
                
#                 results1,results2,imgInput,imgOutput = main.process_omr_sheet(os.path.join(self.folder_path, filename),filename,idx, self.input1, self.input2, self.input3, self.thresh, self.answer_key_path,100)
#                 # Add the results to the list of all results
#                 if not results1 or not results2:
#                     shutil.copy(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))

#                         # Move the file to the non-evaluated folder
#                     # shutil.move(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))
#                     continue
#                 all_results1.append([*results1])
#                 all_results2.append([*results2])
#                 # all_results1.append([*papers])
#                 idx+=1

#                 # Move the input and output images to the evaluated folder
#                 regno = results1[1]  # Assuming "RegNo" is the second item in results1
                
#                 cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_inp.tif"), imgInput)
#                 cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_out.tif"), imgOutput)
#         # print("hello",all_results1)
#         # Convert the list of results to a pandas DataFrame
#         df1 = pd.DataFrame(all_results1, columns=["S.No","Enrollment No", "Set", "Category", "Gender", "CorrectAns", "IncorrectAns", "Left", "Score"])
#         df2 = pd.DataFrame(all_results2)
#         columns = ['S.No', 'Enrollment No','Set','Gender','Category']
        
#         columns.extend(['Q{}'.format(i) for i in range(1,100+1)])
#         columns.extend(['Score'])
#         df2.columns = columns
#         # Write the DataFrame to an Excel file
#         # output_file1 = os.path.join(output_folder, "output1.xlsx")
#         # output_file2 = os.path.join(output_folder, "output2.xlsx")
#         df1.to_excel(output_file1, index=False)
#         df2.to_excel(output_file2,index=False)

#         shutil.move(output_file1, os.path.join(output_path, output_file1))
#         shutil.move(output_file2, os.path.join(output_path, output_file2))
#         self.download()
#         end_time=time.time()
#         print("Time Taken : ")
#         print(end_time-start_time)

#     def evaluate_visibility(self):
#         start_time=time.time()
#         all_results1 = []
#         all_results2 = []
#         idx=1

#         #Clear folders
#         shutil.rmtree(os.path.join(output_path, "evaluated"))

#         # Create folders
#         os.makedirs(os.path.join(output_path, "evaluated"), exist_ok=True)
        
#         # selected_certificate = self.certificate_var.get()
#         # if selected_certificate == "A":
#         #     num_questions = 140
#         # elif selected_certificate == "B":
#         #     num_questions = 175
#         # else:
#         #     # Default to 175 questions for any other certificate type
#         #     num_questions = 140

#         for filename in os.listdir(self.folder_path):
#             if filename.endswith(".jpg") or filename.endswith(".JPG") or filename.endswith(".png") or filename.endswith(".tif"):
#                 # Process the OMR sheet
#                 results1,results2,imgInput,imgOutput= main.process_omr_sheet(os.path.join(self.folder_path, filename),filename,idx, self.input1, self.input2, self.input3, self.thresh, self.answer_key_path,100)

#                 if not results1 or not results2:
#                         # Move the file to the non-evaluated folder
#                     # shutil.move(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))
#                     shutil.copy(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))

#                     continue

#                 cv2.imshow("evaluated_image", imgOutput)
#                 cv2.waitKey(0)
#                 # Add the results to the list of all results

#                 all_results1.append([*results1])
#                 all_results2.append([*results2])
#                 idx+=1

#                 # Move the input and output images to the evaluated folder
#                 regno = results1[1]  # Assuming "RegNo" is the second item in results1
#                 cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_inp.tif"), imgInput)
#                 cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_out.tif"), imgOutput)

#         # Convert the list of results to a pandas DataFrame
#         df1 = pd.DataFrame(all_results1, columns=["S.No","Enrollment No", "Set", "Category", "Gender", "CorrectAns", "IncorrectAns", "Left", "Score"])
#         df2 = pd.DataFrame(all_results2)
#         columns = ['S.No', 'Enrollment No','Set','Gender','Category']
        
#         columns.extend(['Q{}'.format(i) for i in range(1,100+1)])
#         columns.extend(['Score'])
#         df2.columns = columns

#         # Write the DataFrame to an Excel file
#         df1.to_excel(output_file1, index=False)
#         df2.to_excel(output_file2,index=False)
#         shutil.move(output_file1, os.path.join(output_path, output_file1))
#         shutil.move(output_file2, os.path.join(output_path, output_file2))
#         self.download()
#         end_time=time.time()
#         print("Time Taken : ")
#         print(end_time-start_time)

#     def evaluate_correction(self):
#         start_time=time.time()
#         all_results1 = []
#         all_results2 = []
#         idx=1

#         #Clear folders
#         shutil.rmtree(os.path.join(output_path, "evaluated"))
#         shutil.rmtree(os.path.join(output_path, "non_evaluated"))

#         # Create folders
#         os.makedirs(os.path.join(output_path, "non_evaluated"), exist_ok=True)
#         os.makedirs(os.path.join(output_path, "evaluated"), exist_ok=True)

#         # selected_certificate = self.certificate_var.get()
#         # if selected_certificate == "A":
#         #     num_questions = 140
#         # elif selected_certificate == "B":
#         #     num_questions = 175
#         # else:
#         #     # Default to 140 questions for any other certificate type
#         #     num_questions = 140

#         for filename in os.listdir(self.folder_path):
#             if filename.endswith(".jpg") or filename.endswith(".JPG") or filename.endswith(".png") or filename.endswith(".tif"):
#                 # Process the OMR sheet
#                 self.root.iconify()
#                 results1,results2,imgInput,imgOutput= main.process_omr_sheet(os.path.join(self.folder_path, filename),filename,idx, self.input1, self.input2, self.input3, self.thresh, self.answer_key_path,100)
#                 if not results1 or not results2:
#                     # Move the file to the non-evaluated folder
#                     # shutil.move(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))
#                     if  imgInput is not None and imgInput.any():
#                         cv2.imshow("Original_Image", imgInput)
#                         cv2.waitKey(0)
#                     shutil.copy(os.path.join(self.folder_path, filename), os.path.join(non_evaluated_folder, filename))
#                     continue
#                 cv2.imshow("Orignal_Image", imgInput)
#                 cv2.imshow("Evaluated_Image", imgOutput)
                
#                 #cv2.waitKey(0)
#                 confirmation = messagebox.askokcancel("Confirmation", "Are you sure you want to consider this Data?")
#                 if confirmation :
#                     # Add the results to the list of all results
                   

#                     all_results1.append([*results1])
#                     all_results2.append([*results2])
#                     idx+=1

#                     # Move the input and output images to the evaluated folder
#                     regno = results1[1]  # Assuming "RegNo" is the second item in results1
#                     cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_inp.tif"), imgInput)
#                     cv2.imwrite(os.path.join(output_path, "evaluated", f"{regno}_out.tif"), imgOutput)
#                 else:
#                     # Move the file to the non_evaluated folder
#                     regno = results1[1]
#                     cv2.imwrite(os.path.join(output_path, "non_evaluated", f"{regno}.tif"), imgInput)
                    
#                 cv2.destroyAllWindows()
#                 self.root.deiconify()
#         end_time=time.time()
#         print("Time Taken : ")
#         print(end_time-start_time)

#         # Convert the list of results to a pandas DataFrame
#         df1 = pd.DataFrame(all_results1, columns=["S.No","Enrollment No", "Set", "Category", "Gender", "CorrectAns", "IncorrectAns", "Left", "Score"])
#         df2 = pd.DataFrame(all_results2)
#         columns = ['S.No', 'Enrollment No','Set','Gender','Category']
        
#         columns.extend(['Q{}'.format(i) for i in range(1,100+1)])
#         columns.extend(['Score'])
#         # df2.columns = columns
#         df2.columns = columns
#         # Write the DataFrame to an Excel file
#         df1.to_excel(output_file1, index=False)
#         df2.to_excel(output_file2,index=False)
#         shutil.move(output_file1, os.path.join(output_path, output_file1))
#         shutil.move(output_file2, os.path.join(output_path, output_file2))
#         self.download()       

#     def download(self):
#         # destroy browse and evaluate
#         self.btn_fast.destroy()
#         self.btn_visibility.destroy()
#         self.btn_correction.destroy()
        
#         self.label.config(text="Evaluation complete. Download the desired results file.", fg="green")
#         output_file1 = os.path.join("output", "abstract.xlsx")
#         self.btn_download1 = tk.Button(self.root, text="Abstract Result", command=lambda: os.startfile(output_file1), width=15)
#         self.btn_download1.pack(pady=10)
#         output_file2 = os.path.join("output", "detailed.xlsx")
#         self.btn_download2 = tk.Button(self.root, text="Detailed Result", command=lambda: os.startfile(output_file2), width=15)
#         self.btn_download2.pack(pady=10)
#         end_time=time.time()


# root = tk.Tk()

# # Create a label with the logo image
# logo_img = tk.PhotoImage(file="ku.png")
# logo_label = tk.Label(root, image=logo_img, bg="#F9CEC8")
# logo_label.pack(pady=2)

# # Create a label with the heading text
# heading_label = tk.Label(root, text="OMR Sheet Evaluator", font=("Arial", 18, "bold"), bg="#F9CEC8")
# heading_label.pack(pady=10)

# app = App(root)

# root.mainloop()
# # Close the log file
# log_file.close()