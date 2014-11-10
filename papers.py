#!/usr/bin/env python3

""" Computer-based immigration office for Kanadia """

__author__ = 'Peymon & Archon'
__email__ = "peymonarchon@peychon.com"

__copyright__ = "2014 PeymonArchon"
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
    # open and read json files
    with open(input_file, "r") as input_file_reader:
        traveller_information = input_file_reader.read()
        traveller_information_output = json.loads(traveller_information)
    with open(countries_file, "r") as countries_file_reader:
        countries_file_contents = countries_file_reader.read()
        countries_file_output = json.loads(countries_file_contents)
    with open(watchlist_file, "r") as watchlist_file_reader:
        watchlist_file_contents = watchlist_file_reader.read()
        watchlist_file_output = json.loads(watchlist_file_contents)

    # function begins testing
    decision_list = []
    for traveller in traveller_information_output:
        decision = {"Quarantine": "", "Reject": "", "Secondary": ""}
        if incompleteness(traveller):
            decision["Reject"] = True
        elif quarantine(traveller, countries_file_output):
            decision["Quarantine"] = True
        elif not valid_visa(traveller, countries_file_output):
            decision["Reject"] = True
        elif watchlist(traveller, watchlist_file_output):
            decision["Secondary"] = True
        # add the decisions to decision_list
        if decision["Quarantine"]:
            decision_list.append("Quarantine")
        elif decision["Reject"]:
            decision_list.append("Reject")
        elif decision["Secondary"]:
            decision_list.append("Secondary")
        else:
            decision_list.append("Accept")
    # show what is on the decision_list
    return decision_list


def returning_home(traveller):
    """
    Check whether or not the traveller's home country is KAN

    :param traveller: Dictionary of traveller information
    :return: Whether or not traveller is from KAN, TRUE for yes, False for no
    """

    if traveller["home"]["country"].lower() == "kan":
        return True
    return False


def quarantine(q_traveller, q_countries_file):
    """
    Check if the traveller needs to be quarantined

    :param q_traveller: Dictionary of traveller info
    :param q_countries_file: The current watchlist dictionary from json file
    :return: quarantine_state; True if needs to be quarantined, False otherwise
    """
    if "via" in q_traveller:
        if q_countries_file[q_traveller["via"]["country"].upper()]["medical_advisory"]:
            return True
    elif "from" in q_traveller:
        if q_countries_file[q_traveller["from"]["country"].upper()]["medical_advisory"]:
            return True
    return False


def incompleteness(traveller_info):
    """
    Check if the traveller info has every required field

    :param traveller_info: list of traveller info
    :return: completeness_state; True if has everything, False otherwise
    """
    # adding required fields to a list
    req_field = ["passport", "first_name", "last_name", "birth_date", "home",
                 "entry_reason", "from"]
    # checking for each field and if any is missing return as incomplete
    for field in req_field:
        if field not in traveller_info:
            return True
        elif traveller_info[field] == "":
            return True
    if "via" in traveller_info:
        for via_key in traveller_info["via"]:
            if traveller_info["via"][via_key] == "":
                return True

    # checking for format of each key
    if not valid_date_format(traveller_info["birth_date"]):
        return True
    if "visa" in traveller_info:
        if not valid_visa_date_format(traveller_info["visa"]["date"]):
            return True
        if not valid_visa_code_format(traveller_info["visa"]["code"]):
            return True
    if not valid_passport_format(traveller_info["passport"]):
        return True
    return False


def valid_visa(traveller, countries_file):
    """
    Check if the traveller has valid visa if need

    :param traveller: list of traveller info
    :param countries_file: the current countries file from json file
    :return: visa_state; True if visa is within 2 years, False otherwise
    """
    today = date.today()
    year = timedelta(days=365)
    cut_off_date = today - year * 2

    if returning_home(traveller) and traveller["entry_reason"].lower() == "returning":
        return True
    if traveller["entry_reason"].lower() == "visit":
        if countries_file[traveller["from"]["country"].upper()]["visitor_visa_required"] == "0":
            return True
        elif traveller["visa"]["date"] >= str(cut_off_date):
            return True
    if traveller["entry_reason"].lower() == "transit":
        if countries_file[traveller["from"]["country"].upper()]["transit_visa_required"] == "0":
            return True
        elif traveller["visa"]["date"] >= str(cut_off_date):
            return True
    return False


def watchlist(traveller, watchlist_file):
    """
    Check if the traveller is on watchlist

    :param traveller: list of traveller info
    :param watchlist_file: the current watchlist file from json file
    :return: watchlist_state; True if on watchlist, False otherwise
    """
    for watchlist_person in watchlist_file:
        if traveller["first_name"].lower() == watchlist_person["first_name"].lower() and traveller[
            "last_name"].lower() == watchlist_person["last_name"].lower():
            if watchlist_person["passport"] == "":
                #prevent misjudging someone who has the same name as a watchlist person, but different passport no.#
                return True
        if traveller["passport"].upper() == watchlist_person["passport"].upper():
            return True
    return False


def valid_date_format(date_string):
    """
    Check whether a date has the format YYYY-mm-dd in numbers

    :param date_string: date to be checked
    :return: Boolean True if the format is valid, False otherwise
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def valid_visa_date_format(visa_date):
    """
    Check to see if visa is in the right format

    :param visa_date: string, date to be checked
    :return: Boolean True if the format is valid, False otherwise
    """
    try:
        datetime.strptime(visa_date, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def valid_visa_code_format(visa_code):
    """
    Check whether a visa number is two sets of five alpha-number characters separated by a dash

    :param visa_code: string, visa number to be checked
    :return:
    """
    code_format = re.compile('^\w{5}-\w{5}$')
    if code_format.match(visa_code):
        return True
    else:
        return False


def valid_passport_format(passport_number):
    """
    Check whether a passport number is five sets of five alpha-number characters separated by dashes

    :param passport_number: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('^\w{5}-\w{5}-\w{5}-\w{5}-\w{5}$')

    if passport_format.match(passport_number):
        return True
    else:
        return False





