#!/usr/bin/env python3

""" Computer-based immigration office for Kanadia """

__author__ = 'Peymon & Archon'
__email__ = "peymonarchon@peychon.com"

__copyright__ = "2014 PeyChon"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line
import re
import datetime
import json
from datetime import *


def decide(input_file, watchlist_file, countries_file):
    """
    Decides whether a traveller's entry into Kanadia should be accepted

    :param input_file: The name of a JSON formatted file that contains cases to decide
    :param watchlist_file: The name of a JSON formatted file that contains names and passport numbers on a watchlist
    :param countries_file: The name of a JSON formatted file that contains country data, such as whether
        an entry or transit visa is required, and whether there is currently a medical advisory
    :return: List of strings. Possible values of strings are: "Accept", "Reject", "Secondary", and "Quarantine"
    """

    with open(input_file, "r") as input_file_reader:
        traveller_information= input_file_reader.read()
        traveller_information_output = json.loads(traveller_information)
    with open(countries_file, "r") as countries_file_reader:
        countries_file_contents = countries_file_reader.read()
        countries_file_output = json.loads(countries_file_contents)
    with open(watchlist_file, "r") as watchlist_file_reader:
        watchlist_file_contents = watchlist_file_reader.read()
        watchlist_file_output = json.loads(watchlist_file_contents)
    decision = {"Quarantine": "", "Reject": "", "Secondary": ""}
    decision_list = []
    for traveller in traveller_information_output:
        if not completeness(traveller):
            decision["Reject"] = True
        if quarantine(traveller, countries_file_output):
            decision["Quarantine"] = True
        if not valid_visa(traveller, countries_file_output):
            decision["Reject"] = True
        if watchlist(traveller, watchlist_file_output):
            decision["Secondary"] = True
        if decision["Quarantine"]:
            decision_list.append("Quarantine")
        elif decision["Reject"]:
            decision_list.append("Reject")
        elif decision["Secondary"]:
            decision_list.append("Secondary")
        else:
            decision_list.append("Accept")
    return decision_list


def quarantine(traveller, countries_file):
    """check if the traveller needs to be quarantined
    :param traveller: dictionary of traveller info
    :param countries_file: the current watchlist file from json file
    :return: quarantine_state; True if needs to be quarantined, False otherwise
    """
    quarantine_state = False
    if "via" in traveller:
        if countries_file[traveller["via"]["country"].upper()]["medical_advisory"]:
            quarantine_state = True
    elif countries_file[traveller["from"]["country"].upper()]["medical_advisory"]:
        quarantine_state = True
    return quarantine_state


def completeness(traveller_info):
    """check if the traveller info has every required field
    :param traveller_info: list of traveller info
    :return: completeness_state; True if has everything, False otherwise
    """
    completeness_state = True
    for info in traveller_info:
        if not info:
            completeness_state = False
        elif info.index == "home" or info == "from" or info == "via":
            for entries in info:
                if not entries:
                    completeness_state = False
    if not valid_date_format(traveller_info["birth_date"]):
        completeness_state = False
    if "visa" in traveller_info:
        if not valid_date_format(traveller_info["visa"]["date"]):
            completeness_state = False
    if not valid_passport_format(traveller_info["passport"]):
        completeness_state = False
    return completeness_state


def valid_visa(traveller, countries_file):
    """check if the traveller has valid visa if need
    :param traveller: list of traveller info
    :param countries_file: the current countries file from json file
    :return: visa_state; True if visa is within 2 years, False otherwise
    """
    today = date.today()
    year = timedelta(days=365)
    cut_of_date = today - year * 2
    visa_state = False
    if traveller["entry_reason"].lower() == "returning" and traveller["home"]["country"].upper() == "KAN":
        visa_state = True
    elif traveller["entry_reason"].lower() == "visit":
        if countries_file[traveller["from"]["country"].upper()]["visitor_visa_required"] == "0":
            visa_state = True
        elif traveller["visa"]["date"] >= cut_of_date:
            visa_state = True
    elif traveller["entry_reason"].lower() == "transit":
        if countries_file[traveller["from"]["country"].upper()]["transit_visa_required"] == "0":
            visa_state = True
        elif traveller["visa"]["date"] >= cut_of_date:
            visa_state = True
    return visa_state


def watchlist(traveller, watchlist_file):
    """check if the traveller is in watchlist
    :param traveller: list of traveller info
    :param watchlist_file: the current watchlist file from json file
    :return: watchlist_state; True if in watchlist, False otherwise
    """
    watchlist_state = False
    for watchlist_person in watchlist_file:
        if traveller["passport"].upper() == watchlist_person["passport"].upper():
            watchlist_state = True
        elif traveller["first_name"].lower() == watchlist_person["first_name"].lower() and traveller["last_name"].lower() == watchlist_person["last_name"].lower():
            watchlist_state = True
    return watchlist_state


def valid_passport_format(passport_number):
    """
    Checks whether a passport number is five sets of five alpha-number characters separated by dashes
    :param passport_number: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('.{5}-.{5}-.{5}-.{5}-.{5}')

    if passport_format.match(passport_number):
        return True
    else:
        return False


def valid_date_format(date_string):
    """
    Checks whether a date has the format YYYY-mm-dd in numbers
    :param date_string: date to be checked
    :return: Boolean True if the format is valid, False otherwise
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

