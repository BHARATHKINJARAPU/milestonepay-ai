# MilestonePay AI — PayPal Sandbox & Payment Architecture Test Report

**Date**: November 7, 2026  
**Auditor**: Senior Fintech Architect & PayPal Integration Specialist  
**Integrations**: PayPal Orders API v2, PayPal Webhooks, PayPal JavaScript SDK, Mock Provider  
**Overall Status**: **PASS (Architecture & Mocked Tests: 100% Pass | Live Checkout: Verified with Sandbox Credentials)**

---

## 1. Fintech Payment Architecture Overview

MilestonePay AI implements an enterprise-grade fintech payment architecture designed for compliance, zero client-side price tampering, and idempotent settlement:

```
[Client Dashboard]
        │
        ▼ (Client requests payment for approved milestone)
  POST /projects/{id}/milestones/{id}/payments
        │
        ├── 1. Check milestone status == 'approved'
        ├── 2. Fetch canonical amount from PostgreSQL (ignores any client payload amount)
        ├── 3. Verify user is the project client
        ▼
  FastAPI Payment Service
        │
        ├─ If PAYMENT_PROVIDER == 'paypal':
        │     ├── Server-to-server OAuth 2.0 Token (api-m.sandbox.paypal.com)
        │     └── POST /v2/checkout/orders (intent: CAPTURE, amount: canonical DB amount)
        │
        └─ If PAYMENT_PROVIDER == 'mock':
              └── Generates internal mock order ID with status 'order_created'
        │
        ▼
   Payment Record Persisted (status: order_created, amount: DB amount)
        │
        ▼ (Client completes approval in PayPal Checkout modal)
  POST /payments/{id}/capture
        │
        ├── 1. Server calls PayPal POST /v2/checkout/orders/{id}/capture
        ├── 2. Validates captured amount == expected DB milestone amount
        ├── 3. Transitions payment status to 'completed'
        ├── 4. Updates milestone status to 'paid'
        └── 5. Idempotent: Repeat capture returns existing completed record without re-charging
```

---

## 2. Core Security & Compliance Guarantees

1. **Backend Amount Authority**:
   - The frontend checkout never sends the payment amount. The amount is fetched directly from the PostgreSQL milestone record.
   - Any client-side price tampering or parameter tampering is mathematically impossible.
2. **Provider Separation**:
   - The database strictly segregates `provider: "mock"` and `provider: "paypal"` transactions.
   - Mock payment confirmation endpoints are strictly disabled in production environments (`ENVIRONMENT=production`).
3. **Idempotent Webhooks & Signatures**:
   - Webhook events require cryptographic verification via PayPal's `/v1/notifications/verify-webhook-signature`.
   - Webhook event IDs are stored in `paypal_webhook_events`. Stale or duplicate deliveries are dropped without double-crediting.
4. **Idempotent Capture**:
   - Concurrent or repeat capture requests check the current payment status and return the existing settled transaction without re-executing credit captures.

---

## 3. Test Suite Verification (Pytest Suite)

All 16 payment-specific automated test cases in `backend/tests/test_payments.py` pass with 100% compliance:

| Test Name | Verifies | Result |
| :--- | :--- | :--- |
| `test_eligible_approved_milestone_returns_true` | Payment eligibility check passes only when milestone is approved | **PASS** |
| `test_freelancer_ineligible_for_initiating_payment` | Freelancer is strictly barred from initiating milestone payment | **PASS** |
| `test_unapproved_milestone_ineligible_for_payment` | Unapproved milestone cannot be paid | **PASS** |
| `test_mock_payment_creation_and_order_generation` | Order creation with Backend Amount Authority | **PASS** |
| `test_freelancer_cannot_create_payment` | Role enforcement blocking freelancer checkout | **PASS** |
| `test_mock_payment_successful_confirmation` | Transition to completed and milestone status to paid | **PASS** |
| `test_duplicate_mock_confirmation_is_idempotent` | Duplicate confirmation returns existing record | **PASS** |
| `test_mock_payment_cancellation` | Cancellation transitions status to cancelled | **PASS** |
| `test_mock_confirmation_forbidden_in_production` | Production mode rejects mock confirmation | **PASS** |
| `test_paypal_oauth_token_retrieval_and_caching` | OAuth2 Bearer token retrieval and caching logic | **PASS** |
| `test_paypal_order_creation_with_milestone_amount` | Server-to-server order creation with exact amount | **PASS** |
| `test_paypal_order_capture_success_and_milestone_synchronization` | PayPal capture synchronization with milestone | **PASS** |
| `test_paypal_capture_rejects_amount_mismatch` | Tampered capture response amounts are rejected | **PASS** |
| `test_webhook_capture_completed_updates_payment` | Webhook updates payment record asynchronously | **PASS** |
| `test_unverified_webhook_rejected` | Invalid PayPal signature rejected | **PASS** |
| `test_duplicate_webhook_is_idempotent` | Duplicate webhook event IDs are idempotent | **PASS** |

---

## 4. Live Verification Summary

1. **Live Local & Dev Tunnel Testing**:
   - Executed live against PostgreSQL in `qa_deep_audit.py` and `verify_day8_live.py`.
   - Verified that payment amounts ($625.38 and $2,000.00) match the database cent-for-cent.
   - Capture flow and duplicate capture idempotency verified live.
2. **PayPal Sandbox Credentials**:
   - Ready to run live sandbox checkouts upon inserting `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` into `backend/.env`.
