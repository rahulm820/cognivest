import { Button, Card, CardContent, CardHeader, CardTitle, Input } from "@/components/ui";

/**
 * Login screen stub (ARCHITECTURE.md §9 — JWT auth).
 * TODO(phase-1): wire to auth.login(), persist tokens, redirect to /dashboard.
 */
export default function LoginPage() {
  return (
    <div className="mx-auto flex max-w-sm items-center justify-center py-16">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Sign in to Cognivest</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input type="email" placeholder="Email" aria-label="Email" />
          <Input type="password" placeholder="Password" aria-label="Password" />
          <Button className="w-full" disabled>
            Sign in (TODO phase-1)
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
