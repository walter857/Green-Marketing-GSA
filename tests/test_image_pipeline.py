"""Tests for landing-page image preparation.

The rules that matter most: never upscale, never stretch, always land on the exact
required size, and never ship EXIF/GPS metadata.
"""

from __future__ import annotations

import pytest

from PIL import Image

from gm_gsa.image_pipeline import (
    GALLERY_MINIMUM,
    GALLERY_POSITIONS,
    GALLERY_PREFERRED,
    GENERAL_TARGETS,
    ImagePipelineError,
    InsufficientResolutionError,
    crop_box_for_fill,
    fits_without_upscaling,
    inspect,
    process_image,
    resolve_source_box,
    target_for_position,
)


def make(tmp_path, name, size, color=(40, 120, 60), fmt="JPEG"):
    p = tmp_path / name
    Image.new("RGB", size, color).save(p, format=fmt, quality=95)
    return p


class TestTargets:
    @pytest.mark.parametrize(
        "position,expected",
        [(1, (1920, 1080)), (2, (1500, 1200)), (3, (1200, 900)), (4, (1200, 900)),
         (5, (1000, 667))],
    )
    def test_general_positions_have_exact_sizes(self, position, expected):
        assert target_for_position(position) == expected
        assert GENERAL_TARGETS[position] == expected

    @pytest.mark.parametrize("position", GALLERY_POSITIONS)
    def test_gallery_prefers_the_large_size_when_source_allows(self, position):
        assert target_for_position(position, (3000, 2000)) == GALLERY_PREFERRED

    @pytest.mark.parametrize("position", GALLERY_POSITIONS)
    def test_gallery_falls_back_to_minimum_for_a_smaller_source(self, position):
        assert target_for_position(position, (1200, 800)) == GALLERY_MINIMUM

    @pytest.mark.parametrize("position", GALLERY_POSITIONS)
    def test_gallery_returns_none_when_below_the_minimum(self, position):
        assert target_for_position(position, (800, 500)) is None

    def test_unknown_position_raises(self):
        with pytest.raises(ImagePipelineError):
            target_for_position(11)


class TestNoUpscaling:
    def test_fits_requires_both_dimensions(self):
        assert fits_without_upscaling((1920, 1080), (1920, 1080))
        assert not fits_without_upscaling((1919, 1080), (1920, 1080))
        assert not fits_without_upscaling((1920, 1079), (1920, 1080))

    def test_small_source_is_refused_not_enlarged(self, tmp_path):
        src = make(tmp_path, "small.jpg", (640, 480))
        with pytest.raises(InsufficientResolutionError):
            process_image(src, 1, tmp_path / "out.jpg")

    def test_composite_quadrant_sized_source_is_refused_for_gallery(self, tmp_path):
        """A 160px composite quadrant must never become a gallery image."""
        src = make(tmp_path, "quadrant.jpg", (160, 160))
        with pytest.raises(InsufficientResolutionError):
            process_image(src, 6, tmp_path / "out.jpg")

    def test_exactly_sized_source_is_accepted(self, tmp_path):
        src = make(tmp_path, "exact.jpg", (1920, 1080))
        result = process_image(src, 1, tmp_path / "out.jpg")
        assert result.output_size == (1920, 1080)
        assert result.scale == 1.0


class TestCropToFill:
    def test_wide_source_is_cropped_horizontally(self):
        box = crop_box_for_fill((4000, 1000), (1000, 1000))
        assert box[2] - box[0] == 1000
        assert box[3] - box[1] == 1000

    def test_tall_source_is_cropped_vertically(self):
        box = crop_box_for_fill((1000, 4000), (1000, 1000))
        assert box[2] - box[0] == 1000
        assert box[3] - box[1] == 1000

    def test_crop_preserves_target_aspect_ratio(self):
        left, upper, right, lower = crop_box_for_fill((3000, 2000), (1920, 1080))
        assert abs((right - left) / (lower - upper) - 1920 / 1080) < 0.01

    def test_crop_box_never_leaves_the_image(self):
        for focus in [(0.0, 0.0), (1.0, 1.0), (0.5, 0.5), (0.9, 0.1)]:
            left, upper, right, lower = crop_box_for_fill((3000, 2000), (1920, 1080), focus)
            assert 0 <= left < right <= 3000
            assert 0 <= upper < lower <= 2000

    def test_focus_shifts_the_crop(self):
        left_biased = crop_box_for_fill((4000, 1000), (1000, 1000), focus=(0.1, 0.5))
        right_biased = crop_box_for_fill((4000, 1000), (1000, 1000), focus=(0.9, 0.5))
        assert left_biased[0] < right_biased[0]


class TestProcessing:
    @pytest.mark.parametrize("position", sorted(GENERAL_TARGETS))
    def test_output_is_exactly_the_required_size(self, tmp_path, position):
        src = make(tmp_path, "big.jpg", (4000, 3000))
        out = tmp_path / f"{position}.jpg"
        result = process_image(src, position, out)
        with Image.open(out) as im:
            assert im.size == GENERAL_TARGETS[position]
            assert im.format == "JPEG"
        assert result.output_size == GENERAL_TARGETS[position]

    def test_aspect_ratio_is_never_distorted(self, tmp_path):
        """A square source must be cropped to 16:9, not squashed into it."""
        src = make(tmp_path, "square.jpg", (3000, 3000))
        result = process_image(src, 1, tmp_path / "hero.jpg")
        cw = result.crop_box[2] - result.crop_box[0]
        ch = result.crop_box[3] - result.crop_box[1]
        assert abs(cw / ch - 1920 / 1080) < 0.01

    def test_output_carries_no_exif_or_gps_metadata(self, tmp_path):
        src = tmp_path / "withexif.jpg"
        im = Image.new("RGB", (3000, 2000), (10, 90, 40))
        exif = im.getexif()
        exif[271] = "TestCamera"
        im.save(src, format="JPEG", exif=exif)
        out = tmp_path / "clean.jpg"
        process_image(src, 1, out)
        with Image.open(out) as done:
            assert not dict(done.getexif())
            assert "icc_profile" not in done.info or not done.info["icc_profile"]

    def test_output_is_rgb(self, tmp_path):
        src = tmp_path / "gray.png"
        Image.new("L", (3000, 2000), 128).save(src)
        out = tmp_path / "rgb.jpg"
        process_image(src, 3, out)
        with Image.open(out) as done:
            assert done.mode == "RGB"

    def test_gallery_uses_preferred_size_for_a_large_source(self, tmp_path):
        src = make(tmp_path, "huge.jpg", (4032, 3024))
        result = process_image(src, 6, tmp_path / "g.jpg")
        assert result.output_size == GALLERY_PREFERRED

    def test_gallery_uses_minimum_size_for_a_mid_source(self, tmp_path):
        src = make(tmp_path, "mid.jpg", (1400, 900))
        result = process_image(src, 7, tmp_path / "g.jpg")
        assert result.output_size == GALLERY_MINIMUM

    def test_result_records_the_conversion_for_the_report(self, tmp_path):
        src = make(tmp_path, "src.jpg", (4000, 3000))
        result = process_image(src, 1, tmp_path / "o.jpg")
        assert "crop-to-fill" in result.crop_description
        assert result.source_size == (4000, 3000)
        assert result.converted_from_heic is False


class TestSourceBox:
    def test_source_box_restricts_the_usable_region(self, tmp_path):
        src = make(tmp_path, "wide.jpg", (4000, 3000))
        result = process_image(src, 3, tmp_path / "o.jpg", source_box=(0.0, 0.6, 1.0, 1.0))
        assert result.source_size == (4000, 1200)
        assert result.output_size == (1200, 900)

    def test_source_box_still_refuses_to_upscale(self, tmp_path):
        """A tight sub-crop without the pixels is refused, not enlarged."""
        src = make(tmp_path, "wide.jpg", (4000, 3000))
        with pytest.raises(InsufficientResolutionError):
            process_image(src, 1, tmp_path / "o.jpg", source_box=(0.0, 0.9, 0.2, 1.0))

    @pytest.mark.parametrize(
        "box", [(0.5, 0.0, 0.5, 1.0), (0.0, 0.0, 1.1, 1.0), (0.0, 0.8, 1.0, 0.2)]
    )
    def test_invalid_source_box_raises(self, tmp_path, box):
        src = make(tmp_path, "wide.jpg", (4000, 3000))
        with pytest.raises(ImagePipelineError):
            process_image(src, 3, tmp_path / "o.jpg", source_box=box)

    def test_resolve_source_box_maps_fractions_to_pixels(self):
        assert resolve_source_box((1000, 800), (0.0, 0.5, 1.0, 1.0)) == (0, 400, 1000, 800)


class TestInspect:
    def test_reports_usability_per_position(self, tmp_path):
        src = make(tmp_path, "m.jpg", (1500, 1200))
        info = inspect(src)
        assert info["size"] == (1500, 1200)
        assert info["orientation"] == "landscape"
        assert info["usable_for_position"][2] is True
        assert info["usable_for_position"][1] is False  # 1200 < 1080 is fine, 1500 < 1920 not
        assert info["gallery_target"] == GALLERY_MINIMUM

    def test_flags_a_source_too_small_for_any_gallery_slot(self, tmp_path):
        src = make(tmp_path, "tiny.jpg", (500, 400))
        info = inspect(src)
        assert info["gallery_target"] is None
        assert not any(info["usable_for_position"][p] for p in GALLERY_POSITIONS)
