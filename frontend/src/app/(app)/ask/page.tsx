import { AskPanel } from "@/components/ask/ask-panel";
import { APP_NAME } from "@/lib/site-config";

export default function AskPage() {
  return (
    <div className="mx-auto w-full max-w-4xl px-6 py-8">
      <header className="rounded-3xl border border-primary/10 bg-gradient-to-r from-primary/5 to-accent px-6 py-8 text-center shadow-sm">
        <h1 className="text-3xl font-bold tracking-tight text-brand text-balance">
          Ask your contracts
        </h1>
        <p className="mx-auto mt-2 max-w-xl text-sm leading-relaxed text-muted-foreground text-pretty">
          Pick a contract and ask {APP_NAME} a question in plain language — it
          searches the document and returns the passages that answer it.
        </p>
      </header>

      <div className="mt-8">
        <AskPanel />
      </div>
    </div>
  );
}
