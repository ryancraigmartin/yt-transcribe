"""
Email delivery module for sending summaries via SMTP.

Handles formatting and sending of Markdown summaries to configured
email addresses.

TypeScript Context:
- Similar to using nodemailer in Node.js
- SMTP is the standard email protocol (like HTTP for email)
- Type hints make email structure clear
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dataclasses import dataclass


@dataclass
class EmailConfig:
    """
    SMTP configuration.

    TypeScript Equivalent:
        interface EmailConfig {
            server: string;
            port: number;
            username: string;
            password: string;
            fromAddress: string;
            toAddress: string;
        }
    """

    server: str
    port: int
    username: str
    password: str
    from_address: str
    to_address: str


class EmailError(Exception):
    """Raised when email sending fails."""

    pass


def send_summary_email(
    config: EmailConfig,
    video_title: str,
    summary: str,
    playlist_name: Optional[str] = None,
) -> None:
    """
    Send a summary email via SMTP.

    Args:
        config: SMTP configuration
        video_title: Title of the video
        summary: Markdown-formatted summary
        playlist_name: Optional playlist name

    Raises:
        EmailError: If email sending fails

    TypeScript Context:
        Similar to using nodemailer:
        const sendEmail = async (config: EmailConfig, subject: string, body: string) => {
            const transporter = nodemailer.createTransport({
                host: config.server,
                port: config.port,
                auth: { user: config.username, pass: config.password }
            })
            await transporter.sendMail({
                from: config.fromAddress,
                to: config.toAddress,
                subject,
                html: markdownToHtml(body)
            })
        }
    """
    # Build subject line
    subject = f"[YT-Transcribe] {video_title}"
    if playlist_name:
        subject = f"[YT-Transcribe: {playlist_name}] {video_title}"

    # Create email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.from_address
    msg["To"] = config.to_address

    # Add plain text version
    text_part = MIMEText(summary, "plain", "utf-8")
    msg.attach(text_part)

    # Convert Markdown to HTML for better email display
    html_content = markdown_to_html(summary)
    html_part = MIMEText(html_content, "html", "utf-8")
    msg.attach(html_part)

    # Send email
    try:
        with smtplib.SMTP(config.server, config.port, timeout=30) as server:
            server.starttls()  # Enable TLS encryption
            server.login(config.username, config.password)
            server.send_message(msg)

    except smtplib.SMTPAuthenticationError:
        raise EmailError(
            "SMTP authentication failed. Check username/password. "
            "For Gmail, use an App Password instead of your regular password."
        )
    except smtplib.SMTPException as e:
        raise EmailError(f"Failed to send email: {e}")
    except Exception as e:
        raise EmailError(f"Unexpected error sending email: {e}")


def markdown_to_html(markdown_text: str) -> str:
    """
    Convert Markdown to basic HTML for email display.

    This is a simple converter for basic Markdown features.
    For production, consider using a library like markdown or mistune.

    Args:
        markdown_text: Markdown-formatted text

    Returns:
        str: HTML-formatted text

    TypeScript Context:
        Similar to using marked or markdown-it:
        const markdownToHtml = (md: string): string => marked.parse(md)
    """
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
                margin-top: 24px;
                margin-bottom: 16px;
            }}
            h1 {{ font-size: 2em; border-bottom: 2px solid #eee; padding-bottom: 8px; }}
            h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 4px; }}
            h3 {{ font-size: 1.25em; }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Monaco', 'Courier New', monospace;
            }}
            pre {{
                background-color: #f4f4f4;
                padding: 12px;
                border-radius: 4px;
                overflow-x: auto;
            }}
            ul, ol {{
                margin-left: 24px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            blockquote {{
                border-left: 4px solid #ddd;
                padding-left: 16px;
                margin-left: 0;
                color: #666;
            }}
        </style>
    </head>
    <body>
"""

    # Simple Markdown to HTML conversion
    # In production, use a proper Markdown library
    lines = markdown_text.split("\n")
    in_code_block = False

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                html += "</pre>\n"
                in_code_block = False
            else:
                html += "<pre><code>"
                in_code_block = True
            continue

        if in_code_block:
            html += line + "\n"
            continue

        # Headers
        if line.startswith("### "):
            html += f"<h3>{line[4:]}</h3>\n"
        elif line.startswith("## "):
            html += f"<h2>{line[3:]}</h2>\n"
        elif line.startswith("# "):
            html += f"<h1>{line[2:]}</h1>\n"
        # Lists
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            html += f"<li>{line.strip()[2:]}</li>\n"
        elif line.strip() and line.strip()[0].isdigit() and ". " in line.strip()[:5]:
            # Handle numbered lists (e.g., "1. ", "10. ", "100. ")
            content = line.strip().split(". ", 1)
            if len(content) > 1:
                html += f"<li>{content[1]}</li>\n"
            else:
                html += f"<p>{line}</p>\n"
        # Paragraphs
        elif line.strip():
            html += f"<p>{line}</p>\n"
        else:
            html += "<br/>\n"

    html += """
    </body>
    </html>
    """

    return html


def verify_smtp_config(config: EmailConfig) -> bool:
    """
    Verify SMTP configuration by attempting to connect.

    Args:
        config: SMTP configuration to verify

    Returns:
        bool: True if connection successful, False otherwise

    TypeScript Context:
        Similar to testing a connection:
        const verifySmtpConfig = async (config: EmailConfig): Promise<boolean> => {
            try {
                const transporter = createTransporter(config)
                await transporter.verify()
                return true
            } catch {
                return false
            }
        }
    """
    try:
        with smtplib.SMTP(config.server, config.port, timeout=10) as server:
            server.starttls()
            server.login(config.username, config.password)
            return True
    except Exception:
        return False
