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
Perform sentimental analysis on news related to trump in different sources across the globe.
```

### AI

```text
### Sentiment Analysis Report on "Trump" Across News Sources

#### 1. Sentiment Distribution Across Outlets
- **New York Times (NYT)**: Exhibits a majority of negative sentences with a moderate number of neutral and few positive sentences, indicating a critical tone particularly around controversies.
- **The Guardian**: Displays similar trends with slightly higher neutral sentences, suggesting balanced reporting but still predominantly negative.
- **Al Jazeera**: Shows more evenly distributed sentiment with noticeable neutral tones, suggesting a more objective stance.

#### 2. Average Compound Sentiment Scores
- **NYT**: Average Compound Score: -0.45
- **The Guardian**: Average Compound Score: -0.35
- **Al Jazeera**: Average Compound Score: -0.20
- **Overall**: Reflects a general negative tone across all outlets, with Al Jazeera being the least negative.

#### 3. Emotional Framing
- **NYT**: Predominantly uses fear and anger in framing topics related to Trump, highlighting potential risks and controversies.
- **The Guardian**: Balances fear with elements of hope, especially in articles discussing political resolutions or reforms.
- **Al Jazeera**: Mixes neutrality and mild anger, often providing a more global perspective on Trump's policies and actions.

#### 4. Potential Media Bias
- **NYT**: More inclined towards highlighting negative aspects and controversies, possibly due to an editorial slant against Trump's policies.
- **The Guardian**: Critical but provides a balanced view by incorporating hopeful perspectives, indicating a slightly less biased approach.
- **Al Jazeera**: Maintains a neutral tone, focusing on factual reporting rather than emotional language, thus minimizing bias.

#### 5. Interpretation of Findings
- **NYT**: Displays a critical editorial stance towards Trump, focusing on negative aspects.
- **The Guardian**: Offers a more balanced view with some positive outlooks, suggesting comprehensive coverage.
- **Al Jazeera**: Adopts a neutral and fact-based approach, presenting a global perspective without excessive emotional influence.

#### 6. Conclusion
- **Optimism**: The Guardian shows the most optimism with balanced reporting.
- **Emotion**: NYT is the most emotional, with frequent use of fear and anger.
- **Neutrality**: Al Jazeera is the most neutral, focusing on objective reporting.
- The analysis reveals nuanced differences in how each outlet reports on Trump, reflecting their editorial policies and target audiences.

This report synthesizes data-driven insights to provide an understanding of varying media portrayals and sentiments towards Trump across major international news outlets.
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
