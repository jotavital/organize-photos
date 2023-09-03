from os import listdir, rename
from os.path import isfile, join, splitext
from PIL import Image as PilImage
import colors
from datetime import datetime
from time import sleep, time
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory


def ask_files_path():
    search_files_button['state'] = "disabled"
    global selected_path
    global files_found_text

    start_button['state'] = 'disabled'
    selected_path = askdirectory(title='Selecione a pasta onde estão as fotos')
    selected_path_label.configure(fg="#000")

    if selected_path == "":
        selected_path_label.configure(fg="#FF0000")
        files_path_text.set("Nenhuma pasta foi selecionada.")
        files_found_text.set("")
        return

    files_path_text.set(selected_path)
    files_found_text.set('')
    search_files_button['state'] = "normal"


def scan_selected_path():
    global files
    global total_files

    extensions_to_process = []

    # código duplicado, transformar em funcao
    for c, t in enumerate(selected_extensions):
        if t.get():
            extensions_to_process.append(extension_options[c])

    if len(extensions_to_process) == 0:
        files_found_label.configure(fg="red")
        files_found_text.set("Selecione ao menos um formato!")
        return

    final_message.set("")

    files = [
        f for f in listdir(selected_path)
        if isfile(join(selected_path, f))
           and f.upper().endswith(tuple(extensions_to_process))
    ]

    total_files = len(files)

    if total_files == 0:
        files_found_label.configure(fg="red")
        files_found_text.set("Não encontramos na pasta selecionada.")

    files_found_label.configure(fg="#008f00")
    files_found_text.set(f"{total_files} arquivos encontrados.")
    start_button['state'] = 'normal'


def process_files():
    global progress
    global elapsed_time
    global current_file
    global progress_frame
    global progress_bar
    global selected_extensions

    extensions_to_process = []

    for c, t in enumerate(selected_extensions):
        if t.get():
            extensions_to_process.append(extension_options[c])

    if len(extensions_to_process) == 0:
        final_message_label.configure(fg="red")
        final_message.set("Selecione ao menos um formato!")
        return

    final_message.set("")

    progress.set(0)

    start_button['state'] = "disabled"
    start = time()

    progress_bar.configure(maximum=total_files)

    files_renamed = 0
    for i, file_name in enumerate(files):
        current_file.set('')
        current_file.set(file_name)

        file_path = f'{selected_path}/{file_name}'
        file_extension = splitext(file_path)[1]
        file = PilImage.open(f'{file_path}')
        exif = file.getexif()
        file.close()

        if not exif or not (306 in exif) or exif[306] == "0000:00:00 00:00:00":
            print(f'{colors.bcolors.DANGER}ERRO: O arquivo {file_name} não contém o metadado. {colors.bcolors.ENDC}')
            tk_root.update_idletasks()
            progress.set(progress.get() + 1)
            continue

        date_taken = exif[306]

        formatted_date_taken = None

        try:
            formatted_date_taken = datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
        except ValueError:
            print(f'{colors.bcolors.DANGER}ERRO: O arquivo {file_name} contém um formato inválido do metadado. {colors.bcolors.ENDC}')
            continue

        formatted_date_taken = formatted_date_taken.strftime('%d-%m-%Y %H-%M-%S')

        new_file_name = f'{formatted_date_taken}{file_extension}'
        new_file_path = f'{selected_path}/{new_file_name}'

        repeated_file_counter = 0
        while isfile(new_file_path) == 1:
            repeated_file_counter += 1
            new_file_name = f'{formatted_date_taken}-{repeated_file_counter}{file_extension}'
            new_file_path = f'{selected_path}/{new_file_name}'

        rename(f'{file_path}', f'{new_file_path}')
        files_renamed += 1
        sleep(0.1)

        tk_root.update_idletasks()
        progress.set(progress.get() + 1)

        end = time()
        elapsed_time.set((int(end - start), 's'))

    current_file.set('')

    final_message_label.configure(fg='#008f00')
    final_message.set(f"Sucesso! {files_renamed} arquivos renomeados.")


tk_root = Tk()
tk_root.geometry('700x600')
tk_root.resizable(False, False)
tk_root.title("Organizador de fotos")

# Variables
selected_path = ''
files_path_text = StringVar()
files_found_text = StringVar()
current_file = StringVar()
files = []
total_files = 0
progress = DoubleVar()
elapsed_time = StringVar()
final_message = StringVar()

top_frame = Frame(tk_root)
top_frame.pack(fill=X)

settings_frame = Frame(tk_root, pady=10)
settings_frame.pack(fill=X)

progress_frame = Frame(tk_root, pady=10)
progress_frame.pack(fill=X)
Label(progress_frame, textvariable=current_file).pack()

progress_bar_frame = Frame(progress_frame, pady=10)
progress_bar_frame.pack()
progress_bar = ttk.Progressbar(
    progress_bar_frame,
    orient='horizontal',
    mode='determinate',
    length=300,
    variable=progress,
)
progress_bar.pack(side=LEFT, padx=10)
Label(progress_bar_frame, textvariable=elapsed_time).pack(side=LEFT)

bottom_frame = Frame(tk_root)
bottom_frame.pack(fill=X)
final_message_label = (Label(bottom_frame, textvariable=final_message, fg='#008f00'))
final_message_label.pack(side=BOTTOM)

start_button = Button(bottom_frame, text="Iniciar", command=lambda: process_files())
start_button['state'] = "disabled"
start_button.pack()

Button(top_frame, text="Selecionar pasta", command=lambda: ask_files_path()).pack(pady=10)
search_files_button = Button(settings_frame, text="Buscar arquivos", command=lambda: scan_selected_path())
search_files_button['state'] = "disabled"
search_files_button.pack(side=BOTTOM, pady=10)
selected_path_label = Label(top_frame, textvariable=files_path_text)
selected_path_label.pack()
files_found_label = Label(settings_frame, textvariable=files_found_text, fg='#008f00')  # transformar cor em constante
files_found_label.pack(side=BOTTOM);

extension_options = [".JPG", ".JPEG", ".PNG", ".JFIF", ".WEBP"]
selected_extensions = []

Label(settings_frame, text='Quais formatos deseja organizar?', pady=10).pack()

for i, option in enumerate(extension_options):
    selected_extensions.append(IntVar())

    Checkbutton(
        settings_frame,
        text=option,
        variable=selected_extensions[i],
        onvalue=1,
        offvalue=0,
        command=lambda: None,
    ).pack()

tk_root.mainloop()
