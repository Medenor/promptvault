import json
import os
from collections import defaultdict
import csv
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QMessageBox, QLabel, QListWidget,
                             QListWidgetItem, QApplication, QAbstractItemView,
                             QToolTip, QDialog, QCheckBox, QSizePolicy,
                             QSpacerItem, QFrame, QMenu, QFileDialog)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PyQt6.QtCore import Qt, QSize

from prompt_dialog import PromptDialog
from category_dialog import CategoryDialog
from tag_dialog import TagDialog

class PromptManager(QWidget):
    def __init__(self):
        super().__init__()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(script_dir, "prompts_data.json")

        self.prompts = {}
        self.next_id = 0
        self.categories = []
        self.global_tags = set() # New attribute for globally managed tags
        self.load_prompts()
        self.initUI()
        self.update_category_list()
        self.update_tag_list()
        self.update_prompt_list()


    def initUI(self):
        self.setGeometry(200, 200, 950, 600)
        self.setWindowTitle('Prompt Manager')

        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()

        left_layout.addWidget(QLabel("Categories"))

        self.manageCategoriesButton = QPushButton('Manage Categories')
        self.manageCategoriesButton.setToolTip("Manage prompt categories")
        self.manageCategoriesButton.clicked.connect(self.manageCategories)
        left_layout.addWidget(self.manageCategoriesButton)

        self.categoryList = QListWidget()
        self.categoryList.itemClicked.connect(self.filter_prompts_by_category)
        left_layout.addWidget(self.categoryList)

        left_layout.addWidget(QLabel("Tags"))

        self.manageTagsButton = QPushButton('Manage Tags')
        self.manageTagsButton.setToolTip("Manage tags globally")
        self.manageTagsButton.clicked.connect(self.manageTags)
        left_layout.addWidget(self.manageTagsButton)

        self.tagList = QListWidget()
        self.tagList.itemClicked.connect(self.filter_prompts_by_tag)
        left_layout.addWidget(self.tagList)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        left_layout.addWidget(line)

        left_layout.addWidget(QLabel("Filters"))

        self.showFavoritesButton = QPushButton("⭐ Show Favorites")
        self.showFavoritesButton.setCheckable(True)
        self.showFavoritesButton.setToolTip("Show only prompts marked as favorites")
        self.showFavoritesButton.clicked.connect(self.toggle_favorites_filter)
        left_layout.addWidget(self.showFavoritesButton)

        self.showAllButton = QPushButton("🔄 Show All")
        self.showAllButton.clicked.connect(self.show_all_prompts)
        left_layout.addWidget(self.showAllButton)

        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        main_layout.addLayout(left_layout, 1)

        right_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Search in title, prompt, note...")
        self.searchBar.textChanged.connect(self.filter_prompts_by_search)
        search_layout.addWidget(self.searchBar, 1)

        self.caseSensitiveCheckbox = QCheckBox("Case Sensitive")
        self.caseSensitiveCheckbox.setToolTip("Enable case-sensitive search")
        self.caseSensitiveCheckbox.stateChanged.connect(self.filter_prompts_by_search)
        search_layout.addWidget(self.caseSensitiveCheckbox, 0)

        right_layout.addLayout(search_layout)

        self.promptList = QListWidget()
        self.promptList.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.promptList.itemDoubleClicked.connect(self.editPrompt)
        self.promptList.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.promptList.customContextMenuRequested.connect(self.show_context_menu)
        right_layout.addWidget(self.promptList)


        button_layout = QHBoxLayout()
        self.addButton = QPushButton('Add')
        self.addButton.setToolTip("Add a new prompt")
        self.addButton.clicked.connect(self.addPrompt)
        button_layout.addWidget(self.addButton)

        self.editButton = QPushButton('Edit')
        self.editButton.setToolTip("Edit selected prompt")
        self.editButton.clicked.connect(self.editPrompt)
        button_layout.addWidget(self.editButton)

        self.deleteButton = QPushButton('Delete')
        self.deleteButton.setToolTip("Delete selected prompt(s)")
        self.deleteButton.clicked.connect(self.deleteSelectedPrompts)
        button_layout.addWidget(self.deleteButton)


        right_layout.addLayout(button_layout)

        main_layout.addLayout(right_layout, 3)

    def update_category_list(self):
        self.categoryList.clear()
        categories_in_use = set(p['data'].get('category', 'No category') for p in self.prompts.values())
        all_display_categories = categories_in_use.union(set(self.categories))

        sorted_display_categories = sorted(list(all_display_categories))
        self.categoryList.addItems(sorted_display_categories)


    def update_tag_list(self):
        self.tagList.clear()
        all_tags_from_prompts = set()
        for prompt_info in self.prompts.values():
            all_tags_from_prompts.update(prompt_info['data'].get('tags', []))
        
        # Combine tags from prompts and globally managed tags
        all_display_tags = all_tags_from_prompts.union(self.global_tags)

        for tag in sorted(list(all_display_tags)):
            self.tagList.addItem(tag)

    def update_prompt_list(self, filter_category=None, filter_tag=None, search_term="", filter_favorites=False):
        self.promptList.clear()

        case_sensitive = self.caseSensitiveCheckbox.isChecked()

        processed_search_term = search_term if case_sensitive else search_term.lower()

        filtered_prompts = []

        for prompt_id, prompt_info in self.prompts.items():
            data = prompt_info['data']
            category = data.get('category') if data.get('category') else 'No category'
            tags = data.get('tags', [])
            is_favorite = data.get('favorite', False)

            title_text = data.get('title', '')
            prompt_text = data.get('prompt', '')
            note_text = data.get('note', '')

            processed_title = title_text if case_sensitive else title_text.lower()
            processed_prompt = prompt_text if case_sensitive else prompt_text.lower()
            processed_note = note_text if case_sensitive else note_text.lower()

            category_match = filter_category is None or category == filter_category
            tag_match = filter_tag is None or filter_tag in tags
            search_match = (
                processed_search_term == "" or
                processed_search_term in processed_title or
                processed_search_term in processed_prompt or
                processed_search_term in processed_note
            )
            favorite_match = (not filter_favorites) or is_favorite
            if category_match and tag_match and search_match and favorite_match:
                filtered_prompts.append({'id': prompt_id, **data})

        sorted_prompts = sorted(filtered_prompts, key=lambda p: p.get('title', ''))

        for prompt_data in sorted_prompts:
            prompt_id = prompt_data['id']
            title = prompt_data.get('title', 'Untitled')
            is_favorite = prompt_data.get('favorite', False)

            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(2, 5, 2, 5)
            item_layout.setSpacing(5)

            if is_favorite:
                fav_label = QLabel("⭐")
                item_layout.addWidget(fav_label, 0)

            title_label = QLabel(title)
            item_layout.addWidget(title_label, 1)

            copy_button = QPushButton()
            copy_button.setObjectName("copyPromptButton") # Add objectName for QSS targeting
            copy_button.setFixedSize(QSize(24, 24))
            copy_button.setToolTip(f"Copy prompt '{title}'")
            copy_button.setStyleSheet("""
                QPushButton { border: none; background-color: transparent; padding: 0px; }
                QPushButton:hover { background-color: rgba(128, 128, 128, 50); }
                QPushButton:pressed { background-color: rgba(128, 128, 128, 100); }
            """)
            copy_button.setProperty("prompt_id", prompt_id)
            copy_button.clicked.connect(self.copy_prompt_text_from_button)
            copy_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            item_layout.addWidget(copy_button, 0)

            item_widget.setLayout(item_layout)

            list_item = QListWidgetItem(self.promptList)
            list_item.setSizeHint(item_widget.sizeHint())
            list_item.setData(Qt.ItemDataRole.UserRole, prompt_id)

            self.promptList.addItem(list_item)
            self.promptList.setItemWidget(list_item, item_widget)

    def copy_prompt_text_from_button(self):
        sender_button = self.sender()
        if sender_button:
            prompt_id = sender_button.property("prompt_id")
            if prompt_id is not None and prompt_id in self.prompts:
                prompt_text = self.prompts[prompt_id]['data'].get('prompt', '')
                clipboard = QApplication.clipboard()
                clipboard.setText(prompt_text)
                QToolTip.showText(sender_button.mapToGlobal(sender_button.rect().bottomLeft()),
                                  "Prompt copied!", widget=sender_button, msecShowTime=1500)
                print(f"Prompt ID {prompt_id} copied via integrated button.")
            else:
                print(f"Error: Could not find prompt ID {prompt_id} from button.")

    def get_selected_prompt_id(self):
        selected_items = self.promptList.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.ItemDataRole.UserRole)
        return None

    def get_selected_prompt_ids(self):
        selected_ids = []
        selected_items = self.promptList.selectedItems()
        for item in selected_items:
            prompt_id = item.data(Qt.ItemDataRole.UserRole)
            if prompt_id is not None:
                selected_ids.append(prompt_id)
        return selected_ids

    def filter_prompts_by_category(self, item):
        category = item.text()
        current_tag = self.current_filter_tag()
        current_search = self.searchBar.text()
        favorites_only = self.is_favorites_filter_active()
        print(f"Filtering by Category: {category}, Tag: {current_tag}, Search: {current_search}, Favorites: {favorites_only}")
        self.update_prompt_list(filter_category=category, filter_tag=current_tag, search_term=current_search, filter_favorites=favorites_only)

    def filter_prompts_by_tag(self, item):
        tag = item.text()
        current_category = self.current_filter_category()
        current_search = self.searchBar.text()
        favorites_only = self.is_favorites_filter_active()
        print(f"Filtering by Tag: {tag}, Category: {current_category}, Search: {current_search}, Favorites: {favorites_only}")
        self.update_prompt_list(filter_category=current_category, filter_tag=tag, search_term=current_search, filter_favorites=favorites_only)

    def filter_prompts_by_search(self, text=None):
        search_term = self.searchBar.text()
        current_category = self.current_filter_category()
        current_tag = self.current_filter_tag()
        case_sensitive = self.caseSensitiveCheckbox.isChecked()
        favorites_only = self.is_favorites_filter_active()
        print(f"Filtering by Search: '{search_term}', Category: {current_category}, Tag: {current_tag}, Case Sensitive: {case_sensitive}, Favorites: {favorites_only}")
        self.update_prompt_list(filter_category=current_category, filter_tag=current_tag, search_term=search_term, filter_favorites=favorites_only)

    def toggle_favorites_filter(self):
        favorites_only = self.is_favorites_filter_active()
        current_category = self.current_filter_category()
        current_tag = self.current_filter_tag()
        current_search = self.searchBar.text()
        print(f"Toggling Favorites Filter: {'Activated' if favorites_only else 'Deactivated'}")
        self.update_prompt_list(filter_category=current_category, filter_tag=current_tag, search_term=current_search, filter_favorites=favorites_only)

    def show_all_prompts(self):
        self.categoryList.clearSelection()
        self.tagList.clearSelection()
        self.searchBar.clear()
        self.showFavoritesButton.setChecked(False)
        print("Displaying all prompts (filters reset)")
        self.update_prompt_list()

    def is_favorites_filter_active(self):
        return self.showFavoritesButton.isChecked()

    def current_filter_category(self):
        selected_items = self.categoryList.selectedItems()
        return selected_items[0].text() if selected_items else None

    def current_filter_tag(self):
        selected_items = self.tagList.selectedItems()
        return selected_items[0].text() if selected_items else None

    def addPrompt(self):
        selected_category_items = self.categoryList.selectedItems()
        default_category = 'No category'
        if selected_category_items:
            default_category = selected_category_items[0].text()
        elif self.categories:
            default_category = self.categories[0]

        initial_data = {'category': default_category, 'favorite': False}

        dialog = PromptDialog(self, data=initial_data, categories=self.categories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.getPromptData()
            if not data['title']:
                QMessageBox.warning(self, "Missing Title", "Prompt title cannot be empty.")
                return

            prompt_id = self.next_id
            self.next_id += 1
            self.prompts[prompt_id] = {'data': data, 'history': [data]}
            self.update_category_list()
            self.update_tag_list()
            self.update_prompt_list(filter_category=self.current_filter_category(),
                                    filter_tag=self.current_filter_tag(),
                                    search_term=self.searchBar.text(),
                                    filter_favorites=self.is_favorites_filter_active())
            self.save_prompts()

    def editPrompt(self):
        prompt_id = self.get_selected_prompt_id()

        if prompt_id is None:
             selected_ids = self.get_selected_prompt_ids()
             if not selected_ids:
                 QMessageBox.warning(self, "No Selection", "Please select a prompt to edit.")
                 return
             if len(selected_ids) > 1:
                 QMessageBox.warning(self, "Multiple Selection", "Please select only one prompt to edit.")
                 return
             prompt_id = selected_ids[0]


        if prompt_id not in self.prompts:
            QMessageBox.critical(self, "Error", f"Could not find prompt with ID {prompt_id}.")
            return

        current_data = self.prompts[prompt_id]['data']
        history = self.prompts[prompt_id]['history']

        dialog = PromptDialog(self, current_data, history=history, categories=self.categories)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.getPromptData()
            if not new_data['title']:
                QMessageBox.warning(self, "Missing Title", "Prompt title cannot be empty.")
                return

            history_changed = False
            data_changed = new_data != current_data

            if dialog.history_purged:
                self.prompts[prompt_id]['history'] = [new_data]
                self.prompts[prompt_id]['data'] = new_data
                history_changed = True
                data_changed = True
                print(f"History purged and updated for ID {prompt_id}")

            elif data_changed:
                self.prompts[prompt_id]['data'] = new_data
                if not self.prompts[prompt_id]['history'] or new_data != self.prompts[prompt_id]['history'][-1]:
                     self.prompts[prompt_id]['history'].append(new_data)
                     history_changed = True
                     print(f"New version added to history for ID {prompt_id}")
                else:
                     print(f"Data identical to last history version for ID {prompt_id}, history not modified.")
            else:
                print(f"No changes detected for ID {prompt_id}, history not modified.")

            if data_changed:
                self.update_category_list()
                self.update_tag_list()
                self.update_prompt_list(filter_category=self.current_filter_category(),
                                        filter_tag=self.current_filter_tag(),
                                        search_term=self.searchBar.text(),
                                        filter_favorites=self.is_favorites_filter_active())
                self.save_prompts()
            else:
                print("No save necessary.")

    def deleteSelectedPrompts(self):
        selected_ids = self.get_selected_prompt_ids()

        if not selected_ids:
            QMessageBox.warning(self, "No Selection", "Please select at least one prompt to delete.")
            return

        prompts_to_delete_titles = [self.prompts[pid]['data'].get('title', 'Untitled') for pid in selected_ids if pid in self.prompts]

        count = len(selected_ids)
        if count == 1:
            message = f"Are you sure you want to delete the prompt '{prompts_to_delete_titles[0]}'?"
        else:
            message = f"Are you sure you want to delete the {count} selected prompts?"

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle('Deletion Confirmation')
        msgBox.setText(message)
        msgBox.setIcon(QMessageBox.Icon.Question)
        yesButton = msgBox.addButton("Yes", QMessageBox.ButtonRole.YesRole)
        noButton = msgBox.addButton("No", QMessageBox.ButtonRole.NoRole)
        msgBox.setDefaultButton(noButton)

        reply = msgBox.exec()

        if msgBox.clickedButton() == yesButton:
            deleted_count = 0
            for prompt_id in selected_ids:
                if prompt_id in self.prompts:
                    del self.prompts[prompt_id]
                    deleted_count += 1
                    print(f"Prompt ID {prompt_id} deleted.")

            if deleted_count > 0:
                print(f"{deleted_count} prompt(s) deleted.")
                self.update_category_list()
                self.update_tag_list()
                self.update_prompt_list(filter_category=self.current_filter_category(),
                                        filter_tag=self.current_filter_tag(),
                                        search_term=self.searchBar.text(),
                                        filter_favorites=self.is_favorites_filter_active())
                self.save_prompts()

    def current_filter_category(self):
        selected_items = self.categoryList.selectedItems()
        return selected_items[0].text() if selected_items else None

    def current_filter_tag(self):
        selected_items = self.tagList.selectedItems()
        return selected_items[0].text() if selected_items else None

    def save_prompts(self):
        try:
            self.categories.sort()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                prompts_to_save = {str(k): v for k, v in self.prompts.items()}
                # Save global_tags along with other data
                save_data = {
                    'next_id': self.next_id,
                    'prompts': prompts_to_save,
                    'categories': self.categories,
                    'global_tags': sorted(list(self.global_tags)) # Save as sorted list
                }
                json.dump(save_data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            QMessageBox.critical(self, "Save Error", f"Could not save prompts: {e}")
        except Exception as e:
             QMessageBox.critical(self, "Unknown Save Error", f"An unexpected error occurred while saving: {e}")


    def load_prompts(self):
        if not os.path.exists(self.data_file):
            self.prompts = {}
            self.next_id = 0
            self.categories = []
            self.global_tags = set() # Initialize global_tags if file doesn't exist
            return
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                self.next_id = loaded_data.get('next_id', 0)
                loaded_prompts = {}
                for k, v in loaded_data.get('prompts', {}).items():
                    try:
                        prompt_id = int(k)
                        if isinstance(v, dict) and 'data' in v and 'history' in v:
                             if 'category' not in v['data'] or not v['data']['category']:
                                 v['data']['category'] = 'No category'
                             if 'favorite' not in v['data']:
                                 v['data']['favorite'] = False
                             for history_entry in v.get('history', []):
                                 if 'favorite' not in history_entry:
                                     history_entry['favorite'] = False
                             loaded_prompts[prompt_id] = v
                        else:
                             print(f"Warning: Invalid structure for prompt ID '{k}', ignored.")
                    except ValueError:
                         print(f"Warning: Invalid prompt key '{k}', ignored.")

                self.prompts = loaded_prompts
                self.categories = loaded_data.get('categories', [])
                self.categories.sort()
                self.global_tags = set(loaded_data.get('global_tags', [])) # Load global_tags

        except (IOError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "Load Error", f"Could not load prompts from {self.data_file}: {e}")
            self.prompts = {}
            self.next_id = 0
            self.categories = []
            self.global_tags = set() # Reset global_tags on error
        except Exception as e:
            QMessageBox.critical(self, "Unknown Error", f"An unexpected error occurred while loading: {e}")
            self.prompts = {}
            self.next_id = 0
            self.categories = []
            self.global_tags = set() # Reset global_tags on error

    def show_context_menu(self, position):
        menu = QMenu()

        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        copy_prompt_action = menu.addAction("Copy Prompt")
        export_action = menu.addAction("Export")
        toggle_favorite_action = menu.addAction("Add to Favorites" if not self.is_selected_prompt_favorite() else "Remove from Favorites")

        edit_action.triggered.connect(self.editPrompt)
        delete_action.triggered.connect(self.deleteSelectedPrompts)
        copy_prompt_action.triggered.connect(self.copy_selected_prompt_text)
        export_action.triggered.connect(self.export_selected_prompts)
        toggle_favorite_action.triggered.connect(self.toggle_selected_prompt_favorite)

        selected_items = self.promptList.selectedItems()
        num_selected = len(selected_items)

        edit_action.setEnabled(num_selected == 1)
        copy_prompt_action.setEnabled(num_selected == 1)
        export_action.setEnabled(num_selected > 0)
        toggle_favorite_action.setEnabled(num_selected >= 1)
        delete_action.setEnabled(num_selected >= 1)

        menu.exec(self.promptList.mapToGlobal(position))

    def copy_selected_prompt_text(self):
        prompt_id = self.get_selected_prompt_id()
        if prompt_id is not None and prompt_id in self.prompts:
            prompt_text = self.prompts[prompt_id]['data'].get('prompt', '')
            clipboard = QApplication.clipboard()
            clipboard.setText(prompt_text)
            QToolTip.showText(self.promptList.mapToGlobal(self.promptList.viewport().rect().center()),
                              "Prompt copied!", msecShowTime=1500)
            print(f"Prompt ID {prompt_id} copied via context menu.")
        else:
            QMessageBox.warning(self, "Copy Failed", "Please select a prompt to copy.")

    def is_selected_prompt_favorite(self):
        selected_ids = self.get_selected_prompt_ids()
        if not selected_ids:
            return False
        return all(self.prompts[pid]['data'].get('favorite', False) for pid in selected_ids if pid in self.prompts)

    def toggle_selected_prompt_favorite(self):
        selected_ids = self.get_selected_prompt_ids()
        if not selected_ids:
            QMessageBox.warning(self, "No Selection", "Please select at least one prompt to change its favorite status.")
            return

        current_state_all_favorite = self.is_selected_prompt_favorite()
        new_favorite_state = not current_state_all_favorite

        prompts_changed = False
        for prompt_id in selected_ids:
            if prompt_id in self.prompts:
                current_favorite = self.prompts[prompt_id]['data'].get('favorite', False)
                if current_favorite != new_favorite_state:
                    self.prompts[prompt_id]['data']['favorite'] = new_favorite_state
                    if self.prompts[prompt_id]['history']:
                        self.prompts[prompt_id]['history'][-1]['favorite'] = new_favorite_state
                    prompts_changed = True
                    print(f"Prompt ID {prompt_id} favorite toggled to {new_favorite_state}.")

        if prompts_changed:
            self.update_prompt_list(filter_category=self.current_filter_category(),
                                    filter_tag=self.current_filter_tag(),
                                    search_term=self.searchBar.text(),
                                    filter_favorites=self.is_favorites_filter_active())
            self.save_prompts()
            QToolTip.showText(self.promptList.mapToGlobal(self.promptList.viewport().rect().center()),
                              f"Favorite status updated for {len(selected_ids)} prompt(s)!", msecShowTime=1500)
        else:
            print("No favorite status change necessary.")

    def export_selected_prompts(self):
        selected_ids = self.get_selected_prompt_ids()
        if not selected_ids:
            QMessageBox.warning(self, "No Selection", "Please select at least one prompt to export.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Export Selected Prompts", "",
                                                  "CSV Files (*.csv);;Markdown Files (*.md);;All Files (*)")
        if file_name:
            try:
                if file_name.lower().endswith('.csv'):
                    self._export_to_csv(file_name, selected_ids)
                elif file_name.lower().endswith('.md'):
                    self._export_to_markdown(file_name, selected_ids)
                else:
                    QMessageBox.warning(self, "Export Error", "Unsupported file format. Please use .csv or .md")
                    return
                QMessageBox.information(self, "Export Successful", f"Selected prompts exported to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export selected prompts: {e}")

    def export_prompts(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Prompts", "",
                                                  "CSV Files (*.csv);;Markdown Files (*.md);;All Files (*)")
        if file_name:
            try:
                if file_name.lower().endswith('.csv'):
                    self._export_to_csv(file_name)
                elif file_name.lower().endswith('.md'):
                    self._export_to_markdown(file_name)
                else:
                    QMessageBox.warning(self, "Export Error", "Unsupported file format. Please use .csv or .md")
                    return
                QMessageBox.information(self, "Export Successful", f"Prompts exported to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export prompts: {e}")

    def _export_to_csv(self, file_path, prompt_ids=None):
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'prompt', 'note', 'category', 'tags', 'favorite']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            prompts_to_export = self.prompts.items()
            if prompt_ids is not None:
                prompts_to_export = [(pid, self.prompts[pid]) for pid in prompt_ids if pid in self.prompts]

            for prompt_id, prompt_info in prompts_to_export:
                data = prompt_info['data']
                row = {
                    'title': data.get('title', ''),
                    'prompt': data.get('prompt', ''),
                    'note': data.get('note', ''),
                    'category': data.get('category', 'No category'),
                    'tags': ', '.join(data.get('tags', [])),
                    'favorite': 'Yes' if data.get('favorite', False) else 'No'
                }
                writer.writerow(row)

    def _export_to_markdown(self, file_path, prompt_ids=None):
        with open(file_path, 'w', encoding='utf-8') as mdfile:
            prompts_to_export = self.prompts.items()
            if prompt_ids is not None:
                prompts_to_export = [(pid, self.prompts[pid]) for pid in prompt_ids if pid in self.prompts]

            for prompt_id, prompt_info in prompts_to_export:
                data = prompt_info['data']
                mdfile.write(f"# {data.get('title', 'Untitled')}\n\n")
                mdfile.write(f"**Category:** {data.get('category', 'No category')}\n")
                mdfile.write(f"**Tags:** {', '.join(data.get('tags', []))}\n")
                mdfile.write(f"**Favorite:** {'Yes' if data.get('favorite', False) else 'No'}\n\n")
                mdfile.write("## Prompt\n")
                mdfile.write(f"{data.get('prompt', '')}\n\n")
                if data.get('note'):
                    mdfile.write("## Note\n")
                    mdfile.write(f"{data.get('note', '')}\n\n")
                mdfile.write("---\n\n") # Separator

    def import_prompts(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Prompts", "",
                                                  "CSV Files (*.csv);;Markdown Files (*.md);;All Files (*)")
        if file_name:
            try:
                imported_prompts = []
                if file_name.lower().endswith('.csv'):
                    imported_prompts = self._import_from_csv(file_name)
                elif file_name.lower().endswith('.md'):
                    imported_prompts = self._import_from_markdown(file_name)
                else:
                    QMessageBox.warning(self, "Import Error", "Unsupported file format. Please use .csv or .md")
                    return

                if not imported_prompts:
                    QMessageBox.information(self, "Import Complete", "No prompts found in the selected file.")
                    return

                imported_count = 0
                for prompt_data in imported_prompts:
                    if self._handle_imported_prompt(prompt_data):
                        imported_count += 1

                self.update_category_list()
                self.update_tag_list()
                self.update_prompt_list(filter_category=self.current_filter_category(),
                                        filter_tag=self.current_filter_tag(),
                                        search_term=self.searchBar.text(),
                                        filter_favorites=self.is_favorites_filter_active())
                self.save_prompts()
                QMessageBox.information(self, "Import Successful", f"Successfully imported {imported_count} prompt(s).")

            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import prompts: {e}")

    def _import_from_csv(self, file_path):
        prompts = []
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert 'Yes'/'No' to boolean for 'favorite'
                row['favorite'] = row.get('favorite', 'No').lower() == 'yes'
                # Convert tags string to list
                if 'tags' in row and row['tags']:
                    row['tags'] = [tag.strip() for tag in row['tags'].split(',')]
                else:
                    row['tags'] = []
                prompts.append(row)
        return prompts

    def _import_from_markdown(self, file_path):
        prompts = []
        current_prompt = {}
        current_section = None
        with open(file_path, 'r', encoding='utf-8') as mdfile:
            content = mdfile.read()
            # Split by '---' separator, then process each block
            blocks = content.split('---')
            for block in blocks:
                if not block.strip():
                    continue

                lines = block.strip().split('\n')
                current_prompt = {'title': '', 'prompt': '', 'note': '', 'category': 'No category', 'tags': [], 'favorite': False}
                current_section = None
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    if line.startswith('# '): # Title
                        current_prompt['title'] = line[2:].strip()
                        current_section = 'title'
                    elif line.startswith('## Prompt'):
                        current_section = 'prompt'
                    elif line.startswith('## Note'):
                        current_section = 'note'
                    elif line.startswith('**Category:**'):
                        current_prompt['category'] = line.replace('**Category:**', '').strip()
                    elif line.startswith('**Tags:**'):
                        tags_str = line.replace('**Tags:**', '').strip()
                        current_prompt['tags'] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                    elif line.startswith('**Favorite:**'):
                        current_prompt['favorite'] = line.replace('**Favorite:**', '').strip().lower() == 'yes'
                    elif current_section == 'prompt':
                        current_prompt['prompt'] += line + '\n'
                    elif current_section == 'note':
                        current_prompt['note'] += line + '\n'
                
                # Clean up trailing newlines
                current_prompt['prompt'] = current_prompt['prompt'].strip()
                current_prompt['note'] = current_prompt['note'].strip()

                if current_prompt.get('title') or current_prompt.get('prompt'): # Only add if it has some content
                    prompts.append(current_prompt)
        return prompts

    def _handle_imported_prompt(self, imported_data):
        # Check for existing prompt with the same title
        existing_prompt_id = None
        for pid, p_info in self.prompts.items():
            if p_info['data'].get('title') == imported_data.get('title'):
                existing_prompt_id = pid
                break

        if existing_prompt_id is not None:
            # Duplicate found, ask user for action
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Duplicate Prompt Detected")
            msg_box.setText(f"A prompt with the title '{imported_data.get('title', 'Untitled')}' already exists.")
            msg_box.setInformativeText("What would you like to do?")
            
            skip_button = msg_box.addButton("Skip", QMessageBox.ButtonRole.RejectRole)
            overwrite_button = msg_box.addButton("Overwrite", QMessageBox.ButtonRole.AcceptRole)
            keep_both_button = msg_box.addButton("Keep Both", QMessageBox.ButtonRole.ActionRole)
            
            msg_box.setDefaultButton(skip_button)
            
            msg_box.exec()

            if msg_box.clickedButton() == overwrite_button:
                # Overwrite existing prompt
                self.prompts[existing_prompt_id]['data'] = imported_data
                self.prompts[existing_prompt_id]['history'].append(imported_data) # Add to history
                print(f"Prompt '{imported_data.get('title')}' overwritten.")
                return True
            elif msg_box.clickedButton() == keep_both_button:
                # Add as a new prompt
                prompt_id = self.next_id
                self.next_id += 1
                self.prompts[prompt_id] = {'data': imported_data, 'history': [imported_data]}
                print(f"Prompt '{imported_data.get('title')}' imported as new.")
                return True
            else: # Skip
                print(f"Prompt '{imported_data.get('title')}' skipped.")
                return False
        else:
            # No duplicate, add as a new prompt
            prompt_id = self.next_id
            self.next_id += 1
            self.prompts[prompt_id] = {'data': imported_data, 'history': [imported_data]}
            print(f"Prompt '{imported_data.get('title')}' imported.")
            return True

    def manageCategories(self):
        dialog = CategoryDialog(self, self.categories)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_managed_categories = dialog.getCategories()
            new_managed_categories.sort()

            if new_managed_categories != self.categories:
                removed_categories = set(self.categories) - set(new_managed_categories)
                self.categories = new_managed_categories

                prompts_updated = False
                if removed_categories:
                    print(f"Categories removed from management: {removed_categories}")
                    for prompt_id, prompt_info in self.prompts.items():
                        current_category = prompt_info['data'].get('category', 'No category')
                        if current_category in removed_categories:
                            prompt_info['data']['category'] = 'No category'
                            if prompt_info['history']:
                                 prompt_info['history'][-1]['category'] = 'No category'
                            print(f"Prompt ID {prompt_id} moved to 'No category' because its category '{current_category}' was removed.")
                            prompts_updated = True

                self.update_category_list()
                self.update_prompt_list(filter_category=self.current_filter_category(),
                                        filter_tag=self.current_filter_tag(),
                                        search_term=self.searchBar.text(),
                                        filter_favorites=self.is_favorites_filter_active())
                self.save_prompts()
                print("Managed categories list and prompts updated and saved.")
            else:
                print("No changes detected in managed categories.")
        else:
            print("Category management cancelled.")

    def manageTags(self):
        # Pass the current global_tags to the dialog
        dialog = TagDialog(self, tags=list(self.global_tags))

        if dialog.exec() == QDialog.DialogCode.Accepted:
            renamed_tags, removed_tags, added_tags = dialog.getChanges()

            if not renamed_tags and not removed_tags and not added_tags:
                print("No tag changes to apply.")
                return

            prompts_updated = False
            # Apply renames and removals to existing prompts
            for prompt_id, prompt_info in self.prompts.items():
                current_prompt_tags = set(prompt_info['data'].get('tags', []))
                new_prompt_tags = set()
                tags_changed_for_prompt = False

                for tag in current_prompt_tags:
                    if tag in removed_tags:
                        tags_changed_for_prompt = True
                        continue
                    elif tag in renamed_tags:
                        new_prompt_tags.add(renamed_tags[tag])
                        tags_changed_for_prompt = True
                    else:
                        new_prompt_tags.add(tag)

                if tags_changed_for_prompt:
                    sorted_new_tags = sorted(list(new_prompt_tags))
                    prompt_info['data']['tags'] = sorted_new_tags
                    if prompt_info['history']:
                        prompt_info['history'][-1]['tags'] = sorted_new_tags
                    print(f"Tags updated for Prompt ID {prompt_id}: {sorted_new_tags}")
                    prompts_updated = True

            # Update global_tags based on changes from the dialog
            for old_name, new_name in renamed_tags.items():
                if old_name in self.global_tags:
                    self.global_tags.remove(old_name)
                self.global_tags.add(new_name)

            for tag in removed_tags:
                if tag in self.global_tags:
                    self.global_tags.remove(tag)

            for tag in added_tags:
                self.global_tags.add(tag)

            # Always mark as updated if any changes were made to global_tags or prompts
            if prompts_updated or renamed_tags or removed_tags or added_tags:
                print("Updating UI and saving after tag changes...")
                self.update_tag_list()
                self.update_prompt_list(filter_category=self.current_filter_category(),
                                        filter_tag=self.current_filter_tag(),
                                        search_term=self.searchBar.text(),
                                        filter_favorites=self.is_favorites_filter_active())
                self.save_prompts()
            else:
                print("No changes detected in tags.")
        else:
            print("Tag management cancelled.")
