from typing import Dict, Any

def calculate_profile_scores(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes deep readiness scores across 4 dimensions + overall readiness index.
    Dimensions:
      1. Academic Strength (0-100)
      2. Financial Readiness (0-100)
      3. Career Clarity (0-100)
      4. Admission Readiness (0-100)
      Overall Readiness (0-100)
    """
    # 1. Academic Strength
    # Baseline inputs
    cgpa = float(profile.get("gpa") or profile.get("degree_cgpa") or 3.2)
    # CGPA might be out of 10 or 4.0
    if cgpa > 4.0:
        norm_cgpa = min(100.0, (cgpa / 10.0) * 100.0)
    else:
        norm_cgpa = min(100.0, (cgpa / 4.0) * 100.0)

    tenth_pct = float(profile.get("tenth_pct") or 82.0)
    twelfth_pct = float(profile.get("twelfth_pct") or 84.0)

    academic_strength = round(
        (norm_cgpa * 0.50) + (twelfth_pct * 0.30) + (tenth_pct * 0.20)
    )
    academic_strength = max(10, min(99, academic_strength))

    # 2. Financial Readiness
    # Budget vs target country average total cost (INR)
    country = (profile.get("country_goal") or profile.get("country_pref") or "USA").upper()
    cost_benchmarks_inr = {
        "USA": 5500000,      # ~55 Lakhs
        "UK": 4000000,       # ~40 Lakhs
        "CANADA": 3500000,   # ~35 Lakhs
        "GERMANY": 1800000,  # ~18 Lakhs
        "AUSTRALIA": 4200000,# ~42 Lakhs
        "SINGAPORE": 4000000,# ~40 Lakhs
        "INDIA": 1000000     # ~10 Lakhs
    }
    target_cost = cost_benchmarks_inr.get(country, 4000000)
    raw_budget = profile.get("budget") or "3500000"

    # Map string ranges to numbers if given as categorical
    if isinstance(raw_budget, str):
        if "low" in raw_budget.lower() or "10" in raw_budget:
            student_budget = 1500000
        elif "medium" in raw_budget.lower() or "30" in raw_budget:
            student_budget = 3500000
        elif "high" in raw_budget.lower() or "50" in raw_budget:
            student_budget = 5500000
        else:
            try:
                student_budget = float(raw_budget.replace(",", "").replace("₹", "").replace("L", "00000"))
            except ValueError:
                student_budget = 3500000
    else:
        student_budget = float(raw_budget)

    # Ratio of budget to cost + loan readiness cushion
    has_coapplicant = 1 if profile.get("has_coapplicant", True) else 0
    financial_ratio = (student_budget / target_cost) * 75
    financial_readiness = round(min(100, financial_ratio + (has_coapplicant * 20)))
    financial_readiness = max(20, min(98, financial_readiness))

    # 3. Career Clarity
    # Completeness of interests, skill ratings, target program definition
    has_target_program = 25 if profile.get("target_program") else 10
    has_interests = 25 if profile.get("interests") or profile.get("field") else 10
    has_assessment = 30 if profile.get("career_assessment_completed") or profile.get("riasec_code") else 15
    has_skills = 20 if profile.get("skills") else 10
    career_clarity = min(98, has_target_program + has_interests + has_assessment + has_skills)

    # 4. Admission Readiness
    # Academic score + test scores (GRE/IELTS) + Work Exp + Research + Projects
    gre = int(profile.get("gre") or profile.get("gre_score") or 310)
    ielts = float(profile.get("ielts") or profile.get("ielts_score") or 7.0)
    work_exp = int(profile.get("work_exp") or 1)
    research = int(profile.get("research_papers") or profile.get("research") or 0)
    internships = int(profile.get("internships") or 1)
    projects = int(profile.get("projects") or 2)

    test_score_contrib = min(25, max(5, int((gre - 280) / 40 * 15) + int((ielts - 5.5) / 2.5 * 10)))
    exp_contrib = min(25, (work_exp * 5) + (internships * 4) + (research * 6) + (projects * 3))
    acad_contrib = academic_strength * 0.50

    admission_readiness = round(acad_contrib + test_score_contrib + exp_contrib)
    admission_readiness = max(15, min(98, admission_readiness))

    # Overall Index (Weighted average)
    overall_score = round(
        (academic_strength * 0.35) +
        (admission_readiness * 0.30) +
        (financial_readiness * 0.20) +
        (career_clarity * 0.15)
    )
    overall_score = max(20, min(98, overall_score))

    return {
        "academic_strength": academic_strength,
        "financial_readiness": financial_readiness,
        "career_clarity": career_clarity,
        "admission_readiness": admission_readiness,
        "overall_score": overall_score
    }
