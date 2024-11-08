import os
import uuid
from datetime import datetime
import base64

from python_serviceplatformen.models.message import (
    Message, MessageHeader, Sender, Recipient, MessageBody, MainDocument, File, Action, EntryPoint
)


def compose_message(label: str, cvr: str, recipient_cpr: str, attachment_file_path: str):
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
                label="Python Serviceplatformen"
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
                           entryPoint=EntryPoint(url="https://direc.to/kN8s")),
                    Action(label="What do you think of this letter? Complete our survey for a chance to win a gift card to Musikhuset Aarhus!",
                           actionCode="INFORMATION",
                           entryPoint=EntryPoint(url="https://www.survey-xact.dk/LinkCollector?key=1HZ74774L19K")),
                ]
            )
        )
    )
