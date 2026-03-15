"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";

import { ApiError, apiRequest } from "@/lib/api";
import { formatDate } from "@/lib/format";
import { StoryDetail } from "@/lib/types";

type StoryDetailViewProps = {
  storyId: string;
};

export function StoryDetailView({ storyId }: StoryDetailViewProps) {
  const [story, setStory] = useState<StoryDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    async function loadStory() {
      try {
        const response = await apiRequest<StoryDetail>(`/stories/${storyId}`);
        if (isActive) {
          setStory(response);
        }
      } catch (err) {
        const message = err instanceof ApiError ? err.message : "No se pudo cargar la historia";
        if (isActive) {
          setError(message);
        }
      }
    }

    void loadStory();

    return () => {
      isActive = false;
    };
  }, [storyId]);

  if (error) {
    return (
      <div className="reader-layout">
        <div className="reader-panel panel">
          <Link className="ghost-button" href="/">
            Volver
          </Link>
          <p className="error-text">{error}</p>
        </div>
      </div>
    );
  }

  if (!story) {
    return (
      <div className="reader-layout">
        <div className="reader-panel panel">
          <p className="muted">Cargando historia...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="reader-layout">
      <div className="reader-panel panel">
        <div className="button-row">
          <Link className="ghost-button" href="/">
            Volver a la biblioteca
          </Link>
          <span className={`status-pill ${story.status}`}>{story.status}</span>
        </div>

        <div className="reader-title">
          <h1>{story.title ?? "Historia sin titulo"}</h1>
          <p className="muted">{story.summary ?? story.plot}</p>
        </div>

        <div className="reader-meta">
          <p>{formatDate(story.updated_at)}</p>
          <p>{story.style}</p>
          <p>{story.length}</p>
          <p>{story.language.toUpperCase()}</p>
        </div>

        {story.status === "completed" && story.story_text ? (
          <article className="reader-copy">{story.story_text}</article>
        ) : null}

        {story.status === "failed" ? (
          <p className="error-text">{story.error_message ?? "La historia fallo durante la generacion."}</p>
        ) : null}

        {story.status === "pending" || story.status === "running" ? (
          <p className="muted">
            El equipo de escritores sigue trabajando. Vuelve a esta pagina en unos segundos para leer el texto final.
          </p>
        ) : null}
      </div>
    </div>
  );
}
