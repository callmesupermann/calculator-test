import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class Calculator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Calculator")
        self.window.geometry("400x600")
        
        # Theme state
        self.is_dark_mode = False
        
        # History popup
        self.history_popup = None
        
        # Define themes
        self.light_theme = {
            'bg': '#ffffff',
            'display_bg': '#f0f0f0',
            'display_fg': '#000000',
            'button_bg': '#e1e1e1',
            'button_fg': '#000000',
            'operator_bg': '#f0f0f0',
            'operator_fg': '#000000'
        }
        
        self.dark_theme = {
            'bg': '#2d2d2d',
            'display_bg': '#1e1e1e',
            'display_fg': '#ffffff',
            'button_bg': '#404040',
            'button_fg': '#ffffff',
            'operator_bg': '#333333',
            'operator_fg': '#ffffff'
        }
        
        # Create a frame for the theme toggle
        self.toggle_frame = tk.Frame(self.window)
        self.toggle_frame.grid(row=0, column=0, columnspan=4, sticky="ne", padx=5, pady=2)
        
        # Theme toggle button
        self.theme_button = tk.Button(self.toggle_frame, text="☀", width=3,  # Start with sun symbol for light mode
                                    command=self.toggle_theme, relief="raised",
                                    font=('Times New Roman', 12, 'bold'))
        self.theme_button.pack(side="right")
        
        # History list to store calculations
        self.history = []
        self.convert_mode = False
        self.timer = None
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('Calculator.TButton', font=('Times New Roman', 12, 'bold'), width=6)
        self.style.configure('Operator.TButton', font=('Times New Roman', 14, 'bold'), width=6)
        
        # Text widget for multi-line display
        self.display = tk.Text(self.window, height=3, font=("Times New Roman", 20, "bold"), 
                             wrap=tk.WORD, relief="sunken", bd=2)
        self.display.tag_configure('right', justify='right')
        self.display.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        
        # Calculator buttons with their display and evaluation values
        self.buttons_normal = [
            ('÷', '/'), ('H', 'H'), ('CLR', 'CLR'), ('⌫', '⌫'),
            ('×', '*'), ('7', '7'), ('8', '8'), ('9', '9'),
            ('−', '-'), ('4', '4'), ('5', '5'), ('6', '6'),
            ('+', '+'), ('1', '1'), ('2', '2'), ('3', '3'),
            ('Convert', 'convert'), ('0', '0'), ('.', '.'), ('=', '=')
        ]
        
        self.buttons_convert = [
            ('÷', '/'), ('H', 'H'), ('FRACTION', 'fraction'), ('BIN', 'bin'),
            ('×', '*'), ('7', '7'), ('8', '8'), ('9', '9'),
            ('−', '-'), ('4', '4'), ('5', '5'), ('6', '6'),
            ('+', '+'), ('1', '1'), ('2', '2'), ('3', '3'),
            ('Convert', 'convert'), ('0', '0'), ('.', '.'), ('=', '=')
        ]
        
        # Create and store button widgets
        self.button_widgets = {}
        self.create_buttons(self.buttons_normal)
                
        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=1)  # Toggle frame row
        self.window.grid_rowconfigure(1, weight=2)  # Display row
        for i in range(2, 7):  # Button rows
            self.window.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.window.grid_columnconfigure(i, weight=1)
            
        self.equation = ""
        self.result = ""
        self.last_result = None

        # Bind keyboard events
        self.window.bind('<Key>', self.handle_keypress)
        self.window.bind('<Return>', lambda e: self.click('='))
        self.window.bind('<BackSpace>', lambda e: self.click('⌫'))
        self.window.bind('<Delete>', lambda e: self.click('CLR'))
        self.window.bind('<Escape>', lambda e: self.window.quit())
        
        # Apply initial theme
        self.apply_theme(self.light_theme)

    def create_history_popup(self):
        """Create a custom history popup window"""
        # If popup exists, destroy it
        if self.history_popup and self.history_popup.winfo_exists():
            self.history_popup.destroy()
            self.history_popup = None
            return

        # Get H button position
        h_button = None
        for key, button in self.button_widgets.items():
            if button['text'] == 'H':
                h_button = button
                break

        if not h_button:
            return

        # Create popup
        self.history_popup = tk.Toplevel(self.window)
        self.history_popup.overrideredirect(True)  # Remove window decorations
        
        # Calculate position relative to H button
        x = h_button.winfo_rootx() + h_button.winfo_width()
        y = h_button.winfo_rooty()
        
        # Create frame with border
        frame = tk.Frame(self.history_popup, borderwidth=2, relief="solid")
        frame.pack(expand=True, fill="both")
        
        # Title
        title = tk.Label(frame, text="History", font=("Times New Roman", 12, "bold"),
                        padx=5, pady=5)
        title.pack(fill="x")
        
        # History text
        history_text = tk.Text(frame, width=30, height=10, font=("Times New Roman", 10),
                             wrap=tk.WORD)
        history_text.pack(padx=5, pady=5)
        
        # Add close button
        close_btn = tk.Button(frame, text="×", command=self.history_popup.destroy,
                            font=("Times New Roman", 12, "bold"))
        close_btn.place(relx=1.0, rely=0.0, anchor="ne")
        
        # Add history content
        if not self.history:
            history_text.insert("1.0", "No calculations yet")
        else:
            for item in self.history[-10:]:  # Show last 10 calculations
                history_text.insert("end", item + "\n")
        history_text.configure(state="disabled")  # Make read-only
        
        # Apply current theme
        current_theme = self.dark_theme if self.is_dark_mode else self.light_theme
        frame.configure(bg=current_theme['bg'])
        title.configure(bg=current_theme['bg'], fg=current_theme['button_fg'])
        history_text.configure(bg=current_theme['display_bg'], fg=current_theme['display_fg'])
        close_btn.configure(bg=current_theme['button_bg'], fg=current_theme['button_fg'])
        
        # Position the popup
        self.history_popup.geometry(f"+{x}+{y}")
        
        # Add bindings to close popup when clicking outside
        def on_focus_out(event):
            if self.history_popup and self.history_popup.winfo_exists():
                self.history_popup.destroy()
                self.history_popup = None
        
        self.history_popup.bind('<FocusOut>', on_focus_out)
        
        # Make sure popup stays on top
        self.history_popup.lift()
        self.history_popup.focus_force()

    def show_history(self):
        """Show history in custom popup"""
        self.create_history_popup()

    def apply_theme(self, theme):
        """Apply the selected theme to all widgets"""
        self.window.configure(bg=theme['bg'])
        self.toggle_frame.configure(bg=theme['bg'])
        self.display.configure(bg=theme['display_bg'], fg=theme['display_fg'])
        self.theme_button.configure(bg=theme['button_bg'], fg=theme['button_fg'])
        
        # Update all buttons
        for key, button in self.button_widgets.items():
            if any(op[0] in ['÷', '×', '−', '+'] for op in [self.buttons_normal[int(key.split(',')[0])-2][0]]):
                button.configure(bg=theme['operator_bg'], fg=theme['operator_fg'],
                              activebackground=theme['operator_bg'],
                              activeforeground=theme['operator_fg'])
            else:
                button.configure(bg=theme['button_bg'], fg=theme['button_fg'],
                              activebackground=theme['button_bg'],
                              activeforeground=theme['button_fg'])
        
        # Update history popup if it exists
        if self.history_popup and self.history_popup.winfo_exists():
            for widget in self.history_popup.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.configure(bg=theme['bg'])
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.configure(bg=theme['bg'], fg=theme['button_fg'])
                        elif isinstance(child, tk.Text):
                            child.configure(bg=theme['display_bg'], fg=theme['display_fg'])
                        elif isinstance(child, tk.Button):
                            child.configure(bg=theme['button_bg'], fg=theme['button_fg'])

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.apply_theme(self.dark_theme)
            self.theme_button.configure(text="☾")  # Moon symbol for dark mode
        else:
            self.apply_theme(self.light_theme)
            self.theme_button.configure(text="☀")  # Sun symbol for light mode

    def create_buttons(self, button_config):
        row = 2
        col = 0
        for button_text, button_value in button_config:
            cmd = lambda x=button_value: self.click(x)
            # Use different style for operators
            if button_text in ['÷', '×', '−', '+']:
                btn = tk.Button(self.window, text=button_text, command=cmd,
                              font=('Times New Roman', 14, 'bold'),
                              width=6, relief="raised")
            else:
                btn = tk.Button(self.window, text=button_text, command=cmd,
                              font=('Times New Roman', 12, 'bold'),
                              width=6, relief="raised")
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew", ipady=10, ipadx=10)
            # Store button widget reference
            key = f"{row},{col}"
            self.button_widgets[key] = btn
            col += 1
            if col > 3:
                col = 0
                row += 1

    def switch_buttons(self, to_convert_mode):
        if to_convert_mode:
            buttons = self.buttons_convert
        else:
            buttons = self.buttons_normal
            
        # Update button text and commands
        row = 2
        col = 0
        for button_text, button_value in buttons:
            key = f"{row},{col}"
            if key in self.button_widgets:
                cmd = lambda x=button_value: self.click(x)
                self.button_widgets[key].configure(text=button_text, command=cmd)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def start_convert_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(5.0, self.switch_to_normal)
        self.timer.start()

    def switch_to_normal(self):
        if self.convert_mode:
            self.convert_mode = False
            self.window.after(0, lambda: self.switch_buttons(False))

    def update_display(self):
        self.display.delete(1.0, tk.END)
        # Display equation at top-left
        if self.equation:
            display_text = self.equation.replace('*', '×').replace('/', '÷').replace('-', '−')
            if self.result:
                display_text += " ="
            self.display.insert(tk.END, display_text + '\n')
        # Display result at bottom-right if exists
        if self.result:
            self.display.insert(tk.END, '\n')
            self.display.insert(tk.END, self.result, 'right')

    def to_binary(self, number):
        """Convert a number to binary representation including fractional parts"""
        try:
            # Handle negative numbers
            is_negative = number < 0
            number = abs(number)
            
            # Check if number is too large
            if number > 2**32:
                return "NUMBER TOO LARGE FOR BINARY"
            
            # Split into integer and fractional parts
            int_part = int(number)
            frac_part = number - int_part
            
            # Convert integer part
            if int_part == 0:
                int_binary = "0"
            else:
                int_binary = ""
                while int_part > 0:
                    int_binary = str(int_part % 2) + int_binary
                    int_part //= 2
            
            # Convert fractional part (up to 8 decimal places to avoid infinite loops)
            if frac_part == 0:
                frac_binary = ""
            else:
                frac_binary = "."
                max_digits = 8  # Limit decimal places
                while frac_part > 0 and len(frac_binary) <= max_digits:
                    frac_part *= 2
                    bit = int(frac_part)
                    frac_binary += str(bit)
                    frac_part -= bit
            
            # Combine results
            result = int_binary + frac_binary
            
            # Add negative sign if needed
            if is_negative:
                result = "-" + result
                
            return result
            
        except Exception as e:
            print(f"Binary conversion error: {e}")  # For debugging
            return "CANNOT CONVERT TO BINARY"

    def simplify_fraction(self, numerator, denominator):
        """Simplify a fraction by finding the GCD"""
        def gcd(a, b):
            a, b = abs(a), abs(b)  # Work with absolute values
            while b:
                a, b = b, a % b
            return a
        
        # Special case for zero numerator
        if numerator == 0:
            return 0, 1
            
        # Get GCD and simplify
        divisor = gcd(numerator, denominator)
        num = numerator // divisor
        den = denominator // divisor
        
        # If denominator is negative, move the negative sign to numerator
        if den < 0:
            num = -num
            den = -den
            
        return num, den

    def detect_repetition(self, decimal_str):
        """Detect repeating pattern in decimal string"""
        if len(decimal_str) < 2:
            return None
            
        # Look for patterns up to half the string length
        max_pattern_length = len(decimal_str) // 2
        for pattern_length in range(1, max_pattern_length + 1):
            pattern = decimal_str[:pattern_length]
            # Check if this pattern repeats at least twice
            if pattern * 2 == decimal_str[:pattern_length * 2]:
                # Verify pattern continues throughout string
                if all(decimal_str[i:i+pattern_length] == pattern 
                      for i in range(0, len(decimal_str) - pattern_length, pattern_length)):
                    return pattern
        return None

    def to_fraction(self, number):
        """Convert a number to fraction representation, handling both terminating and repeating decimals"""
        try:
            number = float(number)
            
            # Handle special cases
            if number == 0:
                return "0/1"
            
            # Check if number is too large
            if abs(number) > 1e10:
                return "NUMBER TOO LARGE"
            
            # If it's a whole number, return number/1
            if number.is_integer():
                return str(int(number))
            
            # Get the sign and work with absolute value
            is_negative = number < 0
            number = abs(number)
            
            # Split into integer and decimal parts
            int_part = int(number)
            decimal_part = str(number).split('.')[1]
            
            # Remove trailing zeros
            decimal_part = decimal_part.rstrip('0')
            
            if not decimal_part:  # If all zeros after decimal
                return str(int_part if not is_negative else -int_part)
            
            # Check for repeating pattern
            pattern = self.detect_repetition(decimal_part)
            
            if pattern:
                # Handle repeating decimal using algebraic method
                pattern_len = len(pattern)
                non_repeating = decimal_part[:decimal_part.index(pattern)]
                
                # Calculate numerator and denominator
                power = 10 ** len(non_repeating)
                factor = 10 ** pattern_len - 1
                
                # Convert repeating part to integer
                repeating = int(pattern)
                
                # Calculate the fraction
                numerator = int(non_repeating + pattern) - (int(non_repeating) if non_repeating else 0)
                denominator = factor * power
                
            else:
                # Handle terminating decimal
                decimal_length = len(decimal_part)
                numerator = int(str(int_part) + decimal_part)
                denominator = 10 ** decimal_length
            
            # Add the whole number part if exists
            if int_part > 0:
                numerator += int_part * denominator
            
            # Simplify the fraction
            num, den = self.simplify_fraction(numerator, denominator)
            
            # Apply original sign
            if is_negative:
                num = -num
            
            # Check if denominator is too large
            if den > 1000000:
                return "FRACTION TOO COMPLEX"
            
            # If result is a whole number after simplification
            if den == 1:
                return str(num)
                
            return f"{num}/{den}"
            
        except Exception as e:
            print(f"Fraction conversion error: {e}")  # For debugging
            return "CANNOT CONVERT TO FRACTION"

    def format_number(self, number):
        """Format number to show 3 decimal places if decimal, whole number if integer"""
        try:
            # Convert to float for checking decimal places
            num = float(number)
            # Check if it's effectively a whole number
            if num.is_integer():
                return str(int(num))
            else:
                # Round to 3 decimal places and remove trailing zeros
                rounded = round(num, 3)
                # Convert to string and remove trailing zeros if present
                str_num = f"{rounded:.3f}".rstrip('0').rstrip('.')
                return str_num
        except:
            return str(number)

    def click(self, value):
        if value == '=':
            try:
                # Only check for actual equation content if there is any
                if self.equation:
                    # Check for invalid operators at the end
                    if self.equation[-1] in ['*', '/', '+', '-', '.']:
                        raise ValueError("INCOMPLETE EQUATION")

                    # Check for division by zero
                    if '/0' in self.equation.replace(' ', ''):
                        if self.equation.replace(' ', '').endswith('/0'):
                            raise ZeroDivisionError("DIVISION BY ZERO")
                        # Check if it's like /0.1 which is valid
                        parts = self.equation.split('/')
                        for part in parts[1:]:
                            if part.strip().startswith('0') and not '.' in part:
                                raise ZeroDivisionError("DIVISION BY ZERO")

                    # Check for consecutive operators
                    prev_char = ''
                    for char in self.equation:
                        if char in '*/+-' and prev_char in '*/+-':
                            raise ValueError("INVALID OPERATOR SEQUENCE")
                        prev_char = char

                    # Store the equation with display symbols
                    display_equation = self.equation.replace('*', '×').replace('/', '÷').replace('-', '−')
                    
                    # Evaluate the equation
                    result = eval(self.equation)

                    # Check if result is too large
                    if abs(result) > 1e100:
                        raise OverflowError("NUMBER TOO LARGE")

                    # Check if result is complex or imaginary
                    if isinstance(result, complex):
                        raise ValueError("COMPLEX RESULT")

                    # Store the numerical result for conversions
                    self.last_result = result
                    # Format the result
                    formatted_result = self.format_number(result)
                    # Add to history with display symbols
                    history_entry = f"{display_equation} = {formatted_result}"
                    self.history.append(history_entry)
                    self.result = formatted_result
                    self.update_display()

            except ZeroDivisionError:
                self.display.delete(1.0, tk.END)
                self.display.insert(tk.END, "DIVISION BY ZERO")
                self.equation = ""
                self.result = ""
                self.last_result = None
            except SyntaxError:
                self.display.delete(1.0, tk.END)
                self.display.insert(tk.END, "SYNTAX ERROR")
                self.equation = ""
                self.result = ""
                self.last_result = None
            except OverflowError:
                self.display.delete(1.0, tk.END)
                self.display.insert(tk.END, "NUMBER TOO LARGE")
                self.equation = ""
                self.result = ""
                self.last_result = None
            except ValueError as e:
                self.display.delete(1.0, tk.END)
                self.display.insert(tk.END, str(e))
                self.equation = ""
                self.result = ""
                self.last_result = None
            except Exception as e:
                print(f"Calculation error: {e}")  # For debugging
                self.display.delete(1.0, tk.END)
                self.display.insert(tk.END, "INVALID INPUT")
                self.equation = ""
                self.result = ""
                self.last_result = None
        elif value == 'CLR':
            self.display.delete(1.0, tk.END)
            self.equation = ""
            self.result = ""
            self.last_result = None
        elif value == '⌫':
            self.equation = self.equation[:-1]
            self.result = ""
            self.update_display()
        elif value == 'H':
            self.show_history()
        elif value == 'convert':
            if self.convert_mode:
                self.convert_mode = False
                if self.timer:
                    self.timer.cancel()
                self.switch_buttons(False)
            else:
                self.convert_mode = True
                self.switch_buttons(True)
                self.start_convert_timer()
        elif value == 'bin':
            if self.last_result is not None:
                binary_result = self.to_binary(self.last_result)
                self.result = binary_result
                self.update_display()
        elif value == 'fraction':
            if self.last_result is not None:
                fraction_result = self.to_fraction(self.last_result)
                self.result = fraction_result
                self.update_display()
        else:
            # Prevent multiple decimal points in a number
            if value == '.':
                parts = self.equation.split(' ')
                if parts and '.' in parts[-1]:
                    return
            self.equation += value
            self.result = ""
            self.update_display()
    
    def run(self):
        self.window.mainloop()

    def handle_keypress(self, event):
        """Handle keyboard input"""
        key = event.char
        
        # Number keys and decimal point
        if key in '0123456789':
            self.click(key)
        elif key == '.':
            # Only add decimal if there isn't one already in the current number
            parts = self.equation.split(' ')
            if not parts or '.' not in parts[-1]:
                self.click('.')
            
        # Operator keys
        elif key == '+':
            self.click('+')
        elif key == '-':
            self.click('-')
        elif key == '*':
            self.click('*')
        elif key == '/':
            self.click('/')
            
        # Special keys
        elif key == 'h':  # History
            self.click('H')
        elif key == 'c':  # Convert
            self.click('convert')
        elif key == 'b':  # Binary (when in convert mode)
            if self.convert_mode:
                self.click('bin')
        elif key == 'f':  # Fraction (when in convert mode)
            if self.convert_mode:
                self.click('fraction')
        
        # Prevent the key from being inserted into the display
        return "break"

if __name__ == "__main__":
    calc = Calculator()
    calc.run() 