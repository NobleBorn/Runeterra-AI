
export type AnswerStatus =
  | "answered"
  | "partial"
  | "insufficient_evidence";

export interface SourceReference {
  id: number;
  chunk_id: string;
  document_id: string;
  title: string;
  url: string;
  content: string;
}

export interface ChatResponse {
  answer: string;
  sources: SourceReference[];
  status: AnswerStatus;
  grounded: boolean;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources: SourceReference[];
  status?: AnswerStatus;
  createdAt: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
}

export type StreamStage =
  | "understanding_question"
  | "retrieving"
  | "checking_evidence"
  | "generating";


export type ChatStreamEvent =
  | {
      type: "status";
      stage: StreamStage;
    }
  | {
      type: "token";
      content: string;
    }
  | ({
      type: "done";
    } & ChatResponse)
  | {
      type: "error";
      message: string;
    };

    
export interface ChatHistoryMessage {
  role: "user" | "assistant";
  content: string;
}
