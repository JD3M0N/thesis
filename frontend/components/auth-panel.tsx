"use client";

import React, { FormEvent, useState } from "react";

import { ApiError, apiRequest } from "@/lib/api";
import { AuthResponse } from "@/lib/types";

type AuthPanelProps = {
  onAuthenticated: (response: AuthResponse) => void;
};

export function AuthPanel({ onAuthenticated }: AuthPanelProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await apiRequest<AuthResponse>(`/auth/${mode}`, {
        method: "POST",
        body: { email, password },
      });
      onAuthenticated(response);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "No se pudo autenticar";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-panel panel">
        <div className="brand">
          <div className="brand-mark">SW</div>
          <h1>Story Writers</h1>
          <p className="muted">
            Genera historias con un equipo de escritores IA en una experiencia limpia y directa.
          </p>
        </div>

        <div className="button-row">
          <button
            className={mode === "login" ? "primary-button" : "secondary-button"}
            onClick={() => setMode("login")}
            type="button"
          >
            Iniciar sesion
          </button>
          <button
            className={mode === "register" ? "primary-button" : "secondary-button"}
            onClick={() => setMode("register")}
            type="button"
          >
            Crear cuenta
          </button>
        </div>

        <form className="grid" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="email">Correo</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="tu@correo.com"
              required
            />
          </div>

          <div className="field">
            <label htmlFor="password">Contrasena</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Minimo 8 caracteres"
              minLength={8}
              required
            />
          </div>

          {error ? <p className="error-text">{error}</p> : null}

          <button className="primary-button" disabled={isSubmitting} type="submit">
            {isSubmitting
              ? "Procesando..."
              : mode === "login"
                ? "Entrar"
                : "Crear cuenta y entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
