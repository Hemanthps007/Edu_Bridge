from typing import Dict, Any, List

SCHOLARSHIPS_DATA: List[Dict[str, Any]] = [
    {
        "id": "chevening",
        "name": "Chevening Scholarship",
        "country": "UK",
        "amount_usd": 45000,
        "amount_display": "100% Tuition + Living Stipend + Flights (~£35,000)",
        "deadline": "November 03, 2026",
        "category": "Government Funded",
        "min_cgpa": 3.3,
        "min_work_exp_years": 2,
        "max_family_income_inr": None,
        "application_link": "https://www.chevening.org/apply/",
        "eligibility_desc": "Minimum 2 years (2,800 hours) work experience, leadership track record, undergraduate degree.",
        "documents_required": ["Statement of Purpose", "2 Professional LORs", "Undergraduate Transcripts", "Unconditional Offer"]
    },
    {
        "id": "fulbright",
        "name": "Fulbright-Nehru Master's Fellowships",
        "country": "USA",
        "amount_usd": 65000,
        "amount_display": "Full Tuition + Living + J-1 Visa Support",
        "deadline": "May 15, 2027",
        "category": "US-India Bilateral",
        "min_cgpa": 3.4,
        "min_work_exp_years": 3,
        "max_family_income_inr": None,
        "application_link": "https://www.usief.org.in/",
        "eligibility_desc": "Equivalent to US bachelor's degree (4-year degree or master's), minimum 3 years professional work experience.",
        "documents_required": ["Study/Research Objective", "Personal Statement", "3 Reference Letters", "GRE/TOEFL Scores"]
    },
    {
        "id": "daad",
        "name": "DAAD Development-Related Postgraduate Courses (EPOS)",
        "country": "Germany",
        "amount_usd": 22000,
        "amount_display": "€934/month Stipend + Health & Travel Allowance",
        "deadline": "October 15, 2026",
        "category": "German Academic Exchange",
        "min_cgpa": 3.2,
        "min_work_exp_years": 2,
        "max_family_income_inr": None,
        "application_link": "https://www.daad.de/en/",
        "eligibility_desc": "Bachelor's degree with above-average results, minimum 2 years relevant professional experience.",
        "documents_required": ["Europass CV", "Letter of Motivation", "Employer Reference", "Language Certificates"]
    },
    {
        "id": "erasmus",
        "name": "Erasmus Mundus Joint Master Degrees (EMJM)",
        "country": "Europe",
        "amount_usd": 38000,
        "amount_display": "Full Tuition Waiver + €1,400 Monthly Living Allowance",
        "deadline": "January 15, 2027",
        "category": "European Union Flagship",
        "min_cgpa": 3.4,
        "min_work_exp_years": 0,
        "max_family_income_inr": None,
        "application_link": "https://erasmus-plus.ec.europa.eu/",
        "eligibility_desc": "Open to all nationalities; study across at least two European countries during the program.",
        "documents_required": ["Motivation Letter", "Academic Transcripts", "2 Academic LORs", "Proof of English Proficiency"]
    },
    {
        "id": "inlaks",
        "name": "Inlaks Shivdasani Foundation Scholarship",
        "country": "USA / UK / Europe",
        "amount_usd": 50000,
        "amount_display": "Up to $100,000 for Tuition & Living Expenses",
        "deadline": "March 30, 2027",
        "category": "Philanthropic Trust",
        "min_cgpa": 3.6,
        "min_work_exp_years": 0,
        "max_family_income_inr": None,
        "application_link": "https://www.inlaksfoundation.org/",
        "eligibility_desc": "Indian passport holders under 30 with first-class degree from a recognized Indian university.",
        "documents_required": ["Admission Offer Letter", "Fee Structure", "Portfolio / Writing Sample", "Evidence of Outstanding Potential"]
    },
    {
        "id": "narotam",
        "name": "Narotam Sekhsaria Scholarship Programme",
        "country": "Global",
        "amount_usd": 24000,
        "amount_display": "Interest-Free Loan Scholarship up to ₹20,00,000",
        "deadline": "March 20, 2027",
        "category": "Merit Loan Scholarship",
        "min_cgpa": 3.3,
        "min_work_exp_years": 0,
        "max_family_income_inr": 1500000,
        "application_link": "https://pg.nsfoundation.co.in/",
        "eligibility_desc": "Indian nationals below 30 pursuing postgraduate degrees at top accredited global institutions.",
        "documents_required": ["Statement of Purpose", "Attested Marksheets", "Parent ITR Copies", "Interview Round"]
    },
    {
        "id": "commonwealth",
        "name": "Commonwealth Master's Scholarship",
        "country": "UK",
        "amount_usd": 40000,
        "amount_display": "Full Tuition + Airfare + £1,347/month Living Stipend",
        "deadline": "December 12, 2026",
        "category": "Government Funded",
        "min_cgpa": 3.4,
        "min_work_exp_years": 0,
        "max_family_income_inr": 800000,
        "application_link": "https://cscuk.fcdo.gov.uk/",
        "eligibility_desc": "Permanent resident of a Commonwealth country; cannot afford to study in the UK without scholarship.",
        "documents_required": ["Development Impact Statement", "2 References", "Undergraduate Transcripts", "Family Income Proof"]
    }
]

def match_scholarships(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    cgpa = float(profile.get("gpa") or profile.get("cgpa") or 3.3)
    if cgpa > 4.0:
        cgpa = (cgpa / 10.0) * 4.0

    work_exp = int(profile.get("work_exp") or profile.get("work_experience") or 1)
    target_country = str(profile.get("country_goal") or profile.get("country_pref") or "ALL").upper()

    results = []
    for s in SCHOLARSHIPS_DATA:
        # Country relevance
        country_match = target_country in ["ALL", "GLOBAL"] or s["country"].upper() in ["GLOBAL", "EUROPE"] or target_country in s["country"].upper()

        # Criteria evaluations
        cgpa_ok = cgpa >= s["min_cgpa"]
        work_ok = work_exp >= s["min_work_exp_years"]

        match_score = 50
        if country_match:
            match_score += 25
        if cgpa_ok:
            match_score += 15
        if work_ok:
            match_score += 10

        if match_score >= 85:
            status = "Eligible — High Match"
            status_badge = "emerald"
        elif match_score >= 65:
            status = "Eligible — Moderate Match"
            status_badge = "sky"
        else:
            status = "Potential Reach"
            status_badge = "amber"

        results.append({
            **s,
            "match_score": match_score,
            "status": status,
            "status_badge": status_badge,
            "cgpa_ok": cgpa_ok,
            "work_ok": work_ok
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results
