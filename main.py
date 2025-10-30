#!/usr/bin/env python3
"""
Railway Editor and Monitoring Application
Main entry point for the Qt application
"""

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Railway Editor & Monitor")
    app.setOrganizationName("RailwayApp")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

