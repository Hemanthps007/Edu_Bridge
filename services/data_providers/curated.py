from typing import List, Dict, Any, Optional
from .base import UniversityDataProvider

CURATED_UNIVERSITIES: List[Dict[str, Any]] = [
    {
        "id": "cmu",
        "name": "Carnegie Mellon University",
        "country": "USA",
        "city": "Pittsburgh, PA",
        "qs_ranking": 52,
        "the_ranking": 24,
        "tuition_usd": 62000,
        "living_cost_usd": 20000,
        "acceptance_rate": 11.0,
        "application_deadline": "Dec 15, 2026",
        "website": "https://www.cmu.edu",
        "popular_programs": ["MS Computer Science", "MS AI & Innovation", "MS Robotics", "MS Software Engineering"],
        "admission_requirements": {"min_cgpa": 3.7, "min_gre": 322, "min_ielts": 7.5, "work_exp_preferred": True},
        "description": "Global leader in Computer Science, Artificial Intelligence, Robotics, and Software Engineering."
    },
    {
        "id": "stanford",
        "name": "Stanford University",
        "country": "USA",
        "city": "Stanford, CA",
        "qs_ranking": 5,
        "the_ranking": 2,
        "tuition_usd": 64000,
        "living_cost_usd": 26000,
        "acceptance_rate": 3.9,
        "application_deadline": "Dec 05, 2026",
        "website": "https://www.stanford.edu",
        "popular_programs": ["MS Computer Science", "MBA", "MS Electrical Engineering", "MS Data Science"],
        "admission_requirements": {"min_cgpa": 3.85, "min_gre": 328, "min_ielts": 8.0, "research_required": True},
        "description": "Silicon Valley's premier research powerhouse known for pioneering entrepreneurship and computing."
    },
    {
        "id": "mit",
        "name": "Massachusetts Institute of Technology",
        "country": "USA",
        "city": "Cambridge, MA",
        "qs_ranking": 1,
        "the_ranking": 3,
        "tuition_usd": 61500,
        "living_cost_usd": 22000,
        "acceptance_rate": 4.0,
        "application_deadline": "Dec 15, 2026",
        "website": "https://www.mit.edu",
        "popular_programs": ["MS EECS", "Master of Business Analytics", "MS Mech Eng", "PhD Computation"],
        "admission_requirements": {"min_cgpa": 3.9, "min_gre": 330, "min_ielts": 8.0, "research_required": True},
        "description": "World's top university for engineering, physical sciences, economics, and computational research."
    },
    {
        "id": "gatech",
        "name": "Georgia Institute of Technology",
        "country": "USA",
        "city": "Atlanta, GA",
        "qs_ranking": 97,
        "the_ranking": 38,
        "tuition_usd": 32000,
        "living_cost_usd": 15000,
        "acceptance_rate": 16.0,
        "application_deadline": "Jan 10, 2027",
        "website": "https://www.gatech.edu",
        "popular_programs": ["MS Computer Science", "MS Analytics", "MS Cyber Security", "MS Industrial Eng"],
        "admission_requirements": {"min_cgpa": 3.5, "min_gre": 318, "min_ielts": 7.0, "work_exp_preferred": False},
        "description": "High-ROI public engineering powerhouse with globally acclaimed computing programs."
    },
    {
        "id": "utaustin",
        "name": "University of Texas at Austin",
        "country": "USA",
        "city": "Austin, TX",
        "qs_ranking": 58,
        "the_ranking": 52,
        "tuition_usd": 22000,
        "living_cost_usd": 14000,
        "acceptance_rate": 28.0,
        "application_deadline": "Dec 01, 2026",
        "website": "https://www.utexas.edu",
        "popular_programs": ["MS Computer Science", "MS Business Analytics", "MS ECE", "MS Information Studies"],
        "admission_requirements": {"min_cgpa": 3.4, "min_gre": 315, "min_ielts": 7.0},
        "description": "Located in Silicon Hills tech corridor, renowned for stellar academics and affordable in-state/out-state rates."
    },
    {
        "id": "northeastern",
        "name": "Northeastern University",
        "country": "USA",
        "city": "Boston, MA",
        "qs_ranking": 396,
        "the_ranking": 168,
        "tuition_usd": 54000,
        "living_cost_usd": 19000,
        "acceptance_rate": 33.0,
        "application_deadline": "Feb 01, 2027",
        "website": "https://www.northeastern.edu",
        "popular_programs": ["MS Computer Science", "MS Information Systems", "MS Data Analytics", "MS Biotechnology"],
        "admission_requirements": {"min_cgpa": 3.2, "min_gre": 308, "min_ielts": 6.5},
        "description": "Famous for industry Co-op programs providing up to 8 months of paid full-time corporate work experience."
    },
    {
        "id": "oxford",
        "name": "University of Oxford",
        "country": "UK",
        "city": "Oxford",
        "qs_ranking": 3,
        "the_ranking": 1,
        "tuition_usd": 48000,
        "living_cost_usd": 18000,
        "acceptance_rate": 13.0,
        "application_deadline": "Jan 08, 2027",
        "website": "https://www.ox.ac.uk",
        "popular_programs": ["MSc Advanced Computer Science", "MBA Said", "MSc Financial Economics", "MSc AI"],
        "admission_requirements": {"min_cgpa": 3.8, "min_gre": 0, "min_ielts": 7.5},
        "description": "The oldest university in the English-speaking world, offering 1-year intensive master's programs."
    },
    {
        "id": "cambridge",
        "name": "University of Cambridge",
        "country": "UK",
        "city": "Cambridge",
        "qs_ranking": 2,
        "the_ranking": 5,
        "tuition_usd": 50000,
        "living_cost_usd": 18500,
        "acceptance_rate": 14.0,
        "application_deadline": "Dec 03, 2026",
        "website": "https://www.cam.ac.uk",
        "popular_programs": ["MPhil in Advanced Computer Science", "Master of Finance", "MPhil Technology Policy"],
        "admission_requirements": {"min_cgpa": 3.85, "min_gre": 0, "min_ielts": 7.5},
        "description": "Historic institution at the heart of the Silicon Fen high-tech business cluster."
    },
    {
        "id": "imperial",
        "name": "Imperial College London",
        "country": "UK",
        "city": "London",
        "qs_ranking": 6,
        "the_ranking": 8,
        "tuition_usd": 46000,
        "living_cost_usd": 22000,
        "acceptance_rate": 15.0,
        "application_deadline": "Jan 15, 2027",
        "website": "https://www.imperial.ac.uk",
        "popular_programs": ["MSc Computing (AI & ML)", "MSc Business Analytics", "MSc Risk Management"],
        "admission_requirements": {"min_cgpa": 3.6, "min_gre": 0, "min_ielts": 7.0},
        "description": "STEM, business, and medicine titan in central London with unmatched employer connectivity."
    },
    {
        "id": "edinburgh",
        "name": "University of Edinburgh",
        "country": "UK",
        "city": "Edinburgh",
        "qs_ranking": 22,
        "the_ranking": 30,
        "tuition_usd": 38000,
        "living_cost_usd": 16000,
        "acceptance_rate": 26.0,
        "application_deadline": "Jan 25, 2027",
        "website": "https://www.ed.ac.uk",
        "popular_programs": ["MSc Data Science", "MSc Artificial Intelligence", "MSc Informatics", "MSc Finance"],
        "admission_requirements": {"min_cgpa": 3.3, "min_gre": 0, "min_ielts": 7.0},
        "description": "Home to Europe's largest artificial intelligence research group and Bayes Centre data institute."
    },
    {
        "id": "utoronto",
        "name": "University of Toronto",
        "country": "Canada",
        "city": "Toronto, ON",
        "qs_ranking": 21,
        "the_ranking": 18,
        "tuition_usd": 32000,
        "living_cost_usd": 16000,
        "acceptance_rate": 18.0,
        "application_deadline": "Jan 15, 2027",
        "website": "https://www.utoronto.ca",
        "popular_programs": ["MSc Applied Computing", "Master of Data Science", "MBA Rotman", "MEng ECE"],
        "admission_requirements": {"min_cgpa": 3.5, "min_gre": 315, "min_ielts": 7.0},
        "description": "Canada's top institution, world-renowned birthplace of modern Deep Learning under Geoffrey Hinton."
    },
    {
        "id": "waterloo",
        "name": "University of Waterloo",
        "country": "Canada",
        "city": "Waterloo, ON",
        "qs_ranking": 112,
        "the_ranking": 158,
        "tuition_usd": 28000,
        "living_cost_usd": 14000,
        "acceptance_rate": 21.0,
        "application_deadline": "Feb 01, 2027",
        "website": "https://uwaterloo.ca",
        "popular_programs": ["MMath Computer Science", "MEng Electrical & Computer", "Master of Data Analytics"],
        "admission_requirements": {"min_cgpa": 3.4, "min_gre": 312, "min_ielts": 7.0},
        "description": "North America's greatest tech co-op powerhouse, highly recruited by Big Tech firms."
    },
    {
        "id": "ubc",
        "name": "University of British Columbia",
        "country": "Canada",
        "city": "Vancouver, BC",
        "qs_ranking": 34,
        "the_ranking": 40,
        "tuition_usd": 29000,
        "living_cost_usd": 17000,
        "acceptance_rate": 24.0,
        "application_deadline": "Jan 10, 2027",
        "website": "https://www.ubc.ca",
        "popular_programs": ["Master of Data Science", "MSc Computer Science", "MEng Clean Energy"],
        "admission_requirements": {"min_cgpa": 3.4, "min_gre": 312, "min_ielts": 7.0},
        "description": "Top research university on the Pacific Rim with easy access to Vancouver's booming tech scene."
    },
    {
        "id": "tum",
        "name": "Technical University of Munich (TUM)",
        "country": "Germany",
        "city": "Munich",
        "qs_ranking": 37,
        "the_ranking": 30,
        "tuition_usd": 4000,
        "living_cost_usd": 13000,
        "acceptance_rate": 19.0,
        "application_deadline": "May 31, 2027",
        "website": "https://www.tum.de",
        "popular_programs": ["MSc Informatics", "MSc Data Engineering", "MSc Robotics", "MSc Management & Technology"],
        "admission_requirements": {"min_cgpa": 3.4, "min_gre": 315, "min_ielts": 6.5},
        "description": "Germany's #1 technical university with nominal semester administrative fees and strong industry ties (BMW, Siemens, SAP)."
    },
    {
        "id": "rwth",
        "name": "RWTH Aachen University",
        "country": "Germany",
        "city": "Aachen",
        "qs_ranking": 106,
        "the_ranking": 99,
        "tuition_usd": 1500,
        "living_cost_usd": 11000,
        "acceptance_rate": 27.0,
        "application_deadline": "Mar 01, 2027",
        "website": "https://www.rwth-aachen.de",
        "popular_programs": ["MSc Software Systems Eng", "MSc Automotive Eng", "MSc Data Science"],
        "admission_requirements": {"min_cgpa": 3.2, "min_gre": 310, "min_ielts": 6.5},
        "description": "Europe's foremost engineering titan offering nearly tuition-free master's degrees taught in English."
    },
    {
        "id": "nus",
        "name": "National University of Singapore (NUS)",
        "country": "Singapore",
        "city": "Singapore",
        "qs_ranking": 8,
        "the_ranking": 19,
        "tuition_usd": 36000,
        "living_cost_usd": 14000,
        "acceptance_rate": 12.0,
        "application_deadline": "Jan 31, 2027",
        "website": "https://www.nus.edu.sg",
        "popular_programs": ["Master of Computing (AI)", "MSc Business Analytics", "MSc Digital Financial Technology"],
        "admission_requirements": {"min_cgpa": 3.6, "min_gre": 320, "min_ielts": 7.0},
        "description": "Asia's premier higher education powerhouse with top-ranked computing and quantitative finance faculties."
    },
    {
        "id": "ntu",
        "name": "Nanyang Technological University (NTU)",
        "country": "Singapore",
        "city": "Singapore",
        "qs_ranking": 26,
        "the_ranking": 32,
        "tuition_usd": 34000,
        "living_cost_usd": 13500,
        "acceptance_rate": 15.0,
        "application_deadline": "Jan 31, 2027",
        "website": "https://www.ntu.edu.sg",
        "popular_programs": ["MSc Artificial Intelligence", "MSc Data Science", "MSc Analytics"],
        "admission_requirements": {"min_cgpa": 3.5, "min_gre": 318, "min_ielts": 6.5},
        "description": "Rapidly rising smart campus institution with extensive AI patenting and corporate labs."
    },
    {
        "id": "unimelb",
        "name": "University of Melbourne",
        "country": "Australia",
        "city": "Melbourne, VIC",
        "qs_ranking": 14,
        "the_ranking": 37,
        "tuition_usd": 35000,
        "living_cost_usd": 16000,
        "acceptance_rate": 30.0,
        "application_deadline": "Nov 30, 2026",
        "website": "https://www.unimelb.edu.au",
        "popular_programs": ["Master of Computer Science", "Master of Data Science", "Master of Information Systems"],
        "admission_requirements": {"min_cgpa": 3.3, "min_gre": 0, "min_ielts": 6.5},
        "description": "Australia's top-ranked comprehensive research university with generous post-study work visa terms."
    },
    {
        "id": "unsw",
        "name": "University of New South Wales (UNSW)",
        "country": "Australia",
        "city": "Sydney, NSW",
        "qs_ranking": 19,
        "the_ranking": 84,
        "tuition_usd": 34000,
        "living_cost_usd": 17500,
        "acceptance_rate": 34.0,
        "application_deadline": "Nov 30, 2026",
        "website": "https://www.unsw.edu.au",
        "popular_programs": ["Master of Information Technology", "Master of Commerce", "Master of Engineering Science"],
        "admission_requirements": {"min_cgpa": 3.2, "min_gre": 0, "min_ielts": 6.5},
        "description": "Renowned for producing Australia's highest number of startup founders and engineering innovators."
    },
    {
        "id": "iitb",
        "name": "IIT Bombay",
        "country": "India",
        "city": "Mumbai",
        "qs_ranking": 149,
        "the_ranking": 350,
        "tuition_usd": 3000,
        "living_cost_usd": 2500,
        "acceptance_rate": 1.2,
        "application_deadline": "Apr 15, 2027",
        "website": "https://www.iitb.ac.in",
        "popular_programs": ["M.Tech Computer Science", "M.Tech Data Science", "M.Des Interaction Design"],
        "admission_requirements": {"min_cgpa": 3.6, "min_gre": 0, "gate_score": 750},
        "description": "India's highest ranked engineering institute with extraordinary alumni leadership across global tech."
    },
    {
        "id": "iisc",
        "name": "Indian Institute of Science (IISc)",
        "country": "India",
        "city": "Bengaluru",
        "qs_ranking": 225,
        "the_ranking": 250,
        "tuition_usd": 2000,
        "living_cost_usd": 2200,
        "acceptance_rate": 1.0,
        "application_deadline": "Mar 31, 2027",
        "website": "https://iisc.ac.in",
        "popular_programs": ["M.Tech Computational & Data Science", "M.Tech AI", "M.Des"],
        "admission_requirements": {"min_cgpa": 3.7, "gate_score": 780},
        "description": "Premier scientific research institute in the Silicon Valley of India with immense research citation impact."
    }
]

class CuratedDataProvider(UniversityDataProvider):
    """Data provider sourcing from curated, verified higher education datasets."""

    def __init__(self):
        self.universities = CURATED_UNIVERSITIES

    def search_universities(self, query: str = "", country: str = "", max_tuition: Optional[int] = None,
                            min_acceptance_rate: Optional[float] = None, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        results = []
        q = query.strip().lower()
        c = country.strip().lower()

        for u in self.universities:
            if q and not (q in u["name"].lower() or any(q in p.lower() for p in u["popular_programs"]) or q in u["city"].lower()):
                continue
            if c and c != "all" and u["country"].lower() != c:
                continue
            if max_tuition and u["tuition_usd"] > max_tuition:
                continue
            if min_acceptance_rate and u["acceptance_rate"] < min_acceptance_rate:
                continue
            results.append(u)

        start = (page - 1) * limit
        return results[start:start + limit]

    def get_university_by_id(self, university_id: str) -> Optional[Dict[str, Any]]:
        for u in self.universities:
            if u["id"].lower() == university_id.lower() or u["name"].lower() == university_id.lower():
                return u
        return None

    def get_courses(self, university_id: str) -> List[Dict[str, Any]]:
        u = self.get_university_by_id(university_id)
        if not u:
            return []
        return [
            {
                "course_name": prog,
                "degree_level": "Masters",
                "duration_years": 2.0 if u["country"] in ["USA", "Canada", "Germany", "India"] else 1.0,
                "tuition_usd": u["tuition_usd"],
                "intake_months": ["August / September", "January"],
                "requirements": u["admission_requirements"]
            }
            for prog in u["popular_programs"]
        ]
