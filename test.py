import requests


def test_valid_auth():
    auth_path = '/novapass/api/v1.0/getauth'
    auth_host = 'http://localhost'
    auth_port = '1916'
    auth_url = "{0}:{1}{2}".format(auth_host, auth_port, auth_path)
    payload = {
        'api_key': 'ECE22945F7A2800E',
        'card_id': '15.30755',
        'tool_id': 'tst_tool1'
    }
    response = requests.post(auth_url, json=payload)
    assert response.status_code == 200

    json_response = response.json()

    assert json_response.get('message') == 'granted'
    assert json_response.get('user_name') == 'Joe CraftUser'
    assert json_response.get('error') == 0
    assert json_response.get('tool_auths') == 'ind_sew:tst_tool1:tst_tool2:tst_tool3:tst_tool4:'


def run_tests():
    test_valid_auth()
    print 'Success: All tests passed'


if __name__ == '__main__':
    run_tests()
