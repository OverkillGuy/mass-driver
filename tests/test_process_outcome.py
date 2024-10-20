"""Check the process_outcome function for complex multi-file PatchDriver management

Feature: Processing many files' outcomes
  As a mass-driver driver dev
  I need to compute overall driver success from many file outcomes
  In order to make a drivers that process many files
"""

import logging

import pytest
from mass_driver_plugins.drivers.bricks import process_outcomes
from mass_driver_core.patchdriver import PatchOutcome, PatchResult

LOGGER = logging.getLogger()


def test_outcomes_all_ok():
    """Scenario: All files outcome OK"""
    # Given all PATCHED_OK outcomes
    all_ok = {
        f"file{i}": PatchResult(outcome=PatchOutcome.PATCHED_OK) for i in range(3)
    }
    # When I process the outcomes
    result = process_outcomes(all_ok, fail_on_any_error=True, logger=LOGGER)
    # Then I get a PATCHED_OK outcome
    assert result.outcome == PatchOutcome.PATCHED_OK, "Should get a PATCHED_OK outcome"


def test_outcomes_fail_on_error():
    """Scenario: Fail on any error"""
    # Given one error outcome
    one_bad = {
        f"file{i}": PatchResult(outcome=PatchOutcome.PATCHED_OK) for i in range(2)
    }
    # And two OK outcomes
    one_bad["file2"] = PatchResult(
        outcome=PatchOutcome.PATCH_ERROR, detail="Bad thingy"
    )
    # When I process the outcomes
    result = process_outcomes(one_bad, fail_on_any_error=True, logger=LOGGER)
    # Then I get a PATCHED_OK outcome
    assert result.outcome == PatchOutcome.PATCH_ERROR, "Should get an error outcome"


@pytest.mark.parametrize("fail_on_any_error", [True, False])
def test_outcomes_all_already_patched(fail_on_any_error, logger=LOGGER):
    """Scenario: All Already-Patched propagates"""
    # Given all ALREADY_PATCHED outcomes
    all_patched = {
        f"file{i}": PatchResult(outcome=PatchOutcome.ALREADY_PATCHED) for i in range(3)
    }
    # When I process the outcomes
    result = process_outcomes(
        all_patched, fail_on_any_error=fail_on_any_error, logger=LOGGER
    )
    # Then I get a PATCHED_OK outcome
    assert (
        result.outcome == PatchOutcome.ALREADY_PATCHED
    ), "Should get an already patched outcome"


@pytest.mark.parametrize("fail_on_any_error", [True, False])
def test_outcomes_all_not_apply(fail_on_any_error):
    """Scenario: All does-not-apply propagates"""
    # Given all PATCH_DOES_NOT_APPLY outcomes
    all_patched = {
        f"file{i}": PatchResult(outcome=PatchOutcome.PATCH_DOES_NOT_APPLY)
        for i in range(3)
    }
    # When I process the outcomes
    result = process_outcomes(
        all_patched, fail_on_any_error=fail_on_any_error, logger=LOGGER
    )
    # Then I get a PATCHED_OK outcome
    assert (
        result.outcome == PatchOutcome.PATCH_DOES_NOT_APPLY
    ), "Should get a does not apply outcome"
