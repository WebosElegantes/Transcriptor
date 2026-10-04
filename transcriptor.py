import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import whisper
import threading

# ---------- Paleta ----------
COLOR_FONDO = "#EDF1F7"
COLOR_TARJETA = "#FFFFFF"
COLOR_ENCABEZADO = "#24344D"
COLOR_ENCABEZADO_TEXTO = "#FFFFFF"
COLOR_ENCABEZADO_SUB = "#A9B8D0"
COLOR_PRIMARIO = "#2563EB"
COLOR_PRIMARIO_HOVER = "#1D4ED8"
COLOR_SECUNDARIO = "#E3E9F3"
COLOR_SECUNDARIO_HOVER = "#D3DCEB"
COLOR_TEXTO = "#1F2A3C"
COLOR_TEXTO_SUAVE = "#6B778C"
COLOR_BORDE = "#D5DDEA"
COLOR_DESACTIVADO_BG = "#E6EAF1"
COLOR_DESACTIVADO_FG = "#9AA5B8"

COLOR_INFO = "#2563EB"
COLOR_OK = "#15803D"
COLOR_AVISO = "#B45309"
COLOR_ERROR = "#B91C1C"
COLOR_NEUTRO = "#1F2A3C"

FUENTE = "Segoe UI"


class BotonModerno(tk.Button):
    """Botón plano con efecto hover y estilo para estado deshabilitado."""

    def __init__(self, master, texto, comando, primario=True, **kwargs):
        self.bg = COLOR_PRIMARIO if primario else COLOR_SECUNDARIO
        self.bg_hover = COLOR_PRIMARIO_HOVER if primario else COLOR_SECUNDARIO_HOVER
        self.fg = "#FFFFFF" if primario else COLOR_TEXTO

        super().__init__(
            master,
            text=texto,
            command=comando,
            font=(FUENTE, 11, "bold"),
            bg=self.bg,
            fg=self.fg,
            activebackground=self.bg_hover,
            activeforeground=self.fg,
            disabledforeground=COLOR_DESACTIVADO_FG,
            relief="flat",
            bd=0,
            padx=22,
            pady=10,
            cursor="hand2",
            **kwargs,
        )
        self.bind("<Enter>", self._al_entrar)
        self.bind("<Leave>", self._al_salir)

    def _al_entrar(self, _):
        if str(self["state"]) != "disabled":
            self.config(bg=self.bg_hover)

    def _al_salir(self, _):
        if str(self["state"]) != "disabled":
            self.config(bg=self.bg)

    def config(self, cnf=None, **kwargs):
        # Ajusta colores y cursor automáticamente al habilitar/deshabilitar
        if "state" in kwargs:
            if kwargs["state"] == tk.DISABLED:
                kwargs.setdefault("bg", COLOR_DESACTIVADO_BG)
                kwargs.setdefault("cursor", "arrow")
            else:
                kwargs.setdefault("bg", self.bg)
                kwargs.setdefault("cursor", "hand2")
        return super().config(cnf, **kwargs)

    configure = config


class TranscriptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcriptor de Audio Local")
        self.root.geometry("640x620")
        self.root.minsize(560, 520)
        self.root.configure(bg=COLOR_FONDO)

        # Variables
        self.ruta_archivo = None

        self.configurar_estilos()

        # ---------- Encabezado ----------
        encabezado = tk.Frame(root, bg=COLOR_ENCABEZADO)
        encabezado.pack(fill="x")

        tk.Label(
            encabezado,
            text="Transcriptor de Audio",
            font=(FUENTE, 20, "bold"),
            bg=COLOR_ENCABEZADO,
            fg=COLOR_ENCABEZADO_TEXTO,
        ).pack(anchor="w", padx=28, pady=(22, 0))

        tk.Label(
            encabezado,
            text="Convierte tus audios en texto, sin conexión y en tu propio equipo.",
            font=(FUENTE, 10),
            bg=COLOR_ENCABEZADO,
            fg=COLOR_ENCABEZADO_SUB,
        ).pack(anchor="w", padx=28, pady=(2, 22))

        # ---------- Contenedor principal ----------
        contenedor = tk.Frame(root, bg=COLOR_FONDO)
        contenedor.pack(fill="both", expand=True, padx=28, pady=22)

        # ---------- Tarjeta de estado ----------
        tarjeta_estado = tk.Frame(
            contenedor,
            bg=COLOR_TARJETA,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1,
        )
        tarjeta_estado.pack(fill="x")

        self.label_estado = tk.Label(
            tarjeta_estado,
            text="Cargando modelo de IA...",
            font=(FUENTE, 11, "bold"),
            bg=COLOR_TARJETA,
            fg=COLOR_INFO,
            anchor="w",
            wraplength=540,
            justify="left",
        )
        self.label_estado.pack(fill="x", padx=18, pady=(14, 8))

        self.barra_progreso = ttk.Progressbar(
            tarjeta_estado, mode="indeterminate", style="Moderna.Horizontal.TProgressbar"
        )
        self.barra_progreso.pack(fill="x", padx=18, pady=(0, 16))
        self.barra_progreso.start(12)

        # Cargamos el modelo en un hilo para no congelar el inicio
        threading.Thread(target=self.cargar_modelo, daemon=True).start()

        # ---------- Botones ----------
        fila_botones = tk.Frame(contenedor, bg=COLOR_FONDO)
        fila_botones.pack(fill="x", pady=18)

        self.btn_seleccionar = BotonModerno(
            fila_botones,
            "Seleccionar MP3",
            self.seleccionar_archivo,
            primario=False,
            state=tk.DISABLED,
        )
        self.btn_seleccionar.config(state=tk.DISABLED)
        self.btn_seleccionar.pack(side="left")

        self.btn_transcribir = BotonModerno(
            fila_botones,
            "Transcribir",
            self.iniciar_transcripcion,
            primario=True,
            state=tk.DISABLED,
        )
        self.btn_transcribir.config(state=tk.DISABLED)
        self.btn_transcribir.pack(side="left", padx=(12, 0))

        # ---------- Resultado ----------
        tk.Label(
            contenedor,
            text="Transcripción",
            font=(FUENTE, 11, "bold"),
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            anchor="w",
        ).pack(fill="x", pady=(0, 6))

        marco_texto = tk.Frame(
            contenedor,
            bg=COLOR_TARJETA,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1,
        )
        marco_texto.pack(fill="both", expand=True)

        scroll = ttk.Scrollbar(
            marco_texto, orient="vertical", style="Moderna.Vertical.TScrollbar"
        )
        scroll.pack(side="right", fill="y")

        self.texto_resultado = tk.Text(
            marco_texto,
            height=15,
            width=55,
            font=(FUENTE, 11),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            selectbackground="#BFD3FA",
            selectforeground=COLOR_TEXTO,
            relief="flat",
            bd=0,
            wrap="word",
            padx=16,
            pady=14,
            spacing2=4,
            yscrollcommand=scroll.set,
        )
        self.texto_resultado.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.texto_resultado.yview)

    def configurar_estilos(self):
        estilo = ttk.Style(self.root)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure(
            "Moderna.Horizontal.TProgressbar",
            troughcolor=COLOR_SECUNDARIO,
            background=COLOR_PRIMARIO,
            bordercolor=COLOR_SECUNDARIO,
            lightcolor=COLOR_PRIMARIO,
            darkcolor=COLOR_PRIMARIO,
            thickness=6,
        )
        estilo.configure(
            "Moderna.Vertical.TScrollbar",
            troughcolor=COLOR_TARJETA,
            background=COLOR_SECUNDARIO,
            bordercolor=COLOR_TARJETA,
            arrowcolor=COLOR_TEXTO_SUAVE,
            relief="flat",
        )
        estilo.map(
            "Moderna.Vertical.TScrollbar",
            background=[("active", COLOR_SECUNDARIO_HOVER)],
        )

    def cargar_modelo(self):
        # Modelos disponibles: tiny, base, small, medium, large
        self.modelo = whisper.load_model("medium")
        self.barra_progreso.stop()
        self.label_estado.config(text="Modelo listo. Esperando archivo.", fg=COLOR_OK)
        self.btn_seleccionar.config(state=tk.NORMAL)

    def seleccionar_archivo(self):
        self.ruta_archivo = filedialog.askopenfilename(
            title="Selecciona un archivo de audio",
            filetypes=[("Archivos MP3", "*.mp3"), ("Todos los archivos", "*.*")]
        )
        if self.ruta_archivo:
            self.label_estado.config(text=f"Archivo cargado: {self.ruta_archivo.split('/')[-1]}", fg=COLOR_NEUTRO)
            self.btn_transcribir.config(state=tk.NORMAL)

    def iniciar_transcripcion(self):
        self.btn_transcribir.config(state=tk.DISABLED)
        self.label_estado.config(text="Transcribiendo... (Esto puede tomar un momento)", fg=COLOR_AVISO)
        self.barra_progreso.start(12)
        self.texto_resultado.delete(1.0, tk.END)

        # Ejecutar la transcripción en un hilo separado
        hilo = threading.Thread(target=self.procesar_audio)
        hilo.start()

    def procesar_audio(self):
        try:
            # La IA hace el trabajo aquí
            resultado = self.modelo.transcribe(self.ruta_archivo, language="es")

            # Mostrar resultado
            self.texto_resultado.insert(tk.END, resultado["text"])
            self.label_estado.config(text="Transcripción completada.", fg=COLOR_OK)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
            self.label_estado.config(text="Error en la transcripción.", fg=COLOR_ERROR)
        finally:
            self.barra_progreso.stop()
            self.btn_transcribir.config(state=tk.NORMAL)


if __name__ == "__main__":
    ventana = tk.Tk()
    app = TranscriptorApp(ventana)
    ventana.mainloop()