from flask import Blueprint

v1_toolkit_swagger_test_bp = Blueprint('v1_toolkit_swagger_test', __name__)

@v1_toolkit_swagger_test_bp.route('/v1/toolkit/swagger-test', methods=['GET'])
def swagger_test():
    """
    Test endpoint for Swagger
    ---
    tags:
      - Test
    summary: Swagger Test Endpoint
    description: Simple test endpoint to verify Swagger docstring parsing
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Swagger works!"
    """
    return {"message": "Swagger works!"}, 200
