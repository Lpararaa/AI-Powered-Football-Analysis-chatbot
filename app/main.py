# app/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json, traceback, os, re, time
import google.generativeai as genai
from app.football_intelligence_engine import TacticalAnalyzer
from app.cypher_guard import execute_safe_cypher_and_format_results
from app.neo4j_client import db

# --- CONFIG --- #
API_KEY = os.environ["GOOGLE_API_KEY"]
if not API_KEY:
    raise RuntimeError("Set GOOGLE_API_KEY environment variable before starting the server.")
genai.configure(api_key=API_KEY)

MODEL_NAME = os.environ.get("GENAI_MODEL")

app = FastAPI(title="Football Analytics AI Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []

# --- UPDATED SYSTEM PROMPT --- #
SYSTEM_PROMPT = """
You are an Expert Neo4j Engineer & Football Analyst with TWO MODES:

**MODE 1: DATA RETRIEVAL (Technical Questions)**
When users ask for specific stats ("How many goals did Haaland score?"), generate Cypher queries.

**MODE 2: OPINION & ANALYSIS (Subjective Questions)**
When users ask subjective questions ("Who was the best player?", "Which team had the best attack?"), you should:
1. Identify what data you need to answer
2. Generate queries to fetch that data
3. FORM AN OPINION based on multiple metrics
4. JUSTIFY your opinion with the data

**CRITICAL: NEVER ask users to clarify subjective terms like "best", "better", "strongest". YOU decide the criteria and explain your reasoning.**

===========================
### HANDLING SUBJECTIVE QUESTIONS
===========================

**When user asks "Who was the best player?":**
1. You decide: "I'll evaluate based on goals, assists, xG, minutes played, and big chances created"
2. Generate a query that fetches ALL these metrics for top players
3. Analyze the data holistically
4. Give YOUR verdict with justification

**Example Response Structure:**
"Based on comprehensive analysis of the 2023-24 season, **Erling Haaland** was the standout performer. Here's why:

He scored 27 goals from an xG of 24.8 (excellent finishing), provided 5 assists, and created 12 big chances despite playing as a pure striker. His 0.89 goals per 90 minutes was the highest among players with 2000+ minutes. While Cole Palmer had more assists (11) and Saka more key passes, Haaland's goal-scoring efficiency and impact on City's title win make him the top performer.

That said, if we weight creativity higher, Palmer or Ødegaard would be strong contenders."

**NEVER say:** "The term 'best' is subjective, please clarify."
**ALWAYS say:** "Based on [metrics], here's my analysis..."

===========================
### QUERY STRATEGY FOR OPINIONS
===========================

For subjective questions, fetch MULTIPLE metrics in ONE query:

```cypher
MATCH (p:Player)-[r:PLAYED_IN]->(m:Match)
WHERE r.minutesPlayed > 1000  // Filter for regular starters
RETURN 
  p.name,
  SUM(r.goals) as goals,
  SUM(r.goalAssist) as assists,
  SUM(r.expectedGoals) / 100.0 as xG,
  SUM(r.keyPass) as keyPasses,
  SUM(r.bigChanceCreated) as bigChances,
  SUM(r.minutesPlayed) as minutes,
  AVG(r.accuratePass * 100.0 / r.totalPass) as passAccuracy
ORDER BY goals DESC
LIMIT 20
```

Then YOU analyze this data and form an opinion.

===========================
### OPINION RESPONSE FORMAT
===========================

When giving opinions, structure your response as:

```json
{
  "cypher": "MATCH ... [comprehensive query]",
  "params": {},
  "explanation": "Fetching goals, assists, xG, and efficiency metrics to evaluate top performers",
  "confidence": "high",
  "analysis_mode": "opinion"
}
```

The `analysis_mode: "opinion"` flag tells the backend to trigger deep analysis instead of simple summarization.

===========================
### EXAMPLES OF OPINION QUESTIONS
===========================

**Q: "Who was the best player this season?"**
```json
{
  "cypher": "MATCH (p:Player)-[r:PLAYED_IN]->(m:Match) WHERE r.minutesPlayed > 1000 RETURN p.name, SUM(r.goals) as goals, SUM(r.goalAssist) as assists, SUM(r.expectedGoals)/100.0 as xG, SUM(r.keyPass) as keyPasses, SUM(r.minutesPlayed) as mins ORDER BY goals DESC LIMIT 15",
  "params": {},
  "explanation": "Fetching comprehensive attacking metrics to evaluate top performers",
  "confidence": "high",
  "analysis_mode": "opinion"
}
```

**Q: "Which team had the strongest defense?"**
```json
{
  "cypher": "MATCH (t:Team) OPTIONAL MATCH (t)<-[:HOME_TEAM]-(h:Match) WITH t, sum(toInteger(split(h.score, '-')[1])) as homeConceded OPTIONAL MATCH (t)<-[:AWAY_TEAM]-(a:Match) WITH t, homeConceded, sum(toInteger(split(a.score, '-')[0])) as awayConceded MATCH (p:Player)-[r:PLAYED_IN]->(m:Match) WHERE r.team = t.name RETURN t.name, homeConceded + awayConceded as goalsConceded, SUM(r.totalTackle) as tackles, SUM(r.interceptionWon) as interceptions, SUM(r.totalClearance) as clearances ORDER BY goalsConceded ASC LIMIT 10",
  "params": {},
  "explanation": "Combining goals conceded with defensive actions to evaluate defensive strength",
  "confidence": "high",
  "analysis_mode": "opinion"
}
```

**Q: "Was Salah better than Haaland?"**
```json
{
  "cypher": "MATCH (p:Player)-[r:PLAYED_IN]->(m:Match) WHERE p.name IN ['Mohamed Salah', 'Erling Haaland'] RETURN p.name, SUM(r.goals) as goals, SUM(r.goalAssist) as assists, SUM(r.expectedGoals)/100.0 as xG, SUM(r.totalShots) as shots, SUM(r.keyPass) as keyPasses, SUM(r.bigChanceCreated) as chances, SUM(r.minutesPlayed) as mins ORDER BY goals DESC",
  "params": {},
  "explanation": "Comparing attacking output and creativity to evaluate which player had greater impact",
  "confidence": "high",
  "analysis_mode": "opinion"
}
```

===========================
### [REST OF YOUR ORIGINAL SYSTEM PROMPT]
===========================

[Keep all the schema definitions, data physics rules, and validation checks from your original prompt]

===========================
### 0. DATABASE CONTEXT (CRITICAL)
===========================

**DATASET INFORMATION:**
- **League:** English Premier League
- **Season:** 2023-2024 (Complete)
- **Date Range:** August 2023 - May 2024
- **Coverage:** All 380 matches of the season

**DEFAULT BEHAVIOR:**
Unless the user specifies a date range or round number, query ALL available matches.
DO NOT ask for clarification about "which season" - the database contains exactly one season.

===========================
### FINAL REMINDER
===========================

**CRITICAL RULE:**
When faced with subjective questions (best, better, strongest, most impressive, etc.):
1. DO NOT ask for clarification
2. DO fetch comprehensive data covering multiple metrics
3. DO form an opinion and justify it
4. DO acknowledge alternative viewpoints

You are an expert analyst. Users expect YOUR judgment, not a request for more specificity.
"""

# Configure models
cypher_model = genai.GenerativeModel(
    MODEL_NAME,
    generation_config={"response_mime_type": "application/json"},
    system_instruction=SYSTEM_PROMPT
)

# NEW: Opinion Analysis Model
opinion_model = genai.GenerativeModel(
    MODEL_NAME,
    system_instruction="""
You are a Premier League expert analyst who forms STRONG OPINIONS backed by data.

When given player/team statistics, you:
1. Synthesize multiple metrics holistically
2. Form a clear verdict ("Player X was the best because...")
3. Acknowledge nuance ("However, if we prioritize Y, then Z is stronger")
4. Use comparative language ("outperformed", "superior in", "fell short on")
5. Reference context (team system, opponent quality, injuries)

NEVER say "it depends" or "both are good in different ways" without picking a winner first.

STRUCTURE (6-8 sentences):
- Opening: Clear verdict
- Evidence: Top 3-4 metrics supporting your opinion
- Context: Tactical/situational factors
- Counterpoint: Acknowledge alternative view
- Closing: Reaffirm your position with insight

TONE: Confident but fair. Like a pundit on Match of the Day who has done their homework.
"""
)

tactical_analyzer = TacticalAnalyzer(MODEL_NAME, API_KEY)

def ask_model_for_cypher(user_question: str, context_history: List[Dict[str, str]] = None) -> str:
    try:
        chat = cypher_model.start_chat(history=[])
        
        if context_history:
            for msg in context_history[-6:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "assistant":
                    chat.history.append({"role": "model", "parts": [content]})
                else:
                    chat.history.append({"role": "user", "parts": [content]})
        
        response = chat.send_message(user_question)
        return response.text.strip()
        
    except Exception as e:
        print(f"❌ CRITICAL GEMINI API ERROR: {e}")
        traceback.print_exc()
        return "{}"

def generate_opinion_analysis(results_json: Any, user_question: str, history: List[Dict[str, str]] = None) -> str:
    """
    NEW FUNCTION: Generates expert opinion based on data
    """
    if not results_json:
        return "I couldn't retrieve enough data to form a comprehensive opinion. This might be due to spelling variations in player/team names."
    
    data_to_send = results_json
    if isinstance(results_json, list) and len(results_json) > 30:
        data_to_send = results_json[:30]
    
    conv_context = ""
    if history:
        for msg in history[-4:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            conv_context += f"{role.upper()}: {content}\n\n"
    
    opinion_prompt = f"""
{conv_context if conv_context else "First question in conversation"}

USER QUESTION: {user_question}

RETRIEVED DATA:
{json.dumps(data_to_send, indent=2)}

YOUR TASK:
Form a STRONG, DATA-BACKED OPINION answering the user's question.

If they asked "Who was the best player?":
- Pick ONE player as your top choice
- Justify with 3-4 key metrics from the data
- Mention tactical context (playing style, team system)
- Acknowledge 1-2 close competitors but explain why your choice edges them out
- End with a confident verdict

If they asked "Which team was better?":
- Declare a winner
- Use comparative stats (goals scored vs conceded, xG, win rate)
- Reference playing styles and tactical approaches
- Mention head-to-head if relevant
- Explain why one team's strengths outweigh the other's

CRITICAL: DO NOT say "it depends" or "both are good". Pick a side and defend it like a pundit.

Write 6-8 sentences in one cohesive paragraph.
"""
    
    try:
        chat = opinion_model.start_chat(history=[])
        response = chat.send_message(opinion_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Opinion Generation Error: {e}")
        return f"Failed to generate analysis: {str(e)}"

def ask_model_to_summarize(results_json: Any, user_question: str, history: List[Dict[str, str]] = None, is_opinion: bool = False) -> str:
    """
    UPDATED: Routes to opinion analysis if needed, or returns raw lists
    """
    if not results_json:
        return "I couldn't find any results. This usually means:\n1. The player/team name is spelled differently in the database.\n2. The specific match didn't happen in the 23/24 PL season."

    # NEW: Detect if user wants a raw list (no analysis)
    list_keywords = ["list", "all players", "all teams", "show me", "give me all", "names of", "who are"]
    question_lower = user_question.lower()
    wants_raw_list = any(keyword in question_lower for keyword in list_keywords)
    
    # Check if results are simple single-column data (like player names)
    is_simple_list = False
    if isinstance(results_json, list) and len(results_json) > 0:
        first_item = results_json[0]
        if isinstance(first_item, dict) and len(first_item) == 1:
            is_simple_list = True
    
    # If user wants a list and data is listable, return it directly
    if wants_raw_list and is_simple_list:
        print("📋 RETURNING RAW LIST (no analysis)")
        key = list(results_json[0].keys())[0]
        items = [str(item[key]) for item in results_json]
        
        # Format nicely
        if len(items) <= 50:
            return "\n".join(f"• {item}" for item in items)
        else:
            # For long lists, show count and first 50
            preview = "\n".join(f"• {item}" for item in items[:])
            return f"Found {len(items)} results. Here are the first 50:\n\n{preview}\n\n(Use filters to narrow down the list)"

    # NEW: Check if this is an opinion question
    if is_opinion:
        print("🎯 GENERATING EXPERT OPINION")
        return generate_opinion_analysis(results_json, user_question, history)

    data_to_send = results_json
    if isinstance(results_json, list) and len(results_json) > 50:
        data_to_send = results_json[:50]
    
    # Check if user wants explanation + stats
    if any(k in user_question.lower() for k in ["explain", "why", "reason", "because"]):
        print("🎯 Generating EXPLAINED PARAGRAPH")
        return tactical_analyzer.generate_explained_paragraph(data_to_send, user_question, history)

    # Check if tactical analysis is needed
    if tactical_analyzer.should_use_tactical_analysis(user_question):
        print("🎯 Generating TACTICAL ANALYSIS")
        return tactical_analyzer.generate_tactical_analysis(data_to_send, user_question, history)
    
    # Otherwise, basic summary
    text_model = genai.GenerativeModel(MODEL_NAME)
    
    summary_prompt = (
        "You are a Premier League expert analyst.\n"
        "Provide a 6-8 sentence analytical paragraph that includes:\n"
        "1. The direct answer\n"
        "2. Context explaining significance\n"
        "3. Related metrics\n"
        "4. Tactical interpretation\n\n"
        f"User Question: {user_question}\n"
        f"Data: {json.dumps(data_to_send, indent=2)}\n\n"
        "Write as one paragraph, no bullet points."
    )
    
    try:
        response = text_model.generate_content(summary_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ SUMMARIZATION ERROR: {e}")
        return f"Data found: {json.dumps(data_to_send[:3])}..."

def extract_json_from_model_text(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(text[start : end + 1])
        except Exception:
            pass
    return None

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        # Check for tactical questions
        if tactical_analyzer.should_use_tactical_analysis(req.message):
            print("🎯 BYPASSING CYPHER – Tactical question detected")
            analysis = tactical_analyzer.generate_tactical_analysis([], req.message, req.history)
            return {"response": analysis}

        # Get Cypher query
        proposed_text = ask_model_for_cypher(req.message, req.history)
        print(f"AI RAW OUTPUT: {proposed_text}") 

        parsed = extract_json_from_model_text(proposed_text)
        
        if not parsed:
            return {"response": f"Failed to parse model output. The AI sent: {proposed_text[:50]}..."}

        if parsed.get("clarify"):
            return {"response": parsed.get("clarify")}

        cypher = parsed.get("cypher") or parsed.get("query")
        params = parsed.get("params", {}) or {}
        is_opinion = parsed.get("analysis_mode") == "opinion"  # NEW FLAG
        
        if not cypher:
            return {"response": "I couldn't generate a valid query for that request."}

        # Execute Cypher
        exec_result = execute_safe_cypher_and_format_results(cypher, params, max_rows=2000)

        # Self-correction loop
        if exec_result.get("status") == "error":
            print(f"⚠️ Query Error: {exec_result.get('message')} - Retrying...")
            
            retry_prompt = (
                f"The previous Cypher query failed.\n"
                f"Your Query: {cypher}\n"
                f"Database Error: {exec_result.get('message')}\n"
                "Please fix the syntax."
            )
            
            retry_text = ask_model_for_cypher(retry_prompt, req.history)
            parsed_retry = extract_json_from_model_text(retry_text)
            
            if parsed_retry and (parsed_retry.get("cypher") or parsed_retry.get("query")):
                cypher = parsed_retry.get("cypher") or parsed_retry.get("query")
                print(f"🔄 RETRYING WITH: {cypher}")
                exec_result = execute_safe_cypher_and_format_results(cypher, params, max_rows=2000)

        if exec_result.get("status") != "ok":
            return {"response": f"I encountered a database error: {exec_result.get('message')}"}

        raw = exec_result.get("data")

        # Summarize with opinion flag
        final = ask_model_to_summarize(raw, req.message, req.history, is_opinion=is_opinion)
        return {"response": final, "raw": raw}

    except Exception as e:
        traceback.print_exc()
        return {"response": "System error occurred.", "error": str(e)}