# System Architecture

## Layers

1.  API Layer
2.  Service Layer
3.  AI Layer
4.  Data Layer

## Cross Cutting

-   Logging
-   Validation
-   Error Handling
-   Authentication
-   Rate Limiting
-   Configuration

## RAG Pipeline

Question → Embedding → Top-K Retrieval → Context Builder → Prompt
Builder → LLM → Response

## Rules

-   Retrieval always precedes generation.
-   metadata.csv is the single source of truth.
-   Configuration is externalized.
