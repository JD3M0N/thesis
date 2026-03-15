import { StoryDetailView } from "@/components/story-detail-view";

type StoryPageProps = {
  params: Promise<{ storyId: string }>;
};

export default async function StoryPage({ params }: StoryPageProps) {
  const { storyId } = await params;
  return <StoryDetailView storyId={storyId} />;
}
