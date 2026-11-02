
import type { ChatHistoryMessage, ChatStreamEvent, ChatResponse} from "@/types/chat";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";


export async function askRuneterra(
  message: string,
  signal?: AbortSignal
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
    signal,
  });

  if (!response.ok) {
    throw new Error(
      `Chat request failed: ${response.status}`
    );
  }

  const data: ChatResponse = await response.json();

  return data;
}


export async function streamRuneterra(
  message: string,
  history: ChatHistoryMessage[],
  onEvent: (event: ChatStreamEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
        message,
        history,
    }),
    signal,
  });

  if (!response.ok) {
    throw new Error(
      `Streaming request failed: ${response.status}`
    );
  }

  if (!response.body) {
    throw new Error("Streaming is not supported");
  }

  const reader = response.body
    .pipeThrough(new TextDecoderStream())
    .getReader();

  let buffer = "";
  let terminalEventReceived = false;

  function processLine(line: string) {
    const trimmed = line.trim();

    if (!trimmed) return;

    const event = JSON.parse(trimmed) as ChatStreamEvent;

    if (
      !["status", "token", "done", "error"].includes(
        event.type
      )
    ) {
      throw new Error("Unknown streaming event");
    }

    if (terminalEventReceived) {
      throw new Error("Received data after terminal event");
    }

    onEvent(event);

    if (event.type === "done") {
      terminalEventReceived = true;
    }

    if (event.type === "error") {
      terminalEventReceived = true;
      throw new Error(event.message);
    }
  }

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += value;

      let newlineIndex = buffer.indexOf("\n");

      while (newlineIndex !== -1) {
        const line = buffer.slice(0, newlineIndex);
        buffer = buffer.slice(newlineIndex + 1);

        processLine(line);

        newlineIndex = buffer.indexOf("\n");
      }

      // Protect against an unbounded incomplete line.
      if (buffer.length > 1_000_000) {
        throw new Error("Streaming event too large");
      }
    }

    // The final line might not end with a newline.
    if (buffer.trim()) {
      processLine(buffer);
    }

    if (!terminalEventReceived) {
      throw new Error(
        "Stream ended before the final response"
      );
    }
  } finally {
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}

