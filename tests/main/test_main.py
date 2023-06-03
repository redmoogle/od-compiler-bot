def test_route_post(mocker, client):
    mocked_return = {"compiler": "PASS", "server": "PASS", "timeout": False}
    mocker.patch("od_compiler.compileOD", return_value=mocked_return)

    resp = client.post("/compile", json={"code_to_compile": 'world.log << "Hello!"'})

    assert resp.json == mocked_return


def test_route_invalid_call(client):
    resp = client.get("/compile")
    assert resp.status_code == 405


def test_route_mangled_post(client):
    resp = client.post("/compile", json={"this_will_fail": True})
    assert resp.status_code == 400
