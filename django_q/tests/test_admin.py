def test_admin_view(admin_client):
    response = admin_client.get('/admin/django_q/')
    assert response.status_code == 200
    response = admin_client.get('/admin/django_q/failure/')
    assert response.status_code == 200
    response = admin_client.get('/admin/django_q/success/')
    assert response.status_code == 200
    response = admin_client.get('/admin/django_q/schedule/')
    assert response.status_code == 200
    response = admin_client.get('/admin/django_q/schedule/add/')
    assert response.status_code == 200
