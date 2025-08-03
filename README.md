![](https://repository-images.githubusercontent.com/1031380370/45369aed-0984-47e7-b9d0-587b5637d93c)
# PromptVault

PromptVault is a prompt management application designed to help users easily organize, store, and retrieve their prompts for various AI applications, software development, content marketing, and much more. Whether you are a developer, writer, marketer, or simply a user of AI-based tools, PromptVault allows you to centralize your prompts and improve your productivity.

## Features

*   **Prompt Management**: Create, edit, and delete prompts with titles, content, categories, and tags.
*   **Categorization**: Organize your prompts by customizable categories for better structuring.
*   **Tagging**: Add tags to your prompts for quick search and filtering.
*   **Search and Filtering**: Quickly find the prompts you need with advanced search and filtering features.
*   **Versioning**: Track prompt history to maintain a complete record of changes, and easily roll back to previous versions if needed.
*   **Intuitive User Interface**: A simple and easy-to-use graphical interface for a pleasant user experience.

## File Structure

*   `main.py`: The main entry point of the application.
*   `prompt_manager_widget.py`: Manages the user interface for prompt management.
*   `prompt_dialog.py`: Dialog for adding or editing a prompt.
*   `category_dialog.py`: Dialog for managing categories.
*   `tag_dialog.py`: Dialog for managing tags.
*   `prompts_data.json`: JSON file to store prompt data.

## Installation

To install and run PromptVault locally, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Medenor/PromptVault.git
    cd PromptVault
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To launch the application, run the `main.py` script:

```bash
python main.py
```

The application will open, allowing you to start managing your prompts.

## Contribution

Contributions are welcome! If you wish to improve PromptVault, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/new-feature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add a new feature'`).
5.  Push to the branch (`git push origin feature/new-feature`).
6.  Open a Pull Request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
