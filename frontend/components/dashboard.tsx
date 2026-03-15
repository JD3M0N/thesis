"use client";

import React, { useEffect, useState } from "react";

import { apiRequest } from "@/lib/api";
import { AuthResponse, StoryJobCreated, StoryListItem, User } from "@/lib/types";
import { AuthPanel } from "./auth-panel";
import { StoryComposer } from "./story-composer";
import { StoryHighlights } from "./story-highlights";
import { StoryLibrary } from "./story-library";

async function fetchStories() {
  return apiRequest<StoryListItem[]>("/stories");
}

export function Dashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [stories, setStories] = useState<StoryListItem[]>([]);

  useEffect(() => {
    let isActive = true;

    async function bootstrap() {
      try {
        const auth = await apiRequest<AuthResponse>("/auth/me");
        if (!isActive) {
          return;
        }
        setUser(auth.user);
        const nextStories = await fetchStories();
        if (isActive) {
          setStories(nextStories);
        }
      } catch {
        if (isActive) {
          setUser(null);
          setStories([]);
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    void bootstrap();

    return () => {
      isActive = false;
    };
  }, []);

  useEffect(() => {
    if (!user) {
      return;
    }

    const hasActiveStories = stories.some((story) => story.status === "pending" || story.status === "running");
    if (!hasActiveStories) {
      return;
    }

    const interval = window.setInterval(() => {
      void fetchStories().then(setStories).catch(() => undefined);
    }, 3000);

    return () => window.clearInterval(interval);
  }, [stories, user]);

  async function handleAuthenticated(response: AuthResponse) {
    setUser(response.user);
    const nextStories = await fetchStories();
    setStories(nextStories);
  }

  async function handleLogout() {
    await apiRequest<void>("/auth/logout", { method: "POST" });
    setUser(null);
    setStories([]);
  }

  async function handleStoryCreated(_: StoryJobCreated) {
    const nextStories = await fetchStories();
    setStories(nextStories);
  }

  if (isLoading) {
    return (
      <div className="auth-shell">
        <div className="auth-panel panel">
          <h1>Story Writers</h1>
          <p className="muted">Cargando espacio de trabajo...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <AuthPanel onAuthenticated={handleAuthenticated} />;
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">SW</div>
          <h1>Story Writers</h1>
          <p className="muted tiny">Tu sala de escritores multiagente.</p>
        </div>

        <div className="grid">
          <div>
            <h2>{user.email}</h2>
            <p className="muted tiny">Sesión local activa</p>
          </div>
          <button className="ghost-button" onClick={handleLogout} type="button">
            Cerrar sesion
          </button>
        </div>

        <div className="grid">
          <div className="section-title">
            <h2>Biblioteca</h2>
            <span className="muted tiny">{stories.length}</span>
          </div>
          <StoryLibrary stories={stories} />
        </div>
      </aside>

      <main className="content">
        <header className="content-header">
          <div className="hero">
            <h1>Historias con un equipo de escritores IA</h1>
            <p className="muted">
              Define personajes, estilo y trama. El sistema encadena cinco agentes y guarda cada historia
              para que la leas cuando termine.
            </p>
          </div>
        </header>

        <StoryComposer onCreated={handleStoryCreated} />

        <section className="grid">
          <div className="section-title">
            <div>
              <h2>Recientes</h2>
              <p className="muted">Consulta el estado de los encargos y abre cualquier historia terminada.</p>
            </div>
          </div>
          <StoryHighlights stories={stories} />
        </section>
      </main>
    </div>
  );
}
