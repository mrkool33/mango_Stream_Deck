# 🥭 Mango Stream Deck

A professional Python-based Stream Deck application with a modern GUI, customizable button grid, and multiple action types.

[![Download Latest Release](https://github.com/mrkool33/mango_Stream_Deck/releases/latest)
[![Downloads](https://github.com/mrkool33/mango_Stream_Deck/releases)

## 📥 Download

**[Download Latest Release](https://github.com/mrkool33/mango_Stream_Deck/releases/latest)** - Windows 10/11

Extract the ZIP file and run `Mango Stream Deck.exe` - no installation required!

## ✨ Features

### Button Customization

- **Dynamic Grid**: Adjustable grid size (1-8 rows and columns)
- **Button Actions**: 5 action types per button
  - **Open**: Launch applications
  - **Website**: Open URLs in browser
  - **Hotkey**: Record and execute keyboard shortcuts
  - **Text**: Type text automatically
  - **Multi Action**: Execute multiple actions (coming soon)
- **Visual Customization**:
  - Custom button colors with hex picker and presets
  - Icon/image support with opacity control
  - Text customization (size, color, opacity)
  - Adjustable corner radius for buttons

### Icon Management

- **Local Storage**: Icons are copied to and stored in the `icons` folder
- **Smart Deletion**: Unused icons are automatically deleted when removed
- **Duplicate Prevention**: Automatic unique naming for duplicate files

### UI Features

- **Modern Design**: CustomTkinter-based professional interface
- **Themes**: Dark and light mode toggle
- **Centered Layout**: Settings and customization dialogs centered on screen
- **Help System**: Comprehensive user guide accessible from header
- **Scrollable Dialogs**: Customization panels with scrollable content
- **Status Feedback**: Real-time status updates for user actions

### Configuration & Persistence

- **JSON Config**: All settings saved to `button_config.json`
- **Session Recovery**: Automatically loads previous button configurations
- **Reset to Defaults**: One-click reset with warning confirmation

## 💻 For Developers

### Requirements

- Python 3.12+
- tkinter (included with Python)
- customtkinter 5.2.2
- Pillow 12.0.0
- (Optional) pyautogui - for hotkey and text typing features

### Installation

1. Clone the repository:

```bash
git clone https://github.com/mrkool33/mango_Stream_Deck.git
cd mango_Stream_Deck
```

2. Install required packages:

```bash
pip install customtkinter Pillow pyautogui
```

3. Run the application:

```bash
python main.py
```

### Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name="Mango Stream Deck" --add-data "logos;logos" main.py --clean
```

The executable will be in the `dist` folder.

## 🎯 Usage

### Basic Setup

1. **Grid Configuration**: Click the Settings button to adjust grid size and corner radius
2. **Theme**: Toggle between dark and light mode with the Theme button
3. **Help**: Click the Help button for detailed instructions

### Customizing Buttons

1. **Right-click** any button to open the customization dialog
2. Configure the button:
   - **Title**: Set button name/display text
   - **Text Appearance**: Adjust text size (6-72), color, and opacity
   - **Color**: Pick button background color with hex input or presets
   - **Icon**: Select and manage button icons with opacity control
   - **Action**: Choose action type and configure parameters
3. Click **OK** to save and close, or **Save** to save without closing

### Icon Management

- **Browse**: Select an image to use as button icon (copied to `icons` folder)
- **Clear**: Remove icon from button (file only deleted on Save if unused)
- Icons are automatically deleted when:
  - Removed from a button and not used elsewhere
  - When resetting to defaults

### Actions

#### Open Application

- Select an .exe or application file
- Button executes the application when clicked

#### Website

- Enter a URL (http:// or https://)
- Opens the website in default browser

#### Hotkey

- Click "Record" button
- Press the desired keyboard shortcut
- Button will execute that hotkey combination

#### Text

- Enter text to type
- Button will type the text when clicked

#### Multi Action

- Coming soon feature for executing multiple actions

### Settings

- **Grid Size**: 1-8 rows and columns
- **Corner Radius**: 0-50 pixels
- **Theme**: Dark or Light mode
- **Reset to Defaults**: Clear all configurations and icons

## 📁 File Structure

```
mango_Stream_Deck/
├── main.py                 # Main application file
├── create_icon.py          # Icon creation utility
├── icon.ico                # Application icon
├── button_config.json      # Saved button configurations (auto-generated)
├── icons/                  # Folder for stored button icons
├── logos/                  # Application logos
│   ├── mango_256_transparent.png
│   └── mango_32_transparent.png
├── dist/                   # Built executable (after PyInstaller)
└── README.md               # This file
```

## Keyboard Shortcuts

- **Right-click** on any button: Open customization dialog
- **Escape** (when in dialog): Close dialog

## Configuration File Format

`button_config.json` structure:

```json
{
  "grid_cols": 4,
  "grid_rows": 3,
  "corner_radius": 15,
  "theme": "dark",
  "buttons": {
    "1": {
      "text": "Button Name",
      "image_path": "icons/image.png",
      "app_path": "/path/to/app.exe",
      "color": "#2196F3",
      "text_size": 12,
      "text_color": "white",
      "color_opacity": 100,
      "image_opacity": 100,
      "action_type": "Open",
      "url": null,
      "hotkey": null,
      "type_text": null
    }
  }
}
```

## 🔧 Troubleshooting

**Icons not loading**: Ensure images are in supported formats (PNG, JPG, GIF, BMP)

**Hotkey not recording**: Requires pyautogui to be installed (`pip install pyautogui`)

**Settings not saving**: Check that `button_config.json` is writable in the application directory

**CustomTkinter errors**: Update to the latest version: `pip install --upgrade customtkinter`

**Executable not running**: Make sure the `logos` folder is in the same directory as the `.exe` file

## 🚀 Future Enhancements

- Multi Action sequences
- Custom button layouts
- Macro recording and playback
- Cloud synchronization
- Plugin system for extensions
- Advanced scheduling options

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 👨‍💻 Author

Created by [mrkool33](https://github.com/mrkool33)

## ⭐ Support

If you like this project, please give it a star on GitHub!
