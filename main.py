import sys
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
    global selected_path
    selected_path = askdirectory(title='Selecione a pasta onde estão as fotos')
    selected_path_label.configure(fg="#000")

    if selected_path == "":
        selected_path_label.configure(fg="#FF0000")
        files_path_text.set("Nenhuma pasta foi selecionada.")
        files_found_text.set("")
        return

    files_path_text.set(selected_path)
    scan_selected_path()


def scan_selected_path():
    global files
    files = [
        f for f in listdir(selected_path)
        if isfile(join(selected_path, f))
           and f.upper().endswith((".JPG", ".JPEG", ".PNG", ".GIF", ".MOV", ".MP4", ".AVI", ".JFIF", ".WEBP"))
    ]

    global total_files
    total_files = len(files)

    if total_files == 0:
        files_found_text.set("Não há arquivos na pasta selecionada.")

    files_found_text.set(f"{total_files} arquivos encontrados.")
    start_button['state'] = 'normal'


def process_files():
    global progress
    global elapsed_time
    global current_file
    global progress_frame
    global progress_bar

    progress.set(0)

    start_button['state'] = "disabled"
    start = time()

    progress_frame.destroy()
    progress_frame = Frame(tk_root, pady=20)

    Label(progress_frame, textvariable=current_file).pack()

    progress_bar.destroy()
    progress_bar = ttk.Progressbar(
        progress_frame,
        orient='horizontal',
        mode='determinate',
        length=300,
        maximum=total_files,
        variable=progress,
    )

    progress_bar.pack(side=LEFT, padx=10)
    ttk.Label(progress_frame, textvariable=elapsed_time).pack(side=LEFT)

    progress_frame.pack()

    files_renamed = 0
    for i, file_name in enumerate(files):
        current_file.set(file_name)

        file_path = f'{selected_path}/{file_name}'
        file_extension = splitext(file_path)[1]
        file = PilImage.open(f'{file_path}')
        exif = file.getexif()
        file.close()

        if not exif:
            print(f'{colors.bcolors.DANGER}ERRO: O arquivo {file_name} não contém o metadado. {colors.bcolors.ENDC}')
            tk_root.update_idletasks()
            progress.set(progress.get() + 1)
            break

        date_taken = exif[306]
        formatted_date_taken = datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
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
        sleep(0.5)

        tk_root.update_idletasks()
        progress.set(progress.get() + 1)

        end = time()
        elapsed_time.set((int(end - start), 's'))

    current_file.set('')
    start_button['state'] = "normal"


tk_root = Tk()
tk_root.geometry('500x300')
tk_root.resizable(False, False)
tk_root.title("Organizar fotos")

selected_path = ''
files_path_text = StringVar()
files_found_text = StringVar()
current_file = StringVar()
files = []
total_files = 0
progress = DoubleVar()
elapsed_time = StringVar()
progress_frame = Frame(tk_root, pady=20)
progress_bar = ttk.Progressbar()

Button(tk_root, text="Selecionar pasta", command=lambda: ask_files_path()).pack(pady=10)
selected_path_label = Label(tk_root, textvariable=files_path_text)
selected_path_label.pack()
Label(tk_root, textvariable=files_found_text, fg='#008f00').pack()
start_button = Button(tk_root, text="Iniciar", command=lambda: process_files())
start_button['state'] = "disabled"
start_button.pack(side=BOTTOM, pady=10)

tk_root.mainloop()
