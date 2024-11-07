import os
import uuid
from datetime import datetime
import base64

from python_serviceplatformen.models.message import (
    Message, MessageHeader, Sender, Recipient, MessageBody, MainDocument, File
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
                        encodingFormat="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        filename=os.path.basename(attachment_file_path),
                        language="en",
                        content=encoded_content
                    )
                ]
            )
        )
    )
