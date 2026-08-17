"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { ChevronDown, Loader2, MessageCircleQuestion, Search, SearchX, Clock } from "lucide-react";
import { get, post, ApiError } from "@/lib/api-client";
import { PassageResult, type Passage } from "./passage-result";

interface ContractOption {
  id: string;
  name: string;
}

interface ContractListResponse {
  items: (ContractOption & { status: string })[];
}

interface AskResponse {
  passages: Passage[];
  message: string | null;
}

type AskState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "answered"; passages: Passage[]; message: string | null }
  | { kind: "not-ready" }
  | { kind: "error"; message: string };

const LOADING_LINES = [
  "Reading through clauses\u2026",
  "Cross-referencing sections\u2026",
  "Ranking the closest matches\u2026",
];

export function AskPanel() {
  const [contracts, setContracts] = useState<ContractOption[]>([]);
  const [contractsLoading, setContractsLoading] = useState(true);
  const [contractsError, setContractsError] = useState<string | null>(null);

  const [contractId, setContractId] = useState("");
  const [question, setQuestion] = useState("");
  const [askedQuestion, setAskedQuestion] = useState("");
  const [askState, setAskState] = useState<AskState>({ kind: "idle" });
  const [loadingLine, setLoadingLine] = useState(LOADING_LINES[0]);
  const lineTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    // Only contracts that finished processing have embeddings to search against.
    get<ContractListResponse>("/api/contracts/?status=ready&page_size=100")
      .then((data) => {
        setContracts(data.items);
        if (data.items.length > 0) setContractId(data.items[0].id);
        setContractsLoading(false);
      })
      .catch((err) => {
        setContractsError(err instanceof ApiError ? err.message : "Couldn't load contracts.");
        setContractsLoading(false);
      });

    return () => {
      if (lineTimer.current) clearInterval(lineTimer.current);
    };
  }, []);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || !contractId || askState.kind === "loading") return;

    setAskedQuestion(trimmed);
    setAskState({ kind: "loading" });

    let i = 0;
    setLoadingLine(LOADING_LINES[0]);
    if (lineTimer.current) clearInterval(lineTimer.current);
    lineTimer.current = setInterval(() => {
      i = (i + 1) % LOADING_LINES.length;
      setLoadingLine(LOADING_LINES[i]);
    }, 900);

    post<AskResponse>(`/api/contracts/${contractId}/ask`, { question: trimmed })
      .then((res) => {
        setAskState({ kind: "answered", passages: res.passages, message: res.message });
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 409) {
          setAskState({ kind: "not-ready" });
        } else {
          setAskState({
            kind: "error",
            message: err instanceof ApiError ? err.message : "Something went wrong. Try again.",
          });
        }
      })
      .finally(() => {
        if (lineTimer.current) clearInterval(lineTimer.current);
      });
  }

  const selectedContract = contracts.find((c) => c.id === contractId);
  const canAsk = !contractsLoading && contracts.length > 0 && question.trim().length > 0 && askState.kind !== "loading";

  return (
    <div className="flex flex-col gap-6">
      <form
        onSubmit={handleSubmit}
        className="rounded-2xl border border-border bg-card p-6 shadow-sm"
      >
        <div className="grid gap-4 sm:grid-cols-[minmax(0,260px)_1fr]">
          <div>
            <label htmlFor="ask-contract" className="mb-1.5 block text-sm font-medium text-foreground">
              Contract
            </label>
            <div className="relative">
              <select
                id="ask-contract"
                value={contractId}
                onChange={(e) => {
                  setContractId(e.target.value);
                  setAskState({ kind: "idle" });
                }}
                disabled={contractsLoading || contracts.length === 0}
                className="w-full appearance-none rounded-lg border border-border bg-background py-2.5 pl-3 pr-9 text-sm text-foreground disabled:cursor-not-allowed disabled:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                {contractsLoading && <option value="">Loading contracts…</option>}
                {!contractsLoading && contracts.length === 0 && <option value="">No processed contracts yet</option>}
                {contracts.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
              <ChevronDown
                className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
                aria-hidden="true"
              />
            </div>
          </div>

          <div>
            <label htmlFor="ask-question" className="mb-1.5 block text-sm font-medium text-foreground">
              Your question
            </label>
            <div className="flex gap-2">
              <input
                id="ask-question"
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g. Can the client terminate for convenience?"
                disabled={contractsLoading || contracts.length === 0}
                className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
              <button
                type="submit"
                disabled={!canAsk}
                className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground transition-colors hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <Search className="h-4 w-4" aria-hidden="true" />
                Ask
              </button>
            </div>
          </div>
        </div>

        {contractsError && (
          <p className="mt-4 rounded-lg border border-danger-200 bg-danger-50 px-3 py-2 text-sm text-danger-700">
            {contractsError}
          </p>
        )}

        {!contractsLoading && !contractsError && contracts.length === 0 && (
          <p className="mt-4 text-sm text-muted-foreground">
            No contracts have finished processing yet.{" "}
            <Link href="/upload" className="font-medium text-primary hover:underline">
              Upload one
            </Link>{" "}
            to get started.
          </p>
        )}
      </form>

      {askState.kind === "loading" && (
        <div
          role="status"
          aria-live="polite"
          className="flex items-center gap-3 rounded-2xl border border-border bg-card px-6 py-8 text-sm text-muted-foreground"
        >
          <Loader2 className="h-5 w-5 animate-spin text-primary" aria-hidden="true" />
          {loadingLine}
        </div>
      )}

      {askState.kind === "not-ready" && (
        <div className="flex items-start gap-3 rounded-2xl border border-warning-200 bg-warning-50 px-6 py-5 text-sm text-warning-800">
          <Clock className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
          <p>
            <span className="font-semibold">{selectedContract?.name ?? "This contract"}</span> hasn&apos;t
            finished processing yet. Check back once analysis completes.
          </p>
        </div>
      )}

      {askState.kind === "error" && (
        <div className="rounded-2xl border border-danger-200 bg-danger-50 px-6 py-5 text-sm text-danger-700">
          {askState.message}
        </div>
      )}

      {askState.kind === "answered" && askState.passages.length > 0 && (
        <div>
          <p className="mb-3 text-sm text-muted-foreground">
            <span className="font-semibold text-foreground">{askState.passages.length}</span>{" "}
            matching {askState.passages.length === 1 ? "passage" : "passages"} in{" "}
            <span className="font-semibold text-foreground">{selectedContract?.name}</span> for
            &ldquo;{askedQuestion}&rdquo;
          </p>
          <ul className="flex flex-col gap-3">
            {askState.passages.map((p, i) => (
              <PassageResult key={p.chunk_id} passage={p} rank={i + 1} />
            ))}
          </ul>
        </div>
      )}

      {askState.kind === "answered" && askState.passages.length === 0 && (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-border bg-card px-6 py-12 text-center">
          <SearchX className="h-8 w-8 text-muted-foreground" aria-hidden="true" />
          <div>
            <p className="font-semibold text-foreground">No matching passages</p>
            <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">
              {askState.message ?? "Couldn't find any passages in this contract that closely match your question."}
            </p>
          </div>
        </div>
      )}

      {askState.kind === "idle" && !contractsLoading && contracts.length > 0 && (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-border px-6 py-12 text-center text-muted-foreground">
          <MessageCircleQuestion className="h-8 w-8" aria-hidden="true" />
          <p className="text-sm">Ask a question above to search this contract for the passages that answer it.</p>
        </div>
      )}
    </div>
  );
}
