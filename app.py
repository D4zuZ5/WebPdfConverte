import os
import logging
import requests
from flask import Flask, render_template, request, jsonify, send_file
from weasyprint import HTML, CSS
from io import BytesIO
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

@app.route('/')
def index():
    """Render the main page of the application."""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    """Convert HTML content to PDF and return the PDF file."""
    try:
        # Get HTML content from the request
        html_content = request.form.get('html_content', '')
        
        if not html_content:
            return jsonify({'error': 'No HTML content provided'}), 400
        
        # Create a BytesIO object to store the PDF
        pdf_buffer = BytesIO()
        
        # Convert HTML to PDF using WeasyPrint
        HTML(string=html_content).write_pdf(
            pdf_buffer,
            # Enable link preservation
            presentational_hints=True
        )
        
        # Reset the buffer position to the beginning
        pdf_buffer.seek(0)
        
        # Return the PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='converted.pdf'
        )
    
    except Exception as e:
        logger.error(f"Error in PDF conversion: {str(e)}")
        return jsonify({'error': f'PDF conversion failed: {str(e)}'}), 500

@app.route('/preview', methods=['POST'])
def preview():
    """Generate a preview of the HTML content for the live preview feature."""
    try:
        # Get HTML content from the request
        html_content = request.form.get('html_content', '')
        
        if not html_content:
            return jsonify({'error': 'No HTML content provided'}), 400
        
        # Return the HTML content as-is for preview
        return html_content
    
    except Exception as e:
        logger.error(f"Error in preview generation: {str(e)}")
        return jsonify({'error': f'Preview generation failed: {str(e)}'}), 500

@app.route('/get_logo', methods=['GET'])
def get_logo():
    """Fetch a company logo from Clearbit API."""
    try:
        # Get domain from the request
        domain = request.args.get('domain', '')
        
        if not domain:
            return jsonify({'error': 'No domain provided'}), 400
        
        # Validate domain format
        parsed = urlparse(domain)
        if not parsed.netloc:
            # If no scheme is provided, add http:// and try again
            if not domain.startswith('http'):
                parsed = urlparse(f"http://{domain}")
        
        # Extract the domain name
        domain_name = parsed.netloc or parsed.path
        
        # Remove www. if present
        if domain_name.startswith('www.'):
            domain_name = domain_name[4:]
        
        # Request logo from Clearbit
        logo_url = f"https://logo.clearbit.com/{domain_name}"
        
        # Return the logo URL
        return jsonify({'logo_url': logo_url})
    
    except Exception as e:
        logger.error(f"Error fetching logo: {str(e)}")
        return jsonify({'error': f'Failed to fetch logo: {str(e)}'}), 500

@app.route('/templates', methods=['GET'])
def get_templates():
    """Return a list of available templates with dynamic company logos."""
    templates = [
        {
            'id': 1,
            'name': 'Basic Template',
            'description': 'A simple template with header, content, and footer',
            'html': """
<!DOCTYPE html>
<html>
<head>
    <title>Basic Template</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { text-align: center; margin-bottom: 20px; }
        .logo { max-width: 150px; }
        .content { line-height: 1.6; }
        .footer { margin-top: 30px; text-align: center; font-size: 12px; color: #666; }
        a { color: #0066cc; }
    </style>
</head>
<body>
    <div class="header">
        <img class="logo" src="LOGO_PLACEHOLDER" alt="Company Logo">
        <h1>COMPANY_NAME</h1>
    </div>
    <div class="content">
        <h2>Welcome to our document</h2>
        <p>This is a sample paragraph with a <a href="https://example.com">link</a> that will remain clickable in the PDF.</p>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
    </div>
    <div class="footer">
        <p>&copy; 2023 COMPANY_NAME. All rights reserved.</p>
        <p>Visit our website: <a href="https://DOMAIN_PLACEHOLDER">DOMAIN_PLACEHOLDER</a></p>
    </div>
</body>
</html>
            """
        },
        {
            'id': 2,
            'name': 'Business Report',
            'description': 'A professional template for business reports',
            'html': """
<!DOCTYPE html>
<html>
<head>
    <title>Business Report</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }
        .report-header { background-color: #f5f5f5; padding: 20px; display: flex; align-items: center; justify-content: space-between; }
        .logo { max-width: 120px; }
        .company-info { text-align: right; }
        .report-title { text-align: center; margin: 30px 0; }
        .report-content { padding: 0 30px; line-height: 1.6; }
        .section { margin-bottom: 30px; }
        .footer { margin-top: 50px; border-top: 1px solid #ddd; padding-top: 20px; text-align: center; font-size: 12px; color: #666; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="report-header">
        <img class="logo" src="LOGO_PLACEHOLDER" alt="Company Logo">
        <div class="company-info">
            <h2>COMPANY_NAME</h2>
            <p>Business Report</p>
            <p>Date: January 1, 2023</p>
        </div>
    </div>
    <div class="report-title">
        <h1>Quarterly Business Report</h1>
        <p>Q4 2022</p>
    </div>
    <div class="report-content">
        <div class="section">
            <h2>Executive Summary</h2>
            <p>This report provides an overview of our business performance for Q4 2022. For more details, please visit our <a href="https://DOMAIN_PLACEHOLDER/reports">reports page</a>.</p>
        </div>
        <div class="section">
            <h2>Financial Performance</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Q3 2022</th>
                    <th>Q4 2022</th>
                    <th>Change</th>
                </tr>
                <tr>
                    <td>Revenue</td>
                    <td>$1,245,000</td>
                    <td>$1,385,000</td>
                    <td>+11.2%</td>
                </tr>
                <tr>
                    <td>Expenses</td>
                    <td>$845,000</td>
                    <td>$895,000</td>
                    <td>+5.9%</td>
                </tr>
                <tr>
                    <td>Net Profit</td>
                    <td>$400,000</td>
                    <td>$490,000</td>
                    <td>+22.5%</td>
                </tr>
            </table>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2023 COMPANY_NAME. All rights reserved.</p>
        <p>For inquiries, please contact us at <a href="mailto:info@DOMAIN_PLACEHOLDER">info@DOMAIN_PLACEHOLDER</a></p>
        <p>Visit our website: <a href="https://DOMAIN_PLACEHOLDER">DOMAIN_PLACEHOLDER</a></p>
    </div>
</body>
</html>
            """
        },
        {
            'id': 3,
            'name': 'Newsletter',
            'description': 'A template for newsletters and announcements',
            'html': """
<!DOCTYPE html>
<html>
<head>
    <title>Newsletter</title>
    <style>
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 0; padding: 0; background-color: #f9f9f9; color: #333; }
        .container { max-width: 800px; margin: 0 auto; background-color: white; padding: 30px; }
        .header { text-align: center; padding-bottom: 20px; border-bottom: 2px solid #eaeaea; }
        .logo { max-width: 180px; margin-bottom: 15px; }
        .issue-info { font-size: 14px; color: #777; margin-top: 10px; }
        .content { padding: 20px 0; }
        .article { margin-bottom: 30px; }
        .article h2 { color: #2c3e50; }
        .article-meta { font-size: 13px; color: #95a5a6; margin-bottom: 10px; }
        .cta-button { display: inline-block; background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 10px; }
        .footer { text-align: center; padding-top: 20px; border-top: 2px solid #eaeaea; font-size: 12px; color: #7f8c8d; }
        .social-links { margin: 15px 0; }
        .social-links a { margin: 0 10px; color: #3498db; text-decoration: none; }
        a { color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img class="logo" src="LOGO_PLACEHOLDER" alt="Company Logo">
            <h1>COMPANY_NAME Newsletter</h1>
            <p class="issue-info">Issue #42 - January 2023</p>
        </div>
        <div class="content">
            <div class="article">
                <h2>Exciting Company Updates</h2>
                <p class="article-meta">Posted on January 5, 2023 by Marketing Team</p>
                <p>We're thrilled to announce several exciting developments at COMPANY_NAME. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt.</p>
                <p>Read more on our <a href="https://DOMAIN_PLACEHOLDER/news">news page</a>.</p>
                <a href="https://DOMAIN_PLACEHOLDER/updates" class="cta-button">Learn More</a>
            </div>
            <div class="article">
                <h2>Product Spotlight: New Features</h2>
                <p class="article-meta">Posted on January 3, 2023 by Product Team</p>
                <p>Check out these amazing new features we've added to our flagship product. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.</p>
                <a href="https://DOMAIN_PLACEHOLDER/features" class="cta-button">See Features</a>
            </div>
        </div>
        <div class="footer">
            <div class="social-links">
                <a href="https://twitter.com/COMPANY_NAME">Twitter</a>
                <a href="https://facebook.com/COMPANY_NAME">Facebook</a>
                <a href="https://linkedin.com/company/COMPANY_NAME">LinkedIn</a>
            </div>
            <p>&copy; 2023 COMPANY_NAME. All rights reserved.</p>
            <p>Visit our website: <a href="https://DOMAIN_PLACEHOLDER">DOMAIN_PLACEHOLDER</a></p>
            <p>To unsubscribe, <a href="https://DOMAIN_PLACEHOLDER/unsubscribe">click here</a>.</p>
        </div>
    </div>
</body>
</html>
            """
        }
    ]
    
    return jsonify({'templates': templates})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
