#!/usr/bin/env python3
"""
QR Code Label Generator for Zebra ZT510 Printer - Simple Version
No PIL/Pillow dependencies - uses web API for QR generation
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import socket
import threading
import os
from datetime import datetime
from io import BytesIO

class QRPrinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Label Generator for Zebra ZT510 - Simple")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.prefix_var = tk.StringVar(value="ITEM")
        self.start_number_var = tk.StringVar(value="1")
        self.quantity_var = tk.StringVar(value="1")
        self.description_var = tk.StringVar(value="")
        self.printer_path_var = tk.StringVar(value="\\\\printserver\\printer")
        
        self.generated_labels = []
        self.current_qr_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="QR Code Label Generator - Simple Version", 
                              font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel - Form
        form_frame = ttk.LabelFrame(main_frame, text="Label Configuration", padding="15")
        form_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Prefix
        ttk.Label(form_frame, text="Prefix:").grid(row=0, column=0, sticky=tk.W, pady=5)
        prefix_entry = ttk.Entry(form_frame, textvariable=self.prefix_var, width=20)
        prefix_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Starting Number
        ttk.Label(form_frame, text="Starting Number:").grid(row=1, column=0, sticky=tk.W, pady=5)
        start_entry = ttk.Entry(form_frame, textvariable=self.start_number_var, width=20)
        start_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Quantity
        ttk.Label(form_frame, text="Number of Labels:").grid(row=2, column=0, sticky=tk.W, pady=5)
        quantity_entry = ttk.Entry(form_frame, textvariable=self.quantity_var, width=20)
        quantity_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky=tk.W, pady=5)
        desc_entry = ttk.Entry(form_frame, textvariable=self.description_var, width=20)
        desc_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Printer Path
        ttk.Label(form_frame, text="Printer Path:").grid(row=4, column=0, sticky=tk.W, pady=5)
        printer_entry = ttk.Entry(form_frame, textvariable=self.printer_path_var, width=20)
        printer_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Generate QR Code", 
                  command=self.generate_qr).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Print Labels", 
                  command=self.print_labels).pack(side=tk.LEFT, padx=5)
        
        # Test buttons
        test_frame = ttk.LabelFrame(form_frame, text="Test QR Codes", padding="10")
        test_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(test_frame, text="TEST123", 
                  command=lambda: self.generate_test_qr("TEST123")).pack(side=tk.LEFT, padx=2)
        ttk.Button(test_frame, text="ITEM-1", 
                  command=lambda: self.generate_test_qr("ITEM-1")).pack(side=tk.LEFT, padx=2)
        ttk.Button(test_frame, text="A-1", 
                  command=lambda: self.generate_test_qr("A-1")).pack(side=tk.LEFT, padx=2)
        
        # Right panel - Preview
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="15")
        preview_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # QR Code display
        self.qr_label = ttk.Label(preview_frame, text="Click 'Generate QR Code' to see preview")
        self.qr_label.pack(pady=20)
        
        # Label info
        self.info_label = ttk.Label(preview_frame, text="Label Size: 4\" x 8\" (Landscape)\nCurrent QR Data: None")
        self.info_label.pack(pady=10)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # ZPL Output
        zpl_frame = ttk.LabelFrame(main_frame, text="ZPL Code", padding="10")
        zpl_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.zpl_text = scrolledtext.ScrolledText(zpl_frame, height=8, width=70)
        self.zpl_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
    def generate_qr(self):
        try:
            prefix = self.prefix_var.get().strip()
            start_number = int(self.start_number_var.get())
            quantity = int(self.quantity_var.get())
            description = self.description_var.get().strip()
            
            if not prefix:
                messagebox.showerror("Error", "Please enter a prefix")
                return
                
            if start_number < 0:
                messagebox.showerror("Error", "Starting number must be 0 or greater")
                return
                
            if quantity < 1 or quantity > 100:
                messagebox.showerror("Error", "Quantity must be between 1 and 100")
                return
            
            # Generate label data
            self.generated_labels = []
            for i in range(quantity):
                number = start_number + i
                qr_data = f"{prefix}-{number}"
                self.generated_labels.append({
                    'qr_data': qr_data,
                    'description': description,
                    'number': number
                })
            
            # Generate QR code for preview (first label)
            first_qr_data = self.generated_labels[0]['qr_data']
            self.current_qr_image = self.create_qr_code_web(first_qr_data)
            
            # Update preview
            self.qr_label.configure(image=self.current_qr_image, text="")
            self.info_label.configure(text=f"Label Size: 4\" x 8\" (Landscape)\nCurrent QR Data: {first_qr_data}")
            
            self.status_label.configure(text=f"Generated {quantity} label(s) successfully!", foreground="green")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating QR code: {str(e)}")
    
    def generate_test_qr(self, test_text):
        try:
            self.current_qr_image = self.create_qr_code_web(test_text)
            self.qr_label.configure(image=self.current_qr_image, text="")
            self.info_label.configure(text=f"Label Size: 4\" x 8\" (Landscape)\nTest QR Data: {test_text}")
            self.status_label.configure(text=f"Test QR code generated for '{test_text}'!", foreground="blue")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating test QR: {str(e)}")
    
    def create_qr_code_web(self, text):
        """Create QR code using web API"""
        try:
            # Use QR Server API
            url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={text}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Convert to PhotoImage
            from PIL import Image, ImageTk
            img = Image.open(BytesIO(response.content))
            return ImageTk.PhotoImage(img)
            
        except ImportError:
            # Fallback: show text instead of image
            return None
        except Exception as e:
            print(f"QR generation error: {e}")
            return None
    
    def generate_zpl_code(self):
        """Generate ZPL code for all labels - Landscape orientation, centered"""
        zpl_code = ""
        
        for i, label in enumerate(self.generated_labels):
            # ZPL for 4" x 8" label in landscape orientation
            # Use ^A0R for rotated text and adjust coordinates for landscape
            
            # Landscape positioning (8" wide x 4" tall)
            # QR Code positioning - centered for landscape
            qr_x = 400  # Center horizontally for landscape (8" = 1624 dots, so ~800 center)
            qr_y = 100  # Top margin
            
            # Text positioning - below QR code
            text_x = 400  # Center horizontally (same as QR)
            text_y = 400  # Below QR code
            
            # Description positioning - bottom of label
            desc_x = 400  # Center horizontally
            desc_y = 500  # Below text
            
            zpl_code += f"""^XA
^FO400,500^BY3
^BQN,2,10
^FD MM,{label['qr_data']}^FS
^FO300,520^A0R,50,50^FD{label['qr_data']}^FS"""
            
            if label['description']:
                zpl_code += f"^FO200,520^A0R,50,50^FD{label['description']}^FS"
            
            zpl_code += "^XZ"
            
            if i < len(self.generated_labels) - 1:
                zpl_code += "\n"
        
        return zpl_code
    
    def print_labels(self):
        if not self.generated_labels:
            messagebox.showerror("Error", "Please generate QR codes first")
            return
        
        printer_path = self.printer_path_var.get().strip()
        if not printer_path:
            messagebox.showerror("Error", "Please enter a printer path")
            return
        
        # Generate ZPL code
        zpl_code = self.generate_zpl_code()
        
        # Show ZPL in text area
        self.zpl_text.delete(1.0, tk.END)
        self.zpl_text.insert(1.0, zpl_code)
        
        # Ask user if they want to print
        result = messagebox.askyesno("Print Labels", 
                                   f"Generated ZPL code for {len(self.generated_labels)} labels.\n\n"
                                   f"Do you want to print directly to:\n{printer_path}")
        
        if result:
            self.print_to_printer(zpl_code, printer_path)
    
    def print_to_printer(self, zpl_code, printer_path):
        """Print ZPL code directly to network printer"""
        def print_thread():
            try:
                self.root.after(0, lambda: self.status_label.configure(text="Printing...", foreground="orange"))
                self.root.after(0, lambda: self.progress.configure(value=0))
                
                # Method 1: Try direct network printing
                if self.try_network_print(zpl_code, printer_path):
                    self.root.after(0, lambda: self.status_label.configure(
                        text=f"Successfully printed {len(self.generated_labels)} labels!", 
                        foreground="green"))
                    self.root.after(0, lambda: self.progress.configure(value=100))
                    return
                
                # Method 2: Try Windows copy command
                if self.try_copy_command(zpl_code, printer_path):
                    self.root.after(0, lambda: self.status_label.configure(
                        text=f"Successfully printed {len(self.generated_labels)} labels!", 
                        foreground="green"))
                    self.root.after(0, lambda: self.progress.configure(value=100))
                    return
                
                # Method 3: Save file and show manual command
                filename = self.save_zpl_file(zpl_code)
                self.root.after(0, lambda: self.status_label.configure(
                    text=f"Saved {filename}. Run: copy \"{filename}\" \"{printer_path}\"", 
                    foreground="blue"))
                self.root.after(0, lambda: self.progress.configure(value=100))
                
            except Exception as e:
                self.root.after(0, lambda: self.status_label.configure(
                    text=f"Print error: {str(e)}", foreground="red"))
                self.root.after(0, lambda: self.progress.configure(value=0))
        
        # Start printing in separate thread
        threading.Thread(target=print_thread, daemon=True).start()
    
    def try_network_print(self, zpl_code, printer_path):
        """Try to print directly via network socket"""
        try:
            # Extract IP/hostname from UNC path
            if printer_path.startswith("\\\\"):
                hostname = printer_path[2:].split("\\")[0]
            else:
                hostname = printer_path
            
            # Try to connect to printer on port 9100 (standard ZPL port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((hostname, 9100))
            sock.send(zpl_code.encode('utf-8'))
            sock.close()
            return True
        except:
            return False
    
    def try_copy_command(self, zpl_code, printer_path):
        """Try to use Windows copy command"""
        try:
            filename = self.save_zpl_file(zpl_code)
            import subprocess
            result = subprocess.run(['cmd', '/c', 'copy', filename, printer_path], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def save_zpl_file(self, zpl_code):
        """Save ZPL code to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qr_labels_{timestamp}.zpl"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(zpl_code)
        
        return filename

def main():
    root = tk.Tk()
    app = QRPrinterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
