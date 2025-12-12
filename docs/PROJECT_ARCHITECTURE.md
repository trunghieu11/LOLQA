# 🏗️ Project Architecture & How It Works

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Component Breakdown](#component-breakdown)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [How Each Component Works](#how-each-component-works)
7. [Complete Request Lifecycle](#complete-request-lifecycle)
8. [Key Concepts Explained](#key-concepts-explained)

---

## 🎯 Project Overview

This is a **Retrieval Augmented Generation (RAG)** application that answers questions about League of Legends using:

- **LangChain 1.1.3**: For RAG implementation and LLM integration
- **LangGraph 1.0+**: For workflow orchestration
- **LangSmith**: For monitoring and observability
- **Streamlit**: For the web interface
- **ChromaDB**: For vector storage and semantic search

The application allows users to ask questions about League of Legends champions, abilities, game mechanics, and strategies, and receives accurate answers based on a knowledge base.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web Interface                   │
│                         (app.py)                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ User Question
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Workflow Orchestration               │
│                  (langgraph_workflow.py)                    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Extract    │→ │   Retrieve   │→ │   Generate   │     │
│  │   Question   │  │   Context    │  │   Answer     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                    │           │
└─────────┼─────────────────┼────────────────────┼───────────┘
          │                 │                    │
          ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG System                               │
│                  (rag_system.py)                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Vector Store (ChromaDB)                            │   │
│  │  - Stores document embeddings                       │   │
│  │  - Performs semantic search                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                        │                                     │
│                        ▼                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Retriever                                           │   │
│  │  - Finds relevant documents                          │   │
│  │  - Returns top-k similar chunks                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                        │                                     │
│                        ▼                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  LLM Chain (GPT-4o-mini)                            │   │
│  │  - Takes question + context                         │   │
│  │  - Generates answer                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Collector                                  │
│              (data_collector.py)                            │
│  - Creates sample League of Legends data                    │
│  - Converts to Document format                              │
│  - Splits into chunks                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Breakdown

### 1. **app.py** - Streamlit Web Interface

**Purpose**: Main entry point and user interface

**Key Functions**:
- `initialize_systems()`: Initializes RAG system and LangGraph workflow (cached)
- `process_query()`: Processes user questions (traced with LangSmith)
- `main()`: Streamlit UI setup and interaction handling

**How It Works**:
1. Loads environment variables (API keys)
2. Configures LangSmith for tracing
3. Initializes RAG system and LangGraph workflow on startup
4. Displays chat interface
5. When user asks a question:
   - Adds question to chat history
   - Calls `process_query()` which invokes LangGraph workflow
   - Displays the answer
   - Updates chat history

**Key Features**:
- Chat interface with message history
- Example question buttons
- Error handling
- LangSmith tracing integration

---

### 2. **rag_system.py** - RAG System Core

**Purpose**: Handles vector storage, retrieval, and answer generation

**Class**: `LoLRAGSystem`

**Key Components**:

#### A. **Initialization** (`initialize()` method)

1. **Embeddings Setup**:
   ```python
   self.embeddings = OpenAIEmbeddings()
   ```
   - Uses OpenAI's embedding model to convert text to vectors
   - Each document chunk becomes a high-dimensional vector

2. **LLM Setup**:
   ```python
   self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
   ```
   - Uses GPT-4o-mini for answer generation
   - Temperature 0.7 for balanced creativity/consistency

3. **Vector Store Creation/Loading**:
   - **If exists**: Loads existing ChromaDB vector store
   - **If not exists**:
     - Collects data from `LoLDataCollector`
     - Splits documents into chunks (1000 chars, 200 overlap)
     - Creates embeddings for each chunk
     - Stores in ChromaDB

4. **Retriever Setup**:
   ```python
   self.retriever = self.vectorstore.as_retriever(
       search_type="similarity",
       search_kwargs={"k": 3}
   )
   ```
   - Creates a retriever that finds top 3 most similar documents
   - Uses cosine similarity for matching

5. **QA Chain Creation**:
   ```python
   self.qa_chain = (
       {"context": self.retriever, "question": RunnablePassthrough()}
       | prompt
       | self.llm
       | StrOutputParser()
   )
   ```
   - Creates a LangChain Runnable chain
   - Flow: Question → Retrieve Context → Format Prompt → LLM → Parse Answer

#### B. **Query Method** (`query()` method)

1. Takes a question string
2. Invokes the QA chain
3. Returns the generated answer

#### C. **Document Retrieval** (`get_relevant_documents()` method)

1. Takes a question
2. Uses retriever to find similar documents
3. Returns list of relevant Document objects
4. Uses `invoke()` for LangChain 1.x compatibility

**How RAG Works**:
1. **Retrieval**: Finds relevant context from knowledge base
2. **Augmentation**: Adds context to the prompt
3. **Generation**: LLM generates answer using context + question

---

### 3. **langgraph_workflow.py** - Workflow Orchestration

**Purpose**: Orchestrates the Q&A process using LangGraph

**Class**: `LoLQAGraph`

**State Definition**:
```python
class GraphState(TypedDict):
    messages: Annotated[list, add_messages]  # Chat history
    question: str                            # Extracted question
    answer: str                              # Generated answer
    rag_context: str                         # Retrieved context
```

**Workflow Nodes**:

1. **extract_question**:
   - Extracts question from the latest message
   - Updates state with question

2. **retrieve_context**:
   - Calls RAG system's `get_relevant_documents()`
   - Formats retrieved documents into context string
   - Updates state with context

3. **generate_answer**:
   - Calls RAG system's `query()` method
   - Generates answer using LLM
   - Updates state with answer

4. **format_response**:
   - Formats the final response
   - Adds AI message to chat history
   - Returns final state

**Workflow Flow**:
```
extract_question → retrieve_context → generate_answer → format_response → END
```

**Why LangGraph?**:
- **State Management**: Tracks state across workflow steps
- **Modularity**: Each step is a separate node
- **Observability**: Easy to trace and debug
- **Extensibility**: Easy to add new steps (e.g., validation, filtering)

---

### 4. **data_collector.py** - Data Collection

**Purpose**: Creates and structures League of Legends knowledge base

**Class**: `LoLDataCollector`

**How It Works**:

1. **Champion Data Creation**:
   - Defines sample champion data (Ahri, Yasuo, Jinx, Thresh, Lee Sin)
   - Each champion has: name, role, description, abilities, playstyle

2. **Document Conversion**:
   - Converts each champion to a `Document` object
   - Formats content with structured information
   - Adds metadata (champion name, role, type)

3. **Game Mechanics**:
   - Adds general game mechanics documents
   - Covers: laning, objectives, teamfighting, positioning, vision
   - Adds item build information
   - Adds ranked system information

4. **Returns Documents**:
   - Returns list of `Document` objects
   - Ready for embedding and storage

**Document Structure**:
```python
Document(
    page_content="Champion: Ahri\nRole: Mage/Assassin\n...",
    metadata={"champion": "Ahri", "role": "Mage/Assassin", "type": "champion"}
)
```

---

## 🔄 Data Flow

### Complete Request Flow

```
1. User Input
   └─> Streamlit receives question: "What are Ahri's abilities?"

2. LangGraph Workflow Starts
   └─> Initial state created with question

3. Extract Question Node
   └─> Extracts: "What are Ahri's abilities?"
   └─> Updates state.question

4. Retrieve Context Node
   └─> RAG System: get_relevant_documents("What are Ahri's abilities?")
       └─> Retriever searches vector store
       └─> Finds top 3 similar document chunks
       └─> Returns: [Ahri document, ...]
   └─> Formats context string
   └─> Updates state.rag_context

5. Generate Answer Node
   └─> RAG System: query("What are Ahri's abilities?")
       └─> QA Chain invoked:
           ├─> Retriever finds relevant docs (already done)
           ├─> Prompt template filled:
           │   - Context: [Ahri's abilities info]
           │   - Question: "What are Ahri's abilities?"
           ├─> LLM (GPT-4o-mini) generates answer
           └─> Answer parsed and returned
   └─> Updates state.answer

6. Format Response Node
   └─> Formats answer
   └─> Adds to message history
   └─> Returns final state

7. Streamlit Display
   └─> Shows answer to user
   └─> Updates chat history
```

### Vector Store Creation Flow (First Run)

```
1. Data Collector
   └─> Creates sample League of Legends data
   └─> Returns list of Document objects

2. Text Splitting
   └─> RecursiveCharacterTextSplitter splits documents
   └─> Chunk size: 1000 chars, Overlap: 200 chars
   └─> Creates multiple chunks per document

3. Embedding Generation
   └─> OpenAIEmbeddings converts each chunk to vector
   └─> Each chunk → 1536-dimensional vector

4. Vector Store Creation
   └─> ChromaDB stores:
       - Document chunks (text)
       - Embeddings (vectors)
       - Metadata (champion, role, type)
   └─> Persisted to disk (chroma_db/)

5. Retriever Setup
   └─> Creates similarity search retriever
   └─> Configured to return top 3 results
```

---

## 🛠️ Technology Stack

### Core Libraries

1. **LangChain 1.1.3**
   - RAG framework
   - LLM integration
   - Chain composition
   - Document handling

2. **LangGraph 1.0+**
   - Workflow orchestration
   - State management
   - Graph-based execution

3. **LangSmith**
   - Monitoring and tracing
   - Performance tracking
   - Debugging tools

4. **OpenAI**
   - GPT-4o-mini for answer generation
   - Embeddings for vector creation

5. **ChromaDB**
   - Vector database
   - Similarity search
   - Persistent storage

6. **Streamlit**
   - Web interface
   - Chat UI
   - User interaction

### Supporting Libraries

- `langchain-openai`: OpenAI integrations
- `langchain-community`: Community integrations
- `langchain-chroma`: ChromaDB integration
- `langchain-text-splitters`: Text splitting utilities
- `langchain-core`: Core abstractions
- `python-dotenv`: Environment variable management

---

## 🔍 How Each Component Works

### 1. Embeddings & Vector Search

**What are Embeddings?**
- Numerical representations of text
- Similar texts have similar vectors
- Enables semantic search (meaning-based, not keyword-based)

**How It Works**:
```
Text: "Ahri's Q ability is Orb of Deception"
         ↓
   OpenAI Embeddings API
         ↓
Vector: [0.123, -0.456, 0.789, ..., 0.234] (1536 dimensions)
         ↓
   Stored in ChromaDB
```

**Similarity Search**:
- User question → Embedding vector
- Compare with all stored vectors
- Find vectors with highest cosine similarity
- Return corresponding documents

### 2. RAG (Retrieval Augmented Generation)

**Traditional LLM**:
```
Question → LLM → Answer
(No context, may hallucinate)
```

**RAG System**:
```
Question → Retrieve Relevant Context → LLM (with context) → Answer
(Accurate, based on knowledge base)
```

**Benefits**:
- ✅ More accurate answers
- ✅ Can cite sources
- ✅ Updatable knowledge base
- ✅ Reduces hallucinations

### 3. LangGraph Workflow

**Why Use LangGraph?**
- **State Management**: Tracks data across steps
- **Modularity**: Each step is independent
- **Observability**: Easy to debug and trace
- **Flexibility**: Can add conditional logic, loops, etc.

**State Flow**:
```
Initial State:
  messages: [HumanMessage("What are Ahri's abilities?")]
  question: ""
  answer: ""
  rag_context: ""

After extract_question:
  question: "What are Ahri's abilities?"

After retrieve_context:
  rag_context: "[Source 1]\nAhri's abilities...\n"

After generate_answer:
  answer: "Ahri has four abilities: Q - Orb of Deception..."

After format_response:
  messages: [HumanMessage(...), AIMessage("Ahri has four...")]
```

### 4. Document Chunking

**Why Chunk Documents?**
- LLMs have token limits
- Smaller chunks = better retrieval precision
- Overlap ensures context continuity

**Example**:
```
Original Document (2000 chars):
"Ahri is a mage... [long text] ...ultimate ability."

After Chunking (1000 chars, 200 overlap):
Chunk 1: "Ahri is a mage... [1000 chars]"
Chunk 2: "[200 chars overlap] ... [800 new chars] ...ultimate ability."
```

---

## 📊 Complete Request Lifecycle

### Step-by-Step Example

**User Question**: "How should I play Yasuo?"

#### Step 1: User Input (app.py)
```python
user_question = "How should I play Yasuo?"
st.session_state.messages.append({"role": "user", "content": user_question})
```

#### Step 2: LangGraph Invocation (langgraph_workflow.py)
```python
initial_state = {
    "messages": [HumanMessage(content="How should I play Yasuo?")],
    "question": "",
    "answer": "",
    "rag_context": ""
}
result = workflow.invoke(initial_state)
```

#### Step 3: Extract Question
```python
# Extracts from HumanMessage
question = "How should I play Yasuo?"
state["question"] = question
```

#### Step 4: Retrieve Context
```python
# RAG system searches vector store
docs = rag_system.get_relevant_documents("How should I play Yasuo?", k=3)

# Finds:
# - Yasuo champion document
# - Fighter/Assassin role document
# - Positioning guide

# Formats context
rag_context = "[Source 1]\nYasuo requires precise positioning...\n[Source 2]..."
state["rag_context"] = rag_context
```

#### Step 5: Generate Answer
```python
# QA Chain execution
answer = rag_system.query("How should I play Yasuo?")

# Internally:
# 1. Retriever finds relevant docs (already done in step 4)
# 2. Prompt template:
#    "Context: [Yasuo's playstyle info]
#     Question: How should I play Yasuo?
#     Answer:"
# 3. LLM generates:
#    "Yasuo requires precise positioning and timing..."
# 4. Returns answer

state["answer"] = answer
```

#### Step 6: Format Response
```python
# Adds AI response to messages
new_messages = messages + [AIMessage(content=answer)]
state["messages"] = new_messages
```

#### Step 7: Display Answer
```python
# Streamlit displays answer
st.markdown(answer)
st.session_state.messages.append({"role": "assistant", "content": answer})
```

---

## 🎓 Key Concepts Explained

### 1. **Vector Embeddings**

**What**: Numerical representation of text meaning

**Example**:
- "Ahri's Q ability" → `[0.1, -0.3, 0.5, ...]`
- "Ahri's first skill" → `[0.12, -0.28, 0.52, ...]` (similar!)
- "Yasuo's ultimate" → `[0.8, 0.2, -0.1, ...]` (different!)

**Why**: Enables semantic search - finds meaning, not just keywords

### 2. **Semantic Search**

**Traditional Search**: Keyword matching
- "Ahri abilities" → finds documents with words "Ahri" AND "abilities"

**Semantic Search**: Meaning matching
- "Ahri abilities" → finds documents about Ahri's skills, even if they say "Ahri's Q, W, E, R"

### 3. **RAG Chain**

**Components**:
1. **Retriever**: Finds relevant context
2. **Prompt Template**: Formats question + context
3. **LLM**: Generates answer
4. **Output Parser**: Formats response

**Flow**:
```
Question → Retriever → Context + Question → LLM → Answer
```

### 4. **LangGraph State**

**Purpose**: Maintains data across workflow steps

**Structure**:
- `messages`: Chat history (for conversation context)
- `question`: Current question being processed
- `answer`: Generated answer
- `rag_context`: Retrieved context (for debugging/transparency)

### 5. **Document Metadata**

**Purpose**: Filter and organize documents

**Example**:
```python
Document(
    page_content="Ahri's abilities...",
    metadata={
        "champion": "Ahri",
        "role": "Mage/Assassin",
        "type": "champion"
    }
)
```

**Use Cases**:
- Filter by champion
- Filter by document type
- Organize search results

---

## 🔧 Extending the Project

### Adding More Data

**In `data_collector.py`**:
```python
# Add more champions
champions.append({
    "name": "New Champion",
    "role": "Role",
    "description": "...",
    "abilities": {...},
    "playstyle": "..."
})

# Add new document types
documents.append(Document(
    page_content="New game mechanic...",
    metadata={"type": "new_type"}
))
```

### Changing the LLM

**In `rag_system.py`**:
```python
# Use different model
self.llm = ChatOpenAI(
    model="gpt-4",  # or "gpt-3.5-turbo"
    temperature=0.7,
)
```

### Adjusting Retrieval

**In `rag_system.py`**:
```python
# Get more/fewer documents
self.retriever = self.vectorstore.as_retriever(
    search_kwargs={"k": 5}  # Get top 5 instead of 3
)

# Use different search type
self.retriever = self.vectorstore.as_retriever(
    search_type="mmr",  # Maximum Marginal Relevance
    search_kwargs={"k": 3, "fetch_k": 10}
)
```

### Adding Workflow Steps

**In `langgraph_workflow.py`**:
```python
# Add validation node
def _validate_question(self, state: GraphState) -> GraphState:
    question = state.get("question", "")
    if len(question) < 3:
        return {**state, "answer": "Question too short"}
    return state

# Add to workflow
workflow.add_node("validate_question", self._validate_question)
workflow.add_edge("extract_question", "validate_question")
workflow.add_edge("validate_question", "retrieve_context")
```

---

## 📝 Summary

This project demonstrates a complete RAG application:

1. **Data Collection**: Creates structured knowledge base
2. **Vector Storage**: Stores documents as embeddings in ChromaDB
3. **Retrieval**: Finds relevant context using semantic search
4. **Generation**: Uses LLM to generate answers from context
5. **Orchestration**: LangGraph manages the workflow
6. **Interface**: Streamlit provides user-friendly UI
7. **Monitoring**: LangSmith tracks all operations

The architecture is modular, extensible, and follows best practices for production RAG applications.

---

**For more details on specific components, see:**
- `README.md` - Setup and usage
- `QUICKSTART.md` - Quick start guide
- `API_KEYS_SETUP.md` - API key configuration
- `INSTALL_LANGCHAIN_1.1.3.md` - Installation guide

