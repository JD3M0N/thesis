export function formatDate(dateValue: string): string {
  const date = new Date(dateValue);
  return new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function storyLabel(title: string | null, plot: string): string {
  if (title && title.trim().length > 0) {
    return title;
  }
  return plot.length > 64 ? `${plot.slice(0, 64)}...` : plot;
}
