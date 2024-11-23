from flask import Flask, jsonify, request
from mongoengine import ValidationError,disconnect,errors,Document,EmailField, StringField,DateField,DecimalField,DateTimeField,IntField,BooleanField,ObjectIdField,ReferenceField, connect,ListField
from datetime import datetime
# Connect to MongoDB
# connect('example_db')  # Replace with your database name
# from pymongo import MongoClient
from urllib.parse import quote_plus


# Your MongoDB credentials
username = "all_users"  # Replace with your actual username
password = "Users@123"  # Replace with your actual password

# URL-encode the username and password
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)
connect(
    db='gullygrocery',
    host = f"mongodb+srv://{encoded_username}:{encoded_password}@gullygrocery.swlbs.mongodb.net/?retryWrites=true&w=majority&tls=true"
    # host=f"mongodb+srv://{encoded_username}:{encoded_password}@gullygrocery.swlbs.mongodb.net/?retryWrites=true&w=majority&appName=GullyGrocery"
)



#Models
class CommonModel(Document):
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())
    meta = {
        'allow_inheritance': True,  # Allow subclassing,
        'abstract': True  # Make this model abstract
    }
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()  # Set only on first save
        self.updated_at = datetime.now()  # Update on every save
        return super(CommonModel, self).save(*args, **kwargs)

class Users(CommonModel):
    username = StringField(required=True, unique=True,null=False)
    full_name = StringField(required=True,null=False)
    dob = DateField(required=True,null=False)
    email = EmailField(required=True,null=False,unique=True)
    phone_number = StringField(required=True,null=False,unique=True)
    address = StringField(required=True,null=False)
    landmark = StringField(null=False)
    role = StringField(default = 'user')
    # user_type = StringField(default="user")
    password=StringField(required=True,null=False)

class Vendors(CommonModel):
    username=StringField(required=True, unique=True,null=False)
    shop_name = StringField(required=True,null=False)
    email = EmailField(required=True,null=False,unique=True)
    phone_number = StringField(required=True,null=False,unique=True)
    address = StringField(required=True,null=False)
    landmark = StringField(null=False)
    role = StringField(default = 'vendor')
    image_path = StringField(required = True,null=False)
    # user_type = StringField(default="vendor")
    password=StringField(required=True,null=False)

class LoginHistory(CommonModel):
    username=StringField(required=True, unique=True,null=False)

class AllItems(Document):
    shop_id = StringField(required=True,null=False)
    item_name = StringField(required=True,null=False)
    image = StringField(required=True,null=False)
    quantity = IntField(required=True)
    price = IntField(required=True)
    stock = IntField(required=True)
    category = StringField(required=True,null=False)


class Cart(Document):
    user_id = StringField(required=True,null=False)
    # category = StringField(required=True,null=False)
    item_id = StringField(required=True,null=False)


class Payment(Document):
    user = ReferenceField(Users, required=True)  # Reference to User model
    payment_intent_id = StringField(required=True, unique=True)  # Unique payment intent ID
    amount = DecimalField(required=True, precision=2)  # Total amount paid
    status = StringField(required=True)  # Payment status
    payment_method_id = StringField(required=True)  # Payment method ID
    created_at = DateTimeField(default=datetime.now())  # Payment creation timestamp

    def __str__(self):
        return f"Payment {self.payment_intent_id} of {self.amount} by {self.user.username}"
    # def clean():
    #     if not Users.objects.filter(id=user.id).first():
    #         raise ValidationError("Invalid user reference.")

class Order(Document):
    user = ReferenceField(Users, required=True)  # Reference to the User model
    payment = ReferenceField(Payment, required=True)  # Reference to the Payment model
    products = ListField(ReferenceField(AllItems), required=True)  # List of products in the order
    total_amount = DecimalField(required=True, precision=2)  # Total amount for the order
    
    order_date = DateTimeField(default=datetime.now())  # Date when the order was placed
    status = StringField(default="Pending")  # Order status (e.g., Pending, Completed, Canceled)
    
    # shipping_address = StringField(required=True)  # Shipping address for the order
    # tracking_number = StringField()  # Optional tracking number for shipment

    def __str__(self):
        return f"Order {self.id} by {self.user.username} - Total: {self.total_amount} {self.products}"

class VendorOrders(Document):
    shop_id = StringField(required=True)
    order = ReferenceField(Order,required=True)
    products = ListField(ReferenceField(AllItems), required=True)
    user = ReferenceField(Users,required=True)
    amount = DecimalField(required=True, precision=2)

    def __str__(self):
        return f"{self.user.username} from {self.shop_id} - Total amout : {self.amount}"

class Category(Document):
    category_name = StringField(required=True, max_length=100)
    image = StringField(required=True, max_length=200)

    def to_json(self):
        return {
            'id': str(self.id),  # Convert ObjectId to string for JSON serialization
            'category_name': self.category_name,
            'image': self.image
        }


class OTP_REG(Document):
    email = EmailField(required=True,null=False,unique=True)
    otp = IntField(required=True,null=False)
    otp_time = DateTimeField()



