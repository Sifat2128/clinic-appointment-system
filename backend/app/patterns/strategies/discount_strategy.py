from abc import ABC, abstractmethod
from typing import Any

# Clinic Standard Discount Constants
STUDENT_DISCOUNT_PERCENTAGE = 0.18  # Revised standard student concession rate to 18%
SENIOR_DISCOUNT_PERCENTAGE = 0.20
INSURANCE_DISCOUNT_PERCENTAGE = 0.30
HEALTHCARE_TAX_RATE = 0.05


class IDiscountStrategy(ABC):
    """Abstract Strategy defining the contract for calculating consultation billing discounts."""

    @abstractmethod
    def get_discount_name(self) -> str:
        """Returns the canonical name of the discount category."""
        pass

    @abstractmethod
    def get_discount_percentage(self) -> float:
        """Returns the discount fraction (e.g. 0.15 for 15%)."""
        pass

    def calculate_discount(self, gross_amount: float) -> float:
        """Calculates monetary discount amount rounded to 2 decimal places."""
        return round(gross_amount * self.get_discount_percentage(), 2)


class NoDiscountStrategy(IDiscountStrategy):
    """Standard billing with no promotional or concessionary deduction (0%)."""

    def get_discount_name(self) -> str:
        return "NONE"

    def get_discount_percentage(self) -> float:
        return 0.0


class StudentDiscountStrategy(IDiscountStrategy):
    """Concessionary discount for verified students with valid academic ID."""

    def get_discount_name(self) -> str:
        return "STUDENT"

    def get_discount_percentage(self) -> float:
        return STUDENT_DISCOUNT_PERCENTAGE


class SeniorCitizenDiscountStrategy(IDiscountStrategy):
    """Concessionary discount for patients aged 60 and above."""

    def get_discount_name(self) -> str:
        return "SENIOR_CITIZEN"

    def get_discount_percentage(self) -> float:
        return SENIOR_DISCOUNT_PERCENTAGE


class InsuranceDiscountStrategy(IDiscountStrategy):
    """Direct billing concession for corporate or insured partners."""

    def get_discount_name(self) -> str:
        return "INSURANCE"

    def get_discount_percentage(self) -> float:
        return INSURANCE_DISCOUNT_PERCENTAGE


class BillingCalculationEngine:
    """Context executor that delegates calculation to an injected discount strategy."""

    def __init__(self, tax_rate: float = HEALTHCARE_TAX_RATE):
        self.tax_rate = tax_rate

    def calculate_bill(self, gross_amount: float, strategy: IDiscountStrategy) -> dict[str, Any]:
        """Computes gross fee, discount, taxable subtotal, tax, and net payable total."""
        discount_amount = strategy.calculate_discount(gross_amount)
        taxable_subtotal = round(max(0.0, gross_amount - discount_amount), 2)
        tax_amount = round(taxable_subtotal * self.tax_rate, 2)
        net_total = round(taxable_subtotal + tax_amount, 2)

        return {
            "gross_amount": gross_amount,
            "discount_type": strategy.get_discount_name(),
            "discount_percentage": strategy.get_discount_percentage(),
            "discount_amount": discount_amount,
            "taxable_subtotal": taxable_subtotal,
            "tax_amount": tax_amount,
            "net_total": net_total,
        }


def get_discount_strategy(discount_type: str) -> IDiscountStrategy:
    """Strategy resolver mapping string keys to strategy implementations."""
    mapping = {
        "NONE": NoDiscountStrategy,
        "STUDENT": StudentDiscountStrategy,
        "SENIOR_CITIZEN": SeniorCitizenDiscountStrategy,
        "INSURANCE": InsuranceDiscountStrategy,
    }
    strategy_cls = mapping.get(discount_type.upper(), NoDiscountStrategy)
    return strategy_cls()
