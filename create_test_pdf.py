from fpdf import FPDF

def create_test_pdf(output_path):
    pdf = FPDF()
    pdf.add_page()
    
    # Add a title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'PDF Converter API Test Document', ln=True, align='C')
    pdf.ln(10)
    
    # Add some text
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'This is a test PDF document created for testing the PDF Converter API.', ln=True)
    pdf.cell(0, 10, 'It contains text that can be extracted and converted to other formats.', ln=True)
    pdf.ln(10)
    
    # Add a subtitle
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Features to Test:', ln=True)
    pdf.ln(5)
    
    # Add a list
    pdf.set_font('Arial', '', 12)
    features = [
        'PDF to DOCX conversion',
        'PDF to JPEG conversion',
        'Text extraction',
        'Layout preservation',
        'Page selection'
    ]
    
    for feature in features:
        pdf.cell(10, 10, '*', ln=0)
        pdf.cell(0, 10, feature, ln=True)
    
    pdf.ln(10)
    
    # Add a conclusion
    pdf.set_font('Arial', 'I', 12)
    pdf.cell(0, 10, 'This document was automatically generated for testing purposes.', ln=True)
    
    # Save the PDF
    pdf.output(output_path)
    print(f"Test PDF created successfully at: {output_path}")

if __name__ == "__main__":
    create_test_pdf("C:/Xesium/pdfconvertorapi/tmp/test.pdf")
