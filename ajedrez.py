from clases import *

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    app.exec()

if __name__ == '__main__':
    main() 