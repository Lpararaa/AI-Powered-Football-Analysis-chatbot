# app/tactical_analyzer.py
import google.generativeai as genai
import json
from typing import Dict, Any, List

class TacticalAnalyzer:
    """
    Expert Football Analyst with deep tactical knowledge
    Combines database stats with football intelligence
    """
    
    def __init__(self, model_name: str, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name,
            system_instruction="""
You are Michael Cox (The Athletic's Chief Tactical Analyst) meets Pep Guardiola's analyst team.

YOUR EXPERTISE:
- 20+ years analyzing Premier League tactics
- Deep knowledge of team playing styles, manager philosophies, formations
- Understanding of tactical trends (pressing, buildup patterns, transitions)
- Familiarity with player profiles (Haaland = poacher, Salah = inside forward, etc.)
- Context of the 2023-24 PL season (City dominance, Arsenal's challenge, etc.)

WHEN ANALYZING:
1. **Use Your Football Knowledge FIRST**
   - You already KNOW that Guardiola plays possession-based football
   - You already KNOW that Arsenal uses inverted fullbacks
   - You already KNOW that Haaland is a penalty box specialist
   
2. **Then Use Data to PROVE Your Analysis**
   - Don't say "The data shows Arsenal had possession"
   - Say "Arsenal's typical possession-based approach is confirmed by their 68% ball retention"
   
3. **Connect Individual Stats to Team Systems**
   - If Saka scores, explain it through Arsenal's tactical setup
   - If De Bruyne assists, connect it to City's positional play
   
4. **Provide Historical Context**
   - Compare current stats to player/team norms
   - Reference tactical evolution ("This is higher than their usual pressing intensity")

5. **Think Like a Scout**
   - When analyzing players, assess tactical fit
   - Identify strengths/weaknesses in system context

YOUR TONE:
Professional but engaging. Like you're writing for The Athletic, not a textbook.
Use phrases like:
- "What's fascinating here is..."
- "This tells us that..."
- "The underlying story..."
- "In tactical terms, this means..."

FORBIDDEN:
- Generic statements ("they played well")
- Just repeating numbers without interpretation
- Ignoring your football knowledge
- Treating every team/player as unknown

REMEMBER:
You're not a data analyst who happens to know football.
You're a football expert who uses data to support your analysis.
"""
        )
        
        # Premier League 2023-24 Context Knowledge Base
        self.pl_context = {
            "teams": {
                "Manchester City": {
                    "style": "Possession-based positional play, high defensive line, inverted fullbacks",
                    "manager": "Pep Guardiola",
                    "key_players": ["Haaland (clinical finisher)", "De Bruyne (creative hub)", "Rodri (defensive anchor)"],
                    "tactical_identity": "Control through possession, patient buildup, exploiting half-spaces"
                },
                "Arsenal": {
                    "style": "High pressing, quick transitions, width from inverted fullbacks",
                    "manager": "Mikel Arteta (ex-Guardiola assistant)",
                    "key_players": ["Saka (inverted winger)", "Ødegaard (8/10 hybrid)", "Saliba (ball-playing CB)"],
                    "tactical_identity": "Guardiola principles with more directness"
                },
                "Liverpool": {
                    "style": "Gegenpressing, vertical transitions, fullback overloads",
                    "manager": "Jürgen Klopp",
                    "key_players": ["Salah (inside forward)", "Van Dijk (defensive leader)", "Alexander-Arnold (creative fullback)"],
                    "tactical_identity": "High-intensity pressing, quick counter-attacks"
                },
                "Chelsea": {
                    "style": "Varied (multiple managers), focus on youth development",
                    "tactical_identity": "Transitional season, tactical identity in flux"
                },
                "Manchester United": {
                    "style": "Counter-attacking, direct play",
                    "manager": "Erik ten Hag",
                    "tactical_identity": "Vertical passing, pressing in phases"
                },
                "Tottenham": {
                    "style": "Counter-attacking, compact defending",
                    "manager": "Ange Postecoglou (2023-24)",
                    "tactical_identity": "High defensive line, aggressive pressing under Postecoglou"
                }
            },
            
            "player_archetypes": {
                "Erling Haaland": "Pure penalty box striker - elite finishing, minimal buildup involvement",
                "Mohamed Salah": "Inside forward - cuts inside from right, high-volume shooter",
                "Bukayo Saka": "Inverted winger - dribbling threat, final third creativity",
                "Kevin De Bruyne": "Advanced playmaker - through balls, chance creation from deep",
                "Declan Rice": "Defensive midfielder - ball progression, defensive stability",
                "Bruno Fernandes": "Risk-taking 10 - high creativity, high turnover rate"
            },
            
            "tactical_trends_2023_24": [
                "Increased use of inverted fullbacks (City, Arsenal)",
                "High defensive lines becoming standard",
                "Emphasis on progressive passing over possession for possession's sake",
                "Pressing in organized structures rather than chaotic chasing"
            ]
        }
    
    def should_use_tactical_analysis(self, question: str) -> bool:
        """Detects if question requires deep tactical analysis"""
        tactical_keywords = [
            "analyze", "analysis", "tactical", "how did", "why did",
            "explain", "performance", "style", "approach", "battle",
            "strategy", "formation", "pressing", "buildup", "transition",
            "compare", "vs", "versus", "difference between"
        ]
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in tactical_keywords)
    
    def _get_team_context(self, team_name: str) -> str:
        """Get tactical context for a specific team"""
        context = self.pl_context["teams"].get(team_name, {})
        if context:
            return f"""
TEAM CONTEXT - {team_name}:
- Playing Style: {context.get('style', 'N/A')}
- Manager: {context.get('manager', 'N/A')}
- Tactical Identity: {context.get('tactical_identity', 'N/A')}
- Key Players: {', '.join(context.get('key_players', []))}
"""
        return ""
    
    def _get_player_context(self, player_name: str) -> str:
        """Get tactical profile for a specific player"""
        profile = self.pl_context["player_archetypes"].get(player_name, "")
        if profile:
            return f"\nPLAYER PROFILE - {player_name}: {profile}\n"
        return ""
    
    def _extract_entities(self, question: str, data: Any) -> Dict[str, List[str]]:
        """Extract teams and players mentioned in question or data"""
        entities = {"teams": [], "players": []}
        
        question_lower = question.lower()
        
        # Check for teams
        for team in self.pl_context["teams"].keys():
            if team.lower() in question_lower:
                entities["teams"].append(team)
        
        # Check for players
        for player in self.pl_context["player_archetypes"].keys():
            if player.lower() in question_lower:
                entities["players"].append(player)
        
        # Extract from data if available
        if isinstance(data, list) and data:
            first_row = data[0]
            # Check for team names in data
            for key, value in first_row.items():
                if isinstance(value, str):
                    for team in self.pl_context["teams"].keys():
                        if team in value and team not in entities["teams"]:
                            entities["teams"].append(team)
                    # Check player names
                    for player in self.pl_context["player_archetypes"].keys():
                        if player in value and player not in entities["players"]:
                            entities["players"].append(player)
        
        return entities
    
    def generate_tactical_analysis(
        self, 
        data: Any, 
        question: str, 
        history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generates expert tactical analysis combining data + football knowledge
        """
        
        # Prepare data
        data_preview = data[:10] if isinstance(data, list) else data
        
        # Extract entities (teams/players mentioned)
        entities = self._extract_entities(question, data_preview)
        
        # Build contextual knowledge
        context_knowledge = ""
        
        # Add team contexts
        for team in entities["teams"]:
            context_knowledge += self._get_team_context(team)
        
        # Add player contexts
        for player in entities["players"]:
            context_knowledge += self._get_player_context(player)
        
        # Add general tactical trends
        if entities["teams"] or entities["players"]:
            context_knowledge += f"""
2023-24 PREMIER LEAGUE TACTICAL TRENDS:
{chr(10).join(f"- {trend}" for trend in self.pl_context["tactical_trends_2023_24"])}
"""
        
        # Build conversation history
        conv_context = ""
        if history:
            recent_history = history[-4:]
            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                conv_context += f"{role.upper()}: {content}\n\n"
        
        # Prepare data string
        data_str = json.dumps(data_preview, indent=2) if data_preview else "No specific match data provided."
        
        # Build the expert prompt
        prompt = f"""
CONVERSATION HISTORY:
{conv_context if conv_context else "First question in conversation"}

TACTICAL CONTEXT (YOUR EXISTING KNOWLEDGE):
{context_knowledge if context_knowledge else "General Premier League knowledge"}

CURRENT QUESTION:
{question}

DATABASE STATS:
{data_str}

YOUR TASK:
As an expert tactical analyst, provide deep analysis that:

1. **Starts with Your Football Knowledge**
   - Use what you know about these teams/players/managers
   - Reference their typical playing styles
   - Mention their tactical identities

2. **Then Support with Data**
   - Use stats to PROVE your tactical assessment
   - Don't just list numbers - explain what they reveal tactically
   - Connect stats to system/style

3. **Provide Causal Explanations**
   - Explain WHY results happened (tactics, not luck)
   - Use phrases: "This is because...", "The reason is...", "This happened due to..."

4. **Compare to Norms**
   - Is this typical for this team/player?
   - How does it compare to their usual performance?
   - What's different/surprising?

5. **Tactical Terminology**
   - Use proper football language (pressing triggers, half-spaces, build-up patterns, transitions)
   - Explain formations, shape, movement patterns

STRUCTURE (5-8 sentences):
- Opening: Context of who these teams/players are tactically
- Middle: What the stats reveal + WHY
- Closing: Tactical verdict or insight

EXAMPLE GOOD ANALYSIS:
"Arsenal, under Arteta's Guardiola-influenced system, typically dominates possession through patient buildup. Their 89% pass accuracy in the opposition half confirms this approach was in full effect against Chelsea. What's particularly telling is their 12 turnovers forced in the final third - this high pressing intensity is a deliberate tactical evolution from their earlier, more cautious style. Saka's 2 goals from xG positions of 0.8 and 0.6 weren't fortunate strikes; they're the direct result of Arsenal's systematic creation of overloads in wide areas, pulling Chelsea's compact shape apart. This tactical superiority is exactly why Arteta's side challenged City for the title."

EXAMPLE BAD ANALYSIS:
"Arsenal had 68% possession and won 3-1. Saka scored 2 goals. They created more chances."

NOW ANALYZE:
"""
        
        try:
            chat = self.model.start_chat(history=[])
            response = chat.send_message(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"❌ Tactical Analysis Error: {e}")
            return f"Failed to generate analysis: {str(e)}"
    
    def generate_explained_paragraph(
        self, 
        data: Any, 
        question: str,
        history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generates expert explanation paragraph mixing stats + tactical knowledge
        """
        short_data = data[:10] if isinstance(data, list) else data
        entities = self._extract_entities(question, short_data)
        
        # Build context
        context_knowledge = ""
        for team in entities["teams"]:
            context_knowledge += self._get_team_context(team)
        for player in entities["players"]:
            context_knowledge += self._get_player_context(player)
        
        # Conversation history
        conv_context = ""
        if history:
            recent_history = history[-4:]
            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                conv_context += f"{role.upper()}: {content}\n\n"
        
        data_str = json.dumps(short_data, indent=2)
        
        prompt = f"""
{conv_context if conv_context else "First question"}

YOUR FOOTBALL KNOWLEDGE:
{context_knowledge if context_knowledge else "General PL knowledge"}

QUESTION: {question}

DATA: {data_str}

Write ONE PARAGRAPH (5-7 sentences) that:
- Opens with WHO these players/teams are tactically
- Explains the stat in context of their style
- Uses football intelligence to interpret numbers
- Provides tactical reasoning for WHY
- Compares to their typical performance if relevant
- Sounds like Michael Cox or Jonathan Wilson

Use your knowledge of formations, playing styles, manager philosophies.
Don't just report stats - explain them through tactical lens.
"""

        try:
            chat = self.model.start_chat(history=[])
            response = chat.send_message(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"❌ Explanation Error: {e}")
            return f"Failed to explain: {str(e)}"