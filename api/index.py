from flask import Flask, jsonify, request,render_template, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import db_utills as DB
# from marshmallow import ValidationError
import validators
from datetime import datetime,timedelta
import pymongo
from bson import ObjectId
from flask.json.provider import DefaultJSONProvider
import models
from mongoengine.errors import NotUniqueError
from pymongo.errors import DuplicateKeyError
import ast,time
from flask_principal import Principal, Permission, RoleNeed
from urllib.parse import quote_plus
from flask_cors import CORS,cross_origin

#######
from flask import Flask, request, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import os 
###############

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "gullyygroceryy@gmail.com"
SENDER_PASSWORD = "bzhj kmux nwny qxpv"
RECEIVER_EMAIL = "gullyygroceryy@gmail.com"

import smtplib
import random

class MongoJSONEncoder(DefaultJSONProvider):  #To conver the every ObjectId into str automatically
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MongoJSONEncoder, self).default(obj)

app=Flask(__name__)
# Configure CORS to allow your frontend origin
CORS(app, resources={r"*": {"origins": "*"}})

app.json = MongoJSONEncoder(app)  # Set the custom JSON provider
principals = Principal(app)

########image
# Define the upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  #######################################====================

CATEGORIES = 'static/shop_images'
if not os.path.exists(CATEGORIES):
    os.makedirs(CATEGORIES)

SINGLEITEM = 'static/item_images'
if not os.path.exists(SINGLEITEM):
    os.makedirs(SINGLEITEM)


admin_permission = Permission(RoleNeed('admin'))
vendor_permission = Permission(RoleNeed('vendor'))
user_permission = Permission(RoleNeed('user'))


secret_key = "78cbd8686b67b6e077fc1638ce74e8c7204e911e5d9f6481bad8b3eac5dc111e99d3e142fd65386e8ef5a2ed195dfade3c006c6d2ed5ae41bcf7bd89d5d68d92f9aa014589d3dc03b18ea81605ef7e147af34ec8f09ebb2b663fa5d81b9b6e3a6ae76e6c79cb22379fffcd72bd7e0d8cff0406e219e220cdb51032f63e42b5d5b45705833d37fdeef1998e3049440e59da92d5f5db3fc857ac3f0d6be1aab484a8cc376d1ef71c0f1bef97685cb748f5793237ba962d68a0fec8f16130bba052d589011a8b04de1ed689ddaf92176839732ee452862d6234a96a7726495affe619a1294cd532ad7949809aa7058b10c9f9127e1c8818f8d751e91e7620b14f48"
app.config['JWT_SECRET_KEY'] = secret_key  # Change this to a more secure key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60) 
jwt = JWTManager(app)

all_categories=["dairy","snaks","rice","dal","atta","oils","cooldrinks","cleaning"]

@app.route('/',methods=['GET'])
def one():
    return "Welcome to Gully Grocery !"

@app.route('/user_signup',methods=['POST','PUT'])
def user_signup():
    if request.method == 'POST':
        context = {
        "data":{},
        "success":1,
        "message":"registered successfully!"
        }
        json_data = request.get_json()
        try:
            data = validators.user_schema.load(json_data)
            if not data:
                raise ValidationError("data is not validated properly! ")
            context['data']=validators.user_schema.dump(data)
            context['data']['password']=generate_password_hash(context['data']['password'])

            user = models.Users(**context['data'])
            user.save()
            # DB.users_collection.insert_one(context['data'])
            context['data']['_id']=str(user.id)
        except NotUniqueError as e:
            a=(str(e)[str(e).find("full error"):-1])
            x=a.find('full error: ')+(len('full error: ')-1)
            dict_obj = ast.literal_eval(a[x:])
            for i in dict_obj['keyValue']:
                err = f"user existed with {i} : {dict_obj['keyValue'][i]}"
            context['data']={}
            context['message']=err
            context['success']=0   
        except Exception as e:
            context['success']=0
            context['data']={}
            context['message']=str(e)
        return jsonify(context)
    
@app.route('/user_data',methods=['GET','PUT'])
@jwt_required()
def user_data():
    if request.method=='GET':
        context = {
        "data":{},
        "success":1,
        "message":"data found successfully!"
        }
        jwt_data = get_jwt_identity()
        id = jwt_data.get('user_id')
        try:
            user = models.Users.objects.get(id=id)
            data = {}
            for i in user:
                data[i]=user[i]
            del data['created_at']
            del data['updated_at']
            del data['dob']
            # print("user = >>>>>",data)
            context['data']=data
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return context
    
    elif request.method == 'PUT':
        context = {
            "data": {},
            "success": 1,
            "message": "Profile updated successfully!"
        }
        json_data = request.get_json()
        try:
            # Extract the user ID and email from the request
            user_id = json_data.get('id')
            email = json_data.get('email')

            if not user_id or not email:
                raise Exception("User ID and email are required.")

            # Find the user in the database
            user = models.Users.objects(id=user_id).first()
            if not user:
                raise Exception("User not found.")

            # # Verify the email before updating
            # if user['email'] != email:
            #     raise Exception("Email verification failed.")

            # Update the user's data (excluding protected fields like email)
            update_fields = {k: v for k, v in json_data.items()}
            user.update(**update_fields,updated_at=datetime.now())
            user.reload()

            context['data'] = {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "address": user.address,
                "landmark": user.landmark,
                "dob": user.dob,
                "role": user.role
            }
        except Exception as ve:
            context['success'] = 0
            context['message'] = str(ve)
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return jsonify(context)


@app.route('/vendor_signup',methods=['POST'])  #ok
def vendor_signup():
    context = {
        "data":{},
        "success":1,
        "message":"registered successfully!"
    }
    shop_name = request.form.get('shop_name')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    username = request.form.get('username')
    password = request.form.get('password')
    address = request.form.get('address')
    landmark = request.form.get('landmark')
    json_data = {"shop_name":shop_name,"email":email,"phone_number":phone_number,"username":username,"password":password,"address":address,"landmark":landmark}
    # print(request.files)
    try:
        if 'image' not in request.files:
            raise Exception("shop image is required")
        file = request.files['image']
        if file.filename == '':
            raise Exception("No selected file")
        
        # json_data = validators.vendor_schema.load(json_data)
        if not json_data:
            raise DuplicateKeyError("data is not validated properly! ")
        user_name = json_data['username']
        context['data']=validators.vendor_schema.dump(json_data)
        context['data']['password']=generate_password_hash(context['data']['password'])
        if file:
            filename = secure_filename(user_name)
            file_path = os.path.join('static/shop_images', filename+file.filename[file.filename.rfind('.'):])
        # print(context['data'],file_path)
        vendor = models.Vendors(**context['data'],image_path = filename)
        vendor.save()
        file.save(file_path)
        context['data']['_id']=str(vendor.id)         
    except NotUniqueError as e:
        a=(str(e)[str(e).find("full error"):-1])
        x=a.find('full error: ')+(len('full error: ')-1)
        dict_obj = ast.literal_eval(a[x:])
        for i in dict_obj['keyValue']:
            err = f"user existed with {i} : {dict_obj['keyValue'][i]}"
        context['data']={}
        context['message']=err
        context['success']=0    
    except Exception as e:
        context['success']=0
        context['data']={}
        context['message']=str(e)
    return jsonify(context)

@app.route('/user_login', methods=['POST'])    #ok
def user_login():
    context = {
        "success":1,
        "message":"logged in successfully!",
        "data":{}
    }
    json_data = request.get_json()
    try:
        data = validators.login_schema.load(json_data)
        username = data.get('username')
        password = data.get('password')
        user = models.Users.objects.filter(username=username).first().to_mongo().to_dict()
        if not user:
            raise Exception("no user found with given details")
        if user['username']:
            if check_password_hash(user.get("password"),password):
                access_token = create_access_token(identity={"username":username,"role":user.get('role'),"user_id":str(user.get('_id'))})
                # print('##########$$$$$$$$$$$',{"username":username,"role":user.get('role'),"user_id":str(user.get('_id'))})
                idd=str(user.get("_id"))
                # del user['_id']
                del user['password']
                context['data']={**user,"_id":idd}
                
                return jsonify({**context,"accessToken":access_token})
            else:
                context['message']="please enter correct password"
                context['success']=0
        else:
            msg = f"no user existed with {username}"
            context['message']=msg
            context['success']=0
            pass # user not found
    except Exception as e:
        context['message']=str(e)
        context['success']=0
    return context

@app.route('/login', methods=['POST'])    #ok
def login():
    context = {
        "success":1,
        "message":"logged in successfully!",
        "data":{}
    }
    json_data = request.get_json()
    try:
        data = validators.login_schema.load(json_data)
        username = data.get('username')
        password = data.get('password')
        try:
            user = models.Vendors.objects.filter(username=username).first()
            if user == None:
                try:
                    user = models.Users.objects.filter(username=username).first()
                finally:
                    if user == None:
                        raise Exception('user not found')
        finally:
                if user == None:
                    raise Exception('user not found')
        user = user.to_mongo().to_dict()
        role = user['role']
        if user['username']:
            if check_password_hash(user.get("password"),password):
                # access_token = create_access_token(identity=username)
                idd=str(user.get("_id"))
                del user['_id']
                del user['password']
                if role=='user':
                    access_token = create_access_token(identity={"username": username, "role": user.get('role'),"user_id":idd})
                else:
                    access_token = create_access_token(identity={"username": username, "role": user.get('role'),"shop_id":idd})
                context['data']={**user,"_id":idd}
                # access_token = create_access_token(identity={**context['data']})
                # print('############################# role =',{"username": username, "role": user.get('role'),"shop_id":idd})
                return jsonify({"accessToken":access_token,**context})
                # context['data']={**user,"_id":idd,"access_token":access_token}
            else:
                context['message']="please enter correct password"
                context['success']=0
        else:
            msg = f"no user existed with {username}"
            context['message']=msg
            context['success']=0
            pass # user not found
    except Exception as e:
        context['message']=str(e)
        context['success']=0
    return context




@app.route('/add_item', methods=['POST'])                            # TTT
@jwt_required()  
def add_item():
    context = {
        "success": 1,
        "message": "Item added successfully",
        "data": {}
    }
    
    current_user = get_jwt_identity()
    user_role = current_user['role']

    # Ensure only 'vendor' role can add items
    if user_role != 'vendor':
        context['message'] = "No permission to add item"
        context['success'] = 0
        return jsonify(context)
    
    # Extract form data and file
    try:
        item_name = request.form.get('item_name')
        quantity = int(request.form.get('quantity'))
        price = int(request.form.get('price'))
        stock = int(request.form.get('stock'))
        category = request.form.get('category')

        # Validate if image file is included in the form
        if 'image' not in request.files:
            raise Exception("No file part")
        
        file = request.files['image']
        
        if file.filename == '':
            raise Exception("No selected file")
        
        # Save the image file locally
        if file:
            # Ensure the file is saved with a secure filename
            filename = secure_filename(file.filename)
            image_path = os.path.join(SINGLEITEM, filename).replace("\\", "/")
            file.save(image_path)

        # Ensure category exists
        all_categories = models.Category.objects.filter(category_name=category)
        if not len(all_categories):
            raise Exception(f"{category} is not defined")

        # Create the new item in the database
        item = models.AllItems(
            item_name=item_name,
            quantity=quantity,
            price=price,
            stock=stock,
            category=category,
            shop_id=current_user['shop_id'],
            image=file.filename  # Save the image filename in the database
        )
        item.save()

        # Add the item ID to the response data
        context['data'] = {
            '_id': str(item.id),
            'item_name': item_name,
            'quantity': quantity,
            'price': price,
            'stock': stock,
            'category': category,
            "image":url_for('static', filename=f"item_images/{filename}", _external=True)
        }

    except Exception as e:
        context['success'] = 0
        context['message'] = str(e)

    return jsonify(context)

@app.route('/single_item/<item_id>',methods=['DELETE','PATCH'])      # TTT
@jwt_required()
def remove_item(item_id):
    current_user = get_jwt_identity()
    shop_id = current_user.get('shop_id')
    # print("shop_id",shop_id)
    if request.method == 'DELETE':
        context = {
            "data":{},
            "message":"item removed successfully",
            "success":1
        }
        try:
            data = models.AllItems.objects.filter(shop_id=shop_id,id=item_id).first()
            if data == None:
                raise Exception('item not found to remove')
            context['data']=data.to_mongo().to_dict()
            data.delete()
            data.save()
            # print(f'######################################### all {item_id} is removes from shop : {shop_id}')
            # print(all_items)
            # print()
            
        except Exception as e:
            context['success']=0
            context['message']=str(e)

    elif request.method == 'PATCH':
        context = {
            "data": {},
            "message": "item data updated successfully",
            "success": 1
        }
        try:
            # Get form data
            item_name = request.form.get('item_name')
            price = request.form.get('price')
            stock = request.form.get('stock')
            quantity = request.form.get('quantity')
            category = request.form.get('category')
            file = request.files.get('image')  # File field

            # Get the existing item data
            old_data = models.AllItems.objects.filter(id=item_id, shop_id=shop_id).first()
            if old_data is None:
                raise Exception('old data not found')

            # Update fields that have been changed
            if item_name:
                old_data.item_name = item_name
            if price:
                old_data.price = float(price)
            if stock:
                old_data.stock = int(stock)
            if quantity:
                old_data.quantity = int(quantity)
            if category:
                old_data.category = category

            # Save the image file locally
            if file:
                # Ensure the file is saved with a secure filename
                filename = secure_filename(file.filename)
                image_path = os.path.join(SINGLEITEM, filename).replace("\\", "/")
                file.save(image_path)
                # Update the image path in the database
                old_data.image = filename

            # Save the updated data
            old_data.save()
            context['data'] = {**old_data.to_mongo().to_dict(),
             "image":url_for('static', filename=f"item_images/{filename}", _external=True)
                               }

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

    return context

@app.route('/single_type/<item_type>',methods=['GET'])               # TTT
@jwt_required()
def all_category_items(item_type):
    context = {
        "data":[],
        "message":"data fount successfully",
        "success":1
    }
    current_user = get_jwt_identity()
    shop_id = current_user.get('shop_id')
    # print("shop_id",shop_id)
    try:
        data = models.AllItems.objects.filter(category=item_type)
        if data == None:
            raise Exception(f'no items found in {item_type}')
        all_items = []
        for item in data:
            all_items.append({**item.to_mongo().to_dict(),
                              "image":url_for('static', filename=f"item_images/{item.to_mongo().to_dict()['image']}", _external=True)
                              })
        # print(f'######################################### all {item_type} items {len(all_items)} found in {shop_id} shop ')
        # print(all_items)
        print()
        context['data']=all_items
    except Exception as e:
        context['success']=0
        context['message']=str(e)
    return context



@app.route('/vendor_single_type/<item_type>',methods=['GET','POST'])     
@jwt_required()
def single_cat_with_vendor(item_type):
    context = {
        "data":[],
        "message":"data fount successfully",
        "success":1
    }
    if request.method == 'GET':
        current_vendor = get_jwt_identity()
        shop_id = current_vendor.get('shop_id')
    if request.method=='POST':
        json_data = request.get_json()
        shop_id = json_data.get('shop_id')
        
    # print("shop_id",shop_id)
    try:
        data = models.AllItems.objects.filter(category=item_type,shop_id=shop_id)
        if data == None:
            raise Exception(f'no items found in {item_type}')
        all_items = []
        for item in data:
            all_items.append({**item.to_mongo().to_dict(),
                            "image":url_for('static', filename=f"item_images/{item.to_mongo().to_dict()['image']}", _external=True)
                            })
        # print(f'######################################### all {item_type} items {len(all_items)} found in {shop_id} shop ')
        # print(all_items)
        print()
        context['data']=all_items
    except Exception as e:
        context['success']=0
        context['message']=str(e)
    return context

    
        



@app.route('/add_to_cart',methods=['POST'])  #ok
@jwt_required()
def add_to_cart():
    context={
        "success":1,
        "message":"item added successfully",
        "data":{}
    }
    current_user = get_jwt_identity()
    # print('################################## current user ',current_user)
    user_role = current_user['role']
    user_id = current_user['user_id']
    if user_role != 'user':
        context['message']="no permission to add item"
        context['success']=0
        return context
    json_data = request.get_json()
    try:
        data = validators.add_to_cart_schema.load(json_data)
        # DB.cart_collection.insert_one(data)
        item = models.Cart(**data,user_id=user_id)
        item.save()
        data['_id']=str(item.id)
        context['data']=data
    except Exception as e:
        context['success']=0
        context['message']=str(e)
    return context



@app.route('/cart',methods=['GET'])  # ok
@jwt_required()
def cart():
    context={
        "success":1,
        "message":"cart items found successfully",
        "data":{}
    }
    current_user = get_jwt_identity()
    # print('####################################',current_user)
    user_role = current_user['role']
    if user_role != 'user':
        context['message']="no permission to see cart"
        context['success']=0
        return context
  
    if request.method == 'GET':
        try:
            # user_id = json_data.get('user_id')
            # print('####################################',current_user)
            data = models.Cart.objects.filter(user_id=current_user['user_id'])
            data = [item.to_mongo().to_dict() for item in data]
            # print(data)
            if len(data)==0:
                raise Exception(" cart is empty ")
            else:
                cart_array = []
                id_array=[]
                for obj in data:
                    # print('###############iterating the cart items',obj)
                    # time.sleep(2)
                    # single_item = DB.items_db[obj.get("category")].find_one({'_id': ObjectId(obj.get("item_id"))}) #ObjectId is return the document
                    single_item = models.Cart.objects.filter(item_id=obj.get("item_id")).first().to_mongo().to_dict()
                    # print(single_item)
                    if not single_item:
                        # print('none')
                        # time.sleep(2)
                        pass
                    else:
                        # print('###################got single item from Cart with item_id',obj.get("item_id"))
                        # time.sleep(2)
                        item_id = obj.get("item_id")
                        item_dict = models.AllItems.objects.filter(id=item_id)[0].to_mongo().to_dict()
                        if item_id not in id_array:
                            # print('#############>>>>>> got new item_id adding to cart_array')
                            # time.sleep(2)
                            id_array.append(item_id)
                            single_item['count']=1
                            del single_item['item_id']
                            cart_array.append({**single_item,"item_data":item_dict})
                        else:
                            # print('                    ######>>>>> got existing item_id updating in cart_array')
                            # time.sleep(2)
                            pre_count = id_array.count(item_id)
                            # print(item_id,"pre_count =>",pre_count)
                            del single_item['item_id']
                            # print()
                            # print()
                            # print({**single_item,"item_data":item_dict,"count":pre_count})
                            # print(cart_array)
                            # print()
                            # print()
                            cart_array.remove({**single_item,"item_data":item_dict,"count":pre_count})
                            single_item['count']=pre_count+1
                            cart_array.append({**single_item,"item_data":item_dict})
                            id_array.append(item_id)
                            # print(item_id,'after count= >',single_item['count'])
                    # print('latest cart array ========******',cart_array)
            context['data']=cart_array
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return context
    
    # elif request.method == 'PATCH':
    #     '''
    #     TO REMOVE THE CART ITEMS
    #     input required is:
    #         {
    #         "user_id":"67167c3d8b29326aaff1a73b",
    #         "item_id":"67186607c1df5f0274ce1b37"
    #         }
    #     '''
    #     context={
    #     "success":1,
    #     "message":"item removed from cart ",
    #     "data":{}
    #     }
    #     try:
    #         print(json_data.get('item_id'))
    #         item  = models.Cart.objects.filter(item_id=json_data.get('item_id')).first()
    #         if item==None:
    #             raise Exception(' cart is empty !')
    #         print(item)
    #         item.delete()
    #         item.save()
    #     except Exception as e:
    #         context['success']=0
    #         context['message']=str(e)
    #     return context
        

@app.route('/clear_cart',methods=["DELETE"])
@jwt_required()
def clear_cart():
    context={
        "success":1,
        "message":"items removed from cart ",
        "data":{}
        }
    current_user = get_jwt_identity()
    # print('####################################',current_user)
    user_role = current_user['role']
    if user_role != 'user':
        context['message']="no permission to see cart"
        context['success']=0
        return context
    try:
        # print('#####################',current_user.get('user_id'))
        items = models.Cart.objects.filter(user_id=current_user.get('user_id'))
        if items==None or len(items)==0:
            raise Exception(' cart is empty !')
        # print(items)
        items.delete()
        # items.save()
    except Exception as e:
        context['success']=0
        context['message']=str(e)
    return context


@app.route('/add_one_del/<id>',methods=['PATCH','DELETE'])
@jwt_required()
def add_one_del(id):
    current_user = get_jwt_identity()
    # print('####################################',current_user)
    user_role = current_user['role']
    if user_role != 'user':
         raise Exception('no permission to see Cart ')    
    # json_data = request.get_json()
    # print("################################json_data => ",json_data)
    if request.method == 'DELETE':
        context={
        "success":1,
        "message":"item removes from cart ",
        "data":{}
        }
        try:
            # print('for deleteing the one item =======>>> ',id)
            item  = models.Cart.objects.filter(item_id=id).first()
            # print(item)
            # print("################################ id  item => ",item.to_mongo().to_dict())
            if item == None:
                raise Exception('item not found to remove from cart')
            if item==None:
                raise Exception(' cart is empty !')
            # print(item)
            item.delete()
            # item.save()
        except Exception as e:
            context['success']=0
            context['message']=str(e)

    if request.method == 'PATCH': # add one more item(item_id from all items and add in cart)
        context={
        "success":1,
        "message":"one item added to cart ",
        "data":{}
        }
        try:
            # print(json_data.get('id'),current_user.get('user_id'))
            # PASS ITEM_ID FROM CART
            item = models.AllItems.objects(id=id).first() #(item_id)in cart is    (id) in AllItems
            if item == None:
                raise Exception('item not found')
            if item==None:
                raise Exception(' item not available choose another !')
            cart_item  = models.Cart(item_id=id,user_id=current_user.get('user_id'))
            cart_item.save()
            # item.save()
        except Exception as e:
            context['success']=0
            context['message']=str(e)
    return context

@app.route('/remove_cart_item/<item_id>',methods=['DELETE'])
@jwt_required()
def remove_cart_item(item_id):
    context={
    "success":1,
    "message":"item removes from cart ",
    "data":{}
    }
    try:
        # print('for deleteing the one item =======>>> ',item_id)
        items  = models.Cart.objects.filter(item_id=item_id)
        # print(items)
        # print("################################ id  items => ",items)
        if items == None:
            raise Exception('items not found to remove from cart')
        if items==None:
            raise Exception(' cart is empty !')
        # print(items)
        items.delete()
        # item.save()
    except Exception as e:
        context['success']=0
        context['message']=str(e)
    return context


@app.route('/all_item_types',methods=['GET'])
@jwt_required()
def all_items():
    context = {
        "data":[],
        "message":"data fount successfully",
        "success":1
    }
    try:
        context['data']=all_categories
    except Exception as e:
        context['success']=0
        context['message']=str(e)
    return context


@app.route('/all_shops',methods=['GET'])
# @jwt_required()
def all_shops():
    context = {
        "data":[],
        "message":"data found successfully",
        "success":1
    }
    try:
        # context['data']=models.Vendors.objects.filter()
        shops = []
        for obj in models.Vendors.objects.filter():
            shop = {}
            shop['id']=str(obj['id'])
            shop['shop_name']=obj['shop_name']
            shop['image']=url_for('static', filename=f"shop_images/{obj['image_path']}", _external=True)
            # print(obj.to_mongo().to_dict())
            shops.append(shop)
        context['data']=shops
    except Exception as e:
        context['success']=0
        context['message']=str(e)
    return context


@app.route('/payment',methods=['POST'])
@jwt_required()
def add_payment():
    context = {
        'data':{},
        "success":1,
        "message":"payment deatils added successfully"
    }
    current_user = get_jwt_identity()
    # print("current_user= ",current_user)
    json_data = request.get_json()
    # print("json_data = ",json_data)
    try:
        user = models.Users.objects.get(id=current_user['user_id'])
        pay = models.Payment(user=user,**json_data)
        pay.save()
        cart_instance = models.Cart.objects(user_id=current_user['user_id'])
        # list_of_cart_items = [models.AllItems.objects.get(id=obj['item_id']) for obj in cart_instance]
        list_of_cart_items =[]
        shop_ids = []
        vendor_orders = {}
        for obj in cart_instance:
            item = models.AllItems.objects.get(id=obj['item_id'])
            list_of_cart_items.append(item)
            if item['shop_id'] not in shop_ids:
                shop_ids.append(item['shop_id'])
                vendor_orders[item['shop_id']] = {'shop_id':item['shop_id']}
                vendor_orders[item['shop_id']]['products']=[item]
                vendor_orders[item['shop_id']]['amount']=item['price']
                vendor_orders[item['shop_id']]['user'] = user
            else:
                vendor_orders[item['shop_id']]['products'].append(item)
                vendor_orders[item['shop_id']]['amount']=vendor_orders[item['shop_id']]['amount']+item['price']
        #adding to orders
        order = models.Order(user=user,payment=pay,total_amount = json_data['amount'],products = list_of_cart_items)
        order.save()

        # add orders to vendor orders
        for sID in vendor_orders:
            v_order = models.VendorOrders(order=order['id'],**vendor_orders[sID])
            v_order.save()
            # print(f'################## ordre saved for vendor {sID}')

        cart_instance.delete()
        context['data']=pay.to_mongo().to_dict()
    except Exception as e:
        context['success']=0
        context['message']=str(e)
    return context


@app.route('/my-orders',methods=['GET'])
@jwt_required()
def my_orders():
    context = {
        "data":[],
        "message":"data found successfully",
        "success":1
    }
    user = get_jwt_identity()
    try:
        data = models.Order.objects.filter(user=user['user_id'])
        orders_array = []
        for i in data:
            new_obj = {}
            obj = i.to_mongo().to_dict()
            new_obj['id'] = obj['payment']
            new_obj['date'] = obj['order_date']
            new_obj['status'] = obj['status']
            new_obj['total'] = obj['total_amount']
            orders_array.append(new_obj)
        context['data']=orders_array
    except Exception as e:
        context['message']=str(e)
        context['success']=0
    return context


@app.route('/categories', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def categories():
    if request.method == 'GET':
        context = {
            'data':[],
            'message':"data found successfully",
            "success":1
        }
        try:
            # Retrieve all categories
            categories = models.Category.objects()  
            context['data']=[ 
                             {
                                 "id":category['id'],
                                "category_name" :category['category_name'],
                                "image":url_for('static', filename=f"shop_images/{category['image']}", _external=True)
                             }
                             for category in categories]
        except Exception as e:
            context['message']=str(e)
            context['success']=0
        return context

    elif request.method == 'POST':
        context = {
            'data':[],
            'message':"data saved successfully",
            "success":1
        }
        try:
            if 'image' not in request.files:
                raise Exception("No file part")
            file = request.files['image']
            # Validate if the file is selected
            if file.filename == '':
                raise Exception("No selected file")
            if file:
                # Save the file locally
                image_path = os.path.join(CATEGORIES, file.filename).replace("\\", "/")
                file.save(image_path)

                # Create a new category with the image path
                new_category = models.Category(category_name=request.form['category_name'], image=file.filename)
                new_category.save()  # Save to MongoDB
                context['data']={
                                "id":new_category['id'],
                                "category_name" :new_category['category_name'],
                                "image":url_for('static', filename=f"shop_images/{new_category['image']}", _external=True)
                             }
                return context
        except Exception as e:
            context['message']=str(e)
            context['success']=0

    elif request.method == 'DELETE':
        context = {
            'data':[],
            'message':"data updated successfully",
            "success":1
        }
        data = request.get_json()
        # print('===============================>>>>>>>>',data['id'])
        try:
            category = models.Category.objects(id=data['id']).first()  # Retrieve the category by id
            if category:
                raise Exception('no item found')
            category.delete()  # Save the updated category
            return context
        except Exception as e:
            context['message']=str(e)
            context['success']=0

@app.route('/delete-cat/<string:id>',methods=['DELETE'])
@jwt_required()
def delete_cat(id):
    context = {
            'data':[],
            'message':"data deleted successfully",
            "success":1
        }
    # print('===============================>>>>>>>>',id)
    try:
        category = models.Category.objects(id=id).first()  # Retrieve the category by id
        if not category:
            raise Exception('no item found')
        # Get the image path from the category document
        image_path = category["image"]
        
        # Delete the category from the database
        category.delete()
        
        # Now delete the image file from the filesystem if it exists
        if image_path and os.path.exists(f"{CATEGORIES}/{image_path}"):
            os.remove(f"{CATEGORIES}/{image_path}")
        return context
    except Exception as e:
        context['message']=str(e)
        context['success']=0
    return context


@app.route('/search', methods=['GET'])
@jwt_required()
def search_items():
    query = request.args.get('query', '')
    if len(query) >= 2:  # Trigger search only if query length is 2 or more characters
        results = models.AllItems.objects(item_name__icontains=query)[:10]  # Limit results for performance
        items = [{
            "id": str(item.id), 
            "name": item.item_name,
            "image":url_for('static', filename=f"item_images/{item.image}", _external=True),
            "price":item.price,
            "quantity":item.quantity
            } for item in results]
        return jsonify(items)
    return jsonify([])



@app.route('/contact_us', methods=['POST'])
def submit_form():
    context={
        'success':1,
        'message':"request send successfully",
        'data':{}
    }
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not name or not email or not message:
            if not name:
                context['message']='name is required field'
            if not email:
                context['message']='email is required field'
            if not message:
                context['message']='message is required field'
            context['success']=0
            # return jsonify({'error': 'All fields are required'}), 400

        # Email content
        email_subject = "New Contact Form Submission"
        email_body = f"Name: {name}\nEmail: {email}\nMessage: {message}"

        # Sending email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Start secure connection
            server.login(SENDER_EMAIL, SENDER_PASSWORD)  # Login to sender email
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, f"Subject: {email_subject}\n\n{email_body}")

        return jsonify({'message': 'Your message was successfully sent!'}), 200

    except Exception as e:
        return jsonify({'error': f"An error occurred: {e}"}), 500






@app.route('/send-otp', methods=['POST'])
def send_otp():
    context={
        'success':1,
        "message":"otp send successfully",
        "data":{}
    }
    try:
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        user = models.Users.objects.filter(email=email).first()
        vendor = models.Vendors.objects.filter(email=email).first()
        if user or vendor:
            context['message'] = 'email is already in use'
            context['success'] = 0
        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)
        dataa = models.OTP_REG.objects.filter(email=email).first()

        #check weather email is listed or not
        if not dataa:
            dataa = models.OTP_REG(email=email,otp=otp,otp_time=datetime.now())
        else:
            dataa['otp']=otp
            dataa['otp_time']=datetime.now()
        # Email content
        email_subject = "Gully Grocery verify OTP"
        email_body = f"VERIFY your gully grocery\nEmail: {email}\nOTP is: {otp}"

        RECEIVER_EMAIL = email

        # Sending email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Start secure connection
            server.login(SENDER_EMAIL, SENDER_PASSWORD)  # Login to sender email
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, f"Subject: {email_subject}\n\n{email_body}")

        # context['data']=otp
        dataa.save()
    except Exception as e:
        context['success']=0
        context['message']=str(e)
    return context


@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    context={
        'success':1,
        "message":"otp verified successfully",
        "data":{}
    }
    try:
        data = request.json
        email = data.get('email')
        otp = data.get('otp')

        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400

        stored_data = models.OTP_REG.objects.filter(email=email).first()
        # print("stored_data  = ",stored_data['otp'])

        if not stored_data:
            context['success']=0
            context['message']='OTP not found for this email'
        # print('===========>>>>>>>>>',stored_data['otp'] == int(otp) and (datetime.now() - stored_data['otp_time']).total_seconds() <= 300)
        # Check if OTP matches and is within the valid timeframe (5 minutes)
        if stored_data['otp'] == int(otp) and (datetime.now() - stored_data['otp_time']).total_seconds() <= 300:
            context['message'] = 'OTP verified successfully!'
            stored_data['otp']=0
            stored_data.save()
        else:
            context['message']='Invalid or Expired OTP'
            context['success']=0
    except Exception as e:
        context['success']=0
        context['message']='Invalid or Expired OTP'
    return context

@app.route('/verfy-email', methods=['POST'])
def verify_email():
    context={
        'success':1,
        "message":"otp send successfully",
        "data":{}
    }
    try:
        data = request.json
        email = data.get('email')

        if not email:
            raise Exception('Email is required')

        user = models.Users.objects.filter(email=email).first()
        vendor = models.Vendors.objects.filter(email=email).first()
        if not user or not vendor:
            context['message'] = 'email is not existed'
            context['success'] = 0
        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)
        dataa = models.OTP_REG.objects.filter(email=email).first()

        #check weather email is listed or not
        if not dataa:
            dataa = models.OTP_REG(email=email,otp=otp,otp_time=datetime.now())
        else:
            dataa['otp']=otp
            dataa['otp_time']=datetime.now()
        # Email content
        email_subject = "Gully Grocery verify OTP"
        email_body = f"VERIFY your gully grocery\nEmail: {email}\nOTP is: {otp}"

        RECEIVER_EMAIL = email

        # Sending email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Start secure connection
            server.login(SENDER_EMAIL, SENDER_PASSWORD)  # Login to sender email
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, f"Subject: {email_subject}\n\n{email_body}")

        # context['data']=otp
        dataa.save()
    except Exception as e:
        context['success']=0
        context['message']=str(e)
    return context


if __name__ == "__main__":
    if not os.path.exists('static/shop_images'):
        os.makedirs('static/shop_images')
    app.run(host='0.0.0.0', port=5000, debug=True)
