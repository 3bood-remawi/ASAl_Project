import { Lightbulb } from "lucide-react";
import { AppSidebar } from "@/components/sidebar/app-sidebar";
import { TopNav } from "@/components/navbar/top-nav";
import { UploadPanel } from "@/components/contract/upload-panel";
import { FeatureCards } from "@/components/contract/feature-cards";
import { APP_NAME } from "@/lib/site-config";

export default function UploadPage() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <AppSidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <TopNav />

        <main className="flex-1 overflow-y-auto bg-[linear-gradient(180deg,rgba(244,247,252,0.96),rgba(255,255,255,0.96))]">
          <div className="mx-auto w-full max-w-3xl px-6 py-8">
            <header className="rounded-3xl border border-primary/10 bg-gradient-to-r from-primary/5 to-accent px-6 py-8 text-center shadow-sm">
              <h1 className="text-3xl font-bold tracking-tight text-brand text-balance">
                Upload Documents
              </h1>
              <p className="mx-auto mt-2 max-w-xl text-sm leading-relaxed text-muted-foreground text-pretty">
                {APP_NAME} processes PDF legal documents with advanced
                semantic recognition.
              </p>
            </header>

            <div className="mt-8 flex flex-col gap-10">
              <UploadPanel />
              <FeatureCards />
            </div>
          </div>

          <div className="mt-4 flex items-center justify-center gap-2 bg-brand px-6 py-3.5 text-center text-xs font-medium text-brand-foreground">
            <Lightbulb className="h-4 w-4" aria-hidden="true" />
            <span>
              Pro Tip: Use the &apos;Legal Folders&apos; integration to sync
              directly from OneDrive or SharePoint.
            </span>
          </div>
        </main>
      </div>
    </div>
  );
}
