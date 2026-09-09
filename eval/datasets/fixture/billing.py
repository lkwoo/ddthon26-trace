"""Billing: invoices and payments for the fixture app."""


def create_invoice(customer_id: str, amount_cents: int) -> dict:
    """Create an invoice for a customer to charge a payment of the given amount."""
    return {
        "customer_id": customer_id,
        "amount_cents": amount_cents,
        "status": "unpaid",
    }


def mark_paid(invoice: dict) -> dict:
    """Mark an invoice as paid once the payment settles."""
    invoice["status"] = "paid"
    return invoice
