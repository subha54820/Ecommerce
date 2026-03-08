import os
import requests
from django.core.files.base import ContentFile
from ecommerceapp.models import Category, Product

# Define Categories and Products
DATA = [
    {
        "category": "Electronics",
        "products": [
            {
                "name": "Portable Bluetooth Speaker",
                "description": "Powerful sound and deep bass in a compact, waterproof design. 20 hours of playtime.",
                "price": 3500.00,
                "stock": 45,
                "featured": True,
                "image_url": "https://images.unsplash.com/photo-1608156639585-342c348ce65e?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "name": "Mechanical Gaming Keyboard",
                "description": "RGB backlit mechanical keyboard with tactile switches for precision gaming and typing.",
                "price": 4500.00,
                "stock": 30,
                "featured": True,
                "image_url": "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?q=80&w=1000&auto=format&fit=crop"
            }
        ]
    },
    {
        "category": "Fashion",
        "products": [
            {
                "name": "Oversized Streetwear Hoodie",
                "description": "Premium cotton blend hoodie with a modern oversized fit and minimalist design.",
                "price": 2200.00,
                "stock": 60,
                "featured": True,
                "image_url": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "name": "Vintage Denim Jacket",
                "description": "Classic wash denim jacket with a timeless look and durable construction.",
                "price": 3000.00,
                "stock": 25,
                "featured": False,
                "image_url": "https://images.unsplash.com/photo-1523205771623-e0faa4d2813d?q=80&w=1000&auto=format&fit=crop"
            }
        ]
    },
    {
        "category": "Home Decor",
        "products": [
            {
                "name": "Modern LED Desk Lamp",
                "description": "Sleek, touch-controlled LED lamp with adjustable brightness and color temperature.",
                "price": 1200.00,
                "stock": 80,
                "featured": True,
                "image_url": "https://images.unsplash.com/photo-1534073828943-f801091bb18c?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "name": "Scented Soy Candle Set",
                "description": "Set of 3 hand-poured soy candles with calming lavender and sandalwood scents.",
                "price": 800.00,
                "stock": 120,
                "featured": False,
                "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "name": "Abstract Geometric Wall Art",
                "description": "Premium framed canvas print featuring modern abstract geometric shapes.",
                "price": 2500.00,
                "stock": 15,
                "featured": True,
                "image_url": "https://images.unsplash.com/photo-1549490349-8643362247b5?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "name": "Velvet Throw Pillow Covers",
                "description": "Set of 2 ultra-soft velvet pillow covers in a rich forest green color.",
                "price": 450.00,
                "stock": 200,
                "featured": False,
                "image_url": "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "name": "Ceramic Indoor Plant Pot",
                "description": "Elegant white ceramic pot with a gold-accented base, perfect for indoor succulents.",
                "price": 900.00,
                "stock": 50,
                "featured": True,
                "image_url": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?q=80&w=1000&auto=format&fit=crop"
            }
        ]
    },
    {
        "category": "Beauty",
        "products": [
            {
                "name": "Hydrating Face Moisturizer",
                "description": "Dermatologist-tested cream with hyaluronic acid for long-lasting hydration.",
                "price": 600.00,
                "stock": 150,
                "featured": True,
                "image_url": "https://images.unsplash.com/photo-1556227702-d1e4e7ca1e43?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "name": "Argan Hair Serum",
                "description": "Nourishing serum that adds shine and reduces frizz for silky smooth hair.",
                "price": 1100.00,
                "stock": 90,
                "featured": False,
                "image_url": "https://images.unsplash.com/photo-1526947425960-945c6e72858f?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "name": "Handmade Soap Gift Box",
                "description": "Artisan collection of 4 organic, essential oil-infused handmade soaps.",
                "price": 1500.00,
                "stock": 40,
                "featured": True,
                "image_url": "https://images.unsplash.com/photo-1600857062241-98e5dba7f214?q=80&w=1000&auto=format&fit=crop"
            }
        ]
    },
    {
        "category": "Accessories",
        "products": [
            {
                "name": "Genuine Leather Wallet",
                "description": "Slim, handcrafted bifold wallet made from premium full-grain leather.",
                "price": 1800.00,
                "stock": 55,
                "featured": True,
                "image_url": "https://images.unsplash.com/photo-1627123424574-724758594e93?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "name": "Floral Silk Scarf",
                "description": "Exquisite 100% silk scarf with a vibrant hand-painted floral pattern.",
                "price": 1200.00,
                "stock": 35,
                "featured": False,
                "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=1000&auto=format&fit=crop"
            },
            {
                "name": "Insulated Stainless Bottle",
                "description": "Double-walled vacuum insulated water bottle. Keeps drinks cold for 24 hours.",
                "price": 900.00,
                "stock": 110,
                "featured": True,
                "image_url": "https://images.unsplash.com/photo-1602143307185-83cdde695022?q=80&w=1000&auto=format&fit=crop"
            }
        ]
    }
]

def populate():
    for entry in DATA:
        cat_name = entry["category"]
        category, created = Category.objects.get_or_create(name=cat_name)
        
        for p_data in entry["products"]:
            product, p_created = Product.objects.get_or_create(
                name=p_data["name"],
                category=category,
                defaults={
                    "description": p_data["description"],
                    "price": p_data["price"],
                    "stock": p_data["stock"],
                    "featured": p_data["featured"]
                }
            )
            
            if p_created:
                print(f"Adding product: {product.name}")
                try:
                    response = requests.get(p_data["image_url"], timeout=10)
                    if response.status_code == 200:
                        file_name = f"{product.name.lower().replace(' ', '_')}.jpg"
                        product.image.save(file_name, ContentFile(response.content), save=True)
                    else:
                        print(f"Failed to download image: {response.status_code}")
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    populate()
