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
    assert decide("test_watchlist.json", "watchlist.json", "countries.json") == ["Secondary"]


def test_quarantine():
    assert decide("test_quarantine.json", "watchlist.json", "countries.json") == ["Quarantine"]


def test_incomplete():
    assert decide("test_4cases_should_give_Accept_Accept_incomplete_incomplete.json", "watchlist.json", "countries.json") == ["Accept", "Accept", "Reject", "Reject"]


def test_files():
    with pytest.raises(FileNotFoundError):
        decide("test_returning_citizen.json", "", "countries.json")

# add functions for other tests
test_incomplete()
