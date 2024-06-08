import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
def send_user_activation_mail( recipient_email, username,token):
    try:
    # Create message container
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.EMAIL_ID
        msg['To'] = recipient_email
        msg['Subject'] = 'User Account Activation'

        # Create the HTML content
        html_content = f"""
        <html>
        <body>
            <p>Hello {username},</p>
            <p>Thanks for creating account in Rathna Store. Kindly click this <a href="{settings.CLIENT_URL}account-activation/{token}" target="_blank">link</a> to account and continue shopping.</p>
            <p>regards</p>
            <p>Rathna Store</p>
            <p>9445737480</p>
        </body>
        </html>
        """

        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))

        # Connect to SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(settings.EMAIL_ID, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_ID, recipient_email, msg.as_string())

    except Exception as e:
        print(e)



def send_otp_mail( recipient_email, username,otp):
    try:
    # Create message container
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.EMAIL_ID
        msg['To'] = recipient_email
        msg['Subject'] = 'Forget Password Request'

        # Create the HTML content
        html_content = f"""
        <html>
        <body>
            <p>Hello {username},</p>
            <p>OTP to reset password is {otp}. This OTP is valid for 10 minutes </p>
            <p>Kindly don't share it to anyone.</p>
            <p>Thank You</p>
            <p>regards</p>
            <p>Rathna Store</p>
            <p>9445737480</p>
        </body>
        </html>
        """

        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))

        # Connect to SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(settings.EMAIL_ID, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_ID, recipient_email, msg.as_string())

    except Exception as e:
        print(e)