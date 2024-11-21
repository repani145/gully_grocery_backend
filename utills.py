from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify

# def hash_password(password):
#     if password:
#         hashed_password = generate_password_hash(password)
#         return hashed_password
#     return "password is not recieved"

# # Endpoint to verify a hashed password
# # @app.route('/verify_password', methods=['GET','POST'])
# def verify_password(password,hashed_password):
#         if password and hashed_password:
#             if check_password_hash(hashed_password, password):
#                 return jsonify({"message": "Password is correct!"}), 200
#             return jsonify({"message": "Incorrect password!"}), 400
#         return jsonify({"error": "Password or hash not provided"}), 400
