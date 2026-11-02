ALTER TABLE lore_documents
ADD COLUMN IF NOT EXISTS source_key TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS
    idx_lore_documents_source_key
ON lore_documents (source_key);