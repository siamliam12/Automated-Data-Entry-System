import pytesseract
import re
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

class Text():
    def extractor(self,path,files):
        files = os.listdir(path)
        for file in files:
            workfile = os.path.join(path, file)
            text = pytesseract.image_to_string(workfile)
            # Define regex patterns
            name_pattern = r'Patient:\s*(.*?)\s*\n'
            age_pattern = r'Female,\s*(\d+)\s*years'
            date_pattern = r'Date:\s*(\d{2}-\d{2}-\d{4})'
            complaint_pattern = r'Complaint:\s*(.*?)\s*\n'
            diagnosis_pattern = r'Diagnosis:\s*(.*?)\s*\n'
            prescription_pattern = r'Rx\nMedicine\s+(.*?)\n\n'

            # Search for patterns in the text
            name_match = re.search(name_pattern, text)
            age_match = re.search(age_pattern, text)
            date_match = re.search(date_pattern, text)
            complaint_match = re.search(complaint_pattern, text)
            diagnosis_match = re.search(diagnosis_pattern, text)
            prescription_match = re.search(prescription_pattern, text, re.DOTALL)

            # Extract information
            name = name_match.group(1) if name_match else None
            age = int(age_match.group(1)) if age_match else None
            date = date_match.group(1) if date_match else None
            complaint = complaint_match.group(1) if complaint_match else None
            diagnosis = diagnosis_match.group(1) if diagnosis_match else None
            prescription_info = prescription_match.group(1).strip() if prescription_match else None

            # Print extracted information
            print("Name:", name)
            print("Age:", age)
            print("Date:", date)
            print("Complaint:", complaint)
            print("Diagnosis:", diagnosis)
            print("Prescription info: ",prescription_info)
            print("================================================")

text = Text()