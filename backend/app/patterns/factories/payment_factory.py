from abc import ABC, abstractmethod
from typing import Any
from backend.app.models.billing import Invoice, Payment, PaymentStatus


class IPaymentProcessor(ABC):
    """Abstract Product interface for payment processing channels."""

    @abstractmethod
    def process_payment(self, invoice: Invoice, amount: float, transaction_ref: str | None = None) -> Payment:
        """Processes payment and instantiates a persistent Payment entity."""
        pass


class CashPaymentProcessor(IPaymentProcessor):
    """Concrete Processor handling physical cash transactions at clinic reception."""

    def process_payment(self, invoice: Invoice, amount: float, transaction_ref: str | None = None) -> Payment:
        if amount < invoice.net_total:
            raise ValueError(f"Insufficient cash tendered: provided {amount}, required {invoice.net_total}.")

        return Payment(
            invoice_id=invoice.id,
            payment_method="CASH",
            amount_paid=amount,
            transaction_ref=transaction_ref or "CASH-COUNTER",
            status=PaymentStatus.SUCCESS.value,
        )


class CardPaymentProcessor(IPaymentProcessor):
    """Concrete Processor integrating with external credit/debit card gateway."""

    def _simulate_bank_gateway(self, card_ref: str, amount: float) -> dict[str, Any]:
        """External banking network gateway simulation (Mocked in isolated unit tests)."""
        return {"gateway_status": "APPROVED", "auth_code": f"AUTH-{card_ref[:8]}"}

    def process_payment(self, invoice: Invoice, amount: float, transaction_ref: str | None = None) -> Payment:
        if amount < invoice.net_total:
            raise ValueError(f"Charged amount {amount} is less than invoice total {invoice.net_total}.")

        ref = transaction_ref or "CARD-UNKNOWN"
        gateway_resp = self._simulate_bank_gateway(ref, amount)

        if gateway_resp.get("gateway_status") != "APPROVED":
            raise ValueError("Card payment authorization declined by issuing bank.")

        return Payment(
            invoice_id=invoice.id,
            payment_method="CARD",
            amount_paid=amount,
            transaction_ref=f"{ref} ({gateway_resp.get('auth_code', '')})",
            status=PaymentStatus.SUCCESS.value,
        )


class MobileBankingPaymentProcessor(IPaymentProcessor):
    """Concrete Processor handling mobile financial services (bKash / Nagad / Rocket)."""

    def _simulate_wallet_verification(self, txn_id: str, amount: float) -> bool:
        """Verifies electronic mobile transaction validity (Mocked in unit tests)."""
        return bool(txn_id and len(txn_id) >= 6)

    def process_payment(self, invoice: Invoice, amount: float, transaction_ref: str | None = None) -> Payment:
        if not transaction_ref:
            raise ValueError("Mobile banking requires a valid electronic transaction reference ID.")

        if not self._simulate_wallet_verification(transaction_ref, amount):
            raise ValueError(f"Mobile transaction reference '{transaction_ref}' could not be verified.")

        return Payment(
            invoice_id=invoice.id,
            payment_method="MOBILE_BANKING",
            amount_paid=amount,
            transaction_ref=transaction_ref,
            status=PaymentStatus.SUCCESS.value,
        )


class PaymentProcessorFactory:
    """Creational Factory managing instantiation of payment channel processors."""

    _registry: dict[str, type[IPaymentProcessor]] = {
        "CASH": CashPaymentProcessor,
        "CARD": CardPaymentProcessor,
        "MOBILE_BANKING": MobileBankingPaymentProcessor,
    }

    @classmethod
    def register_processor(cls, method_name: str, processor_cls: type[IPaymentProcessor]):
        """Allows runtime extension for new payment methods conforming to Open/Closed Principle."""
        cls._registry[method_name.upper()] = processor_cls

    @classmethod
    def create_processor(cls, method: str) -> IPaymentProcessor:
        """Instantiates and returns the processor corresponding to requested payment method."""
        normalized = method.upper().strip()
        processor_class = cls._registry.get(normalized)
        if not processor_class:
            supported = list(cls._registry.keys())
            raise ValueError(f"Unsupported payment method '{method}'. Supported methods: {supported}")
        return processor_class()
