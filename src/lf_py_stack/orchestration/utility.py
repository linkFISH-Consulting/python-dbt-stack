import inspect


def get_caller_name(num_back: int = 1) -> str | None:
    """
    Infer caller function name by walking up the frame stack.

    Args:
        num_back: Number of `.f_back` hops from current frame.
                      Example:
                      - 0 -> direct caller (function where use get_caller_name)
                      - 1 -> caller's caller (useful in dataclass __post_init__)
    Returns:
        The inferred function name, or None if unavailable.
    """
    frame = inspect.currentframe()
    try:
        if frame is None:
            return None

        current = frame
        for _ in range(num_back + 1):
            if current.f_back is None:
                return None
            current = current.f_back

        return current.f_code.co_name
    finally:
        # Avoid reference cycles
        del frame
