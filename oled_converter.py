"""
OLED Function Converter v2.0
Convert old OLED function calls to new format with two conversion modes
"""

import re
import sys
from typing import Optional, List, Tuple, Dict
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog

class OLEDConverter:
    """OLED function converter with two modes"""

    def __init__(self):
        # Conversion rules for mode 1: direct function conversion
        self.direct_conversion = {
            "OLED_ShowChar": {
                "old_params": ["uint8_t Line", "uint8_t Column", "char Char"],
                "new_params": ["int16_t X", "int16_t Y", "char Char", "uint8_t FontSize"],
                "new_name": "OLED_ShowChar",
            },
            "OLED_ShowString": {
                "old_params": ["uint8_t Line", "uint8_t Column", "char *String"],
                "new_params": ["int16_t X", "int16_t Y", "char *String", "uint8_t FontSize"],
                "new_name": "OLED_ShowString",
            },
            "OLED_ShowNum": {
                "old_params": ["uint8_t Line", "uint8_t Column", "uint32_t Number", "uint8_t Length"],
                "new_params": ["int16_t X", "int16_t Y", "uint32_t Number", "uint8_t Length", "uint8_t FontSize"],
                "new_name": "OLED_ShowNum",
            },
            "OLED_ShowSignedNum": {
                "old_params": ["uint8_t Line", "uint8_t Column", "int32_t Number", "uint8_t Length"],
                "new_params": ["int16_t X", "int16_t Y", "int32_t Number", "uint8_t Length", "uint8_t FontSize"],
                "new_name": "OLED_ShowSignedNum",
            },
            "OLED_ShowHexNum": {
                "old_params": ["uint8_t Line", "uint8_t Column", "uint32_t Number", "uint8_t Length"],
                "new_params": ["int16_t X", "int16_t Y", "uint32_t Number", "uint8_t Length", "uint8_t FontSize"],
                "new_name": "OLED_ShowHexNum",
            },
            "OLED_ShowBinNum": {
                "old_params": ["uint8_t Line", "uint8_t Column", "uint32_t Number", "uint8_t Length"],
                "new_params": ["int16_t X", "int16_t Y", "uint32_t Number", "uint8_t Length", "uint8_t FontSize"],
                "new_name": "OLED_ShowBinNum",
            },
        }

    def convert_line(self, line: str, conversion_mode: int, font_size: str) -> Optional[str]:
        """Convert a single line based on conversion mode"""
        line = line.strip()
        if not line or line.startswith('//'):
            return line

        # Try to match function calls
        for func_name in self.direct_conversion.keys():
            pattern = re.compile(fr'{func_name}\s*\(\s*(.*?)\s*\)\s*;')
            match = pattern.search(line)
            if match:
                params_str = match.group(1)
                params = self._parse_params(params_str)

                if len(params) >= len(self.direct_conversion[func_name]["old_params"]):
                    if conversion_mode == 1:
                        return self._convert_direct(func_name, params, font_size)
                    elif conversion_mode == 2:
                        return self._convert_to_printf(func_name, params, font_size)

        return line

    def _parse_params(self, params_str: str) -> List[str]:
        """Parse function parameters, handling strings with commas"""
        params = []
        in_string = False
        current_param = ""

        for char in params_str:
            if char == '"' or char == "'":
                in_string = not in_string
                current_param += char
            elif char == ',' and not in_string:
                params.append(current_param.strip())
                current_param = ""
            else:
                current_param += char

        if current_param:
            params.append(current_param.strip())

        return params

    def _convert_coords(self, line: str, column: str) -> Tuple[int, int]:
        """Convert (Line, Column) to (X, Y)"""
        try:
            line_num = int(line)
            col_num = int(column)
            x = (col_num - 1) * 8
            y = (line_num - 1) * 16
            return x, y
        except ValueError:
            # If not numbers, keep as variables
            x = f"({column} - 1) * 8"
            y = f"({line} - 1) * 16"
            return x, y

    def _convert_direct(self, func_name: str, params: List[str], font_size: str) -> str:
        """Mode 1: Direct function conversion with new parameters"""
        mapping = self.direct_conversion[func_name]

        # Extract coordinates
        line_param = params[0]
        col_param = params[1]
        x, y = self._convert_coords(line_param, col_param)

        # Build new parameter list
        new_params = []

        # Add X, Y coordinates
        new_params.append(str(x))
        new_params.append(str(y))

        # Add remaining parameters (skip Line and Column)
        for i in range(2, len(params)):
            new_params.append(params[i])

        # Add FontSize
        new_params.append(font_size)

        return f"{mapping['new_name']}({', '.join(new_params)});"

    def _convert_to_printf(self, func_name: str, params: List[str], font_size: str) -> str:
        """Mode 2: Convert all functions to OLED_Printf"""
        line_param = params[0]
        col_param = params[1]
        x, y = self._convert_coords(line_param, col_param)

        if func_name == "OLED_ShowChar":
            # OLED_ShowChar -> OLED_Printf with %c
            char_param = params[2]
            return f'OLED_Printf({x}, {y}, {font_size}, "%c", {char_param});'

        elif func_name == "OLED_ShowString":
            # OLED_ShowString -> OLED_Printf
            string_param = params[2]
            return f'OLED_Printf({x}, {y}, {font_size}, {string_param});'

        elif func_name == "OLED_ShowNum":
            # OLED_ShowNum -> OLED_Printf with %d
            number_param = params[2]
            length_param = params[3]
            return f'OLED_Printf({x}, {y}, {font_size}, "%{length_param}d", {number_param});'

        elif func_name == "OLED_ShowSignedNum":
            # OLED_ShowSignedNum -> OLED_Printf with %+d
            number_param = params[2]
            length_param = params[3]
            return f'OLED_Printf({x}, {y}, {font_size}, "%+{length_param}d", {number_param});'

        elif func_name == "OLED_ShowHexNum":
            # OLED_ShowHexNum -> OLED_Printf with %X
            number_param = params[2]
            length_param = params[3]
            return f'OLED_Printf({x}, {y}, {font_size}, "%{length_param}X", {number_param});'

        elif func_name == "OLED_ShowBinNum":
            # OLED_ShowBinNum needs special handling
            number_param = params[2]
            length_param = params[3]
            return f'// Note: Binary display requires custom formatting\n// OLED_Printf({x}, {y}, {font_size}, "%{length_param}s", binary_string);'

        return ""

    def convert_code(self, code: str, conversion_mode: int, font_size: str,
                     add_clear: bool = False, add_update: bool = True) -> str:
        """Convert entire code block"""
        lines = code.split('\n')
        result_lines = []
        converted_count = 0

        # Add OLED_Clear if requested
        if add_clear:
            result_lines.append("OLED_Clear();")

        # Convert each line
        for line in lines:
            converted_line = self.convert_line(line, conversion_mode, font_size)
            result_lines.append(converted_line)

            # Count conversions
            if "OLED_Printf" in converted_line or any(func in converted_line for func in self.direct_conversion.keys()):
                converted_count += 1

        # Add OLED_Update at the end if requested and any conversions were made
        if add_update and converted_count > 0:
            result_lines.append("")
            result_lines.append("OLED_Update();")

        return '\n'.join(result_lines)


class OLEDConverterGUI:
    """GUI for OLED function converter"""

    def __init__(self):
        self.converter = OLEDConverter()

        # Create main window
        self.root = tk.Tk()
        self.root.title("OLED Function Converter v2.0")
        self.root.geometry("900x700")

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_frame = tk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(title_frame, text="OLED Function Converter",
                font=("Arial", 16, "bold")).pack(pady=5)
        tk.Label(title_frame, text="Convert old OLED functions to new format",
                font=("Arial", 10)).pack()

        # Control panel
        control_frame = tk.LabelFrame(self.root, text="Conversion Settings", padx=10, pady=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Conversion mode selection
        mode_frame = tk.Frame(control_frame)
        mode_frame.pack(fill=tk.X, pady=5)

        tk.Label(mode_frame, text="Conversion Mode:", width=15).pack(side=tk.LEFT)

        self.mode_var = tk.IntVar(value=1)
        tk.Radiobutton(mode_frame, text="Mode 1: Direct function conversion",
                      variable=self.mode_var, value=1).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="Mode 2: Convert all to OLED_Printf",
                      variable=self.mode_var, value=2).pack(side=tk.LEFT, padx=10)

        # Font size selection
        font_frame = tk.Frame(control_frame)
        font_frame.pack(fill=tk.X, pady=5)

        tk.Label(font_frame, text="Font Size:", width=15).pack(side=tk.LEFT)

        self.font_var = tk.StringVar(value="OLED_8X16")
        tk.Radiobutton(font_frame, text="OLED_8X16",
                      variable=self.font_var, value="OLED_8X16").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(font_frame, text="OLED_6X8",
                      variable=self.font_var, value="OLED_6X8").pack(side=tk.LEFT, padx=10)

        # Options
        options_frame = tk.Frame(control_frame)
        options_frame.pack(fill=tk.X, pady=5)

        self.clear_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Add OLED_Clear() at beginning",
                      variable=self.clear_var).pack(side=tk.LEFT, padx=10)

        self.update_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Add OLED_Update() at end",
                      variable=self.update_var).pack(side=tk.LEFT, padx=10)

        # Main content area
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Input area
        input_frame = tk.LabelFrame(content_frame, text="Input Code")
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        input_button_frame = tk.Frame(input_frame)
        input_button_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(input_button_frame, text="Load Example",
                 command=self.load_example).pack(side=tk.LEFT, padx=2)
        tk.Button(input_button_frame, text="Load File",
                 command=self.load_file).pack(side=tk.LEFT, padx=2)
        tk.Button(input_button_frame, text="Clear",
                 command=self.clear_input).pack(side=tk.LEFT, padx=2)

        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD,
                                                   font=("Consolas", 10))
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Output area
        output_frame = tk.LabelFrame(content_frame, text="Output Code")
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        output_button_frame = tk.Frame(output_frame)
        output_button_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(output_button_frame, text="Convert",
                 command=self.convert_code, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(output_button_frame, text="Copy Result",
                 command=self.copy_result).pack(side=tk.LEFT, padx=2)
        tk.Button(output_button_frame, text="Save Result",
                 command=self.save_result).pack(side=tk.LEFT, padx=2)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD,
                                                    font=("Consolas", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Load example
        self.load_example()

    def load_example(self):
        """Load example code"""
        example_code = """// Example code showing various OLED functions
OLED_ShowChar(1, 1, 'A');
OLED_ShowString(1, 1, "Temperature: ");
OLED_ShowNum(2, 1, 1234, 4);
OLED_ShowSignedNum(3, 1, -567, 3);
OLED_ShowHexNum(4, 1, 0xABCD, 4);
OLED_ShowBinNum(4, 10, 0b1101, 4);"""

        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, example_code)
        self.status_bar.config(text="Example code loaded")

    def load_file(self):
        """Load code from file"""
        file_path = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[("C files", "*.c"), ("Header files", "*.h"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()

                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(1.0, code)
                self.status_bar.config(text=f"Loaded: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def clear_input(self):
        """Clear input text"""
        self.input_text.delete(1.0, tk.END)
        self.status_bar.config(text="Input cleared")

    def convert_code(self):
        """Convert the code"""
        code = self.input_text.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "Please enter code to convert")
            return

        try:
            conversion_mode = self.mode_var.get()
            font_size = self.font_var.get()
            add_clear = self.clear_var.get()
            add_update = self.update_var.get()

            result = self.converter.convert_code(code, conversion_mode, font_size, add_clear, add_update)

            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, result)

            # Count conversions
            lines = result.split('\n')
            conversions = sum(1 for line in lines if "OLED_Printf" in line or
                             any(func in line for func in self.converter.direct_conversion.keys()))

            mode_text = "Direct function conversion" if conversion_mode == 1 else "OLED_Printf conversion"
            self.status_bar.config(text=f"Converted {conversions} functions using {mode_text}")

        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")

    def copy_result(self):
        """Copy result to clipboard"""
        result = self.output_text.get(1.0, tk.END).strip()
        if result:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            self.status_bar.config(text="Result copied to clipboard")
        else:
            messagebox.showwarning("Warning", "No result to copy")

    def save_result(self):
        """Save result to file"""
        result = self.output_text.get(1.0, tk.END).strip()
        if not result:
            messagebox.showwarning("Warning", "No result to save")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save output file",
            defaultextension=".c",
            filetypes=[("C files", "*.c"), ("Header files", "*.h"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                self.status_bar.config(text=f"Saved to: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = OLEDConverterGUI()
    app.run()

if __name__ == "__main__":
    main()
