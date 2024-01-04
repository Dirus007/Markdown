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
css_filename = 'style.css'


setting_ranges = {
    "window_width": (600, 1600),
    "window_height": (400, 1200),
    "input_name_input_width": (20, 100),
    "input_name_input_height": (1, 5),
    "input_label_input_width": (40, 200),
    "input_label_input_height": (5, 30),
    "run_button_width": (5, 20),
    "run_button_height": (1, 5),
    "run_button_padding": (5, 50),
    "save_as_button_width": (10, 30),
    "save_as_button_height": (1, 5),
    "save_as_button_padding": (5, 50)
}

default_settings = {
    "window_width": 900,
    "window_height": 620,
    "input_name_input_width": 90,
    "input_name_input_height": 2,
    "input_label_input_width": 90,
    "input_label_input_height": 25,
    "run_button_width": 9,
    "run_button_height": 1,
    "run_button_padding": 10,
    "save_as_button_width": 16,
    "save_as_button_height": 1,
    "save_as_button_padding": 10
}

def load_settings():
    try:
        with open(settings_filename, 'r') as settings_file:
            return json.load(settings_file)
    except FileNotFoundError:
        with open(settings_filename, 'w') as new_settings_file:
            json.dump(default_settings, new_settings_file, indent=2)
        return default_settings

def markdown2table():
    text = input_label_input.get("1.0", tk.END)
    with open(text_filename, "w") as file:
        file.write(text)
    with open(text_filename, "r") as file:
        readFile = file.read()

    table_html = markdown.markdown(readFile, extensions=['markdown.extensions.tables', 'markdown.extensions.extra'])

    default_stylesheet = """<style>
    body {font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;}
    table {width: 100%; border-collapse: collapse; margin-top: 20px;}
    th, td {border: 1px solid #ddd; padding: 8px; text-align: left;}
    th {background-color: #f2f2f2;}
</style>
    """

    if not os.path.exists(css_filename):
        with open(css_filename, 'w') as css_file:
            css_file.write(default_stylesheet)

    # Read the stylesheet from the file
    with open(css_filename, 'r') as css_file:
        stylesheet = css_file.read()

    with open(html_filename, 'w') as html_file:
        html_file.write(f"<html><head><title>Table Viewer</title>{stylesheet}</head><body>")
        html_file.write(table_html)
        html_file.write("</body></html>")
    webbrowser.open_new_tab(html_filename)


def save_as_csv():
    text = input_label_input.get("1.0", tk.END)
    name = input_name_input.get("1.0", tk.END).strip()
    with open(text_filename, "w") as file:
        file.write(text)
    with open(text_filename, "r") as file:
        readFile = file.read()

    table_html = markdown.markdown(readFile, extensions=['markdown.extensions.tables', 'markdown.extensions.extra'])
    soup = BeautifulSoup(table_html, 'html.parser')
    table = soup.find('table')
    if table is None:
        messagebox.showerror("Error", "No table found. Cannot save as CSV.", parent=root)
        return

    csv_filename = f"{name}_table.csv"
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

            lexer = get_lexer_by_name(language, stripall=True)
            formatter = HtmlFormatter(style='friendly', full=True)
            highlighted_code = highlight(code, lexer, formatter)
            html_code += highlighted_code
        i += 1

    with open(html_filename, 'w') as html_file:
        html_file.write(html_code)
    webbrowser.open_new_tab(html_filename)

def create_styled_frame(parent, padx=10, pady=10):
    frame = ttk.Frame(parent)
    frame.pack(fill='x', padx=padx, pady=pady)
    return frame

def create_label(frame, text):
    label = ttk.Label(frame, text=text, font=("Arial", 12))
    label.pack(side='left', padx=5, pady=5)
    return label

def create_text_input(frame, width, height):
    text_input = tk.Text(frame, wrap=tk.WORD, width=width, height=height, font=("Arial", 10))
    text_input.pack(side='left', padx=5, pady=5, fill='x', expand=True)
    return text_input

def create_button(frame, text, command, style=None):
    button = ttk.Button(frame, text=text, command=command, style=style)
    button.pack(side='left', padx=5, pady=5)
    return button

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
        global settings
        settings[setting] = value

    def save_settings():
        with open(settings_filename, 'w') as new_settings_file:
            json.dump(settings, new_settings_file, indent=2)
        messagebox.showinfo("Settings", "Settings saved successfully!", parent=settings_window)

    def reset_to_default():
        global settings
        settings = default_settings.copy()
        for setting, value in settings.items():
            if setting in scales:
                scales[setting].set(value)

    scales = {}
    for setting, value in settings.items():
        if setting in setting_ranges:
            min_val, max_val = setting_ranges[setting]
            scale = Scale(scrollable_frame, from_=min_val, to=max_val, label=setting.replace("_", " ").capitalize(), orient=tk.HORIZONTAL, command=lambda v, s=setting: update_setting(s, int(v)))
            scale.set(value)
            scale.pack(padx=30, pady=10)
            scales[setting] = scale

    reset_button = ttk.Button(scrollable_frame, text="Reset to Default", command=reset_to_default)
    reset_button.pack(pady=10)

    save_settings_button = ttk.Button(scrollable_frame, text="Save Settings", command=save_settings)
    save_settings_button.pack(pady=10)

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

style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=('Arial', 10), borderwidth='1')
style.configure('Big.TButton', font=('Arial', 20, 'bold'))
style.configure('TLabel', font=('Arial', 12), background='light grey')
style.configure('TFrame', background='light grey')

header_frame = create_styled_frame(root)
input_frame = create_styled_frame(root)
button_frame = create_styled_frame(root)

checkbox_var = tk.IntVar()
checkbox = ttk.Checkbutton(header_frame, text="Code Mode", variable=checkbox_var)
checkbox.pack(side='left', padx=5, pady=5)

input_name = tk.Label(root, text="Enter Table Name:")
input_name.pack()

input_name_input = tk.Text(root, wrap=tk.WORD, width=settings["input_name_input_width"], height=settings["input_name_input_height"])
input_name_input.pack()

settings_button = create_button(header_frame, text="Settings", command=open_settings_window)
settings_button.pack(side='right', padx=5, pady=5)  

create_label(input_frame, "Enter Markdown Text:")
input_label_input = create_text_input(input_frame, settings["input_label_input_width"], settings["input_label_input_height"])

create_button(button_frame, "Run", execute)
create_button(button_frame, "Save Table as CSV", save_as_csv)

root.geometry(f"{settings['window_width']}x{settings['window_height']}")

root.mainloop()

if os.path.exists(html_filename):
    os.remove(html_filename)
    
if os.path.exists(text_filename):
    os.remove(text_filename)

