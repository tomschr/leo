import leo
import requests
import pytest
from unittest.mock import MagicMock
from functools import partial
from os import path
from lxml import html


def mock_response_text(url, ok=True):
    current_dir = path.dirname(__file__)
    with open(path.join(current_dir, "data/leo_mock_response.html"),
              "r") as htmlfile:
        text = htmlfile.read()
    response = MagicMock(spec=requests.Response)
    response.ok = ok
    response.url = url
    response.text = text
    return response


def test_get_leo_page_ok(monkeypatch):
    monkeypatch.setattr(leo.requests, 'get',
                        partial(mock_response_text, ok=True))
    assert leo.get_leo_page("mock") == mock_response_text("mock").text


def test_get_leo_page_not_ok(monkeypatch):
    monkeypatch.setattr(leo.requests, 'get',
                        partial(mock_response_text, ok=False))
    with pytest.raises(requests.exceptions.HTTPError):
        leo.get_leo_page("mock")


def test_parse_leo_page(monkeypatch):
    expected = ['subst_en_foo', 'subst_de_foo', 'subst_en_bar', 'subst_de_bar',
                'verb_en_foo', 'verb_de_foo', 'verb_en_bar', 'verb_de_bar',
                'definition_en_foo', 'definition_de_foo', 'definition_en_bar',
                'definition_de_bar', 'phrase_en_foo', 'phrase_de_foo',
                'phrase_en_bar', 'phrase_de_bar', 'example_en_foo',
                'example_de_foo', 'example_en_bar', 'example_de_bar']
    monkeypatch.setattr(leo.requests, 'get',
                        partial(mock_response_text, ok=True))
    text_nodes = list(
            leo.parse_leo_page(leo.get_leo_page("mock")).getroot().itertext())
    text_nodes = [node.strip() for node in text_nodes]
    text_nodes = list(filter(None, text_nodes))
    assert text_nodes == expected


def test_extract_text():
    expected = ["subst_en_foo", "subst_de_foo"]
    tr = html.fromstring('''<tr><td lang="en"><samp><a '''
                         '''href="/englisch-deutsch/subst_en_foo">{}'''
                         '''</a></samp></td><td lang="de"><samp><a '''
                         '''ref="/englisch-deutsch/subst_de_foo">{}'''
                         '''</a></samp></td></tr>'''.format(*expected))
    tds_text = [leo.extract_text(td) for td in tr.getchildren()]
    assert tds_text == expected


def test_format_as_table(capsys):
    expected = ["foo", "bar", "foobar", "foobaz"]
    tr = html.fromstring('''<tbody> <tr> <td lang="en"> <samp> <a
        href="/englisch-deutsch/subst_en_foo"> {} </a> </samp>
        </td> <td lang="de"> <samp> <a href="/englisch-deutsch/subst_de_foo">
        {} </a> </samp> </td> </tr> <tr> <td lang="en"> <samp> <a
        href="/englisch-deutsch/subst_en_bar"> <mark> {} </mark>
        </a> </samp> </td> <td lang="de"> <samp> <a
        href="/englisch-deutsch/subst_de_bar"> {} </a> </samp>
        </td> </tr> </tbody>'''.format(*expected))
    leo.format_as_table(tr)
    captured = capsys.readouterr()
    for e in expected:
        assert e in captured.out
