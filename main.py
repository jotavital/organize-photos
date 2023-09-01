import sys
from os import listdir, rename
from os.path import isfile, join, splitext
from PIL import Image as PilImage
import colors
from datetime import datetime
from time import sleep
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory

def ask_photos_path():
    global selected_path
    selected_path = askdirectory(title='Selecione a pasta onde estão as fotos')
    selected_path_label.configure(fg="#000")

    if selected_path == "":
        selected_path_label.configure(fg="#FF0000")
        files_path_text.set("Nenhuma pasta foi selecionada.")
        files_found_text.set("")
        return

    files_path_text.set(selected_path)
    scan_for_files()


def scan_for_files():
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
    start_button['state'] = "disabled"

    progress_bar = ttk.Progressbar(tk_root, orient='horizontal', mode='determinate', length=300, maximum=total_files)
    progress_bar.pack()
    progress_bar.start()

    files_renamed = 0
    for file_name in files:
        print(file_name)
        file_path = f'{selected_path}/{file_name}'
        file_extension = splitext(file_path)[1]
        file = PilImage.open(f'{file_path}')
        exif = file.getexif()
        file.close()

        if not exif:
            print(f'{colors.bcolors.DANGER}ERRO: O arquivo {file_name} não contém o metadado. {colors.bcolors.ENDC}')
            tk_root.update_idletasks()
            progress_bar.step(1)
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
        progress_bar.step(1)

    tk_root.update_idletasks()
    progress_bar.stop()


tk_root = Tk()
tk_root.geometry('500x200')
tk_root.resizable(False, False)
tk_root.title("Organizar fotos")

selected_path = ''
files_path_text = StringVar()
files_found_text = StringVar()
files = []
total_files = 0

Button(tk_root, text="Selecionar pasta", command=lambda: ask_photos_path()).pack()
selected_path_label = Label(tk_root, textvariable=files_path_text)
selected_path_label.pack()
Label(tk_root, textvariable=files_found_text).pack()
start_button = Button(tk_root, text="Iniciar", command=lambda: process_files())
start_button['state'] = "disabled"
start_button.pack()

tk_root.mainloop()

# bar = ChargingBar(f'Processando ', max=100)
# bar.color = "blue"
#
# files_renamed = 0
# for file_name in files:
#     bar.bar_prefix = f'{file_name}  '
#     bar.suffix = f'%(percent)d%% {bar.elapsed}s'
#
#     file_path = f'{selected_path}/{file_name}'
#     file_extension = splitext(file_path)[1]
#     file = Image.open(f'{file_path}')
#     exif = file.getexif()
#     file.close()
#
#     if not exif:
#         print(f'{colors.bcolors.DANGER}ERRO: O arquivo {file_name} não contém o metadado. {colors.bcolors.ENDC}')
#         bar.next()
#         break
#
#     date_taken = exif[306]
#     formatted_date_taken = datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
#     formatted_date_taken = formatted_date_taken.strftime('%d-%m-%Y %H-%M-%S')
#
#     new_file_name = f'{formatted_date_taken}{file_extension}'
#     new_file_path = f'{selected_path}/{new_file_name}'
#
#     repeated_file_counter = 0
#     while isfile(new_file_path) == 1:
#         repeated_file_counter += 1
#         new_file_name = f'{formatted_date_taken}-{repeated_file_counter}{file_extension}'
#         new_file_path = f'{selected_path}/{new_file_name}'
#
#     rename(f'{file_path}', f'{new_file_path}')
#     files_renamed += 1
#     sleep(0.1)
#     bar.next()
#
# bar.finish()
# print(f"{colors.bcolors.SUCCESS}{files_renamed} arquivos renomeados em {bar.elapsed} segundos.{colors.bcolors.ENDC}")
