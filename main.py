import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog, QLabel, QPushButton
from PyQt6.QtGui import QAction, QDesktopServices, QPixmap
from PyQt6.QtCore import QDir, Qt, QUrl, QSize
from prompt_manager_widget import PromptManager
from theme_manager import ThemeManager

# Custom About Dialog for displaying SVG and text
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About PromptVault")
        self.setFixedSize(450, 400) # Fixed size for the dialog

        layout = QVBoxLayout(self)

        # Load and display SVG logo
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "images", "promptvault_logo.svg")
        logo_label = QLabel(self)
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            # Scale pixmap to fit within a reasonable size, e.g., 200x200
            scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            logo_label.setText("Logo not found or could not be loaded.")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # App description
        description_label = QLabel("PromptVault is a desktop application designed to help users manage, organize, and quickly access their AI prompts.", self)
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description_label)

        # Add a spacer to push content up
        layout.addStretch(1)

        # OK button
        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Prompt Manager')
        self.setGeometry(200, 200, 950, 600)  # Set a default size
        self.initUI()

    def initUI(self):
        # Initialize ThemeManager
        current_dir = os.path.dirname(os.path.abspath(__file__))
        themes_path = os.path.join(current_dir, "themes")
        QDir.addSearchPath("themes", themes_path)
        self.theme_manager = ThemeManager(QApplication.instance(), themes_path)
        self.theme_manager.load_theme("light") # Set initial theme
        
        # Create a container widget for the central area
        central_widget_container = QWidget()
        central_layout = QHBoxLayout(central_widget_container)
        central_layout.setContentsMargins(0, 0, 0, 0) # Remove margins

        # Create the PromptManager widget
        self.prompt_manager = PromptManager()
        central_layout.addWidget(self.prompt_manager)

        # Set the central widget container as the central widget
        self.setCentralWidget(central_widget_container)

        # Create the right panel (QDockWidget)
        self.right_dock = QDockWidget("Prompt Editor", self)
        self.right_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.right_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.right_dock.setVisible(False) # Initially hidden
        self.right_dock.setMinimumWidth(800) # Double the minimum width for the dock widget

        # Create a placeholder widget for the dock content
        # This will be replaced by PromptDialog content later
        prompt_editor_panel_content = QWidget()
        prompt_editor_panel_content.setLayout(QVBoxLayout()) # Use a layout for future content
        self.right_dock.setWidget(prompt_editor_panel_content)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_dock)

        # Pass the dock widget and its content widget to PromptManager
        self.prompt_manager.set_editor_panel(self.right_dock, prompt_editor_panel_content)

        # Create the menu bar
        menubar = self.menuBar()
        
        # Create PromptVault menu
        promptvault_menu = menubar.addMenu('PromptVault')

        # About PromptVault action
        about_action = QAction('About PromptVault', self)
        about_action.triggered.connect(self.show_about_dialog)
        about_action.setMenuRole(QAction.MenuRole.NoRole) # Prevent macOS from moving it to the application menu
        promptvault_menu.addAction(about_action)

        # Codeberg repository action
        codeberg_action = QAction('Codeberg repository', self)
        codeberg_action.triggered.connect(self.open_codeberg_repo)
        promptvault_menu.addAction(codeberg_action)

        # Create the File menu
        file_menu = menubar.addMenu('File')
        
        # Create Import action
        import_action = QAction('Import', self)
        import_action.triggered.connect(self.prompt_manager.import_prompts)
        file_menu.addAction(import_action)
        
        # Create Export action
        export_action = QAction('Export', self)
        export_action.triggered.connect(self.prompt_manager.export_prompts)
        file_menu.addAction(export_action)

        # Create the View menu for themes
        view_menu = menubar.addMenu('View')

        # Create Light Theme action
        light_theme_action = QAction('Light Theme', self)
        light_theme_action.triggered.connect(self.theme_manager.set_light_theme)
        view_menu.addAction(light_theme_action)

        # Create Dark Theme action
        dark_theme_action = QAction('Dark Theme', self)
        dark_theme_action.triggered.connect(self.theme_manager.set_dark_theme)
        view_menu.addAction(dark_theme_action)

        # Add separator
        view_menu.addSeparator()

        # Create Toggle Prompt Editor Panel action
        toggle_editor_panel_action = QAction('Toggle Prompt Editor Panel', self)
        toggle_editor_panel_action.setCheckable(True)
        toggle_editor_panel_action.setChecked(self.right_dock.isVisible())
        toggle_editor_panel_action.triggered.connect(self.right_dock.setVisible)
        self.right_dock.visibilityChanged.connect(toggle_editor_panel_action.setChecked) # Keep menu item in sync
        view_menu.addAction(toggle_editor_panel_action)

        # Create Toggle Fullscreen action
        fullscreen_action = QAction('Toggle Fullscreen', self)
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(lambda: self.toggle_fullscreen(fullscreen_action))
        view_menu.addAction(fullscreen_action)
    
    def toggle_fullscreen(self, action):
        if self.isFullScreen():
            self.showNormal()
            action.setChecked(False)
        else:
            self.showFullScreen()
            action.setChecked(True)

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def open_codeberg_repo(self):
        url = QUrl("https://codeberg.org/medenor/promptvault")
        QDesktopServices.openUrl(url)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    # Show the main window maximized
    main_window.showMaximized()
    sys.exit(app.exec())
