from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QMessageBox, QDialogButtonBox, QLabel,
                             QTextEdit, QComboBox, QToolTip, QCheckBox)
from PyQt6.QtCore import Qt

class PromptDialog(QDialog):
    def __init__(self, parent=None, data=None, history=None, categories=None):
        super().__init__(parent)
        self.history_data = history if history else []
        self.current_data = data
        self.history_purged = False
        self.categories = categories if categories else []
        self.initUI(data)

    def initUI(self, data=None):
        self.setWindowTitle('Add/Edit Prompt')
        layout = QVBoxLayout(self)

        if self.history_data and len(self.history_data) > 1:
            history_layout = QHBoxLayout()
            self.historyCombo = QComboBox()
            for i, version_data in enumerate(reversed(self.history_data)):
                version_label = f"Version {len(self.history_data) - i}"
                if i == 0:
                    version_label += " (Current)"
                self.historyCombo.addItem(version_label, i)
            self.historyCombo.currentIndexChanged.connect(self.display_history_version)
            self.historyCombo.setCurrentIndex(0)
            history_layout.addWidget(QLabel("History:"), 0)
            history_layout.addWidget(self.historyCombo, 1)

            self.purgeHistoryButton = QPushButton("Purge")
            self.purgeHistoryButton.setToolTip("Delete all history except the current version")
            self.purgeHistoryButton.clicked.connect(self.purge_history)
            history_layout.addWidget(self.purgeHistoryButton, 0)

            layout.addLayout(history_layout)

        layout.addWidget(QLabel('Prompt Title:'))
        self.titleEdit = QLineEdit()
        self.titleEdit.setPlaceholderText("Add prompt title here")
        if data:
            self.titleEdit.setText(data.get('title', ''))
        layout.addWidget(self.titleEdit)

        self.favoriteCheckbox = QCheckBox("Mark as favorite")
        if data:
            self.favoriteCheckbox.setChecked(data.get('favorite', False))
        layout.addWidget(self.favoriteCheckbox)

        layout.addWidget(QLabel('Category:'))
        self.categoryCombo = QComboBox()
        display_categories = list(self.categories)
        if 'No category' not in display_categories:
             display_categories.insert(0, 'No category')
        display_categories.sort()

        self.categoryCombo.addItems(display_categories)
        default_category = 'No category'
        if data:
            default_category = data.get('category', 'No category')
        self.categoryCombo.setCurrentText(default_category)
        layout.addWidget(self.categoryCombo)


        layout.addWidget(QLabel('Tags (comma separated):'))
        self.tagsEdit = QLineEdit()
        if data:
            self.tagsEdit.setText(", ".join(data.get('tags', [])))
        layout.addWidget(self.tagsEdit)

        layout.addWidget(QLabel('Prompt:'))
        self.promptEdit = QTextEdit()
        self.promptEdit.setPlaceholderText("Add prompt here")
        if data:
            self.promptEdit.setPlainText(data.get('prompt', ''))
        layout.addWidget(self.promptEdit)

        layout.addWidget(QLabel('Note:'))
        self.noteEdit = QTextEdit()
        self.noteEdit.setPlaceholderText("Add additional notes or information here...")
        if data:
            self.noteEdit.setPlainText(data.get('note', ''))
        layout.addWidget(self.noteEdit)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

    def display_history_version(self, index):
        if not self.history_data or index < 0:
            return

        original_history_index = len(self.history_data) - 1 - index
        if 0 <= original_history_index < len(self.history_data):
            version_data = self.history_data[original_history_index]
            self.titleEdit.setText(version_data.get('title', ''))
            self.favoriteCheckbox.setChecked(version_data.get('favorite', False))
            self.categoryCombo.setCurrentText(version_data.get('category', 'No category'))
            self.tagsEdit.setText(", ".join(version_data.get('tags', [])))
            self.promptEdit.setPlainText(version_data.get('prompt', ''))
            self.noteEdit.setPlainText(version_data.get('note', ''))
            print(f"Displaying history version index {original_history_index}")

    def purge_history(self):
        if not self.history_data or len(self.history_data) <= 1:
            QMessageBox.information(self, "No History", "There is no history to purge.")
            return

        message = "Are you sure you want to delete all history for this prompt?\n\nOnly the version displayed as '(Current)' will be kept after clicking OK."
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("History Purge Confirmation")
        msgBox.setText(message)
        msgBox.setIcon(QMessageBox.Icon.Warning)
        yesButton = msgBox.addButton("Yes, purge", QMessageBox.ButtonRole.YesRole)
        noButton = msgBox.addButton("No, cancel", QMessageBox.ButtonRole.NoRole)
        msgBox.setDefaultButton(noButton)

        reply = msgBox.exec()

        if msgBox.clickedButton() == yesButton:
            self.history_purged = True
            self.purgeHistoryButton.setEnabled(False)
            self.historyCombo.setEnabled(False)
            self.purgeHistoryButton.setText("Purged (on OK)")
            QToolTip.showText(self.purgeHistoryButton.mapToGlobal(self.purgeHistoryButton.rect().bottomLeft()),
                              "History will be purged when you click OK.", msecShowTime=3000)
            print("Marked for purge.")

    def accept(self):
        title = self.titleEdit.text().strip()
        prompt_text = self.promptEdit.toPlainText().strip()

        if not title:
            QMessageBox.warning(self, "Missing Required Field", "The 'Prompt Title' field cannot be empty.")
            self.titleEdit.setFocus()
            return

        if not prompt_text:
            QMessageBox.warning(self, "Missing Required Field", "The 'Prompt' field cannot be empty.")
            self.promptEdit.setFocus()
            return

        super().accept()

    def getPromptData(self):
        tags_text = self.tagsEdit.text()
        tags = [tag_text.strip() for tag_text in tags_text.split(',') if tag_text.strip()]
        return {
            'title': self.titleEdit.text(),
            'favorite': self.favoriteCheckbox.isChecked(),
            'category': self.categoryCombo.currentText(),
            'tags': tags,
            'prompt': self.promptEdit.toPlainText(),
            'note': self.noteEdit.toPlainText()
        }
