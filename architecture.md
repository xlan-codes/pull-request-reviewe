# Architecture Overview

This project implements a complete **AI-Agentic Code Review System** combining:
- Multi-agent LLM reasoning
- RAG (Retrieval-Augmented Generation)
- Static code analysis tools
- Multi-platform PR ingestion (GitHub/GitLab/Bitbucket)
- Streamlit frontend interface

---

# Architectural Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Agent Orchestrator                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Analyzer │→ │Retriever │→ │  Critic  │→ │Synthesizer│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────┬──────────────────────┬──────────────────┬─────────┘
          │                      │                  │
┌─────────▼──────┐    ┌─────────▼────────┐  ┌─────▼─────────┐
│ Platform APIs  │    │   RAG Pipeline   │  │ Code Analysis │
│ (GH/GL/BB)     │    │ (Chroma + Embeds)│  │  Tools        │
└────────────────┘    └──────────────────┘  └───────────────┘
```

---

# Components

## 1. **Frontend**
- Built with **Streamlit**
- Provides:
  - PR URL input
  - Review modes (quick, standard, deep)
  - Review results UI
  - Metrics dashboard

---

## 2. **Agentic System (CrewAI)**

### **Analyzer Agent**
- Parses diffs  
- Detects smells, issues, complexity risks  
- Integrates static analysis tools  

### **Retriever Agent**
- Queries ChromaDB vector store  
- Retrieves:
  - Best practices  
  - Security rules  
  - Language guidelines  

### **Critic Agent (Self-Reflection)**
- Evaluates suggestions  
- Removes false positives  
- Scores severity + relevance  

### **Synthesizer Agent**
- Produces final structured review:
  - Bugs  
  - Security issues  
  - Code smells  
  - Performance risks  
  - Documentation fixes  

---

# RAG Pipeline

### Vector DB
- **ChromaDB**
- Stores:
  - Best practices  
  - Code review examples  
  - Security rules  
  - Language-specific patterns  

### Retrieval
- Hybrid:
  - Semantic embedding search  
  - Keyword matching  

---

# Tools & Integrations

### Platform Support
- GitHub REST API  
- GitLab API  
- Bitbucket API  
- Unified ingestion layer  

### Static Analysis Tools
- **Semgrep**
- **Pylint**
- **Flake8**
- **Radon** (complexity)
- **Tree-sitter** (AST parsing)

---

# Project Structure

```
pull-request-reviewer/
├── src/
│   ├── agents/
│   ├── data_preparation/
│   ├── rag/
│   ├── tools/
│   ├── reasoning/
│   ├── evaluation/
│   ├── frontend/
│   ├── config/
│   └── utils/
├── scripts/
├── tests/
└── data/
```

---

# Evaluation Framework

- Detection accuracy  
- False positive rate  
- Severity correctness  
- Actionability of suggestions  
- Token efficiency  
- LLM-as-judge scoring  

---

# Technologies Used

| Category | Technology |
|---------|------------|
| Language | Python 3.10 |
| Frontend | Streamlit |
| Agents | CrewAI |
| RAG | ChromaDB |
| LLM | OpenAI (GPT-4o / GPT-4o-mini) |
| Platforms | GitHub, GitLab, Bitbucket APIs |
| Testing | PyTest |

---

# Data Flow

1. User enters PR URL  
2. Platform adapter fetches diff  
3. Analyzer agent inspects code  
4. Retriever fetches relevant knowledge  
5. Critic verifies suggestion quality  
6. Synthesizer generates final report  
7. Streamlit UI displays results  
