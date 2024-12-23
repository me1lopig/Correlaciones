import tkinter as tk
from tkinter import ttk
import pandas as pd
import os


# Ruta del archivo Excel
file_path = './Resources/Tablas.xlsx'

# Verificar si el archivo existe
if not os.path.exists(file_path):
    print(f"El archivo {file_path} no se encuentra en el directorio actual.")
else:
    # Cargar el archivo Excel
    df = pd.read_excel(file_path)

    # Extraer los datos de la primera columna
    first_column_data = df.iloc[:, 0].dropna().tolist()

    # Crear la ventana principal
    root = tk.Tk()
    root.title("Tabla de Parámetros del GrundbauTaschenBuch")

    # Ajustar el tamaño de la ventana para que se vea bien el texto del desplegable
    root.geometry("600x200")

    # Crear una etiqueta
    label = ttk.Label(root, text="Seleccionar el tipo de terreno:")
    label.pack(pady=10)

    # Crear un combobox (desplegable) con un ancho adecuado y bloquear la edición del texto
    combobox = ttk.Combobox(root, values=first_column_data, width=60, state="readonly")
    combobox.pack(pady=10)

    # Mostrar automáticamente el primer elemento de la lista en el desplegable
    if first_column_data:
        combobox.set(first_column_data[0])

    # Crear un botón para terminar el programa
    def terminar_programa():
        root.destroy()

    boton_terminar = ttk.Button(root, text="Terminar programa", command=terminar_programa)
    boton_terminar.pack(pady=10)

    # Ejecutar la aplicación
    root.mainloop()