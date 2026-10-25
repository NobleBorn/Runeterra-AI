
"use client";

import { useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAsk(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!message.trim() || loading) return;

    setLoading(true);
    setError("");
    setAnswer("");

    try {
      const response = await fetch(
        "http://localhost:8000/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: message.trim()
          })
        }
      );

      if (!response.ok) {
        throw new Error("The request failed");
      }

      const data = await response.json();
      setAnswer(data.answer);
    } catch {
      setError("Could not connect to the backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-3xl p-8">
      <h1 className="mb-2 text-4xl font-bold">
        Runeterra AI
      </h1>

      <p className="mb-8 text-gray-500">
        Explore the world of League of Legends.
      </p>

      <form onSubmit={handleAsk} className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask about Runeterra lore..."
          className="flex-1 rounded border p-3"
        />

        <button
          type="submit"
          disabled={loading}
          className="rounded bg-blue-700 px-5 py-3 text-white disabled:opacity-50"
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>

      {error && (
        <p className="mt-4 text-red-500">{error}</p>
      )}

      {answer && (
        <div className="mt-8 rounded-lg border p-5">
          <h2 className="mb-3 font-bold">
            Runeterra AI
          </h2>
          <p className="whitespace-pre-wrap">{answer}</p>
        </div>
      )}
    </main>
  );
}
