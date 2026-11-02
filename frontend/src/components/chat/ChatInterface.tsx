
"use client";

import {
  useEffect,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";

import {
  BookOpen,
  Menu,
  Plus,
  Trash2,
  X,
  LoaderCircle,
} from "lucide-react";

import { streamRuneterra } from "@/lib/api";

import type {
  ChatMessage as Message,
  Conversation,
  StreamStage,
} from "@/types/chat";

import { buildRecentHistory } from "@/lib/chatHistory";

import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

const STORAGE_KEY = "runeterra-conversations-v1";

const SUGGESTIONS = [
  "Who is Aatrox?",
  "What happened to Varus?",
  "Tell me about the Darkin.",
  "What is Warwick's origin?",
];

const subscribe = () => () => {};

function getClientSnapshot() {
  return true;
}

function getServerSnapshot() {
  return false;
}

function newConversation(): Conversation {
  return {
    id: crypto.randomUUID(),
    title: "New conversation",
    messages: [],
    createdAt: Date.now(),
  };
}

function loadConversations(): Conversation[] {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (!saved) return [];

    const parsed: unknown = JSON.parse(saved);

    return Array.isArray(parsed)
      ? (parsed as Conversation[])
      : [];
  } catch {
    return [];
  }
}

function createMessage(
  role: "user" | "assistant",
  content: string,
  sources: Message["sources"] = [],
  status?: Message["status"]
): Message {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    sources,
    status,
    createdAt: Date.now(),
  };
}

export default function ChatInterface() {
    const isClient = useSyncExternalStore(
        subscribe,
        getClientSnapshot,
        getServerSnapshot
    );

    const [conversations, setConversations] =
        useState<Conversation[]>(loadConversations);

    const [activeId, setActiveId] = useState<string | null>(
        () => loadConversations()[0]?.id ?? null
    );

  const [loading, setLoading] = useState(false);
  const [streamStage, setStreamStage] = useState<StreamStage | null>(null);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const pendingMessageRef = useRef<{
    conversationId: string;
    assistantId: string;
  } | null>(null);

  function removeIncompleteMessage(
    conversationId: string,
    assistantId: string
  ) {
    setConversations((current) =>
        current.map((conversation) =>
        conversation.id === conversationId
            ? {
                ...conversation,
                messages: conversation.messages.filter(
                (message) => message.id !== assistantId
                ),
            }
            : conversation
        )
    );
  }

  function cancelCurrentStream() {
        abortRef.current?.abort();
        abortRef.current = null;

        const pending = pendingMessageRef.current;

        if (pending) {
            removeIncompleteMessage(
            pending.conversationId,
            pending.assistantId
            );
        }

        pendingMessageRef.current = null;
        setLoading(false);
        setStreamStage(null);
    }

  // Save conversations whenever they change.
    useEffect(() => {
        if (!isClient) return;

        try {
            localStorage.setItem(
            STORAGE_KEY,
            JSON.stringify(conversations)
            );
        } catch {
            // Storage can be unavailable or full.
        }
    }, [conversations, isClient]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
        behavior: "auto",
    });
  }, [conversations, activeId, loading]);

  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  const activeConversation = conversations.find(
    (conversation) => conversation.id === activeId
  );

  function startNewConversation() {
    cancelCurrentStream();

    const conversation = newConversation();

    setConversations((current) => [
      conversation,
      ...current,
    ]);

    setActiveId(conversation.id);
    setLoading(false);
    setError("");
    setSidebarOpen(false);
  }

  function selectConversation(id: string) {
    cancelCurrentStream();

    setActiveId(id);
    setLoading(false);
    setError("");
    setSidebarOpen(false);
  }

  function deleteConversation(id: string) {
    cancelCurrentStream();

    const remaining = conversations.filter(
      (conversation) => conversation.id !== id
    );

    setConversations(remaining);

    if (activeId === id) {
      setActiveId(remaining[0]?.id ?? null);
    }

    setLoading(false);
    setError("");
  }

  const STAGE_LABELS: Record<StreamStage, string> = {
    understanding_question: "Understanding your question...",
    retrieving: "Searching the archives of Runeterra...",
    checking_evidence: "Checking lore evidence...",
    generating: "Runeterra AI is writing...",
  };

  
  async function handleSend(text: string) {
    if (loading) return;

    const history = buildRecentHistory(
        activeConversation?.messages ?? []
    );

    const conversationId =
        activeId ?? crypto.randomUUID();

    const userMessage = createMessage("user", text);

    // Prepare one stable ID for the streamed response.
    const assistantMessage = createMessage("assistant", "");

    const assistantId = assistantMessage.id;

    pendingMessageRef.current = {
        conversationId,
        assistantId,
    };

    // Add the user's message immediately.
    setConversations((current) => {
        const exists = current.some(
        (conversation) => conversation.id === conversationId
        );

        if (!exists) {
        return [
            {
            id: conversationId,
            title: text.slice(0, 42),
            messages: [userMessage],
            createdAt: userMessage.createdAt,
            },
            ...current,
        ];
        }

        return current.map((conversation) =>
        conversation.id === conversationId
            ? {
                ...conversation,
                title:
                conversation.messages.length === 0
                    ? text.slice(0, 42)
                    : conversation.title,
                messages: [
                ...conversation.messages,
                userMessage,
                ],
            }
            : conversation
        );
    });

    setActiveId(conversationId);
    setLoading(true);
    setStreamStage("retrieving");
    setError("");

    const controller = new AbortController();
    abortRef.current = controller;

    function updateAssistant(
        content: string,
        replace: boolean,
        sources: Message["sources"] = [],
        status?: Message["status"]
    ) {
        setConversations((current) =>
        current.map((conversation) => {
            if (conversation.id !== conversationId) {
            return conversation;
            }

            const existing = conversation.messages.find(
            (message) => message.id === assistantId
            );

            if (!existing) {
            return {
                ...conversation,
                messages: [
                ...conversation.messages,
                {
                    ...assistantMessage,
                    content,
                    sources,
                    status,
                },
                ],
            };
            }

            return {
            ...conversation,
            messages: conversation.messages.map(
                (message) =>
                message.id === assistantId
                    ? {
                        ...message,
                        content: replace
                        ? content
                        : message.content + content,
                        sources: replace
                        ? sources
                        : message.sources,
                        status: replace
                        ? status
                        : message.status,
                    }
                    : message
            ),
            };
        })
        );
    }

    try {
        await streamRuneterra(
        text,
        history,
        (event) => {
            if (controller.signal.aborted) return;

            switch (event.type) {
            case "status":
                setStreamStage(event.stage);
                break;

            case "token":
                // Text is provisional until 'done'.
                updateAssistant(event.content, false);
                break;

            case "done":
                // Replace provisional text with the
                // final validated response.
                updateAssistant(
                event.answer,
                true,
                event.sources,
                event.status
                );
                pendingMessageRef.current = null;
                break;

            case "error":
                throw new Error(event.message);
            }
        },
        controller.signal
        );
    } catch (err) {
        // Always remove an incomplete assistant response.
        setConversations((current) =>
            current.map((conversation) =>
            conversation.id === conversationId
                ? {
                    ...conversation,
                    messages: conversation.messages.filter(
                    (message) => message.id !== assistantId
                    ),
                }
                : conversation
            )
        );

        // Cancellation is intentional, so don't show an error.
        if (controller.signal.aborted) return;

        setError(
            err instanceof Error
            ? err.message
            : "Streaming failed. Please try again."
        );
    } finally {
        if (abortRef.current === controller) {
        abortRef.current = null;
        setLoading(false);
        setStreamStage(null);
        }
    }
 }


  if (!isClient) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#091522] text-[#C8AA6E]">
        <LoaderCircle className="animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex h-dvh bg-[#091522] text-[#F0E6D2]">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-30 w-72 border-r border-[#283D51] bg-[#0D1B2A] transition-transform md:static md:translate-x-0 ${
          sidebarOpen
            ? "translate-x-0"
            : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b border-[#283D51] p-5">
          <span className="font-bold tracking-wider text-[#C8AA6E]">
            RUNETERRA AI
          </span>

          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden"
            aria-label="Close sidebar"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-4">
          <button
            onClick={startNewConversation}
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-[#C8AA6E] p-3 text-sm text-[#C8AA6E] transition hover:bg-[#1A2A39]"
          >
            <Plus size={17} />
            New conversation
          </button>
        </div>

        <nav
          className="space-y-1 overflow-y-auto px-3"
          aria-label="Conversations"
        >
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`group flex items-center rounded-lg ${
                conversation.id === activeId
                  ? "bg-[#20364B]"
                  : "hover:bg-[#14283A]"
              }`}
            >
              <button
                onClick={() =>
                  selectConversation(conversation.id)
                }
                className="min-w-0 flex-1 truncate px-3 py-3 text-left text-sm"
              >
                {conversation.title}
              </button>

              <button
                onClick={() =>
                  deleteConversation(conversation.id)
                }
                aria-label={`Delete ${conversation.title}`}
                className="p-2 text-[#8291A0] hover:text-red-400"
              >
                <Trash2 size={15} />
              </button>
            </div>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 shrink-0 items-center gap-3 border-b border-[#283D51] px-5">
          <button
            onClick={() => setSidebarOpen(true)}
            className="md:hidden"
            aria-label="Open sidebar"
          >
            <Menu size={22} />
          </button>

          <BookOpen
            size={22}
            className="text-[#C8AA6E]"
          />

          <div>
            <h1 className="font-semibold">Runeterra AI</h1>
            <p className="text-xs text-[#8291A0]">
              League of Legends Lore Companion
            </p>
          </div>

          <span className="ml-auto rounded-full border border-emerald-800 px-3 py-1 text-xs text-emerald-400">
            Local AI
          </span>
        </header>

        <div className="min-h-0 flex-1 overflow-y-auto">
          <div className="mx-auto max-w-3xl space-y-6 p-5 md:p-8">
            {!activeConversation?.messages.length ? (
              <div className="py-16 text-center">
                <BookOpen
                  size={42}
                  className="mx-auto mb-5 text-[#C8AA6E]"
                />

                <h2 className="mb-3 text-3xl font-bold">
                  Explore Runeterra
                </h2>

                <p className="mb-8 text-sm text-[#8291A0]">
                  Discover champions, histories, and legends.
                </p>

                <div className="grid gap-3 sm:grid-cols-2">
                  {SUGGESTIONS.map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => handleSend(suggestion)}
                      disabled={loading}
                      className="rounded-xl border border-[#304658] bg-[#101F2F] p-4 text-left text-sm transition hover:border-[#C8AA6E] disabled:opacity-50"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              activeConversation.messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                />
              ))
            )}

            {loading && (
                <div
                    className="flex items-center gap-3 text-sm text-[#C8AA6E]"
                    role="status"
                    aria-live="polite"
                >
                    <LoaderCircle
                    size={18}
                    className="animate-spin"
                    />

                    <span>
                    {streamStage
                        ? STAGE_LABELS[streamStage]
                        : "Preparing response..."}
                    </span>
                </div>
            )}

            {error && (
              <div
                role="alert"
                className="rounded-lg border border-red-800 bg-red-950/40 p-3 text-sm text-red-300"
              >
                {error}
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        </div>

        <div className="shrink-0 border-t border-[#283D51] bg-[#091522] p-4">
          <div className="mx-auto max-w-3xl">
            <ChatInput
              onSend={handleSend}
              disabled={loading}
            />

            <p className="mt-2 text-center text-xs text-[#8291A0]">
              AI-generated answers may contain mistakes.
              Verify important lore using the cited sources.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
