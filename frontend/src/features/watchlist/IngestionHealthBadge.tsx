import type { Company } from "@/types";
import { Badge, type BadgeProps } from "@/components/ui";

const STATUS_VARIANT: Record<Company["status"], BadgeProps["variant"]> = {
  active: "success",
  backfilling: "secondary",
  error: "destructive",
};

/** Badge showing per-company ingestion health. */
export function IngestionHealthBadge({ status }: { status: Company["status"] }) {
  return <Badge variant={STATUS_VARIANT[status]}>{status}</Badge>;
}
