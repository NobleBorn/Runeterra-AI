
"use client";

import { useState, type KeyboardEvent } from "react";
import { ArrowUp, LoaderCircle } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export default function ChatInput({
  onSend,
  disabled,
}: ChatInputProps) {
  const [value, setValue] = useState("");

  function handleSubmit() {
    const message = value.trim();

    if (!message || disabled) return;

    onSend(message);
    setValue("");
  }

  function handleKeyDown(
    event: KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !event.nativeEvent.isComposing
    ) {
      event.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="rounded-2xl border border-[#405468] bg-[#101F2F] p-3 shadow-lg">
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        maxLength={1000}
        rows={2}
        placeholder="Ask anything about Runeterra lore..."
        aria-label="Your lore question"
        className="w-full resize-none bg-transparent px-2 py-1 text-sm text-[#F0E6D2] outline-none placeholder:text-[#8291A0] disabled:opacity-60"
      />

      <div className="flex items-center justify-between">
        <p className="text-xs text-[#8291A0]">
          Enter to send · Shift+Enter for new line
        </p>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={!value.trim() || disabled}
          aria-label="Send message"
          className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#C8AA6E] text-[#091522] transition hover:bg-[#E3C78D] disabled:cursor-not-allowed disabled:opacity-40"
        >
          {disabled ? (
            <LoaderCircle
              size={18}
              className="animate-spin"
            />
          ) : (
            <ArrowUp size={19} />
          )}
        </button>
      </div>
    </div>
  );
}
