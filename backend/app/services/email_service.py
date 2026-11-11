import logging

logger = logging.getLogger("email_service")


class EmailService:
    """Service simulating transactional email delivery for clinic notifications."""

    @staticmethod
    def send_appointment_confirmation(to_email: str, doctor_name: str, date_str: str, time_str: str) -> bool:
        """Dispatches an appointment confirmation email to the patient or clinic staff."""
        logger.info(f"Dispatched appointment confirmation to {to_email} with {doctor_name} at {date_str} {time_str}")
        return True

    @staticmethod
    def send_cancellation_notification(to_email: str, doctor_name: str, date_str: str, time_str: str, reason: str) -> bool:
        """Dispatches an appointment cancellation notification."""
        logger.info(f"Dispatched cancellation notice to {to_email} for {doctor_name} on {date_str}. Reason: {reason}")
        return True
