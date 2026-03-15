import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";

import { StoryComposer } from "./story-composer";

vi.mock("@/lib/api", () => ({
  apiRequest: vi.fn().mockResolvedValue({ id: "story-1", status: "pending" }),
  ApiError: class ApiError extends Error {},
}));

describe("StoryComposer", () => {
  it("adds a new character block", async () => {
    render(<StoryComposer onCreated={vi.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: /agregar personaje/i }));

    expect(screen.getAllByLabelText(/nombre/i)).toHaveLength(2);
  });
});
