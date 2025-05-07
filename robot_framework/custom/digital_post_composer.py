"""Function for composing a message for Digital Post welcoming letter."""
import os
import uuid
from datetime import datetime
import base64
import io

from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from python_serviceplatformen.models.message import (
    Message, MessageHeader, Sender, Recipient, MessageBody, MainDocument, File, Action, EntryPoint
)

from robot_framework import config


def compose_message(label: str, cvr: str, recipient_cpr: str, recipient_name: str, attachment_file_path: str) -> Message:
    """Compose a message for Digital Post according to the requirements for a welcome letter.

    Args:
        label: Title of letter.
        cvr: CVR of the entity sending the letter.
        recipient_cpr: CPR of person to send the letter to.
        attachment_file_path: File for the message body.

    Returns:
        Message formatted with data to send with Digital Post.
    """
    encoded_content = generate_pdf(attachment_file_path, recipient_name)

    return Message(
        messageHeader=MessageHeader(
            messageType="DIGITALPOST",
            messageUUID=str(uuid.uuid4()),
            label=label,
            mandatory=False,
            legalNotification=False,
            sender=Sender(
                senderID=cvr,
                idType="CVR",
                label="Aarhus Kommune"
            ),
            recipient=Recipient(
                recipientID=recipient_cpr,
                idType="CPR"
            )
        ),
        messageBody=MessageBody(
            createdDateTime=datetime.now(),
            mainDocument=MainDocument(
                files=[
                    File(
                        encodingFormat="application/pdf",
                        filename=os.path.basename(attachment_file_path),
                        language="en",
                        content=encoded_content
                    )
                ],
                actions=[
                    Action(label="Explore international.aarhus.dk to discover more",
                           actionCode="INFORMATION",
                           entryPoint=EntryPoint(url=config.EXPLORE_LINK)),
                    Action(label="What do you think of this letter? Complete our survey for a chance to win a gift card to Musikhuset Aarhus!",
                           actionCode="INFORMATION",
                           entryPoint=EntryPoint(url=config.FEEDBACK_LINK)),
                ]
            )
        )
    )


def generate_pdf(pdf_template: str, name: str) -> str:
    packet = io.BytesIO()
    name_canvas = canvas.Canvas(packet, A4)
    _, height = A4

    # Setup font
    pdfmetrics.registerFont(TTFont(config.FONT_NAME, config.FONT_PATH))
    name_canvas.setFont(config.FONT_NAME, 24)
    name_canvas.setFillColor(HexColor(config.FONT_COLOR))

    # Create PDF layer for name
    name_canvas.drawString(100, height - 64, f"{name},")
    name_canvas.save()
    packet.seek(0)
    name_pdf = PdfReader(packet)

    # Add name to template
    template_pdf = PdfReader(pdf_template)
    page = template_pdf.pages[0]
    page.merge_page(name_pdf.pages[0])

    # Prepare output
    output = PdfWriter()
    output.add_page(page)

    output.write(packet)  # packet

    # Encoded content
    return base64.b64encode(packet.getvalue()).decode('utf-8')
