import pytest
import sys
sys.path.insert(0,r"Y:\ndha\pre-deposit_prod\LD_working\SOUNZ\scripts")
from Pypdf2_text import parse_pdf
import os
cwd = os.getcwd()



# Test case 1: Check if function returns a dictionary with all keys
def test_parse_pdf_keys():
    result = parse_pdf(os.path.join(cwd,'files','test_copy.pdf'))
    assert isinstance(result, dict)
    assert 'Piano Sonata No. 10' in result.values()
    assert 'for solo piano' in result.values()
    assert '2022' in result.values()
    assert 'Colin Decio' in result.values()
    assert '' in result.values()

# Test case 2: Check if function returns correct metadata for a sample PDF
def test_parse_pdf_content():
    result = parse_pdf(os.path.join(cwd,'files','test_copy2.pdf'))
    assert result['title'] == 'Piano Concerto in F ("Elizabeth")'
    assert result['subtitle'] == 'for piano and orchestra'
    assert result['year'] == '2022'
    assert result['author'] == 'Michael Bell'
    assert result['message'] == ''


# Test case 3: Check if function raises an exception when passed an invalid file path
def test_parse_pdf_invalid_path():
    with pytest.raises(Exception):
        parse_pdf(os.path.join(cwd,'files','test_copy3.pdf'))


# Test case 4: Unvalid pdf
def test_invalid_pdf():
    with pytest.raises(Exception) as e:
        parse_pdf(os.path.join(cwd,'files','test_copy_wrong.pdf'))
    assert str(e.value) == "EOF marker not found"