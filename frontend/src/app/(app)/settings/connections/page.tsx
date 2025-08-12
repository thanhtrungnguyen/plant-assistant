"use client";

import { Button } from "@/components/ui/button";

const API = process.env.NEXT_PUBLIC_API_URL!;

export default function ConnectionsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Connections</h1>
      <p className="text-sm text-muted-foreground">Link external providers to your account.</p>
      <a href={`${API}/auth/login/google?mode=link`}>
        <Button>Link Google</Button>
      </a>
    </div>
  );
}
