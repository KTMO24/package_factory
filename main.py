import os
import re
import json
import zipfile
from io import BytesIO
from datetime import datetime
from pathlib import Path
import ipywidgets as widgets
from IPython.display import display, HTML
import syntaxhighlight as sh

# OPTIONAL: For AI file generation via Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class FileManager:
    """Handles file operations and content management"""
    def __init__(self):
        self.files = {}
        self.current_file = None
        
    def add_file(self, path, content):
        """Add or update a file in the manager"""
        self.files[path] = content
        
    def get_file(self, path):
        """Retrieve file content"""
        return self.files.get(path, '')
        
    def update_file(self, path, content):
        """Update existing file content"""
        if path in self.files:
            self.files[path] = content
            return True
        return False
        
    def delete_file(self, path):
        """Remove a file from the manager"""
        if path in self.files:
            del self.files[path]
            return True
        return False
        
    def get_all_files(self):
        """Get list of all files"""
        return sorted(self.files.keys())
        
    def create_zip(self):
        """Create a ZIP file from all managed files"""
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for path, content in self.files.items():
                zf.writestr(path, content)
        return zip_buffer.getvalue()

class EnhancedPackageGenerator:
    def __init__(self):
        self.file_manager = FileManager()
        self.setup_ui_components()
        self.setup_layout()
        
    def setup_ui_components(self):
        """Initialize all UI components"""
        # Style definitions
        self.style = self.get_style_definitions()
        
        # Basic Info Components
        self.setup_basic_info_components()
        
        # Advanced Settings Components
        self.setup_advanced_settings_components()
        
        # File Manager Components
        self.setup_file_manager_components()
        
        # Action Buttons
        self.setup_action_buttons()
        
        # Output Areas
        self.status_output = widgets.Output()
        self.preview_output = widgets.Output()
        
    def get_style_definitions(self):
        """Define custom styles for the UI"""
        return HTML("""
        <style>
        .widget-label { min-width: 130px; }
        .custom-header { 
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .file-manager {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
        }
        .editor-area {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            background-color: #f8f9fa;
        }
        </style>
        """)
        
    def setup_basic_info_components(self):
        """Setup basic package information components"""
        self.package_name = widgets.Text(
            value='my_package',
            description='Package Name:',
            style={'description_width': 'initial'}
        )
        
        self.version = widgets.Text(
            value='0.1.0',
            description='Version:',
            pattern=r'^\d+\.\d+\.\d+$',
            style={'description_width': 'initial'}
        )
        
        self.author = widgets.Text(
            value='Your Name',
            description='Author:',
            style={'description_width': 'initial'}
        )
        
        self.email = widgets.Text(
            value='',
            description='Email:',
            style={'description_width': 'initial'}
        )
        
        self.description = widgets.Textarea(
            value='A short description of your package',
            description='Description:',
            layout=widgets.Layout(width='600px', height='100px')
        )
        
    def setup_advanced_settings_components(self):
        """Setup advanced package settings components"""
        self.python_requires = widgets.Text(
            value='>=3.8',
            description='Python Required:',
            style={'description_width': 'initial'}
        )
        
        self.keywords = widgets.Text(
            value='',
            description='Keywords:',
            placeholder='Comma-separated keywords',
            style={'description_width': 'initial'}
        )
        
        self.dependencies = widgets.Textarea(
            value='',
            description='Dependencies:',
            placeholder='One package per line (e.g., requests>=2.25.1)',
            layout=widgets.Layout(width='600px', height='100px')
        )
        
        self.license_type = widgets.Dropdown(
            options=['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause'],
            value='MIT',
            description='License:',
            style={'description_width': 'initial'}
        )
        
        self.include_tests = widgets.Checkbox(
            value=True,
            description='Include tests directory'
        )
        
        self.include_docs = widgets.Checkbox(
            value=True,
            description='Include docs directory'
        )
        
        self.use_gemini = widgets.Checkbox(
            value=False,
            description='Use Gemini for docs'
        )
        
    def setup_file_manager_components(self):
        """Setup file manager components"""
        self.file_list = widgets.Select(
            options=[],
            description='Files:',
            layout=widgets.Layout(width='300px', height='400px')
        )
        
        self.file_editor = widgets.Textarea(
            value='',
            description='Content:',
            layout=widgets.Layout(width='700px', height='400px')
        )
        
        self.new_file_name = widgets.Text(
            value='',
            description='New File:',
            placeholder='Enter file path',
            style={'description_width': 'initial'}
        )
        
    def setup_action_buttons(self):
        """Setup all action buttons"""
        self.generate_button = widgets.Button(
            description='Generate Package',
            button_style='primary',
            icon='check'
        )
        
        self.download_button = widgets.Button(
            description='Download ZIP',
            button_style='success',
            icon='download',
            disabled=True
        )
        
        self.save_file_button = widgets.Button(
            description='Save File',
            button_style='info',
            icon='save'
        )
        
        self.delete_file_button = widgets.Button(
            description='Delete File',
            button_style='danger',
            icon='trash'
        )
        
        self.add_file_button = widgets.Button(
            description='Add File',
            button_style='warning',
            icon='plus'
        )
        
        # Wire up button callbacks
        self.generate_button.on_click(self.on_generate_package_clicked)
        self.download_button.on_click(self.on_download_zip_clicked)
        self.save_file_button.on_click(self.on_save_file_clicked)
        self.delete_file_button.on_click(self.on_delete_file_clicked)
        self.add_file_button.on_click(self.on_add_file_clicked)
        self.file_list.observe(self.on_file_selected, names='value')
        
    def setup_layout(self):
        """Create the main UI layout"""
        # Basic Info Section
        basic_info = widgets.VBox([
            widgets.HBox([
                widgets.VBox([
                    self.package_name,
                    self.version,
                    self.author,
                    self.email
                ]),
                widgets.VBox([
                    self.description,
                    self.keywords
                ])
            ])
        ])
        
        # Advanced Settings Section
        advanced_settings = widgets.VBox([
            widgets.HBox([
                widgets.VBox([
                    self.python_requires,
                    self.license_type
                ]),
                self.dependencies
            ]),
            widgets.HBox([
                self.include_tests,
                self.include_docs,
                self.use_gemini
            ])
        ])
        
        # File Manager Section
        file_manager = widgets.VBox([
            widgets.HTML("<h3>File Manager</h3>"),
            widgets.HBox([
                widgets.VBox([
                    self.file_list,
                    widgets.HBox([
                        self.new_file_name,
                        self.add_file_button
                    ])
                ]),
                widgets.VBox([
                    self.file_editor,
                    widgets.HBox([
                        self.save_file_button,
                        self.delete_file_button
                    ])
                ])
            ])
        ], layout={'border': '1px solid #ddd', 'padding': '10px'})
        
        # Action Buttons Section
        action_buttons = widgets.HBox([
            self.generate_button,
            self.download_button
        ])
        
        # Main Layout
        self.main_layout = widgets.VBox([
            self.style,
            widgets.HTML("<div class='custom-header'><h2>Enhanced Python Package Generator</h2></div>"),
            basic_info,
            widgets.HTML("<h3>Advanced Settings</h3>"),
            advanced_settings,
            file_manager,
            action_buttons,
            self.status_output,
            self.preview_output
        ])
        
    def display(self):
        """Display the complete UI"""
        display(self.main_layout)
        
    def validate_inputs(self):
        """Validate user inputs"""
        errors = []
        
        # Package name validation
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', self.package_name.value):
            errors.append("Invalid package name format")
            
        # Version validation
        if not re.match(r'^\d+\.\d+\.\d+$', self.version.value):
            errors.append("Invalid version format (use X.Y.Z)")
            
        # Email validation
        if self.email.value and not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.email.value):
            errors.append("Invalid email format")
            
        # Dependencies validation
        for dep in self.dependencies.value.split('\n'):
            dep = dep.strip()
            if dep and not re.match(r'^[a-zA-Z0-9_-]+([><=]=?\d+\.\d+\.\d+)?$', dep):
                errors.append(f"Invalid dependency format: {dep}")
                
        return errors
        
    def generate_package_files(self):
        """Generate all package files"""
        pkg_name = self.package_name.value
        
        # Generate pyproject.toml
        pyproject = {
            "build-system": {
                "requires": ["setuptools>=45", "wheel"],
                "build-backend": "setuptools.build_meta"
            },
            "project": {
                "name": pkg_name,
                "version": self.version.value,
                "description": self.description.value,
                "authors": [{"name": self.author.value, "email": self.email.value}],
                "license": {"text": self.license_type.value},
                "requires-python": self.python_requires.value,
                "keywords": [k.strip() for k in self.keywords.value.split(',') if k.strip()],
                "dependencies": [d.strip() for d in self.dependencies.value.split('\n') if d.strip()]
            }
        }
        
        # Add files to manager
        self.file_manager.add_file(
            f"{pkg_name}/pyproject.toml",
            json.dumps(pyproject, indent=4)
        )
        
        # Generate other standard files
        self.generate_standard_files(pkg_name)
        
        # Generate optional files
        if self.include_tests.value:
            self.generate_test_files(pkg_name)
            
        if self.include_docs.value:
            self.generate_doc_files(pkg_name)
            
        # Update file list
        self.update_file_list()
        
    def generate_standard_files(self, pkg_name):
        """Generate standard package files"""
        # __init__.py
        init_content = f'"""Package {pkg_name}"""\n\n__version__ = "{self.version.value}"\n'
        self.file_manager.add_file(f"{pkg_name}/{pkg_name}/__init__.py", init_content)
        
        # README.md
        readme_content = self.generate_readme_content(pkg_name)
        self.file_manager.add_file(f"{pkg_name}/README.md", readme_content)
        
        # LICENSE
        license_content = self.generate_license_content()
        self.file_manager.add_file(f"{pkg_name}/LICENSE", license_content)
        
    def generate_test_files(self, pkg_name):
        """Generate test files"""
        test_content = f"""import pytest
from {pkg_name} import __version__

def test_version():
    assert __version__ == "{self.version.value}"
"""
        self.file_manager.add_file(f"{pkg_name}/tests/__init__.py", "")
        self.file_manager.add_file(f"{pkg_name}/tests/test_main.py", test_content)
        self.file_manager.add_file(f"{pkg_name}/pytest.ini", "[pytest]\npython_files = test_*.py")
        
    def generate_doc_files(self, pkg_name):
        """Generate documentation files"""
        if self.use_gemini.value and GEMINI_AVAILABLE:
            docs_content = self.generate_gemini_content(
                f"Generate documentation for Python package '{pkg_name}' that {self.description.value}"
            )
        else:
            docs_content = self.generate_basic_docs(pkg_name)
            
        self.file_manager.add_file(f"{pkg_name}/docs/index.md", docs_content)
        
    def generate_readme_content(self, pkg_name):
        """Generate README content"""
        return f"""# {pkg_name}

{self.description.value}

## Installation

```bash
pip install {pkg_name}
```

## Usage

```python
import {pkg_name}
```

## License

{self.license_type.value}
"""

    def generate_license_content(self):
        """Generate license content"""
        year = datetime.now().year
        author = self.author.value
        
        if self.license_type.value == 'MIT':
            return f"""MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights</antArtifact>
