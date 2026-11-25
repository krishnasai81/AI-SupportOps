import asyncio
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _load_mirage():
    try:
        import cactus
    except ImportError as exc:
        raise RuntimeError(
            "Mirage is not installed. Install requirements including cactus-compute."
        ) from exc
    return cactus.Mirage()


def analyze_image(image_path: str) -> dict:
    """
    Analyze an image with Cactus Mirage. Returns the raw model output and a
    conservative evidence warning; it does not claim definitive root cause.
    """
    path = Path(image_path)
    if not path.exists() or not path.is_file():
        raise ValueError("Image file was not found.")
    result = _load_mirage().describe(str(path))
    return {
        "provider": "cactus-mirage",
        "analysis": result,
        "limitations": "Visual symptoms only. Root cause must be verified by troubleshooting or a human.",
    }


async def analyze_image_async(image_path: str) -> dict:
    return await asyncio.to_thread(analyze_image, image_path)
