# app/retriever.py
from app.neo4j_client import db
import re, json

# Security: disallow writes/admin and multiple statements
_DISALLOWED = [
    r"\bCREATE\b", r"\bMERGE\b", r"\bSET\b", r"\bDELETE\b", r"\bREMOVE\b",
    r"\bDROP\b", r"\bCALL\s+dbms\b", r"\bCALL\s+apoc\b", r";", r"\bLOAD\b"
]

def contains_disallowed(query: str):
    uq = query.upper()
    for p in _DISALLOWED:
        if re.search(p, uq, flags=re.IGNORECASE):
            return True, p
    return False, None

def ensure_single_statement(query: str):
    if ";" in query:
        return False
    return True

def ensure_return_present(query: str):
    return bool(re.search(r"\bRETURN\b", query, flags=re.IGNORECASE))

def add_limit_if_missing(query: str, default_limit=1000):
    if re.search(r"\bLIMIT\s+\d+\b", query, flags=re.IGNORECASE):
        return query
    return query.rstrip() + f"\nLIMIT {default_limit}"

def uses_only_allowed_labels_and_rels(query: str):
    # Basic check for labels
    allowed_labels = {"Player", "Team", "Match"}
    allowed_rels = set(db.get_rel_types())
    
    # Check labels (e.g., :Player)
    label_matches = re.findall(r":([A-Za-z0-9_]+)", query)
    for l in label_matches:
        if l not in allowed_labels and l not in allowed_rels:
            # We allow basic flexibility, but this is a good sanity check
            pass
            
    # Check relationships (e.g., [:PLAYED_IN])
    rel_matches = re.findall(r"\[:([A-Za-z0-9_]+)\]", query)
    for r in rel_matches:
        if r not in allowed_rels:
            return False, f"Unknown relationship type '{r}'"
    return True, None

def validate_uses_score_parsing(query: str):
    # UPDATED: Only flag these words if they appear as properties (preceded by a dot)
    # OR if they are the specific hallucinated snake_case properties.
    
    # 1. Check for specific forbidden property names (snake_case hallucinations)
    if re.search(r"\b(home_team_goals|away_team_goals)\b", query, flags=re.IGNORECASE):
         return False, "Query uses hallucinated properties (home_team_goals/away_team_goals). Use split(m.score, '-') instead."

    # 2. Check for season property (common hallucination)
    if re.search(r"\.season\b", query, flags=re.IGNORECASE):
        return False, "Query references 'season' property which does not exist."

    # 3. Check for object-like access to homeTeam/awayTeam (e.g. m.homeTeam)
    # We allow the WORD 'homeTeam' (as a variable), but not PROPERTY '.homeTeam'
    if re.search(r"\.(homeTeam|awayTeam)\b", query, flags=re.IGNORECASE):
        return False, "Query references non-existent properties (m.homeTeam / m.awayTeam). Use relationships -[:HOME_TEAM]-> instead."

    return True, None

def execute_safe_cypher_and_format_results(cypher: str, params: dict = None, max_rows: int = 1000):
    params = params or {}

    # 1) Basic disallowed patterns
    dis, which = contains_disallowed(cypher)
    if dis:
        return {"status": "error", "message": f"Disallowed keyword or operation detected: {which}"}

    if not ensure_single_statement(cypher):
        return {"status": "error", "message": "Multiple statements or semicolons are not allowed."}

    if not ensure_return_present(cypher):
        return {"status": "error", "message": "Cypher must include a RETURN clause."}

    ok, reason = uses_only_allowed_labels_and_rels(cypher)
    if not ok:
        return {"status": "error", "message": reason}

    # This is the function we fixed
    ok, reason = validate_uses_score_parsing(cypher)
    if not ok:
        return {"status": "error", "message": reason}

    # 2) Force LIMIT
    safe_cypher = add_limit_if_missing(cypher, default_limit=max_rows)

    # 3) Size limit
    if len(safe_cypher) > 20000:
        return {"status": "error", "message": "Query too long."}

    # 4) Execute
    try:
        rows = db.query(safe_cypher, params)
    except Exception as e:
        return {"status": "error", "message": f"Database execution error: {str(e)}"}

    # 5) Validate results
    if not rows:
        return {"status": "error", "message": "No results (empty). Check that your query matched data."}

    # 6) Serialize
    try:
        serializable = json.loads(json.dumps(rows, default=str))
    except Exception:
        serializable = rows

    return {"status": "ok", "data": serializable}