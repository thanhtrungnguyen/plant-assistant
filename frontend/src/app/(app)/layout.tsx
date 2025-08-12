import { Nav } from "@/components/ui/nav";
import * as React from "react";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-dvh">
      <Nav />
      <div className="p-6">{children}</div>
    </div>
  );
}
