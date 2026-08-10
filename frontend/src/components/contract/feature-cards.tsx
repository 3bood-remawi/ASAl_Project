import { ShieldCheck, Sparkles, Layers } from "lucide-react";

const features = [
  {
    icon: ShieldCheck,
    title: "Secure Encryption",
    description:
      "All documents are encrypted with AES-256 and never used for public training.",
  },
  {
    icon: Sparkles,
    title: "Auto-Classification",
    description:
      "Our AI automatically detects contract types and relevant jurisdictional law.",
  },
  {
    icon: Layers,
    title: "Batch Processing",
    description:
      "Upload up to 50 documents at once for large-scale litigation review.",
  },
];

export function FeatureCards() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {features.map(({ icon: Icon, title, description }) => (
        <div
          key={title}
          className="rounded-xl border border-border bg-gradient-to-br from-white to-blue-50/40 p-5 shadow-sm transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-md"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent">
            <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
          </div>
          <h3 className="mt-3 text-sm font-semibold text-foreground">
            {title}
          </h3>
          <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
            {description}
          </p>
        </div>
      ))}
    </div>
  );
}
