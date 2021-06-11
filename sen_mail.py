import smtplib

from email.mime.multipart import MIMEMultipart  
from email.mime.base import MIMEBase  
from email.mime.text import MIMEText  
from email.utils import formatdate  
from email import encoders



def sndMail(no):
    toaddr = 'iotcloudsfire@gmail.com'      # To id 
    me = 'iotcloudsfire@gmail.com'          # your id
    subject = "Unregistered CAR"              # Subject

    msg = MIMEMultipart()  
    msg['Subject'] = subject  
    msg['From'] = me  
    msg['To'] = toaddr  
    msg.preamble = "test "   
    msg.attach(MIMEText('Stolen CAR no: '+no+' Identified'))
    
    part = MIMEBase('application', "octet-stream")  
    part.set_payload(open("abc1.jpg", "rb").read())  
    encoders.encode_base64(part)  
    part.add_header('Content-Disposition', 'attachment; filename="saved_img.jpg"')   # File name and format name
    msg.attach(part)  

    try:  
       s = smtplib.SMTP('smtp.gmail.com', 587)  # Protocol
       s.ehlo()  
       s.starttls()  
       s.ehlo()  
       s.login(user = 'iotcloudsfire@gmail.com', password = 'cloudiotcloud')  # User id & password
       #s.send_message(msg)  
       s.sendmail(me, toaddr, msg.as_string())  
       s.quit()  
    #except:  
    #   print ("Error: unable to send email")    
    except SMTPException as error:  
          print ("Error")                # Exception
