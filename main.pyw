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

    log_file = open(f"./logs/log-{time()}.txt", "a", encoding="utf-8")

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
        current_file.set(file_name)
        current_file_label.update()

        file_path = f'{selected_path}/{file_name}'
        file_extension = splitext(file_path)[1]

        exif = None
        date_taken = None

        if file_extension.upper() in image_extensions:
            file = PilImage.open(f'{file_path}')
            
            try:
                exif = piexif.load(file.info['exif'])
            except KeyError:
                exif = None
            finally:
                file.close()
        else:
            continue

        try: 
            if exif:
                if 36867 in exif.get("Exif", {}):
                    date_taken = exif["Exif"][36867].decode('utf-8')
                
                if 306 in exif.get("Exif", {}):
                    date_taken = exif["Exif"][306].decode('utf-8')
                    
                if date_taken and date_taken != "0000:00:00 00:00:00":
                    formatted_date_taken = datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
                    formatted_date_taken = formatted_date_taken.strftime('%d-%m-%Y %H-%M-%S')
            else:                
                formatted_date_taken = None
                is_screenshot = file_name.startswith("Screenshot_")
                is_img_type1 = file_name.startswith("IMG-")
                is_img_type2 = file_name.startswith("IMG_")
                is_vid_type1 = file_name.startswith("VID-")
                is_vid_type2 = file_name.startswith("VID_")
                
                if is_screenshot:
                    file_date = file_name.split("_")[1]
                    file_date_pieces = file_date.split("-")

                    if len(file_date_pieces) > 2:
                        date_year, date_month, date_day, date_hours, date_minutes, date_seconds, *trash = file_date.split("-")
                    elif len(file_date_pieces) == 2:
                        file_date, file_time = file_date.split("-")
                        date_year = file_date[0:4]
                        date_month = file_date[4:6]
                        date_day = file_date[6:8]
                        date_hours = file_time[0:2]
                        date_minutes = file_time[2:4]
                        date_seconds = file_time[4:6]

                    formatted_date_taken = f'{date_day}-{date_month}-{date_year} {date_hours}-{date_minutes}-{date_seconds}'
                elif is_img_type1 or is_vid_type1:
                    file_date = file_name.split("-")[1]
                    date_year = file_date[0:4]
                    date_month = file_date[4:6]
                    date_day = file_date[6:8]
                    formatted_date_taken = f'{date_day}-{date_month}-{date_year}'
                elif is_vid_type2 or is_img_type2:
                    file_date_pieces = file_name.split("_")

                    if len(file_date_pieces) >= 3:
                        trash, file_date, file_time, *trash = file_date_pieces

                        date_year = file_date[0:4]
                        date_month = file_date[4:6]
                        date_day = file_date[6:8]
                        date_hours = file_time[0:2]
                        date_minutes = file_time[2:4]
                        date_seconds = file_time[4:6]
                        formatted_date_taken = f'{date_day}-{date_month}-{date_year} {date_hours}-{date_minutes}-{date_seconds}'
                elif getmtime(file_path):
                    formatted_date_taken = datetime.fromtimestamp(getmtime(file_path)).strftime('%d-%m-%Y %H-%M-%S')
        except Exception as e:
            log_file.write(e.__str__())
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado.")
            tk_root.destroy()

        if formatted_date_taken:
            new_file_name = f'{formatted_date_taken}{file_extension}'
            new_file_path = f'{selected_path}/{new_file_name}'  
            repeated_file_counter = 0
            
            while isfile(new_file_path) == 1:
                repeated_file_counter += 1
                new_file_name = f'{formatted_date_taken}-{repeated_file_counter}{file_extension}'
                new_file_path = f'{selected_path}/{new_file_name}'

            rename(f'{file_path}', f'{new_file_path}')
            files_renamed += 1

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
