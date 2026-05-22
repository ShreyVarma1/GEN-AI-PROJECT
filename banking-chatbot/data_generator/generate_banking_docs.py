"""
Synthetic Banking Document Generator
Generates 5 realistic banking documents for RAG seeding.
Run: python data_generator/generate_banking_docs.py
"""
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "sample_docs")


def write_doc(filename: str, content: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {filepath}")


PERSONAL_LOANS_FAQ = """PERSONAL LOANS - FREQUENTLY ASKED QUESTIONS
============================================

1. ELIGIBILITY & BASICS
------------------------

Q: Who is eligible for a personal loan?
A: Salaried individuals aged 21–60 years with a minimum monthly income of Rs. 25,000 are eligible. Self-employed professionals aged 25–65 with a minimum annual income of Rs. 3,00,000 may also apply. A CIBIL score of 700 or above is required for standard rates.

Q: What is the minimum and maximum loan amount?
A: Personal loans are available from Rs. 50,000 to Rs. 40,00,000 depending on your income, credit profile, and repayment capacity.

Q: What is the loan tenure?
A: Loan tenure ranges from 12 months to 60 months (1 to 5 years). Longer tenures result in lower EMIs but higher total interest paid.

Q: How quickly will my loan be disbursed?
A: For pre-approved customers, disbursement happens within 4 hours of document submission. For new applicants, disbursement typically takes 2–5 working days after document verification and approval.

2. INTEREST RATES & FEES
-------------------------

Q: What are the interest rates on personal loans?
A: Interest rates range from 10.5% to 24% per annum depending on your credit score, income, employer category, and loan amount. Customers with CIBIL scores above 750 qualify for the lowest rates starting at 10.5% p.a.

Q: What is the processing fee?
A: A one-time processing fee of 1%–3% of the loan amount (minimum Rs. 999, maximum Rs. 15,000) plus applicable GST is charged. This is deducted from the disbursed amount.

Q: Are there any prepayment charges?
A: Prepayment is allowed after 6 EMIs. Prepayment charges are 2%–4% of the outstanding principal plus GST. Foreclosure (full prepayment) charges are 4% of outstanding principal plus GST.

Q: Is there a late payment penalty?
A: Yes. A late payment charge of 2% per month on the overdue EMI amount is levied if payment is not received within 3 days of the due date.

3. EMI CALCULATION
-------------------

Q: How is my EMI calculated?
A: EMI = [P × R × (1+R)^N] / [(1+R)^N – 1], where P = Principal, R = Monthly interest rate (Annual rate / 12 / 100), N = Number of months.

Example: For a loan of Rs. 5,00,000 at 12% p.a. for 36 months:
- Monthly rate R = 12/12/100 = 0.01
- EMI = [5,00,000 × 0.01 × (1.01)^36] / [(1.01)^36 – 1]
- EMI ≈ Rs. 16,607

Q: Can I change my EMI date?
A: Yes, you can request an EMI date change once per year. Allowed dates are 1st, 5th, 10th, 15th, or 25th of each month.

4. DOCUMENTATION REQUIRED
--------------------------

Q: What documents are needed for a personal loan application?
A: The following documents are required:
- Identity Proof: Aadhaar Card, PAN Card, Passport, or Voter ID
- Address Proof: Aadhaar Card, Utility Bill (not older than 3 months), Rental Agreement
- Income Proof (Salaried): Last 3 months' salary slips, 6 months' bank statements, Form 16
- Income Proof (Self-employed): Last 2 years' ITR with computation, 12 months' bank statements, business registration proof
- Passport-size photographs (2 copies)

Q: Is a guarantor required?
A: A guarantor is not required for standard personal loans. However, for applicants with CIBIL scores between 650–699, a co-applicant or guarantor may be requested.

5. LOAN MANAGEMENT
-------------------

Q: How can I check my loan balance and EMI schedule?
A: Log in to our mobile app or internet banking portal. Navigate to 'My Loans' to view outstanding balance, EMI schedule, and payment history.

Q: Can I get a top-up loan on my existing personal loan?
A: Yes, after 12 months of regular repayment with no defaults, you may be eligible for a top-up loan of up to 50% of the original loan amount.

Q: What happens if I miss an EMI?
A: Missing an EMI triggers a late payment charge. After 3 consecutive missed EMIs, the account is classified as NPA (Non-Performing Asset), which severely impacts your CIBIL score and may lead to legal recovery proceedings.

Q: How do I apply for a personal loan?
A: You can apply through: (1) Our mobile app, (2) Internet banking portal, (3) Visiting any branch, (4) Calling our helpline at 1800-XXX-XXXX. Online applications receive faster processing.

6. SPECIAL SCHEMES
-------------------

Q: Are there any special personal loan schemes?
A: Yes, we offer:
- Salary Advance Loan: Up to 3 months' salary for salaried customers, disbursed in 2 hours
- Festival Loan: Special rates during Diwali, Eid, and Christmas — rates starting at 9.99% p.a.
- Medical Emergency Loan: Disbursed within 6 hours for medical emergencies with minimal documentation
- Education Loan (Personal): For professional courses, up to Rs. 10,00,000 at 11% p.a.
"""


CREDIT_CARD_POLICY = """CREDIT CARD POLICY & TERMS
============================

1. CARD TYPES & ELIGIBILITY
-----------------------------

Classic Card:
- Annual fee: Rs. 500 (waived on annual spend of Rs. 50,000)
- Credit limit: Rs. 25,000 – Rs. 1,00,000
- Eligibility: Minimum monthly income Rs. 20,000, CIBIL score 700+
- Reward points: 1 point per Rs. 100 spent

Gold Card:
- Annual fee: Rs. 1,000 (waived on annual spend of Rs. 1,00,000)
- Credit limit: Rs. 1,00,000 – Rs. 3,00,000
- Eligibility: Minimum monthly income Rs. 40,000, CIBIL score 720+
- Reward points: 2 points per Rs. 100 spent; 3x on dining and travel

Platinum Card:
- Annual fee: Rs. 2,500 (waived on annual spend of Rs. 2,50,000)
- Credit limit: Rs. 3,00,000 – Rs. 7,00,000
- Eligibility: Minimum monthly income Rs. 75,000, CIBIL score 750+
- Reward points: 3 points per Rs. 100 spent; 5x on international transactions
- Benefits: Airport lounge access (4 visits/year), travel insurance up to Rs. 50 lakhs

Infinite Card:
- Annual fee: Rs. 10,000 (waived on annual spend of Rs. 10,00,000)
- Credit limit: Rs. 7,00,000 – Rs. 25,00,000 (by invitation only)
- Eligibility: Minimum monthly income Rs. 2,00,000, CIBIL score 780+
- Reward points: 5 points per Rs. 100 spent; 10x on luxury brands
- Benefits: Unlimited airport lounge access, concierge service, golf privileges

2. INTEREST & CHARGES
-----------------------

Q: What is the interest rate on revolving credit?
A: If you do not pay the full outstanding amount by the due date, interest is charged at 3.5% per month (42% per annum) on the revolving balance from the transaction date.

Q: What is the minimum payment due?
A: The minimum payment due is 5% of the total outstanding balance or Rs. 500, whichever is higher. Paying only the minimum amount will result in interest charges on the remaining balance.

Q: What are the late payment charges?
A: Late payment charges based on outstanding balance:
- Up to Rs. 500: Rs. 100
- Rs. 501 – Rs. 5,000: Rs. 400
- Rs. 5,001 – Rs. 10,000: Rs. 600
- Rs. 10,001 – Rs. 25,000: Rs. 800
- Rs. 25,001 – Rs. 50,000: Rs. 1,100
- Above Rs. 50,000: Rs. 1,300

Q: What is the cash advance fee?
A: Cash advances attract a fee of 2.5% of the amount withdrawn (minimum Rs. 300) plus interest at 3.5% per month from the date of withdrawal. There is no interest-free period on cash advances.

Q: What is the foreign currency transaction fee?
A: A markup fee of 3.5% is charged on all foreign currency transactions. This is in addition to the exchange rate applied by the card network (Visa/Mastercard).

3. REWARD POINTS
-----------------

Q: How do I redeem reward points?
A: Reward points can be redeemed through:
- Our mobile app or internet banking portal
- Catalogue redemption (merchandise, vouchers)
- Statement credit (100 points = Rs. 25 credit)
- Air miles conversion (100 points = 1 air mile with partner airlines)
- Minimum redemption: 500 points

Q: Do reward points expire?
A: Reward points are valid for 3 years from the date of earning. Points earned in a calendar year expire on December 31st of the third subsequent year.

4. FRAUD PROTECTION & SECURITY
--------------------------------

Q: What should I do if my card is lost or stolen?
A: Immediately call our 24/7 helpline at 1800-XXX-XXXX to block your card. You can also block your card instantly through the mobile app. Zero liability protection applies for fraudulent transactions reported within 7 days.

Q: What is the zero liability policy?
A: You are not liable for unauthorized transactions if: (1) You report the loss/theft promptly, (2) The fraud was not due to your negligence, (3) You have not shared your PIN or OTP with anyone.

Q: How does the bank protect against online fraud?
A: All online transactions require OTP (One-Time Password) authentication via registered mobile number. International online transactions require additional 3D Secure verification.

5. CREDIT LIMIT MANAGEMENT
----------------------------

Q: How can I increase my credit limit?
A: Submit a credit limit enhancement request through the mobile app or branch. Eligibility is reviewed based on income, repayment history, and credit score. Limit enhancements are processed within 7 working days.

Q: Can I set spending limits on my card?
A: Yes, you can set daily transaction limits, online transaction limits, and international usage limits through the mobile app.
"""


HOME_LOAN_GUIDE = """HOME LOAN GUIDE - COMPLETE INFORMATION
========================================

1. OVERVIEW & ELIGIBILITY
---------------------------

Our home loans are designed to help you purchase, construct, or renovate your dream home. We offer competitive interest rates with flexible repayment options.

Eligibility Criteria:
- Age: 21–65 years (loan must be repaid before age 70)
- Employment: Salaried (minimum 2 years of employment, 1 year with current employer) or Self-employed (minimum 3 years in business)
- Minimum Income: Rs. 25,000/month (salaried) or Rs. 3,00,000/year (self-employed)
- CIBIL Score: Minimum 650 (best rates for 750+)
- Property: Must be in approved locations; clear title required

2. LOAN AMOUNT & LTV RATIO
---------------------------

Loan-to-Value (LTV) Ratio:
- Loans up to Rs. 30 lakhs: Up to 90% of property value
- Loans Rs. 30 lakhs – Rs. 75 lakhs: Up to 80% of property value
- Loans above Rs. 75 lakhs: Up to 75% of property value

Maximum Loan Amount: Rs. 5 crores (higher amounts considered case-by-case)
Minimum Loan Amount: Rs. 5 lakhs

3. INTEREST RATES
------------------

Fixed Rate Home Loans:
- Rate: 8.75% – 9.50% p.a. (fixed for 2, 5, or 10 years, then converts to floating)
- Suitable for: Customers who prefer payment certainty

Floating Rate Home Loans (linked to RLLR - Repo Linked Lending Rate):
- Current RLLR: 8.50% p.a. (subject to RBI repo rate changes)
- Spread: 0.25% – 1.50% above RLLR based on credit profile
- Effective rate: 8.75% – 10.00% p.a.
- Suitable for: Customers who can benefit from rate reductions

4. DOCUMENTATION CHECKLIST
----------------------------

For Salaried Applicants:
- Identity & Address Proof: Aadhaar, PAN, Passport
- Income Documents: Last 3 months' salary slips, 6 months' bank statements, Form 16 (last 2 years), employment letter
- Property Documents: Sale agreement, title deed, approved building plan, NOC from builder/society, property tax receipts

For Self-Employed Applicants:
- Identity & Address Proof: Aadhaar, PAN, Passport
- Income Documents: Last 3 years' ITR with computation, CA-certified balance sheet and P&L, 12 months' bank statements
- Business Proof: GST registration, business license, partnership deed (if applicable)
- Property Documents: Same as salaried applicants

5. PROCESSING & TIMELINE
--------------------------

Step 1 - Application Submission: 1 day
Step 2 - Document Verification: 2–3 working days
Step 3 - Legal Verification of Property: 5–7 working days
Step 4 - Technical Valuation of Property: 3–5 working days
Step 5 - Credit Appraisal & Sanction: 3–5 working days
Step 6 - Loan Agreement Execution: 1–2 days
Step 7 - Disbursement: 1–2 days after agreement

Total Timeline: Approximately 15–25 working days from complete document submission.

Processing Fee: 0.5%–1% of loan amount plus GST (non-refundable after sanction)

6. PMAY SUBSIDY (PRADHAN MANTRI AWAS YOJANA)
----------------------------------------------

Under PMAY Credit Linked Subsidy Scheme (CLSS):
- EWS/LIG (Annual income up to Rs. 6 lakhs): 6.5% interest subsidy on loans up to Rs. 6 lakhs
- MIG-I (Annual income Rs. 6–12 lakhs): 4% interest subsidy on loans up to Rs. 9 lakhs
- MIG-II (Annual income Rs. 12–18 lakhs): 3% interest subsidy on loans up to Rs. 12 lakhs

Subsidy is credited upfront to the loan account, reducing the principal. First-time homebuyers only.

7. TAX BENEFITS
----------------

Section 80C: Principal repayment up to Rs. 1.5 lakhs per year is deductible from taxable income.

Section 24(b): Interest paid on home loan is deductible:
- Self-occupied property: Up to Rs. 2 lakhs per year
- Let-out property: Full interest amount deductible (no limit)

Section 80EEA: Additional deduction of Rs. 1.5 lakhs for first-time homebuyers on affordable housing (stamp duty value up to Rs. 45 lakhs).

8. PREPAYMENT & FORECLOSURE
-----------------------------

Floating Rate Loans: No prepayment or foreclosure charges (as per RBI guidelines).
Fixed Rate Loans: Prepayment charge of 2% on the amount prepaid if prepaid from own funds; 4% if refinanced from another institution.

Partial prepayment: Minimum Rs. 10,000. Can be done anytime after 6 months of loan disbursement.
"""


BANKING_GENERAL_FAQ = """GENERAL BANKING FAQ
====================

1. ACCOUNT TYPES
-----------------

Q: What types of savings accounts do you offer?
A: We offer the following savings account types:
- Basic Savings Account: Zero minimum balance, basic features, free debit card
- Regular Savings Account: Minimum balance Rs. 5,000 (metro/urban), Rs. 2,000 (semi-urban/rural), interest rate 3.5% p.a.
- Premium Savings Account: Minimum balance Rs. 25,000, higher interest rate 4% p.a., free RTGS/NEFT, dedicated relationship manager
- Senior Citizen Account: For customers aged 60+, higher FD rates (+0.50%), priority service
- Salary Account: Zero minimum balance, linked to employer, free unlimited ATM transactions

Q: What is the interest rate on savings accounts?
A: Standard savings accounts earn 3.5% p.a. on daily balance. Premium accounts earn 4% p.a. Interest is credited quarterly.

2. KYC PROCESS
---------------

Q: What is KYC and why is it required?
A: KYC (Know Your Customer) is a mandatory RBI requirement to verify customer identity and prevent financial fraud and money laundering.

Q: What documents are accepted for KYC?
A: Officially Valid Documents (OVDs) accepted:
- Identity Proof: Aadhaar Card, PAN Card, Passport, Voter ID, Driving License
- Address Proof: Aadhaar Card, Passport, Utility Bills (electricity/water/gas, not older than 3 months), Bank Statement, Rental Agreement

Q: How often is KYC renewal required?
A: KYC renewal frequency based on risk category:
- Low Risk customers: Every 10 years
- Medium Risk customers: Every 8 years
- High Risk customers: Every 2 years

3. FUND TRANSFER LIMITS & CHARGES
-----------------------------------

NEFT (National Electronic Funds Transfer):
- Minimum: Rs. 1 (no minimum)
- Maximum: No upper limit (subject to account limits)
- Charges: Free for online transactions; Rs. 2–25 for branch transactions based on amount
- Timing: Available 24x7 (processed in half-hourly batches)

RTGS (Real Time Gross Settlement):
- Minimum: Rs. 2,00,000
- Maximum: No upper limit
- Charges: Free for online transactions; Rs. 25–50 for branch transactions
- Timing: Available 24x7

IMPS (Immediate Payment Service):
- Minimum: Rs. 1
- Maximum: Rs. 5,00,000 per transaction
- Charges: Free up to Rs. 1,000; Rs. 5 for Rs. 1,001–1 lakh; Rs. 15 for above Rs. 1 lakh
- Timing: 24x7, instant transfer

UPI (Unified Payments Interface):
- Maximum: Rs. 1,00,000 per transaction (Rs. 2,00,000 for verified merchants)
- Charges: Free
- Timing: 24x7, instant

4. FIXED DEPOSITS
------------------

Q: What are the current FD interest rates?
A: Fixed Deposit rates (per annum):
- 7–14 days: 3.50%
- 15–29 days: 4.00%
- 30–45 days: 4.50%
- 46–90 days: 5.00%
- 91–180 days: 5.75%
- 181 days – 1 year: 6.25%
- 1 year – 2 years: 6.75%
- 2 years – 3 years: 7.00%
- 3 years – 5 years: 7.25%
- 5 years – 10 years: 7.00%
Senior Citizens receive an additional 0.50% on all tenures.

Q: What is the minimum FD amount?
A: Minimum FD amount is Rs. 1,000. There is no maximum limit.

Q: Can I break my FD before maturity?
A: Yes, premature withdrawal is allowed with a penalty of 1% on the applicable rate. Tax Saver FDs (5-year lock-in) cannot be broken prematurely.

5. NOMINATION
--------------

Q: How do I add or change a nominee?
A: You can add/change a nominee through: (1) Mobile app → Account Settings → Nomination, (2) Internet banking → Services → Nomination, (3) Visiting any branch with Form DA1.

Q: Can I have multiple nominees?
A: Yes, you can have up to 3 nominees with specified percentage shares. Total must equal 100%.

6. GRIEVANCE REDRESSAL
-----------------------

Q: How do I register a complaint?
A: Complaints can be registered through:
- Mobile app: Help & Support → Raise a Complaint
- Email: customercare@bank.com
- Phone: 1800-XXX-XXXX (toll-free, 24x7)
- Branch: Submit written complaint to Branch Manager

Q: What are the resolution timelines?
A: As per RBI guidelines:
- Account-related queries: 3 working days
- Transaction disputes: 7 working days
- Loan-related complaints: 10 working days
- Complex complaints: 30 working days

If not resolved within 30 days, you may escalate to the Banking Ombudsman (RBI).
"""


CUSTOMER_SUPPORT_PROCEDURES = """CUSTOMER SUPPORT PROCEDURES & ESCALATION GUIDE
================================================

1. COMPLAINT REGISTRATION
--------------------------

How to Register a Complaint:
Customers can register complaints through multiple channels:

Channel 1 - Mobile App:
- Open the app → Tap 'Help & Support' → Select 'Raise a Complaint'
- Choose complaint category → Describe issue → Submit
- You will receive a Complaint Reference Number (CRN) via SMS and email

Channel 2 - Internet Banking:
- Login → Go to 'Service Requests' → 'New Complaint'
- Fill in details and submit → CRN generated immediately

Channel 3 - Phone Banking:
- Call 1800-XXX-XXXX (toll-free, available 24x7)
- IVR options: Press 1 for Account, Press 2 for Cards, Press 3 for Loans, Press 0 for Agent
- Average wait time: 3–5 minutes during business hours

Channel 4 - Branch Visit:
- Visit any branch during working hours (Mon–Sat, 10 AM – 4 PM)
- Submit written complaint to Branch Manager
- Receive acknowledgment receipt with CRN

Channel 5 - Email:
- Send to: customercare@bank.com
- Subject line format: [Complaint] - [Account Number] - [Issue Type]
- Response within 24 hours

2. SLA TIMELINES (SERVICE LEVEL AGREEMENTS)
--------------------------------------------

Priority 1 - Critical (Same Day Resolution):
- Unauthorized transactions / fraud
- Card blocked incorrectly
- Account frozen without notice
- ATM cash not dispensed but account debited

Priority 2 - High (1–3 Working Days):
- Failed fund transfers (NEFT/RTGS/IMPS)
- Incorrect charges or fees
- Cheque return issues
- Internet banking access problems

Priority 3 - Medium (3–7 Working Days):
- Statement discrepancies
- Address/contact update requests
- Nominee addition/change
- Cheque book requests

Priority 4 - Low (7–15 Working Days):
- General account queries
- Product information requests
- Feedback and suggestions

3. ESCALATION MATRIX
---------------------

Level 1 - Customer Service Representative:
- First point of contact
- Resolves standard queries and complaints
- Escalates if unresolved within SLA

Level 2 - Senior Customer Service Officer:
- Handles escalated complaints
- Authority to waive charges up to Rs. 2,000
- Contact: Escalate through app or ask for supervisor on phone

Level 3 - Branch Manager / Regional Grievance Officer:
- Handles complex disputes
- Authority to waive charges up to Rs. 10,000
- Contact: Visit branch or email regional.grievance@bank.com

Level 4 - Nodal Officer (Head Office):
- Final internal escalation
- Contact: nodalofficer@bank.com
- Response within 7 working days

Level 5 - Banking Ombudsman (RBI):
- External escalation if bank fails to resolve within 30 days
- Website: https://cms.rbi.org.in
- No fee for filing complaint

4. FRAUD REPORTING & CARD BLOCKING
------------------------------------

Immediate Card Block (24x7):
- Call: 1800-XXX-XXXX → Press 2 for Cards → Press 1 to Block
- Mobile App: Cards → Select Card → Block Card (instant)
- SMS: Send 'BLOCK XXXX' (last 4 digits) to 56161

What to Do If You Suspect Fraud:
Step 1: Immediately block your card (see above)
Step 2: Call fraud helpline: 1800-XXX-XXXX (dedicated fraud line, 24x7)
Step 3: File a complaint with CRN
Step 4: File a police complaint (FIR) for amounts above Rs. 10,000
Step 5: Submit fraud dispute form within 7 days for zero-liability protection

Chargeback Process:
- Raise dispute within 45 days of transaction date
- Provisional credit within 10 working days
- Final resolution within 45–90 days (as per card network timelines)

5. ACCOUNT FREEZE & UNFREEZE
------------------------------

Reasons for Account Freeze:
- Suspicious transaction patterns
- KYC non-compliance
- Court order or regulatory directive
- Customer request (self-freeze for security)

To Unfreeze Account:
- Visit home branch with valid KYC documents
- Submit written request with explanation
- Processing time: 1–3 working days for KYC-related freeze
- Court-ordered freeze: Requires court order reversal

Self-Freeze (Customer-Initiated):
- Available through mobile app for immediate security
- Can be reversed through app or branch visit
- Useful when card/credentials are suspected compromised

6. DISPUTE RESOLUTION PROCESS
-------------------------------

For Transaction Disputes:
1. Raise dispute within 45 days of transaction
2. Bank investigates with merchant/payment network
3. Provisional credit may be applied within 10 days
4. Final resolution communicated within 45 days

For Loan Disputes:
1. Submit written dispute with supporting documents
2. Loan department review within 10 working days
3. If unresolved, escalate to Nodal Officer
4. RBI Ombudsman as final recourse

For Credit Card Billing Disputes:
1. Raise dispute before payment due date to avoid interest
2. Disputed amount placed on hold (no interest during investigation)
3. Resolution within 30–45 days

7. CONTACT DIRECTORY
---------------------

General Customer Care: 1800-XXX-XXXX (24x7, toll-free)
Credit Card Helpline: 1800-XXX-YYYY (24x7, toll-free)
Loan Support: 1800-XXX-ZZZZ (Mon–Sat, 8 AM – 8 PM)
Fraud Reporting: 1800-XXX-XXXX (24x7, dedicated line)
NRI Services: +91-22-XXXX-XXXX
Email: customercare@bank.com
Nodal Officer: nodalofficer@bank.com
Website: www.bank.com
"""


def main():
    docs = [
        ("personal_loans_faq.txt", PERSONAL_LOANS_FAQ),
        ("credit_card_policy.txt", CREDIT_CARD_POLICY),
        ("home_loan_guide.txt", HOME_LOAN_GUIDE),
        ("banking_general_faq.txt", BANKING_GENERAL_FAQ),
        ("customer_support_procedures.txt", CUSTOMER_SUPPORT_PROCEDURES),
    ]
    for filename, content in docs:
        write_doc(filename, content)
    print(f"\nAll {len(docs)} documents generated in: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
