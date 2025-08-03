from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QInputDialog, QMessageBox, QDialogButtonBox,
                             QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
import copy

class TagDialog(QDialog):
    def __init__(self, parent=None, tags=None):
        super().__init__(parent)
        self.initial_tags = set(tags) if tags else set()
        self.current_tags = set(tags) if tags else set()

        self.renamed_tags = {}
        self.removed_tags = set()
        self.added_tags = set()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Manage Tags')
        layout = QVBoxLayout(self)

        self.tagListWidget = QListWidget()
        self.populate_list()
        layout.addWidget(self.tagListWidget)

        button_layout = QHBoxLayout()
        self.addButton = QPushButton('Add')
        self.addButton.clicked.connect(self.addTag)
        button_layout.addWidget(self.addButton)

        self.renameButton = QPushButton('Rename')
        self.renameButton.clicked.connect(self.renameTag)
        button_layout.addWidget(self.renameButton)

        self.removeButton = QPushButton('Remove')
        self.removeButton.clicked.connect(self.removeTag)
        button_layout.addWidget(self.removeButton)

        layout.addLayout(button_layout)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

    def populate_list(self):
        self.tagListWidget.clear()
        for tag in sorted(list(self.current_tags)):
            self.tagListWidget.addItem(tag)

    def addTag(self):
        tag, ok = QInputDialog.getText(self, 'Add Tag', 'Tag Name:')
        tag = tag.strip()
        if ok and tag:
            if tag in self.current_tags:
                QMessageBox.warning(self, "Tag Exists", f"The tag '{tag}' already exists.")
                return
            self.current_tags.add(tag)
            self.added_tags.add(tag)
            if tag in self.removed_tags:
                self.removed_tags.remove(tag)
            self.populate_list()
            print(f"Tag '{tag}' added (will be effective if OK).")

    def renameTag(self):
        selected_items = self.tagListWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a tag to rename.")
            return
        if len(selected_items) > 1:
             QMessageBox.warning(self, "Multiple Selection", "Please select only one tag to rename.")
             return

        old_name = selected_items[0].text()

        new_name, ok = QInputDialog.getText(self, 'Rename Tag', f"New name for '{old_name}':", text=old_name)
        new_name = new_name.strip()

        if ok and new_name and new_name != old_name:
            if new_name in self.current_tags:
                QMessageBox.warning(self, "Tag Exists", f"The tag '{new_name}' already exists.")
                return

            self.current_tags.remove(old_name)
            self.current_tags.add(new_name)

            if old_name in self.added_tags:
                self.added_tags.remove(old_name)
                self.added_tags.add(new_name)
            elif old_name in self.initial_tags:
                 original_name_for_old = None
                 for orig, renamed in self.renamed_tags.items():
                     if renamed == old_name:
                         original_name_for_old = orig
                         break

                 if original_name_for_old:
                     self.renamed_tags[original_name_for_old] = new_name
                 else:
                     self.renamed_tags[old_name] = new_name

                 if new_name in self.removed_tags:
                     self.removed_tags.remove(new_name)

            self.populate_list()
            print(f"Tag '{old_name}' renamed to '{new_name}' (will be effective if OK).")


    def removeTag(self):
        selected_items = self.tagListWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select at least one tag to remove.")
            return

        tags_to_remove = {item.text() for item in selected_items}

        reply = QMessageBox.question(self, 'Confirmation',
                                     f"Delete selected tag(s)?\nThey will be removed from all prompts.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            for tag in tags_to_remove:
                if tag in self.current_tags:
                    self.current_tags.remove(tag)

                    if tag in self.added_tags:
                        self.added_tags.remove(tag)
                    elif tag in self.initial_tags:
                        self.removed_tags.add(tag)
                        original_name_to_remove_rename = None
                        for orig, renamed in self.renamed_tags.items():
                            if renamed == tag:
                                original_name_to_remove_rename = orig
                                break
                        if original_name_to_remove_rename:
                             del self.renamed_tags[original_name_to_remove_rename]
                             self.removed_tags.add(original_name_to_remove_rename)


                    print(f"Tag '{tag}' marked for removal (will be effective if OK).")

            self.populate_list()


    def getChanges(self):
        final_renamed = {old: new for old, new in self.renamed_tags.items() if old in self.initial_tags}
        final_removed = {tag for tag in self.removed_tags if tag in self.initial_tags}

        processed_removed = set(final_removed)
        processed_renamed = {}
        for old, new in final_renamed.items():
            if new in self.current_tags:
                 processed_renamed[old] = new
            else:
                 processed_removed.add(old)


        print(f"Changes to apply: Renamed={processed_renamed}, Removed={processed_removed}, Added={self.added_tags}")
        return processed_renamed, processed_removed, self.added_tags
