# Veritas AI - Production Architecture

## 🎯 System Overview
A production-ready, self-auditing legal research system using adversarial multi-agent reasoning to prevent hallucinations and ensure explainability.

**Product Name:** Veritas AI (Latin for "truth")  
**Tagline:** Legal research, verified & challenged.

## 🏗️ Architecture Philosophy

### Core Principles
1. **Domain-Driven Design**: Organized by business capability
2. **Hexagonal Architecture**: Core logic isolated from external dependencies
3. **Type Safety**: Pydantic everywhere, no raw dicts
4. **Explicit over Implicit**: No magic, every decision is traceable
5. **Agent Adversarial**: Counter-agents validate main agents

### Tech Stack
- **Backend**: Python 3.11, FastAPI, LangGraph, LangChain
- **Vector Store**: FAISS (dev) → pgvector (prod)
- **LLMs**: OpenAI GPT-4 / Anthropic Claude
- **Frontend**: Next.js 14 (App Router), Tailwind
- **Infra**: AWS (S3, ECS, RDS)

## 📁 Project Structure

```
veritas-ai/
├── backend/
│   ├── src/
│   │   ├── agents/          # LangGraph agent nodes
│   │   ├── schemas/         # Pydantic models (data contracts)
│   │   ├── graph/           # LangGraph state machine
│   │   ├── retrieval/       # Vector store & retrieval logic
│   │   ├── ingestion/       # Document processing & chunking
│   │   ├── verification/    # Citation & clause verification
│   │   ├── scoring/         # Confidence & risk scoring
│   │   ├── api/             # FastAPI endpoints
│   │   └── utils/           # Logging, config, helpers
│   ├── tests/               # Unit & integration tests
│   ├── requirements.txt
│   └── config.yaml
├── frontend/
│   └── (Next.js app - later step)
├── data/
│   ├── raw/                 # Original legal documents
│   ├── processed/           # Chunked & indexed
│   └── vector_store/        # FAISS index
└── docs/
    └── architecture.md      # System design docs
```

## 🔄 Agent Flow (State Machine)

```
START
  ↓
[Query Classification] → Determine query type & complexity
  ↓
[Jurisdiction Detection] → Extract legal jurisdiction context
  ↓
[Clause Retrieval] → Retrieve relevant clauses from vector store
  ↓
[Answer Agent] → Generate legally grounded answer
  ↓
[Counter-Argument Agent] → Attempt to invalidate answer
  ↓
[Citation Verifier] → Verify all citations exist & are accurate
  ↓
[Confidence & Risk Scorer] → Compute confidence & legal risk scores
  ↓
[Decision Gate] → confidence ≥ 85? → Answer
                  60-84? → Answer + Warning
                  < 60? → Refuse
  ↓
END
```

## 🚀 Getting Started

### Quick Start

1. **Activate your virtual environment:**
   ```bash
   cd /Users/ishkumar/Desktop/Projects/LegalAI\ RAG
   source legalRAG/bin/activate
   ```
   You should see `(legalRAG)` in your prompt.

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Test the system:**
   ```bash
   python test_graph.py  # Test the state machine with stubs
   ```

5. **Next steps:** See `GETTING_STARTED.md` for detailed instructions

## 🧪 Testing Strategy
- **Unit tests**: Individual agent logic
- **Integration tests**: End-to-end graph execution
- **Adversarial tests**: Attempt to trigger hallucinations

## 📚 Learning Resources
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [RAG Best Practices](https://python.langchain.com/docs/use_cases/question_answering/)
- System design decisions documented in `/docs`

