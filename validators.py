from enum import Enum
from marshmallow import Schema, fields, validate, ValidationError
import re

class UserType(Enum):
    NORMAL = "normal user"
    SHOP_OWNER = "shop owner"

# Custom validation function for username
def validate_username(value):
    if not len(value)>7:
        raise ValidationError("usename must contain min 8 charecters")
    # Check if the username contains at least one uppercase letter, one number, and one special character
    if not re.search(r'[A-Z]', value):
        raise ValidationError("Username must contain at least one uppercase letter.")
    if not re.search(r'[0-9]', value):
        raise ValidationError("Username must contain at least one number.")
    if not re.search(r'[\W_]', value):  # \W matches any non-word character, including special characters
        raise ValidationError("Username must contain at least one special character.")

# Define the serializer using Marshmallow Schema
class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate_username,error_messages={
            "required": "A username is mandatory.",
            "invalid": "The username format is invalid.",
            "null": "Username cannot be null."
        })
    full_name = fields.Str(required=True,error_messages={
            "required": "A full_name is mandatory.",
            "null": "full_name cannot be null."
        })
    dob=fields.Date(required=True, error_messages={
        "required": "Birthdate is required.",
        "invalid": "Invalid date format. Please use YYYY-MM-DD."
    })
    email = fields.Email(required=True,error_messages={
            "required": "A email is mandatory.",
            "invalid": "The email format is invalid.",
            "null": "email cannot be null."
        })
    phone_number=fields.Str(required=True,validate=validate.Length(min=10,max=13),error_messages={
            "required": "A phone_number is mandatory.",
            "invalid": "The phone_number format is invalid.",
            "null": "phone_number cannot be null."
        })
    address = fields.Str(required=True,error_messages={
                "required": "address is mandatory.",
                "null": "address cannot be null."
            })
    landmark = fields.Str(required=True,error_messages={
            "required": "landmark is mandatory.",
            "null": "landmark cannot be null."
        })
    password = fields.Str(required=True, validate=validate.Length(min=6),error_messages={
            "required": "A password is mandatory.",
            "invalid": "The password format is invalid.",
            "null": "password cannot be null."
        })
user_schema = UserSchema()


class LoginSchema(Schema):
    username = fields.Str(required=True,validate=validate.Length(min=8),error_messages={
            "required": " username is mandatory.",
            "null": "Username cannot be null."
        })
    password = fields.Str(required=True, validate=validate.Length(min=6),error_messages={
            "required": " password is mandatory.",
            "null": "password cannot be null."
        })
login_schema = LoginSchema()

class VendorSchema(Schema):
        username = fields.Str(required=True, validate=validate_username,error_messages={
            "required": "username is mandatory.",
            "invalid": "The username format is invalid.",
            "null": "Username cannot be null."
        })
        shop_name = fields.Str(required=True,error_messages={
                "required": "shop_name is mandatory.",
                "null": "shop_name cannot be null."
            })
        email = fields.Email(required=True,error_messages={
                "required": "email is mandatory.",
                "invalid": "The email format is invalid.",
                "null": "email cannot be null."
            })
        phone_number=fields.Str(required=True,validate=validate.Length(min=10,max=13),error_messages={
                "required": "phone_number is mandatory.",
                "invalid": "The phone_number format is invalid.",
                "null": "phone_number cannot be null."
            })
        address = fields.Str(required=True,error_messages={
                "required": "address is mandatory.",
                "null": "address cannot be null."
            })
        landmark = fields.Str(required=True,error_messages={
                "required": "landmark is mandatory.",
                "null": "landmark cannot be null."
            })
        image_path = fields.Str(required=True,error_messages={
                "required": "image is mandatory.",
                "null": "image cannot be null."
            })
        password = fields.Str(required=True, validate=validate.Length(min=6),error_messages={
                "required": "A password is mandatory.",
                "invalid": "The password format is invalid.",
                "null": "password cannot be null."
            })
vendor_schema = VendorSchema()

class AddItemSchema(Schema):
    # shop_id = fields.Str(required=True,error_messages={
    #         "required": "shop_id is mandatory.",
    #         "null": "shop_id cannot be null."
    #     })
    item_name = fields.Str(required=True,validate=validate.Length(min=3),error_messages={
            "required": "item_name is mandatory.",
            "null": "item_name cannot be null."
        })
    image = fields.Str(required=True,validate=validate.Length(min=3),error_messages={
            "required": "image is mandatory.",
            "null": "image cannot be null."
        })
    quantity = fields.Int(required=True,error_messages={
            "required": "quantity is mandatory.",
            "null": "quantity cannot be null."
        })
    price = fields.Int(required=True,error_messages={
            "required": "price is mandatory.",
            "null": "price cannot be null."
        })
    stock = fields.Int(required=True,error_messages={
            "required": "stock is mandatory.",
            "null": "stock cannot be null."
        })
    category = fields.Str(required=True,validate=validate.Length(min=3),error_messages={
            "required": "category is mandatory.",
            "null": "category cannot be null."
        })

add_item_schema = AddItemSchema()

class AddToCartSchema(Schema):
    # user_id = fields.Str(required=True,error_messages={
    #         "required": "user_id is mandatory.",
    #         "null": "user_id cannot be null."
    #     })
    # category = fields.Str(required=True,validate=validate.Length(min=3),error_messages={
    #         "required": "category is mandatory.",
    #         "null": "category cannot be null."
    #     })
    item_id = fields.Str(required=True,error_messages={
            "required": "item_id is mandatory.",
            "null": "item_id cannot be null."
        })
    
add_to_cart_schema=AddToCartSchema()

