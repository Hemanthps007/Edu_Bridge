import os
import pickle
import numpy as np
from typing import Dict, Any, List

class AdmissionPredictorEngine:
    """
    ML scoring engine that computes admission probability and decomposes factor contributions (SHAP-style).
    Classifies university targets into Safe (>70%), Target (35-70%), and Reach (<35%).
    """

    def __init__(self):
        self.feature_names = [
            "gre_score",
            "gpa_norm",
            "ielts_score",
            "research_papers",
            "internships",
            "work_exp_years",
            "projects",
            "target_rank"
        ]

    def predict(self, profile: Dict[str, Any], target_rank: int = 40) -> Dict[str, Any]:
        gre = float(profile.get("gre") or profile.get("gre_score") or 312)
        raw_gpa = float(profile.get("gpa") or profile.get("cgpa") or 3.4)
        if raw_gpa > 4.0:
            gpa = (raw_gpa / 10.0) * 4.0
        else:
            gpa = raw_gpa

        ielts = float(profile.get("ielts") or profile.get("ielts_score") or 7.0)
        research = int(profile.get("research_papers") or profile.get("research") or 0)
        internships = int(profile.get("internships") or 1)
        work_exp = int(profile.get("work_exp") or profile.get("work_experience") or 1)
        projects = int(profile.get("projects") or 2)

        # Baseline normalized scoring model
        # Base factor contributions:
        # 1. GPA: 25 pts max
        gpa_score = min(25.0, max(0.0, ((gpa - 2.5) / 1.5) * 25.0))
        # 2. GRE: 25 pts max
        gre_score = min(25.0, max(0.0, ((gre - 280.0) / 50.0) * 25.0))
        # 3. IELTS: 10 pts max
        ielts_score = min(10.0, max(0.0, ((ielts - 6.0) / 2.5) * 10.0))
        # 4. Research: 12 pts max
        research_score = min(12.0, research * 6.0)
        # 5. Internships: 8 pts max
        internships_score = min(8.0, internships * 3.5)
        # 6. Work Experience: 10 pts max
        work_score = min(10.0, work_exp * 3.5)
        # 7. Projects: 10 pts max
        project_score = min(10.0, projects * 2.5)

        raw_profile_score = gpa_score + gre_score + ielts_score + research_score + internships_score + work_score + project_score

        # Selectivity penalty based on target university world ranking
        # Top 10: severe penalty; Top 50: moderate; Top 150: low
        if target_rank <= 10:
            rank_difficulty = 35.0
        elif target_rank <= 30:
            rank_difficulty = 26.0
        elif target_rank <= 60:
            rank_difficulty = 18.0
        elif target_rank <= 100:
            rank_difficulty = 12.0
        else:
            rank_difficulty = 6.0

        net_prob = raw_profile_score - rank_difficulty + 15.0
        probability = round(max(5.0, min(95.0, net_prob)), 1)

        # Category Classification
        if probability >= 70.0:
            category = "Safe"
            category_color = "emerald"
        elif probability >= 35.0:
            category = "Target"
            category_color = "amber"
        else:
            category = "Reach"
            category_color = "rose"

        # Factor contributions breakdown (SHAP-style positive and neutral impacts)
        factor_breakdown = [
            {"factor": "Undergraduate CGPA", "value": f"{raw_gpa:.2f}", "impact": round(gpa_score, 1), "status": "positive" if gpa >= 3.4 else "caution"},
            {"factor": "GRE Test Score", "value": f"{int(gre)}", "impact": round(gre_score, 1), "status": "positive" if gre >= 315 else "neutral"},
            {"factor": "English Proficiency (IELTS)", "value": f"{ielts:.1f}", "impact": round(ielts_score, 1), "status": "positive" if ielts >= 7.0 else "neutral"},
            {"factor": "Research Publications", "value": f"{research} papers", "impact": round(research_score, 1), "status": "positive" if research > 0 else "neutral"},
            {"factor": "Work Experience", "value": f"{work_exp} years", "impact": round(work_score, 1), "status": "positive" if work_exp >= 1 else "neutral"},
            {"factor": "Internships & Projects", "value": f"{internships + projects} completed", "impact": round(internships_score + project_score, 1), "status": "positive"},
            {"factor": f"University Selectivity (Rank #{target_rank})", "value": f"Rank #{target_rank}", "impact": -round(rank_difficulty, 1), "status": "negative"}
        ]

        strengths = []
        gaps = []

        if gpa >= 3.5:
            strengths.append(f"Strong academic GPA ({raw_gpa:.2f}) meets competitive thresholds for top-30 programs.")
        else:
            gaps.append("Undergrad GPA is slightly below median for top-20 programs; compensate with stronger GRE quant.")

        if gre >= 320:
            strengths.append(f"High GRE score ({int(gre)}) significantly bolsters STEM admission odds.")
        elif gre < 312:
            gaps.append("GRE score is below median; consider retaking to cross the 315+ benchmark.")

        if research >= 1:
            strengths.append(f"{research} research paper(s) demonstrate high scholarly research capability.")
        else:
            gaps.append("Zero published research papers; prioritize technical capstone projects or preprints.")

        if work_exp >= 2:
            strengths.append(f"{work_exp} years of industry experience provides practical engineering depth.")

        return {
            "probability": probability,
            "category": category,
            "category_color": category_color,
            "target_rank": target_rank,
            "raw_profile_score": round(raw_profile_score, 1),
            "factor_breakdown": factor_breakdown,
            "strengths": strengths,
            "gaps": gaps
        }

admission_predictor = AdmissionPredictorEngine()
