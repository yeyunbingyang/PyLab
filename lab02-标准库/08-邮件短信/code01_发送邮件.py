'''
============================================================
 邮件发送: smtplib + email.mime
============================================================
对照笔记: 08 邮件短信-smtplib/Python发送邮件和短信.md
  — SMTP_SSL 连接邮件服务器
  — login 登录 (邮箱 + 授权码)
  — MIMEMultipart 构造邮件
  — MIMEText 纯文本/HTML/附件 (BASE64)
  — Header 中文主题
============================================================
'''

# ═══════════════════════════════════════════════════════════════
# 1. SMTP 邮件服务器配置
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【SMTP 邮件服务器】")
print("=" * 50)

print("  常用 SMTP 配置:")
print("    QQ邮箱  : smtp.qq.com       SSL端口 465")
print("    163邮箱 : smtp.163.com      SSL端口 465")
print("    126邮箱 : smtp.126.com      SSL端口 465")
print("    Gmail   : smtp.gmail.com    SSL端口 465")
print()
print("  注意:")
print("    1. 需要开启 SMTP 服务 (邮箱设置中)")
print("    2. 获取授权码 (非登录密码)")
print("    3. QQ邮箱 → 设置 → 账户 → POP3/SMTP服务 → 开启")

# ═══════════════════════════════════════════════════════════════
# 2. 发送纯文本邮件
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【发送纯文本邮件 — 示例代码】")
print("=" * 50)

print(r'''
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. 创建邮件对象
email = MIMEMultipart()
email['From'] = 'your_email@126.com'
email['To'] = 'receiver@qq.com;other@1000phone.com'
email['Subject'] = Header('上半年工作情况汇报', 'utf-8')

# 2. 添加正文
content = """尊敬的领导：
  上半年工作汇报内容...
"""
email.attach(MIMEText(content, 'plain', 'utf-8'))

# 3. 连接服务器 + 登录 + 发送
smtp_obj = smtplib.SMTP_SSL('smtp.126.com', 465)
smtp_obj.login('your_email@126.com', '授权码')
smtp_obj.sendmail(
    'your_email@126.com',
    ['receiver@qq.com'],
    email.as_string()
)
print('邮件发送成功!')
'''.strip())

# ═══════════════════════════════════════════════════════════════
# 3. 发送 HTML 邮件
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【HTML 邮件 — 带格式】")
print("=" * 50)

print(r'''
html_content = """<p>亲爱的同事：</p>
<p>你需要的文件在附件中，请查收！</p>
<br>
<p>祝，好！</p>
<hr>
<p>孙美丽 即日</p>"""
email.attach(MIMEText(html_content, 'html', 'utf-8'))
'''.strip())

# ═══════════════════════════════════════════════════════════════
# 4. 发送带附件的邮件
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【发送附件 — BASE64 编码】")
print("=" * 50)

print(r'''
from urllib.parse import quote

# 读取文件并以 BASE64 编码附加
with open('王大锤离职证明.docx', 'rb') as file:
    attachment = MIMEText(file.read(), 'base64', 'utf-8')
    attachment['content-type'] = 'application/octet-stream'
    # 中文文件名需编码
    attachment['content-disposition'] = f'attachment; filename="{quote("王大锤离职证明.docx")}"'

email.attach(attachment)
'''.strip())

# ═══════════════════════════════════════════════════════════════
# 5. MIME 类型速查
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【MIME 类型速查】")
print("=" * 50)

print("  MIMEText(content, 'plain', 'utf-8')    — 纯文本")
print("  MIMEText(content, 'html', 'utf-8')     — HTML 内容")
print("  MIMEText(data, 'base64', 'utf-8')      — 附件")
print("  MIMEImage(img_data)                     — 图片附件")
print("  MIMEApplication(pdf_data)               — 应用附件")
print()
print("  标准流程:")
print("    创建 MIMEMultipart → 设置 From/To/Subject")
print("    → attach 正文/附件 → SMTP_SSL 连接 → login → sendmail")
