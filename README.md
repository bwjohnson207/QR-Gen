# QR Code Label Generator for Zebra ZT510

A Python GUI application that generates QR codes and automatically prints labels to your Zebra ZT510 printer.

## Features

- **GUI Interface**: Clean Tkinter interface with form inputs
- **QR Code Generation**: Uses web API for reliable QR code generation
- **Automatic Printing**: Multiple printing methods with automatic fallbacks
- **Label Configuration**: Prefix, starting number, quantity, and description
- **Real-time Preview**: See QR codes before printing
- **ZPL Code Display**: Review generated ZPL code
- **Progress Tracking**: Visual progress bar and status updates

## Quick Start

### Option 1: Run the Batch File (Recommended)
```bash
# Double-click this file:
run.bat
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python qr_printer.py
```

## How to Use

1. **Configure Labels**:
   - Enter prefix (e.g., "ITEM")
   - Set starting number (e.g., 1)
   - Choose quantity (e.g., 5)
   - Add description (optional)

2. **Generate QR Code**:
   - Click "Generate QR Code" to see preview
   - Test with sample buttons if needed

3. **Print Labels**:
   - Click "Print Labels"
   - Review ZPL code if desired
   - Click "Yes" to print automatically

## Printing Methods

The application tries multiple printing methods automatically:

1. **Direct Network Printing**: Connects to printer via socket (port 9100)
2. **Windows Copy Command**: Uses `subprocess` to execute copy command
3. **File Save Fallback**: Saves ZPL file and shows manual command

## Printer Configuration

Default printer path: `\\edg1i-bjohnson\testzeb`

You can change this in the "Printer Path" field to match your network printer.

## Label Specifications

- **Size**: 4" x 8" labels (printed in landscape orientation)
- **Format**: ZPL (Zebra Programming Language)
- **Layout**: Centered QR code and text for optimal appearance
- **QR Code**: High error correction for reliable scanning
- **Text**: Human-readable text below QR code
- **Description**: Optional static text at bottom of label

## Requirements

- Python 3.7+
- Windows (for network printing)
- Network access to Zebra ZT510 printer

## Dependencies

- `requests`: For web-based QR code generation
- `tkinter`: GUI framework (included with Python)

## Troubleshooting

### Printing Issues
- Ensure printer is accessible on network
- Check printer path format: `\\hostname\sharename`
- Try manual copy command if auto-print fails

### QR Code Issues
- Test with sample buttons (TEST123, ITEM-1, A-1)
- Check internet connection for QR generation
- Verify QR scanner can read generated codes

## File Structure

```
QR Gen/
├── qr_printer.py      # Main application
├── requirements.txt    # Python dependencies
├── run.bat           # Quick start batch file
└── README.md         # This file
```

## Example Usage

1. Run `run.bat`
2. Set prefix to "PART"
3. Set starting number to 100
4. Set quantity to 10
5. Add description "Widget Assembly"
6. Click "Generate QR Code"
7. Click "Print Labels"
8. Click "Yes" to print

This will generate labels: PART-100, PART-101, PART-102, ..., PART-109