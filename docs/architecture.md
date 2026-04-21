# Legal RAG System - Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Design Principles](#design-principles)
3. [Architecture Patterns](#architecture-patterns)
4. [State Machine Flow](#state-machine-flow)
5. [Agent Behaviors](#agent-behaviors)
6. [Data Contracts (Schemas)](#data-contracts-schemas)
7. [Decision Logic](#decision-logic)
8. [Error Handling](#error-handling)
9. [Failure Modes & Mitigations](#failure-modes--mitigations)
10. [Production Considerations](#production-considerations)

---

## System Overview

### Purpose
A production-ready Legal RAG (Retrieval-Augmented Generation) system that prevents hallucinations through adversarial multi-agent reasoning, verifies citations at the clause level, and provides explainable confidence scores.

### Key Capabilities
- ✅ Adversarial validation (Answer Agent vs Counter-Argument Agent)
- ✅ Citation verification (verbatim matching)
- ✅ Confidence & risk scoring (quantified uncertainty)
- ✅ Safe refusal (when confidence is low)
- ✅ Complete audit trail (every decision logged)
- ✅ Explainable AI (show all reasoning)

### Non-Goals (for MVP)
- ❌ Document ingestion pipeline (separate step)
- ❌ Frontend UI (covered in later phase)
- ❌ Multi-turn conversations (single-turn for now)
- ❌ User authentication (infrastructure concern)

---

## Design Principles

### 1. **Explicit Over Implicit**
- No magic: Every decision is traceable
- No hidden state mutations
- No silent fallbacks

**Why:** Legal systems require auditability. Implicit behavior creates liability.

### 2. **Type Safety Everywhere**
- Pydantic models for all data
- No raw dictionaries
- Structured LLM outputs

**Why:** Prevent runtime errors. LLMs return unstructured text; we enforce structure.

### 3. **Separation of Concerns**
- Agents do one thing well
- Orchestration separated from logic
- Computation separated from presentation

**Why:** Testability, maintainability, team scalability.

### 4. **Fail Closed, Not Open**
- When uncertain → refuse
- When citation fails → refuse
- When risk is high → refuse

**Why:** Legal liability > user satisfaction. Better to refuse than hallucinate.

### 5. **Radical Transparency**
- Show all reasoning to users
- Expose confidence & risk scores
- Display counter-arguments

**Why:** Legal professionals need to verify. Trust requires transparency.

---

## Architecture Patterns

### Hexagonal Architecture (Ports & Adapters)

```
┌────────────────────────────────────────────┐
│           API Layer (FastAPI)              │  ← External Interface
└────────────────────────────────────────────┘
                    │
┌────────────────────────────────────────────┐
│      LangGraph State Machine (Core)        │  ← Business Logic
│  - Orchestration                           │
│  - Agent coordination                      │
│  - Decision gates                          │
└────────────────────────────────────────────┘
                    │
┌───────────────┬───────────────┬────────────┐
│   Vector DB   │   LLM APIs    │  Storage   │  ← Infrastructure
│   (FAISS)     │   (OpenAI)    │   (S3)     │
└───────────────┴───────────────┴────────────┘
```

**Benefits:**
- Core logic independent of external dependencies
- Easy to swap FAISS → pgvector
- Easy to swap OpenAI → Anthropic
- Easy to test (mock external layers)

### Domain-Driven Design

**Domains:**
1. **Schemas**: Data contracts
2. **Agents**: Business logic (answer, counter, verify, score)
3. **Graph**: Orchestration (state machine)
4. **Retrieval**: Vector search
5. **Ingestion**: Document processing
6. **API**: External interface
7. **Utils**: Cross-cutting concerns (config, logging)

**Why DDD:**
- Clear boundaries
- Independent evolution
- Team can work in parallel

---

## State Machine Flow

### High-Level Flow

```
START
  ↓
classify_query
  ↓
retrieve_clauses
  ↓
generate_answer ──┐
  ↓               │ Adversarial
generate_counter ─┘ Validation
  ↓
verify_citations
  ↓
score_confidence
  ↓
decision_gate
  ├─→ [confidence ≥ 85] → format_answer → END
  └─→ [confidence < 60] → format_refusal → END
```

### Detailed Node Descriptions

#### 1. **classify_query**
- **Input:** Raw user query
- **Output:** Query type, jurisdiction
- **Purpose:** Route appropriately, set context
- **LLM Used:** Yes (lightweight classifier)

#### 2. **retrieve_clauses**
- **Input:** Query + jurisdiction
- **Output:** Top-k relevant clauses
- **Purpose:** Ground answer in documents
- **LLM Used:** No (vector search)

#### 3. **generate_answer**
- **Input:** Query + retrieved clauses
- **Output:** Answer with citations
- **Purpose:** Produce legally grounded answer
- **LLM Used:** Yes (main reasoning)

#### 4. **generate_counter**
- **Input:** Answer + retrieved clauses
- **Output:** Counter-arguments
- **Purpose:** Challenge answer, find exceptions
- **LLM Used:** Yes (adversarial reasoning)

#### 5. **verify_citations**
- **Input:** Answer citations + retrieved clauses
- **Output:** Verification results
- **Purpose:** Ensure citations are accurate
- **LLM Used:** No (string matching)

#### 6. **score_confidence**
- **Input:** Answer, counter-args, verification
- **Output:** Confidence & risk scores
- **Purpose:** Quantify uncertainty
- **LLM Used:** No (rule-based scoring)

#### 7. **decision_gate**
- **Input:** Confidence, risk, verification
- **Output:** should_answer (boolean)
- **Purpose:** Decide whether to answer or refuse
- **LLM Used:** No (threshold logic)

#### 8. **format_answer / format_refusal**
- **Input:** All state data
- **Output:** Final user-facing response
- **Purpose:** Format for presentation
- **LLM Used:** No (formatting only)

---

## Agent Behaviors

### Answer Agent

**Goal:** Produce the strongest legally grounded answer.

**Rules:**
1. Must cite every claim (no citation → no claim)
2. Must quote exact text (no paraphrasing)
3. Must explain reasoning (show your work)
4. Must state assumptions (what we're assuming)
5. Must note caveats (what could go wrong)

**LLM Prompt Structure:**
```
You are a legal analysis AI.
Context: {retrieved_clauses}
Query: {user_question}

Instructions:
- Answer ONLY what's supported by the context
- Cite clause_id for EVERY claim
- Quote exact text (no paraphrasing)
- If uncertain, say so
- Never hallucinate citations

Output: {Answer schema}
```

**Common Failure Modes:**
- ❌ Hallucinated citations → Caught by verifier
- ❌ Paraphrasing errors → Caught by verifier
- ❌ Overconfident claims → Caught by counter-agent
- ❌ Missing caveats → Caught by risk scorer

### Counter-Argument Agent

**Goal:** Actively attempt to invalidate the answer.

**Rules:**
1. Seek contradictions in retrieved clauses
2. Identify exceptions and carve-outs
3. Flag jurisdictional issues
4. Highlight ambiguous language
5. Note missing context

**Why Adversarial:**
- LLMs are overconfident by default
- Legal reasoning has exceptions
- Single-agent systems miss edge cases
- Adversarial = Red Team testing

**LLM Prompt Structure:**
```
You are a legal counter-argument AI.
Your job: CHALLENGE the answer below.

Original Answer: {answer}
Context: {retrieved_clauses}

Find:
- Contradictions
- Exceptions
- Jurisdictional conflicts
- Ambiguities
- Missing information

Output: {CounterArgument schema}
```

**Severity Levels:**
- **Minor:** Unlikely to affect outcome
- **Moderate:** Could affect interpretation
- **Severe:** Likely invalidates answer

### Citation Verifier

**Goal:** Validate that citations are grounded.

**Rules:**
1. Clause ID must exist in retrieved context
2. Quoted text must match verbatim
3. Reasoning must be faithful to text

**Implementation:**
```python
def verify_citation(citation, retrieved_clauses):
    # 1. Find clause
    clause = find_clause_by_id(citation.clause_id, retrieved_clauses)
    if not clause:
        return False, "Clause not found"
    
    # 2. Verify verbatim match
    if citation.quoted_text not in clause.text:
        return False, "Quoted text not found"
    
    # 3. Check reasoning (heuristic)
    if is_reasoning_faithful(citation.reasoning, clause.text):
        return True, ""
    else:
        return False, "Reasoning not faithful"
```

**Why Verbatim Matching:**
- LLMs paraphrase incorrectly
- Legal language is precise
- One word changes meaning

### Confidence & Risk Scorer

**Goal:** Quantify uncertainty and legal risk.

**Confidence Factors:**
1. Citation validity (0-100): Are all citations verified?
2. Counter-argument strength (0-100): How strong are objections?
3. Jurisdiction match (0-100): Does jurisdiction align?
4. Context completeness (0-100): Is context sufficient?
5. Query complexity (0-100): How complex is the query?

**Composite Score:**
```python
confidence = (
    citation_validity * 0.35 +
    (100 - counter_strength) * 0.25 +
    jurisdiction_match * 0.20 +
    context_completeness * 0.15 +
    (100 - query_complexity) * 0.05
)
```

**Risk Factors:**
- Liability risk: Could this advice cause harm?
- Compliance risk: Does this touch regulated areas?
- Ambiguity risk: Is language open to interpretation?

**Risk Levels:**
- **Low:** Factual, well-supported
- **Medium:** Some ambiguity
- **High:** Significant uncertainty
- **Critical:** Dangerous to answer

---

## Data Contracts (Schemas)

### Why Pydantic

**Benefits:**
1. **Type Safety:** Catch errors at definition time
2. **Validation:** Automatic input validation
3. **Documentation:** Schema = contract
4. **LLM Outputs:** Structured outputs prevent hallucinated formats
5. **API:** FastAPI uses Pydantic natively

**Example:**
```python
class Citation(BaseModel):
    clause_id: str
    quoted_text: str
    reasoning: str

# LLM must output this structure
# If it doesn't → validation error (caught early)
```

### Schema Hierarchy

```
GraphState (top-level)
  ├─ Query
  │   └─ QueryType (enum)
  ├─ RetrievalResult
  │   └─ RetrievedClause (list)
  ├─ Answer
  │   └─ Citation (list)
  ├─ CounterArgument
  ├─ VerificationResult
  │   └─ CitationValidation (list)
  ├─ ConfidenceScore
  ├─ RiskAssessment
  └─ FinalResponse
      └─ RefusalReason (enum)
```

---

## Decision Logic

### Decision Gate Rules

```python
if not all_citations_valid:
    return REFUSE  # Hard blocker

if risk == "critical":
    return REFUSE  # Hard blocker

if confidence < 60:
    return REFUSE  # Below threshold

if confidence >= 85 and risk != "critical":
    return ANSWER  # High confidence path

if 60 <= confidence < 85:
    return ANSWER_WITH_WARNINGS  # Medium confidence path
```

### Threshold Tuning

**Production Strategy:**
1. Start conservative (high thresholds)
2. Monitor refusal rate
3. Monitor error rate (hallucinations)
4. Adjust thresholds to balance coverage vs accuracy

**Metrics to Track:**
- Refusal rate by category
- User satisfaction (when we answer)
- Error rate (when we hallucinate)
- Coverage (what % of queries we answer)

---

## Error Handling

### Failure Recovery

**Philosophy:** Graceful degradation.

**Levels:**
1. **Node Failure:** Try to continue pipeline, mark error in state
2. **LLM Timeout:** Retry with exponential backoff
3. **Validation Error:** Log error, return refusal
4. **System Error:** Return safe refusal with error message

**Example:**
```python
try:
    answer = await generate_answer_node(state)
except LLMTimeoutError:
    # Retry
    answer = await retry_with_backoff(generate_answer_node, state)
except Exception as e:
    # Safe failure
    logger.error(f"Answer generation failed: {e}")
    return format_safe_refusal(state, error=str(e))
```

---

## Failure Modes & Mitigations

### Common RAG Failure Modes

| Failure Mode | Impact | Mitigation |
|--------------|--------|------------|
| **Hallucinated citations** | High (false grounding) | Citation verifier |
| **Overconfident answers** | High (misleading) | Counter-agent + confidence scoring |
| **Context window truncation** | Medium (missing info) | Clause-aware chunking |
| **Retrieval failure** | Medium (wrong context) | Metadata filtering + reranking |
| **Jurisdictional mismatch** | High (wrong law) | Jurisdiction detection + filtering |
| **Paraphrasing errors** | Medium (incorrect meaning) | Verbatim matching |
| **Ambiguity ignoring** | Medium (overconfident) | Counter-agent highlights ambiguity |

### LangGraph-Specific Considerations

**State Mutations:**
- ❌ Don't mutate nested objects in-place
- ✅ Create new objects, return updated state

**Error Propagation:**
- ❌ Don't silently swallow errors
- ✅ Add error field to state, handle in formatter

**Conditional Routing:**
- ❌ Don't use complex logic in routing functions
- ✅ Set flags in nodes, simple logic in router

---

## Production Considerations

### Scalability

**Bottlenecks:**
1. LLM API calls (slowest)
2. Vector search (fast with FAISS, slower with pgvector)
3. Citation verification (CPU-bound)

**Solutions:**
- Async/await throughout
- Connection pooling for LLM APIs
- Caching for repeated queries
- Batch processing for multiple queries

### Monitoring

**Key Metrics:**
1. **Latency:** P50, P95, P99 response times
2. **Error Rate:** % of system errors
3. **Refusal Rate:** % of refused queries (by category)
4. **Confidence Distribution:** Histogram of confidence scores
5. **LLM Costs:** $ per query

**Logging:**
- Every agent execution
- Every refusal (with reason)
- Every low-confidence answer
- Never log PII

### Security

**Threats:**
1. **Prompt Injection:** User tries to manipulate LLM
2. **Data Leakage:** User extracts training data
3. **API Abuse:** User spams expensive queries

**Mitigations:**
- Input sanitization
- Rate limiting
- Output filtering
- Audit logs

### Cost Optimization

**LLM Costs:**
- Use cheaper models for classification
- Use expensive models for reasoning
- Cache repeated queries
- Use streaming for long answers

**Example Cost:**
- Classification: GPT-3.5-turbo (~$0.001/query)
- Answer + Counter: GPT-4 (~$0.05/query)
- Total: ~$0.05/query (acceptable for legal use case)

---

## Next Steps

### Phase 2: Agent Implementation
- Implement Answer Agent with LLM
- Implement Counter-Argument Agent
- Implement full citation verification
- Implement confidence scoring algorithm

### Phase 3: Retrieval & Ingestion
- Build document ingestion pipeline
- Implement clause-aware chunking
- Set up FAISS vector store
- Add metadata filtering

### Phase 4: API & Frontend
- FastAPI endpoints
- Authentication & authorization
- Next.js UI with citation display
- Confidence & risk visualization

### Phase 5: Production Hardening
- Monitoring & alerting
- Load testing
- Security audit
- Cost optimization

---

## Interview Talking Points

### System Design
"I built a Legal RAG system using LangGraph to orchestrate multi-agent workflows. The key innovation is adversarial validation: one agent generates answers, another tries to break them. This prevents overconfident hallucinations."

### LangGraph vs LangChain
"LangGraph gives explicit state management and conditional routing, which is critical for complex workflows. I needed decision gates (if confidence < 60, refuse) and loops for refinement. Pure LangChain chains don't support this well."

### RAG Failure Modes
"The biggest failure mode in RAG is hallucinated citations. LLMs will confidently cite 'Section 12.3' that doesn't exist. My solution: strict citation verification with verbatim text matching. If any citation fails, we refuse to answer."

### Production Readiness
"I designed for observability from day one: structured logging, confidence scoring, refusal tracking. In production, you need to monitor not just errors but also 'silent failures' like low-confidence answers that shouldn't have been returned."

### Trade-offs
"I optimized for accuracy over coverage. High refusal thresholds mean we answer fewer queries, but with much higher reliability. For legal tech, this is the right trade-off. In other domains (e.g., customer service), you might optimize differently."

