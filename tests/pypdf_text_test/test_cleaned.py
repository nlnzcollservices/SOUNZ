import pytest
import sys
sys.path.insert(0,r"Y:\ndha\pre-deposit_prod\LD_working\SOUNZ\scripts")
from Pypdf2_text import cleaned

def test_cleaned_replaces_single_quotes():
    assert cleaned("It's a beautiful day") == "It's a beautiful day"


def test_cleaned_replaces_ligatures():
    assert cleaned("officeﬂoor") == "officefloor"

def test_cleaned_removes_copyright_symbol():
    assert cleaned("Copyright © 2023") == "Copyright 2023"

def test_cleaned_removes_leading_and_trailing_spaces():
    assert cleaned("  hello world ") == "hello world"

def test_cleaned_removes_extra_spaces_between_words():
    assert cleaned("Hello     world") == "Hello world"

def test_cleaned_removes_line_separator_character():
    assert cleaned("Hello\u2028world") == "Helloworld"

def test_cleaned_replaces_german_char():
    assert cleaned("Großenwahn") == "Groflenwahn"

def test_cleaned_works_with_empty_string():
    assert cleaned("") == ""

def test_cleaned_handles_special_characters():
    assert cleaned("!@#$%^&*()_+{}|:\"<>?[]';,./`~") == "!@#$%^&*()_+{}|:\"<>?[]';,./`~"

