import math
import re

import pytest
from asg_top_down.schemas import (
    ID_PATTERN,
    NarrativeBlueprint,
    RoleSuggestion,
    SemanticSkeletonRanking,
    SemanticSkeletonScore,
    SkeletonMatch,
    StoryRequest,
)
from asg_top_down.skeleton_match import (
    FALLBACK_SHORTLIST,
    LEXICAL_WEIGHT,
    SEMANTIC_WEIGHT,
    lexical_scores,
    normalize,
    rank_skeletons,
    skeleton_query,
)
from asg_top_down.skeletons import (
    PLOT_SKELETONS,
    SKELETONS_BY_ID,
    FunctionalRole,
    Layer,
    blueprint_guidance,
    find_skeleton,
    skeletons_for_layer,
)
from pydantic import ValidationError


def make_request() -> StoryRequest:
    return StoryRequest(
        original_prompt="Escribe una historia sobre un robo en un museo vigilado",
        processed_prompt="Write a story about a theft in a guarded museum.",
        title="The Price of Truth",
        language="Spanish",
        genre="drama",
        tone="tense",
        narrative_profile="essential",
        premise="A thief steals a relic from a guarded museum to save his sister.",
        constraints=[],
        creative_directions=[],
    )


class RankingProvider:
    """Return one fixed semantic ranking, or raise, without touching the network."""

    def __init__(self, scores=None, *, fail=False) -> None:
        self.scores = scores or {}
        self.fail = fail
        self.calls = 0

    def generate_structured(self, *, system_instruction, prompt, schema, profile):
        self.calls += 1
        if self.fail:
            raise RuntimeError("semantic ranking unavailable")
        return SemanticSkeletonRanking(
            scores=[
                SemanticSkeletonScore(skeleton_id=key, relevance=value)
                for key, value in self.scores.items()
            ]
        )


def test_catalog_covers_both_layers_with_unique_valid_ids() -> None:
    assert len(PLOT_SKELETONS) >= 20
    ids = [item.id for item in PLOT_SKELETONS]
    assert len(set(ids)) == len(ids)
    for item in PLOT_SKELETONS:
        assert re.fullmatch(ID_PATTERN, item.id), item.id
    subplot_only = [item for item in PLOT_SKELETONS if item.layers == (Layer.SUBPLOT,)]
    assert len(subplot_only) >= 6
    assert len(skeletons_for_layer(Layer.MACROPLOT)) >= 20


def test_cross_references_and_roles_resolve() -> None:
    valid_roles = {role.value for role in FunctionalRole}
    for item in PLOT_SKELETONS:
        assert {role.value for role in item.typical_functional_roles} <= valid_roles
        for reference in (*item.pairs_well_with, *item.tensions_with):
            assert reference in SKELETONS_BY_ID
            assert reference != item.id
    for reference in FALLBACK_SHORTLIST:
        assert reference in SKELETONS_BY_ID


def test_catalog_entry_hides_thesis_only_attribution() -> None:
    entry = find_skeleton("heist").catalog_entry()
    assert "influences" not in entry
    assert entry["id"] == "heist"


def test_lexical_scoring_is_deterministic_and_ranks_the_obvious_shape() -> None:
    query = "A thief must steal a relic from a guarded museum to save his sister"
    first = lexical_scores(query)
    second = lexical_scores(query)
    assert [(row.skeleton_id, row.score) for row in first] == [
        (row.skeleton_id, row.score) for row in second
    ]
    ranked = rank_skeletons(query, limit=5)
    assert ranked[0].skeleton_id == "heist"
    assert "rescue" in {row.skeleton_id for row in ranked}


def test_accented_spanish_query_still_tokenizes() -> None:
    assert normalize("Una traición en la prisión") == "una traicion en la prision"
    ranked = rank_skeletons("Un preso planea su huida de la prision", limit=3)
    assert ranked


def test_empty_query_returns_the_varied_fallback_shortlist() -> None:
    ranked = rank_skeletons("", limit=8)
    assert [row.skeleton_id for row in ranked] == list(FALLBACK_SHORTLIST[:8])
    assert all(row.semantic_score is None for row in ranked)


def test_missing_provider_degrades_to_lexical_only() -> None:
    ranked = rank_skeletons("a detective investigates a murder", provider=None)
    assert ranked
    assert all(row.semantic_score is None for row in ranked)


def test_failing_semantic_call_degrades_without_raising() -> None:
    provider = RankingProvider(fail=True)
    ranked = rank_skeletons("a detective investigates a murder", provider=provider)
    assert provider.calls == 1
    assert ranked
    assert all(row.semantic_score is None for row in ranked)


def test_semantic_blend_uses_the_declared_weights() -> None:
    query = "A thief must steal a relic from a guarded museum"
    lexical = {row.skeleton_id: row.lexical_score for row in lexical_scores(query)}
    provider = RankingProvider({"mystery": 1.0})
    ranked = rank_skeletons(query, provider=provider, limit=len(PLOT_SKELETONS))
    scored = {row.skeleton_id: row for row in ranked}
    mystery = scored["mystery"]
    assert mystery.semantic_score == 1.0
    expected = LEXICAL_WEIGHT * lexical["mystery"] + SEMANTIC_WEIGHT * 1.0
    assert math.isclose(mystery.score, expected, rel_tol=1e-9)
    heist = scored["heist"]
    assert heist.semantic_score == 0.0
    assert math.isclose(heist.score, LEXICAL_WEIGHT * lexical["heist"], rel_tol=1e-9)


def test_unknown_semantic_ids_are_ignored_rather_than_raising() -> None:
    provider = RankingProvider({"not_a_skeleton": 1.0})
    ranked = rank_skeletons("a betrayal among thieves", provider=provider)
    assert ranked
    assert all(row.semantic_score is None for row in ranked)


def test_skeleton_query_leads_with_processed_prompt_and_skips_the_original() -> None:
    request = make_request()
    query = skeleton_query(request)
    assert request.processed_prompt in query
    assert request.premise in query
    assert request.original_prompt not in query


def test_spanish_request_fields_still_rank_from_the_english_brief() -> None:
    """The analyst leaves premise, genre and tone in Spanish for Spanish stories."""
    request = StoryRequest(
        original_prompt="Escribe un relato sobre una fuga de una prision en una isla",
        processed_prompt=(
            "A political prisoner studies the guard rotation for months to escape a prison "
            "on an island, and discovers his only route out condemns his cellmate."
        ),
        title="La Marea de Piedra",
        language="Spanish",
        genre="Suspense / Drama Carcelario",
        tone="tenso y sobrio",
        narrative_profile="essential",
        premise="Un preso politico planea su fuga de una prision en una isla.",
        constraints=[],
        creative_directions=[],
    )
    ranked = rank_skeletons(skeleton_query(request), limit=3)
    assert ranked[0].skeleton_id == "escape"
    assert ranked[0].lexical_score > 0.5


def blueprint(**overrides) -> NarrativeBlueprint:
    payload = {
        "macroplot_id": "heist",
        "macroplot_reading": "The theft is a way of paying an older debt.",
        "subplot_ids": ["infiltration"],
        "role_suggestions": [
            RoleSuggestion(functional_role="helper", persona="thief", sketch="opens the way")
        ],
        "unexpected_angle": "The vault is already empty when they arrive.",
        "considered": [
            SkeletonMatch(
                skeleton_id="heist",
                score=0.9,
                lexical_score=0.9,
                catalog_order=0,
            )
        ],
    }
    payload.update(overrides)
    return NarrativeBlueprint(**payload)


def test_guidance_is_phrased_as_optional_inspiration() -> None:
    text = blueprint_guidance(blueprint())
    assert "non-binding" in text
    assert "must" not in text.casefold()
    assert "The vault is already empty when they arrive." in text
    assert "helper" in text


def test_guidance_drops_unknown_ids_instead_of_raising() -> None:
    text = blueprint_guidance(blueprint(macroplot_id="not_a_skeleton", subplot_ids=["nope"]))
    assert "not_a_skeleton" in text
    assert "none in particular" in text


def test_blueprint_accepts_unknown_ids_but_caps_subplots() -> None:
    assert blueprint(macroplot_id="invented").macroplot_id == "invented"
    with pytest.raises(ValidationError):
        blueprint(subplot_ids=["heist", "escape", "duel", "ambush"])
