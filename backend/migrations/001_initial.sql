
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Champion metadata
CREATE TABLE IF NOT EXISTS champions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT,
    region TEXT,
    image_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Original source documents
CREATE TABLE IF NOT EXISTS lore_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT,
    continuity TEXT NOT NULL DEFAULT 'main',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Many-to-many champion-document relationship
CREATE TABLE IF NOT EXISTS document_champions (
    document_id UUID NOT NULL
        REFERENCES lore_documents(id) ON DELETE CASCADE,
    champion_id TEXT NOT NULL
        REFERENCES champions(id) ON DELETE CASCADE,
    PRIMARY KEY (document_id, champion_id)
);

-- 4. Searchable passages
CREATE TABLE IF NOT EXISTS lore_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL
        REFERENCES lore_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    content TEXT NOT NULL CHECK (length(content) > 0),
    embedding VECTOR(768) NOT NULL,
    embedding_model TEXT NOT NULL DEFAULT 'embeddinggemma',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (document_id, chunk_index)
);

-- Conventional indexes
CREATE INDEX IF NOT EXISTS idx_champions_region
    ON champions(region);

CREATE INDEX IF NOT EXISTS idx_chunks_document
    ON lore_chunks(document_id);

-- Vector similarity index
CREATE INDEX IF NOT EXISTS idx_chunks_embedding
    ON lore_chunks
    USING hnsw (embedding vector_cosine_ops);

-- Keyword-search index
CREATE INDEX IF NOT EXISTS idx_chunks_fts
    ON lore_chunks
    USING gin (to_tsvector('english', content));
