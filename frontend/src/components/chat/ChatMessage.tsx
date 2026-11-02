
import { BookOpen, UserRound } from "lucide-react";
import type { ChatMessage as Message } from "@/types/chat";
import SourceList from "./SourceList";

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({
  message,
}: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <article
      className={`flex gap-3 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      {!isUser && (
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-[#5B4B32] bg-[#172838] text-[#C8AA6E]">
          <BookOpen size={18} />
        </div>
      )}

      <div
        className={`min-w-0 max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? "rounded-br-sm bg-[#1D3B52] text-[#F0E6D2]"
            : "rounded-bl-sm border border-[#304658] bg-[#101F2F] text-[#E6DDD0]"
        }`}
      >
        {!isUser && (
          <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-[#C8AA6E]">
            Runeterra AI
          </p>
        )}

        <p className="whitespace-pre-wrap wrap-break-words text-sm leading-7">
          {message.content}
        </p>

        {!isUser &&
          message.status === "insufficient_evidence" && (
            <p className="mt-3 text-xs text-amber-300">
              Insufficient lore evidence
            </p>
          )}

        {!isUser && (
          <SourceList sources={message.sources} />
        )}
      </div>

      {isUser && (
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#1D3B52] text-[#C8AA6E]">
          <UserRound size={18} />
        </div>
      )}
    </article>
  );
}
