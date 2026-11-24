import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from pypdf import PdfReader


lecture_to_notes_summarizer_window = tk.Tk()
lecture_to_notes_summarizer_window.title('Briefly App')
lecture_to_notes_summarizer_window.geometry('700x900')
lecture_to_notes_summarizer_window.configure(background='white')

# placeholder text shown in the two text boxes before the user does anything

NOTES_PLACEHOLDER = 'Type or paste your lecture notes here....'
SUMMARY_PLACEHOLDER = ('Lecture Summary \n'
                       '\n'
                       '. Main concepts from the lecture \n'
                       '\n'
                       '. Important supporting information \n'
                       '\n'
                       '. Key points to remember \n')

#________________________________________________________________________________________________
#                   IMAGE SECTION
#________________________________________________________________________________________________
img = Image.open('image 1.png')

# PILLOW>=10 changed ANTIALIAS; this keeps it compatible
try:
    img = img.resize((150, 100), Image.Resampling.LANCZOS)
except AttributeError:
    img = img.resize((100, 100), Image.ANTIALIAS)
img = img.convert('RGBA')
image_data = list(img.get_flattened_data())

newData = []
for item in image_data:
    # if pixel is white, make it transparent; else keep it
    if item[:3] == (255,255,255):
        newData.append((255,255,255,0))
    else:
        newData.append(item)
img.putdata(newData)

# convert image for Tkinter
logo = ImageTk.PhotoImage(img)

# display logo
logoLabel = tk.Label(
    lecture_to_notes_summarizer_window,
    image=logo,
    bg='white'
)
logoLabel.pack(pady=(10, 0))

# Upload Lecture Material label
upload_label = tk.Label(lecture_to_notes_summarizer_window,text='Upload Lecture Material', font=('Arial', 12, 'bold'), fg='black', bg='white')
upload_label.pack(anchor='w', padx=30, pady=(20,5))

# frame for the upload section
upload_frame= tk.Frame(lecture_to_notes_summarizer_window, bg='white')
upload_frame.pack(fill='x', padx=30, pady=5)

# creating the file path box
file_entry = tk.Entry(upload_frame, width=50, fg='black', bg='white')
file_entry.insert(0,'Select Lecture Material')
file_entry.pack(anchor='w', side='left', expand=True)

# _____________________________________________________________________________________
#                   FUNCTION TO MAKE THE BROWSE BUTTON FUNCTIONAL
#  ____________________________________________________________________________________

def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select Lecture Material",
        filetypes=[
            ("PDF and Text Files", "*.pdf *.txt"),
            ("PDF Files", "*.pdf"),
            ("Text Files", "*.txt")
        ]
    )
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

# Browse button
browse_button = tk.Button(upload_frame,text='Browse',command=browse_file, width=10, fg='black', bg='white', font=('Arial', 12, 'bold'))
browse_button.pack(side='right', padx=(10,0))

# _____________________________________________________________________________________
#                   SECTION TO UPLOAD LECTURE NOTES
#  _____________________________________________________________________________________

notes_label = tk.Label(lecture_to_notes_summarizer_window, text='Enter Lecture Notes', font=('Arial', 12, 'bold'), fg='black', bg='white')
notes_label.pack(anchor='w', padx=30, pady=5)

notes_text = tk.Text(lecture_to_notes_summarizer_window, height=8, width=50, font=('Arial', 12, 'bold'), fg='gray', bg='white',wrap='word')
notes_text.pack(fill='x', padx=30, pady=5)
notes_text.insert('1.0', NOTES_PLACEHOLDER)
# _____________________________________________________________________________________
#                   FUNCTION TO REMOVE THE PLACEHOLDER TEXT
#  ____________________________________________________________________________________

def clear_placeholder(event=None):
    if notes_text.get('1.0', tk.END).strip() == NOTES_PLACEHOLDER:
        notes_text.delete('1.0', tk.END)
        notes_text.config(fg='black')

# _____________________________________________________________________________________
#                   FUNCTION TO RESTORE PLACEHOLDER IF THE BOX IS EMPTY
#  ____________________________________________________________________________________
def restore_placeholder(event=None):
    if not notes_text.get('1.0', tk.END).strip():
        notes_text.insert('1.0', NOTES_PLACEHOLDER)
        notes_text.config(fg='gray')


# Bind the function
notes_text.bind('<FocusIn>', clear_placeholder)
notes_text.bind('<FocusOut>', restore_placeholder)

# _____________________________________________________________________________________
#                   SUMMARY SECTION
#  _____________________________________________________________________________________

summary_label=tk.Label(lecture_to_notes_summarizer_window, text='Summary Options', font=('Arial', 12, 'bold'), fg='black', bg='white')
summary_label.pack(anchor='w', padx=30, pady=5)

# Variable to store the selected option
summary_length =tk.StringVar(value='Short')

# Frame for the summary options
options_frame = tk.Frame(lecture_to_notes_summarizer_window, bg='white')
options_frame.pack(anchor='w', padx=30)

# Short summary radiobutton
short_radio = tk.Radiobutton(options_frame, text='Short', variable=summary_length, value='Short',bg='white', fg='black')
short_radio.pack(side='left')

# Detailed summary radiobutton
detailed_radio = tk.Radiobutton(options_frame, text='Detailed', variable=summary_length, value='Detailed',bg='white', fg='black')
detailed_radio.pack(side='left')

# include keypoints check box
include_key_points = tk.BooleanVar(value=False)

key_points_checkbox = tk.Checkbutton(options_frame, text='Include Key Points', variable=include_key_points, bg='white', fg='black')
key_points_checkbox.pack(side='left', padx=15)


# _____________________________________________________________________________________
#                   FUNCTION TO GENERATE SUMMARY
# _____________________________________________________________________________________

def generate_summary():

    # Get uploaded file
    uploaded_file = file_entry.get().strip()

    # Get manually entered lecture notes
    lecture_notes = notes_text.get('1.0', tk.END).strip()

    # Get summary options
    selected_length = summary_length.get()
    key_points = include_key_points.get()

    # Ignore placeholder text
    if lecture_notes == NOTES_PLACEHOLDER:
        lecture_notes = ''

    if uploaded_file == 'Select Lecture Material':
        uploaded_file = ''

    # Read uploaded PDF or TXT file
    if uploaded_file:
        try:
            file_path = Path(uploaded_file)

            if file_path.suffix.lower() == '.txt':
                file_notes = file_path.read_text(encoding='utf-8')

            elif file_path.suffix.lower() == '.pdf':
                reader = PdfReader(str(file_path))
                file_notes = '\n'.join(
                    page.extract_text() or ''
                    for page in reader.pages
                )

            else:
                messagebox.showerror(
                    'Unsupported File',
                    'Please select a PDF or TXT file.'
                )
                return

            # Combine uploaded material with typed notes
            lecture_notes = file_notes + '\n' + lecture_notes

        except Exception as error:
            messagebox.showerror(
                'File Error',
                f'Unable to read the file: {error}'
            )
            return

    # Validate lecture notes
    if not lecture_notes.strip():
        messagebox.showwarning(
            'Missing Lecture Notes',
            'Please enter notes or upload a readable PDF/TXT file.'
        )
        return

    # Generate summary using Claude
    try:
        generated_text = summarize_with_claude(
            lecture_notes,
            selected_length,
            key_points
        )

        # Display the generated summary
        display_summary(generated_text)

    except Exception as error:
        messagebox.showerror(
            'Claude API Error',
            f'Unable to generate summary: {error}'
        )


# button frame
button_frame = tk.Frame(lecture_to_notes_summarizer_window, bg='white')
button_frame.pack(pady=20)

# _____________________________________________________________________________________
#                   FUNCTION TO CLEAR THE FORM
#  ____________________________________________________________________________________
def clear_form():
    #Clear the uploaded path
    file_entry.delete(0, tk.END)
    file_entry.insert(0, 'Select Lecture Material')

    #Clear lecture note
    notes_text.delete('1.0', tk.END)

    # restore
    notes_text.insert('1.0', NOTES_PLACEHOLDER)
    notes_text.config(fg='gray')

    #Reset the summary length
    summary_length.set('Short')

    #Uncheck Include Key Points
    include_key_points.set(False)

    # Enable generated summary box for editing
    summary_output.config(state='normal')

    # Clear the generated summary
    summary_output.delete('1.0', tk.END)

    # Restore summary placeholder
    summary_output.insert('1.0', SUMMARY_PLACEHOLDER)

    # Restore gray text and make output read-only
    summary_output.config(fg='gray', state='disabled')

    # Reset scrollbar to the top
    summary_output.yview_moveto(0)

# Generate summary button
generate_summary_btn = tk.Button(button_frame,text='Generate Summary', width=18, fg='black', bg='white', font=('Arial', 12, 'bold'), command=generate_summary )
generate_summary_btn.pack(side='left',padx=10)

# clear button
clear_btn = tk.Button(button_frame, text='Clear', fg='black', bg='white', command=clear_form, font=('Arial', 12, 'bold'))
clear_btn.pack(side='left',padx=10)


# _____________________________________________________________________________________
#                   CLAUDE AI SUMMARIZATION FUNCTION
# _____________________________________________________________________________________

def summarize_with_claude(lecture_notes, selected_length, key_points):
    import anthropic
    # Connect to Claude using the API key from PyCharm
    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"]
    )

    # Instructions based on the selected summary length
    if selected_length == 'Short':
        length_instruction = 'Create a short, concise summary.'
    else:
        length_instruction = 'Create a detailed, well-organized summary.'

    # Instructions for key points
    if key_points:
        key_points_instruction = 'Include a Key Points section with bullet points.'
    else:
        key_points_instruction = 'Do not add a separate Key Points section.'

    # Create the prompt
    prompt = (
        f'{length_instruction}\n'
        f'{key_points_instruction}\n'
        'Use clear headings and student-friendly language.\n'
        'Only use information from the lecture material.\n'
        'Do not invent information.\n\n'
        f'Lecture Notes:\n{lecture_notes}'
    )

    # Send the lecture notes to Claude
    response = client.messages.create(
        model='claude-sonnet-5-5',
        max_tokens=5000,
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )

    # Return the generated summary
    return '\n'.join(
        block.text
        for block in response.content
        if block.type == 'text'
    )

# _____________________________________________________________________________________
#                   GENERATED SUMMARY SECTION
#  _____________________________________________________________________________________

result_label = tk.Label(lecture_to_notes_summarizer_window, text = 'Generated Summary', fg='black', bg='white', font=('Ariel',12, 'bold'))
result_label.pack(anchor='w', padx=30, pady=(10,5))

#Result Frame
result_frame = tk.Frame(lecture_to_notes_summarizer_window, bg='white')
result_frame.pack(fill='x', padx=30, pady=5)

# Scroll Bar
summary_scrollbar = tk.Scrollbar(result_frame)
summary_scrollbar.pack(side='right', fill='y')

# Text box to show the generated summary
summary_output = tk.Text(result_frame, height=10, width=50, font=('Arial', 12, 'bold'), fg='gray', bg='white', wrap='word', yscrollcommand=summary_scrollbar.set)
summary_output.pack(side='left', fill='both', expand=True)

# Connect the scrollbar to the textbox
summary_scrollbar.config(command=summary_output.yview)

# Display the placeholder text
summary_output.insert('1.0', SUMMARY_PLACEHOLDER)

# Prevent users from editing generated summaries
summary_output.config(state='disabled')

# _____________________________________________________________________________________
#                   FUNCTION TO DISPLAY THE GENERATED SUMMARY
#  _____________________________________________________________________________________

def display_summary(generated_text):
    summary_output.config(state='normal')
    summary_output.delete('1.0', tk.END)
    summary_output.insert('1.0', generated_text)
    summary_output.config(fg='black', state='disabled')

# _____________________________________________________________________________________
#                   FUNCTION TO SAVE THE GENERATED NOTES
#  _____________________________________________________________________________________
def save_notes():

    # get the generated summary
    notes = summary_output.get('1.0', tk.END).strip()

    # Check whether a summary has been generated
    if not notes or notes == SUMMARY_PLACEHOLDER.strip():
        messagebox.showwarning('No Summary', 'Please Generate a summary before saving.')
        return

# Ask the user where to save the notes
    file_path =filedialog.asksaveasfilename(defaultextension='.md', filetypes=[
        ('Markdown Files', '*.md'), ('Text Files', '*.txt')
        ],
        initialfile='Briefly_Notes.md',
        title='Save LectureNotes')

# save the notes to the selected path
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(notes)
            messagebox.showinfo('Success', 'Your file has been saved successfully')
        except OSError as error:
            messagebox.showerror(
                'Error',
                f'Unable to save file: {error}'
            )
# _____________________________________________________________________________________
#                   FUNCTION TO QUIT THE APP
#  _____________________________________________________________________________________
def quit_app():
    lecture_to_notes_summarizer_window.destroy()

# bottom frame
bottom_frame = tk.Frame(lecture_to_notes_summarizer_window, bg='white')
bottom_frame.pack(pady=20)

save_notes_btn = tk.Button(bottom_frame, text='Save Notes', width=18, fg='black', bg='white', command=save_notes)
save_notes_btn.pack(side='left',padx=10)

quit_app_btn = tk.Button(lecture_to_notes_summarizer_window, text='Quit', command=quit_app)
quit_app_btn.pack(padx=10)


lecture_to_notes_summarizer_window.mainloop()
