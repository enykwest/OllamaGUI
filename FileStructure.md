# Project Structure

```
OllamaGUI/
├── src/
│   ├── __init__.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── base_window.py  # BaseWindow class
│   │   └── custom_windows.py  # Derived window classes
│   ├── utils/
│   │   ├── __init__.py
│   │   └── file_helpers.py  # Additional utilities
│   └── main.py  # Application entry point
├── FileStructure.md
├── README.md
├── LICENSE
├── TestConvo-2025-05-14-100827.md
└── requirements.txt (TBD, should be replaced with .toml)
```

This structure follows Python packaging conventions and separates concerns for better maintainability. All GUI related code should go into src/gui while backend related code goes into src/utils. src/main.py ties everything together.

>[!note]
> `__init__.py` can be completely empty. It simply tells Python to look for submodules inside that directory. [It can also be used to initialize things upon import.](https://stackoverflow.com/questions/448271/what-is-init-py-for)

## ChatWindow Class

The `ChatWindow` class in `src/gui/chat_window.py` serves as the foundation for all other windows in the application. It provides:

- Basic window setup and configuration
- Standard menu structure (File, Edit, Options)
- Common file operations (New, Open, Save, Save As)
- Input/output widgets and basic functionality

This class should be as generic as possible while including functionality common to all windows. If a GUI feature is needed for ALL LLM backends, then ChatWindowshould be updated. Placeholder functions may be used and src/main.py can be updated to read requirements from the LLMbackend and update the appropriate functions.

## Creating Custom Windows

See src/gui/chat_window.py , esspecially ChatWindow.create_menu