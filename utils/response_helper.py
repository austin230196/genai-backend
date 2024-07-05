from flask import jsonify, Response


def response(message: str, status: str, status_code: int, data:any=None) -> Response:
    """
        This method is a helper function for returning API response to the user
        @param {str} message: the message to return
        @param {str} status: the status of the response
        @param {any} data: data to be returned with this response

        @return {Response}
    """
    res = {
        "message": message,
        "status": status
    }
    if data != None:
        res["data"] = data
    response = jsonify(res)
    response.status_code = status_code
    return response