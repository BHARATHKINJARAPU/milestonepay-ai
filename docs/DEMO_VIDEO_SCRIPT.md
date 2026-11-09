# MilestonePay AI — Demo Video Script & Recording Guide
**PayPal AI Hackathon Submission**  
**Target Video Duration:** 2 minutes 45 seconds (165 seconds)

---

## 1. Demo Video Overview

This script is engineered specifically for hackathon judges evaluating the **PayPal AI Hackathon**. It demonstrates how MilestonePay AI bridges the trust and clarity gap in freelancing by uniting **Google Gemini 2.5 Flash** for milestone generation and deliverable evaluation with **PayPal Sandbox Checkout** for secure, instantaneous milestone settlement.

---

## 2. Timed Scene-by-Scene Script

| Timestamp | Visual Cue / Screen Action | Spoken Voiceover (Presenter) |
|---|---|---|
| **0:00 - 0:20** *(20s)* | **Title Slide & Hero Landing Page:**<br>• Show landing page at `http://localhost:5173`.<br>• Highlight tagline: *"Work Smarter. Deliver Transparently. Get Paid Confidently."*<br>• Quick montage of the problem: Freelance scope creep, delayed milestone releases, and subjective disputes. | *"Every year, freelancers and clients lose millions of dollars and thousands of hours to one recurring problem: ambiguous project scopes that spiral into endless revisions and unpaid invoices.<br><br>Introducing **MilestonePay AI** — the intelligent freelance management platform powered by Google Gemini and PayPal that converts vague ideas into crystal-clear milestones and guarantees transparent, automated milestone settlement."* |
| **0:20 - 0:45** *(25s)* | **Project Creation & Natural Language Prompt:**<br>• Client logs into dashboard.<br>• Clicks **+ New Project**.<br>• Pastes an unstructured, messy client brief into the description box ($4,500 budget).<br>• Invites freelancer via email. | *"Let's see it in action. A client creates a new project with a messy, unstructured brief: 'Build us a modern fintech web dashboard with dark mode, interactive charts, and PayPal checkout.'<br><br>Normally, this invites scope creep. But with MilestonePay AI, the client invites their freelancer and taps into the power of Gemini."* |
| **0:45 - 1:15** *(30s)* | **Gemini AI Milestone Generation & Bilateral Lock:**<br>• Clicks **Generate Milestones with Gemini AI**.<br>• Watch Gemini decompose the brief in real-time into 2 structured milestones with explicit deliverables and acceptance criteria.<br>• Highlight exact budget breakdown summing to 100%.<br>• Show Freelancer approving and Client approving to lock the contract. | *"With one click, Google Gemini analyzes the unstructured requirements, decomposing them into a 2-phase roadmap with explicit, measurable acceptance criteria, timelines, and exact budget allocations totaling 100%.<br><br>Crucially, to protect both parties, work is locked until both client and freelancer review and approve the proposal. Once both sign off, the agreement is legally immutable and milestones become active."* |
| **1:15 - 1:45** *(30s)* | **Deliverable Submission & Multimodal AI Evaluation:**<br>• Switch to Freelancer window.<br>• Open Milestone 1 and submit work with proof (Figma link, design tokens, PDF summary).<br>• Hit **Submit for AI Evaluation**.<br>• Show AI Audit Card: 95% Confidence, objective criterion-by-criterion check, strengths, and recommendations. | *"Now the freelancer executes Milestone 1 and submits work with evidence artifacts: Figma prototypes and architecture tokens.<br><br>Instantly, Gemini performs an objective multimodal evaluation against the agreed acceptance criteria. It scores completion confidence at 95%, itemizes which criteria were met, and delivers an objective audit report accessible to both parties. No guesswork. No subjective arguments."* |
| **1:45 - 2:20** *(35s)* | **Client Approval & PayPal Sandbox Checkout:**<br>• Client reviews AI audit report and clicks **Approve Deliverable**.<br>• Milestone status changes to `APPROVED`.<br>• Click **Release Payment ($2,000.00)**.<br>• PayPal Checkout Modal opens with official PayPal Smart Buttons.<br>• Authenticate with PayPal Sandbox buyer account.<br>• Click **Pay Now** and show real-time capture. | *"The client reviews the verified deliverable and clicks Approve. Milestone 1 is now eligible for payment.<br><br>The client clicks Release Payment. The PayPal checkout modal launches with official PayPal Smart Buttons. Behind the scenes, our FastAPI backend controls all monetary amounts directly from PostgreSQL to prevent tampering.<br><br>The client logs into PayPal Sandbox, authorizes the $2,000 payment, and our backend immediately captures the order via PayPal REST API v2, issuing instant settlement."* |
| **2:20 - 2:45** *(25s)* | **Settlement, Real-Time Notifications & Analytics:**<br>• Show instant receipt modal.<br>• Freelancer receives real-time notification: *"Payment Released!"*<br>• Project Activity Timeline updates with settlement audit trail.<br>• Show Dashboard Analytics with updated earnings and completed milestones.<br>• Closing slide with GitHub repo & hackathon badges. | *"Within seconds, the transaction settles. The freelancer receives an instant notification, the milestone is marked PAID, and the project activity timeline logs the immutable audit event.<br><br>MilestonePay AI combines the intelligence of Google Gemini with the trust and scale of PayPal to create the future of freelance work. Transparent scopes. Objective verification. Guaranteed payouts. Thank you!"* |

---

## 3. Video Recording Checklist

### Pre-Recording Setup:
1. **Screen Resolution:** 1920x1080 (1080p 60fps recommended).
2. **Browsers:**
   - Window 1: Chrome (Regular) — Client account logged in.
   - Window 2: Chrome (Incognito / Side-by-side) — Freelancer account logged in.
3. **Local Services Running:**
   - PostgreSQL daemon active on port `5432`.
   - FastAPI backend running on `http://127.0.0.1:8000`.
   - Vite frontend running on `http://localhost:5173`.
4. **PayPal Sandbox Credentials Prepared:**
   - Personal Sandbox Buyer: `personal-buyer@sandbox.paypal.com`
   - Password ready in clipboard for fast entry.
5. **Clean Data State:** Run tests or use a fresh test project for a crisp, spotless timeline.
6. **Audio Quality:** Clear external microphone, no background fan or typing noise.

