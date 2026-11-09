import React, { useEffect, useState, useCallback } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  ExternalLink,
  Info,
  Loader2,
  Lock,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  UserCheck,
} from 'lucide-react';
import { Payment, PaymentStatusCheck } from '../../types/payment';
import { capturePayment, getPaymentStatus } from '../../lib/api';

interface PayPalCheckoutProps {
  payment: Payment;
  onPaymentUpdated: (updated: Payment) => void;
}

export const PayPalCheckout: React.FC<PayPalCheckoutProps> = ({
  payment,
  onPaymentUpdated,
}) => {
  const clientId = import.meta.env.VITE_PAYPAL_CLIENT_ID || '';
  const [statusCheck, setStatusCheck] = useState<PaymentStatusCheck | null>(null);
  const [isCheckingStatus, setIsCheckingStatus] = useState<boolean>(false);
  const [isCapturing, setIsCapturing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Extract PayPal HATEOAS approval link from backend order metadata or status check
  const links = (payment.provider_metadata?.links as Array<{ rel: string; href: string }>) || [];
  const metadataApprovalLink = links.find((l) => l.rel === 'approve' || l.rel === 'payer-action')?.href;
  const rawApprovalUrl = statusCheck?.approval_url || metadataApprovalLink || '';

  // Validate approval URL is an authentic PayPal Sandbox endpoint
  const isValidSandboxUrl =
    rawApprovalUrl.startsWith('https://www.sandbox.paypal.com/') ||
    rawApprovalUrl.startsWith('https://sandbox.paypal.com/');

  const approvalUrl = isValidSandboxUrl ? rawApprovalUrl : null;

  // Query live payment lifecycle status from backend / PayPal
  const checkStatus = useCallback(async (quiet = false) => {
    if (!payment.id || payment.status === 'completed') return;
    if (!quiet) setIsCheckingStatus(true);
    setErrorMessage(null);
    try {
      const data = await getPaymentStatus(payment.id);
      setStatusCheck(data);
      if (data.internal_status === 'completed') {
        onPaymentUpdated({
          ...payment,
          status: 'completed',
          provider_capture_id: data.provider_capture_id,
        });
      }
    } catch (err: unknown) {
      if (!quiet) {
        setErrorMessage(
          err instanceof Error
            ? err.message
            : 'Unable to verify order status with PayPal Sandbox.'
        );
      }
    } finally {
      if (!quiet) setIsCheckingStatus(false);
    }
  }, [payment, onPaymentUpdated]);

  // Initial check on mount if payment is not already completed
  useEffect(() => {
    if (payment.status !== 'completed') {
      checkStatus(true);
    }
  }, [payment.id, payment.status, checkStatus]);

  // Open PayPal Sandbox Approval Window
  const handleOpenSandboxWindow = () => {
    setErrorMessage(null);
    if (!approvalUrl) {
      setErrorMessage('PayPal approval URL is missing or invalid. Please check your Sandbox configuration.');
      return;
    }

    const popup = window.open(
      approvalUrl,
      'PayPalSandboxPopup',
      'width=550,height=700,status=no,toolbar=no,menubar=no'
    );
    if (!popup || popup.closed || typeof popup.closed === 'undefined') {
      setErrorMessage(
        'Pop-up was blocked by browser. Please click "Open PayPal Window in New Tab" below.'
      );
    }
  };

  // Trigger server-to-server capture
  const handleCaptureOrder = async () => {
    setIsCapturing(true);
    setErrorMessage(null);
    try {
      const updated = await capturePayment(payment.id);
      setIsCapturing(false);
      onPaymentUpdated(updated);
    } catch (err: unknown) {
      setIsCapturing(false);
      const msg = err instanceof Error ? err.message : 'Payment capture failed.';
      setErrorMessage(msg);
      // Refresh status after failure to synchronize UI
      checkStatus(true);
    }
  };

  const isCompleted = payment.status === 'completed' || statusCheck?.stage === 'completed';
  const canCapture = Boolean(statusCheck?.can_capture);
  const isApproved = statusCheck?.stage === 'buyer_approved' || canCapture;

  return (
    <div className="rounded-2xl border border-blue-500/30 bg-blue-950/20 p-6 backdrop-blur-sm space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30 font-black text-sm">
            PP
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">PayPal Sandbox Checkout</h3>
            <span className="text-[11px] font-mono text-cyan-300">
              REST API v2 Orders & Capture • Merchant Authorized
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full border border-blue-500/40 bg-blue-950/80 px-2.5 py-0.5 text-[11px] font-mono text-blue-300 uppercase">
            SANDBOX MODE
          </span>
        </div>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="rounded-xl border border-rose-500/40 bg-rose-950/50 p-4 text-xs text-rose-300 flex items-start gap-2.5">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-rose-200">Payment Action Required</p>
            <p className="text-rose-300/90 leading-relaxed">{errorMessage}</p>
          </div>
        </div>
      )}

      {/* Missing Client ID Notice */}
      {!clientId && (
        <div className="rounded-xl border border-amber-500/40 bg-amber-950/30 p-4 space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-amber-300 flex items-center gap-1.5">
            <ShieldAlert className="h-4 w-4 text-amber-400" />
            <span>PayPal Client ID Not Set in Frontend</span>
          </div>
          <p className="text-xs text-amber-200/80 leading-relaxed">
            To enable PayPal Sandbox checkout, add your public Sandbox Client ID to{' '}
            <code className="rounded bg-slate-900 px-1 py-0.5 text-cyan-300 font-mono">frontend/.env</code> as{' '}
            <code className="font-mono text-cyan-300">VITE_PAYPAL_CLIENT_ID=your_sandbox_client_id</code>.
          </p>
          <div className="pt-1 text-[11px] text-slate-400 flex items-center gap-1.5">
            <Lock className="h-3.5 w-3.5 text-slate-400" />
            <span>The Client Secret remains strictly in backend configuration and is never exposed.</span>
          </div>
        </div>
      )}

      {/* COMPLETED STATE */}
      {isCompleted ? (
        <div className="rounded-xl border border-emerald-500/40 bg-emerald-950/30 p-6 text-center space-y-3">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="h-7 w-7" />
          </div>
          <div>
            <h4 className="text-base font-bold text-white">PayPal Payment Captured & Settled</h4>
            <p className="text-xs text-slate-300 mt-1">
              Payment was confirmed by PayPal REST API v2 and credited to the freelancer milestone balance.
            </p>
          </div>

          <div className="pt-2 grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-md mx-auto text-xs font-mono text-left">
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Settled Amount</span>
              <span className="text-emerald-400 font-bold text-sm">
                {payment.currency} {Number(payment.amount).toFixed(2)}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase">Capture ID</span>
              <span className="text-slate-200 font-bold text-xs truncate block" title={payment.provider_capture_id || 'COMPLETED'}>
                {payment.provider_capture_id || statusCheck?.provider_capture_id || 'COMPLETED'}
              </span>
            </div>
          </div>

          <div className="pt-2 text-[11px] text-slate-400 flex items-center justify-center gap-1.5">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <span>Transaction recorded in PostgreSQL database with immutable audit log</span>
          </div>
        </div>
      ) : (
        /* IN PROGRESS CHECKOUT WORKFLOW */
        <div className="space-y-5">
          {/* Order Details Card */}
          <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4 text-xs space-y-2.5 font-mono">
            <div className="flex justify-between items-center text-slate-400">
              <span>PayPal Order ID:</span>
              <span className="text-white font-bold tracking-wider">{payment.provider_order_id || 'Initializing...'}</span>
            </div>
            <div className="flex justify-between items-center text-slate-400">
              <span>Payment Amount:</span>
              <span className="text-emerald-400 font-bold text-sm">
                {payment.currency} {Number(payment.amount).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center text-slate-400">
              <span>Approval Status:</span>
              {isApproved ? (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-950/70 text-emerald-300 border border-emerald-500/40 text-[11px]">
                  <CheckCircle2 className="h-3 w-3" />
                  Buyer Approved
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-950/70 text-amber-300 border border-amber-500/40 text-[11px]">
                  <RefreshCw className={`h-3 w-3 ${isCheckingStatus ? 'animate-spin' : ''}`} />
                  Awaiting Buyer Approval
                </span>
              )}
            </div>
            {statusCheck?.payer_email && (
              <div className="flex justify-between items-center text-slate-400 pt-1 border-t border-slate-900">
                <span className="flex items-center gap-1">
                  <UserCheck className="h-3.5 w-3.5 text-cyan-400" />
                  Payer:
                </span>
                <span className="text-cyan-300 font-semibold">{statusCheck.payer_email}</span>
              </div>
            )}
          </div>

          {/* Workflow Stage Guidance */}
          {isCapturing ? (
            <div className="py-8 flex flex-col items-center justify-center text-slate-300 space-y-3 rounded-xl border border-blue-500/20 bg-blue-950/30">
              <Loader2 className="h-9 w-9 text-cyan-400 animate-spin" />
              <div className="text-center font-mono text-xs">
                <p className="font-bold text-white text-sm">Capturing PayPal Sandbox Order...</p>
                <p className="text-slate-400 text-[11px] mt-1">Executing server-to-server PayPal REST API v2 capture</p>
              </div>
            </div>
          ) : isApproved ? (
            /* STAGE: BUYER APPROVED -> CAPTURE READY */
            <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/30 p-5 space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />
                <div className="text-xs text-slate-300 space-y-1">
                  <p className="font-bold text-white text-sm">Buyer Approval Confirmed</p>
                  <p className="text-slate-300 leading-relaxed">
                    The PayPal Sandbox order has been approved by the buyer. Click below to verify amounts and execute the server-side capture.
                  </p>
                </div>
              </div>

              <div className="pt-2 flex flex-col sm:flex-row gap-3">
                <button
                  type="button"
                  onClick={handleCaptureOrder}
                  disabled={isCapturing}
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-emerald-950/50 transition-all cursor-pointer disabled:opacity-50"
                >
                  <ShieldCheck className="h-4 w-4" />
                  <span>Verify & Capture Payment ({payment.currency} {Number(payment.amount).toFixed(2)})</span>
                </button>

                <button
                  type="button"
                  onClick={() => checkStatus(false)}
                  disabled={isCheckingStatus}
                  className="flex items-center justify-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-xs font-semibold text-slate-300 hover:text-white hover:border-slate-600 transition-colors cursor-pointer"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${isCheckingStatus ? 'animate-spin' : ''}`} />
                  <span>Re-check Status</span>
                </button>
              </div>
            </div>
          ) : (
            /* STAGE: BUYER APPROVAL REQUIRED */
            <div className="rounded-xl border border-blue-500/30 bg-blue-950/40 p-5 space-y-4">
              <div className="flex items-start gap-3">
                <Info className="h-5 w-5 text-cyan-400 shrink-0 mt-0.5" />
                <div className="text-xs text-slate-300 space-y-1.5">
                  <p className="font-bold text-white text-sm">Complete Buyer Approval in PayPal Sandbox</p>
                  <ol className="list-decimal pl-4 space-y-1 text-slate-300 text-[11px] leading-relaxed">
                    <li>Click <strong>&quot;Continue to PayPal Sandbox&quot;</strong> below.</li>
                    <li>Log in with your <strong>Personal Sandbox buyer account</strong> credentials.</li>
                    <li>Review the milestone details ({payment.currency} {Number(payment.amount).toFixed(2)}) and click <strong>&quot;Complete Purchase&quot;</strong>.</li>
                    <li>Return here and click <strong>&quot;Check Approval Status&quot;</strong> to proceed to capture.</li>
                  </ol>
                </div>
              </div>

              <div className="pt-2 flex flex-col sm:flex-row gap-3">
                <button
                  type="button"
                  onClick={handleOpenSandboxWindow}
                  disabled={!approvalUrl}
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-[#0070BA] hover:bg-[#003087] px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-blue-950/50 transition-all cursor-pointer disabled:opacity-50"
                >
                  <ExternalLink className="h-4 w-4" />
                  <span>Continue to PayPal Sandbox</span>
                </button>

                <button
                  type="button"
                  onClick={() => checkStatus(false)}
                  disabled={isCheckingStatus}
                  className="flex items-center justify-center gap-2 rounded-xl border border-cyan-500/50 bg-cyan-950/40 hover:bg-cyan-900/40 px-5 py-3 text-xs font-semibold text-cyan-300 transition-colors cursor-pointer disabled:opacity-50"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${isCheckingStatus ? 'animate-spin' : ''}`} />
                  <span>{isCheckingStatus ? 'Checking...' : 'Check Approval Status'}</span>
                </button>
              </div>

              {approvalUrl && (
                <div className="text-center pt-1">
                  <a
                    href={approvalUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] text-cyan-400 hover:text-cyan-300 underline font-mono"
                  >
                    <span>Direct Sandbox Approval Link</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
