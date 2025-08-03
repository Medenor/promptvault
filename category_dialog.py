from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QInputDialog, QMessageBox, QDialogButtonBox,
                             QListWidget)
from PyQt6.QtCore import Qt

class CategoryDialog(QDialog):
    def __init__(self, parent=None, categories=None):
        super().__init__(parent)
        self.categories = list(categories) if categories else []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Manage Categories')
        layout = QVBoxLayout(self)

        self.categoryList = QListWidget()
        self.categoryList.addItems(self.categories)
        self.categoryList.sortItems(Qt.SortOrder.AscendingOrder)
        layout.addWidget(self.categoryList)

        button_layout = QHBoxLayout()
        self.addButton = QPushButton('Add')
        self.addButton.clicked.connect(self.addCategory)
        button_layout.addWidget(self.addButton)

        self.removeButton = QPushButton('Remove')
        self.removeButton.clicked.connect(self.removeCategory)
        button_layout.addWidget(self.removeButton)

        layout.addLayout(button_layout)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

    def addCategory(self):
        category, ok = QInputDialog.getText(self, 'Add Category', 'Category Name:')
        if ok and category:
            if category == 'No category':
                 QMessageBox.warning(self, "Reserved Name", "'No category' is a reserved name.")
                 return
            if category not in self.categories:
                self.categories.append(category)
                self.categoryList.addItem(category)
                self.categoryList.sortItems(Qt.SortOrder.AscendingOrder)
            else:
                QMessageBox.warning(self, "Category Exists", "This category already exists.")

    def removeCategory(self):
        selected_items = self.categoryList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a category to remove.")
            return

        category_to_remove = selected_items[0].text()

        if category_to_remove == 'No category':
             QMessageBox.warning(self, "Deletion Impossible", "The category 'No category' cannot be deleted.")
             return

        reply = QMessageBox.question(self, 'Confirmation',
                                     f"Delete category '{category_to_remove}'?\nAssociated prompts will be moved to 'No category'.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if category_to_remove in self.categories:
                self.categories.remove(category_to_remove)
                self.categoryList.takeItem(self.categoryList.row(selected_items[0]))
                print(f"Category '{category_to_remove}' marked for deletion (will be effective if you click OK).")

    def getCategories(self):
        return self.categories
