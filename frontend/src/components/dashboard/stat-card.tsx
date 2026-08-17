import { type ReactNode } from "react";
import Card from "@/components/Card";

interface StatCardProps {
  icon: ReactNode;
  label: string;
  value: number;
}

export function StatCard({ icon, label, value }: StatCardProps) {
  return (
    <Card padding="lg" className="flex items-center gap-4">
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-primary-50 text-primary-600">
        {icon}
      </div>
      <div>
        <p className="text-2xl font-semibold text-neutral-900">{value}</p>
        <p className="text-sm text-neutral-500">{label}</p>
      </div>
    </Card>
  );
}