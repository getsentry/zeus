def test_index(client, default_hook_token):
    path = '/hooks/job/{}/{}'.format(default_hook_token.id, default_hook_token.get_signature())
    payload = {
        'provider': 'travis',
        'build': {
            'external_id': '3',
        },
        'job': {
            'provider': 'travis',
            'external_id': '3.2',
            'result': 'passed',
            'status': 'finished',
        },
    }

    resp = client.post(
        path,
        json=payload,
    )
    assert resp.status_code == 200, repr(resp.data)
