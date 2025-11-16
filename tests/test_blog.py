def test_index_shows_posts(client):
    res = client.get('/')
    assert res.status_code == 200
    data = res.data
    assert b'First Post' in data
    assert b'Second Post' in data


def test_post_page(client):
    res = client.get('/1')
    assert res.status_code == 200
    assert b'First Post' in res.data
    assert b'Content for the first post' in res.data


def test_create_post_and_validation(client):
    # missing title should show flash
    res = client.post('/create', data={'title': '', 'content': 'x'}, follow_redirects=True)
    assert b'Title is required!' in res.data

    # create a new post
    res = client.post('/create', data={'title': 'New', 'content': 'New content'}, follow_redirects=True)
    assert res.status_code == 200
    assert b'New' in res.data


def test_edit_post(client):
    # edit post 1
    res = client.post('/1/edit', data={'title': 'First Edited', 'content': 'Edited content'}, follow_redirects=True)
    assert res.status_code == 200
    assert b'First Edited' in res.data


def test_delete_post(client):
    # delete post 2
    res = client.post('/2/delete', follow_redirects=True)
    assert res.status_code == 200
    assert b'was successfully deleted' in res.data
