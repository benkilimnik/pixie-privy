import schemathesis
from hypothesis_faker import abas
from hypothesis_faker import addresses
from hypothesis_faker import am_pms
from hypothesis_faker import android_platform_tokens
from hypothesis_faker import ascii_company_emails
from hypothesis_faker import ascii_emails
from hypothesis_faker import ascii_free_emails
from hypothesis_faker import ascii_safe_emails
from hypothesis_faker import bank_countries
from hypothesis_faker import bbans
from hypothesis_faker import binaries
from hypothesis_faker import booleans
from hypothesis_faker import bss
from hypothesis_faker import building_numbers
from hypothesis_faker import catch_phrases
from hypothesis_faker import centuries
from hypothesis_faker import chromes
from hypothesis_faker import cities
from hypothesis_faker import city_suffixes
from hypothesis_faker import color_names
from hypothesis_faker import colors
from hypothesis_faker import companies
from hypothesis_faker import company_emails
from hypothesis_faker import company_suffixes
from hypothesis_faker import coordinates
from hypothesis_faker import countries
from hypothesis_faker import country_calling_codes
from hypothesis_faker import country_codes
from hypothesis_faker import credit_card_expires
from hypothesis_faker import credit_card_numbers
from hypothesis_faker import credit_card_providers
from hypothesis_faker import credit_card_security_codes
from hypothesis_faker import credit_cards_full
from hypothesis_faker import cryptocurrencies
from hypothesis_faker import cryptocurrency_codes
from hypothesis_faker import cryptocurrency_names
from hypothesis_faker import csvs
from hypothesis_faker import currencies
from hypothesis_faker import currency_codes
from hypothesis_faker import currency_names
from hypothesis_faker import currency_symbols
from hypothesis_faker import current_countries
from hypothesis_faker import current_country_codes
from hypothesis_faker import date_between_dates
from hypothesis_faker import date_objects
from hypothesis_faker import date_time
from hypothesis_faker import date_times_ad
from hypothesis_faker import date_times_between
from hypothesis_faker import date_times_between_dates
from hypothesis_faker import date_times_this_century
from hypothesis_faker import date_times_this_decade
from hypothesis_faker import date_times_this_month
from hypothesis_faker import date_times_this_year
from hypothesis_faker import dates
from hypothesis_faker import dates_between
from hypothesis_faker import dates_of_birth
from hypothesis_faker import dates_this_century
from hypothesis_faker import dates_this_decade
from hypothesis_faker import dates_this_month
from hypothesis_faker import dates_this_year
from hypothesis_faker import days_of_month
from hypothesis_faker import days_of_week
from hypothesis_faker import dgas
from hypothesis_faker import domain_names
from hypothesis_faker import domain_words
from hypothesis_faker import dsvs
from hypothesis_faker import ean8s
from hypothesis_faker import ean13s
from hypothesis_faker import eans
from hypothesis_faker import emails
from hypothesis_faker import file_extensions
from hypothesis_faker import file_names
from hypothesis_faker import file_paths
from hypothesis_faker import firefoxes
from hypothesis_faker import first_name_females
from hypothesis_faker import first_name_males
from hypothesis_faker import first_name_nonbinaries
from hypothesis_faker import first_names
from hypothesis_faker import fixed_widths
from hypothesis_faker import free_email_domains
from hypothesis_faker import free_emails
from hypothesis_faker import future_dates
from hypothesis_faker import future_datetimes
from hypothesis_faker import hex_colors
from hypothesis_faker import hostnames
from hypothesis_faker import http_methods
from hypothesis_faker import iana_ids
from hypothesis_faker import ibans
from hypothesis_faker import image_urls
from hypothesis_faker import images
from hypothesis_faker import internet_explorers
from hypothesis_faker import ios_platform_tokens
from hypothesis_faker import ipv4_network_classes
from hypothesis_faker import ipv4_privates
from hypothesis_faker import ipv4_publics
from hypothesis_faker import ipv4s
from hypothesis_faker import ipv6s
from hypothesis_faker import isbn10s
from hypothesis_faker import isbn13s
from hypothesis_faker import iso8601s
from hypothesis_faker import jobs
from hypothesis_faker import jsons
from hypothesis_faker import language_names
from hypothesis_faker import last_name_females
from hypothesis_faker import last_name_males
from hypothesis_faker import last_name_nonbinaries
from hypothesis_faker import last_names
from hypothesis_faker import license_plates
from hypothesis_faker import linux_platform_tokens
from hypothesis_faker import linux_processors
from hypothesis_faker import localized_ean8s
from hypothesis_faker import localized_ean13s
from hypothesis_faker import localized_eans
from hypothesis_faker import mac_addresses
from hypothesis_faker import mac_platform_tokens
from hypothesis_faker import mac_processors
from hypothesis_faker import md5s
from hypothesis_faker import mime_types
from hypothesis_faker import month_names
from hypothesis_faker import months
from hypothesis_faker import msisdns
from hypothesis_faker import name_females
from hypothesis_faker import name_males
from hypothesis_faker import name_nonbinaries
from hypothesis_faker import names
from hypothesis_faker import nic_handles
from hypothesis_faker import null_booleans
from hypothesis_faker import operas
from hypothesis_faker import paragraphs
from hypothesis_faker import passwords
from hypothesis_faker import past_dates
from hypothesis_faker import past_datetime
from hypothesis_faker import phone_numbers
from hypothesis_faker import port_numbers
from hypothesis_faker import postcodes
from hypothesis_faker import prefix_females
from hypothesis_faker import prefix_males
from hypothesis_faker import prefix_nonbinaries
from hypothesis_faker import prefixes
from hypothesis_faker import pricetags
from hypothesis_faker import psvs
from hypothesis_faker import pybools
from hypothesis_faker import pydecimals
from hypothesis_faker import pyfloats
from hypothesis_faker import pyints
from hypothesis_faker import pystr_formats
from hypothesis_faker import pystrs
from hypothesis_faker import rgb_colors
from hypothesis_faker import rgb_css_colors
from hypothesis_faker import ripe_ids
from hypothesis_faker import safaris
from hypothesis_faker import safe_color_names
from hypothesis_faker import safe_domain_names
from hypothesis_faker import safe_emails
from hypothesis_faker import sentences
from hypothesis_faker import sha1s
from hypothesis_faker import sha256s
from hypothesis_faker import slugs
from hypothesis_faker import ssns
from hypothesis_faker import street_addresses
from hypothesis_faker import street_names
from hypothesis_faker import street_suffixes
from hypothesis_faker import suffix_females
from hypothesis_faker import suffix_males
from hypothesis_faker import suffix_nonbinaries
from hypothesis_faker import suffixes
from hypothesis_faker import swift8s
from hypothesis_faker import swift11s
from hypothesis_faker import swifts
from hypothesis_faker import tars
from hypothesis_faker import texts
from hypothesis_faker import time_deltas
from hypothesis_faker import time_objects
from hypothesis_faker import times
from hypothesis_faker import timezones
from hypothesis_faker import tlds
from hypothesis_faker import tsvs
from hypothesis_faker import unix_devices
from hypothesis_faker import unix_partitions
from hypothesis_faker import unix_times
from hypothesis_faker import uri_extensions
from hypothesis_faker import uri_pages
from hypothesis_faker import uri_paths
from hypothesis_faker import uris
from hypothesis_faker import urls
from hypothesis_faker import user_agents
from hypothesis_faker import user_names
from hypothesis_faker import windows_platform_tokens
from hypothesis_faker import words
from hypothesis_faker import years
from hypothesis_faker import zips


class FakerStrategies:
    """Register Faker strategies for generating data for specific API parameter "format", corresponding to
    the one used in the API schema as the "format" keyword value.
    """

    def __init__(self):
        schemathesis.register_string_format("abas", abas())
        schemathesis.register_string_format("addresses", addresses())
        schemathesis.register_string_format("am_pms", am_pms())
        schemathesis.register_string_format(
            "android_platform_tokens", android_platform_tokens())
        schemathesis.register_string_format(
            "ascii_company_emails", ascii_company_emails())
        schemathesis.register_string_format("ascii_emails", ascii_emails())
        schemathesis.register_string_format(
            "ascii_free_emails", ascii_free_emails())
        schemathesis.register_string_format(
            "ascii_safe_emails", ascii_safe_emails())
        schemathesis.register_string_format("bank_countries", bank_countries())
        schemathesis.register_string_format("bbans", bbans())
        schemathesis.register_string_format("binaries", binaries())
        schemathesis.register_string_format("booleans", booleans())
        schemathesis.register_string_format("bss", bss())
        schemathesis.register_string_format(
            "building_numbers", building_numbers())
        schemathesis.register_string_format("catch_phrases", catch_phrases())
        schemathesis.register_string_format("centuries", centuries())
        schemathesis.register_string_format("chromes", chromes())
        schemathesis.register_string_format("cities", cities())
        schemathesis.register_string_format("city_suffixes", city_suffixes())
        schemathesis.register_string_format("color_names", color_names())
        schemathesis.register_string_format("colors", colors())
        schemathesis.register_string_format("companies", companies())
        schemathesis.register_string_format("company_emails", company_emails())
        schemathesis.register_string_format(
            "company_suffixes", company_suffixes())
        schemathesis.register_string_format("coordinates", coordinates())
        schemathesis.register_string_format("countries", countries())
        schemathesis.register_string_format(
            "country_calling_codes", country_calling_codes())
        schemathesis.register_string_format("country_codes", country_codes())
        schemathesis.register_string_format(
            "credit_card_expires", credit_card_expires())
        schemathesis.register_string_format(
            "credit_card_numbers", credit_card_numbers())
        schemathesis.register_string_format(
            "credit_card_providers", credit_card_providers())
        schemathesis.register_string_format(
            "credit_card_security_codes", credit_card_security_codes())
        schemathesis.register_string_format(
            "credit_cards_full", credit_cards_full())
        schemathesis.register_string_format(
            "cryptocurrencies", cryptocurrencies())
        schemathesis.register_string_format(
            "cryptocurrency_codes", cryptocurrency_codes())
        schemathesis.register_string_format(
            "cryptocurrency_names", cryptocurrency_names())
        schemathesis.register_string_format("csvs", csvs())
        schemathesis.register_string_format("currencies", currencies())
        schemathesis.register_string_format("currency_codes", currency_codes())
        schemathesis.register_string_format("currency_names", currency_names())
        schemathesis.register_string_format(
            "currency_symbols", currency_symbols())
        schemathesis.register_string_format(
            "current_countries", current_countries())
        schemathesis.register_string_format(
            "current_country_codes", current_country_codes())
        schemathesis.register_string_format(
            "date_between_dates", date_between_dates())
        schemathesis.register_string_format("date_objects", date_objects())
        schemathesis.register_string_format("date_time", date_time())
        schemathesis.register_string_format("date_times_ad", date_times_ad())
        schemathesis.register_string_format(
            "date_times_between", date_times_between())
        schemathesis.register_string_format(
            "date_times_between_dates", date_times_between_dates())
        schemathesis.register_string_format(
            "date_times_this_century", date_times_this_century())
        schemathesis.register_string_format(
            "date_times_this_decade", date_times_this_decade())
        schemathesis.register_string_format(
            "date_times_this_month", date_times_this_month())
        schemathesis.register_string_format(
            "date_times_this_year", date_times_this_year())
        schemathesis.register_string_format("dates", dates())
        schemathesis.register_string_format("dates_between", dates_between())
        schemathesis.register_string_format("dates_of_birth", dates_of_birth())
        schemathesis.register_string_format(
            "dates_this_century", dates_this_century())
        schemathesis.register_string_format(
            "dates_this_decade", dates_this_decade())
        schemathesis.register_string_format(
            "dates_this_month", dates_this_month())
        schemathesis.register_string_format(
            "dates_this_year", dates_this_year())
        schemathesis.register_string_format("days_of_month", days_of_month())
        schemathesis.register_string_format("days_of_week", days_of_week())
        schemathesis.register_string_format("dgas", dgas())
        schemathesis.register_string_format("domain_names", domain_names())
        schemathesis.register_string_format("domain_words", domain_words())
        schemathesis.register_string_format("dsvs", dsvs())
        schemathesis.register_string_format("ean8s", ean8s())
        schemathesis.register_string_format("ean13s", ean13s())
        schemathesis.register_string_format("eans", eans())
        schemathesis.register_string_format("emails", emails())
        schemathesis.register_string_format(
            "file_extensions", file_extensions())
        schemathesis.register_string_format("file_names", file_names())
        schemathesis.register_string_format("file_paths", file_paths())
        schemathesis.register_string_format("firefoxes", firefoxes())
        schemathesis.register_string_format(
            "first_name_females", first_name_females())
        schemathesis.register_string_format(
            "first_name_males", first_name_males())
        schemathesis.register_string_format(
            "first_name_nonbinaries", first_name_nonbinaries())
        schemathesis.register_string_format("first_names", first_names())
        schemathesis.register_string_format("fixed_widths", fixed_widths())
        schemathesis.register_string_format(
            "free_email_domains", free_email_domains())
        schemathesis.register_string_format("free_emails", free_emails())
        schemathesis.register_string_format("future_dates", future_dates())
        schemathesis.register_string_format(
            "future_datetimes", future_datetimes())
        schemathesis.register_string_format("hex_colors", hex_colors())
        schemathesis.register_string_format("hostnames", hostnames())
        schemathesis.register_string_format("http_methods", http_methods())
        schemathesis.register_string_format("iana_ids", iana_ids())
        schemathesis.register_string_format("ibans", ibans())
        schemathesis.register_string_format("image_urls", image_urls())
        schemathesis.register_string_format("images", images())
        schemathesis.register_string_format(
            "internet_explorers", internet_explorers())
        schemathesis.register_string_format(
            "ios_platform_tokens", ios_platform_tokens())
        schemathesis.register_string_format(
            "ipv4_network_classes", ipv4_network_classes())
        schemathesis.register_string_format("ipv4_privates", ipv4_privates())
        schemathesis.register_string_format("ipv4_publics", ipv4_publics())
        schemathesis.register_string_format("ipv4s", ipv4s())
        schemathesis.register_string_format("ipv6s", ipv6s())
        schemathesis.register_string_format("isbn10s", isbn10s())
        schemathesis.register_string_format("isbn13s", isbn13s())
        schemathesis.register_string_format("iso8601s", iso8601s())
        schemathesis.register_string_format("jobs", jobs())
        schemathesis.register_string_format("jsons", jsons())
        schemathesis.register_string_format("language_names", language_names())
        schemathesis.register_string_format(
            "last_name_females", last_name_females())
        schemathesis.register_string_format(
            "last_name_males", last_name_males())
        schemathesis.register_string_format(
            "last_name_nonbinaries", last_name_nonbinaries())
        schemathesis.register_string_format("last_names", last_names())
        schemathesis.register_string_format("license_plates", license_plates())
        schemathesis.register_string_format(
            "linux_platform_tokens", linux_platform_tokens())
        schemathesis.register_string_format(
            "linux_processors", linux_processors())
        schemathesis.register_string_format(
            "localized_ean8s", localized_ean8s())
        schemathesis.register_string_format(
            "localized_ean13s", localized_ean13s())
        schemathesis.register_string_format("localized_eans", localized_eans())
        schemathesis.register_string_format("mac_addresses", mac_addresses())
        schemathesis.register_string_format(
            "mac_platform_tokens", mac_platform_tokens())
        schemathesis.register_string_format("mac_processors", mac_processors())
        schemathesis.register_string_format("md5s", md5s())
        schemathesis.register_string_format("mime_types", mime_types())
        schemathesis.register_string_format("month_names", month_names())
        schemathesis.register_string_format("months", months())
        schemathesis.register_string_format("msisdns", msisdns())
        schemathesis.register_string_format("name_females", name_females())
        schemathesis.register_string_format("name_males", name_males())
        schemathesis.register_string_format(
            "name_nonbinaries", name_nonbinaries())
        schemathesis.register_string_format("names", names())
        schemathesis.register_string_format("nic_handles", nic_handles())
        schemathesis.register_string_format("null_booleans", null_booleans())
        schemathesis.register_string_format("operas", operas())
        schemathesis.register_string_format("paragraphs", paragraphs())
        schemathesis.register_string_format("passwords", passwords())
        schemathesis.register_string_format("past_dates", past_dates())
        schemathesis.register_string_format("past_datetime", past_datetime())
        schemathesis.register_string_format("phone_numbers", phone_numbers())
        schemathesis.register_string_format("port_numbers", port_numbers())
        schemathesis.register_string_format("postcodes", postcodes())
        schemathesis.register_string_format("prefix_females", prefix_females())
        schemathesis.register_string_format("prefix_males", prefix_males())
        schemathesis.register_string_format(
            "prefix_nonbinaries", prefix_nonbinaries())
        schemathesis.register_string_format("prefixes", prefixes())
        schemathesis.register_string_format("pricetags", pricetags())
        schemathesis.register_string_format("psvs", psvs())
        schemathesis.register_string_format("pybools", pybools())
        schemathesis.register_string_format("pydecimals", pydecimals())
        schemathesis.register_string_format("pyfloats", pyfloats())
        schemathesis.register_string_format("pyints", pyints())
        schemathesis.register_string_format("pystr_formats", pystr_formats())
        schemathesis.register_string_format("pystrs", pystrs())
        schemathesis.register_string_format("rgb_colors", rgb_colors())
        schemathesis.register_string_format("rgb_css_colors", rgb_css_colors())
        schemathesis.register_string_format("ripe_ids", ripe_ids())
        schemathesis.register_string_format("safaris", safaris())
        schemathesis.register_string_format(
            "safe_color_names", safe_color_names())
        schemathesis.register_string_format(
            "safe_domain_names", safe_domain_names())
        schemathesis.register_string_format("safe_emails", safe_emails())
        schemathesis.register_string_format("sentences", sentences())
        schemathesis.register_string_format("sha1s", sha1s())
        schemathesis.register_string_format("sha256s", sha256s())
        schemathesis.register_string_format("slugs", slugs())
        schemathesis.register_string_format("ssns", ssns())
        schemathesis.register_string_format(
            "street_addresses", street_addresses())
        schemathesis.register_string_format("street_names", street_names())
        schemathesis.register_string_format(
            "street_suffixes", street_suffixes())
        schemathesis.register_string_format("suffix_females", suffix_females())
        schemathesis.register_string_format("suffix_males", suffix_males())
        schemathesis.register_string_format(
            "suffix_nonbinaries", suffix_nonbinaries())
        schemathesis.register_string_format("suffixes", suffixes())
        schemathesis.register_string_format("swift8s", swift8s())
        schemathesis.register_string_format("swift11s", swift11s())
        schemathesis.register_string_format("swifts", swifts())
        schemathesis.register_string_format("tars", tars())
        schemathesis.register_string_format("texts", texts())
        schemathesis.register_string_format("time_deltas", time_deltas())
        schemathesis.register_string_format("time_objects", time_objects())
        schemathesis.register_string_format("times", times())
        schemathesis.register_string_format("timezones", timezones())
        schemathesis.register_string_format("tlds", tlds())
        schemathesis.register_string_format("tsvs", tsvs())
        schemathesis.register_string_format("unix_devices", unix_devices())
        schemathesis.register_string_format(
            "unix_partitions", unix_partitions())
        schemathesis.register_string_format("unix_times", unix_times())
        schemathesis.register_string_format("uri_extensions", uri_extensions())
        schemathesis.register_string_format("uri_pages", uri_pages())
        schemathesis.register_string_format("uri_paths", uri_paths())
        schemathesis.register_string_format("uris", uris())
        schemathesis.register_string_format("urls", urls())
        schemathesis.register_string_format("user_agents", user_agents())
        schemathesis.register_string_format("user_names", user_names())
        schemathesis.register_string_format(
            "windows_platform_tokens", windows_platform_tokens())
        schemathesis.register_string_format("words", words())
        schemathesis.register_string_format("years", years())
        schemathesis.register_string_format("zips", zips())
