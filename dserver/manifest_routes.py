"""Route for retrieving the manifest of a dataset"""
from flask import (
    abort,
    jsonify,
    current_app
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from dserver import UnknownURIError
from dserver.blueprint import Blueprint
from dserver.schemas import ManifestSchema
import dserver.utils_auth
from dserver.utils import (
    url_suffix_to_uri,
    get_manifest_from_uri_by_user
)

bp = Blueprint("manifests", __name__, url_prefix="/manifests")

@bp.route("/<path:uri>", methods=["GET"])
@bp.response(200, ManifestSchema)
@bp.alt_response(1, description=2)
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def manifest(uri):
    """Request the dataset manifest."""
    username = get_jwt_identity()
    if not dserver.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    uri = url_suffix_to_uri(uri)
    if not dserver.utils_auth.may_access(username, uri):
        # Authorization errors should return 400.
        abort(403)

    try:
        manifest_ = get_manifest_from_uri_by_user(username, uri)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(404)

    return jsonify(manifest_)


