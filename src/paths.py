import os
from dataclasses import dataclass
from pathlib import Path


def _get_xdg_dir(env_var: str, default_subpath: str, app_name: str = "banking") -> Path:
    """Resolve an XDG directory with fallback, ensuring the directory exists."""

    val = os.environ.get(env_var)
    base = Path(val) if val else Path.home() / default_subpath
    target = base / app_name
    target.mkdir(parents=True, exist_ok=True)
    return target


@dataclass
class Paths:
    config_dir: Path = _get_xdg_dir("XDG_CONFIG_HOME", ".config")
    cache_dir: Path = _get_xdg_dir("XDG_CACHE_HOME", ".cache")
    state_dir: Path = _get_xdg_dir("XDG_STATE_HOME", ".local/state")

    @property
    def config_file(self) -> Path:
        """exposes config.yaml in the current working directory first,
        then ~/.config/banking/."""

        local_config = Path("config.yaml")
        if local_config.is_file():
            return local_config
        return self.config_dir / "config.yaml"

    @property
    def rules_file(self) -> Path:
        """Looks for rules.yaml in current working directory first, then ~/.config/banking/."""
        local_rules = Path("rules.yaml")
        if local_rules.is_file():
            return local_rules
        return self.config_dir / "rules.yaml"

    @property
    def sync_state_file(self) -> Path:
        return self.state_dir / "sync_state.json"


PATHS = Paths()
paths = PATHS

if __name__ == "__main__":
    print(f"Config Dir:     {PATHS.config_dir}")
    print(f"Config File:    {PATHS.config_file}")
    print(f"exists:         {PATHS.config_file.exists()}")
    print(f"Cache Dir:      {PATHS.cache_dir}")
    print(f"State Dir:      {PATHS.state_dir}")
    print(f"State File:     {PATHS.sync_state_file}")
