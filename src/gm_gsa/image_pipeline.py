"""Landing-page image preparation: crop-to-fill, HEIC conversion, no-upscale guard.

Rules encoded here, so a future client inherits them automatically:

* every position has an exact output size;
* images are cropped to fill, never stretched, so aspect ratio is always preserved;
* a source that lacks the resolution for a position is REFUSED, never upscaled;
* HEIC originals are converted to high-quality sRGB JPEG;
* EXIF orientation is applied, then metadata is dropped so no GPS or device data ships;
* nothing is sharpened, saturated, bordered, or watermarked.

Pillow does the pixel work. ``pillow-heif`` is registered when present so ``.heic``
originals open like any other file.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:  # pragma: no cover - exercised implicitly when the optional dep is installed
    import pillow_heif

    pillow_heif.register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:  # pragma: no cover
    HEIC_SUPPORTED = False

from PIL import Image, ImageCms, ImageOps

#: Gallery positions accept either size; the larger is preferred.
GALLERY_PREFERRED = (2000, 1212)
GALLERY_MINIMUM = (1000, 606)

GENERAL_TARGETS: dict[int, tuple[int, int]] = {
    1: (1920, 1080),
    2: (1500, 1200),
    3: (1200, 900),
    4: (1200, 900),
    5: (1000, 667),
}
GALLERY_POSITIONS = (6, 7, 8, 9)

JPEG_QUALITY = 92
HEIC_SUFFIXES = {".heic", ".heif"}


class ImagePipelineError(ValueError):
    """Raised when a source cannot satisfy a position's requirements."""


class InsufficientResolutionError(ImagePipelineError):
    """Raised when filling the target would require upscaling."""


@dataclass(frozen=True)
class ProcessResult:
    source: str
    destination: str
    source_size: tuple[int, int]
    output_size: tuple[int, int]
    scale: float
    crop_box: tuple[int, int, int, int]
    source_format: str
    converted_from_heic: bool
    metadata_stripped: bool = True

    @property
    def crop_description(self) -> str:
        sw, sh = self.source_size
        ow, oh = self.output_size
        left, upper, right, lower = self.crop_box
        cw, ch = right - left, lower - upper
        bits = []
        if self.converted_from_heic:
            bits.append("HEIC -> sRGB JPEG")
        if (cw, ch) != (sw, sh):
            bits.append(f"crop-to-fill {sw}x{sh} -> {cw}x{ch} at ({left},{upper})")
        else:
            bits.append("no crop needed")
        if (cw, ch) != (ow, oh):
            bits.append(f"downscale to {ow}x{oh}")
        return "; ".join(bits)


def target_for_position(position: int, source_size: tuple[int, int] | None = None):
    """The required output size for a position.

    Gallery positions return the preferred size when the source can fill it, otherwise the
    minimum. ``None`` means the source is too small for even the minimum.
    """
    if position in GENERAL_TARGETS:
        return GENERAL_TARGETS[position]
    if position not in GALLERY_POSITIONS:
        raise ImagePipelineError(f"unknown image position {position!r}")
    if source_size is None:
        return GALLERY_PREFERRED
    if fits_without_upscaling(source_size, GALLERY_PREFERRED):
        return GALLERY_PREFERRED
    if fits_without_upscaling(source_size, GALLERY_MINIMUM):
        return GALLERY_MINIMUM
    return None


def fits_without_upscaling(source_size: tuple[int, int], target: tuple[int, int]) -> bool:
    """True when the source can cover the target without being enlarged."""
    sw, sh = source_size
    tw, th = target
    return sw >= tw and sh >= th


def crop_box_for_fill(
    source_size: tuple[int, int],
    target: tuple[int, int],
    focus: tuple[float, float] = (0.5, 0.5),
) -> tuple[int, int, int, int]:
    """The crop rectangle that gives ``target``'s aspect ratio at maximum size.

    ``focus`` is the point to keep, as fractions of width and height. The box is clamped so
    it always stays inside the image.
    """
    sw, sh = source_size
    tw, th = target
    if sw <= 0 or sh <= 0:
        raise ImagePipelineError("source has no area")

    target_ratio = tw / th
    source_ratio = sw / sh
    if source_ratio > target_ratio:
        # Source is wider: full height, crop width.
        cw, ch = int(round(sh * target_ratio)), sh
    else:
        cw, ch = sw, int(round(sw / target_ratio))
    cw, ch = min(cw, sw), min(ch, sh)

    fx, fy = focus
    left = int(round(sw * fx - cw / 2))
    upper = int(round(sh * fy - ch / 2))
    left = max(0, min(left, sw - cw))
    upper = max(0, min(upper, sh - ch))
    return (left, upper, left + cw, upper + ch)


def _to_srgb(image: Image.Image) -> Image.Image:
    """Convert to sRGB, honoring an embedded ICC profile when one is present."""
    profile = image.info.get("icc_profile")
    if profile:
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(profile))
            image = ImageCms.profileToProfile(
                image, src, ImageCms.createProfile("sRGB"), outputMode="RGB"
            )
        except Exception:  # noqa: BLE001 - a bad profile must not lose the image
            image = image.convert("RGB")
    elif image.mode != "RGB":
        image = image.convert("RGB")
    return image


def resolve_source_box(
    size: tuple[int, int], box: tuple[float, float, float, float]
) -> tuple[int, int, int, int]:
    """Turn a fractional (left, top, right, bottom) region into pixel coordinates."""
    w, h = size
    left, top, right, bottom = box
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise ImagePipelineError(f"source_box {box!r} must be fractions with left<right, top<bottom")
    return (int(round(w * left)), int(round(h * top)),
            int(round(w * right)), int(round(h * bottom)))


def process_image(
    source: str | Path,
    position: int,
    destination: str | Path,
    *,
    focus: tuple[float, float] = (0.5, 0.5),
    quality: int = JPEG_QUALITY,
    allow_target: tuple[int, int] | None = None,
    source_box: tuple[float, float, float, float] | None = None,
) -> ProcessResult:
    """Crop-to-fill ``source`` to ``position``'s size and write a clean sRGB JPEG.

    ``source_box`` optionally restricts the usable region first, as fractions of the full
    frame. Use it to exclude people, house numbers, clutter, or dead space before the
    aspect-ratio crop. The no-upscale rule is applied to the restricted region, so a tight
    sub-crop that lacks the pixels for a position is refused rather than enlarged.
    """
    source, destination = Path(source), Path(destination)
    if source.suffix.lower() in HEIC_SUFFIXES and not HEIC_SUPPORTED:
        raise ImagePipelineError(
            f"{source.name}: HEIC support unavailable. Install 'pillow-heif'."
        )

    with Image.open(source) as raw:
        source_format = (raw.format or source.suffix.lstrip(".")).upper()
        image = ImageOps.exif_transpose(raw)  # apply rotation, then discard EXIF
        image = _to_srgb(image)
        if source_box is not None:
            image = image.crop(resolve_source_box(image.size, source_box))
        source_size = image.size

        target = allow_target or target_for_position(position, source_size)
        if target is None:
            raise InsufficientResolutionError(
                f"{source.name}: {source_size[0]}x{source_size[1]} is below the "
                f"{GALLERY_MINIMUM[0]}x{GALLERY_MINIMUM[1]} gallery minimum"
            )
        if not fits_without_upscaling(source_size, target):
            raise InsufficientResolutionError(
                f"{source.name}: {source_size[0]}x{source_size[1]} cannot fill "
                f"{target[0]}x{target[1]} without upscaling"
            )

        box = crop_box_for_fill(source_size, target, focus)
        out = image.crop(box)
        if out.size != target:
            out = out.resize(target, Image.LANCZOS)

        destination.parent.mkdir(parents=True, exist_ok=True)
        # No exif= and no icc_profile= argument: metadata is intentionally dropped.
        out.save(destination, format="JPEG", quality=quality, subsampling=0, optimize=True)
        scale = target[0] / (box[2] - box[0])

    return ProcessResult(
        source=str(source),
        destination=str(destination),
        source_size=source_size,
        output_size=target,
        scale=round(scale, 4),
        crop_box=box,
        source_format=source_format,
        converted_from_heic=source.suffix.lower() in HEIC_SUFFIXES,
    )


def inspect(source: str | Path) -> dict[str, Any]:
    """Cheap metadata read used to decide whether a source is usable at all."""
    source = Path(source)
    with Image.open(source) as raw:
        image = ImageOps.exif_transpose(raw)
        size = image.size
    usable = {
        p: (
            fits_without_upscaling(size, GENERAL_TARGETS[p])
            if p in GENERAL_TARGETS
            else target_for_position(p, size) is not None
        )
        for p in list(GENERAL_TARGETS) + list(GALLERY_POSITIONS)
    }
    return {
        "path": str(source),
        "size": size,
        "orientation": "landscape" if size[0] >= size[1] else "portrait",
        "megapixels": round(size[0] * size[1] / 1e6, 2),
        "usable_for_position": usable,
        "gallery_target": target_for_position(6, size),
    }
