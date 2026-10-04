# Transcriptor

Recursos utilizados:

- tkinter (y sus submódulos filedialog, messagebox, ttk): Para construir toda la interfaz gráfica de usuario, incluyendo botones, cuadros de texto, la ventana de selección de archivos y las alertas de error.

- whisper: Para cargar el modelo de inteligencia artificial y procesar el archivo de audio para convertirlo en texto.

- threading: Para ejecutar tareas pesadas (la carga del modelo y el proceso de transcripción) en hilos secundarios, lo que evita que la interfaz del programa se congele mientras trabaja.
