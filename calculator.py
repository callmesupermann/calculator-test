import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class Calculator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Calculator")
        self.window.geometry("400x600")
        
        # History list to store calculations
        self.history = []
        self.convert_mode = False
        self.timer = None
        
        # Style configuration
        style = ttk.Style()
        style.configure('Calculator.TButton', font=('Times New Roman', 12, 'bold'))
        style.configure('Operator.TButton', font=('Times New Roman', 14, 'bold'))
        
        # Text widget for multi-line display
        self.display = tk.Text(self.window, height=3, font=("Times New Roman", 20, "bold"), 
                             wrap=tk.WORD, relief="sunken", bd=2)
        self.display.tag_configure('right', justify='right')
        self.display.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        
        # Calculator buttons with their display and evaluation values
        self.buttons_normal = [
            ('⌫', '⌫'), ('CLR', 'CLR'), ('H', 'H'), ('÷', '/'),
            ('7', '7'), ('8', '8'), ('9', '9'), ('×', '*'),
            ('4', '4'), ('5', '5'), ('6', '6'), ('−', '-'),
            ('1', '1'), ('2', '2'), ('3', '3'), ('+', '+'),
            ('0', '0'), ('.', '.'), ('=', '='), ('Convert', 'convert')
        ]
        
        self.buttons_convert = [
            ('BIN', 'bin'), ('FRACTION', 'fraction'), ('H', 'H'), ('÷', '/'),
            ('7', '7'), ('8', '8'), ('9', '9'), ('×', '*'),
            ('4', '4'), ('5', '5'), ('6', '6'), ('−', '-'),
            ('1', '1'), ('2', '2'), ('3', '3'), ('+', '+'),
            ('0', '0'), ('.', '.'), ('=', '='), ('Convert', 'convert')
        ]
        
        # Create and store button widgets
        self.button_widgets = {}
        self.create_buttons(self.buttons_normal)
                
        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=2)
        for i in range(1, 6):
            self.window.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.window.grid_columnconfigure(i, weight=1)
            
        self.equation = ""
        self.result = ""
        self.last_result = None

    def create_buttons(self, button_config):
        row = 1
        col = 0
        for button_text, button_value in button_config:
            cmd = lambda x=button_value: self.click(x)
            # Use different style for operators
            if button_text in ['÷', '×', '−', '+']:
                btn = ttk.Button(self.window, text=button_text, command=cmd, style='Operator.TButton')
            else:
                btn = ttk.Button(self.window, text=button_text, command=cmd, style='Calculator.TButton')
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
        row = 1
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
        """Convert a number to binary representation"""
        try:
            # Handle negative numbers
            is_negative = number < 0
            number = abs(number)
            
            # Check if number is too large
            if number > 2**32:
                return "NUMBER TOO LARGE FOR BINARY"
            
            # Convert to integer if it's a whole number
            if float(number).is_integer():
                binary = bin(int(number))[2:]  # Remove '0b' prefix
                return f"-{binary}" if is_negative else binary
            else:
                return "DECIMALS NOT SUPPORTED"
        except:
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

    def to_fraction(self, number):
        """Convert a number to fraction representation"""
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
                return f"{int(number)}/1"
            
            # Convert decimal to fraction using string manipulation for exact conversion
            str_num = str(abs(number))
            if '.' in str_num:
                integer_part = str_num.split('.')[0]
                decimal_part = str_num.split('.')[1]
                
                # Remove trailing zeros from decimal part
                decimal_part = decimal_part.rstrip('0')
                
                # Convert to fraction
                numerator = int(integer_part + decimal_part)
                denominator = 10 ** len(decimal_part)
                
                # Simplify the fraction
                num, den = self.simplify_fraction(numerator, denominator)
                
                # Apply original sign
                if number < 0:
                    num = -num
                
                # Check if denominator is too large
                if den > 1000000:
                    return "FRACTION TOO COMPLEX"
                
                # If result is a whole number after simplification
                if den == 1:
                    return str(num)
                    
                return f"{num}/{den}"
            
            return str(number)
        except:
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
                    if self.equation[-1] in ['*', '/', '+', '-']:
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
            except Exception:
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
            self.equation += value
            self.result = ""
            self.update_display()
    
    def show_history(self):
        history_text = "Calculation History:\n\n"
        if not self.history:
            history_text += "No calculations yet"
        else:
            for item in self.history[-10:]:  # Show last 10 calculations
                history_text += item + "\n"
        messagebox.showinfo("History", history_text)
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    calc = Calculator()
    calc.run() 