"use client";

import * as React from "react";

/**
 * Toggles `.reveal-visible` on elements carrying `.reveal` as they scroll into
 * view. One shared IntersectionObserver; CSS owns the actual transition. Purely
 * decorative — reduced-motion users get the end state immediately (see globals).
 */
export function useScrollReveal() {
  React.useEffect(() => {
    const els = Array.from(document.querySelectorAll<HTMLElement>(".reveal"));
    if (els.length === 0) return;

    if (!("IntersectionObserver" in window)) {
      els.forEach((el) => el.classList.add("reveal-visible"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("reveal-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -10% 0px" },
    );

    els.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);
}
