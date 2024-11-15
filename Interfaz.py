from tkinter import *
from tkinter import filedialog, messagebox
import os
import pygame
from mutagen.mp3 import MP3
import threading
import time

class Interfaz:
    def __init__(self):
        pygame.init()
        self.ventana = Tk()
        self.ventana.geometry("800x600")
        self.ventana.title("Reproductor de Música")
        self.ventana.config(bg="#1E1E1E")

        self.cancion_actual = None
        self.carpeta = None
        self.canciones = []
        self.tocando = False
        self.duracion = 0
        self.paused = False
        self.posicion_actual = 0  # Posición de la canción actual

        self.crear_interfaz()
        self.ventana.protocol("WM_DELETE_WINDOW", self.salir)
        self.ventana.mainloop()

    def crear_interfaz(self):
        # Lista de canciones
        self.lista_canciones = Listbox(self.ventana, bg="#333333", fg="white", selectbackground="#003161", font=("Fira Code", 12), selectmode=SINGLE)
        self.lista_canciones.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.lista_canciones.bind("<<ListboxSelect>>", self.mostrar_info)

        # Botones de control
        self.controles_frame = Frame(self.ventana, bg="#1E1E1E")
        self.controles_frame.pack(fill=X)

        self.btn_cargar = Button(self.controles_frame, text="📂 Cargar Canciones", bg="#003161", fg="white", font=("Fira Code", 12), command=self.cargar_canciones)
        self.btn_cargar.grid(row=0, column=0, padx=5, pady=5)

        self.btn_play = Button(self.controles_frame, text="⏯ Play/Pause", bg="#333333", fg="white", font=("Fira Code", 12), command=self.reproducir_pausar)
        self.btn_play.grid(row=0, column=1, padx=5, pady=5)

        self.btn_stop = Button(self.controles_frame, text="⏹ Stop", bg="#333333", fg="white", font=("Fira Code", 12), command=self.detener)
        self.btn_stop.grid(row=0, column=2, padx=5, pady=5)

        self.btn_adelantar = Button(self.controles_frame, text="⏩ Adelantar", bg="#333333", fg="white", font=("Fira Code", 12), command=self.adelantar)
        self.btn_adelantar.grid(row=0, column=3, padx=5, pady=5)

        self.btn_retroceder = Button(self.controles_frame, text="⏪ Retroceder", bg="#333333", fg="white", font=("Fira Code", 12), command=self.retroceder)
        self.btn_retroceder.grid(row=0, column=4, padx=5, pady=5)

        self.btn_avanzar = Button(self.controles_frame, text="⏩ 10s Avanzar", bg="#333333", fg="white", font=("Fira Code", 12), command=self.avanzar_10s)
        self.btn_avanzar.grid(row=1, column=0, padx=5, pady=5)

        self.btn_devolver = Button(self.controles_frame, text="⏪ 10s Devolver", bg="#333333", fg="white", font=("Fira Code", 12), command=self.devolver_10s)
        self.btn_devolver.grid(row=1, column=1, padx=5, pady=5)

        self.lbltiempo = Label(self.controles_frame, text="00:00 / 00:00", bg="#1E1E1E", fg="white", font=("Fira Code", 12))
        self.lbltiempo.grid(row=1, column=2, padx=5, pady=5)

        # Barra de progreso
        self.bar_progreso = Scale(self.controles_frame, from_=0, to=100, orient=HORIZONTAL, bg="#003161", fg="white", font=("Fira Code", 12), command=self.cambiar_posicion)
        self.bar_progreso.set(0)
        self.bar_progreso.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky="ew")

        # Control de volumen
        self.btn_volumen = Scale(self.controles_frame, from_=0, to=100, orient=HORIZONTAL, bg="#003161", fg="white", font=("Fira Code", 12), label="Volumen", command=self.cambiar_volumen)
        self.btn_volumen.set(100)
        self.btn_volumen.grid(row=3, column=0, columnspan=5, padx=5, pady=5, sticky="ew")

    def cargar_canciones(self):
        self.carpeta = filedialog.askdirectory(title="Seleccionar carpeta de canciones")
        if self.carpeta:
            self.canciones = [f for f in os.listdir(self.carpeta) if f.endswith('.mp3')]
            if self.canciones:
                self.lista_canciones.delete(0, END)
                for cancion in self.canciones:
                    self.lista_canciones.insert(END, cancion)
            else:
                messagebox.showinfo("Información", "No se encontraron canciones en la carpeta seleccionada.")

    def mostrar_info(self, event):
        seleccion = self.lista_canciones.curselection()
        if seleccion:
            index = seleccion[0]
            ruta_cancion = os.path.join(self.carpeta, self.canciones[index])
            if os.path.exists(ruta_cancion):
                try:
                    audio = MP3(ruta_cancion)
                    self.duracion = audio.info.length
                    minutos, segundos = divmod(int(self.duracion), 60)
                    self.lbltiempo.config(text=f"00:00 / {minutos:02d}:{segundos:02d}")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo leer la información de la canción.\n{e}")
            else:
                messagebox.showerror("Error", f"El archivo '{ruta_cancion}' no existe.")
                self.lista_canciones.delete(index)

    def reproducir_pausar(self):
        seleccion = self.lista_canciones.curselection()
        if seleccion:
            index = seleccion[0]
            ruta_cancion = os.path.join(self.carpeta, self.canciones[index])
            if os.path.exists(ruta_cancion):
                if not self.tocando:
                    pygame.mixer.music.load(ruta_cancion)
                    pygame.mixer.music.play(loops=0, start=self.posicion_actual)
                    self.tocando = True
                    self.paused = False
                    self.iniciar_actualizacion_tiempo()
                elif self.paused:
                    pygame.mixer.music.unpause()
                    self.paused = False
                else:
                    pygame.mixer.music.pause()
                    self.paused = True
            else:
                messagebox.showerror("Error", "No se encontró la canción seleccionada.")

    def detener(self):
        pygame.mixer.music.stop()
        self.tocando = False
        self.paused = False
        self.posicion_actual = 0
        self.lbltiempo.config(text="00:00 / 00:00")
        self.bar_progreso.set(0)

    def cambiar_volumen(self, val):
        volumen = int(val) / 100
        pygame.mixer.music.set_volume(volumen)

    def cambiar_posicion(self, val):
        if self.tocando:
            pygame.mixer.music.set_pos(int(val))

    def iniciar_actualizacion_tiempo(self):
        def actualizar_tiempo():
            while self.tocando:
                if not self.paused:
                    tiempo_actual = pygame.mixer.music.get_pos() // 1000
                    minutos, segundos = divmod(tiempo_actual, 60)
                    minutos_total, segundos_total = divmod(int(self.duracion), 60)
                    self.lbltiempo.config(text=f"{minutos:02d}:{segundos:02d} / {minutos_total:02d}:{segundos_total:02d}")
                    # Actualizar la barra de progreso
                    progreso = (tiempo_actual / self.duracion) * 100
                    self.bar_progreso.set(progreso)
                time.sleep(0.1)  # Intervalo de actualización de la barra y el tiempo

        hilo = threading.Thread(target=actualizar_tiempo, daemon=True)
        hilo.start()

    def adelantar(self):
        if self.tocando:
            seleccion = self.lista_canciones.curselection()
            if seleccion:
                index = (seleccion[0] + 1) % len(self.canciones)
                self.lista_canciones.selection_clear(0, END)
                self.lista_canciones.select_set(index)
                self.mostrar_info(None)
                self.reproducir_pausar()

    def retroceder(self):
        if self.tocando:
            seleccion = self.lista_canciones.curselection()
            if seleccion:
                index = (seleccion[0] - 1) % len(self.canciones)
                self.lista_canciones.selection_clear(0, END)
                self.lista_canciones.select_set(index)
                self.mostrar_info(None)
                self.reproducir_pausar()

    def avanzar_10s(self):
        if self.tocando:
            tiempo_actual = pygame.mixer.music.get_pos() // 1000
            nueva_posicion = tiempo_actual + 10
            if nueva_posicion < self.duracion:
                self.posicion_actual = nueva_posicion
                pygame.mixer.music.set_pos(self.posicion_actual)

    def devolver_10s(self):
        if self.tocando:
            tiempo_actual = pygame.mixer.music.get_pos() // 1000
            nueva_posicion = tiempo_actual - 10
            if nueva_posicion > 0:
                self.posicion_actual = nueva_posicion
                pygame.mixer.music.set_pos(self.posicion_actual)

    def salir(self):
        pygame.mixer.quit()
        self.ventana.destroy()
