from .context.blueprint.GLLD import Lake

def test_glld(capsys, example_fixture):
    Lake.check_connection()
    captured = capsys.readouterr()
    assert True in captured.out


