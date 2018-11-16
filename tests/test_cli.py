import pytest
import leo


@pytest.mark.parametrize('cli,expected', [
    ([''], {'query': ''}),
    (['Baum'], {'query': 'Baum'}),
    (['-D', 'Baum'], {'with_defs': True}),
    (['-E', 'baum'], {'with_examples': True}),
    (['--with-examples', 'baum'], {'with_examples': True}),
    (['-P', 'baum'], {'with_phrases': True}),
    (['--with-phrases', 'baum'], {'with_phrases': True}),
    (['-v', 'baum'], {'verbose': 1}),
    (['-l', 'es', 'baum'], {'language': 'es'}),
    (['--language', 'es', 'baum'], {'language': 'es'})
])
def test_parse_cli(cli, expected):
    result = leo.parse(cli)
    # Create set difference and only compare this with the expected dictionary
    diff = set(result.__dict__) & set(expected)
    result = {i: getattr(result, i) for i in diff}
    assert result == expected
