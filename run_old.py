import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Scale, Scrollbar, Frame, Canvas
import markdown
import webbrowser
import os
from bs4 import BeautifulSoup
import csv
import json
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

html_filename = 'table.html'
text_filename = 'markdownText.txt'
settings_filename = 'settings.json'
table_name = ''

setting_ranges = {
    "window_width": (600, 1600), # Minimum width to display content properly, and maximum for large screens
    "window_height": (400, 1200), # Minimum height for usability, and maximum for large screens
    "input_name_input_width": (20, 100), # Width for the name input box
    "input_name_input_height": (1, 5), # Height for the name input box (number of lines)
    "input_label_input_width": (40, 200), # Width for the main input area
    "input_label_input_height": (5, 30), # Height for the main input area (number of lines)
    "run_button_width": (5, 20), # Width of the 'Run' button
    "run_button_height": (1, 5), # Height of the 'Run' button
    "run_button_padding": (5, 50), # Padding around the 'Run' button
    "save_as_button_width": (10, 30), # Width of the 'Save As' button
    "save_as_button_height": (1, 5), # Height of the 'Save As' button
    "save_as_button_padding": (5, 50) # Padding around the 'Save As' button
}

def load_settings():
    try:
        with open(settings_filename, 'r') as settings_file:
            settings_data = json.load(settings_file)
            
    except FileNotFoundError:
        default_settings = {
            "window_width" : 900,
            "window_height" : 800,
            "input_name_input_width": 90,
            "input_name_input_height" : 2,
            "input_label_input_width" : 90,
            "input_label_input_height" : 25,
            "run_button_width" : 9,
            "run_button_height" : 1,
            "run_button_padding" : 10,
            "save_as_button_width" : 16,
            "save_as_button_height" : 1,
            "save_as_button_padding" : 10
        }
        
        with open(settings_filename, 'w') as new_settings_file:
            json.dump(default_settings, new_settings_file, indent=2)
        settings_data = default_settings
        
    return settings_data


def markdown2table():
    text = input_label_input.get("1.0", tk.END)
    
    with open(text_filename, "w") as file:
        file.write(text)

    with open(text_filename, "r") as file:
        readFile = file.read()
        
    table_html = markdown.markdown(readFile, extensions=['markdown.extensions.tables', 'markdown.extensions.extra'])

    stylesheet = """
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }

        th {
            background-color: #f2f2f2;
        }
    </style>
    """

    with open(html_filename, 'w') as html_file:
        html_file.write(f"<html><head><title>Table Viewer</title>{stylesheet}</head><body>")
        html_file.write(table_html)
        html_file.write("</body></html>")

    webbrowser.open_new_tab(html_filename)
    

def save_as_csv():
    text = input_label_input.get("1.0", tk.END)
    name = input_name_input.get("1.0", tk.END)
    
    with open(text_filename, "w") as file:
        file.write(text)

    with open(text_filename, "r") as file:
        readFile = file.read()
        
    table_html = markdown.markdown(readFile, extensions=['markdown.extensions.tables', 'markdown.extensions.extra'])
    soup = BeautifulSoup(table_html, 'html.parser')
    table = soup.find('table')
    
    if table is None:
        tk.messagebox.showerror("Error", "No table found. Cannot save as CSV.", parent=root)
        return
    
    csv_filename = name.replace('\n', '_') + 'table.csv'
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in table.find_all('tr'):
            csv_writer.writerow([col.get_text(strip=True) for col in row.find_all(['th', 'td'])])


def markdown2code():
    text = input_label_input.get("1.0", tk.END)

    with open(text_filename, "w") as file:
        file.write(text)

    with open(text_filename, "r") as file:
        readFile = file.read()
    
    lines = readFile.split('\n')
    i = 0
    html_code = ''
    
    while i < len(lines):
        line = lines[i]
        if line.startswith('```'):
            language = line[3:].strip().lower()
            i += 1
            code = ''

            while i < len(lines) and not lines[i].startswith('```'):
                code += lines[i] + '\n'
                i += 1

            lexer_name = language
            lexer = get_lexer_by_name(lexer_name, stripall=True)

            formatter = HtmlFormatter(style='friendly', full=True)

            highlighted_code = highlight(code, lexer, formatter)
            html_code += highlighted_code

        i += 1

    with open(html_filename, 'w') as html_file:
        html_file.write(html_code)

    webbrowser.open_new_tab(html_filename)

def open_settings_window():
    settings_window = Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x600")

    canvas = Canvas(settings_window)
    scrollbar = Scrollbar(settings_window, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def update_setting(setting, value):
        settings[setting] = value

    def save_settings():
        with open(settings_filename, 'w') as new_settings_file:
            json.dump(settings, new_settings_file, indent=2)
        messagebox.showinfo("Settings", "Settings saved successfully!", parent=settings_window)

    for setting, value in settings.items():
        if setting in setting_ranges:
            min_val, max_val = setting_ranges[setting]
            scale = Scale(scrollable_frame, from_=min_val, to=max_val, label=setting.replace("_", " ").capitalize(), orient=tk.HORIZONTAL, command=lambda v, s=setting: update_setting(s, int(v)))
            scale.set(value)
            scale.pack(padx=30, pady=20)

    save_settings_button = tk.Button(scrollable_frame, text="Save Settings", command=save_settings)
    save_settings_button.pack(pady=20)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def execute():
    if checkbox_var.get() == 1:
        markdown2code()
    else:
        markdown2table()



root = tk.Tk()
root.title("Markdown to Table")


settings = load_settings()

window_width = settings.get("window_width")
window_height = settings.get("window_height")
input_name_input_width = settings.get("input_name_input_width")
input_name_input_height = settings.get("input_name_input_height")
input_label_input_width = settings.get("input_label_input_width")
input_label_input_height = settings.get("input_label_input_height")
run_button_width = settings.get("run_button_width")
run_button_height = settings.get("run_button_height")
run_button_padding = settings.get("run_button_padding")
save_as_button_width = settings.get("save_as_button_width")
save_as_button_height = settings.get("save_as_button_height")
save_as_button_padding = settings.get("save_as_button_padding")

root.geometry(f"{window_width}x{window_height}")

checkbox_var = tk.IntVar()
checkbox = tk.Checkbutton(root, text="Code Mode",variable=checkbox_var)
checkbox.pack()

input_label = tk.Label(root, text="\nEnter Markdown Text:")
input_label.pack()

input_label_input = tk.Text(root, wrap=tk.WORD, width=input_label_input_width, height=input_label_input_height)
input_label_input.pack()

run_button = tk.Button(root, text="Run", command=execute, width=run_button_width, height=run_button_height)
run_button.pack(pady=run_button_padding)

input_name = tk.Label(root, text="Enter Table Name:")
input_name.pack()

settings_button = tk.Button(root, text="*", font=("Arial", 20, "bold"), command=open_settings_window)
settings_button.place(relx=1.0, rely=0.0, x=-10, y=20, anchor="ne")

input_name_input = tk.Text(root, wrap=tk.WORD, width=input_name_input_width, height=input_name_input_height)
input_name_input.pack()

save_as_button = tk.Button(root, text="Save Table as csv", command=save_as_csv, width=save_as_button_width, height=save_as_button_height)
save_as_button.pack(pady=save_as_button_padding)

root.mainloop()

if os.path.exists(html_filename):
    os.remove(html_filename)
    
if os.path.exists(text_filename):
    os.remove(text_filename)
