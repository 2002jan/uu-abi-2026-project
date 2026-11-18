def format_duration(seconds: float) -> str:
    total_seconds = int(seconds)

    minutes, secs = divmod(total_seconds, 60)

    hours, mins = divmod(minutes, 60)

    if hours > 0:
        return f"{hours}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"