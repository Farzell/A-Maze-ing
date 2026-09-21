from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Any
import sys


class Config(BaseModel):
    WIDTH: int = Field(ge=2, le=100)
    HEIGHT: int = Field(ge=2, le=100)
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool
    SEED: int | None = None
    ALGORITHME: str

    @model_validator(mode="after")
    def check_entry_exit(self) -> "Config":
        if self.ENTRY == self.EXIT:
            raise ValueError("ENTRY and EXIT can't be on the same cell.")

        x, y = self.ENTRY
        if not (0 <= x < self.WIDTH and 0 <= y < self.HEIGHT):
            raise ValueError("Error: entry is not in the maze")

        x, y = self.EXIT
        if not (0 <= x < self.WIDTH and 0 <= y < self.HEIGHT):
            raise ValueError("Error: exit is not in the maze")

        return self


def coord_parsed(coord_str: str) -> tuple[int, int]:
    """Convert str to tuple"""
    split_coord = coord_str.split(",")
    if len(split_coord) != 2:
        raise ValueError(f"Error: check the coordinates please -> {coord_str}")
    return int(split_coord[0]), int(split_coord[1])


def config_parsing(text_file: str) -> dict[str, Any]:
    """Extract in a dict the KEY=VALUE from config file"""
    config: dict[str, Any] = {}

    for line_file in text_file.splitlines():
        line = line_file.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise ValueError(f"Error: '{line}' is not a KEY=VALUE as expected.")

        key, value = line.split("=", maxsplit=1)
        key = key.strip()
        value = value.strip()

        if not key or not value:
            raise ValueError("Error: missing KEY or VALUE")

        if key in ("ENTRY", "EXIT"):
            config[key] = coord_parsed(value)
        else:
            config[key] = value

    return config


def read_file(filepath: str) -> Config:
    """Read and parse the config file"""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            lines = file.read()
    except FileNotFoundError as error:
        print(f"Error: '{filepath}' is not found.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: permission denied for file '{filepath}'.")
        sys.exit(1)    
    except OSError as error:
        print(f"Error reading '{filepath}': {error}")
        sys.exit(1)

    try:
        parsed_dict = config_parsing(lines)
    except ValueError as error:
        print(f"Error of format in config: {error}")
        sys.exit(1)

    try:
        output_config = Config(**parsed_dict)
    except ValidationError as error:
        print(f"Error in config: {error}")
        sys.exit(1)

    return output_config


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"To run this program: python3 a-maze-ing.py config.txt")
        sys.exit(1)

    config = read_file(sys.argv[1])
    print(config)
