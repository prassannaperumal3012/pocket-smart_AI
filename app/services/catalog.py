from urllib.parse import quote


CATALOG = {

    "home": [

        {
            "name": "LED Ceiling Light",
            "category": "lighting",
            "platform": "Amazon",
            "price": 1499,
            "keywords": "LED ceiling light home decor",
        },

        {
            "name": "Minimalist Floor Lamp",
            "category": "lighting",
            "platform": "IKEA",
            "price": 2499,
            "keywords": "minimalist floor lamp",
        },

        {
            "name": "Compact Dining Table",
            "category": "furniture",
            "platform": "IKEA",
            "price": 8999,
            "keywords": "compact dining table",
        },

        {
            "name": "3-Seater Fabric Sofa",
            "category": "furniture",
            "platform": "Amazon",
            "price": 18999,
            "keywords": "3 seater fabric sofa",
        },

        {
            "name": "Decorative Wall Art Set",
            "category": "decor",
            "platform": "Amazon",
            "price": 1299,
            "keywords": "decorative wall art set",
        },

        {
            "name": "Storage Cabinet",
            "category": "storage",
            "platform": "IKEA",
            "price": 6999,
            "keywords": "storage cabinet",
        },

        {
            "name": "Kitchen Utility Organizer",
            "category": "kitchen",
            "platform": "Amazon",
            "price": 999,
            "keywords": "kitchen utility organizer",
        },
    ],

    "party": [

        {
            "name": "Catering Search",
            "category": "food",
            "platform": "Zomato",
            "price": 450,
            "keywords": "party catering",
        },

        {
            "name": "Food Delivery Search",
            "category": "food",
            "platform": "Swiggy",
            "price": 400,
            "keywords": "party food delivery",
        },

        {
            "name": "Event Decoration Search",
            "category": "decoration",
            "platform": "Amazon",
            "price": 2500,
            "keywords": "birthday party decorations",
        },

        {
            "name": "Hotel / Venue Search",
            "category": "venue",
            "platform": "OYO",
            "price": 5000,
            "keywords": "event venue",
        },

        {
            "name": "Party Tableware Set",
            "category": "tableware",
            "platform": "Amazon",
            "price": 899,
            "keywords": "party tableware",
        },
    ],

    "jewelry": [

        {
            "name": "Minimal Gold-Tone Earrings",
            "category": "earrings",
            "platform": "Amazon",
            "price": 799,
            "keywords": "minimal gold tone earrings",
        },

        {
            "name": "Pearl Drop Earrings",
            "category": "earrings",
            "platform": "Flipkart",
            "price": 1299,
            "keywords": "pearl drop earrings",
        },

        {
            "name": "Statement Necklace",
            "category": "necklace",
            "platform": "Amazon",
            "price": 1899,
            "keywords": "statement necklace",
        },

        {
            "name": "Delicate Pendant",
            "category": "necklace",
            "platform": "Flipkart",
            "price": 999,
            "keywords": "delicate pendant necklace",
        },

        {
            "name": "Bangle Set",
            "category": "bracelet",
            "platform": "Amazon",
            "price": 1499,
            "keywords": "bangle set",
        },
    ],
}


def search_url(
    platform: str,
    keywords: str,
) -> str:

    domains = {

        "Amazon":
            "https://www.amazon.in/s?k=",

        "Flipkart":
            "https://www.flipkart.com/search?q=",

        "IKEA":
            "https://www.ikea.com/in/en/search/?q=",

        "Swiggy":
            "https://www.swiggy.com/search?query=",

        "Zomato":
            "https://www.zomato.com/search?q=",

        "OYO":
            "https://www.oyorooms.com/search?location=",
    }

    base_url = domains.get(
        platform,
        "https://www.google.com/search?q=",
    )

    return base_url + quote(keywords)


def catalog_for(
    planner: str,
) -> list[dict]:

    return [
        {
            **item,
            "search_url": search_url(
                item["platform"],
                item["keywords"],
            ),
        }
        for item in CATALOG.get(
            planner,
            [],
        )
    ]
