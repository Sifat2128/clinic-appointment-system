"""Experimental third-party SMS notification gateway adapter (Proposal)."""
import logging

logger = logging.getLogger("sms_service")


class SMSService:
    """Experimental adapter for SMS gateway telecommunications."""

    @staticmethod
    def send_sms_alert(phone_number: str, message: str) -> bool:
        logger.info(f"Simulating dispatch of SMS to {phone_number}: {message}")
        return True
