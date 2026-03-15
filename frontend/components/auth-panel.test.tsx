import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { AuthPanel } from "./auth-panel";
import { apiRequest, ApiError } from "@/lib/api";

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    apiRequest: vi.fn(),
  };
});

const apiRequestMock = vi.mocked(apiRequest);

describe("AuthPanel", () => {
  afterEach(() => {
    apiRequestMock.mockReset();
  });

  it("submits login by default", async () => {
    apiRequestMock.mockResolvedValue({
      user: { id: "user-1", email: "writer@example.com" },
    });
    const onAuthenticated = vi.fn();

    render(<AuthPanel onAuthenticated={onAuthenticated} />);

    fireEvent.change(screen.getByLabelText(/correo/i), {
      target: { value: "writer@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/contrasena/i), {
      target: { value: "supersecure123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));

    await waitFor(() =>
      expect(apiRequestMock).toHaveBeenCalledWith("/auth/login", {
        method: "POST",
        body: { email: "writer@example.com", password: "supersecure123" },
      }),
    );
    expect(onAuthenticated).toHaveBeenCalledWith({
      user: { id: "user-1", email: "writer@example.com" },
    });
  });

  it("switches to register mode and submits the correct endpoint", async () => {
    apiRequestMock.mockResolvedValue({
      user: { id: "user-2", email: "new@example.com" },
    });

    render(<AuthPanel onAuthenticated={vi.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));
    fireEvent.change(screen.getByLabelText(/correo/i), {
      target: { value: "new@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/contrasena/i), {
      target: { value: "supersecure123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /crear cuenta y entrar/i }));

    await waitFor(() =>
      expect(apiRequestMock).toHaveBeenCalledWith("/auth/register", {
        method: "POST",
        body: { email: "new@example.com", password: "supersecure123" },
      }),
    );
  });

  it("renders API errors", async () => {
    apiRequestMock.mockRejectedValue(new ApiError("Invalid credentials", 401));

    render(<AuthPanel onAuthenticated={vi.fn()} />);

    fireEvent.change(screen.getByLabelText(/correo/i), {
      target: { value: "writer@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/contrasena/i), {
      target: { value: "wrongpass123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByText("Invalid credentials")).toBeInTheDocument();
  });
});
