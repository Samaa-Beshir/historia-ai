// See docs/preventing-flash-before-hydration.md: React warns when JSX renders a
// plain <script>. Flipping `type` avoids the warning; suppressHydrationWarning
// avoids a mismatch on that same type flip between server and client.
export function InlineScript({ html }: { html: string }) {
  return (
    <script
      type={typeof window === "undefined" ? "text/javascript" : "text/plain"}
      suppressHydrationWarning
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
