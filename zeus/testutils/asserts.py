def assert_json_response(response):
    assert response.headers['Content-Type'] == 'application/json'
