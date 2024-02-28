

import sys
import win32com.client as win32

def send_email(e, image_path=None):
    try:
        print("Sending email")
        # Construct Outlook app instance
        ol_app = win32.Dispatch('Outlook.Application')
        ol_ns = ol_app.GetNameSpace('MAPI')

        mail_item = ol_app.CreateItem(0)
        mail_item.Subject = "Error Script Programación"
        mail_item.BodyFormat = 1
        mail_item.Body = "Error!"
        mail_item.HTMLBody = "Ha sucedido el siguiente error: " + str(e)

        # Add recipients
        mail_item.To = 'santiagoandres.ortiz@cemex.com'

        if image_path:
            # Attach image if image_path is provided
            attachment = mail_item.Attachments.Add(image_path)
            attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "MyImage")
            mail_item.HTMLBody += f'<br><img src="cid:MyImage">'

        mail_item.Save()
        mail_item.Send()
    except Exception as e:
        print(str(e))
        sys.exit()

# Example usage:
send_email("An error occurred", r"C:\Users\snortiz\Documents\projects\Imagen1.png")