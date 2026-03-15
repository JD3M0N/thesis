export type StoryStatus = "pending" | "running" | "completed" | "failed";

export type CharacterInput = {
  name: string;
  role: string;
  description: string;
};

export type User = {
  id: string;
  email: string;
};

export type AuthResponse = {
  user: User;
};

export type StoryListItem = {
  id: string;
  title: string | null;
  summary: string | null;
  style: string;
  plot: string;
  length: "short" | "medium" | "long";
  language: string;
  status: StoryStatus;
  created_at: string;
  updated_at: string;
};

export type StoryDetail = StoryListItem & {
  story_text: string | null;
  error_message: string | null;
};

export type StoryGenerateRequest = {
  characters: CharacterInput[];
  style: string;
  plot: string;
  length: "short" | "medium" | "long";
  language: string;
};

export type StoryJobCreated = {
  id: string;
  status: StoryStatus;
};
