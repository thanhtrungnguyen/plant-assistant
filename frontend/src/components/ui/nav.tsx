"use client";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { getCsrf } from "@/lib/csrf";
import Link from "next/link";
import { useRouter } from "next/navigation";

export function Nav() {
  const router = useRouter();

  async function onLogout() {
    await api("/auth/logout", {
      method: "POST",
      headers: { "x-csrf-token": getCsrf() || "" },
    });
    router.push("/login");
  }

  return (
    <header className="border-b">
      <div className="mx-auto flex max-w-5xl items-center justify-between p-4">
        <nav className="flex items-center gap-4 text-sm">
          <Link href="/">Dashboard</Link>
          <Link href="/settings/connections">Connections</Link>
        </nav>
        <Button variant="outline" onClick={onLogout}>
          Logout
        </Button>
      </div>
    </header>
  );
}
