import boto3
import random
import cfnresponse
from botocore.exceptions import ClientError


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('workshop-Products-1THNY91UDK5EE')
# Sample data for product names, descriptions, categories, genders, and occasions.
#the product names and descriptions should respect the categories
#for example, a product name like "rose" should be used with a category of "flowers"
product_names = {
    'jewelry': ['necklace', 'bracelet', 'ring', 'earrings'],
    'accessories': ['scarf', 'hat', 'bag', 'sunglasses'],
    'perfumes': ['eau de toilette', 'eau de perfume', 'cologne', 'fragrance'],
    'flowers': ['rose', 'lilies', 'tulips', 'orchids'],
    'watches': ['analog', 'digital', 'smartwatch', 'luxury'],
    'toys': ['RC Car', 'action figure', 'board game', 'puzzle']
}
descriptions = {
    'jewelry': ['Elegant', 'Timeless', 'Sparkling', 'Sophisticated'],
    'accessories': ['Stylish', 'Trendy', 'Versatile', 'Chic'],
    'perfumes': ['Captivating', 'Alluring', 'Refreshing', 'Luxurious'],
    'flowers': ['Vibrant', 'Fragrant', 'Romantic', 'Soothing'],
    'watches': ['Precise', 'Durable', 'Sleek', 'Functional'],
    'toys': ['Entertaining', 'Educational', 'Imaginative', 'Engaging']
}
occasion_descriptions = {
    'party': ['Festive', 'Lively', 'Celebratory', 'Joyful'],
    'wedding': ['Bridal', 'Ceremonial', 'Romantic', 'Elegant'],
    'date': ['Charming', 'Intimate', 'Thoughtful', 'Memorable'],
    'valentines day': ['Amorous', 'Passionate', 'Affectionate', 'Sentimental'],
    'mothers day': ['Heartfelt', 'Cherished', 'Appreciative', 'Loving'],
    'birthday': ['Celebratory', 'Festive', 'Delightful', 'Joyous']
}
categories = ['jewelry', 'accessories', 'perfumes', 'flowers', 'watches', 'toys']
genders = ['men', 'women', 'unisex']
occasions = ['party', 'wedding', 'date', 'valentines day', 'mothers day', 'birthday']

def generate_unique_product_name(category, occasion):
    """Generate a unique product name based on the category and occasion."""
    iteration = 0
    while True:
        iteration += 1
        if iteration > 100:
            raise ValueError("Unable to generate a unique product name after 100 iterations.")
        product_name = f"{random.choice(occasion_descriptions[occasion])} {random.choice(product_names[category])}"
        # Check if the product name already exists in the DynamoDB table
        response = table.get_item(
            Key={
                'product_name': product_name
            },
            AttributesToGet=['product_name']
        )
        if 'Item' not in response:
            return product_name
        else:
            print(f"Product name '{product_name}' already exists. Generating a new one...")

def lambda_handler(event, context):
    # Generate 100 sample data entries
    for i in range(100):
        category = random.choice(categories)
        occasion = random.choice(occasions)
        try:
            product_name = generate_unique_product_name(category, occasion)
        except ValueError as e:
            responseData = {"Error": str(e)}
            cfnresponse.send(event, context, cfnresponse.FAILED, responseData, "CustomResourcePhysicalID")
            return
        product_description = f"{random.choice(descriptions[category])} {product_name}"
        gender = random.choice(genders)
        # Insert the sample data into the DynamoDB table
        try:
            table.put_item(
                Item={
                    'product_name': product_name,
                    'Product_description': product_description,
                    'category': category,
                    'gender': gender,
                    'occasion': occasion
                }
            )
            responseData = {"Data": ""}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, "CustomResourcePhysicalID")
        # handle exception
        except ClientError as e:
            responseData = {"Error": str(e)}
            cfnresponse.send(event, context, cfnresponse.FAILED, responseData, "CustomResourcePhysicalID")
            return
