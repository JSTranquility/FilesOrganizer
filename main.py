import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
import threading

# Tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('650x550')
        self.title("📁 File Organizer")
        self.resizable(False, False)
        
        # Agregar icono a la ventana
        try:
            self.iconbitmap('icon.ico')
        except:
            pass  # Si no existe el archivo, continúa sin icono
        
        # Configurar la ventana
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.path = ""
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, corner_radius=20)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="📁 File Organizer",
            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"),
            text_color="#00D9FF"
        )
        title_label.grid(row=0, column=0, pady=(20, 10))
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Organiza tus archivos automáticamente por tipo",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color="gray"
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # Card de carpeta seleccionada
        folder_card = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1a1a1a")
        folder_card.grid(row=2, column=0, sticky="ew", padx=20, pady=15)
        folder_card.grid_columnconfigure(0, weight=1)
        
        folder_label_title = ctk.CTkLabel(
            folder_card,
            text="📂 Carpeta Seleccionada",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00D9FF"
        )
        folder_label_title.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))
        
        self.path_label = ctk.CTkLabel(
            folder_card,
            text="No hay carpeta seleccionada",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=500,
            justify="left"
        )
        self.path_label.grid(row=1, column=0, sticky="w", padx=15, pady=(5, 10))
        
        # Frame para botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=20)
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Botón Seleccionar Carpeta
        select_btn = ctk.CTkButton(
            button_frame,
            text="📁 Seleccionar Carpeta",
            command=self.gettingPath,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=12,
            height=50,
            fg_color="#00D9FF",
            hover_color="#00B8D4",
            text_color="#000000"
        )
        select_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Botón Organizar
        organize_btn = ctk.CTkButton(
            button_frame,
            text="✨ Organizar Archivos",
            command=self.startOperation,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=12,
            height=50,
            fg_color="#00D962",
            hover_color="#00A847",
            text_color="#000000"
        )
        organize_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # Barra de información
        info_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#1a1a1a")
        info_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=15)
        info_frame.grid_columnconfigure(0, weight=1)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="Extensiones soportadas: PNG, JPG, JPEG, TXT, PDF, DOCX, XLSX, EXE, MP3, MP4",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            wraplength=500,
            justify="left"
        )
        info_label.grid(row=0, column=0, sticky="ew", padx=15, pady=12)

    
    def gettingPath(self):
        self.path = filedialog.askdirectory(title="Selecciona una carpeta para organizar")
        if self.path:
            self.path_label.configure(text=self.path)

    def startOperation(self):
        if not self.path:
            messagebox.showerror("Error", "Por favor selecciona una carpeta primero")
            return

        file_list = os.listdir(self.path)

        if len(file_list) == 0:
            messagebox.showerror("Error", "La carpeta está vacía")
            return

        # Ejecutar en un thread para no congelar la UI
        thread = threading.Thread(target=self._organize_files, args=(file_list,))
        thread.start()
    
    def _organize_files(self, file_list):
        count = 0

        extensions = {
            ".png": "PngFiles",
            ".jpg": "ImageFiles",
            ".jpeg": "ImageFiles",
            ".txt": "TextFiles",
            ".pdf": "PdfFiles",
            ".docx": "DocxFiles",
            ".xlsx": "ExcelFiles",
            ".exe": "ExecutableFiles",
            ".mp3": "AudioFiles",
            ".mp4": "VideoFiles"
        }

        for file in file_list:
            file_path = os.path.join(self.path, file)

            if not os.path.isfile(file_path):
                continue

            _, ext = os.path.splitext(file)
            ext = ext.lower()

            folder_name = extensions.get(ext, "OtherFiles")
            new_path = os.path.join(self.path, folder_name)


            if not os.path.exists(new_path):
                os.mkdir(new_path)


            dest_file = os.path.join(new_path, file)
            if os.path.exists(dest_file):
                base, extension = os.path.splitext(file)
                i = 1
                while os.path.exists(dest_file):
                    dest_file = os.path.join(
                        new_path, f"{base}_{i}{extension}")
                    i += 1

            shutil.move(file_path, dest_file)
            count += 1

        self.after(0, lambda: messagebox.showinfo(
            "✅ ¡Éxito!", 
            f"Se organizaron {count} archivos correctamente"
        ))



if __name__ == '__main__':
    app = GUI()
    app.mainloop()
