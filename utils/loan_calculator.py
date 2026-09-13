import math
from typing import Dict, Any, List

LENDER_CATALOG = [
    {
        "id": "sbi",
        "bank_name": "SBI Global Ed-Vantage",
        "tag": "Lowest Public Sector Interest",
        "rate": 10.15,
        "max_loan_inr": 15000000,
        "processing_fee_pct": 0.0,
        "collateral_required": "Required for > ₹75L",
        "turnaround_days": "10-14 days",
        "margin_money_pct": 10,
        "tax_benefit_80e": True,
        "features": ["100% Tax deduction on interest under Sec 80E", "No processing charges", "Repayment up to 15 years"]
    },
    {
        "id": "hdfc_credila",
        "bank_name": "HDFC Credila",
        "tag": "Most Popular Private NBFC",
        "rate": 10.50,
        "max_loan_inr": 7500000,
        "processing_fee_pct": 1.0,
        "collateral_required": "Required for > ₹45L",
        "turnaround_days": "4-6 days",
        "margin_money_pct": 0,
        "tax_benefit_80e": True,
        "features": ["Doorstep service & fast sanction", "Loan sanction before I-20 / Visa", "Covers 100% of living expenses"]
    },
    {
        "id": "icici",
        "bank_name": "ICICI Bank Education Loan",
        "tag": "Fast Digital Approval",
        "rate": 10.85,
        "max_loan_inr": 10000000,
        "processing_fee_pct": 0.75,
        "collateral_required": "Required for > ₹50L",
        "turnaround_days": "3-5 days",
        "margin_money_pct": 5,
        "tax_benefit_80e": True,
        "features": ["Pre-visa disbursement guarantee", "Digital paperless application", "Preferential rates for premier institutes"]
    },
    {
        "id": "axis",
        "bank_name": "Axis Bank",
        "tag": "Competitive Private Lender",
        "rate": 11.25,
        "max_loan_inr": 7500000,
        "processing_fee_pct": 0.50,
        "collateral_required": "Required for > ₹40L",
        "turnaround_days": "5-7 days",
        "margin_money_pct": 5,
        "tax_benefit_80e": True,
        "features": ["No pre-payment penalties", "Covers tuition, exam fees, study gear", "Multi-currency disbursement"]
    },
    {
        "id": "avanse",
        "bank_name": "Avanse Financial Services",
        "tag": "High Non-Collateral Flexibility",
        "rate": 11.75,
        "max_loan_inr": 7500000,
        "processing_fee_pct": 1.25,
        "collateral_required": "Flexible / Non-collateral up to ₹50L",
        "turnaround_days": "3-4 days",
        "margin_money_pct": 0,
        "tax_benefit_80e": True,
        "features": ["Quick unsecured approvals", "Customized tenure & grace periods", "Co-applicant income flexibility"]
    },
    {
        "id": "incred",
        "bank_name": "InCred Education",
        "tag": "100% Unsecured Specialist",
        "rate": 12.25,
        "max_loan_inr": 6000000,
        "processing_fee_pct": 1.50,
        "collateral_required": "No Collateral Required",
        "turnaround_days": "2-3 days",
        "margin_money_pct": 0,
        "tax_benefit_80e": False,
        "features": ["Completely collateral-free", "Fast 48-hour conditional approval", "Simple KYC documentation"]
    }
]

def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Computes standard monthly EMI: P * r * (1+r)^n / ((1+r)^n - 1)"""
    if principal <= 0 or tenure_months <= 0:
        return 0.0
    monthly_rate = annual_rate / 100.0 / 12.0
    factor = (1.0 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * (factor / (factor - 1.0))
    return round(emi)

def get_loan_options(principal: float, tenure_years: int = 10, has_collateral: bool = False, co_income: float = 800000) -> Dict[str, Any]:
    tenure_months = tenure_years * 12
    offers = []

    for lender in LENDER_CATALOG:
        emi = calculate_emi(principal, lender["rate"], tenure_months)
        total_payment = emi * tenure_months
        total_interest = total_payment - principal
        proc_fee = round(principal * (lender["processing_fee_pct"] / 100.0))

        # Eligibility check
        eligible = True
        reason = "Eligible for pre-approval"

        if not has_collateral and "Required" in lender["collateral_required"] and principal > 4500000:
            eligible = False
            reason = "Requires tangible property collateral above ₹45L"
        elif principal > lender["max_loan_inr"]:
            eligible = False
            reason = f"Loan amount exceeds lender cap of ₹{lender['max_loan_inr']/100000:.0f}L"

        offers.append({
            **lender,
            "emi": f"₹{emi:,.0f}",
            "emi_raw": emi,
            "total_payment": f"₹{total_payment/100000:.1f}L",
            "total_interest": f"₹{total_interest/100000:.1f}L",
            "processing_fee_amount": f"₹{proc_fee:,.0f}",
            "eligible": eligible,
            "status_reason": reason
        })

    # Sort offers: lowest rate first
    offers.sort(key=lambda x: x["rate"])

    return {
        "principal": principal,
        "principal_formatted": f"₹{principal/100000:.1f}L",
        "tenure_years": tenure_years,
        "tenure_months": tenure_months,
        "offers": offers
    }
