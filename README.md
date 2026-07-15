# Event-Driven Multi-Agent Web Research & Summarization System

An enterprise-grade, production-ready Multi-Agent Web Research & Summarization system. This pipeline is built with **Python 3.12+**, **FastAPI**, **Redis Streams** (acting as the asynchronous message bus), and the **Groq API SDK**.

The system coordinates multiple specialized agents—a **Planner**, a **Searcher**, a **Synthesizer**, and a **Critic**—supervised by a centralized **Supervisor Agent** to perform autonomous web research, compile structured summaries, map citations, and handle critique-driven loops.

---

## System Architecture

Instead of running agent routines inside a single sequential thread, this application implements a microservices architecture. **Each agent runs in its own independent process and communicates exclusively through the Redis message bus.**

```mermaid
graph TD
    API[FastAPI Gateway] -- "1. POST /research" --> ReqStream[stream:research_requests]
    ReqStream --> Supervisor[Supervisor Agent]
    
    Supervisor -- "State Management" --> RedisDB[(Redis DB)]
    
    Supervisor -- "2. Planning Task" --> PlannerStream[stream:planner]
    PlannerStream --> Planner[Planner Worker]
    Planner -- "3. Plan Completed" --> PlannerComp[stream:planner:completed]
    PlannerComp --> Supervisor
    
    Supervisor -- "4. Search Task" --> SearcherStream[stream:searcher]
    SearcherStream --> Searcher[Searcher Worker]
    Searcher -- "5. Scraped Pages" --> SearcherComp[stream:searcher:completed]
    SearcherComp --> Supervisor
    
    Supervisor -- "6. Synthesis Task" --> SynthStream[stream:synthesizer]
    SynthStream --> Synthesizer[Synthesizer Worker]
    Synthesizer -- "7. Formatted Sections" --> SynthComp[stream:synthesizer:completed]
    SynthComp --> Supervisor
    
    Supervisor -- "8. Critique Task" --> CriticStream[stream:critic]
    CriticStream --> Critic[Critic Worker]
    Critic -- "9. Score & Gaps" --> CriticComp[stream:critic:completed]
    CriticComp --> Supervisor
    
    Critic -- "If Requires Research & Loop < 2" --> SearcherStream
    
    Supervisor -- "10. Completion Event" --> FinishedStream[stream:research:finished]
    FinishedStream --> API
    
    style RedisDB fill:#c0392b,stroke:#fff,color:#fff
    style ReqStream fill:#1abc9c,stroke:#fff,color:#fff
    style FinishedStream fill:#1abc9c,stroke:#fff,color:#fff
```

---

## Detailed Execution Lifecycle

1. **API Entrypoint**: A client submits a research topic to `/research`. The API generates a unique `report_id`, pushes the task onto `stream:research_requests`, and polls the Redis Hash key `research:state:{report_id}`.
2. **Supervisor Init**: The `Supervisor` consumes the request, initializes state metrics, and publishes to `stream:planner`.
3. **Planner Worker**: Consumes the topic, splits it into 3-8 queries, decides on a search strategy, and publishes back to `stream:planner:completed`.
4. **Searcher Worker**: Consumes the sub-queries, executes BM25 searching against a 10,000 document local index, scrapes/normalizes the pages, and publishes to `stream:searcher:completed`.
5. **Synthesizer Worker**: Receives all scraped pages and original plans, resolves conflicts, drafts sections with citation mappings, and publishes to `stream:synthesizer:completed`.
6. **Critic Worker**: Scores confidence, raises bias flags, and flags information gaps. Returns execution back to `stream:critic:completed`.
7. **Loop Decision**: The Supervisor reviews the Critique. If omissions exist and we have run fewer than 2 loops, it publishes new gap queries back to `stream:searcher`. Otherwise, it aggregates total metrics and publishes to `stream:research:finished`.
8. **Fault Tolerance & Retries**: If any worker crashes, it writes to `stream:supervisor:errors`. The supervisor catches it and retries the failed stage (up to 2 attempts) before marking the request failed.
9. **Timeout Enforcer**: A background daemon inspects active request timestamps. Any request executing longer than 300 seconds (5 minutes) is terminated.

---

## Deployment & Installation

### Option A: Running with Docker (Recommended)
This leverages Docker Compose to deploy Redis and the API along with the 5 individual agent worker containers, restricting total resource utilization under 3.5 cores and 3.5GB RAM.

1. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   LOG_LEVEL=INFO
   DATA_DIR=data/
   ```

2. **Run Everything with a Single Command**:
   ```bash
   make run
   ```
   This command automatically down-scales old containers, builds the Docker image, spins up Redis, FastAPI, and the 5 worker daemons, waits for server readiness, executes a query, and verifies output formats.

3. **Check Container Logs**:
   To tail logs from all running agent worker processes:
   ```bash
   docker-compose logs -f
   ```

---

### Option B: Running Locally (Manual)
Requires Python 3.12+ and a local Redis server running on port `6379`.

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Local Redis**:
   Ensure Redis is active on port `6379`.

3. **Configure Environment Variables**:
   ```powershell
   # Windows PowerShell
   $env:USE_REDIS="true"
   $env:REDIS_HOST="localhost"
   $env:REDIS_PORT="6379"
   $env:GROQ_API_KEY="your-api-key"
   ```

4. **Launch Web Server and Worker Daemons**:
   Open separate terminals and start each service:
   - **FastAPI Backend**: `uvicorn app.main:app --port 8000 --reload`
   - **Supervisor**: `python app/worker_entrypoint.py --agent supervisor`
   - **Planner**: `python app/worker_entrypoint.py --agent planner`
   - **Searcher**: `python app/worker_entrypoint.py --agent searcher`
   - **Synthesizer**: `python app/worker_entrypoint.py --agent synthesizer`
   - **Critic**: `python app/worker_entrypoint.py --agent critic`

5. **Launch React Frontend UI**:
   Navigate to the frontend folder, install packages, and boot the Vite dev server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open **`http://localhost:5173/`** to access the research interface dashboard.

---

## Output Verification

Generated report schemas can be verified against schemas, citation links, unique report IDs, and score boundaries using:
```bash
./verify.sh
```

---

## Testing

To run the full test suite locally (including unit tests for the ranker, scraper, validation schemas, and the complete event-driven message-bus integration workflow):
```bash
PYTHONPATH=. pytest
```
All external LLM requests are mocked, allowing tests to run instantly offline.
