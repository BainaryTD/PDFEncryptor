import os
import smtplib
from email.message import EmailMessage
import logging
from dotenv import load_dotenv

# (ถ้าต้องการดู log การทำงานของ smtplib ให้เปิดระดับ DEBUG)
logging.basicConfig(level=logging.INFO)

load_dotenv()
# 1. อ่านค่าจาก Environment
SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT   = 587
USERNAME    = os.getenv('SMTP_USERNAME')
PASSWORD    = os.getenv('SMTP_PASSWORD')

# 2. ตรวจสอบว่ามีค่า ENV หรือไม่
if not USERNAME or not PASSWORD:
    raise RuntimeError("ไม่พบค่า SMTP_USERNAME หรือ SMTP_PASSWORD ใน Environment")

# 3. สร้างอีเมล
msg = EmailMessage()
msg['Subject'] = 'ทดสอบส่งเมลจาก Python'
msg['From']    = USERNAME
msg['To']      = ''   # แก้เป็นอีเมลผู้รับจริง
msg.set_content(
    'สวัสดีครับ\nนี่คือเมลทดสอบ ส่งจาก Python ผ่าน Office365 SMTP'
)

# (ถ้าต้องการส่ง HTML ด้วย)
html = """
<html>
  <body>
    <h2>สวัสดีจาก Microsoft 365!</h2>
    <p>นี่คืออีเมล <b>HTML</b> ที่ส่งจาก Python</p>
  </body>
</html>
"""
msg.add_alternative(html, subtype='html')

# 4. ส่งอีเมล
with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
    smtp.set_debuglevel(1)   # 0=ปิด, 1=ดู DEBUG
    smtp.ehlo()              # ทักทาย
    smtp.starttls()          # เข้ารหัส TLS
    smtp.ehlo()              # ทักทายใหม่หลัง TLS
    smtp.login(USERNAME, PASSWORD)
    smtp.send_message(msg)

print("ส่งอีเมลเรียบร้อยแล้ว")
