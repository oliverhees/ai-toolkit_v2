from flask import Blueprint
from flasgger import swag_from

v1_toolkit_swagger_test_bp = Blueprint('v1_toolkit_swagger_test', __name__)

swagger_spec = {
    "tags": ["Test"],
    "summary": "Swagger Test Endpoint",
    "description": "Simple test endpoint to verify Swagger works",
    "responses": {
        "200": {
            "description": "Success",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Swagger works!"
                    }
                }
            }
        }
    }
}

@v1_toolkit_swagger_test_bp.route('/v1/toolkit/swagger-test', methods=['GET'])
@swag_from(swagger_spec)
def swagger_test():
    return {"message": "Swagger works!"}, 200
