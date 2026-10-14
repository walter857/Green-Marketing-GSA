"""Proofs for the approved location-target rules.

Each test exists to make one specific mistake impossible: a radius quietly converted to
kilometers, a coordinate altered, a distinct-but-overlapping target deduplicated away,
presence-or-interest slipping in, or a postal code claiming a resolution it never had.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gm_gsa.config import load_yaml  # noqa: E402
from validate_location_targets import validate  # noqa: E402

MANIFEST_PATH = ROOT / "clients" / "ekg-lawn-services" / "location-targets.yaml"


def manifest() -> dict:
    return load_yaml(MANIFEST_PATH)


class ApprovedManifestTests(unittest.TestCase):
    def setUp(self):
        self.doc = manifest()
        self.block = self.doc["location_targets"]

    def test_the_shipped_manifest_validates(self):
        self.assertEqual(validate(self.doc), [])

    def test_exactly_six_approved_positive_targets(self):
        self.assertEqual(self.block["total_positive_targets"], 6)
        self.assertEqual(len(self.block["proximity_targets"]), 5)
        self.assertEqual(len(self.block["postal_code_targets"]), 1)

    def test_every_radius_is_two_miles(self):
        for target in self.block["proximity_targets"]:
            self.assertEqual(target["radius"], 2.0)
            self.assertEqual(target["radius_units"], "MILES")

    def test_presence_targeting_only(self):
        self.assertEqual(
            self.block["geo_target_type_setting"]["positive_geo_target_type"], "PRESENCE"
        )

    def test_the_five_coordinate_pairs_are_distinct(self):
        pairs = {(t["latitude"], t["longitude"]) for t in self.block["proximity_targets"]}
        self.assertEqual(len(pairs), 5)
        self.assertEqual(self.block["exact_duplicates_found"], 0)

    def test_micro_degrees_round_trip_exactly(self):
        for target in self.block["proximity_targets"]:
            for axis in ("latitude", "longitude"):
                self.assertEqual(
                    target[f"{axis}_micro_degrees"], round(target[axis] * 1_000_000)
                )

    def test_as_supplied_strings_are_preserved_one_per_target(self):
        self.assertEqual(len(self.block["as_supplied"]), 6)

    def test_the_postal_code_resolved_to_one_targetable_us_constant(self):
        postal = self.block["postal_code_targets"][0]
        self.assertEqual(postal["postal_code"], "23114")
        self.assertEqual(postal["lookup_status"], "RESOLVED")
        self.assertEqual(
            postal["geo_target_constant_resource_name"], "geoTargetConstants/9008421"
        )
        self.assertEqual(postal["resolved_country_code"], "US")
        self.assertEqual(postal["target_type"], "Postal Code")
        self.assertEqual(postal["status"], "ENABLED")
        self.assertTrue(postal["targetable"])

    def test_the_canonical_name_came_from_the_api_not_from_the_coordinates(self):
        """The place name is whatever Google returned, never a guess from lat/lon."""
        postal = self.block["postal_code_targets"][0]
        self.assertEqual(postal["canonical_name"], "23114,Virginia,United States")
        # It must still start with the supplied postal code, so a lookup that drifted to a
        # different place would be caught rather than silently accepted.
        self.assertTrue(postal["canonical_name"].startswith(postal["postal_code"]))

    def test_public_city_wording_comes_from_the_website_not_the_geo_constant(self):
        """City wording must have an independent published source.

        Targeting constants and coordinates authorise Google Ads geo targeting only. Any
        public-facing place name has to come from the client's own published wording, so
        this checks the cities were not lifted out of the resolved constant.
        """
        client = load_yaml(ROOT / "clients" / "ekg-lawn-services" / "client.yaml")["client"]
        area = client["service_area"]
        cities = area.get("cities") or []
        if not cities:
            return  # nothing claimed publicly, trivially safe

        published = area.get("published_service_area_wording", "")
        self.assertTrue(
            published,
            "cities are populated but no published_service_area_wording records the source",
        )
        for city in cities:
            self.assertIn(
                city, published,
                f"{city!r} is not present in the published service-area wording",
            )

        # The resolved constant's canonical name carries no city, so nothing may claim it
        # as a source.
        canonical = self.block["postal_code_targets"][0]["canonical_name"]
        for city in cities:
            self.assertNotIn(
                city, canonical,
                f"{city!r} appears to have been derived from the geo target constant",
            )


class RefusalTests(unittest.TestCase):
    def setUp(self):
        self.doc = manifest()

    def mutate(self, fn):
        doc = copy.deepcopy(self.doc)
        fn(doc["location_targets"])
        return validate(doc)

    def test_kilometre_conversion_is_refused(self):
        def convert(block):
            block["proximity_targets"][0]["radius_units"] = "KILOMETERS"
            block["proximity_targets"][0]["radius"] = 3.22

        errors = self.mutate(convert)
        self.assertTrue(any("kilometers" in e.lower() for e in errors))

    def test_an_altered_coordinate_is_caught(self):
        def alter(block):
            block["proximity_targets"][0]["latitude"] = 37.441925

        errors = self.mutate(alter)
        self.assertTrue(any("was altered" in e for e in errors))

    def test_an_exact_duplicate_is_reported(self):
        def duplicate(block):
            clone = copy.deepcopy(block["proximity_targets"][0])
            clone["id"] = "prox-dupe"
            block["proximity_targets"].append(clone)
            block["total_positive_targets"] = 7
            block["as_supplied"].append(block["as_supplied"][0])

        errors = self.mutate(duplicate)
        self.assertTrue(any("exactly duplicates" in e for e in errors))

    def test_a_dropped_target_is_caught_by_the_count(self):
        def drop(block):
            block["proximity_targets"].pop()

        errors = self.mutate(drop)
        self.assertTrue(any("total_positive_targets" in e for e in errors))

    def test_presence_or_interest_is_refused(self):
        def widen(block):
            block["geo_target_type_setting"]["positive_geo_target_type"] = (
                "PRESENCE_OR_INTEREST"
            )

        errors = self.mutate(widen)
        self.assertTrue(any("PRESENCE" in e for e in errors))

    def test_a_postal_target_cannot_claim_resolution_it_lacks(self):
        def fake(block):
            postal = block["postal_code_targets"][0]
            postal["lookup_status"] = "RESOLVED"
            postal["canonical_name"] = None
            postal["geo_target_constant_resource_name"] = None

        errors = self.mutate(fake)
        self.assertTrue(any("RESOLVED but" in e for e in errors))

    def test_a_pending_target_may_not_carry_a_resource_name(self):
        def sneak(block):
            postal = block["postal_code_targets"][0]
            postal["lookup_status"] = "PENDING_API_ACCESS"
            postal["geo_target_constant_resource_name"] = "geoTargetConstants/9999999"

        errors = self.mutate(sneak)
        self.assertTrue(any("PENDING_API_ACCESS but" in e for e in errors))

    def test_a_non_targetable_constant_is_refused(self):
        def untargetable(block):
            postal = block["postal_code_targets"][0]
            postal.update(
                lookup_status="RESOLVED",
                geo_target_constant_resource_name="geoTargetConstants/9999999",
                canonical_name="Somewhere",
                resolved_country_code="US",
                target_type="Postal Code",
                targetable=False,
            )

        errors = self.mutate(untargetable)
        self.assertTrue(any("not targetable" in e for e in errors))

    def test_an_out_of_range_coordinate_is_refused(self):
        def bad(block):
            target = block["proximity_targets"][0]
            target["latitude"] = 137.441924
            target["latitude_micro_degrees"] = 137441924

        errors = self.mutate(bad)
        self.assertTrue(any("out of range" in e for e in errors))


class WorkOrderConsistencyTests(unittest.TestCase):
    """The work order and the manifest must describe the same six targets."""

    def setUp(self):
        self.block = manifest()["location_targets"]
        self.order = load_yaml(
            ROOT / "clients" / "ekg-lawn-services" / "work-order.yaml"
        )["work_order"]

    def test_service_area_lists_all_six_targets(self):
        self.assertEqual(len(self.order["inputs"]["service_area"]), 6)

    def test_service_area_matches_the_manifest_verbatim(self):
        self.assertEqual(self.order["inputs"]["service_area"], self.block["as_supplied"])

    def test_the_work_order_references_the_manifest(self):
        self.assertIn(
            "clients/ekg-lawn-services/location-targets.yaml",
            self.order["inputs"]["source_files"],
        )

    def test_the_client_profile_keeps_the_single_radius_slot_empty(self):
        """Filling it would mean one proximity target silently outranked the other four."""
        client = load_yaml(ROOT / "clients" / "ekg-lawn-services" / "client.yaml")["client"]
        radius = client["service_area"]["radius"]
        self.assertIsNone(radius["latitude"])
        self.assertIsNone(radius["longitude"])
        self.assertIsNone(radius["distance"])
        self.assertEqual(len(client["service_area"]["proximity_targets"]), 5)


if __name__ == "__main__":
    unittest.main()
