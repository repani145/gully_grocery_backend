# from pymongo import MongoClient, ASCENDING
# from pymongo.mongo_client import MongoClient

# # from pymongo import MongoClient
# from urllib.parse import quote_plus

# # Your MongoDB credentials
# username = "all_users"  # Replace with your actual username
# password = "Users@123"  # Replace with your actual password

# # URL-encode the username and password
# encoded_username = quote_plus(username)
# encoded_password = quote_plus(password)

# # Connect to MongoDB
# client = MongoClient(f"mongodb+srv://{encoded_username}:{encoded_password}@gullygrocery.swlbs.mongodb.net/?retryWrites=true&w=majority&appName=GullyGrocery")
# users_db = client['test_users']  # Replace 'mydatabase' with your database name

# # declare collections required
# users_collection = users_db['users']  # Replace 'users' with your collection name
# items_db = client['items']
# orders_db = client['orders']

# #USERS COLLECTIONS
# personal_details_collection = users_db['personal']
# vendor_details_collections = users_db['vendors']

# #ITEMS COLLECTIONS
# dairy = items_db['dairy']
# snaks = items_db['snaks']
# radal = items_db['radal']
# oils = items_db['oils']
# cooldrinks = items_db['cooldrinks']
# cleaning_essencials = items_db['cleaning']

# # ORDERS COLLECTIONS
# orders_collection = orders_db['orders']
# cart_collection = orders_db['cart']

# # Ensure unique indexes are created for username, email and phone_number fields
# users_collection.create_index([("username", ASCENDING)], unique=True)
# users_collection.create_index([("email", ASCENDING)], unique=True)
# users_collection.create_index([("phone_number", ASCENDING)], unique=True)

# vendor_details_collections.create_index([("username", ASCENDING)], unique=True)
# vendor_details_collections.create_index([("email", ASCENDING)], unique=True)
# vendor_details_collections.create_index([("phone_number", ASCENDING)], unique=True)

