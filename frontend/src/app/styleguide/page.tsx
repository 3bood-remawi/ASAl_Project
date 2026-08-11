"use client";

import { useState } from "react";
import { colors, radius } from "@/theme/tokens";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Select from "@/components/Select";
import Card from "@/components/Card";
import Modal from "@/components/Modal";
import { useToast } from "@/components/ToastProvider";
import Spinner from "@/components/Spinner";
import Skeleton from "@/components/Skeleton";
import EmptyState from "@/components/EmptyState";

export default function StyleguidePage() {
  const colorGroups = Object.entries(colors) as [string, Record<string, string>][];
  const [modalOpen, setModalOpen] = useState(false);
  const toast = useToast();

  return (
    <main className="p-8 max-w-5xl mx-auto flex flex-col gap-12">
      <div>
        <h1 className="text-3xl font-sans text-neutral-900">Style Guide</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Design tokens and shared components — task 847
        </p>
      </div>

      <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Colors</h2>
        <div className="flex flex-col gap-6">
          {colorGroups.map(([groupName, shades]) => (
            <div key={groupName}>
              <p className="text-sm font-medium text-neutral-700 mb-2 capitalize">
                {groupName}
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(shades).map(([shade, hex]) => (
                  <div key={shade} className="flex flex-col items-center">
                    <div
                      className="h-12 w-12 rounded-md border border-neutral-200"
                      style={{ backgroundColor: hex }}
                    />
                    <span className="text-xs text-neutral-500 mt-1">{shade}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Type Scale</h2>
        <div className="flex flex-col gap-3">
            <p className="text-xs">The quick brown fox (text-xs)</p>
            <p className="text-sm">The quick brown fox (text-sm)</p>
            <p className="text-base">The quick brown fox (text-base)</p>
            <p className="text-lg">The quick brown fox (text-lg)</p>
            <p className="text-xl">The quick brown fox (text-xl)</p>
            <p className="text-2xl">The quick brown fox (text-2xl)</p>
            <p className="text-3xl">The quick brown fox (text-3xl)</p>
        </div>
       </section>

       <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Border Radius</h2>
        <div className="flex flex-wrap gap-4">
            {Object.entries(radius).map(([name, value]) => (
            <div key={name} className="flex flex-col items-center gap-1">
                <div
                className="h-16 w-16 bg-primary-100 border border-primary-300"
                style={{ borderRadius: value }}
                />
                <span className="text-xs text-neutral-500">{name}</span>
            </div>
            ))}
        </div>
       </section>

       <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Button</h2>

        <p className="text-sm font-medium text-neutral-700 mb-2">Variants</p>
        <div className="flex flex-wrap gap-3 mb-6">
            <Button variant="primary">Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="danger">Danger</Button>
        </div>

        <p className="text-sm font-medium text-neutral-700 mb-2">Sizes</p>
        <div className="flex flex-wrap items-center gap-3 mb-6">
            <Button size="sm">Small</Button>
            <Button size="md">Medium</Button>
            <Button size="lg">Large</Button>
        </div>

        <p className="text-sm font-medium text-neutral-700 mb-2">Loading state</p>
        <div className="flex flex-wrap gap-3 mb-6">
            <Button isLoading>Primary</Button>
            <Button variant="secondary" isLoading>Secondary</Button>
            <Button variant="danger" isLoading>Danger</Button>
        </div>

        <p className="text-sm font-medium text-neutral-700 mb-2">Disabled</p>
        <div className="flex flex-wrap gap-3">
            <Button disabled>Disabled</Button>
            <Button variant="secondary" disabled>Disabled</Button>
        </div>
       </section>

       <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Input</h2>
        <div className="flex flex-col gap-4 max-w-sm">
            <Input label="Default" placeholder="you@company.com" />
            <Input
            label="With helper text"
            placeholder="you@company.com"
            helperText="We'll never share your email"
            />
            <Input
            label="Error state"
            placeholder="you@company.com"
            error="Please enter a valid email"
            />
            <Input label="Disabled" placeholder="you@company.com" disabled />
        </div>
       </section>

       <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Select</h2>
        <div className="flex flex-col gap-4 max-w-sm">
            <Select
            label="Default"
            placeholder="Select a type"
            options={[
                { label: "Vendor Agreement", value: "vendor" },
                { label: "NDA", value: "nda" },
                { label: "Lease", value: "lease" },
            ]}
            />
            <Select
            label="Error state"
            placeholder="Select a type"
            error="Please select a contract type"
            options={[
                { label: "Vendor Agreement", value: "vendor" },
                { label: "NDA", value: "nda" },
            ]}
            />
        </div>
       </section>

       <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Card</h2>
        <div className="flex flex-wrap gap-4">
            <Card padding="sm">
            <p className="text-sm text-neutral-600">Small padding</p>
            </Card>
            <Card padding="md">
            <p className="text-sm text-neutral-600">Medium padding (default)</p>
            </Card>
            <Card padding="lg">
            <p className="text-sm text-neutral-600">Large padding</p>
            </Card>
        </div>
       </section>

       <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Modal</h2>
        <Button onClick={() => setModalOpen(true)}>Open Modal</Button>
        <Modal
            isOpen={modalOpen}
            onClose={() => setModalOpen(false)}
            title="Example Modal"
        >
            <p className="text-sm text-neutral-600 mb-4">
            This is an example modal — closes on Escape, backdrop click, traps
            focus, and returns focus on close.
            </p>
            <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>
                Cancel
            </Button>
            <Button onClick={() => setModalOpen(false)}>Confirm</Button>
            </div>
        </Modal>
       </section>

       <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Toast</h2>
        <div className="flex flex-wrap gap-3">
            <Button onClick={() => toast.success("Contract uploaded successfully!")}>
            Trigger Success Toast
            </Button>
            <Button variant="danger" onClick={() => toast.error("Something went wrong.")}>
            Trigger Error Toast
            </Button>
        </div>
       </section>

       <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Spinner</h2>
        <div className="flex items-center gap-4 text-primary-600">
            <Spinner size="sm" />
            <Spinner size="md" />
            <Spinner size="lg" />
        </div>
       </section>

       <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Skeleton</h2>
        <div className="flex flex-col gap-3 max-w-sm">
            <Skeleton variant="rectangle" />
            <Skeleton variant="text" />
            <Skeleton variant="text" className="w-2/3" />
            <div className="flex items-center gap-2">
            <Skeleton variant="circle" />
            <Skeleton variant="text" className="w-1/3" />
            </div>
        </div>
       </section>

       <section>
        <h2 className="text-xl font-sans text-neutral-900 mb-4">Empty State</h2>
        <Card>
            <EmptyState
            title="No contracts yet"
            description="Upload your first contract to get started with AI-powered analysis."
            actionLabel="Upload contract"
            onAction={() => toast.success("Upload clicked")}
            />
        </Card>
       </section>
    </main>
  );
}