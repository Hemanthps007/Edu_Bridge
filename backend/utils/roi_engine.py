from typing import Dict, Any

def calculate_advanced_roi(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes detailed higher education ROI with comprehensive cost categories,
    tax deductions, break-even payback timelines, and 3-scenario projections.
    """
    tuition = float(params.get("tuition", 45000))
    accommodation = float(params.get("accommodation", 12000))
    food = float(params.get("food", 6000))
    insurance = float(params.get("insurance", 2000))
    travel = float(params.get("travel", 1800))
    visa_fees = float(params.get("visa_fees", 600))
    misc = float(params.get("misc", 2500))
    duration_years = float(params.get("duration", 2.0))
    country = str(params.get("country", "USA")).upper()
    field = str(params.get("field", "Computer Science"))
    inr_rate = float(params.get("inr_rate", 83.5))

    # Total Annual & Program Cost
    annual_living = accommodation + food + insurance + misc
    total_investment_usd = (tuition * duration_years) + (annual_living * duration_years) + (travel * 2) + visa_fees
    total_investment_inr = total_investment_usd * inr_rate

    # Expected Salaries by Country & Discipline
    SALARY_MATRIX = {
        "COMPUTER SCIENCE": {"USA": 125000, "CANADA": 92000, "UK": 72000, "GERMANY": 66000, "AUSTRALIA": 88000, "INDIA": 28000},
        "DATA SCIENCE": {"USA": 120000, "CANADA": 88000, "UK": 70000, "GERMANY": 64000, "AUSTRALIA": 86000, "INDIA": 25000},
        "BUSINESS ADMINISTRATION": {"USA": 115000, "CANADA": 85000, "UK": 80000, "GERMANY": 68000, "AUSTRALIA": 85000, "INDIA": 24000},
        "ENGINEERING": {"USA": 105000, "CANADA": 84000, "UK": 65000, "GERMANY": 68000, "AUSTRALIA": 84000, "INDIA": 20000},
    }
    field_key = field.upper()
    if field_key not in SALARY_MATRIX:
        field_key = "COMPUTER SCIENCE"

    country_key = country if country in SALARY_MATRIX[field_key] else "USA"
    expected_salary_usd = float(params.get("expected_salary") or SALARY_MATRIX[field_key].get(country_key, 110000))

    # Tax rate approximation
    tax_rate = 0.28 if country_key in ["USA", "CANADA"] else 0.32 if country_key in ["UK", "GERMANY"] else 0.25
    after_tax_annual = expected_salary_usd * (1 - tax_rate)

    # Post-grad living expenses (~45% of after-tax)
    post_grad_annual_living = after_tax_annual * 0.45
    annual_savings_usd = after_tax_annual - post_grad_annual_living
    monthly_savings_usd = annual_savings_usd / 12.0
    monthly_savings_inr = monthly_savings_usd * inr_rate

    # Break-even Payback in years
    payback_years = round(total_investment_usd / annual_savings_usd, 1) if annual_savings_usd > 0 else 99.0

    # 5-year and 10-year ROI
    five_year_net_gain = (annual_savings_usd * 5) - total_investment_usd
    five_year_roi_pct = round((five_year_net_gain / total_investment_usd) * 100.0, 1)

    ten_year_net_gain = (annual_savings_usd * 10) - total_investment_usd
    ten_year_roi_pct = round((ten_year_net_gain / total_investment_usd) * 100.0, 1)

    # 3-Scenario Projections
    best_case_sal = expected_salary_usd * 1.30
    best_annual_savings = (best_case_sal * (1 - tax_rate)) * 0.58
    best_payback = round(total_investment_usd / best_annual_savings, 1)

    worst_case_sal = expected_salary_usd * 0.80
    worst_annual_savings = (worst_case_sal * (1 - tax_rate)) * 0.50
    worst_payback = round(total_investment_usd / worst_annual_savings, 1)

    scenarios = {
        "best_case": {
            "label": "High Performer / Tier-1 Tech",
            "salary_usd": f"${best_case_sal:,.0f}",
            "salary_inr": f"₹{(best_case_sal * inr_rate / 100000):.1f}L",
            "payback_years": best_payback,
            "five_year_gain_inr": f"₹{((best_annual_savings * 5 - total_investment_usd) * inr_rate / 100000):.1f}L"
        },
        "expected_case": {
            "label": "Market Median Expected Admit",
            "salary_usd": f"${expected_salary_usd:,.0f}",
            "salary_inr": f"₹{(expected_salary_usd * inr_rate / 100000):.1f}L",
            "payback_years": payback_years,
            "five_year_gain_inr": f"₹{(five_year_net_gain * inr_rate / 100000):.1f}L"
        },
        "worst_case": {
            "label": "Conservative / Economic Slump",
            "salary_usd": f"${worst_case_sal:,.0f}",
            "salary_inr": f"₹{(worst_case_sal * inr_rate / 100000):.1f}L",
            "payback_years": worst_payback,
            "five_year_gain_inr": f"₹{((worst_annual_savings * 5 - total_investment_usd) * inr_rate / 100000):.1f}L"
        }
    }

    # Year 1 to 10 visual progression for chart
    chart_years = list(range(1, 11))
    chart_cumulative_costs = [round((total_investment_inr) / 100000, 1) for _ in chart_years]
    chart_cumulative_earnings = [round((annual_savings_usd * inr_rate * y) / 100000, 1) for y in chart_years]

    return {
        "total_investment_usd": f"${total_investment_usd:,.0f}",
        "total_investment_inr": f"₹{total_investment_inr / 100000:.1f}L",
        "expected_salary_usd": f"${expected_salary_usd:,.0f}",
        "expected_salary_inr": f"₹{expected_salary_usd * inr_rate / 100000:.1f}L",
        "monthly_savings_usd": f"${monthly_savings_usd:,.0f}",
        "monthly_savings_inr": f"₹{monthly_savings_inr:,.0f}",
        "payback_years": payback_years,
        "five_year_roi_pct": five_year_roi_pct,
        "ten_year_roi_pct": ten_year_roi_pct,
        "scenarios": scenarios,
        "breakdown": {
            "tuition_usd": tuition * duration_years,
            "housing_usd": accommodation * duration_years,
            "food_usd": food * duration_years,
            "insurance_usd": insurance * duration_years,
            "travel_usd": travel * 2,
            "visa_usd": visa_fees,
            "misc_usd": misc * duration_years
        },
        "chart_data": {
            "years": chart_years,
            "costs": chart_cumulative_costs,
            "earnings": chart_cumulative_earnings
        }
    }
