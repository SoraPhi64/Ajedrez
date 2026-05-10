import sys, os, subprocess
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QPixmap, QColor, QBrush
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QToolBar, QStatusBar, QPushButton, QDialog, 
    QDialogButtonBox, QVBoxLayout, QMessageBox, QGroupBox, QCheckBox, QComboBox, QStackedLayout, QWidget,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem
    )
import chess, chess.engine

# Obtiene la ruta relativa de los archivos. Útil para convertirlo a exe
def ruta(relativa):
    # MEIPASS es una variable temporal que forma pyinstaller al convertir a exe. Con esto comprueba si está en pyinstaller
    if hasattr(sys, '_MEIPASS'): 
        return os.path.join(sys._MEIPASS, relativa) # Obtiene la ruta absoluta con MEIPASS
    return os.path.join(os.path.abspath("."), relativa) # Si no está en Pyinstaller, obtiene la ruta absoluta de dónde quiera que esté la carpeta

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() # Inicializo QMainWindow, la clase padre
        self.setWindowTitle("Ajedrez")
        self.config = {"dificultad": "Normal", "blancas": True} # Configuración por defecto
        self.tool() # Toolbar
        self.titulo() # Pantalla de Inicio

    def tool(self):
        toolbar = QToolBar("Main Toolbar") # Creo el objeto
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar) # Añado la toolbar a QMainWindow

        self.setStatusBar(QStatusBar(self)) # Barra de estado para mostrar los tips

        button_action1 = QAction(QIcon(ruta("Iconos/plus.svg")), "Nuevo Juego", self)
        button_action1.setStatusTip("Nuevo Juego")
        button_action1.triggered.connect(self.nuevo_juego) # Triggered detecta cuando se activa el botón y connect lo conecta con la función
        toolbar.addAction(button_action1)

        toolbar.addSeparator()
        button_action2 = QAction(QIcon(ruta("Iconos/settings.svg")), "Configuración", self)
        button_action2.setStatusTip("Ajustes")
        button_action2.triggered.connect(self.configuracion)
        toolbar.addAction(button_action2)
        
        toolbar.addSeparator()
        button_action3 = QAction(QIcon(ruta("Iconos/alert.svg")), "Ayuda", self)
        button_action3.setStatusTip("Ayuda")
        button_action3.triggered.connect(self.ayuda)
        toolbar.addAction(button_action3)

    def titulo(self):
        imagen = QLabel()
        imagen.setPixmap(QPixmap(ruta("titulo.jpg"))) # Obtiene la imagen y la añade al QLabel      
        title = QLabel("Ajedrez")
        title.setAlignment(Qt.AlignCenter) # Centra el texto
        title.setStyleSheet("""font-size: 82px; font-weight: bold; font-family: "Times New Roman";""")
        
        nuevo_juego = QPushButton("Nuevo Juego")
        nuevo_juego.setStatusTip("Inicia una nueva partida")
        nuevo_juego.clicked.connect(self.nuevo_juego)

        continuar = QPushButton("Continuar")
        continuar.setStatusTip("Continua la partida")

        configuracion = QPushButton("Configuración")
        configuracion.setStatusTip("Abre la configuración")
        configuracion.clicked.connect(self.configuracion)

        ayuda = QPushButton("Ayuda")
        ayuda.setStatusTip("Información del programa")
        ayuda.clicked.connect(self.ayuda)

        variables = [nuevo_juego, continuar, configuracion, ayuda]

        # Diseño visual de los botones
        for boton in variables:
            boton.setFixedSize(200, 50) # Tamaño
            boton.setStyleSheet(""" background-color: rgba(0,0,0,120) """) # Color/Opacidad
            boton.setCheckable(True) # Tipo interruptor (puede estar pulsado o no)

        title_layout = QVBoxLayout() # Crea un layout vertical
        title_layout.setAlignment(Qt.AlignHCenter) # Lo centra horizontalmente
        title_layout.addSpacing(50) # Le mete un spacing de 50 de arriba hacia abajo
        title_layout.addWidget(title)
        title_layout.addSpacing(20)
        title_layout.addWidget(nuevo_juego)
        title_layout.addSpacing(20)
        title_layout.addWidget(continuar)
        title_layout.addSpacing(20)
        title_layout.addWidget(configuracion)
        title_layout.addSpacing(20)
        title_layout.addWidget(ayuda)
        title_layout.addStretch() # Añade un espacio final para que quede todo más compacto

        title_contenedor = QWidget()
        title_contenedor.setLayout(title_layout) # Añade el layout al Widget

        layout = QStackedLayout()
        layout.setStackingMode(QStackedLayout.StackAll) # Le indica que muestre todo, una cosa encima de la otra
        layout.addWidget(imagen)
        layout.addWidget(title_contenedor)

        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)
        # Todo esto está dividido por capas para que sea más modular y fácil de mantener/reparar

    DIFICULTAD = {"Fácil": 0.05, "Normal": 0.5, "Difícil": 2.0} # Diccionario con los segundos que tiene la IA para pensar (y por tanto la dificultad de la partida)
    def nuevo_juego(self):
        tiempo = self.DIFICULTAD[self.config["dificultad"]] # self.config tiene la dificultad en string. self.DIFICULTAD tiene el valor del tiempo
        tablero = Tablero(tiempo_ia=tiempo)
        self.setCentralWidget(tablero) # Cambio la pantalla de título por el tablero

        if not self.config["blancas"]:
            tablero.turno_ia()
        
    def configuracion(self):
        configuracion = Settings()
        configuracion.dificultad.setCurrentText(self.config["dificultad"]) # Obtiene la dificultad elegida actualmente
        configuracion.iniciar_blancas.setChecked(self.config["blancas"])
        if configuracion.exec() == QDialog.Accepted: # Si el usuario le pulsa al OK, cambia las opciones a las que haya seleccionadas
            self.config["dificultad"] = configuracion.dificultad.currentText()
            self.config["blancas"] = configuracion.iniciar_blancas.isChecked()

    def ayuda(self):
        QMessageBox(self).about(self, "Ayuda", "Creador: Sora Phi Rodríguez.\nTrabajo de Fin de Grado.\n2025-2026")

    # Función para asegurarnos de cerrar stockfish
    def closeEvent(self, event):
        widget = self.centralWidget() # Obtiene la pantalla actual
        if isinstance(widget, Tablero) and hasattr(widget, 'engine'): # Si es el tablero y stockfish está encendido
            widget.engine.quit() # Lo apaga
        event.accept() # Se le indica a la pantalla que ahora sí se puede cerrar

class Settings(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración")
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel # Defino qué botones habrá. Todavía no los creo

        group_box = QGroupBox("Ajustes de partida") # Contenedor. Agrupa los widgets
        self.iniciar_blancas = QCheckBox("Jugar con blancas") # Uso self para poder verificar luego su estado
        dificultad_label = QLabel("Dificultad")
        self.dificultad = QComboBox() # Desplegable
        self.dificultad.addItems(["Fácil", "Normal", "Difícil"])
        self.dificultad.setCurrentText("Normal") # Normal por defecto

        partida_layout = QVBoxLayout() # Layout vertical
        partida_layout.addWidget(self.iniciar_blancas)
        partida_layout.addWidget(dificultad_label) # La palabra "dificultad"
        partida_layout.addWidget(self.dificultad) # El seleccionable de dificultad

        group_box.setLayout(partida_layout)

        buttonBox = QDialogButtonBox(QBtn) # Creo los botones
        buttonBox.accepted.connect(self.accept) # Devuelve Accepted para la función de configuración y así entre en el if
        buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(group_box)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

class Tablero(QGraphicsView):
    TAMAÑO_CASILLA = 80
    def __init__(self, tiempo_ia=0.5):
        super().__init__()
        # Elimina barras de scroll por motivos de cálculo de clicks
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.tiempo_ia = tiempo_ia
        self.board = chess.Board() # No es el tablero visual, sino el tablero lógico que usa la librería chess
        self.scene = QGraphicsScene() # El tablero visual
        self.scene.setSceneRect(0, 0, 8 * self.TAMAÑO_CASILLA, 8 * self.TAMAÑO_CASILLA)  # Establezco dónde empieza el tablero y qué tamaño tiene (8 casillas de alto y de ancho por 80 de tamaño de casilla)
        self.setScene(self.scene) # Le indico a la clase que muestre esta escena, el tablero
        
        self.piezas = {}
        self.casilla_sel = None
        self.casillas = {}
        self.movimientos_legales = []

        self.dibujar_tablero()

        # Obtengo los iconos de cada pieza usando variables definidas por la librería chess
        self.SIMBOLOS = {
            (chess.KING,   chess.WHITE): ruta("Fichas Blancas/Rey_Blanco.png"),
            (chess.QUEEN,  chess.WHITE): ruta("Fichas Blancas/Reina_Blanca.png"),
            (chess.ROOK,   chess.WHITE): ruta("Fichas Blancas/Torre_Blanca.png"),
            (chess.BISHOP, chess.WHITE): ruta("Fichas Blancas/Alfil_Blanco.png"),
            (chess.KNIGHT, chess.WHITE): ruta("Fichas Blancas/Caballo_Blanco.png"),
            (chess.PAWN,   chess.WHITE): ruta("Fichas Blancas/Peon_Blanco.png"),
            (chess.KING,   chess.BLACK): ruta("Fichas Negras/Rey_Negro.png"),
            (chess.QUEEN,  chess.BLACK): ruta("Fichas Negras/Reina_Negra.png"),
            (chess.ROOK,   chess.BLACK): ruta("Fichas Negras/Torre_Negra.png"),
            (chess.BISHOP, chess.BLACK): ruta("Fichas Negras/Alfil_Negro.png"),
            (chess.KNIGHT, chess.BLACK): ruta("Fichas Negras/Caballo_Negro.png"),
            (chess.PAWN,   chess.BLACK): ruta("Fichas Negras/Peon_Negro.png"),
        }
        # Busco stockfish.exe y creo el motor de IA, pasándole una flag para que no muestre ventanas
        self.engine = chess.engine.SimpleEngine.popen_uci(ruta("stockfish.exe"), creationflags=subprocess.CREATE_NO_WINDOW) 
        
        self.colocar_piezas()
        
    def dibujar_tablero(self):
        # Limpieza de tablero
        for casilla in self.casillas.values():
            self.scene.removeItem(casilla)
        self.casillas = {}

        colores = [QColor("#F0D9B5"), QColor("#B58863")]

        for fila in range(8):
            for columna in range(8):
                color = colores[(fila + columna) % 2] # Si la casilla es par, claro, si es impar, oscuro
                # Creamos las casillas. Usamos el valor de la columna y de la fila para saber el valor por el que se empieza (coordenada 1,0 por ejemplo) y se le aplica el alto y ancho del tamaño de la casilla (80)
                casilla = QGraphicsRectItem(columna * self.TAMAÑO_CASILLA, fila * self.TAMAÑO_CASILLA, self.TAMAÑO_CASILLA, self.TAMAÑO_CASILLA)
                casilla.setBrush(QBrush(color)) # Define el relleno
                casilla.setPen(Qt.NoPen) # Hace que no haya bordes visibles alrededor del rectángulo

                self.scene.addItem(casilla) # Lo añade a la escena para que se dibuje en la pantalla
                self.casillas[(columna, fila)] = casilla # Guardo la referencia de dicha casilla para poder usarla luego

    def colocar_piezas(self):
        # Limpia el tablero cada vez que se mueva una pieza
        for item in self.piezas.values():
            self.scene.removeItem(item)
        self.piezas = {}

        # Comprueba si en X casilla hay una pieza o no
        for square in chess.SQUARES: # chess.SQUARES es un iterable con las casillas de la librería chess
            pieza = self.board.piece_at(square) # Si hay una pieza, devuelve el objeto, sino, devuelve None
            if pieza is None:
                continue

            # Obtiene la imagen de la pieza
            imagen_ruta = self.SIMBOLOS.get((pieza.piece_type, pieza.color))
            if not imagen_ruta: # Si no encuentra la pieza/color, continúa
                continue

            # Obtiene las coordenadas del tablero lógico. Importante invertirlo en la fila, ya que para chess, la Y empieza por abajo, pero para Qt, empieza por arriba
            # Cabe mencionar que al ser un índice con 0 - 7, no puede irse al negativo. Saca 7 - 0 = 7 (abajo para Qt) o 7 - 7 = 0 (arriba para Qt)
            col, fila = chess.square_file(square), 7 - chess.square_rank(square)

            # Carga la imagen, escalada a la casilla
            pixmap = QPixmap(imagen_ruta).scaled(self.TAMAÑO_CASILLA, self.TAMAÑO_CASILLA, Qt.KeepAspectRatio)
            
            item = self.scene.addPixmap(pixmap) # Añade la pieza a la escena
            item.setAcceptedMouseButtons(Qt.NoButton) # Hace que la pieza no pueda recibir clicks, ya que quiero tratarlos por separado
            item.setPos(col * self.TAMAÑO_CASILLA, fila * self.TAMAÑO_CASILLA) # La pone en su casilla
            
            # Se guarda la pieza con su casilla
            self.piezas[square] = item

    def mousePressEvent(self, event):
        pos = self.mapToScene(event.pos()) # Obtengo la posición del ratón (en píxeles)
        # Transformo las coordenadas en píxeles, en coordenadas en Qt (ej. x = 150 y = 330 == 1,4)
        col = int(pos.x() // self.TAMAÑO_CASILLA)
        fila = int(pos.y() // self.TAMAÑO_CASILLA)

        if not (0 <= col <= 7 and 0 <= fila <= 7): # Si la coordenada cae fuera del tablero, la ignora
            return
        square = chess.square(col, 7 - fila) # Transforma la coordenada de Qt a coordenada de chess para la lógica

        if self.casilla_sel is None: # Si no hay ninguna casilla seleccionada
            pieza = self.board.piece_at(square) # Compruebo si hay alguna pieza en la casilla que selecciono
            if pieza and pieza.color == self.board.turn: # Si hay una pieza y es mi turno
                self.casilla_sel = square # La nueva casilla seleccionada es la que selecciono
                self.resaltar_casilla(square)
                self.resaltar_movimientos_legales(square)

        else: # Si sí hay una casilla seleccionada
            # Creo un objeto Move de la librería chess con la casilla seleccionada indicando origen y destino. Todavía no lo aplico
            movimiento = chess.Move(self.casilla_sel, square) 
            if movimiento in self.board.legal_moves: # Si el movimiento es legal
                self.board.push(movimiento) # Lo aplico en el tablero lógico
                self.dibujar_tablero() # Y en el visual
                self.colocar_piezas()
                self.comprobar_fin() # Compruebo si se ha terminado la partida
                if not self.board.is_game_over(): # Si no ha terminado
                    self.turno_ia() # Paso al turno de la IA
            else: # Si el movimiento no es legal
                self.restaurar_casilla(self.casilla_sel) # De-selecciono la casilla
            self.limpiar_movimientos_legales()
            self.casilla_sel = None # Reseteo la casilla después de todo esto

    # Cambio los colores de la casilla dependiendo de si está seleccionada o si deja de estarlo
    def resaltar_casilla(self, square):
        col = chess.square_file(square)
        fila = 7 - chess.square_rank(square)
        self.casillas[(col, fila)].setBrush(QBrush(QColor("#F6F669")))

    def restaurar_casilla(self, square):
        col = chess.square_file(square)
        fila = 7 - chess.square_rank(square)
        colores = [QColor("#F0D9B5"), QColor("#B58863")]
        color = colores[(col + fila) % 2]
        self.casillas[(col, fila)].setBrush(QBrush(color))

    def resaltar_movimientos_legales(self, from_square):
        self.movimientos_legales = []
        for movimiento in self.board.legal_moves: # Compruebo todos los movimientos legales
            if movimiento.from_square == from_square: # Filtro sólo los que provienen de la casilla seleccionada
                self.resaltar_casilla_destino(movimiento.to_square)
                self.movimientos_legales.append(movimiento.to_square) # Añado el destino para luego poder restaurarlo

    def resaltar_casilla_destino(self, square):
        col = chess.square_file(square)
        fila = 7 - chess.square_rank(square)
        self.casillas[(col, fila)].setBrush(QBrush(QColor("#A4C2F4")))

    def limpiar_movimientos_legales(self):
        for square in self.movimientos_legales:
            self.restaurar_casilla(square)
        self.movimientos_legales = []

    def comprobar_fin(self):
        if self.board.is_checkmate(): # Si es jaque mate
            ganador = "Blancas" if self.board.turn == chess.BLACK else "Negras" # Ganan las blancas si es el turno de las negras, y lo mismo al revés
            QMessageBox.information(self, "Fin de partida", f"¡Jaque mate! Ganan las {ganador}.")
        elif self.board.is_stalemate():
            QMessageBox.information(self, "Fin de partida", "Tablas por ahogado.")
        elif self.board.is_insufficient_material():
            QMessageBox.information(self, "Fin de partida", "Tablas por material insuficiente.")
        elif self.board.is_fifty_moves():
            QMessageBox.information(self, "Fin de partida", "Tablas por regla de los 50 movimientos.")
        elif self.board.is_repetition():
            QMessageBox.information(self, "Fin de partida", "Tablas por repetición.")

    def turno_ia(self):
        # Le manda el tablero lógico tal cual está y le da el límite de tiempo para que piense. Devuelve el movimiento que haya realizado
        resultado = self.engine.play(self.board, chess.engine.Limit(time=self.tiempo_ia))
        self.board.push(resultado.move) # Aplica el movimiento. Se asume que la IA no puede hacer movimientos ilegales
        self.dibujar_tablero()
        self.colocar_piezas()
        self.comprobar_fin()
        # Se actualiza todo igual que con el jugador