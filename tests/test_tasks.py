from fastapi.testclient import TestClient

from api.app.main import app

client = TestClient(app)


def test_create_and_get_task():
    resp = client.post("/tasks", json={"title": "first"})
    assert resp.status_code == 200, resp.text
    task = resp.json()
    assert task["title"] == "first"
    assert task["status"] == "NEW"
    task_id = task["id"]

    # Get by id
    g = client.get(f"/tasks/{task_id}")
    assert g.status_code == 200
    fetched = g.json()
    assert fetched["id"] == task_id
    assert fetched["title"] == "first"


def test_list_and_update_and_delete():
    # create two
    t1 = client.post("/tasks/", json={"title": "a"}).json()
    t2 = client.post("/tasks/", json={"title": "b"}).json()

    # list
    L = client.get("/tasks/")
    assert L.status_code == 200
    items = L.json()
    assert len(items) >= 2
    ids = [i["id"] for i in items]
    assert t1["id"] in ids and t2["id"] in ids

    # update
    u = client.put(
        f"/tasks/{t1['id']}", json={"title": "test11", "status": "SUCCEEDED", "result": "ok"}
    )
    print(u.json())
    assert u.status_code == 200
    updated = u.json()
    assert updated["status"] == "SUCCEEDED"
    assert updated["result"] == "ok"

    # delete
    d = client.delete(f"/tasks/{t2['id']}")
    assert d.status_code == 200

    # 404 after delete
    g = client.get(f"/tasks/{t2['id']}")
    assert g.status_code == 404


def test_put_not_found():
    r = client.put(
        "/tasks/c5256521-1111-43e8-9748-6f033cd4a3af",
        json={"title": "test11", "status": "SUCCEEDED", "result": "ok"},
    )
    assert r.status_code == 404
