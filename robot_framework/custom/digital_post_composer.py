"""Function for composing a message for Digital Post welcoming letter."""
import os
import uuid
from datetime import datetime
import base64

from python_serviceplatformen.models.message import (
    Message, MessageHeader, Sender, Recipient, MessageBody, MainDocument, File, Action, EntryPoint
)

from robot_framework import config


def compose_message(label: str, cvr: str, recipient_cpr: str, attachment_file_path: str) -> Message:
    """Compose a message for Digital Post according to the requirements for a welcome letter.

    Args:
        label: Title of letter.
        cvr: CVR of the entity sending the letter.
        recipient_cpr: CPR of person to send the letter to.
        attachment_file_path: File for the message body.

    Returns:
        Message formatted with data to send with Digital Post.
    """
    with open(attachment_file_path, 'rb') as file:
        file_content = file.read()
    encoded_content = base64.b64encode(file_content).decode('utf-8')

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
