import customtkinter as ctk
from tkinter import filedialog, messagebox
from core import PhotoOrganizerCore
import threading
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.core = PhotoOrganizerCore()
        self.stop_event = threading.Event()
        self.files_to_process = []
        self.selected_path = ""

        self.title("Organizador de fotos")
        self.geometry("900x650")

        icon_path = self.core.get_resource_path("app_icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Configurações",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        self.desc_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Renomeie e organize suas fotos/vídeos pela data original de captura.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=220,
        )
        self.desc_label.grid(row=1, column=0, padx=15, pady=(0, 15))

        self.select_folder_btn = ctk.CTkButton(
            self.sidebar_frame, text="Selecionar Pasta", command=self.select_folder
        )
        self.select_folder_btn.grid(row=2, column=0, padx=20, pady=5)

        self.folder_path_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Nenhuma pasta selecionada",
            text_color="gray",
            wraplength=200,
        )
        self.folder_path_label.grid(row=3, column=0, padx=20, pady=(0, 10))

        self.organize_year_switch = ctk.CTkSwitch(
            self.sidebar_frame, text="Criar pastas por ano"
        )
        self.organize_year_switch.grid(row=4, column=0, padx=20, pady=5, sticky="w")

        self.extensions_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Extensões:",
            anchor="w",
            font=ctk.CTkFont(weight="bold"),
        )
        self.extensions_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.sidebar_frame, label_text="Selecionar Tipos"
        )
        self.scrollable_frame.grid(
            row=6, column=0, padx=20, pady=(5, 20), sticky="nsew"
        )

        self.check_vars = []
        all_exts = self.core.all_extensions

        self.select_all_var = ctk.IntVar(value=1)
        self.select_all_check = ctk.CTkCheckBox(
            self.scrollable_frame,
            text="Selecionar Todos",
            command=self.toggle_all,
            variable=self.select_all_var,
        )
        self.select_all_check.pack(pady=5, anchor="w")

        for ext in all_exts:
            var = ctk.IntVar(value=1)
            chk = ctk.CTkCheckBox(
                self.scrollable_frame,
                text=ext,
                variable=var,
                command=self.update_file_count,
            )
            chk.pack(pady=2, anchor="w")
            self.check_vars.append((ext, var, chk))

        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.status_header = ctk.CTkLabel(
            self.main_frame,
            text="Status da Organização",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.status_header.grid(row=0, column=0, sticky="w", pady=(0, 20))

        self.status_container = ctk.CTkFrame(self.main_frame)
        self.status_container.grid(row=1, column=0, sticky="nsew")
        self.status_container.grid_columnconfigure(0, weight=1)

        self.files_found_label = ctk.CTkLabel(
            self.status_container,
            text="Aguardando seleção...",
            font=ctk.CTkFont(size=16),
        )
        self.files_found_label.pack(pady=(40, 10))

        self.current_file_label = ctk.CTkLabel(
            self.status_container, text="", text_color="gray"
        )
        self.current_file_label.pack(pady=(5, 5))

        self.progress_bar = ctk.CTkProgressBar(self.status_container)
        self.progress_bar.pack(pady=10, padx=50, fill="x")
        self.progress_bar.set(0)

        self.time_info_frame = ctk.CTkFrame(
            self.status_container, fg_color="transparent"
        )
        self.time_info_frame.pack(pady=(0, 20), padx=50, fill="x")

        self.elapsed_label = ctk.CTkLabel(
            self.time_info_frame, text="Decorrrido: 00:00", font=ctk.CTkFont(size=12)
        )
        self.elapsed_label.pack(side="left")

        self.eta_label = ctk.CTkLabel(
            self.time_info_frame, text="Restante: --:--", font=ctk.CTkFont(size=12)
        )
        self.eta_label.pack(side="right")

        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)

        self.start_btn = ctk.CTkButton(
            self.buttons_frame,
            text="INICIAR ORGANIZAÇÃO",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled",
            fg_color="green",
            hover_color="darkgreen",
            command=self.start_processing,
        )
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.cancel_btn = ctk.CTkButton(
            self.buttons_frame,
            text="CANCELAR",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled",
            fg_color="darkred",
            hover_color="#800000",
            command=self.cancel_processing,
        )
        self.cancel_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.selected_path = path
            self.folder_path_label.configure(text=path, text_color="white")
            self.update_file_count()

    def toggle_all(self):
        val = self.select_all_var.get()
        for _, var, _ in self.check_vars:
            var.set(val)
        self.update_file_count()

    def update_file_count(self):
        if not self.selected_path:
            return

        selected_exts = [ext for ext, var, _ in self.check_vars if var.get() == 1]
        self.files_to_process = self.core.scan_directory(
            self.selected_path, selected_exts
        )

        count = len(self.files_to_process)
        self.files_found_label.configure(
            text=f"{count} arquivos encontrados prontos para processar."
        )

        if count > 0:
            self.start_btn.configure(state="normal")
        else:
            self.start_btn.configure(state="disabled")

    def format_time(self, seconds):
        if seconds < 0:
            seconds = 0
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def start_processing(self):
        self.stop_event.clear()
        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.select_folder_btn.configure(state="disabled")
        self.progress_bar.set(0)

        organize_by_year = self.organize_year_switch.get() == 1

        threading.Thread(
            target=self.run_logic, args=(organize_by_year,), daemon=True
        ).start()

    def cancel_processing(self):
        if messagebox.askyesno("Cancelar", "Deseja realmente parar o processo?"):
            self.stop_event.set()
            self.current_file_label.configure(
                text="Cancelando... Aguarde terminar o arquivo atual."
            )

    def run_logic(self, organize_by_year):
        def progress_callback(current, total, filename, elapsed, eta):
            progress_val = current / total
            self.progress_bar.set(progress_val)
            self.current_file_label.configure(text=f"Processando: {filename}")

            self.elapsed_label.configure(text=f"Decorrido: {self.format_time(elapsed)}")
            self.eta_label.configure(text=f"Restante: {self.format_time(eta)}")

            self.update_idletasks()

        renamed_count = self.core.process_renaming(
            self.files_to_process,
            self.selected_path,
            organize_by_year,
            progress_callback,
            self.stop_event,
        )

        self.after(0, lambda: self.finish_process(renamed_count))

    def finish_process(self, count):
        status_text = "Processo concluído!"
        if self.stop_event.is_set():
            status_text = "Processo cancelado pelo usuário."
            messagebox.showwarning(
                "Cancelado",
                f"Operação interrompida.\n{count} arquivos foram processados antes do cancelamento.",
            )
        else:
            self.current_file_label.configure(text="Concluído!")
            messagebox.showinfo(
                "Sucesso", f"{count} arquivos foram renomeados e organizados."
            )

        self.current_file_label.configure(text=status_text)
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.select_folder_btn.configure(state="normal")
        self.update_file_count()


if __name__ == "__main__":
    app = App()
    app.mainloop()
