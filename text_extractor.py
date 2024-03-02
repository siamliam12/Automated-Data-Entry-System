import pytesseract


pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

path = './downloads/jpg/web_prescription_big.jpg'


text = pytesseract.image_to_string(path)
print(text)