import React from "react";
import { render, screen } from "@testing-library/react";

import { StoryDetailView } from "./story-detail-view";
import { apiRequest, ApiError } from "@/lib/api";
import { StoryDetail } from "@/lib/types";

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    apiRequest: vi.fn(),
  };
});

const apiRequestMock = vi.mocked(apiRequest);

function buildStory(status: StoryDetail["status"]): StoryDetail {
  return {
    id: "story-1",
    title: "Historia",
    summary: "Resumen",
    style: "Fantasia",
    plot: "Trama",
    length: "medium",
    language: "es",
    status,
    story_text: status === "completed" ? "Texto final" : null,
    error_message: status === "failed" ? "Fallo controlado" : null,
    created_at: "2026-03-15T10:00:00Z",
    updated_at: "2026-03-15T10:05:00Z",
  };
}

describe("StoryDetailView", () => {
  afterEach(() => {
    apiRequestMock.mockReset();
  });

  it("shows a loading state before the request resolves", () => {
    apiRequestMock.mockImplementation(() => new Promise(() => undefined));

    render(<StoryDetailView storyId="story-1" />);

    expect(screen.getByText(/cargando historia/i)).toBeInTheDocument();
  });

  it("renders completed stories", async () => {
    apiRequestMock.mockResolvedValue(buildStory("completed"));

    render(<StoryDetailView storyId="story-1" />);

    expect(await screen.findByText("Texto final")).toBeInTheDocument();
    expect(screen.getByText("completed")).toBeInTheDocument();
  });

  it("renders failed stories", async () => {
    apiRequestMock.mockResolvedValue(buildStory("failed"));

    render(<StoryDetailView storyId="story-1" />);

    expect(await screen.findByText("Fallo controlado")).toBeInTheDocument();
  });

  it("renders pending stories", async () => {
    apiRequestMock.mockResolvedValue(buildStory("pending"));

    render(<StoryDetailView storyId="story-1" />);

    expect(await screen.findByText(/sigue trabajando/i)).toBeInTheDocument();
  });

  it("renders API errors", async () => {
    apiRequestMock.mockRejectedValue(new ApiError("Story not found", 404));

    render(<StoryDetailView storyId="story-1" />);

    expect(await screen.findByText("Story not found")).toBeInTheDocument();
  });
});
