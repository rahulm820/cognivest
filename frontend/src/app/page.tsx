import { redirect } from "next/navigation";

/** Root route redirects to the dashboard. */
export default function HomePage() {
  redirect("/dashboard");
}
