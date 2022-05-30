username = "testuser"
email = "testuser@example.com"
password = "testpassword"
description = "Test cluster"
name = "Test cluster"
edit_name = "Edited test cluster"
edit_description = "Edited test cluster"
username2 = "testuser2"
password2 = "testpassword2"
email2 = "testuser2@example.com"


def get_cluster_data():
    return {"name": name, "description": description}


def get_edited_cluster_data(cluster_id):
    return {
        "name": edit_name,
        "description": edit_description,
        "cluster_id": cluster_id,
    }
