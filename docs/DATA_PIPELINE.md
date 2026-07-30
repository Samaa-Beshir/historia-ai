# Data Pipeline

Raw Dataset → EDA → Cleaning → Normalization → Chunking → Embedding
Generation → ChromaDB

## Rules

-   Never modify raw data.
-   metadata.csv is authoritative.
-   Chunks contain cleaned text only.
-   Metadata is stored separately and linked by document_id.
