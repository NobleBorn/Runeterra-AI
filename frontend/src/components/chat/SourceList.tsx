
import { BookOpen, ExternalLink } from "lucide-react";
import type { SourceReference } from "@/types/chat";

interface SourceListProps {
  sources: SourceReference[];
}

export default function SourceList({
  sources,
}: SourceListProps) {
  if (sources.length === 0) return null;

  return (
    <section className="mt-4 space-y-2">
      <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[#C8AA6E]">
        <BookOpen size={14} />
        Sources
      </div>

      <div className="flex flex-wrap gap-2">
        {sources.map((source) => {
          const isValidUrl =
            source.url.startsWith("https://") ||
            source.url.startsWith("http://");

          return (
            <a
              key={source.chunk_id}
              href={isValidUrl ? source.url : undefined}
              target="_blank"
              rel="noopener noreferrer"
              title={source.content}
              className="flex items-center gap-2 rounded-lg border border-[#384C60] bg-[#142536] px-3 py-2 text-sm text-[#C8AA6E] transition hover:border-[#C8AA6E]"
            >
              <span>
                [{source.id}] {source.title}
              </span>

              <ExternalLink size={13} />
            </a>
          );
        })}
      </div>
    </section>
  );
}
