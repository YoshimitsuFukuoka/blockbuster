from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self, region: str, sender: str, recipient: str) -> None:
        self.region = region
        self.sender = sender
        self.recipient = recipient

    def send(self, subject: str, html_body: str) -> None:
        import boto3
        from botocore.exceptions import ClientError

        client = boto3.client("ses", region_name=self.region)
        try:
            client.send_email(
                Source=self.sender,
                Destination={"ToAddresses": [self.recipient]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {"Html": {"Data": html_body, "Charset": "UTF-8"}},
                },
            )
            logger.info("Email sent to %s: %s", self.recipient, subject)
        except ClientError as exc:
            logger.error("Failed to send email: %s", exc)
            raise
