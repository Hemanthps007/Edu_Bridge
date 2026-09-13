from typing import Dict, Any, List

BADGES_CATALOG = [
    {"id": "profile_complete", "name": "Profile Pioneer", "icon": "fa-user-check", "desc": "Completed student background & scores onboarding", "xp": 200},
    {"id": "career_explorer", "name": "Career Explorer", "icon": "fa-compass", "desc": "Completed RIASEC career assessment", "xp": 300},
    {"id": "uni_researcher", "name": "University Strategist", "icon": "fa-building-columns", "desc": "Shortlisted 5+ higher education programs", "xp": 150},
    {"id": "admission_analyst", "name": "Admission Analyst", "icon": "fa-chart-line", "desc": "Ran ML admission probability simulations", "xp": 100},
    {"id": "finance_master", "name": "Finance Master", "icon": "fa-sack-dollar", "desc": "Modeled advanced 10-year higher ed ROI", "xp": 150},
    {"id": "biometric_secured", "name": "Biometric Shield", "icon": "fa-face-smile", "desc": "Enrolled browser-based Face Recognition ID", "xp": 150},
    {"id": "application_pro", "name": "Application Pro", "icon": "fa-file-signature", "desc": "Tracked first active university application", "xp": 250},
]

def calculate_gamification_state(user_data: Dict[str, Any]) -> Dict[str, Any]:
    xp = int(user_data.get("points") or user_data.get("xp_points") or 100)
    level = max(1, 1 + (xp // 250))
    next_level_xp = level * 250
    current_level_base = (level - 1) * 250
    progress_in_level = xp - current_level_base
    progress_pct = min(100, int((progress_in_level / 250.0) * 100))

    user_badges = user_data.get("badges") or []
    badges_unlocked = []
    badges_locked = []

    for badge in BADGES_CATALOG:
        if badge["id"] in user_badges or (badge["id"] == "profile_complete" and user_data.get("name")):
            badges_unlocked.append({**badge, "unlocked": True})
        else:
            badges_locked.append({**badge, "unlocked": False})

    return {
        "xp": xp,
        "level": level,
        "next_level_xp": next_level_xp,
        "progress_pct": progress_pct,
        "badges_unlocked": badges_unlocked,
        "badges_locked": badges_locked,
        "total_badges": len(BADGES_CATALOG)
    }

def award_xp(user_data: Dict[str, Any], event_id: str, xp_amount: int, badge_id: str = None) -> Dict[str, Any]:
    current_xp = int(user_data.get("points") or user_data.get("xp_points") or 100)
    new_xp = current_xp + xp_amount
    user_data["points"] = new_xp
    user_data["xp_points"] = new_xp
    user_data["level"] = max(1, 1 + (new_xp // 250))

    badges = set(user_data.get("badges") or [])
    if badge_id:
        badges.add(badge_id)
    user_data["badges"] = list(badges)
    return user_data
