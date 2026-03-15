from fastapi import APIRouter, HTTPException, Request, status
from sqlmodel import select

from app.deps import CurrentUserDep, SessionDep
from app.logging_utils import get_audit_logger
from app.models import Story
from app.schemas import StoryDetail, StoryGenerateRequest, StoryJobCreated, StoryListItem

router = APIRouter(prefix="/stories", tags=["stories"])
audit_logger = get_audit_logger()


def _to_list_item(story: Story) -> StoryListItem:
    return StoryListItem(
        id=story.id,
        title=story.title,
        summary=story.summary,
        style=story.style,
        plot=story.plot,
        length=story.length,
        language=story.language,
        status=story.status,
        created_at=story.created_at.isoformat(),
        updated_at=story.updated_at.isoformat(),
    )


def _to_detail(story: Story) -> StoryDetail:
    return StoryDetail(
        id=story.id,
        title=story.title,
        summary=story.summary,
        style=story.style,
        plot=story.plot,
        length=story.length,
        language=story.language,
        status=story.status,
        story_text=story.story_text,
        error_message=story.error_message,
        created_at=story.created_at.isoformat(),
        updated_at=story.updated_at.isoformat(),
    )


@router.get("", response_model=list[StoryListItem])
def list_stories(session: SessionDep, user: CurrentUserDep):
    stories = session.exec(select(Story).where(Story.user_id == user.id).order_by(Story.created_at.desc())).all()
    return [_to_list_item(story) for story in stories]


@router.get("/{story_id}", response_model=StoryDetail)
def get_story(story_id: str, session: SessionDep, user: CurrentUserDep):
    story = session.get(Story, story_id)
    if not story or story.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    return _to_detail(story)


@router.post("/generate", response_model=StoryJobCreated, status_code=status.HTTP_202_ACCEPTED)
async def generate_story(
    payload: StoryGenerateRequest,
    request: Request,
    session: SessionDep,
    user: CurrentUserDep,
):
    input_brief = payload.to_input_brief()
    story = Story(
        user_id=user.id,
        style=payload.style,
        plot=payload.plot,
        length=payload.length,
        language=payload.language,
        characters_json=[character.dict() for character in payload.characters],
        input_brief=input_brief,
        story_packet={"input_brief": input_brief},
        status="pending",
    )
    session.add(story)
    session.commit()
    session.refresh(story)

    audit_logger.info(
        "story.created story_id=%s user_id=%s email=%s style=%s length=%s",
        story.id,
        user.id,
        user.email,
        story.style,
        story.length,
    )
    await request.app.state.worker.enqueue(story.id)
    return StoryJobCreated(id=story.id, status=story.status)
