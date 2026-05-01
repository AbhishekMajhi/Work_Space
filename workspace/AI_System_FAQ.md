# TartanHQ AI Platform — Technical FAQ

> Covers the Policy QA & HR Assistant, Multi-Tenant AI Platform, Underwriting Decision Engine, and CAM Generation System.

---

## Table of Contents

1. [LLM & RAG Architecture](#1-llm--rag-architecture)
2. [Agent Systems & Reasoning](#2-agent-systems--reasoning)
3. [System Design & Optimization](#3-system-design--optimization)
4. [Voice AI & Real-time Systems](#4-voice-ai--real-time-systems)
5. [Security, Access Control & Multi-Tenancy](#5-security-access-control--multi-tenancy)
6. [CAM Generation & Document Intelligence](#6-cam-generation--document-intelligence)
7. [Observability, Debugging & Testing](#7-observability-debugging--testing)

---

## 1. LLM & RAG Architecture

### 1.1 What does a multi-tenant RAG architecture look like at TartanHQ, and how is namespace isolation handled within vector databases to ensure strict data separation across clients?

**Architecture overview**

The platform serves 4+ enterprise clients from a single codebase. Isolation is enforced at every layer of the stack so that one tenant's documents, prompts, and retrieval state can never bleed into another's.

**Vector database isolation (Pinecone)**

Each client maps to its own Pinecone *namespace*, derived directly from the `org_id`. Every upsert and every query carries this namespace:

```python
# Indexing
self.index.upsert(vectors=batch, namespace=self.org_id)

# Querying
results = self.index.query(
    vector=dense_query,
    sparse_vector=sparse_query,
    top_k=top_k,
    include_metadata=True,
    namespace=self.org_id          # ← hard tenant boundary
)
```

Because Pinecone namespaces are fully isolated at the index level, there is zero possibility of cross-tenant result leakage regardless of query similarity.

**BM25 / sparse vector isolation (MongoDB)**

BM25 vocabulary and IDF statistics are stored in a MongoDB `sparse_vector_store` collection, keyed by `org_id`. Document tokens and corpus statistics are never shared across tenants:

```python
collection.find_one({"type": "bm25_stats", "org_id": org_id})
collection.find_one({"type": "bm25_doc_tokens", "org_id": org_id, "doc_id": doc_id})
```

**Prompt isolation (MongoDB + Redis)**

Prompts are stored in a `prompts_v2` collection with an `org_id` field. Retrieval always scopes to the requesting tenant, with an automatic fallback to a `DEFAULT_ORG_ID` if no tenant-specific override exists:

```python
cache_key = f"prompt:{org_id}:{prompt_name}"   # Redis key is tenant-scoped
query = {"org_id": org_id, "prompt_name": prompt_name}
```

**Request-scoped config isolation**

A Python `ContextVar` (`client_config_var`) holds the active client configuration for the lifetime of a single request. This ensures that concurrent requests from different tenants — handled by the same FastAPI worker — never share configuration state:

```python
client_config_var: ContextVar["Client_Config"] = ContextVar("client_config")
cfg = client_config_var.get()   # always returns the config for the *current* request
```

**Dynamic configuration layer (MongoDB)**

Per-client customisation (model selection, API keys, feature flags, cost/performance tradeoffs) is stored in a MongoDB `config` collection and loaded at request time. This allows runtime changes to a tenant's behaviour without any code deployment.

---

### 1.2 How does a hybrid retrieval and reranking pipeline operate, and what models or techniques are used to improve relevance after initial retrieval?

**Stage 1 — Query rewriting**

Before retrieval, the original user query is expanded into multiple alternative phrasings using a small, fast LLM (`QUERY_REWRITER_LLM_ID`). This hedges against vocabulary mismatch between the query and indexed documents:

```python
def rewrite_query(query, llm):
    prompt = query_rewriting_prompt.format(query=query)
    rewrites = safe_llm_call(prompt, llm)
    return [query] + rewrites   # original + N rewrites
```

**Stage 2 — Hybrid retrieval (dense + sparse)**

For each query variant, two retrieval signals are computed in parallel and sent together to Pinecone's native hybrid query API:

| Signal | Model / Technique | Role |
|--------|-------------------|------|
| Dense | AWS Bedrock Titan Embeddings | Semantic / conceptual similarity |
| Sparse | BM25Encoder (pinecone-text) | Exact keyword / term frequency |

```python
dense_query  = self.embedding_model.embed_query(query)
sparse_query = bm25.encode_queries([query])[0]

results = self.index.query(
    vector=dense_query,
    sparse_vector=sparse_query,
    top_k=top_k,
    include_metadata=True,
    namespace=self.org_id
)
```

If BM25 produces an empty sparse vector (e.g., single-word queries) the pipeline falls back gracefully to dense-only retrieval with a warning log.

**Stage 3 — Deduplication and fusion**

Results across all query variants are merged. Duplicates are resolved by keeping the highest-scoring occurrence, then the list is sorted by score descending:

```python
seen = {}
for r in all_results:
    if r["id"] not in seen or r["score"] > seen[r["id"]]["score"]:
        seen[r["id"]] = r
final_docs = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
```

**Stage 4 — Reranking (AWS Titan Rerank)**

The top candidates (up to 80) are passed to AWS Titan Rerank, a cross-encoder model that scores each document against the original query. This replaces the previous LLM-as-ranker approach, reducing latency and cost significantly:

```python
self.reranker.top_n = min(len(retrieved_chunks), 80)
reranked_docs = self.reranker.compress_documents(query=query, documents=formatted_docs)
final_docs = final_docs[:FINAL_TOP_K]   # FINAL_TOP_K = 12
```

The final 12 passages are passed to the generation LLM. This two-stage funnel (retrieve many, rerank to few) keeps generation context compact and relevant.

---

### 1.3 What strategies are used to manage context window limitations when processing long financial documents for CAM generation?

Long financial documents (bank statements, PDFs with hundreds of pages) cannot be passed verbatim to an LLM — they would overflow the context window and introduce hallucination risk from raw numerical noise. Three complementary strategies are used:

**1. Deterministic rule engine for financial computations**

All numerical computations (monthly inflow/outflow, average balance, transaction summaries, ratio calculations) are performed by a rule-based engine (`bre_rules.py`) rather than the LLM. The LLM never sees raw transaction rows:

```
Raw bank statement → Parser → Structured JSON → Rule Engine → Computed metrics
                                                                      ↓
                                                             LLM sees: summary only
```

This eliminates the largest source of token bloat while also making computations deterministic and auditable.

**2. Structured extraction to normalized JSON**

The document intelligence pipeline converts heterogeneous inputs (Aadhaar, PAN, bank statements, scanned docs) into a normalised JSON representation before the LLM layer. The LLM receives a compact, structured payload rather than raw document text.

**3. Block-based chunking with a 4 KB limit**

When markdown text must be processed (e.g., for policy documents), it is split into blocks with a max size of 4,000 characters before LLM calls:

```python
def split_into_blocks(md_text, max_chars=4000):
    paragraphs = md_text.split("\n\n")
    current_block = ""
    for para in paragraphs:
        if len(current_block) + len(para) < max_chars:
            current_block += "\n\n" + para
        else:
            blocks.append(current_block.strip())
            current_block = para
```

**Result**: Token usage dropped from ~17K to 8–10K per query (~40–50% reduction), and the LLM is used purely as an *interpretation and summarization* layer rather than a decision engine.

---

### 1.4 How is hierarchical chunking implemented, and what factors determine optimal chunk size and overlap for accurate retrieval?

**Chunking pipeline**

Policy documents are complex and hierarchically structured (chapters > sections > clauses). A naive fixed-size chunker would split mid-clause or lose the section context. The system uses LLM-based semantic chunking instead:

```
Markdown text
    → split_into_blocks (4 KB blocks for LLM processing)
    → unified_process_sections (LLM call with unified_processing_prompt)
    → structured sections with child chunks
    → enrich each chunk with section_path, title, summary, chunk_type
```

**What the LLM returns per section**

```json
{
  "section_id": "block_2",
  "section_path": "Health Insurance > Coverage > Hospitalization",
  "chunks": [
    {
      "text": "...",
      "summary": "Covers ICU charges up to ₹10,000/day",
      "chunk_type": "policy_rule"
    }
  ]
}
```

**What gets indexed (embedding text)**

The embedding text for each chunk is a concatenation of its hierarchical path, LLM-generated summary, and raw text:

```python
enriched_chunk["embedding_text"] = " ".join(filter(None, [
    enriched_chunk.get("title"),      # "Hospitalization"
    enriched_chunk.get("summary"),    # short LLM summary
    enriched_chunk.get("text")        # actual chunk text
]))
```

This means the embedding captures *context* (where in the document this lives) as well as *content* (what it says), substantially improving retrieval precision.

**Key design choices**

| Factor | Decision | Rationale |
|--------|----------|-----------|
| Block size before LLM | 4,000 chars | Fits within LLM context, preserves paragraph boundaries |
| Chunking strategy | LLM-semantic, not fixed-size | Policy clauses have variable length; fixed-size cuts mid-clause |
| Metadata stored | section_path, summary, chunk_type | Enables hierarchical-aware retrieval and filtering |
| Embedding text | title + summary + text | Context-enriched embedding improves semantic matching |
| Overlap | None (section-boundary aligned) | LLM respects logical boundaries, eliminating need for overlap |

---

### 1.5 What mechanisms are used to minimize hallucinations in a Policy QA system, and how are LLM-generated responses validated for correctness and reliability?

Hallucination risk is addressed at every stage of the pipeline, not just at generation time:

**Retrieval layer**
- Hybrid search (dense + BM25) ensures the retrieval recall is high, so the LLM always has the relevant context rather than trying to fill gaps from parametric knowledge.
- Deduplication removes redundant context that previously caused the model to synthesise contradictory answers from overlapping passages.
- Chat-history-aware query reformulation prevents the model from answering a follow-up question with stale context from a prior turn.

**Reranking layer**
- AWS Titan Rerank replaces the earlier LLM-as-ranker approach. A cross-encoder reranker is more precise at surface-level relevance, reducing the chance that off-topic passages reach the generation prompt.

**Generation layer**
- Generation prompt instructs the model to answer strictly from the retrieved context and signal uncertainty when the context is insufficient, rather than extrapolating.
- Responses are scoped to a FINAL_TOP_K of 12 highly relevant chunks, keeping the context window focused.

**Validation layer (underwriting)**
- A dedicated `validate_decision` node checks that each decision component is grounded in a retrieved source (`source_documents` in AgentState).
- Unsupported or inconsistent claims trigger automatic re-retrieval with a reformulated query via the replan loop.
- `replan_attempts` is tracked in state; `force_finalize` is set after a maximum retry budget to prevent infinite loops.

**Operational hygiene**
- Eliminating duplicate context intersections in the knowledge base (deduplication at indexing time) removed a major class of contradictory-answer hallucinations.
- LLM-generated summaries are stored alongside each chunk and used as part of the embedding text, not as the final answer — the raw policy text is always the authoritative source.

---

## 2. Agent Systems & Reasoning

### 2.1 How does a multi-agent underwriting system function, particularly with respect to planner and re-planner loop architecture?

The underwriting agent uses a **planner–executor–replanner** architecture built on LangGraph. The key insight is that loan eligibility decisions are too complex for a single LLM call — they require structured decomposition, evidence gathering, and iterative refinement.

**Graph topology**

```
START
  └─→ categories
        ├─→ personal_planner → personal_breakdown → personal_task_handler
        │     → personal_keep_relevant → personal_replan ─┐
        │                                                  ├─ sufficient? → eligibility_checker → validate_decision → final_answer → END
        │                                                  └─ !sufficient → personal_breakdown (loop)
        ├─→ corporate_planner → corporate_breakdown → corporate_task_handler
        │     → corporate_keep_relevant → corporate_replan (same loop)
        └─→ final_answer (general queries)
```

**Planner node**

The planner receives the raw query and produces a high-level execution plan in JSON format. The plan specifies *what* needs to be checked (e.g., income criteria, CIBIL score, existing liabilities) without specifying *how* to retrieve the information.

**Breakdown node**

The breakdown agent decomposes the plan into concrete executable tasks, each with a description, an assigned tool (`personal_policy_tool`, `personal_pastcase_tool`, `personal_answer_tool`), and a specific query input. Tasks are skipped on replan loops if they already exist in state (avoiding redundant re-decomposition):

```python
existing_tasks = state.get("tasks", []) or []
if existing_tasks:
    return {}   # preserve existing tasks, just continue execution
```

**Task handler (parallel execution)**

The `PersonalTaskHandler` class executes all tasks concurrently using `asyncio` with a configurable `max_concurrency` (default 12). Each task independently calls the appropriate retrieval tool and accumulates results into `tool_results`.

**Keep-relevant node**

After tool execution, a filtering step removes low-signal snippets, keeping only passages that are genuinely relevant to the original query. This prevents context bloat from propagating through the replan loop.

**Replan node**

The replanner reviews the accumulated evidence (`kept_snippets`) and decides:
- If `sufficient=True` → proceed to `eligibility_checker`
- If `sufficient=False` and `replan_attempts` < max → refine tasks and loop back to breakdown
- If `force_finalize=True` (budget exhausted) → proceed regardless, with whatever evidence is available

**Eligibility checker → validate_decision**

After the replan loop exits, a two-stage synthesis happens:
1. `eligibility_checker` applies constraint-level rules to produce a structured eligibility verdict.
2. `validate_decision` verifies that each decision component has a source attribution — rejecting unsupported claims before they reach the final answer.

---

### 2.2 What is the approach to task decomposition within the system, and which prompting strategies are most effective for breaking down complex workflows?

**Separation of planning from decomposition**

Planning and decomposition are handled by separate LLM nodes with different prompts and, where needed, different model sizes. The planner operates at a strategic level (what to check), while the breakdown agent operates at a tactical level (how to retrieve it). This separation prevents the model from conflating high-level goals with low-level retrieval mechanics.

**Task schema**

Each task produced by the breakdown agent has a well-defined schema:

```json
{
  "task_id": "t1",
  "description": "Retrieve maximum loan-to-income ratio for salaried applicants",
  "tool": "personal_policy_tool",
  "input": "loan to income ratio salaried personal loan eligibility"
}
```

The `input` field is independently formulated by the LLM for each task — this is the actual query sent to the retrieval tool, and it is optimised for recall rather than conversational phrasing.

**Effective prompting strategies**

| Strategy | Why it works |
|----------|-------------|
| Structured JSON output | Enables programmatic routing; eliminates free-text parsing errors |
| Role separation (planner vs executor) | Each LLM call has a single, focused responsibility |
| Task-specific retrieval inputs | Avoids the whole conversation being used as a retrieval query |
| `tool_decision` pattern | LLM decides tool + input in a single step before execution, enabling parallelism |
| Persona per agent | Each node uses a prompt (`categories_agent`, `personal_planner_agent`, etc.) fetched from MongoDB, allowing per-client prompt tuning |

**Category routing as a first gate**

Before any planning occurs, a lightweight classification node (`node_categories`) routes the query to either the personal or corporate path (or a fast-path `final_answer` for general queries). This prevents the heavier planner from running on queries that don't require it, saving ~2–4 seconds per general query.

---

### 2.3 How are validation and correction loops designed to programmatically detect and resolve inconsistencies in generated outputs?

**Three-level correction architecture**

**Level 1 — Retrieval-level correction (replan loop)**

The `personal_replan` / `corporate_replan` node evaluates the sufficiency of accumulated evidence. If the retrieval results don't adequately cover the query's information needs, it generates a *new set of tasks* with reformulated queries and loops back to the breakdown step. State tracks `replan_attempts` to cap the budget:

```python
def after_personal_replan(state: AgentState) -> str:
    if state.get("sufficient", False) or state.get("force_finalize", False):
        return "eligibility_checker"
    return "personal_breakdown"   # loop
```

**Level 2 — Claim-level validation (validate_decision)**

The `validate_decision` node operates after the eligibility check. It inspects each claim in the eligibility verdict against `source_documents` in state. Claims without a traceable source are flagged. For flagged claims, the node triggers query reformulation and re-retrieval automatically, replacing the unsupported claim with a grounded one.

**Level 3 — Output schema enforcement**

All LLM outputs are parsed through a robust `LLMInvoker.invoke_json()` method that tries multiple parsing strategies (strict JSON, literal eval, fence extraction, largest-JSON-block extraction) before falling back to a structured error. This prevents malformed LLM output from propagating as a silent failure.

**Guard rails in state**

| State field | Purpose |
|-------------|---------|
| `replan_attempts` | Tracks retry budget; prevents infinite loops |
| `force_finalize` | Forces exit after max retries |
| `validation_result` | Carries validation verdict to final_answer |
| `source_documents` | Ground truth for claim attribution |
| `retrieval_cache` | Deduplicates retrieval calls across tasks |

---

### 2.4 In a LangGraph-based Policy Assistant, how is state maintained and managed across multi-turn conversations?

**State schema**

The `ChatState` TypedDict defines the complete state envelope for one conversation turn:

```python
class ChatState(TypedDict):
    user_id: str
    message: str
    channel: str
    session: dict           # full conversation history
    memory: Optional[dict]  # long-term user context
    intent: Optional[str]
    intent_result: Optional[dict]
    policies: Optional[list]
    policy_ids: Optional[List[str]]
    policy_data: Optional[dict]
    structured_data: Optional[dict]
    response: Optional[str]
    final_output: Optional[dict]
    has_greeted: Optional[bool]
    greeting_count: Optional[int]
```

**Memory lifecycle**

Every graph execution follows the same memory lifecycle:

```
memory_load → intent → [flow-specific nodes] → memory_update → FINISH
```

- `memory_load_node` pulls the user's conversation history and long-term memory at the start of every turn.
- All intermediate nodes modify the state in-place (LangGraph merges partial dicts).
- `memory_update_node` persists the updated conversation history back to the session store.
- Every path through the graph (greeting, out-of-scope, FAQ, policy flow, ticket, clarification) is wired to `memory_update` before finishing, guaranteeing no turn is lost.

**Conversation history for query reformulation**

The chat history in `session` is used to reformulate ambiguous follow-up queries before retrieval. For example, "What about my other policy?" is expanded using prior turns to "What are the coverage details of [Policy B] for user X?" This context-aware reformulation is a key driver of answer quality improvement.

**Greeting state tracking**

`has_greeted` and `greeting_count` are examples of lightweight inter-turn state — the greeting node gives a progressively shorter greeting on repeated `GREETING` intents without needing to query an external store.

---

### 2.5 What criteria determine whether a task should be routed to smaller versus larger models, and which performance or cost metrics guide this decision?

**Routing logic**

Model selection is configured per-agent via MongoDB (`agent_name` → model config), enabling per-client and per-workflow tuning without code changes:

```python
llm = get_llm_for_org(
    org_id, aws_region, configs,
    agent_name="categories_agent"   # ← determines model from config
)
```

**General routing heuristics**

| Task type | Model size | Reasoning |
|-----------|-----------|-----------|
| Intent classification | Small (e.g., GPT-4o-mini, Claude Haiku) | Binary/categorical output; latency critical |
| Query rewriting | Small | Short structured output; runs on every query |
| Chunking (document processing) | Medium | Needs semantic understanding; offline, not latency-critical |
| Planning & breakdown (underwriting) | Medium-large | Complex JSON; errors compound downstream |
| Response generation | Large | Quality is the primary metric; user-facing |
| Reranking | Dedicated reranker (Titan Rerank) | Cross-encoder; not a generative task |
| General greeting/FAQ | Small | Simple, templated responses |

**Metrics guiding decisions**

- **Latency**: Intent classification must complete in <1s; generation can tolerate 5–8s.
- **Token cost**: Small models cost ~10–20x less per token.
- **Error compounding**: Planning errors propagate to all downstream tasks — here, a larger model's accuracy justifies the cost.
- **Output structure**: Tasks requiring strict JSON (plans, breakdowns) benefit from larger models whose instruction-following is more reliable.
- **Token usage**: With token reduction from 17K → 8–10K, the remaining tokens are concentrated on high-value generation calls.

---

## 3. System Design & Optimization

### 3.1 What optimizations can reduce system latency from 25 seconds to 15 seconds in an LLM-powered pipeline?

The system achieved a ~40% latency reduction on complex policy queries through a combination of complementary optimisations:

**1. Replace LLM-based reranking with a dedicated reranker**

The largest single improvement. LLM-based ranking required a full generative inference pass per candidate document. AWS Titan Rerank (a cross-encoder) processes all candidates in a single forward pass, reducing reranking time from ~8s to ~1s for a typical candidate set.

**2. FAQ caching layer (Redis)**

Frequently asked questions are cached in Redis at the response level. Cache hits skip the entire retrieval + generation pipeline:

```
Query → FAQ cache check → HIT: return cached response (< 100ms)
                       → MISS: full pipeline (15s)
```

**3. Prompt caching (Redis, 6-hour TTL)**

Every LLM call requires a system prompt. These are fetched from MongoDB and cached in Redis for 6 hours:

```python
cache_key = f"prompt:{org_id}:{prompt_name}"
redis_client.set(cache_key, prompt_text, ex=21600)
```

This eliminates a MongoDB round-trip on every node execution.

**4. BM25 in-memory cache**

BM25 statistics are loaded from MongoDB once per service instance and cached in memory (`bm25_cache`), eliminating repeated DB reads on every hybrid retrieval call.

**5. Reduced token footprint (17K → 8–10K)**

- FINAL_TOP_K=12 chunks instead of larger sets
- Structured intermediate representations instead of raw document text
- Summary + title concatenated as embedding text, not full document sections
- Rule engine handles computations, removing raw transactional data from prompts

**6. LLM routing (small models for lightweight tasks)**

Intent classification, query rewriting, and greeting responses use small models with sub-second latency. Only generation and planning use larger models.

**7. Parallel tool execution in underwriting**

The task handler executes all retrieval tasks concurrently using `asyncio` + `ThreadPoolExecutor`, reducing multi-task queries from sequential to near-parallel:

```python
# Before: 3 tasks × 4s = 12s
# After: 3 tasks in parallel ≈ 4s
```

---

### 3.2 How is a system designed to handle concurrent traffic of ~30 TPS while maintaining multi-tenant isolation, and what are the typical bottlenecks?

**Concurrency model**

FastAPI with async endpoints allows many requests to be in-flight simultaneously without blocking. The `ContextVar` pattern ensures that each request carries its own tenant config without thread-local conflicts:

```python
client_config_var: ContextVar["Client_Config"] = ContextVar("client_config")
# Set at request entry, read by all downstream services within the same async task
```

**Rate limiting**

Per-tenant rate limiting is enforced at the middleware layer using `slowapi`, keyed to `organization-id` header:

```python
key_func=get_request_rate_limit_key   # "org:{organization_id}" or IP
default_limits=["100/minute", "1000/hour"]
```

This prevents a single tenant from monopolising shared LLM and vector DB capacity.

**Connection pooling**

- MongoDB: shared `MongoConnectionManager` singleton; clients are reused across requests.
- Redis: `StrictRedis` client is module-level, shared across all requests.
- Pinecone: index client is instantiated once per `KnowledgeBaseManager` instance.

**Typical bottlenecks**

| Bottleneck | Root cause | Mitigation |
|-----------|------------|-----------|
| LLM provider rate limits | External API quotas | Model routing (small models for non-critical), request queuing |
| Pinecone query latency | Vector search + metadata filtering | Namespace-scoped queries, top_k tuning |
| Cold-start BM25 loads | First request per instance | In-memory BM25 cache; pre-warm on startup |
| MongoDB prompt fetches | Per-call DB reads | Redis prompt cache (6-hour TTL) |
| Async/sync boundary | LangGraph is sync; tools are async | `ThreadPoolExecutor` + `asyncio.new_event_loop()` per call |

**Current constraint**: ~30 TPS is infrastructure-constrained (compute / LLM provider concurrency limits), not architecture-constrained. The stateless design supports horizontal scaling.

---

### 3.3 How does a MongoDB-based configuration layer enable per-client customisation, and what does this look like in a production setup?

**Config structure**

Each tenant's configuration is stored as a document in the `config` MongoDB collection, keyed by `org_id`:

```json
{
  "org_id": "client_abc",
  "config": {
    "OPENAI_API_KEY": "...",
    "LLM_PROVIDER": "openai",
    "CHUNKING_LLM_ID": "gpt-4o-mini",
    "QUERY_REWRITER_LLM_ID": "gpt-4o-mini",
    "GENERATION_LLM_ID": "gpt-4o",
    "top_k": 15,
    "FEATURE_UNDERWRITING": true,
    "FEATURE_CAM": false,
    "AWS_REGION": "ap-south-1"
  }
}
```

**What can be configured per client**

| Category | Examples |
|----------|---------|
| Model / provider | OpenAI GPT-4o, AWS Bedrock Claude, Gemini; mix per workflow |
| Agent-level toggles | Enable/disable specific agents (underwriting, CAM, SQL) |
| Retrieval tuning | `top_k`, `max_concurrency`, reranker model |
| Prompts | Full prompt override per `prompt_name` in `prompts_v2` |
| Cost control | Small model for certain workflows, larger for others |

**Prompt override system**

Prompts are versioned and tenant-scoped in a `prompts_v2` collection. Any prompt can be overridden per tenant without code changes. Overrides take precedence; missing prompts fall back to the default org's prompt:

```python
doc = collection_prompt.find_one({"org_id": org_id, "prompt_name": prompt_name})
if not doc:
    # Fallback to DEFAULT_ORG_ID
    doc = collection_prompt.find_one({"org_id": DEFAULT_ORG_ID, "prompt_name": prompt_name})
```

**Live updates without restart**

Prompts are cached in Redis for 6 hours. When a prompt is updated via the API, the cache key is immediately invalidated (`redis_client.delete(cache_key)`), so the next request picks up the new prompt without requiring a service restart. Config changes (non-prompt) take effect on the next request because config is fetched per-request via `client_config_var`.

---

### 3.4 What architectural changes are required to scale such a system from 30 TPS to 100 TPS efficiently?

The current architecture is designed for horizontal scaling. Moving from 30 to 100 TPS primarily requires infra changes, with targeted code changes to remove remaining bottlenecks:

**Infrastructure changes**

| Component | Change |
|-----------|--------|
| App servers | Scale out (3–4× replicas); stateless FastAPI instances scale linearly |
| Redis | Upgrade to Redis Cluster; increase max connections |
| MongoDB | Add read replicas for config/prompt reads; shard `sparse_vector_store` by `org_id` |
| Pinecone | Upgrade pod type or switch to serverless for auto-scaling |
| LLM provider | Use multiple API keys / providers in rotation; implement a request queue with backpressure |

**Code changes**

1. **Async BM25 initialisation**: Pre-warm BM25 cache on service startup to eliminate cold-start latency on early requests.

2. **Connection pool sizing**: Tune MongoDB and Redis pool sizes (`maxPoolSize`) for the higher concurrency.

3. **LLM request queue**: Add a token-bucket or semaphore-based queue in front of LLM calls to prevent provider rate-limit cascades under burst traffic.

4. **Response streaming**: For generation calls, stream tokens to the client as they arrive rather than waiting for the complete response. This improves perceived latency at scale without changing throughput.

5. **Pinecone batch upserts**: Already batched; tune batch size for higher indexing throughput.

6. **FAQ cache hit rate**: Invest in expanding the FAQ cache (broader query normalisation, semantic deduplication) to deflect more traffic before it reaches the LLM.

---

### 3.5 How is asynchronous processing structured in an underwriting system to improve throughput and responsiveness?

**The async/sync boundary problem**

LangGraph graphs execute synchronously (each node is a function returning a new state). However, retrieval tools (Pinecone queries, LLM calls) are inherently async. The system bridges this with a pattern using `asyncio.new_event_loop()` + `ThreadPoolExecutor`:

```python
if loop.is_running():
    import concurrent.futures
    def run_in_new_loop():
        def run_with_context():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(personal_policy_tool(...))
            finally:
                new_loop.close()
        return ctx.run(run_with_context)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.submit(run_in_new_loop).result()
```

A `contextvars.copy_context()` is used to propagate the tenant's `ContextVar` into the spawned thread, maintaining isolation across the async boundary.

**Parallel task execution**

The `PersonalTaskHandler` class executes all tasks for a given underwriting query concurrently via `asyncio`, bounded by `max_concurrency` (default 12). For a typical query with 3 tasks each taking 4s, this reduces wall time from 12s to ~4s.

**Async FastAPI endpoints**

All FastAPI route handlers are `async def`, allowing the event loop to handle other requests while waiting for I/O (Pinecone, MongoDB, Redis, LLM). This is the primary mechanism by which 30 TPS is achieved on a modest number of workers.

---

## 4. Voice AI & Real-time Systems

### 4.1 What is an effective approach to integrating speech-to-text and text-to-speech capabilities into a Policy QA system?

**Architecture overview**

A voice-enabled Policy QA system adds two layers around the existing text pipeline:

```
[Microphone] → STT → text query → [Policy QA pipeline] → response text → TTS → [Speaker]
```

**Speech-to-Text (STT)**

- **Provider options**: AWS Transcribe (low latency, good for Indian English), OpenAI Whisper (high accuracy, slightly higher latency), Google Speech-to-Text (strong multilingual support for Hindi/regional languages).
- **Streaming transcription**: Use streaming APIs (AWS Transcribe Streaming, Whisper live) rather than batch transcription to start processing as the user speaks, reducing perceived latency.
- **Noise handling**: Apply voice activity detection (VAD) before passing audio to STT to strip silence and background noise, improving accuracy and reducing wasted tokens.
- **Domain adaptation**: Fine-tune or provide a custom vocabulary for insurance/HR-specific terms (e.g., "CIBIL", "hospitalisation", "ESIC") that generic models frequently mis-transcribe.

**Text-to-Speech (TTS)**

- **Provider options**: AWS Polly (low latency, Indian English voices), ElevenLabs (highest quality), Google TTS (multilingual).
- **Streaming synthesis**: Use chunked/streaming TTS rather than waiting for the complete response. As soon as the first sentence is generated, begin synthesis. The user hears audio while the rest of the response is still being generated.
- **Response formatting**: Strip markdown, bullet points, and special characters from the LLM response before passing to TTS. A separate post-processing step converts structured responses to natural spoken language.

**Integration with the existing pipeline**

The LangGraph graph and retrieval pipeline remain unchanged. The voice layer acts as a thin adapter: STT converts audio to text (the `message` field in `ChatState`), the pipeline runs as-is, and TTS converts `final_output.message` back to audio. No changes to agent logic are needed.

---

### 4.2 What are the key design considerations when building a voice-based energy assistant, particularly regarding latency, interruption handling, and contextual continuity?

**Latency budget**

For a voice assistant, the target end-to-end latency (speech end → first audio word heard) is under 1.5 seconds. This requires aggressive optimisation at every stage:

| Stage | Target | Technique |
|-------|--------|-----------|
| STT | < 300ms | Streaming transcription; send partial results |
| Intent classification | < 100ms | Small model (Haiku/GPT-4o-mini); Redis cache |
| Retrieval | < 500ms | Pinecone hybrid query; FAQ cache hit |
| Generation (first token) | < 400ms | Streaming LLM; send TTS as tokens arrive |
| TTS (first chunk) | < 200ms | Streaming synthesis; 50-100ms chunk size |

**Interruption handling (barge-in)**

Users expect to interrupt the assistant mid-response, just as they would interrupt a human. Implementation:

1. Maintain a VAD stream in parallel with TTS playback.
2. When voice activity is detected during playback, immediately stop TTS audio output and cancel any in-flight LLM generation.
3. Forward the new speech to STT and restart the pipeline.
4. Update `ChatState.session` to include the interrupted exchange (partial response + new query) so the conversation history remains coherent.

**Contextual continuity**

- Multi-turn context is maintained in `ChatState.session`, exactly as in the text pipeline. Voice turns are treated identically to text turns.
- For domain-specific context (e.g., the user's active policy), store it in `ChatState.memory` so it persists across a session without the user needing to repeat it.
- After an interruption, the replanned response should acknowledge the interruption naturally ("Let me answer your new question instead") rather than resuming the previous response.

**Additional considerations**

- **Silence timeouts**: If the user pauses mid-sentence, use VAD end-of-speech detection with a 700ms–1s silence threshold rather than a fixed timer.
- **Fallback to text**: On high-noise or low-confidence STT transcription (confidence < threshold), prompt the user to rephrase or switch to text input.
- **Language detection**: Detect whether the user is speaking in Hindi, English, or a mix, and route to the appropriate model or prompt variant.

---

### 4.3 How can real-time streaming responses be implemented in a conversational AI system to ensure smooth and responsive user interactions?

**LLM streaming**

Most LLM providers support token-level streaming. In FastAPI, this is exposed as a `StreamingResponse` using Server-Sent Events (SSE) or WebSocket:

```python
from fastapi.responses import StreamingResponse

async def stream_tokens(query: str, org_id: str):
    async for chunk in llm.astream(prompt):
        yield f"data: {chunk.content}\n\n"

@router.get("/chat/stream")
async def chat_stream(query: str):
    return StreamingResponse(stream_tokens(query, org_id), media_type="text/event-stream")
```

**Progressive rendering on the client**

- For Slack/WhatsApp: use message editing (update the bot's message in-place as tokens arrive) rather than sending a new message per chunk.
- For web UIs: render a typing cursor and append characters as they arrive.

**Chunking strategy for voice**

When combining streaming LLM with TTS, buffer the LLM stream until a natural sentence boundary (`.`, `?`, `!`) is reached, then send the complete sentence to TTS. This avoids partial-sentence synthesis artefacts while still starting audio playback within 400–500ms of generation start.

**Partial retrieval results**

For long retrieval pipelines, consider streaming intermediate status updates (e.g., "Found 12 relevant policy clauses, generating answer...") to the client while the full pipeline runs. This improves perceived responsiveness even when actual latency is unchanged.

**Stateful streaming with LangGraph**

LangGraph supports event streaming via `graph.astream_events()`. Each node completion is an event that can be forwarded to the client, enabling detailed progress indicators (e.g., "Classifying intent... ✓", "Retrieving policies... ✓", "Generating response...").

---

## 5. Security, Access Control & Multi-Tenancy

### 5.1 How is API authentication and tenant isolation enforced at the request boundary?

**Authentication**

Every API request must carry two headers: `x-api-key` (the tenant's API key) and `organization-id`. The `AuthMiddleware` validates these against API keys stored in MongoDB, cached in Redis per organization:

```python
api_list = cfg.fetch_api_keys(organization_id)
if x_api_key not in api_list:
    raise HTTPException(status_code=401, detail="Invalid API key.")
```

API keys are cached in Redis for 6 hours to avoid per-request DB lookups at scale.

**Tenant context propagation**

After authentication, the `org_id` is bound to a `ContextVar` that flows through the entire async call chain for the request's lifetime. This ensures that every downstream service — vector DB queries, MongoDB lookups, LLM calls — automatically uses the correct tenant context without explicit parameter threading.

**RBAC and subscription gating**

Role-based access control is enforced at the route level. Feature flags in the per-client MongoDB config determine which agents and endpoints are accessible. A client without `FEATURE_CAM=true` in their config cannot invoke the CAM generation endpoints, regardless of authentication status.

---

### 5.2 How are secrets and API keys managed across multiple cloud providers in a multi-tenant setup?

**Secret storage**

Secrets (LLM API keys, cloud credentials) are stored in AWS Secrets Manager and AWS Parameter Store, accessed via `secretmanager/fetch_secret.py` and `aws_param_handler`. They are never stored in application config files or environment variables in plain text.

**Per-tenant API keys**

Each tenant's LLM provider API keys are stored in their MongoDB `config` document (encrypted at rest by the DB layer). The `AI_CONFIG` class constructs the correct credentials for the tenant's chosen provider at request time.

**Credential rotation**

Redis caching of API keys (6-hour TTL) means that rotated keys take effect within 6 hours without a service restart. For immediate rotation, the cache key can be explicitly invalidated.

---

### 5.3 How is the system protected against prompt injection attacks in a multi-tenant RAG environment?

Prompt injection is a meaningful risk when user-controlled text (queries, document content) is interpolated into LLM prompts. The system's defences are:

- **Structured output enforcement**: All LLM outputs are parsed as JSON with multiple fallback strategies. The system never executes or interprets LLM output as code or instructions — it is treated as data.
- **Retrieval content separation**: Retrieved document chunks are passed to the LLM in clearly delimited sections, reducing the attack surface for adversarial content embedded in indexed documents.
- **Tenant namespace isolation**: A malicious document indexed by one tenant cannot appear in another tenant's retrieval results.
- **Input validation**: The `organization_id` and query text are validated at the middleware layer before reaching any LLM call.
- **Output schema validation**: The `validate_decision` node rejects outputs that don't conform to expected structure, acting as a downstream guard even if an injection modifies the generation.

---

## 6. CAM Generation & Document Intelligence

### 6.1 How does the CAM generation pipeline handle heterogeneous document inputs with varying quality?

**Document preprocessing**

The pipeline's first stage normalises documents before any OCR or parsing occurs:

- **Orientation correction**: Scanned documents are programmatically corrected for rotation, flipping, and skew using image processing. This is critical because OCR accuracy degrades sharply on misaligned text.
- **Format detection**: File type is detected via MIME type (`mimetypes.guess_type`), and the appropriate parser is selected. XLSX/CSV files are read with `pandas.read_excel()` / `pandas.read_csv()` and converted directly to markdown tables, completely bypassing OCR.
- **Large PDF handling**: PDFs are checked for page count and file size (`check_large_pdf`). Files exceeding thresholds are split into per-page chunks (`split_pdf`) and processed in parallel via `ThreadPoolExecutor`, then merged.
- **PDF optimisation**: Low-quality or oversized PDFs are compressed (`compress_pdf` using `pikepdf`) before OCR to improve throughput.

**Multi-modal OCR**

- **Unstructured documents** (Aadhaar, PAN, general text): Processed via Google Document AI, which handles layout understanding, handwriting, and low-quality scans better than generic OCR engines.
- **Tabular financial data** (bank statements): Parsed with specialised tabular parsers that preserve row/column structure, converting to markdown tables for downstream processing.

**Structured extraction layer**

Raw OCR output is converted to normalised JSON before any LLM interaction. This JSON representation is the single source of truth for downstream processing — LLMs receive only the structured, cleaned representation, never raw OCR text with artifacts.

---

### 6.2 How does the rule engine prevent LLM hallucination in financial document processing?

The core insight is that LLMs are excellent at *interpretation* but unreliable at *computation*. The CAM pipeline enforces a strict separation:

**Rule engine responsibilities (deterministic)**
- Monthly inflow / outflow aggregation
- Average balance computation
- Transaction categorisation (salary credits, EMI debits, etc.)
- Derived financial ratios (FOIR, LTI)
- Threshold checks (minimum balance, salary consistency)

**LLM responsibilities (interpretive)**
- Narrative summarisation of financial behaviour
- Anomaly flagging and natural language explanation
- Cross-document consistency commentary
- Credit appraisal memo prose generation

**Why this matters**: Passing 300 rows of bank transactions to an LLM and asking it to compute "average monthly balance" introduces hallucination risk, unpredictable token costs, and non-reproducible results. The rule engine computes a single number; the LLM writes one sentence about it. This architecture reduced both hallucination risk and token usage substantially.

---

## 7. Observability, Debugging & Testing

### 7.1 How is the system debugged when an agent produces an incorrect or incomplete answer?

**Structured intermediate state**

LangGraph's state is the primary debugging tool. Every node transition produces a full state snapshot. Intermediate states can be logged or stored to trace exactly which retrieval results, task decompositions, and planning decisions led to the final answer.

**LangSmith tracing**

The underwriting agent uses `@traceable` decorators from LangSmith (with a graceful no-op fallback if LangSmith is unavailable):

```python
try:
    from langsmith.run_helpers import traceable
except Exception:
    def traceable(*args, **kwargs):
        def _decorator(fn): return fn
        return _decorator
```

Every tool call (`tool_personal_policy`, `tool_corporate_answer`, etc.) is traced with its input query, retrieved results, and latency — enabling replay and root-cause analysis.

**Print-based tracing in development**

Nodes emit structured print statements at key decision points (category classification, plan creation, task breakdown, replan decisions). These are visible in application logs and provide a human-readable trace of agent reasoning.

**Test bed**

A `test_bed.py` exists in both the services and policy agent directories for iterative testing of individual pipeline stages in isolation without running the full API server.

---

### 7.2 How are new clients onboarded onto the multi-tenant platform without code changes?

The modular OOP + MongoDB-driven design means onboarding a new client is a configuration exercise, not a development exercise:

1. **Create MongoDB config document**: Insert a new document in the `config` collection with the client's `org_id`, LLM provider credentials, feature flags, and model preferences.
2. **Create Pinecone namespace**: The namespace (`org_id`) is created implicitly on first upsert. No index changes are needed.
3. **Seed BM25 statistics**: Initialize the `sparse_vector_store` entries for the new `org_id`.
4. **Configure prompts**: Insert prompt overrides into `prompts_v2` for the client, or rely on defaults.
5. **Issue API key**: Add the client's API key to the `api_key` collection.
6. **Index documents**: Upload and index the client's policy documents via the existing ingestion API; they are isolated in the client's Pinecone namespace automatically.

No code deployment is required. A new client can be live within hours of completing the configuration steps.

---

### 7.3 How is the FAQ caching layer implemented, and what are the cache invalidation strategies?

**Cache structure**

The FAQ cache operates at the response level. A normalised form of the user query is used as the cache key. On a cache hit, the full `final_output` (including message and metadata) is returned without touching the retrieval or generation pipeline.

**Invalidation strategies**

| Trigger | Invalidation approach |
|---------|----------------------|
| Policy document updated | Invalidate all FAQ cache entries for the affected `org_id` |
| Prompt updated | `redis_client.delete(cache_key)` immediately on `upsert_prompt` |
| TTL expiry | Entries expire after a configured duration (default 6 hours for prompts) |
| Manual flush | Admin API to flush `org_id`-scoped cache entries |

**Cache key design**

Cache keys are always scoped to `org_id` to prevent cross-tenant cache pollution:

```
faq:{org_id}:{normalised_query_hash}
prompt:{org_id}:{prompt_name}
{org_id}_api_key
```

This namespace discipline means flushing one tenant's cache never affects another's.

---

*Document generated from the TartanHQ ai-be codebase — May 2026.*
