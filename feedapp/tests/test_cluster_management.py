import uuid
from django.test import Client, TestCase
from feedapp.views import edit_cluster
from rest_framework.authtoken.models import Token

from feedapp.models import User, Cluster
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
        r = self.request_client.post("/cluster/create/", data=config.get_cluster_data())
        self.assertEqual(r.status_code, 200)

        # check cluster was indeed created in db
        clusters = Cluster.objects.all()
        self.assertEqual(len(clusters), 1)
        created_cluster = clusters[0]
        self.assertEqual(created_cluster.name, config.name)
        self.assertEqual(created_cluster.description, config.description)

    def test_create_cluster_missing_name(self):
        partial_data = config.get_cluster_data()
        del partial_data["name"]
        r = self.request_client.post("/cluster/create/", data=partial_data)
        self.assertEqual(r.status_code, 400)

    def test_create_cluster_missing_description(self):
        partial_data = config.get_cluster_data()
        del partial_data["description"]
        r = self.request_client.post("/cluster/create/", data=partial_data)
        self.assertEqual(r.status_code, 400)

    def create_cluster(self, user=None):
        user = user if user else self.user
        new_cluster = Cluster(
            name=config.name, description=config.description, admin=user
        )
        new_cluster.save()
        new_cluster.members.add(user)
        new_cluster.save()

        return new_cluster

    def test_edit_cluster_success(self):
        new_cluster = self.create_cluster()
        r = self.request_client.post(
            "/cluster/edit/", data=config.get_edited_cluster_data(new_cluster.id)
        )
        self.assertEqual(r.status_code, 200)

        # check if cluster was indeed edited in db
        clusters = Cluster.objects.all()
        self.assertEqual(len(clusters), 1)
        created_cluster = clusters[0]
        self.assertEqual(created_cluster.name, config.edit_name)
        self.assertEqual(created_cluster.description, config.edit_description)

    def test_edit_cluster_missing_name(self):
        new_cluster = self.create_cluster()
        edited_cluster_data = config.get_edited_cluster_data(new_cluster.id)
        del edited_cluster_data["name"]
        r = self.request_client.post("/cluster/edit/", data=edited_cluster_data)
        self.assertEqual(r.status_code, 400)

    def test_edit_cluster_missing_description(self):
        new_cluster = self.create_cluster()
        edited_cluster_data = config.get_edited_cluster_data(new_cluster.id)
        del edited_cluster_data["description"]
        r = self.request_client.post("/cluster/edit/", data=edited_cluster_data)
        self.assertEqual(r.status_code, 400)

    def test_edit_cluster_missing_id(self):
        new_cluster = self.create_cluster()
        edited_cluster_data = config.get_edited_cluster_data(new_cluster.id)
        del edited_cluster_data["cluster_id"]
        r = self.request_client.post("/cluster/edit/", data=edited_cluster_data)
        self.assertEqual(r.status_code, 400)

    def test_edit_cluster_wrong_id(self):
        new_cluster = self.create_cluster()
        edited_cluster_data = config.get_edited_cluster_data(new_cluster.id)
        edited_cluster_data["cluster_id"] = uuid.uuid4()
        r = self.request_client.post("/cluster/edit/", data=edited_cluster_data)
        self.assertEqual(r.status_code, 403)

    def test_delete_cluster_success(self):
        """Test successful deletion of a cluster"""
        new_cluster = self.create_cluster()
        r = self.request_client.post(
            "/cluster/delete/", data={"cluster_id": new_cluster.id}
        )
        self.assertEqual(r.status_code, 200)

        # check if cluster was indeed deleted from db
        clusters = Cluster.objects.all()
        self.assertEqual(len(clusters), 1)
        deleted_cluster = clusters[0]
        self.assertEqual(deleted_cluster.id, new_cluster.id)
        self.assertTrue(deleted_cluster.deleted)
        self.assertEqual(deleted_cluster.deleted_by, self.user)

    def test_delete_cluster_missing_id(self):
        _ = self.create_cluster()
        r = self.request_client.post("/cluster/delete/")
        self.assertEqual(r.status_code, 400)

    def test_delete_cluster_wrong_id(self):
        _ = self.create_cluster()
        r = self.request_client.post(
            "/cluster/delete/", data={"cluster_id": uuid.uuid4()}
        )
        self.assertEqual(r.status_code, 403)

    def test_leave_cluster_success(self):
        new_cluster = self.create_cluster()
        r = self.request_client.post(
            "/cluster/leave/", data={"cluster_id": new_cluster.id}
        )
        self.assertEqual(r.status_code, 200)

        # check if cluster was indeed deleted from db
        clusters = Cluster.objects.all()
        self.assertEqual(len(clusters), 1)
        left_cluster = clusters[0]
        self.assertEqual(left_cluster.id, new_cluster.id)
        self.assertEqual(len(left_cluster.members.all()), 0)

    def test_leave_cluster_missing_id(self):
        _ = self.create_cluster()
        r = self.request_client.post(
            "/cluster/leave/",
        )
        self.assertEqual(r.status_code, 400)

    def test_leave_clusteer_wrong_id(self):
        _ = self.create_cluster()
        r = self.request_client.post(
            "/cluster/leave/", data={"cluster_id": uuid.uuid4()}
        )
        self.assertEqual(r.status_code, 403)

    def create_user(self):
        user = User.objects.create_user(
            config.username2, config.email2, config.password2
        )
        token, created = Token.objects.get_or_create(user=user)
        return user, token

    def test_join_cluster_success(self):
        new_user, new_token = self.create_user()
        new_cluster = self.create_cluster(new_user)
        r = self.request_client.post(
            "/cluster/join/", data={"cluster_id": new_cluster.id}
        )
        self.assertEqual(r.status_code, 200)

        # check if cluster was indeed deleted from db
        clusters = Cluster.objects.all()
        self.assertEqual(len(clusters), 1)
        left_cluster = clusters[0]
        self.assertEqual(left_cluster.id, new_cluster.id)
        self.assertEqual(len(left_cluster.members.all()), 2)

    def test_join_cluster_missing_id(self):
        new_user, _ = self.create_user()
        _ = self.create_cluster(new_user)
        r = self.request_client.post(
            "/cluster/join/",
        )
        self.assertEqual(r.status_code, 400)

    def test_join_cluster_wrong_id(self):
        new_user, _ = self.create_user()
        _ = self.create_cluster(new_user)
        r = self.request_client.post(
            "/cluster/join/", data={"cluster_id": uuid.uuid4()}
        )
        self.assertEqual(r.status_code, 403)
