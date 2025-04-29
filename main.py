#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AnimeFileSorter main application entry point.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Add the project root to sys.path for easier imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.views.main_window import MainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("AnimeFileSorter")
    
    # Set style sheet (can be moved to a dedicated theme manager later)
    # with open(str(Path(__file__).parent / "views" / "resources" / "style.qss"), "r") as f:
    #     app.setStyleSheet(f.read())
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 