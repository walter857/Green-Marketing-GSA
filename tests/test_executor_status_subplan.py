"""The STATUS subplan of scripts/execute_approved_plan.py is pause-only.

These tests pin the guard rails: it must refuse any operation other than
PAUSE_AD_GROUP_CRITERION, must refuse any proposed_state other than PAUSED, and
must build exactly one status-update operation per action with a mask that
touches only `status`.
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


class FakeMask:
    def __init__(self):
        self.paths = []


class FakeCriterionOp:
    def __init__(self):
        self.update = type("U", (), {"resource_name": "", "status": None})()
        self.update_mask = FakeMask()


class FakeMutateOp:
    def __init__(self):
        self.ad_group_criterion_operation = FakeCriterionOp()


class FakeEnums:
    class AdGroupCriterionStatusEnum:
        PAUSED = "PAUSED_ENUM"
        ENABLED = "ENABLED_ENUM"

    class AdGroupAdStatusEnum:
        ENABLED = "AD_ENABLED"
        PAUSED = "AD_PAUSED"

    class KeywordMatchTypeEnum:
        PHRASE = "PHRASE_ENUM"
        EXACT = "EXACT_ENUM"


class FakeClient:
    enums = FakeEnums()

    def get_type(self, name):
        assert name == "MutateOperation"
        return FakeMutateOp()

    @staticmethod
    def copy_from(dest, src):
        dest.paths = list(src.paths)


def action(**over):
    base = {
        "action_id": "KW-01",
        "operation": "PAUSE_AD_GROUP_CRITERION",
        "proposed_state": "PAUSED",
        "ad_group_id": "191263597345",
        "criterion_id": "123456789",
        "keyword_text": "asphalt contractor near me",
        "match_type": "PHRASE",
        "ad_group_name": "Paver Installation Near Me",
    }
    base.update(over)
    return base


def test_builds_one_pause_operation_per_action():
    ops, log = executor.build(FakeClient(), "2429758629", "STATUS",
                              [action(), action(action_id="KW-02",
                                                criterion_id="987654321")])
    assert len(ops) == 2
    for op in ops:
        u = op.ad_group_criterion_operation.update
        assert u.resource_name.startswith("customers/2429758629/adGroupCriteria/")
        assert "~" in u.resource_name
        assert u.status == "PAUSED_ENUM"
        assert op.ad_group_criterion_operation.update_mask.paths == ["status"]
    assert all("PAUSE keyword" in line for line in log)


def test_refuses_a_non_pause_operation():
    with pytest.raises(SystemExit) as exc:
        executor.build(FakeClient(), "2429758629", "STATUS",
                       [action(operation="ENABLE_AD_GROUP_CRITERION")])
    assert "PAUSE_AD_GROUP_CRITERION" in str(exc.value)


def test_refuses_a_proposed_state_other_than_paused():
    with pytest.raises(SystemExit) as exc:
        executor.build(FakeClient(), "2429758629", "STATUS",
                       [action(proposed_state="ENABLED")])
    assert "must be PAUSED" in str(exc.value)


def test_refuses_removal_disguised_as_status():
    with pytest.raises(SystemExit):
        executor.build(FakeClient(), "2429758629", "STATUS",
                       [action(operation="REMOVE_AD_GROUP_CRITERION")])


def test_one_bad_action_stops_the_whole_batch():
    """No operation may be built if any action in the batch is illegal."""
    with pytest.raises(SystemExit):
        executor.build(FakeClient(), "2429758629", "STATUS",
                       [action(), action(action_id="KW-02", proposed_state="ENABLED")])
