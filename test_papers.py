#!/usr/bin/env python3

""" Module to test papers.py  """

__author__ = 'Susan Sim'
__email__ = "ses@drsusansim.org"

__copyright__ = "2014 Susan Sim"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line
import pytest
from papers import decide


def test_accept():
    assert decide("test_returning_citizen.json", "watchlist.json", "countries.json") == ["Accept", "Accept"]


def test_secondary():
    assert decide("test_watchlist_S_S_S.json", "watchlist.json", "countries.json") == ["Secondary", "Secondary", "Secondary"]


def test_quarantine():
    assert decide("test_quarantine.json", "watchlist.json", "countries.json") == ["Quarantine"]


def test_case_and_incomplete():
    assert decide("test_case_and_incomplete_A_A_R_R.json", "watchlist.json", "countries.json") == ["Accept", "Accept", "Reject", "Reject"]


def test_files():
    with pytest.raises(FileNotFoundError):
        decide("test_returning_citizen.json", "", "countries.json")

# add functions for other tests
test_case_and_incomplete()
