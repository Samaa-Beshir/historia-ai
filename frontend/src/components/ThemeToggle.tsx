"use client";

import { useId, useState } from "react";
import { InlineScript } from "./InlineScript";

export function ThemeToggle() {
  const id = useId();

  // Lazy initializer: on the client this reads the class already applied by
  // the inline script in layout.tsx (before hydration), so it matches the
  // DOM without needing an effect. On the server `document` is undefined,
  // which is fine — that first paint is replaced during hydration.
  const [isDark, setIsDark] = useState(
    () => typeof document !== "undefined" && document.documentElement.classList.contains("dark")
  );

  const toggle = () => {
    const next = !isDark;
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("historia-theme", next ? "dark" : "light");
    setIsDark(next);
  };

  return (
    <>
      <button
        id={id}
        onClick={toggle}
        aria-label="Toggle theme"
        suppressHydrationWarning
        className="control-button"
      >
        {isDark ? "☼" : "☾"}
      </button>
      {/* Corrects the icon text in the DOM before hydration, matching the
          class the theme-init script already applied to <html>. Without
          this, SSR always renders the light-mode icon and hydration flags a
          mismatch when the client's actual theme is dark. */}
      <InlineScript
        html={`{var b=document.getElementById(${JSON.stringify(id)});if(b)b.textContent=document.documentElement.classList.contains("dark")?"☼":"☾"}`}
      />
    </>
  );
}
