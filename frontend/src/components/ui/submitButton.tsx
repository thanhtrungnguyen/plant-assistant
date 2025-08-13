import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useFormStatus } from "react-dom";

export function SubmitButton({ text, className }: { text: string; className?: string }) {
  const { pending } = useFormStatus();

  return (
    <Button className={cn("w-full", className)} type="submit" disabled={pending}>
      {pending ? "Loading..." : text}
    </Button>
  );
}
