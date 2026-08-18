import { FileText, Sparkles, Layers } from "lucide-react";

const features = [
  {
    icon: FileText,
    title: "Text Extraction",
    description:
      "Every page of your PDF is extracted and processed, so it's ready to search and review.",
  },
  {
    icon: Sparkles,
    title: "Ask About Your Contract",
    description:
      "Ask questions about your contract and get answers pulled directly from its content.",
  },
    {
    icon: Layers,
    title: "Multiple Documents",
    description:
      "Drop in several PDF contracts at once — each one is uploaded and processed individually.",
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
