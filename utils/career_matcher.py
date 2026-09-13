from typing import Dict, Any, List

CAREER_ARCHETYPES = [
    {
        "title": "AI & Machine Learning Engineer",
        "holland_code": "IRC",
        "match_field": "Computer Science / AI",
        "why": "High alignment with mathematical problem solving, investigative computing research, and building algorithmic systems.",
        "skills_required": ["Python", "PyTorch/TensorFlow", "Applied Mathematics & Statistics", "Data Structures", "MLOps"],
        "expected_education": "B.Tech/BS in CS or Math + MS in AI / Computer Science",
        "recommended_courses": ["Coursera Deep Learning Specialization", "Fast.ai Practical Deep Learning", "CS231n Computer Vision"],
        "top_universities": ["Carnegie Mellon University", "Stanford University", "University of Toronto", "NUS"],
        "salary_range_usd": "$110,000 - $185,000",
        "salary_range_inr": "₹16,00,000 - ₹38,00,000",
        "demand_growth": "38% YoY growth across enterprise and tech firms"
    },
    {
        "title": "Data Scientist & Quantitative Analyst",
        "holland_code": "ICA",
        "match_field": "Data Science / Statistics",
        "why": "Combines analytical curiosity with statistical rigor to extract actionable predictive intelligence from complex datasets.",
        "skills_required": ["SQL", "Python/R", "Statistical Modeling", "Data Wrangling", "Machine Learning"],
        "expected_education": "BS in Quantitative Field + MS in Data Science or Analytics",
        "recommended_courses": ["IBM Data Science Professional", "Johns Hopkins Data Science", "MITx Micromasters in Statistics & DS"],
        "top_universities": ["Columbia University", "MIT IDSS", "University of Edinburgh", "NTU Singapore"],
        "salary_range_usd": "$100,000 - $165,000",
        "salary_range_inr": "₹14,00,000 - ₹32,00,000",
        "demand_growth": "32% YoY growth across finance, healthcare, and e-commerce"
    },
    {
        "title": "Cloud Solutions & DevOps Architect",
        "holland_code": "RCE",
        "match_field": "Software Engineering / Systems",
        "why": "Ideal for builders who enjoy large-scale distributed systems, infrastructure automation, reliability engineering, and system design.",
        "skills_required": ["Kubernetes", "AWS / GCP / Azure", "Terraform", "CI/CD Pipelines", "Linux Systems"],
        "expected_education": "B.Tech/BS in IT/CS + MS in Computer Engineering or Cloud Computing",
        "recommended_courses": ["AWS Certified Solutions Architect", "CKA Kubernetes Administrator", "Google Cloud Professional Engineer"],
        "top_universities": ["Georgia Tech", "Northeastern University", "University of Waterloo", "RWTH Aachen"],
        "salary_range_usd": "$115,000 - $175,000",
        "salary_range_inr": "₹15,00,000 - ₹35,00,000",
        "demand_growth": "28% YoY growth in enterprise migration"
    },
    {
        "title": "Product & Technology Strategist",
        "holland_code": "ESI",
        "match_field": "Business & Technology",
        "why": "Excels at the intersection of business strategy, technology roadmaps, user empathy, and cross-functional leadership.",
        "skills_required": ["Product Management", "Agile Methodologies", "User Research", "Market Sizing", "Technical Communication"],
        "expected_education": "B.Tech / B.E. + MBA / Master of Engineering Management (MEM)",
        "recommended_courses": ["Reforge Product Strategy", "Duke MEM Program", "Product School Certification"],
        "top_universities": ["Harvard Business School", "Wharton (UPenn)", "London Business School", "INSEAD"],
        "salary_range_usd": "$125,000 - $190,000",
        "salary_range_inr": "₹18,00,000 - ₹45,00,000",
        "demand_growth": "25% YoY steady executive demand"
    },
    {
        "title": "Cybersecurity & Cryptography Specialist",
        "holland_code": "IRC",
        "match_field": "Information Security",
        "why": "Focuses on threat defense, secure protocol engineering, penetration testing, and digital forensics in mission-critical environments.",
        "skills_required": ["Network Security", "Cryptography", "Ethical Hacking", "Python/C", "Zero Trust Architecture"],
        "expected_education": "BS in CS / Cyber + MS in Cybersecurity",
        "recommended_courses": ["CompTIA Security+", "Offensive Security OSCP", "SANS GIAC Security Essentials"],
        "top_universities": ["Georgia Tech", "Purdue University", "University of Maryland", "TU Munich"],
        "salary_range_usd": "$105,000 - $160,000",
        "salary_range_inr": "₹13,00,000 - ₹30,00,000",
        "demand_growth": "35% YoY driven by global regulation and threat vectors"
    }
]

def score_riasec(answers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes RIASEC personality scores from assessment questions.
    R: Realistic, I: Investigative, A: Artistic, S: Social, E: Enterprising, C: Conventional
    """
    scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}

    for key, val in answers.items():
        try:
            rating = int(val)
        except (ValueError, TypeError):
            rating = 3

        if key.startswith("q_r"):
            scores["R"] += rating
        elif key.startswith("q_i"):
            scores["I"] += rating
        elif key.startswith("q_a"):
            scores["A"] += rating
        elif key.startswith("q_s"):
            scores["S"] += rating
        elif key.startswith("q_e"):
            scores["E"] += rating
        elif key.startswith("q_c"):
            scores["C"] += rating

    # Ensure baseline if form was partially answered
    if sum(scores.values()) == 0:
        scores = {"R": 18, "I": 24, "A": 12, "S": 15, "E": 19, "C": 21}

    # Sort descending to build primary Holland code (top 3 letters)
    sorted_codes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    holland_code = "".join([code[0] for code in sorted_codes[:3]])

    # Match against career archetypes
    recommendations = []
    for career in CAREER_ARCHETYPES:
        target_code = career["holland_code"]
        # Overlap points
        overlap = sum(1 for char in holland_code if char in target_code)
        base_pct = 70 + (overlap * 9)
        # Add slight variance
        pct = min(96, base_pct)
        recommendations.append({
            **career,
            "match_pct": pct
        })

    recommendations.sort(key=lambda x: x["match_pct"], reverse=True)

    return {
        "scores": scores,
        "holland_code": holland_code,
        "primary_trait": sorted_codes[0][0],
        "recommendations": recommendations
    }
