"""
Inspect live PayPal Sandbox order status and internal database state.
"""
import asyncio
import os
import sys

os.environ.setdefault("PSYCOPG_IMPL", "python")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.payment import Payment
from app.models.user import User
from app.services.payments.payment_service import payment_service


async def check_status():
    db = SessionLocal()
    try:
        target_id = sys.argv[1] if len(sys.argv) > 1 else "c51ca6d4-87b5-4553-ba4d-c8a9d5895cfa"
        p = db.query(Payment).filter(Payment.id == target_id).first()
        if not p:
            print(f"Payment {target_id} not found.")
            return

        client_user = db.query(User).filter(User.id == p.client_user_id).first()
        status_data = await payment_service.get_payment_lifecycle_status(
            payment_id=p.id,
            current_user=client_user,
            db=db,
        )

        print("=" * 60)
        print("LIVE PAYMENT STATUS INSPECTION")
        print("=" * 60)
        print(f"Payment ID:        {status_data['payment_id']}")
        print(f"PayPal Order ID:   {status_data['provider_order_id']}")
        print(f"Internal Status:   {status_data['internal_status'].value}")
        print(f"PayPal Status:     {status_data['provider_status']}")
        print(f"Lifecycle Stage:   {status_data['stage']}")
        print(f"Can Capture:       {status_data['can_capture']}")
        print(f"Approval URL:      {status_data['approval_url']}")
        print(f"Payer Email:       {status_data['payer_email']}")
        print(f"Payer ID:          {status_data['payer_id']}")
        print(f"Amount / Currency: {status_data['amount']} {status_data['currency']}")
        print(f"Capture ID:        {status_data['provider_capture_id']}")
        print("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(check_status())
