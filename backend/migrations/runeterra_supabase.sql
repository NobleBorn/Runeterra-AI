--
-- PostgreSQL database dump
--

\restrict QX4UqcZJaeAEUt5HhtE6iIjK5QPSiHPH7ttxBhRDwQETet9Y9trI3cEsOAxdd8y

-- Dumped from database version 17.11 (Debian 17.11-1.pgdg13+2)
-- Dumped by pg_dump version 17.11 (Debian 17.11-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: champions; Type: TABLE; Schema: public; Owner: runeterra
--

CREATE TABLE public.champions (
    id text NOT NULL,
    name text NOT NULL,
    title text,
    region text,
    image_url text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);



--
-- Name: document_champions; Type: TABLE; Schema: public; Owner: runeterra
--

CREATE TABLE public.document_champions (
    document_id uuid NOT NULL,
    champion_id text NOT NULL
);



--
-- Name: lore_chunks; Type: TABLE; Schema: public; Owner: runeterra
--

CREATE TABLE public.lore_chunks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id uuid NOT NULL,
    chunk_index integer NOT NULL,
    content text NOT NULL,
    embedding extensions.vector(768) NOT NULL,
    embedding_model text DEFAULT 'embeddinggemma'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT lore_chunks_chunk_index_check CHECK ((chunk_index >= 0)),
    CONSTRAINT lore_chunks_content_check CHECK ((length(content) > 0))
);



--
-- Name: lore_documents; Type: TABLE; Schema: public; Owner: runeterra
--

CREATE TABLE public.lore_documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title text NOT NULL,
    source_url text NOT NULL,
    source_type text NOT NULL,
    content text NOT NULL,
    content_hash text,
    continuity text DEFAULT 'main'::text NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    source_key text
);



--
-- Name: champions champions_pkey; Type: CONSTRAINT; Schema: public; Owner: runeterra
--

ALTER TABLE ONLY public.champions
    ADD CONSTRAINT champions_pkey PRIMARY KEY (id);


--
-- Name: document_champions document_champions_pkey; Type: CONSTRAINT; Schema: public; Owner: runeterra
--

ALTER TABLE ONLY public.document_champions
    ADD CONSTRAINT document_champions_pkey PRIMARY KEY (document_id, champion_id);


--
-- Name: lore_chunks lore_chunks_document_id_chunk_index_key; Type: CONSTRAINT; Schema: public; Owner: runeterra
--

ALTER TABLE ONLY public.lore_chunks
    ADD CONSTRAINT lore_chunks_document_id_chunk_index_key UNIQUE (document_id, chunk_index);


--
-- Name: lore_chunks lore_chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: runeterra
--

ALTER TABLE ONLY public.lore_chunks
    ADD CONSTRAINT lore_chunks_pkey PRIMARY KEY (id);


--
-- Name: lore_documents lore_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: runeterra
--

ALTER TABLE ONLY public.lore_documents
    ADD CONSTRAINT lore_documents_pkey PRIMARY KEY (id);


--
-- Name: lore_documents lore_documents_source_url_key; Type: CONSTRAINT; Schema: public; Owner: runeterra
--

ALTER TABLE ONLY public.lore_documents
    ADD CONSTRAINT lore_documents_source_url_key UNIQUE (source_url);


--
-- Name: idx_champions_region; Type: INDEX; Schema: public; Owner: runeterra
--

CREATE INDEX idx_champions_region ON public.champions USING btree (region);


--
-- Name: idx_chunks_document; Type: INDEX; Schema: public; Owner: runeterra
--

CREATE INDEX idx_chunks_document ON public.lore_chunks USING btree (document_id);


--
-- Name: idx_chunks_embedding; Type: INDEX; Schema: public; Owner: runeterra
--

CREATE INDEX idx_chunks_embedding ON public.lore_chunks USING hnsw (embedding extensions.vector_cosine_ops);


--
-- Name: idx_chunks_fts; Type: INDEX; Schema: public; Owner: runeterra
--

CREATE INDEX idx_chunks_fts ON public.lore_chunks USING gin (to_tsvector('english'::regconfig, content));


--
-- Name: idx_lore_documents_source_key; Type: INDEX; Schema: public; Owner: runeterra
--

CREATE UNIQUE INDEX idx_lore_documents_source_key ON public.lore_documents USING btree (source_key);


--
-- Name: document_champions document_champions_champion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: runeterra
--

ALTER TABLE ONLY public.document_champions
    ADD CONSTRAINT document_champions_champion_id_fkey FOREIGN KEY (champion_id) REFERENCES public.champions(id) ON DELETE CASCADE;


--
-- Name: document_champions document_champions_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: runeterra
--

ALTER TABLE ONLY public.document_champions
    ADD CONSTRAINT document_champions_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.lore_documents(id) ON DELETE CASCADE;


--
-- Name: lore_chunks lore_chunks_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: runeterra
--

ALTER TABLE ONLY public.lore_chunks
    ADD CONSTRAINT lore_chunks_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.lore_documents(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict QX4UqcZJaeAEUt5HhtE6iIjK5QPSiHPH7ttxBhRDwQETet9Y9trI3cEsOAxdd8y

