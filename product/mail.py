import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from django.conf import settings
def send_order_mail( recipient_email, username,order):
    try:
    # Create message container
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.EMAIL_ID
        msg['To'] = recipient_email
        msg['Subject'] = 'Order Confirmation'

        # Create the HTML content
        html_content = f"""
        <html>
        <body>
            <p>Hello {username},</p>
            <p>Your order ID{order.order_id}</p>
            <p>Thanks for puchasing products in our shop</p>
            <p>regards</p>
            <p>Rathna Store</p>
            <p>9445737480</p>
        </body>
        </html>
        """

        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        with open(order.bill.path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {order.order_id}.pdf')
        msg.attach(part)

        
        # Connect to SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(settings.EMAIL_ID, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_ID, recipient_email, msg.as_string())
        
    except Exception as e:
        print(e)
