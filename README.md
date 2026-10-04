# Transcriptor

Recursos utilizados:

- tkinter (y sus submódulos filedialog, messagebox, ttk): Para construir toda la interfaz gráfica de usuario, incluyendo botones, cuadros de texto, la ventana de selección de archivos y las alertas de error.

- whisper: Para cargar el modelo de inteligencia artificial y procesar el archivo de audio para convertirlo en texto.

- threading: Para ejecutar tareas pesadas (la carga del modelo y el proceso de transcripción) en hilos secundarios, lo que evita que la interfaz del programa se congele mientras trabaja.

- Las transcripciones al finalizar se guardan en una carpeta por separado llamada transcripciones y los archivos son en formato TXT con el nombre del archivo de audio.

Archivos Opcionales:

- ffmpeg-9.0.2-essentials_build es el modelo que se necesita descargar y descomprimir para después ponerlo en el disco local C (C:\).
- Es necesario modificar las variables de entorno del sistema en el apartado PATH (C:\ffmpeg\bin) para que el modelo cargue desde el inicio y de manera fluida.
- También ponerlo en el apartado PATH Variables de Python para que funcione de manera correcta.

# Nota Importante

- Se uso PyCharm como entorno de desarrollo.
