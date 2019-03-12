"""Utility functions."""

from sqlalchemy.sql import exists

from dtool_lookup_server import sql_db
from dtool_lookup_server.sql_models import User, BaseURI


#############################################################################
# User helper functions
#############################################################################

def register_users(users):
    """Register a list of users in the system.

    Example input structure::

        [
            {"username": "magic.mirror", "is_admin": True},
            {"username": "snow.white", "is_admin": False},
            {"username": "dopey"},
            {"username": "sleepy"},
        ]

    If a user is already registered in the system it is skipped. To change the
    ``is_admin`` status of an existing user use the
    :func:`dtool_lookup_server.utils.set_user_is_admin`` function.
    """

    for user in users:
        username = user["username"]
        is_admin = user.get("is_admin", False)

        # Skip existing users.
        if sql_db.session.query(
            exists().where(User.username == username)
        ).scalar():
            continue

        user = User(username=username, is_admin=is_admin)
        sql_db.session.add(user)

    sql_db.session.commit()


def list_users():
    """Return list of users."""
    users = []
    for u in User.query.all():
        users.append(u.as_dict())
    return users

def get_user_info(username):
    """Return information about a user as a dictionary.

    Return None if the user does not exist.
    """
    user = User.query.filter_by(username=username).first()

    if user is None:
        return None

    return user.as_dict()


#############################################################################
# Base URI helper functions
#############################################################################

def register_base_uri(base_uri):
    """Register a base URI in the dtool lookup server."""
    base_uri = BaseURI(base_uri=base_uri)
    sql_db.session.add(base_uri)
    sql_db.session.commit()


def list_base_uris():
    """List the base URIs in the dtool lookup server."""
    base_uris = []
    for bu in BaseURI.query.all():
        base_uris.append(bu.as_dict())
    return base_uris


#############################################################################
# Permission helper functions
#############################################################################

def update_all_permissions_on_base_uri(permissions):
    """Rewrite permissions on the base URI."""



#############################################################################
# Dataset helper functions
#############################################################################

def dataset_info_is_valid(dataset_info):
    """Return True if the dataset info is valid."""
    if "uuid" not in dataset_info:
        return False
    if "type" not in dataset_info:
        return False
    if "uri" not in dataset_info:
        return False
    if dataset_info["type"] != "dataset":
        return False
    if len(dataset_info["uuid"]) != 36:
        return False
    return True


def num_datasets(collection):
    """Return the number of datasets in the mongodb collection."""
    return collection.count()


def register_dataset(collection, dataset_info):
    """Register dataset info in the collection.

    If the "uuid" and "uri" are the same as another record in
    the mongodb collection a new record is not created, and
    the UUID is returned.

    Returns None if dataset_info is invalid.
    Returns UUID of dataset otherwise.
    """
    if not dataset_info_is_valid(dataset_info):
        return None

    query = {
        "uuid": dataset_info["uuid"],
        "uri": dataset_info["uri"]
    }

    # If a record with the same UUID and URI exists return the uuid
    # without adding a duplicate record.
    exists = collection.find_one(query)

    if exists is None:
        collection.insert_one(dataset_info)
    else:
        collection.find_one_and_replace(query, dataset_info)

    # The MongoDB client dynamically updates the dataset_info dict
    # with and '_id' key. Remove it.
    if "_id" in dataset_info:
        del dataset_info["_id"]

    return dataset_info["uuid"]


def lookup_datasets(collection, uuid):
    """Return list of dataset info dictionaries with matching uuid."""
    return [i for i in collection.find({"uuid": uuid}, {"_id": False})]


def search_for_datasets(collection, query):
    """Return list of dataset info dictionaries matching the query."""
    return [i for i in collection.find(query, {"_id": False})]