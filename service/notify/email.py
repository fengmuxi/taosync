"""
@Author：dr34m
@Date  ：2024/12/15 14:00 
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr


def send_email(title, content, params):
    """
    发送邮件通知
    :param title: 邮件标题
    :param content: 邮件内容
    :param params: 邮件配置参数
    :return: (bool, str) 发送结果和消息
    """
    try:
        # 解析邮件配置
        smtp_host = params.get('smtpHost')
        smtp_port = int(params.get('smtpPort', 25))
        smtp_user = params.get('smtpUser')
        smtp_password = params.get('smtpPassword')
        from_email = params.get('fromEmail')
        to_emails = params.get('toEmails')
        ssl = params.get('ssl', False)
        tls = params.get('tls', False)
        
        # 验证必填参数
        if not all([smtp_host, smtp_user, smtp_password, from_email, to_emails]):
            return False, "邮件配置不完整"
        
        # 分割收件人邮箱
        to_email_list = [email.strip() for email in to_emails.split(',') if email.strip()]
        if not to_email_list:
            return False, "请至少填写一个收件人邮箱"
        
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = formataddr((str(Header('Taosync', 'utf-8')), from_email))
        msg['To'] = ','.join(to_email_list)
        msg['Subject'] = Header(title, 'utf-8')
        
        # 添加邮件内容
        msg.attach(MIMEText(content, 'html', 'utf-8'))
        
        # 连接SMTP服务器
        if ssl:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
        
        # 启用TLS（如果配置）
        if tls:
            server.starttls()
        
        # 登录SMTP服务器
        server.login(smtp_user, smtp_password)
        
        # 发送邮件
        server.sendmail(from_email, to_email_list, msg.as_string())
        
        # 关闭连接
        server.quit()
        
        return True, "邮件发送成功"
    except Exception as e:
        logging.error(f"邮件发送失败: {str(e)}")
        return False, f"邮件发送失败: {str(e)}"
