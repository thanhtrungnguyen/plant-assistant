"use client";

import * as React from "react";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const [me, setMe] = React.useState<any>(null);

  React.useEffect(() => {
    api("/auth/me").then(async (r) => {
      if (r.ok) setMe(await r.json());
    });
  }, []);

  return (
    <div>
      <h1 className="text-xl font-semibold">Dashboard</h1>
      <pre className="mt-4 text-xs bg-muted p-4 rounded">{JSON.stringify(me, null, 2)}</pre>
    </div>
  );
}
