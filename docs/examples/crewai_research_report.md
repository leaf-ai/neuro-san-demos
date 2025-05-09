# CrewAI Research Report

The **CrewAI Research Report** is a minimal agentic system demonstrating how to connect an LLM to CrewAI using a custom-coded tool.

---

## File

[crewai_research_report.hocon](../../registries/crewai_research_report.hocon)

---

## Prerequisites

- This agent is **disabled by default**. To test it:
  ```bash
  pip install crewai
  ```

---


## Architecture Overview

### Frontman Agent: `research_supervisor`
- Serves as the entry point for user queries.
- Parses input and prepares parameters.
- Aggregates tool responses into a final output

### Tool: `research_report`
- Use DuckDuckGo search to do research.
- Write report based on the search results.
- Source: [`crewai_research_report.py`](../../coded_tools/crewai_research_report.py)

---

## Debugging Hints

Check the following during development or troubleshooting:

- Make sure crewai is installed.
- The LLM API used by CrewAI is properly configured.
- CrewAI tools can be used directly. However, LangChain tools must be subclassed from crewai.BaseTool to be compatible.

---
