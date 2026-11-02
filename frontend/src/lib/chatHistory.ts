
import type {
  ChatMessage,
  ChatHistoryMessage,
} from "@/types/chat";

const MAX_TURNS = 3;
const MAX_HISTORY_CHARS = 1500;

export function buildRecentHistory(
  messages: ChatMessage[]
): ChatHistoryMessage[] {
  const turns: ChatHistoryMessage[][] = [];

  for (let i = 0; i < messages.length - 1; i++) {
    const user = messages[i];
    const assistant = messages[i + 1];

    // Only include complete user/assistant pairs.
    if (
      user.role !== "user" ||
      assistant.role !== "assistant"
    ) {
      continue;
    }

    // A message without a status may be an
    // unfinished streamed response.
    if (
      assistant.status !== "answered" &&
      assistant.status !== "partial"
    ) {
      continue;
    }

    const userText = user.content.trim();
    const assistantText = assistant.content.trim();

    if (!userText || !assistantText) continue;

    turns.push([
      {
        role: "user",
        content: userText.slice(0, MAX_HISTORY_CHARS),
      },
      {
        role: "assistant",
        content: assistantText.slice(
          0,
          MAX_HISTORY_CHARS
        ),
      },
    ]);

    i++; // Skip the assistant message in this pair.
  }

  return turns
    .slice(-MAX_TURNS)
    .flat();
}
