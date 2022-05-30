from django.test import Client, TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from feedapp.tests import config


class ClusterManagementTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            config.username, config.email, config.password
        )
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.headers = {"HTTP_AUTHORIZATION": f"Token {self.token}"}
        self.request_client = Client(**self.headers)

    def test_create_cluster_success(self):
        r = self.request_client.get(
            "/cluster/create/", headers=self.headers, data=config.get_cluster_data()
        )
        self.assertEqual(r.status_code, 200)

        # check cluster was indeed created in db

    def test_create_cluster_missing_name(self):
        pass

    def test_create_cluster_missing_description(self):
        pass

    def test_create_cluster_missing_key(self):
        pass

    def test_create_cluster_wrong_key(self):
        pass

    def test_edit_cluster_success(self):
        pass

    def test_edit_cluster_missing_name(self):
        pass

    def test_edit_cluster_missing_description(self):
        pass

    def test_edit_cluster_missing_id(self):
        pass

    def test_edit_cluster_wrong_key(self):
        pass

    def test_edit_cluster_missing_key(self):
        pass

    def test_edit_cluster_wrong_id(self):
        pass

    def test_delete_cluster_success(self):
        pass

    def test_delete_cluster_wrong_key(self):
        pass

    def test_delete_cluster_missing_key(self):
        pass

    def test_delete_cluster_missing_id(self):
        pass

    def test_delete_cluster_wrong_id(self):
        pass

    def test_leave_cluster_success(self):
        pass

    def test_leave_cluster_wrong_key(self):
        pass

    def test_leave_cluster_missing_key(self):
        pass

    def test_leave_cluster_missing_id(self):
        pass

    def test_leave_clusteer_wrong_id(self):
        pass

    def test_join_cluster_success(self):
        pass

    def test_join_cluster_wrong_key(self):
        pass

    def test_join_cluster_missing_key(self):
        pass

    def test_join_cluster_missing_id(self):
        pass

    def test_join_cluster_wrong_id(self):
        pass
