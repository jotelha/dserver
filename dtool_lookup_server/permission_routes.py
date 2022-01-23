from flask import (
    abort,
    request,
    jsonify,
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest import Blueprint

from dtool_lookup_server import AuthenticationError
import dtool_lookup_server.utils
from dtool_lookup_server.schemas import BaseUriSchema, UriPermissionSchema

bp = Blueprint("permissions", __name__, url_prefix="/admin/permission")


@bp.route("/info", methods=["POST"])
@bp.arguments(BaseUriSchema)
@jwt_required()
def permission_info(base_uri: BaseUriSchema):
    """Get information about the permissions on a base URI.

    The user needs to be admin.
    """
    username = get_jwt_identity()

    try:
        user = dtool_lookup_server.utils.get_user_obj(username)
    except AuthenticationError:
        # Unregistered users should see 404.
        abort(404)

    # Non admin users should see 404.
    if not user.is_admin:
        abort(404)

    data = request.get_json()
    base_uri = data["base_uri"]

    return jsonify(dtool_lookup_server.utils.get_permission_info(base_uri))


@bp.route("/update_on_base_uri", methods=["POST"])
@bp.arguments(UriPermissionSchema)
@jwt_required()
def update_on_base_uri(permissions: UriPermissionSchema):
    """Update the permissions on a base URI.

    The user needs to be admin.
    """

    username = get_jwt_identity()

    try:
        user = dtool_lookup_server.utils.get_user_obj(username)
    except AuthenticationError:
        # Unregistered users should see 404.
        abort(404)

    # Non admin users should see 404.
    if not user.is_admin:
        abort(404)

    # TODO: is it safe to pass this information straight through without
    #       validation?
    permissions = request.get_json()
    dtool_lookup_server.utils.update_permissions(permissions)

    return "", 201
