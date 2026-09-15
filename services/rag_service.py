import os
import re
from typing import Dict, Any, List
from django.conf import settings

KNOWLEDGE_CHUNKS = [
    {
        "source": "US F-1 Visa Guidelines 2026",
        "topic": "visa",
        "content": "F-1 visa applicants must show liquid funds covering at least 1 year of total tuition and living costs as stated on Form I-20. Acceptable funds include bank balances, fixed deposits, education loan sanction letters, and government sponsorships. Real estate property cannot be shown as liquid funds."
    },
    {
        "source": "UK Student Route Visa Rules",
        "topic": "visa",
        "content": "UK Student visa requires 70 points: 50 points for Confirmation of Acceptance for Studies (CAS), 10 points for English language requirement, and 10 points for financial requirement (£1,334/month for London, £1,023/month outside London held for 28 consecutive days)."
    },
    {
        "source": "Education Loan Tax Deductions (Section 80E)",
        "topic": "finance",
        "content": "Under Section 80E of the Indian Income Tax Act, 100% of the interest paid on education loans taken for higher education from scheduled banks (such as SBI, HDFC, ICICI, Axis) is fully tax-deductible for up to 8 continuous financial years with no upper monetary cap."
    },
    {
        "source": "Top US STEM OPT Extensions",
        "topic": "career",
        "content": "Graduates of designated STEM degree programs (Computer Science, Data Science, Electrical Engineering, Business Analytics) are eligible for a 24-month STEM OPT extension in addition to the standard 12-month post-completion OPT, allowing 3 total years of legal employment in the US without an H-1B visa."
    },
    {
        "source": "Carnegie Mellon University Admissions Guide",
        "topic": "admissions",
        "content": "CMU School of Computer Science prioritizes mathematical maturity, linear algebra, discrete math, and significant systems programming experience in C/C++/Python. Average admitted student GRE quant is 168+ with an undergraduate CGPA above 3.7/4.0."
    },
    {
        "source": "German Public University Tuition Rules",
        "topic": "universities",
        "content": "Most public universities in Germany (such as RWTH Aachen, TU Berlin, University of Stuttgart) charge zero tuition fees for international students, requiring only a semester administrative fee of €250 - €350 which covers regional public transport. Blocked account requirement is approximately €11,208 per year."
    }
]

def retrieve_relevant_chunks(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Simple keyword-overlap ranking over knowledge base chunks."""
    query_tokens = set(re.findall(r'\w+', query.lower()))
    scored = []
    for chunk in KNOWLEDGE_CHUNKS:
        chunk_tokens = set(re.findall(r'\w+', chunk["content"].lower() + " " + chunk["source"].lower()))
        overlap = len(query_tokens & chunk_tokens)
        if overlap > 0:
            scored.append((overlap, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_k]]

def answer_rag_query(query: str, user_profile: Dict[str, Any], chat_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Synthesizes an advisor response combining:
    1. Student profile context
    2. Retrieved knowledge chunks
    3. LLM generation (Anthropic Claude with fallback)
    """
    chunks = retrieve_relevant_chunks(query, top_k=2)
    sources = [c["source"] for c in chunks]

    # Build context string
    context_str = "\n".join([f"[{c['source']}]: {c['content']}" for c in chunks])
    profile_summary = f"""
Student Profile Context:
- Name: {user_profile.get('name', 'Student')}
- Target Country: {user_profile.get('country_goal', 'USA')}
- Degree Goal: {user_profile.get('degree', 'MS')}
- Undergraduate GPA: {user_profile.get('gpa', '3.3')}
- Budget: {user_profile.get('budget', 'Moderate')}
"""

    system = f"""You are EduBridge AI — an expert, encouraging study-abroad and higher education advisor.
Use the student profile and knowledge citations below to deliver a precise, tailored, highly actionable response.
Avoid cheesy emojis; use professional formatting, markdown bullet points, and data tables where helpful.

{profile_summary}

Relevant Knowledge Base Citations:
{context_str}
"""

    # 1. First priority: Groq LLM Engine (ultra-fast inference)
    groq_api_key = getattr(settings, "GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
    preferred_model = getattr(settings, "GROQ_MODEL", "") or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    if groq_api_key:
        candidate_models = [
            preferred_model,
            "openai/gpt-oss-120b",
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile"
        ]
        # Deduplicate while preserving order
        unique_models = []
        for m in candidate_models:
            if m and m not in unique_models:
                unique_models.append(m)

        msgs = [{"role": "system", "content": system}]
        if chat_history:
            for m in chat_history[-6:]:
                msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})
        msgs.append({"role": "user", "content": query})

        for model_name in unique_models:
            try:
                try:
                    from groq import Groq
                    client = Groq(api_key=groq_api_key)
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=msgs,
                        temperature=0.5,
                        max_tokens=900
                    )
                    answer_text = response.choices[0].message.content
                    if answer_text:
                        print(f"[EduBridge] (OK) Groq generated response via {model_name}")
                        return {
                            "answer": answer_text,
                            "sources": sources
                        }
                except ImportError:
                    import requests
                    resp = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {groq_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model_name,
                            "messages": msgs,
                            "temperature": 0.5,
                            "max_tokens": 900
                        },
                        timeout=15
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        answer_text = data["choices"][0]["message"]["content"]
                        if answer_text:
                            print(f"[EduBridge] (OK) Groq generated response via {model_name} (HTTP)")
                            return {
                                "answer": answer_text,
                                "sources": sources
                            }
            except Exception as err:
                print(f"[EduBridge] Groq model '{model_name}' attempt failed: {err}")
                continue

    # 2. Second priority: Anthropic Claude
    api_key = getattr(settings, "ANTHROPIC_API_KEY", "") or os.getenv("ANTHROPIC_API_KEY", "")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            msgs = []
            if chat_history:
                for m in chat_history[-6:]:
                    msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})
            msgs.append({"role": "user", "content": query})

            r = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=850,
                system=system,
                messages=msgs
            )
            return {
                "answer": r.content[0].text,
                "sources": sources
            }
        except Exception:
            pass

    # Intelligent offline synthesized response
    q_low = query.lower()
    if any(w in q_low for w in ["visa", "f1", "f-1", "cas", "embassy", "i-20"]):
        ans = f"Regarding visa planning for **{user_profile.get('country_goal', 'USA')}**:\n\n" \
              f"- **Financial Proof:** You must document 1 full year of liquid tuition and living expenses prior to visa interview.\n" \
              f"- **Acceptable Funding:** Fixed deposits, bank balances, or education loan sanction letters from recognized lenders.\n" \
              f"- **Timeline:** Book your visa slot 3 to 4 months before your intended start term once your admission I-20 / CAS is issued."
    elif any(w in q_low for w in ["loan", "finance", "bank", "cost", "emi", "fee"]):
        ans = f"Financial assessment for **{user_profile.get('name', 'your profile')}**:\n\n" \
              f"- **Recommended Lenders:** SBI Global Ed-Vantage (10.15% secured) or HDFC Credila / Avanse (unsecured up to ₹50L).\n" \
              f"- **Section 80E Benefit:** All interest paid is 100% tax-deductible for 8 years under Indian tax code.\n" \
              f"- **Next Action:** Obtain loan pre-approval before your university deposit deadline to avoid disbursement delays."
    elif any(w in q_low for w in ["university", "shortlist", "safe", "target", "reach", "cmu", "stanford", "mit"]):
        ans = f"Based on your profile GPA ({user_profile.get('gpa', '3.3')}) and interest in **{user_profile.get('country_goal', 'USA')}**:\n\n" \
              f"- **Reach Tier:** Carnegie Mellon University (CMU), Stanford, MIT (Target rank 1-20).\n" \
              f"- **Target Tier:** Georgia Tech, UT Austin, University of Toronto (Target rank 20-60).\n" \
              f"- **Safety Tier:** Northeastern University, Arizona State, University of British Columbia.\n\n" \
              f"Would you like to run an ML admission simulation for one of these specific universities?"
    else:
        ans = f"Hello {user_profile.get('name', '')}! I have analyzed your target country (**{user_profile.get('country_goal', 'USA')}**) " \
              f"and degree program (**{user_profile.get('degree', 'MS')}**).\n\n" \
              f"I can guide you across:\n" \
              f"- Real-time university matching and admission odds\n" \
              f"- Education loan comparison and Section 80E tax optimization\n" \
              f"- Statement of Purpose (SOP) critiques and faculty alignment\n" \
              f"- F-1 / UK / German student visa interview preparation.\n\n" \
              f"What specific milestone would you like to review today?"

    return {
        "answer": ans,
        "sources": sources if sources else ["EduBridge Curated Higher Education Knowledge Graph"]
    }
