from .env_vars import EnvVars, env
from .utility import get_caller_name


class OrchestrationConfig:
    """
    Config object that holds details for the the whole run and all steps.

    - User-provided arguments to steps
    - Typed access known environment variables
    """

    env: EnvVars
    step_args: dict[str, str]

    def __init__(self):
        self.env = env
        self.step_args = {}

    def get_step_args(self, step_name: str | None = None) -> str:
        """
        Get the arguments that were provided by the cli for a given step.
        """

        if step_name is None:
            step_name = get_caller_name(1) or "no_step"

        return self.step_args.get(step_name, "")


# singleton
config = OrchestrationConfig()
