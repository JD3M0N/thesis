from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


ARCHITECT_PROMPT = "The Architect"
WORLD_BUILDER_PROMPT = "The World Builder"
DRAMA_COACH_PROMPT = "The Drama Coach"
DEPENDENCY_MANAGER_PROMPT = "The Dependency Manager"
NARRATOR_PROMPT = "The Narrator"

DEFAULT_STORY_REQUEST: dict[str, Any] = {
    "characters": [
        {
            "name": "Ayla",
            "role": "aprendiz",
            "description": "Joven disciplinada que teme perder sus recuerdos",
        }
    ],
    "style": "fantasia melancolica",
    "plot": "Una aprendiz descubre un reloj que rompe el tiempo y debe elegir entre la ciudad y su memoria.",
    "length": "medium",
    "language": "es",
}

DEFAULT_AGENT_PAYLOADS: dict[str, dict[str, Any]] = {
    ARCHITECT_PROMPT: {
        "premise": "Una aprendiz encuentra un reloj que abre grietas temporales.",
        "beats": [
            {
                "title": "La llamada",
                "purpose": "Introducir el artefacto y la mision",
                "stakes": "El tiempo local empieza a deshacerse",
            }
        ],
        "climax": "La protagonista decide romper el reloj para salvar a su mentora.",
        "resolution": "La ciudad sobrevive pero ella pierde el ultimo recuerdo de su padre.",
    },
    WORLD_BUILDER_PROMPT: {
        "characters": [
            {
                "name": "Ayla",
                "role": "aprendiz",
                "description": "Joven precisa y obsesionada con el orden",
                "desire": "Salvar la ciudad",
                "fear": "Repetir el fracaso de su padre",
            }
        ],
        "locations": [
            {
                "name": "Archivo del Reloj",
                "description": "Una torre silenciosa con mecanismos y polvo brillante",
                "mood": "solemne",
            }
        ],
        "objects": [
            {"name": "Reloj umbral", "significance": "Abre fisuras entre momentos cercanos"}
        ],
        "rules": ["Cada uso del reloj borra un recuerdo humano."],
    },
    DRAMA_COACH_PROMPT: {
        "revised_beats": [
            {
                "title": "Traicion del mentor",
                "purpose": "Subir el conflicto emocional",
                "stakes": "Ayla duda de su mision",
            }
        ],
        "tension_notes": ["La mentora intenta quedarse con el reloj."],
        "character_arc_notes": ["Ayla aprende a aceptar la perdida."],
    },
    DEPENDENCY_MANAGER_PROMPT: {
        "is_consistent": True,
        "issues": [],
        "fixes_applied": ["Se mantiene la regla de perdida de memoria."],
        "narrator_guidance": ["Mantener tono melancolico y preciso."],
    },
    NARRATOR_PROMPT: {
        "title": "El reloj de la torre muda",
        "summary": "Ayla intenta salvar su ciudad mientras cada uso del reloj le cuesta un recuerdo.",
        "story_text": "Ayla subio la torre al anochecer y descubrio que el tiempo tambien podia sangrar.",
    },
}

INCONSISTENT_DEPENDENCY_PAYLOAD: dict[str, Any] = {
    "is_consistent": False,
    "issues": ["El objeto crucial desaparece antes del climax."],
    "fixes_applied": [],
    "narrator_guidance": ["No narrar hasta resolver la contradiccion."],
}


class FakeGeminiClient:
    def __init__(
        self,
        *,
        fail_on: str | None = None,
        inconsistent_dependency: bool = False,
        invalid_payload_for: str | None = None,
        custom_payloads: Mapping[str, dict[str, Any]] | None = None,
    ) -> None:
        self.fail_on = fail_on
        self.inconsistent_dependency = inconsistent_dependency
        self.invalid_payload_for = invalid_payload_for
        self.custom_payloads = dict(custom_payloads or {})

    async def generate_json(self, prompt: str) -> dict[str, Any]:
        if self.fail_on and self.fail_on in prompt:
            raise RuntimeError("Synthetic agent failure")

        for marker, default_payload in DEFAULT_AGENT_PAYLOADS.items():
            if marker not in prompt:
                continue

            if self.invalid_payload_for == marker:
                return {"unexpected": "shape"}

            if marker == DEPENDENCY_MANAGER_PROMPT and self.inconsistent_dependency:
                return deepcopy(INCONSISTENT_DEPENDENCY_PAYLOAD)

            payload = self.custom_payloads.get(marker, default_payload)
            return deepcopy(payload)

        raise AssertionError("Prompt desconocido")


def build_story_request(**overrides: Any) -> dict[str, Any]:
    payload = deepcopy(DEFAULT_STORY_REQUEST)
    payload.update(overrides)
    return payload
