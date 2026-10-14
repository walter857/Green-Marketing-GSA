"""The SITE_OR_TRACKING subplan sets campaign.final_url_suffix and nothing else.

These tests pin the guard that protects the ClickCease tracking template: the
branch must refuse any other operation, any proposed_state that is not a final
URL suffix, and anything that mentions a tracking template.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

spec = importlib.util.spec_from_file_location(
    "execute_approved_plan", ROOT / "scripts" / "execute_approved_plan.py")
executor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(executor)

SUFFIX = "utm_source=google&utm_medium=cpc&utm_campaign={campaignid}"


class FakeMask:
    def __init__(self):
        self.paths = []


class FakeCampaignOp:
    def __init__(self):
        self.update = type("U", (), {"resource_name": "", "final_url_suffix": ""})()
        self.update_mask = FakeMask()


class FakeMutateOp:
    def __init__(self):
        self.campaign_operation = FakeCampaignOp()


class FakeClient:
    enums = type("E", (), {})()

    def get_type(self, name):
        assert name == "MutateOperation"
        return FakeMutateOp()

    @staticmethod
    def copy_from(dest, src):
        dest.paths = list(src.paths)


def action(**over):
    base = {
        "action_id": "TRK-01",
        "operation": "SET_CAMPAIGN_FINAL_URL_SUFFIX",
        "resource_id": "23484806108",
        "resource_name": "Patio",
        "proposed_state": "final_url_suffix = " + SUFFIX,
    }
    base.update(over)
    return base


def test_sets_only_the_final_url_suffix():
    ops, log = executor.build(FakeClient(), "2429758629", "SITE_OR_TRACKING",
                              [action(), action(action_id="TRK-02",
                                                resource_id="23489296528",
                                                resource_name="Pavers")])
    assert len(ops) == 2
    for op in ops:
        assert op.campaign_operation.update.final_url_suffix == SUFFIX
        assert op.campaign_operation.update_mask.paths == ["final_url_suffix"]
        assert op.campaign_operation.update.resource_name.startswith(
            "customers/2429758629/campaigns/")
    assert all("SET final_url_suffix" in line for line in log)


def test_refuses_a_non_suffix_operation():
    with pytest.raises(SystemExit) as exc:
        executor.build(FakeClient(), "2429758629", "SITE_OR_TRACKING",
                       [action(operation="SET_CAMPAIGN_TRACKING_URL_TEMPLATE")])
    assert "SET_CAMPAIGN_FINAL_URL_SUFFIX" in str(exc.value)


def test_refuses_a_proposed_state_that_is_not_a_suffix():
    with pytest.raises(SystemExit) as exc:
        executor.build(FakeClient(), "2429758629", "SITE_OR_TRACKING",
                       [action(proposed_state="tracking_url_template = http://x")])
    assert "final_url_suffix = " in str(exc.value)


def test_refuses_anything_mentioning_a_tracking_template():
    with pytest.raises(SystemExit):
        executor.build(FakeClient(), "2429758629", "SITE_OR_TRACKING",
                       [action(proposed_state="final_url_suffix = a=b&tracking_url_template=x")])


def test_refuses_a_clickcease_url_in_the_suffix():
    with pytest.raises(SystemExit):
        executor.build(FakeClient(), "2429758629", "SITE_OR_TRACKING",
                       [action(proposed_state="final_url_suffix = u=https://monitor.clickcease.com/x")])


def test_refuses_a_suffix_over_the_length_limit():
    with pytest.raises(SystemExit) as exc:
        executor.build(FakeClient(), "2429758629", "SITE_OR_TRACKING",
                       [action(proposed_state="final_url_suffix = " + "a" * 2049)])
    assert "2048" in str(exc.value)


def test_one_bad_action_stops_the_whole_batch():
    with pytest.raises(SystemExit):
        executor.build(FakeClient(), "2429758629", "SITE_OR_TRACKING",
                       [action(), action(action_id="TRK-02", operation="SOMETHING_ELSE")])
