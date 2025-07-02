# News-Sentiment Analysis Assistant

The **News-Sentiment Analysis Assistant** is a modular, multi-agent system that analyzes news articles from major global media outlets — *The New York Times (USA)*, 
*The Guardian (UK)*, and *Al Jazeera (Middle East)* — to reveal how topics, events, or individuals are emotionally framed across diverse geopolitical perspectives. Using keyword-driven sentiment analysis, it generates concise, data-backed insights that highlight variations in tone, polarity, and narrative emphasis.

---

## File

[news_sentimental_analysis.hocon](../../registries/news_sentimental_analysis.hocon)

---
## Prerequisites

This agent is **disabled by default**. To enable and use it:

### 1. Install Required Python Packages

Install the following dependencies:
```bash
pip install newspaper3k beautifulsoup4 nltk vaderSentiment backoff lxml
```
### 2. Get API Keys

#### New York Times (NYT)
- Get API key: [https://developer.nytimes.com/get-started](https://developer.nytimes.com/get-started)

#### The Guardian
- Get API key: [https://open-platform.theguardian.com/documentation/](https://open-platform.theguardian.com/documentation/)

#### Al Jazeera
- No API key required because data is fetched directly from the RSS feed.

### 3. Set API Keys via Environment Variables

```bash
export NYT_API_KEY=your_nyt_key
export GUARDIAN_API_KEY=your_guardian_key
```

### 4. Update the manifest.hocon file
- Set `news_sentimental_analysis = false` to `news_sentimental_analysis = true`.
  
---

## Description

The assistant is anchored by a Frontman agent that acts as the primary interface with users and manages coordination across all downstream agents and tools. 
It orchestrates the execution pipeline by sequentially invoking agents, managing dependencies, and structuring inputs and outputs at each stage.

- **Source-Specific Pipelines**  
  Dedicated agents scrape articles from each media outlet using pipelines equipped with exponential backoff strategies to ensure reliable, fault-tolerant data retrieval under rate limits or network disruptions.

- **Sentence-Level Analysis**  
  The system filters and analyzes only those sentences that contain the specified keywords, allowing for context-aware sentiment evaluation while minimizing irrelevant content.

- **VADER-Powered Scoring**  
  Keyword-matched sentences are scored using the VADER framework and aggregated to generate sentence-level, article-level and source-level sentiment summaries, providing both granular and holistic insights.

- **Natural Language Summarization**  
  Rather than exposing raw `.json` outputs, the assistant interprets quantitative sentiment data and generates user-facing natural language summaries—making insights more interpretable and actionable.

- **Modular & Extensible Architecture**  
  The system is designed for flexibility, enabling seamless integration of new sources, languages, or alternative sentiment engines without affecting core functionality.

---

## Example Conversation

### Human

```text
Perform sentimental analysis on news related to Space exploration in different sources across the globe.
```

### AI

```text
The sentiment analysis report on "Space exploration" articles from various news sources has been generated. Here is the detailed summary:

### Sentiment Distribution Across Outlets
1. **New York Times (NYT):**
   - Sentiment is predominantly positive, with frequent association of keywords like "innovation" and "discovery."
   - Average compound score: 0.65, indicating a generally positive outlook.

2. **The Guardian:**
   - Displays a balanced tone with a slightly higher count of neutral sentences. Keywords like "budget" and "policy" tend to have a neutral or slightly negative tone.
   - Average compound score: 0.35, suggesting a balanced to slightly positive sentiment.

3. **Al Jazeera:**
   - Shows a mix with a notable count of negative sentiments, especially around the political aspects of space exploration, with keywords like "conflict" and "competition."
   - Average compound score: 0.20, reflecting a more critical tone overall.

### Emotional Framing
- **NYT:** Predominantly hopeful, framing space exploration as a frontier of human achievement.
- **The Guardian:** Neutral, focusing on factual reporting, though hopeful when discussing technological advancements.
- **Al Jazeera:** Mix of fear and neutrality, with discussions around geopolitical implications.

### Potential Media Bias
- **NYT:** Highlights positive aspects, possibly reflecting a pro-science editorial slant.
- **The Guardian:** Balanced approach, slight bias towards neutral or critical reporting on financial and policy matters.
- **Al Jazeera:** Often presents space exploration in a global politics context, adding a critical or wary tone.

### Key Insights
- **Optimism:** NYT is the most optimistic, focusing on progress and discovery.
- **Neutrality:** The Guardian provides a balanced view, often relying on factual and policy-oriented discourse.
- **Emotion:** Al Jazeera's critical stance highlights geopolitical concerns, reflecting its global news focus.

This analysis provides a nuanced view of how space exploration is portrayed across different media outlets, revealing distinct editorial slants and potential biases.
```

---

## Architecture Overview

### Frontman Agent: News Query Manager

- Interfaces with users to accept keywords and source preferences.  
- Delegates scraping, filtering, and sentiment tasks to coded tools.  
- Coordinates sequential agent execution and manages data flow across the pipeline.

---

### Functional Tool

These are coded tools called by the News Query Manager:

- **News API Specialist**
  - Scraps news articles from *The New York Times*, *The Guardian*, and *Al Jazeera* based on keyword relevance.
  - Uses resilient scraping pipelines with exponential backoff and fallback parsing to ensure robust content extraction.
  - **Arguments** – `keywords` (str, required): List of keywords for filtering (e.g., `"climate, election"`), `source` (str, optional): One of `"nyt"`, `"guardian"`, `"aljazeera"`, or `"all"` (default).


- **Sentiment Analyst** - Analyzes news articles using VADER to generate keyword-based sentiment score summaries in structured JSON format.
  - Load scraped news articles and filters sentences by user-defined keywords
  - Scores sentiment using VADER (compound, positive, negaive, neutral), aggregates results and saves a structured JSON report.
  - Arguments - `keywords` (str, required): List of keywords for filtering (e.g., `"election, fraud"`) and `source` (str, optional): News sources to analyze, defaults to `"all"` (e.g., `"nyt,guardian"`). 
      
- **Data Analyst** - Generates cross-outlet sentiment comparison reports using labeled article data.
  - Compares sentiment distribution and average scores per outlet to identify tonal and emotional differences.
  - Highlights editorial bias and emotional framing (e.g., fear, hope, anger) based on keyword-matched content.
  - Arguments – Structured sentiment `.json` content containing sentence-level scores, article summaries, and aggregated metrics.

---

## Debugging Hints

Check logs for the following stages:

- **Library Dependencies**: Ensure all required libraries and NLTK resources (e.g., `punkt`) are properly installed as per prerequisites.
- **Scraping Issues**: Verify that all API keys are valid and article content is successfully extracted.
- **File Handling**: Confirm all input/output paths are correct, directories exist, and files are saved without errors.
- **Data Analysis**: Validate input JSON format and presence of key fields like sentiment scores and article metadata before analysis.
