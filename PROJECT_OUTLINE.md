# The Internet’s Mood Board
**Tagline:** *A live dashboard that captures what the world is thinking, feeling, and sharing.*

---

## 1. Overview

**Objective:**  
Create a real-time data visualization dashboard that tracks the global “mood” of the internet. The system scrapes and analyzes public data (from YouTube, Reddit, and similar platforms) to show how emotions, interests, and topics evolve across regions and categories.

**Initial Focus Categories:**  
1. **Memes** – humor, viral trends, and cultural tone.  
2. **Economics** – markets, inflation, jobs, and financial sentiment.  
3. **Politics** – elections, social movements, and geopolitical focus.  

Each category will be developed in sequence, with “Memes” serving as the baseline prototype for all scraping, analysis, and visualization layers.

---

## 2. Core Experience

**Concept:**  
A dynamic **3D globe interface** acts as the centerpiece of the dashboard. Users can spin, zoom, and click countries to explore real-time emotional and topical summaries for different regions.

**Flow:**  
1. The dashboard loads the globe and a global sentiment overlay (color-coded by mood intensity).  
2. Selecting a country brings up a **detail panel** on the left with charts, text summaries, and trending examples.  
3. Users can toggle between **Memes**, **Economics**, and **Politics** categories.  
4. Each category view provides both **regional** and **global** insights, refreshed every hour.

---

## 3. Dashboard Layout and Behavior

### A. Global View (Main Scene)
- **3D Interactive Globe** rendered with WebGL or Three.js.  
- Each country is shaded based on **dominant sentiment** (e.g., positive, neutral, negative).  
- Hover tooltips display quick summaries like:  
  *“Japan — curious, discussing AI memes (62% positive sentiment)”*  
- Clicking a country opens a left-side details panel.

### B. Left Detail Panel (Country View)
Once a country is selected:
- **Top Section:**  
  - Country name and flag.  
  - Summary of mood scores for each active category.  
  - “Last updated” timestamp.

- **Middle Section:**  
  - **Category Tabs:** Memes | Economics | Politics  
  - Each tab shows:
    - Top keywords  
    - Most representative posts or video titles  
    - Average emotion breakdown (joy, anger, confusion, etc.)  
    - Engagement metrics (volume of posts, average comment tone)

- **Bottom Section:**  
  - “Vibe summary” text generated dynamically (e.g., *“Canada’s meme culture today is dominated by gaming humor, while economic sentiment is anxious due to housing discussions.”*)

### C. Right Panel (Analytics View)
- Global category summaries:
  - **Top Trending Keywords** by category.  
  - **Emotional Composition** charts over time (line/bar graphs).  
  - **Regional Comparisons** – select two countries for side-by-side statistics.  
- Filters for time range (last hour, day, week) and sentiment intensity.

### D. Chat Interface
A natural-language query tool at the bottom of the dashboard allows users to ask:
- “What’s the global sentiment toward politics this morning?”
- “Which countries are sharing the most memes right now?”
- “How has economic sentiment in Europe changed since yesterday?”
  
The system interprets queries and retrieves relevant insights from stored data, optionally generating short summaries.

---

## 4. Data Pipeline and Architecture

| Stage | Function | Implementation |
|--------|-----------|----------------|
| **Scraping** | Collect trending data for each category (YouTube trending videos and Reddit top posts). Each entry includes title, description, comments, engagement counts, and country tag. | YouTube Data API, PRAW, or direct HTML scraping |
| **Preprocessing** | Clean text, normalize timestamps, deduplicate, and label content by category using keyword filters or classifiers. | Python (pandas, regex, spaCy) |
| **Emotion and Sentiment Analysis** | Assign emotional tone (joy, anger, surprise, sadness, fear) and sentiment score. | Hugging Face model or OpenAI text embedding + classifier |
| **Topic Clustering** | Identify and label clusters for subtopics (e.g., “housing crisis” in economics or “election results” in politics). | BERTopic / UMAP + HDBSCAN |
| **Aggregation and Storage** | Aggregate data by region and category, store hourly updates. | Supabase / PostgreSQL with cron-based pipeline |
| **Visualization Layer** | Frontend rendering of the globe, charts, and UI. | Next.js + Three.js / Mapbox + D3.js |
| **Chat Layer** | Query handler for natural-language questions mapped to database functions. | LangChain / LlamaIndex / OpenAI function calls |

---

## 5. Category Descriptions and Metrics

### A. Memes
**Purpose:** Capture humor, trends, and cultural expression online.  
**Data Sources:** Reddit (r/memes, r/trendingsubreddits), YouTube trending humor or short-form content.  
**Metrics:**
- Average sentiment and energy level.  
- Top visual meme formats or recurring topics.  
- Regional humor differences (e.g., self-deprecating in UK vs. ironic in US).  
**Unique Insight:** Reflects short-term social energy and cultural pulse.

### B. Economics
**Purpose:** Monitor how people feel about markets, jobs, and financial conditions.  
**Data Sources:** Reddit (r/economy, r/stocks), YouTube finance channels.  
**Metrics:**
- Sentiment toward economy (optimism vs. pessimism).  
- Frequency of terms like “recession,” “inflation,” or “growth.”  
- Cross-region comparison of financial anxiety.  
**Unique Insight:** Tracks emotional undercurrents behind market sentiment.

### C. Politics
**Purpose:** Measure global tone and focus of political discourse.  
**Data Sources:** Reddit (r/worldnews, r/politics), YouTube news channels.  
**Metrics:**
- Polarization index (positive vs. negative intensity).  
- Top mentioned leaders, events, or countries.  
- Topic co-occurrence (e.g., “elections” + “AI policy”).  
**Unique Insight:** Reveals how online narratives shape political mood in real time.

---

## 6. Technical Architecture

```mermaid
flowchart TD
    A[Scraper Modules: Reddit/YouTube] --> B[Preprocessing & Cleaning]
    B --> C[Sentiment + Emotion Analysis]
    C --> D[Topic Clustering & Categorization]
    D --> E[Regional Aggregation]
    E --> F[Database: Supabase/PostgreSQL]
    F --> G[Visualization: Next.js + Three.js Globe]
    F --> H[Chat Query Engine (LLM Interface)]
    H --> F
```

---

## 7. Example Interactions

**User Action 1:**  
Click Brazil on the globe →  
Left panel shows:
- Category tabs for memes, economics, politics.  
- Memes: “joyful, trending around football humor.”  
- Economics: “neutral, discussions on rising costs.”  
- Politics: “concerned, mentions of regional corruption.”  

**User Action 2:**  
Ask in chat: “What is Europe’s mood about politics this week?” →  
System aggregates political sentiment from European countries, returning:  
*“Europe shows increasing tension around elections, with 68% negative sentiment dominated by discussions of immigration and leadership trust.”*

---

## 8. MVP Scope (Hackathon Version)

**Build Goals (48–72 hours):**
1. Implement scraping for YouTube trending and Reddit posts (single region).  
2. Perform sentiment and emotion analysis.  
3. Visualize data on interactive 3D globe.  
4. Allow users to switch between Memes, Economics, and Politics tabs.  
5. Display region detail panel with representative posts and metrics.  
6. Include a simple chat query system connected to precomputed results.

**Stretch Goals:**
- Add real-time hourly updates.  
- Animate global sentiment over time.  
- Expand sources and refine classifiers per category.

---

## 9. Future Extensions

- Integrate Twitter/X and Google Trends for more signals.  
- Predict mood trajectories with time-series models.  
- Correlate emotion shifts with global events.  
- Enable “Mood Alerts” or “Category Reports” via email or RSS.  
- Add audio narration or visual “mood shifts” on the globe to enhance engagement.
