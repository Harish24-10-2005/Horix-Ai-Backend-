#!/usr/bin/env python3
"""
Red Hat API MCP Server - CORRECTED VERSION

This MCP server implements tools to interact with Red Hat APIs:
1. Search Red Hat KCS Solutions
2. Get a Solution by ID
3. Search Red Hat Cases
4. Get Case details

The server uses the Model Context Protocol (MCP) to expose these tools to LLM applications.

FIXES:
- Fixed credential handling to match the exact structure from your debug output
- The credentials come as: {"__credentials__": {"offline_token": "...", "access_token": "", "token_expiry": ""}}
- Simplified credential extraction logic
- Added better error handling and debugging
"""

from typing import Optional, List, Dict, Any
import httpx
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
import json


# Create MCP server
mcp = FastMCP("RedHat API", description="Interact with Red Hat KCS and Case APIs", version="1.0.2")

# Configuration
class RedHatAPI:
    """Red Hat API client with authentication and request handling."""
    
    def __init__(self):
        self.base_url = "https://access.redhat.com"
        self.sso_url = "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"
        
    async def get_access_token(self, credentials: Optional[Dict[str, Any]] = None) -> str:
        """Get a valid access token, refreshing if necessary."""
        
        if not credentials:
            raise ValueError("credentials are required")

        access_token = credentials.get("access_token")
        token_expiry_str = credentials.get("token_expiry")
        
        token_expiry = None
        if token_expiry_str:
            try:
                # Attempt to parse ISO format string
                token_expiry = datetime.fromisoformat(token_expiry_str)
            except (TypeError, ValueError):
                # Invalid format, so refresh token
                token_expiry = None

        if access_token and access_token != "" and token_expiry and datetime.now() < token_expiry:
            return access_token

        offline_token = credentials.get("offline_token")
        if not offline_token:
            raise ValueError("offline_token is required in credentials")

        # Refresh token
        async with httpx.AsyncClient() as client:
            payload = {  
                "grant_type": "refresh_token",
                "client_id": "rhsm-api",
                "refresh_token": offline_token
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            response = await client.post(self.sso_url, data=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            new_access_token = data["access_token"]
            # Set expiry time slightly before actual expiry to be safe
            new_token_expiry = datetime.now() + timedelta(seconds=data["expires_in"] - 60)
            
            # Store back in credentials dict for caching within the same request/context
            credentials["access_token"] = new_access_token
            credentials["token_expiry"] = new_token_expiry.isoformat()
            
            return new_access_token
    
    async def make_request(self, method: str, path: str, data: Optional[Dict] = None, credentials: Optional[Dict[str, Any]] = None) -> Dict:
        """Make an authenticated request to the Red Hat API."""
        token = await self.get_access_token(credentials)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{path}"
        
        async with httpx.AsyncClient() as client:
            if method.lower() == "get":
                response = await client.get(url, headers=headers)
            elif method.lower() == "post":
                response = await client.post(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            
            # Handle both JSON responses and text responses
            if "application/json" in response.headers.get("content-type", ""):
                return response.json()
            return {"content": response.text}

# Initialize API client
rhapi = RedHatAPI()

def _get_rh_creds(credentials: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Extracts Red Hat credentials from the request - FIXED VERSION."""
    if not credentials:
        raise ValueError("Credentials not found in request.")
    
    # Debug: Print the credentials structure (remove in production)
    print(f"DEBUG: Received credentials structure: {json.dumps(credentials, indent=2)}")
    
    # CORRECTED: Based on your debug output, the structure is:
    # {"__credentials__": {"offline_token": "...", "access_token": "", "token_expiry": ""}}
    
    # First, check if __credentials__ exists and extract it
    if "__credentials__" in credentials:
        inner_creds = credentials["__credentials__"]
        
        # Check if this inner_creds has offline_token directly
        if isinstance(inner_creds, dict) and "offline_token" in inner_creds:
            print(f"DEBUG: Found offline_token in __credentials__: {inner_creds['offline_token'][:50]}...")
            return inner_creds
        else:
            raise ValueError(f"__credentials__ found but no offline_token inside. Keys: {list(inner_creds.keys()) if isinstance(inner_creds, dict) else 'Not a dict'}")
    
    # Fallback: Check if offline_token is directly in credentials
    elif "offline_token" in credentials:
        print(f"DEBUG: Found offline_token directly in credentials: {credentials['offline_token'][:50]}...")
        return credentials
    
    # Final fallback: Check for REDHAT_MCP structure
    elif "REDHAT_MCP" in credentials:
        rh_creds = credentials["REDHAT_MCP"]
        if isinstance(rh_creds, dict) and "offline_token" in rh_creds:
            print(f"DEBUG: Found offline_token in REDHAT_MCP: {rh_creds['offline_token'][:50]}...")
            return rh_creds
        else:
            raise ValueError(f"REDHAT_MCP found but no offline_token inside. Keys: {list(rh_creds.keys()) if isinstance(rh_creds, dict) else 'Not a dict'}")
    
    else:
        raise ValueError(f"No valid credential structure found. Available keys: {list(credentials.keys())}")

@mcp.tool()
async def search_kcs(query: str, rows: int = 50, start: int = 0, credentials: Optional[Dict[str, Any]] = None) -> List[Dict]:
    """
    Search for Red Hat KCS Solutions and return a list with Solution IDs.
    
    Args:
        query: Search query string
        rows: Number of results to return (default: 50)
        start: Starting index for pagination (default: 0)
        credentials: Authentication credentials containing offline_token
        
    Returns:
        List of solutions with their IDs and metadata
    
    By default, this tool returns only documents where documentKind is either "Article" or "Solution" and accessState is either "active" or "private".
    """
    try:
        print(f"DEBUG: search_kcs called with query: {query}")
        rh_creds = _get_rh_creds(credentials)
        path = "/hydra/rest/search/v2/kcs"
        
        data = {
            "q": query,
            "rows": rows,
            "expression": "sort=score%20DESC&fq=documentKind%3A(%22Article%22%20OR%20%22Solution%22)%20AND%20accessState%3A(%22active%22%20OR%20%22private%22)&fl=allTitle%2CcaseCount%2CdocumentKind%2C%5Belevated%5D%2ChasPublishedRevision%2Cid%2Clanguage%2ClastModifiedDate%2CModerationState%2Cscore%2Curi%2Cresource_uri%2Cview_uri%2CcreatedDate&showRetired=false",
            "start": start,
            "clientName": "mcp"
        }
        
        print(f"DEBUG: Making request to {path} with data: {data}")
        result = await rhapi.make_request("post", path, data, credentials=rh_creds)
        print(f"DEBUG: Got result: {json.dumps(result, indent=2)[:500]}...")
        
        # Format the response to include only relevant information
        solutions = []
        if "response" in result and "docs" in result["response"]:
            for doc in result["response"]["docs"]:
                solution = {
                    "id": doc.get("id"),
                    "title": doc.get("allTitle"),
                    "score": doc.get("score"),
                    "view_uri": doc.get("view_uri"),
                    "document_kind": doc.get("documentKind"),
                    "last_modified": doc.get("lastModifiedDate")
                }
                solutions.append(solution)
        
        print(f"DEBUG: Returning {len(solutions)} solutions")
        return solutions
    
    except Exception as e:
        print(f"ERROR in search_kcs: {str(e)}")
        print(f"ERROR type: {type(e)}")
        import traceback
        print(f"ERROR traceback: {traceback.format_exc()}")
        raise e

@mcp.tool()
async def get_kcs(solution_id: str, credentials: Optional[Dict[str, Any]] = None) -> Dict:
    """Get a specific solution by ID and extract structured content

    Args:
        solution_id: The ID of the solution to retrieve
        credentials: Authentication credentials containing offline_token

    Returns:
        Dictionary with title, Environment, Issue, Resolution, and Root Cause
    """
    try:
        print(f"DEBUG: get_kcs called with solution_id: {solution_id}")
        rh_creds = _get_rh_creds(credentials)
        # Use the KCS search API to get the solution data
        path = "/hydra/rest/search/v2/kcs"
        
        data = {
            "q": f"id:{solution_id}",
        }
        
        print(f"DEBUG: Making request to {path} with data: {data}")
        result = await rhapi.make_request("post", path, data, credentials=rh_creds)
        
        # Check if we got a result
        if not result or "response" not in result or "docs" not in result["response"] or not result["response"]["docs"]:
            print(f"DEBUG: No results found for solution_id: {solution_id}")
            return {
                "title": "",
                "environment": "",
                "issue": "",
                "resolution": "",
                "root_cause": ""
            }
        
        # Extract the solution data from the first document
        doc = result["response"]["docs"][0]
        print(f"DEBUG: Found solution document: {json.dumps(doc, indent=2)[:500]}...")
        
        # Initialize the result dictionary
        solution_data = {
            "title": doc.get("publishedTitle", ""),
            "environment": doc.get("standard_product", ""),
            "issue": doc.get("issue", ""),
            "resolution": doc.get("solution_resolution", ""),
            "root_cause": doc.get("solution_rootcause", ""),
        }
        
        print(f"DEBUG: Returning solution data: {solution_data}")
        return solution_data
    
    except Exception as e:
        print(f"ERROR in get_kcs: {str(e)}")
        print(f"ERROR type: {type(e)}")
        import traceback
        print(f"ERROR traceback: {traceback.format_exc()}")
        raise e

@mcp.tool()
async def search_cases(query: str, rows: int = 10, start: int = 0, credentials: Optional[Dict[str, Any]] = None) -> List[Dict]:
    """
    Search for Red Hat cases and return a list of case numbers.
    
    Args:
        query: Search query string
        rows: Number of results to return (default: 10)
        start: Starting index for pagination (default: 0)
        credentials: Authentication credentials containing offline_token
        
    Returns:
        List of cases with their numbers and metadata
    """
    try:
        print(f"DEBUG: search_cases called with query: {query}")
        rh_creds = _get_rh_creds(credentials)
        path = "/hydra/rest/search/v2/cases"
        
        data = {
            "q": query,
            "start": start,
            "rows": rows,
            "partnerSearch": False,
            "expression": "sort=case_lastModifiedDate%20desc&fl=case_createdByName%2Ccase_createdDate%2Ccase_lastModifiedDate%2Ccase_lastModifiedByName%2Cid%2Curi%2Ccase_summary%2Ccase_status%2Ccase_product%2Ccase_version%2Ccase_accountNumber%2Ccase_number%2Ccase_contactName%2Ccase_owner%2Ccase_severity"
        }
        
        result = await rhapi.make_request("post", path, data, credentials=rh_creds)
        
        # Format the response to include only relevant information
        cases = []
        if "response" in result and "docs" in result["response"]:
            for doc in result["response"]["docs"]:
                case = {
                    "case_number": doc.get("case_number"),
                    "summary": doc.get("case_summary"),
                    "status": doc.get("case_status"),
                    "product": doc.get("case_product"),
                    "version": doc.get("case_version"),
                    "severity": doc.get("case_severity"),
                    "owner": doc.get("case_owner"),
                    "created_date": doc.get("case_createdDate"),
                    "created_by": doc.get("case_createdByName"),
                    "last_modified_date": doc.get("case_lastModifiedDate"),
                    "uri": doc.get("uri")
                }
                cases.append(case)
        
        print(f"DEBUG: Returning {len(cases)} cases")
        return cases
    
    except Exception as e:
        print(f"ERROR in search_cases: {str(e)}")
        print(f"ERROR type: {type(e)}")
        import traceback
        print(f"ERROR traceback: {traceback.format_exc()}")
        raise e

@mcp.tool()
async def get_case(case_number: str, credentials: Optional[Dict[str, Any]] = None) -> Dict:
    """
    Get case details by case number.
    
    Args:
        case_number: The case number (e.g., "04145487")
        credentials: Authentication credentials containing offline_token
        
    Returns:
        Formatted case data with description, severity, issue, case number, and comments
    """
    try:
        print(f"DEBUG: get_case called with case_number: {case_number}")
        rh_creds = _get_rh_creds(credentials)
        path = f"/hydra/rest/v1/cases/{case_number}"
        data = await rhapi.make_request("get", path, credentials=rh_creds)
        
        # Extract comments from the main response
        comments = data.get("comments", [])
        
        # Format the response according to the specified schema
        formatted_result = {
            "case_number": case_number,
            "summary": data.get("summary", data.get("title", "")),
            "description": data.get("description"),
            "severity": data.get("severity"),
            "comments": [
                {
                    "createdDate": comment.get("createdDate"),
                    "createdBy": comment.get("createdBy"),
                    "commentBody": comment.get("commentBody", comment.get("text", ""))
                }
                for comment in reversed(comments)
            ]
        }
        
        # Add any additional useful fields from the original response
        if "status" in data:
            formatted_result["status"] = data.get("status")
        if "product" in data:
            formatted_result["product"] = data.get("product") 
        if "version" in data:
            formatted_result["version"] = data.get("version")
        if "ownerId" in data:
            formatted_result["ownerId"] = data.get("ownerId")
        if "createdDate" in data:
            formatted_result["createdDate"] = data.get("createdDate")
        if "openshiftClusterID" in data:
            formatted_result["openshiftClusterID"] = data.get("openshiftClusterID")
        if "openshiftClusterVersion" in data:
            formatted_result["openshiftClusterVersion"] = data.get("openshiftClusterVersion")
        
        # Add external trackers if present
        if "externalTrackers" in data and isinstance(data["externalTrackers"], list):
            formatted_result["external_trackers"] = [
                {
                    "resourceKey": tracker.get("resourceKey"),
                    "resourceURL": tracker.get("resourceURL"),
                    "status": tracker.get("status"),
                    "system": tracker.get("system"),
                    "title": tracker.get("title"),
                }
                for tracker in data["externalTrackers"]
                if any(tracker.get(k) for k in ("resourceKey", "resourceURL", "status", "system", "title"))
            ]
        
        # Add case resource links if present
        if "caseResourceLinks" in data and isinstance(data["caseResourceLinks"], list):
            formatted_result["case_resource_links"] = [
                {
                    "resourceType": link.get("resourceType"),
                    "resourceViewURI": link.get("resourceViewURI"),
                    "solutionTitle": link.get("solutionTitle"),
                }
                for link in data["caseResourceLinks"]
                if any(link.get(k) for k in ("resourceType", "resourceViewURI", "solutionTitle"))
            ]
        
        print(f"DEBUG: Returning formatted case data for case {case_number}")
        return formatted_result
    
    except Exception as e:
        print(f"ERROR in get_case: {str(e)}")
        print(f"ERROR type: {type(e)}")
        import traceback
        print(f"ERROR traceback: {traceback.format_exc()}")
        raise e

@mcp.prompt(name="summarize_case_prompt", description="Summarize a Red Hat support case in C.A.S.E. markdown format.")
async def summarize_case_prompt(case_number: str) -> str:
    """
    Given a Red Hat support case number, instruct the LLM to fetch the case data and summarize it using the C.A.S.E. markdown template.
    """
    prompt = f'''
You are a Red Hat support expert. Given the following Red Hat support case number, first fetch the full case data using the appropriate tool or API, then analyze and summarize it using this markdown template into an artifact. 
Do not use bold, italics, or any markdown except for headings and bullet points. 
Be concise, actionable, and ensure all sections are filled if possible.

Case Number: {case_number}

## C.A.S.E. Update - [case number] - [title]

- Current Status:
  - [List the current issue(s) and status in bullet points]

- Actions:
  - [Summarize actions taken, outcomes, and any key commands or links in bullet points]

- Severity:
  - [Describe the business impact]

- Expectations:
  - [Outline next steps and expected timing in bullet points]

### ENVIRONMENT:
- [List relevant environmental factors: product, version, clusterID/ResourceID, and related links]

### NOTES:
- [Add any additional insights or actionable suggestions]

Ensure the summary is comprehensive yet concise, providing a clear overview and actionable next steps.
'''
    return prompt.strip()

@mcp.prompt(name="resolve_case_prompt", description="Red Hat Case Resolver Agent: investigation and solution workflow for a support case.")
async def resolve_case_prompt(case_number: str) -> str:
    """
    Given a Red Hat support case number, instruct the LLM to follow the Red Hat Case Resolver Bot workflow and output a markdown document with the required sections and rules.
    """
    prompt = f'''
## Investigation Workflow Round
    1. **Fetch the case**  
        • Get the Redhat with case number   
        • Summary and understand the current issue(s) and status

    2. **Keyword generation**
        • Build a rich keyword list (components, CVEs, error phrases, paraphrases).  
        • Produce at least three query variants.

    3. **Iterative search rounds** (cap=3). In **each** round:

    a. **Search**  
        • Search Red Hat KCS  
        • Search Jira ticket  
        • Search Red Hat cases for similar historical RedHat cases     
        • Search Internet

    b. **Retrieve & Read**  
        • KCS Solution and Articles
        • Jira ticket details, links, and comments 
        • Case history and resolution
        • Fetch any new hyperlinks inside those bodies.

    c. **Link Expansion**  
        • For every new URL try to fetch content  
        • Skip URLs already reviewed.
        
    

    d. **Reflect**  
        • Summarize what new evidence you gained.  
        • **Confidence:** *0 - 1*
        • Decide what is still missing and whether to start another round
        • Max three search rounds until confidence score >= 0.95.


## 2. Output Requirements
Produce **one markdown document** with these exact headings:

### Case Summary  
Concise restatement of the customer's problem.

### Analysis & Findings  
Bullet evidence from reviewed KCS, Jira, previous cases, and public sources.  
Cite inline: *(KCS 12345)* / *(JIRA ABC-42)* / *(CASE 987654)*.

### Proposed Solution  
Step by step fix or next action plan.  

### Sources  
Unordered list of **unique** URLs consulted—KCS first, then Jira, then previous cases (if publicly addressable), then public links. No duplicates.

## 3. Style Guide
* Be concise and factual; minimal fluff.  
* Quote exact error messages when they drive a search.  
* Prefer bullets; avoid unnecessary tables.

## 4. Hard Rules
* No JSON output—markdown only.  
* Never list the same link twice.  
* If still unsatisfied, recommend escalation.

# ================================================================
#                       ⬇️  START  ⬇️
# ================================================================

Case Number: {case_number}
'''
    return prompt.strip()

@mcp.prompt(name="resolve_case_prompt_v2", description="Red Hat Case Resolver Agent: investigation and solution workflow for a support case.")
async def resolve_case_prompt_v2(case_number: str) -> str:
    """
    Given a Red Hat support case number, instruct the LLM to fetch the case data and summarize it using the C.A.S.E. markdown template.
    """
    prompt = f'''

Case Number: {case_number}

# Agent Role and Goal

You are an AI assistant specialized in Red Hat support case resolution. Your primary goal is to comprehensively investigate a given Red Hat support case, gather all relevant information from internal Jira, Red Hat's Knowledge Centered Service (KCS), historical Red Hat cases, and the broader internet, and then synthesize this information into a clear, actionable summary and proposed solution. You must operate methodically through defined phases of fetching case details, iterative investigation, and reflective analysis, culminating in a markdown artifact that includes all relevant source links.

# Workflow and Instructions

Follow these steps precisely:

**Phase 1: Fetch and Understand Case**

1.  **Receive Case Number:** You will be given a Red Hat case number.
2.  **Get Case Details:** Use the `get_case` tool from the Red Hat API MCP server to retrieve the full details of the provided case number. Note any direct resource links provided in the case data.
3.  **Initial Summary & Understanding:**
    * Thoroughly analyze the retrieved case details.
    * Summarize the core problem(s), the current status of the case, the product(s) and version(s) involved, the customer's environment (if described), and any troubleshooting steps already taken or documented in the case.
    * Identify key entities, error messages, and technical terms.

**Phase 2: Iterative Investigation (Maximum 3 Rounds)**

This phase is iterative. You will conduct up to 3 rounds of investigation. A round may be cut short if the confidence threshold is met.

1.  **Keyword and Query Generation:**
    * Based on your initial understanding and the details from `get_case`, generate a rich and diverse list of keyword combinations and specific search queries.
    * Consider symptoms, error messages, product names, versions, components, technologies involved, and potential problem categories.
    * For Jira searches, formulate relevant JQL queries.

2.  **Iterative Search Round (Perform these actions in each round):**
    * **Search Red Hat KCS:** Use `search_kcs` with your generated keywords. Capture the KCS ID and `view_uri` for relevant results.
    * **Search Jira Issues:** Use `jira_search_issues` with appropriate JQL queries. Capture the Jira issue key for relevant results (this key implies the link).
    * **Search Historical Red Hat Cases:** Use `search_cases` with your keywords. Capture the case number for relevant results (this implies the link).
    * **Search Internet:** Perform targeted internet searches using your keywords. Capture the full URL for relevant public web pages.

3.  **Retrieve & Read Detailed Content:**
    * For the most promising results identified in the search phase:
        * **KCS:** Use `get_kcs` to retrieve the full content of relevant KCS solutions/articles using their IDs.
        * **Jira:** Use `jira_get_issue_details`, `jira_get_issue_comments`, and `jira_get_issue_links` to get comprehensive information about relevant Jira tickets using their keys. Note any further links found within these details.
        * **Red Hat Cases:** If highly relevant historical cases are found via `search_cases`, consider if using `get_case` on a very small number (1-2) of the *most* pertinent historical cases is warranted to understand their detailed resolution path. Note any resource links found.
        * **Internet Content:** Analyze the content from promising web links (URLs captured previously).
    * **Deep Dive & Link Traversal:**
        * Carefully examine all retrieved content.
        * Identify any **new** relevant URLs, KCS article IDs (and their `view_uri`s), Jira issue keys, or case numbers mentioned within the bodies of these documents.
        * **Maintain a list of already reviewed URLs/resources/issue keys/IDs** to avoid redundant fetching and processing in subsequent steps or rounds. Store the direct link/URI for each.
        * For newly discovered, unreviewed, and relevant links/IDs, fetch their content using the appropriate tools, ensuring you store their source link/URI.

**Phase 3: Reflect, Evaluate, and Decide**

1.  **Synthesize Information:** After each round of "Retrieve & Read," consolidate all new information gathered in that round with previously acquired knowledge. Ensure all source identifiers (IDs, Keys, URLs) are tracked.
2.  **Evaluate Sufficiency:** Critically assess whether the information you have gathered is sufficient to formulate a comprehensive and reliable resolution or a set of next steps for the original Red Hat case.
3.  **Confidence Score:**
    * Assign a **confidence score between 0.0 and 1.0** representing your certainty that you have enough information to resolve the case or provide definitive next steps.
    * Briefly justify this score based on the quality, relevance, and completeness of the information found and the supporting sources.
4.  **Decision for Next Round:**
    * **If confidence_score >= 0.95 OR you have completed 3 rounds:** Proceed to Phase 4 (Summarization).
    * **If confidence_score < 0.95 AND you have completed fewer than 3 rounds:**
        * Identify information gaps. What is still missing? What questions remain unanswered?
        * Refine your keyword strategy and search queries for the next round.
        * Initiate the next search round (Phase 2, Step 2).

**Phase 4: Summarize and Create Artifact**

Once the iterative investigation concludes:

1.  **Comprehensive Analysis:** Perform a final, holistic analysis of all information gathered throughout all rounds and its supporting sources.
2.  **Formulate Solution/Next Steps:** Based on your analysis, determine the likely root cause(s), a specific proposed solution, or logical next troubleshooting steps.
3.  **Generate Markdown Artifact:** Create a well-structured markdown document containing:
    * **Case ID:** The original Red Hat Case Number.
    * **Initial Case Summary:** Your summary from Phase 1, Step 3.
    * **Investigation Overview:** Briefly describe the search strategies employed in each round.
    * **Key Findings (each with its source identifier/link):**
        * Relevant KCS articles (ID, Title, `view_uri`, brief summary of relevance).
        * Relevant Jira issues (Key, Summary, Status, inferred Jira link, brief summary of relevance).
        * Relevant historical Red Hat cases (Case Number, Summary, inferred link, brief summary of relevance and its resolution if found).
        * Key insights from internet searches (Full URL, Page Title if available, brief summary of relevance).
    * **Correlation and Analysis:** Explain how these findings and their sources connect to the original case and to each other.
    * **Proposed Solution / Recommended Next Steps:** Clearly articulate the proposed solution or recommended steps.
    * **Confidence Score:** State your final confidence score.
    * **Remaining Open Questions / Areas for Further Manual Investigation:** If applicable.
    * **Comprehensive Source List (Key Resources Referenced):** This section must provide a complete list of all unique KCS IDs (with `view_uri`s), Jira Keys (implying direct links), Red Hat Case Numbers (implying direct links), and full URLs from internet searches that were consulted and deemed relevant during the investigation. Format clearly for easy access to the source material. Example:
        * KCS 12345: [Title of KCS] ([view_uri_link])
        * JIRA PROJECT-789: [Summary of Jira] ([link_to_jira_if_pattern_is_known_else_just_key])
        * Case 0098765: [Summary of Case] ([link_to_case_if_pattern_is_known_else_just_number])
        * Web: [Page Title] ([full_url_link])

# General Guidelines

* **Be Methodical:** Follow the workflow strictly.
* **Tool Usage Clarity:** Mentally (or if an option, explicitly state) which tool you are invoking and the key parameters.
* **Prioritization:** Prioritize information from Red Hat KCS, Red Hat Cases, and internal Jira.
* **Efficiency and Source Tracking:** Avoid redundant searches and meticulously track all source links/identifiers.
* **Focus on Resolution:** Aim to provide information that helps resolve the support case.
* **No `jira_create_issue`:** For this task, you will not use the `jira_create_issue` tool.

'''
    return prompt.strip()

# Run the server if executed directly
if __name__ == "__main__":
    mcp.run(transport="stdio")