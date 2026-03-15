import "@testing-library/jest-dom/vitest";
import React from "react";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

afterEach(() => {
  cleanup();
});

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string | URL;
  }) =>
    React.createElement(
      "a",
      {
        ...props,
        href: typeof href === "string" ? href : href.toString(),
      },
      children,
    ),
}));
