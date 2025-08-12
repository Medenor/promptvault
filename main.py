import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu
from PyQt6.QtGui import QAction
from prompt_manager_widget import PromptManager

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Create the main window
    main_window = QMainWindow()
    main_window.setWindowTitle('Prompt Manager')
    main_window.setGeometry(200, 200, 950, 600)  # Set a default size
    
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
    
    # Show the main window
    main_window.show()
    
    sys.exit(app.exec())
