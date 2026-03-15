import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { StoryComposer } from "./story-composer";
import { apiRequest, ApiError } from "@/lib/api";

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    apiRequest: vi.fn(),
  };
});

const apiRequestMock = vi.mocked(apiRequest);

describe("StoryComposer", () => {
  afterEach(() => {
    apiRequestMock.mockReset();
  });

  it("adds and removes character blocks", () => {
    render(<StoryComposer onCreated={vi.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: /agregar personaje/i }));
    expect(screen.getAllByLabelText(/nombre/i)).toHaveLength(2);

    fireEvent.click(screen.getAllByRole("button", { name: /eliminar personaje/i })[0]);
    expect(screen.getAllByLabelText(/nombre/i)).toHaveLength(1);
  });

  it("submits the story payload and notifies creation", async () => {
    apiRequestMock.mockResolvedValue({ id: "story-1", status: "pending" });
    const onCreated = vi.fn();

    render(<StoryComposer onCreated={onCreated} />);

    fireEvent.change(screen.getByLabelText(/nombre/i), {
      target: { value: "Ayla" },
    });
    fireEvent.change(screen.getByLabelText(/rol/i), {
      target: { value: "aprendiz" },
    });
    fireEvent.change(screen.getByLabelText(/descripcion/i), {
      target: { value: "Teme perder sus recuerdos" },
    });
    fireEvent.change(screen.getByLabelText(/^estilo/i), {
      target: { value: "Fantasia melancolica" },
    });
    fireEvent.change(screen.getByLabelText(/trama/i), {
      target: {
        value: "Una aprendiz descubre un reloj que rompe el tiempo y debe elegir entre la ciudad y su memoria.",
      },
    });
    fireEvent.click(screen.getByRole("button", { name: /generar historia/i }));

    await waitFor(() =>
      expect(apiRequestMock).toHaveBeenCalledWith("/stories/generate", {
        method: "POST",
        body: {
          characters: [
            {
              name: "Ayla",
              role: "aprendiz",
              description: "Teme perder sus recuerdos",
            },
          ],
          style: "Fantasia melancolica",
          plot: "Una aprendiz descubre un reloj que rompe el tiempo y debe elegir entre la ciudad y su memoria.",
          length: "medium",
          language: "es",
        },
      }),
    );
    expect(onCreated).toHaveBeenCalledWith({ id: "story-1", status: "pending" });
    expect(screen.getByLabelText(/trama/i)).toHaveValue("");
  });

  it("shows a pending state while submitting and renders API errors", async () => {
    let rejectRequest: ((error: unknown) => void) | undefined;
    apiRequestMock.mockImplementation(
      () =>
        new Promise((_, reject) => {
          rejectRequest = reject;
        }),
    );

    render(<StoryComposer onCreated={vi.fn()} />);

    fireEvent.change(screen.getByLabelText(/nombre/i), {
      target: { value: "Ayla" },
    });
    fireEvent.change(screen.getByLabelText(/rol/i), {
      target: { value: "aprendiz" },
    });
    fireEvent.change(screen.getByLabelText(/descripcion/i), {
      target: { value: "Teme perder sus recuerdos" },
    });
    fireEvent.change(screen.getByLabelText(/trama/i), {
      target: {
        value: "Una aprendiz descubre un reloj que rompe el tiempo y debe elegir entre la ciudad y su memoria.",
      },
    });
    fireEvent.click(screen.getByRole("button", { name: /generar historia/i }));

    expect(screen.getByRole("button", { name: /encolando historia/i })).toBeDisabled();

    rejectRequest?.(new ApiError("No se pudo generar", 500));

    expect(await screen.findByText("No se pudo generar")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generar historia/i })).not.toBeDisabled();
  });
});
