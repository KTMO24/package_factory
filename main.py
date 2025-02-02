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
                errors.append("Invalid dependency format: " + dep)
                
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
        self.file_manager.add_file(pkg_name + "/pyproject.toml", json.dumps(pyproject, indent=4))
        
        # Generate standard files
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
        init_content = '"""Package {}"""\n\n__version__ = "{}"\n'.format(pkg_name, self.version.value)
        self.file_manager.add_file(pkg_name + "/" + pkg_name + "/__init__.py", init_content)
        
        # README.md
        readme_content = self.generate_readme_content(pkg_name)
        self.file_manager.add_file(pkg_name + "/README.md", readme_content)
        
        # LICENSE
        license_content = self.generate_license_content()
        self.file_manager.add_file(pkg_name + "/LICENSE", license_content)
        
    def generate_test_files(self, pkg_name):
        """Generate test files"""
        test_content = ("import pytest\n"
                        "from {} import __version__\n\n"
                        "def test_version():\n"
                        "    assert __version__ == \"{}\"\n").format(pkg_name, self.version.value)
        self.file_manager.add_file(pkg_name + "/tests/__init__.py", "")
        self.file_manager.add_file(pkg_name + "/tests/test_main.py", test_content)
        self.file_manager.add_file(pkg_name + "/pytest.ini", "[pytest]\npython_files = test_*.py")
        
    def generate_doc_files(self, pkg_name):
        """Generate documentation files"""
        if self.use_gemini.value and GEMINI_AVAILABLE:
            docs_content = self.generate_gemini_content("Generate documentation for Python package '{}' that {}".format(pkg_name, self.description.value))
        else:
            docs_content = self.generate_basic_docs(pkg_name)
            
        self.file_manager.add_file(pkg_name + "/docs/index.md", docs_content)
        
    def generate_readme_content(self, pkg_name):
        """Generate README content"""
        return ("# {}\n\n"
                "{}\n\n"
                "## Installation\n\n"
                "```bash\n"
                "pip install {}\n"
                "```\n\n"
                "## Usage\n\n"
                "```python\n"
                "import {}\n"
                "```\n\n"
                "## License\n\n"
                "{}\n").format(pkg_name, self.description.value, pkg_name, pkg_name, self.license_type.value)

    def generate_license_content(self):
        """Generate license content"""
        year = datetime.now().year
        author = self.author.value
        if self.license_type.value == 'MIT':
            return ("MIT License\n\n"
                    "Copyright (c) {} {}\n\n"
                    "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
                    "of this software and associated documentation files (the \"Software\"), to deal\n"
                    "in the Software without restriction, including without limitation the rights\n"
                    "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
                    "copies of the Software, and to permit persons to whom the Software is\n"
                    "furnished to do so, subject to the following conditions:\n\n"
                    "[... MIT text truncated for brevity ...]\n").format(year, author)
        return "# " + self.license_type.value + " license content not defined"
    
    def generate_gemini_content(self, prompt):
        """Generate content using Gemini AI if available"""
        if not GEMINI_AVAILABLE:
            return "# AI-generated content not available\n"
        try:
            gemini_key = os.environ.get('GEMINI_KEY')
            if not gemini_key:
                return "# No GEMINI_KEY found in environment\n"
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return "# Error generating AI content: {}\n".format(str(e))
        
    def generate_basic_docs(self, pkg_name):
        """Generate basic documentation content"""
        return ("# {} Documentation\n\n"
                "## Installation\n\n"
                "```bash\n"
                "pip install {}\n"
                "```\n\n"
                "## Usage\n\n"
                "```python\n"
                "import {}\n"
                "```\n").format(pkg_name, pkg_name, pkg_name)
        
    def update_file_list(self):
        """Update the file list widget with all files from the manager"""
        self.file_list.options = self.file_manager.get_all_files()
        
    def on_generate_package_clicked(self, b):
        """Callback for when the Generate Package button is clicked"""
        with self.status_output:
            self.status_output.clear_output()
            errors = self.validate_inputs()
            if errors:
                for error in errors:
                    print(error)
                return
            try:
                self.generate_package_files()
                print("Package '{}' created successfully!".format(self.package_name.value))
                self.download_button.disabled = False
            except Exception as e:
                print("Error generating package: {}".format(str(e)))
        
    def on_download_zip_clicked(self, b):
        """Callback for when the Download ZIP button is clicked"""
        with self.status_output:
            self.status_output.clear_output()
            try:
                pkg_name = self.package_name.value
                zip_data = self.file_manager.create_zip()
                filename = pkg_name + ".zip"
                from ipywidgets import FileDownload
                fd = FileDownload(
                    data=zip_data,
                    filename=filename,
                    description="Download Package"
                )
                display(fd)
            except Exception as e:
                print("Error preparing download: {}".format(str(e)))
                
    def on_save_file_clicked(self, b):
        """Callback for when the Save File button is clicked"""
        file_path = self.file_list.value
        if file_path:
            self.file_manager.update_file(file_path, self.file_editor.value)
            with self.status_output:
                print("Changes saved for '{}'.".format(file_path))
        else:
            with self.status_output:
                print("No file selected to save.")
                
    def on_delete_file_clicked(self, b):
        """Callback for when the Delete File button is clicked"""
        file_path = self.file_list.value
        if file_path:
            self.file_manager.delete_file(file_path)
            self.update_file_list()
            self.file_editor.value = ""
            with self.status_output:
                print("File '{}' deleted.".format(file_path))
        else:
            with self.status_output:
                print("No file selected to delete.")
                
    def on_add_file_clicked(self, b):
        """Callback for when the Add File button is clicked"""
        new_path = self.new_file_name.value.strip()
        if new_path:
            # Add empty content for the new file
            self.file_manager.add_file(new_path, "")
            self.update_file_list()
            self.new_file_name.value = ""
            with self.status_output:
                print("File '{}' added.".format(new_path))
        else:
            with self.status_output:
                print("Enter a valid file path to add.")
                
    def on_file_selected(self, change):
        """When a file is selected from the file list, load its content into the editor."""
        file_path = change.new
        if file_path:
            content = self.file_manager.get_file(file_path)
            self.file_editor.value = content
        else:
            self.file_editor.value = ""

# Create and display the enhanced generator UI
generator = EnhancedPackageGenerator()
generator.display()
