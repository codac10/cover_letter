from flask import Flask, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_JUSTIFY
import io
import re
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Register Times New Roman font for use in the PDF
pdfmetrics.registerFont(TTFont('Times-Roman', 'Times New Roman.ttf'))

def write_letter(text, company_name, full_name, email, phone):
    """
    Prepares the letter content by replacing placeholders and formatting contact information.

    :param text: The text of the cover letter.
    :param company_name: The name of the company.
    :param full_name: The full name of the person.
    :param email: The email address of the person.
    :param phone: The phone number of the person.
    :return: A tuple containing the formatted contact info and letter content.
    """
    
    text = text.replace('<br>', '<br/>')
    
    # Replace &nbsp; with regular spaces
    text = text.replace('&nbsp;', ' ')
    
    # Replace & with its HTML entity to render correctly
    #text = text.replace('&', '&amp;')
    
    content = text.replace('[EMPRESA]', company_name)
    #content = text.replace('<span class="border-box truncate pill px1 cellToken choiceToken inline-block redLight2 print-color-exact text-dark" contenteditable="false" id="companyToken">@company</span>', company_name)
    
               
    #content = re.sub(r'\s+', ' ', content)
    
    # Prepare contact information with <br/> for correct formatting in PDF
    contact_info = f"{full_name}<br/>{email}<br/>{phone}<br/>"  # Each piece on a new line
    
    # Log the formatted contact info
    logging.info(f"Contact info prepared: {contact_info}")

    return contact_info, content

def generate_pdf(content, full_name, company_name):
    """
    Generates a PDF document containing the letter content and contact information.

    :param content: A tuple containing the contact info and letter content.
    :param full_name: The full name of the person.
    :param company_name: The name of the company.
    :return: A BytesIO object containing the PDF or None if an error occurs.
    """
    # Create a BytesIO buffer to hold the PDF in memory
    buffer = io.BytesIO()

    # Set up the PDF document with specified pagesize and margins
    pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=64, leftMargin=64, topMargin=64, bottomMargin=18)
    styles = getSampleStyleSheet()
    right_align_style = ParagraphStyle(name="RightAlign", alignment=TA_RIGHT, fontName="Times-Roman", fontSize=11)
    justified_style = ParagraphStyle(name="Justified", alignment=TA_JUSTIFY, fontName="Times-Roman", fontSize=11, leading=14)

    story = []
    contact_info, letter_content = content

    # Log the start of PDF generation
    logging.info(f"Generating PDF for {full_name} at {company_name}.")

    # Add contact info to the PDF, using Paragraph for each line
    story.append(Paragraph(contact_info.replace('\n', '<br/>'), right_align_style))  # Using <br/> here is okay since the string is not processed by the Paragraph again
    story.append(Spacer(1, 20))

    # Split letter content into paragraphs and add line breaks for each new paragraph
    paragraphs = letter_content.split("<br/>")
    for para in paragraphs:
        if para.strip():  # Only add non-empty paragraphs
            story.append(Paragraph(para.strip(), justified_style))
            story.append(Spacer(1, 12))

    try:
        # Build the PDF
        pdf.build(story)
        buffer.seek(0)  # Go to the beginning of the BytesIO buffer

        # Log successful PDF generation
        logging.info(f"PDF generated successfully for {full_name}.")
        
        return buffer  # Return the BytesIO object containing the PDF
    except Exception as e:
        # Log any errors encountered during PDF generation
        logging.error(f"Error generating PDF: {e}")
        return None
