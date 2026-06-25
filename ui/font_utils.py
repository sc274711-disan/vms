# ui/font_utils.py
import json
import os

UI_SETTINGS_FILE = "ui_settings.json"

FONT_SIZES = {
    "small": 10,
    "medium": 12,
    "large": 14,
    "xlarge": 16,
    "xxlarge": 18
}

def load_ui_settings():
    """Load UI settings from file"""
    if not os.path.exists(UI_SETTINGS_FILE):
        default = {
            "theme": "dark",
            "accent": "blue",
            "font_size": "medium"
        }
        with open(UI_SETTINGS_FILE, "w") as f:
            json.dump(default, f)
        return default
    with open(UI_SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_ui_settings(data):
    """Save UI settings to file"""
    with open(UI_SETTINGS_FILE, "w") as f:
        json.dump(data, f)

def get_font_size():
    """Get current font size in points"""
    settings = load_ui_settings()
    font_key = settings.get("font_size", "medium")
    return FONT_SIZES.get(font_key, 12)

def get_font_key():
    """Get current font size key"""
    settings = load_ui_settings()
    return settings.get("font_size", "medium")

def get_font_family():
    """Get font family"""
    return "Arial"

def get_font(size=None):
    """Get font tuple for customtkinter"""
    if size is None:
        size = get_font_size()
    return (get_font_family(), size)

def get_font_bold(size=None):
    """Get bold font tuple for customtkinter"""
    if size is None:
        size = get_font_size()
    return (get_font_family(), size, "bold")