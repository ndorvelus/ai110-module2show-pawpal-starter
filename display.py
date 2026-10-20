"""Display helpers: emoji and status indicators plus tabulate-based CLI tables."""

from tabulate import tabulate

from pawpal_system import Task

CATEGORY_EMOJI = {
    "exercise": "🦮",
    "feeding": "🍖",
    "grooming": "🛁",
    "health": "💊",
    "enrichment": "🧶",
    "general": "🐾",
}

PRIORITY_BADGE = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}


def category_label(category: str) -> str:
    """Prefix a category with its emoji, falling back to the generic paw."""
    return f"{CATEGORY_EMOJI.get(category, CATEGORY_EMOJI['general'])} {category}"


def priority_badge(priority: str) -> str:
    """Color-coded priority: red for high, yellow for medium, green for low."""
    return PRIORITY_BADGE.get(priority, priority)


def status_icon(task: Task) -> str:
    """A check for finished tasks and an hourglass for pending ones."""
    return "✅ done" if task.completed else "⏳ pending"


def task_rows(tasks: list[Task]) -> list[dict]:
    """Turn tasks into display rows shared by the CLI table and the Streamlit app."""
    return [
        {
            "Status": status_icon(t),
            "Time": t.time or "--:--",
            "Task": t.title,
            "Pet": t.pet_name,
            "Type": category_label(t.category),
            "Priority": priority_badge(t.priority),
            "Min": t.duration_minutes,
        }
        for t in tasks
    ]


def format_task_table(tasks: list[Task]) -> str:
    """Render tasks as a boxed CLI table, or a friendly note if there are none."""
    if not tasks:
        return "(no tasks)"
    return tabulate(task_rows(tasks), headers="keys", tablefmt="rounded_outline")
