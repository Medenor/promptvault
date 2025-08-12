import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu
from PyQt6.QtGui import QAction
from prompt_manager_widget import PromptManager
from theme_manager import ThemeManager
import os
from PyQt6.QtCore import QDir

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Register the themes directory as a Qt resource path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    themes_path = os.path.join(current_dir, "themes")
    QDir.addSearchPath("themes", themes_path)
    
    # Create the main window
    main_window = QMainWindow()
    main_window.setWindowTitle('Prompt Manager')
    main_window.setGeometry(200, 200, 950, 600)  # Set a default size
    
    # Initialize ThemeManager
    theme_manager = ThemeManager(app, themes_path)
    theme_manager.load_theme("light") # Set initial theme
    
    # Create the PromptManager widget
    prompt_manager = PromptManager()
    
    # Set the PromptManager widget as the central widget
    main_window.setCentralWidget(prompt_manager)
    
    # Create the menu bar
    menubar = main_window.menuBar()
    
    # Create the File menu
    file_menu = menubar.addMenu('File')
    
    # Create Import action
    import_action = QAction('Import', main_window)
    import_action.triggered.connect(prompt_manager.import_prompts)
    file_menu.addAction(import_action)
    
    # Create Export action
    export_action = QAction('Export', main_window)
    export_action.triggered.connect(prompt_manager.export_prompts)
    file_menu.addAction(export_action)

    # Create the View menu for themes
    view_menu = menubar.addMenu('View')

    # Create Light Theme action
    light_theme_action = QAction('Light Theme', main_window)
    light_theme_action.triggered.connect(theme_manager.set_light_theme)
    view_menu.addAction(light_theme_action)

    # Create Dark Theme action
    dark_theme_action = QAction('Dark Theme', main_window)
    dark_theme_action.triggered.connect(theme_manager.set_dark_theme)
    view_menu.addAction(dark_theme_action)

    # Add separator
    view_menu.addSeparator()

    # Create Toggle Fullscreen action
    fullscreen_action = QAction('Toggle Fullscreen', main_window)
    fullscreen_action.setCheckable(True)
    fullscreen_action.triggered.connect(lambda: toggle_fullscreen(main_window, fullscreen_action))
    view_menu.addAction(fullscreen_action)
    
    # Show the main window
    main_window.show()
    
    sys.exit(app.exec())

def toggle_fullscreen(window, action):
    if window.isFullScreen():
        window.showNormal()
        action.setChecked(False)
    else:
        window.showFullScreen()
        action.setChecked(True)
