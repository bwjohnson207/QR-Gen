@echo off
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Starting QR Code Label Printer...
python qr_printer.py

pause
