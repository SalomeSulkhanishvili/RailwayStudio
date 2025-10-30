"""
UI Theme and Styling Constants
Centralized styling for consistent UI appearance
"""

# Color Palette
COLORS = {
    # Primary colors
    'primary': '#48BB78',
    'primary_hover': '#38A169',
    'primary_pressed': '#2F855A',
    
    # Secondary colors
    'secondary': '#4299E1',
    'secondary_hover': '#3182CE',
    'secondary_pressed': '#2C5282',
    
    # Accent colors
    'accent': '#805AD5',
    'accent_hover': '#6B46C1',
    'accent_pressed': '#553C9A',
    
    # Danger colors
    'danger': '#F56565',
    'danger_hover': '#E53E3E',
    'danger_pressed': '#C53030',
    
    # Neutral colors
    'background': '#F7FAFC',
    'background_dark': '#EDF2F7',
    'surface': '#FFFFFF',
    'border': '#E2E8F0',
    'border_hover': '#CBD5E0',
    
    # Text colors
    'text_primary': '#1A202C',
    'text_secondary': '#2D3748',
    'text_muted': '#718096',
    'text_light': '#A0AEC0',
    
    # Status colors
    'success': '#48BB78',
    'warning': '#F6AD55',
    'error': '#FC8181',
    'info': '#4299E1',
    
    # Grid
    'grid_dot': '#D1D5DB',
    'grid_bg': '#F8F9FA',
}

# Font Sizes
FONT_SIZES = {
    'small': '11px',
    'normal': '13px',
    'medium': '14px',
    'large': '16px',
    'xlarge': '18px',
}

# Spacing
SPACING = {
    'xs': '4px',
    'sm': '8px',
    'md': '12px',
    'lg': '16px',
    'xl': '20px',
}

# Border Radius
RADIUS = {
    'sm': '4px',
    'md': '6px',
    'lg': '8px',
    'xl': '12px',
}


def get_button_style(
    bg_color: str,
    hover_color: str,
    pressed_color: str,
    text_color: str = 'white',
    padding: str = '10px 20px',
    border_radius: str = None,
    font_size: str = None
) -> str:
    """Generate button stylesheet"""
    border_radius = border_radius or RADIUS['lg']
    font_size = font_size or FONT_SIZES['normal']
    
    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: none;
            border-radius: {border_radius};
            padding: {padding};
            font-weight: 600;
            font-size: {font_size};
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['border']};
            color: {COLORS['text_light']};
        }}
    """


def get_primary_button_style() -> str:
    """Get primary button style"""
    return get_button_style(
        COLORS['primary'],
        COLORS['primary_hover'],
        COLORS['primary_pressed']
    )


def get_secondary_button_style() -> str:
    """Get secondary button style"""
    return get_button_style(
        COLORS['secondary'],
        COLORS['secondary_hover'],
        COLORS['secondary_pressed']
    )


def get_accent_button_style() -> str:
    """Get accent button style"""
    return get_button_style(
        COLORS['accent'],
        COLORS['accent_hover'],
        COLORS['accent_pressed']
    )


def get_danger_button_style() -> str:
    """Get danger button style"""
    return get_button_style(
        COLORS['danger'],
        COLORS['danger_hover'],
        COLORS['danger_pressed']
    )


def get_toggle_button_style() -> str:
    """Get toggle button style (for checkable buttons)"""
    return f"""
        QPushButton {{
            background-color: {COLORS['background']};
            color: {COLORS['text_secondary']};
            border: 2px solid {COLORS['border']};
            border-radius: {RADIUS['lg']};
            padding: 10px 18px;
            font-weight: 600;
            font-size: {FONT_SIZES['normal']};
        }}
        QPushButton:hover {{
            background-color: {COLORS['background_dark']};
            border-color: {COLORS['border_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['border']};
        }}
        QPushButton:checked {{
            background-color: {COLORS['secondary']};
            color: white;
            border-color: {COLORS['secondary']};
        }}
    """


def get_input_style() -> str:
    """Get input field style (QLineEdit, QSpinBox, etc.)"""
    return f"""
        QSpinBox, QLineEdit, QComboBox {{
            background-color: {COLORS['background']};
            border: 2px solid {COLORS['border']};
            border-radius: {RADIUS['md']};
            padding: 6px 10px;
            color: {COLORS['text_secondary']};
            font-size: {FONT_SIZES['normal']};
        }}
        QSpinBox:hover, QLineEdit:hover, QComboBox:hover {{
            border-color: {COLORS['border_hover']};
            background-color: {COLORS['background_dark']};
        }}
        QSpinBox:focus, QLineEdit:focus, QComboBox:focus {{
            border-color: {COLORS['secondary']};
        }}
    """


def get_combo_box_style() -> str:
    """Get combo box style"""
    return f"""
        QComboBox {{
            background-color: {COLORS['background']};
            border: 2px solid {COLORS['border']};
            border-radius: {RADIUS['lg']};
            padding: 8px 12px;
            color: {COLORS['text_secondary']};
            font-size: {FONT_SIZES['normal']};
            min-width: 130px;
        }}
        QComboBox:hover {{
            border-color: {COLORS['border_hover']};
            background-color: {COLORS['background_dark']};
        }}
        QComboBox::drop-down {{
            border: none;
            padding-right: 10px;
        }}
    """


def get_card_style() -> str:
    """Get card container style"""
    return f"""
        QGroupBox {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['xl']};
            padding: 16px;
            margin-top: 10px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: {COLORS['text_primary']};
        }}
    """


def get_label_style(color: str = None, size: str = 'normal', weight: str = 'normal') -> str:
    """Get label style"""
    color = color or COLORS['text_secondary']
    font_size = FONT_SIZES.get(size, FONT_SIZES['normal'])
    font_weight = '600' if weight == 'bold' else 'normal'
    
    return f"color: {color}; font-weight: {font_weight}; font-size: {font_size};"

