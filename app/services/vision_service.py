import asyncio
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _mirage():
    try:
        import cactus
    except ImportError as exc:
        raise RuntimeError("Mirage is unavailable. Install cactus-compute in the backend environment.") from exc
    return cactus.Mirage()


def analyze_image(image_path: str) -> dict:
    path = Path(image_path)
    if not path.is_file():
        raise ValueError("Image file does not exist.")
    result = _mirage().describe(str(path))
    if isinstance(result, (dict, list)):
        import json
        description = json.dumps(result, ensure_ascii=False)
    else:
        description = str(result)
    if not description.strip():
        raise RuntimeError("Mirage returned an empty description.")
    return {
        "provider": "Cactus Mirage",
        "visual_description": description,
        "limitations": "This describes visible evidence only; it does not prove the underlying root cause.",
    }


async def analyze_image_async(image_path: str) -> dict:
    return await asyncio.to_thread(analyze_image, image_path)
