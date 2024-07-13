import json
import requests
import keyring
import pandas as pd

username = "nooneathome"
password = keyring.get_password("Dremio", "nooneathome")
headers = {"content-type": "application/json"}
dremioServer = "http://192.168.1.211:9047"


def apiGet(endpoint):
    return json.loads(
        requests.get(
            "{server}/api/v3/{endpoint}".format(server=dremioServer, endpoint=endpoint),
            headers=headers,
        ).text
    )


def apiPost(endpoint, body=None):
    text = requests.post(
        "{server}/api/v3/{endpoint}".format(server=dremioServer, endpoint=endpoint),
        headers=headers,
        data=json.dumps(body),
    ).text

    # a post may return no data
    if text:
        return json.loads(text)
    else:
        return None


def apiPut(endpoint, body=None):
    return requests.put(
        "{server}/api/v3/{endpoint}".format(server=dremioServer, endpoint=endpoint),
        headers=headers,
        data=json.dumps(body),
    ).text


def apiDelete(endpoint):
    return requests.delete(
        "{server}/api/v3/{endpoint}".format(server=dremioServer, endpoint=endpoint),
        headers=headers,
    )


def getCatalogRoot():
    return apiGet("catalog")["data"]


def getByPathChildren(path, children, depth):
    # search children for the item we are looking for
    for item in children:
        if item["path"][depth] == path[0]:
            path.pop(0)
            response = apiGet("catalog/{id}".format(id=(item["id"])))
            if len(path) == 0:
                return response
            else:
                return getByPathChildren(path, response["children"], depth + 1)


def getByPath(path):
    # get the root catalog
    root = getCatalogRoot()

    for item in root:
        if item["path"][0] == path[0]:
            path.pop(0)

            if len(path) == 0:
                return item
            else:
                response = apiGet("catalog/{id}".format(id=item["id"]))
                return getByPathChildren(path, response["children"], 1)


def login(username, password, server):
    # we login using the old api for now
    loginData = {"userName": username, "password": password}
    response = requests.post(
        f"{server}/apiv2/login", headers=headers, data=json.dumps(loginData)
    )
    data = json.loads(response.text)

    # retrieve the login token
    token = data["token"]
    return {
        "content-type": "application/json",
        "authorization": "_dremio{authToken}".format(authToken=token),
    }


headers = login(username, password, dremioServer)
