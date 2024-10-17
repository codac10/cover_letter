from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from generate_letter import generate_pdf, write_letter
import logging

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/', methods=['GET', 'POST'])
def form():
    # Log when the form is accessed
    logging.info("Accessed the form page.")

    if request.method == 'POST':
        # Log the request method
        logging.info("Received POST request.")

        # Extract form data
        full_name = request.form.get('full_name')
        company = request.form.get('company')
        email = request.form.get('email')
        phone = request.form.get('phone')
        letter_content = request.form.get('cover_letter').replace('\n', '<br/>')

        # Log the extracted data
        logging.info(f"Form data received - Name: {full_name}, Company: {company}, Email: {email}, Phone: {phone}")

        # Call the write_letter function to prepare the content
        contact_info, content = write_letter(letter_content, company, full_name, email, phone)

        # Generate the PDF file from the letter content
        pdf_buffer = generate_pdf((contact_info, content), full_name, company)

        # Check if PDF generation was successful
        if pdf_buffer is None:
            logging.error("PDF generation failed.")
            flash("Error generating PDF. Please try again.", "error")
            return redirect(url_for('form'))

        # Log the successful PDF generation
        logging.info(f"PDF generated successfully for {full_name} at {company}. Preparing to send.")

        # Send the generated PDF file as an attachment
        return send_file(pdf_buffer, as_attachment=True, download_name=f"Cover_Letter_{company}.pdf", mimetype='application/pdf')

    # Render the form template for GET requests
    return render_template('form.html')

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True)
