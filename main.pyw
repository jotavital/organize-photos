from os import listdir, rename, makedirs
from os.path import isfile, join, splitext, exists, getmtime
from PIL import Image as PilImage
import piexif
from datetime import datetime, timedelta
from time import time
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from pillow_heif import register_heif_opener

register_heif_opener()

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

    if not exists("logs"):
        makedirs("logs")

    log_file = open(f"./logs/log-{datetime.now().strftime('%Y-%m-%d')}.txt", "a", encoding="utf-8")

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
    for file_name in files:
        current_file.set(file_name)
        current_file_label.update()

        file_path = f'{selected_path}/{file_name}'
        file_extension = splitext(file_path)[1]

        exif = None
        date_taken = None
        formatted_date_taken = None

        if file_extension.upper() in image_extensions:
            file = PilImage.open(f'{file_path}')
            
            try:
                exif = piexif.load(file.info['exif'])
            except Exception as e:
                log_file.write(e.__str__())
                exif = None
            finally:
                file.close()

        try: 
            if exif:
                if 36867 in exif.get("Exif", {}):
                    date_taken = exif["Exif"][36867].decode('utf-8')
                
                if 306 in exif.get("Exif", {}):
                    date_taken = exif["Exif"][306].decode('utf-8')
                    
                if date_taken and date_taken != "0000:00:00 00:00:00":
                    formatted_date_taken = datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
                    year_taken = formatted_date_taken.year
                    formatted_date_taken = formatted_date_taken.strftime('%d-%m-%Y %H-%M-%S')
                    
            if not formatted_date_taken:
                if getmtime(file_path):
                    formatted_date_taken = datetime.fromtimestamp(getmtime(file_path)).strftime('%d-%m-%Y %H-%M-%S')
                    year_taken = datetime.fromtimestamp(getmtime(file_path)).year
        except Exception as e:
            log_file.write(e.__str__())
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado.")
            tk_root.destroy()

        if formatted_date_taken:
            new_file_folder = f'{selected_path}'
            new_file_name = f'{formatted_date_taken}{file_extension}'
            
            if should_organize_photos_by_year.get():
                new_file_folder = f'{selected_path}/{year_taken}'
                if not exists(new_file_folder):
                    makedirs(new_file_folder)
            
            repeated_file_counter = 0
            while True:
                try:
                    rename(f'{file_path}', f'{new_file_folder}/{new_file_name}')
                    files_renamed += 1
                    break
                except FileExistsError:
                    repeated_file_counter += 1
                    new_file_name = f'{formatted_date_taken} ({repeated_file_counter}){file_extension}'

        tk_root.update_idletasks()
        progress.set(progress.get() + 1)
        
        end = time()
        elapsed_time.set(str(timedelta(seconds=int(end - start))))

    current_file.set('')
    current_file_label.update()

    final_message_label.configure(fg='#008f00')
    final_message.set(f"Sucesso! {files_renamed} arquivos renomeados.")
    log_file.close()


tk_root = Tk()
tk_root.geometry('700x700')
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
should_organize_photos_by_year = IntVar()

top_frame = Frame(tk_root)
top_frame.pack(fill=X)

settings_frame = Frame(tk_root, pady=10)
settings_frame.pack(fill=X)

progress_frame = Frame(tk_root, pady=10)
progress_frame.pack(fill=X)

current_file_label = Label(progress_frame, textvariable=current_file)
current_file_label.pack()

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

Checkbutton(
    settings_frame,
    text="Organizar as fotos em pastas por ano",
    variable=should_organize_photos_by_year,
    onvalue=1,
    offvalue=0,
    command=lambda: None,
).pack(side=BOTTOM, pady=10)

image_extensions = [".JPG", ".JPEG", ".HEIC", ".PNG", ".JFIF", ".DNG", ".WEBP"]
video_extensions = [".MOV", ".MP4", ".AVI", ".GIF"]
extension_options = image_extensions + video_extensions
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
