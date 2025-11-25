# Changelog

All notable changes to Mango Stream Deck will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-25

### Added

- System tray integration for background operation
- Minimize to tray functionality (clicking X minimizes instead of closing)
- Tray icon context menu (Show, Hide, Quit)
- Mango logo in system tray
- Background process support
- `pystray` dependency for tray functionality
- `requirements.txt` file with all dependencies

### Changed

- Window close behavior now minimizes to tray
- Improved window state management
- Enhanced user experience with non-intrusive background mode

### Fixed

- Resource cleanup on application exit
- Window focus restoration from tray

## [1.0.0] - 2025-11-25

### Added

- Initial release
- Customizable button grid (1-8 rows and columns)
- 5 action types:
  - Open applications
  - Launch websites
  - Execute keyboard shortcuts
  - Type text automatically
  - Multi-action placeholder
- Visual customization:
  - Custom button colors with hex picker
  - Icon/image support with opacity control
  - Text customization (size, color, opacity)
  - Adjustable corner radius for buttons
- Icon management:
  - Local storage in icons folder
  - Smart deletion of unused icons
  - Duplicate prevention
- UI features:
  - Modern CustomTkinter interface
  - Dark and light mode themes
  - Settings dialog
  - Help system with user guide
  - Scrollable customization dialogs
- Configuration persistence:
  - JSON-based config storage
  - Session recovery
  - Reset to defaults option
- Application icon with mango logo
- Standalone Windows executable
- MIT License

### Dependencies

- customtkinter 5.2.2
- Pillow 12.0.0
- pyautogui 0.9.53 (optional, for hotkeys and text typing)
- pystray 0.19.5 (v1.1.0+)

---

## Release Links

- [v1.1.0](https://github.com/mrkool33/mango_Stream_Deck/releases/tag/v1.1.0)
- [v1.0.0](https://github.com/mrkool33/mango_Stream_Deck/releases/tag/v1.0.0)
