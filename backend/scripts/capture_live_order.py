"""
CLI Helper to capture the live PayPal Sandbox payment once approved by buyer.
"""
import asyncio
import os
import sys

os.environ.setdefault("PSYCOPG_IMPL", "python")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.payment import Payment
from app.models.enums import PaymentStatus
from app.models.user import User
from app.services.payments.payment_service import payment_service


async def capture_live_order():
    db = SessionLocal()
    try:
        # Target specific payment or default to live verified sandbox order
        target_id = sys.argv[1] if len(sys.argv) > 1 else "c51ca6d4-87b5-4553-ba4d-c8a9d5895cfa"
        p = db.query(Payment).filter(Payment.id == target_id).first()
        if not p:
            # Fallback to most recent live sandbox order
            p = (
                db.query(Payment)
                .filter(
                    Payment.provider == "paypal",
                    Payment.provider_order_id.like("9%"),
                )
                .order_by(Payment.created_at.desc())
                .first()
            )
        if not p:
            print("No PayPal payment found.")
            return

        client_user = db.query(User).filter(User.id == p.client_user_id).first()
        print(f"Attempting capture for Payment ID: {p.id}")
        print(f"PayPal Order ID: {p.provider_order_id}")
        print(f"Amount: {p.currency} {p.amount}")
        print(f"Status before capture: {p.status.value}")

        try:
            updated = await payment_service.capture_milestone_payment(
                payment_id=p.id,
                current_user=client_user,
                db=db,
            )
            print("=" * 60)
            print("PAYPAL ORDER CAPTURED SUCCESSFULLY!")
            print("=" * 60)
            print(f"Payment Status:        {updated.status.value}")
            print(f"Provider Capture ID:   {updated.provider_capture_id}")
            print(f"Completed At:          {updated.completed_at}")
            print(f"Milestone Status:      {updated.milestone.status.value}")
            print(f"Milestone Payment:     {updated.milestone.payment_status.value}")
        except Exception as e:
            print("\nCapture result:")
            print(e)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(capture_live_order())
