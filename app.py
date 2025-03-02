import streamlit as st
from datetime import datetime, timedelta
import base64
from PIL import Image
import random
import io
import pandas as pd
import numpy as np

# Import the classes from datamodel
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import random
import base64

class Customer:
    def __init__(self, customer_id: str, email: str, birthdate: datetime, gender: str, address: str, favorite_food: List[str] = None):
        self.customer_id = customer_id
        self.email = email
        self.birthdate = birthdate
        self.gender = gender
        self.address = address
        self.favorite_food = favorite_food if favorite_food is not None else []
        self.purchase_history = []
    
    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "email": self.email,
            "birthdate": self.birthdate.isoformat(),
            "gender": self.gender,
            "address": self.address,
            "favorite_food": self.favorite_food
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            customer_id=data["customer_id"],
            email=data["email"],
            birthdate=datetime.fromisoformat(data["birthdate"]),
            gender=data["gender"],
            address=data["address"],
            favorite_food=data["favorite_food"]
        )

class Receipt:
    def __init__(self, receipt_id: str, upload_date: datetime, image_data: bytes, 
                 ocr_text: str, ingredients: List[str], quantity: int, shelf_life: datetime):
        self.receipt_id = receipt_id
        self.upload_date = upload_date
        self.image_data = image_data
        self.ocr_text = ocr_text
        self.ingredients = ingredients
        self.quantity = quantity
        self.shelf_life = shelf_life
    
    def to_dict(self):
        return {
            "receipt_id": self.receipt_id,
            "upload_date": self.upload_date.isoformat(),
            "image_data": base64.b64encode(self.image_data).decode('utf-8') if self.image_data else None,
            "ocr_text": self.ocr_text,
            "ingredients": self.ingredients,
            "quantity": self.quantity,
            "shelf_life": self.shelf_life.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        image_data = base64.b64decode(data["image_data"]) if data.get("image_data") else None
        return cls(
            receipt_id=data["receipt_id"],
            upload_date=datetime.fromisoformat(data["upload_date"]),
            image_data=image_data,
            ocr_text=data["ocr_text"],
            ingredients=data["ingredients"],
            quantity=data["quantity"],
            shelf_life=datetime.fromisoformat(data["shelf_life"])
        )

class MenuItem:
    def __init__(self, item_id: str, name: str, ingredients: List[str], price: float):
        self.item_id = item_id
        self.name = name
        self.ingredients = ingredients
        self.price = price
    
    def match_ingredients(self, ingredients: List[str]) -> bool:
        return any(ingredient in self.ingredients for ingredient in ingredients)
    
    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "ingredients": self.ingredients,
            "price": self.price
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            ingredients=data["ingredients"],
            price=data["price"]
        )

class Store:
    def __init__(self, store_id: str, name: str, location: Tuple, menu_items: List[MenuItem]):
        self.store_id = store_id
        self.name = name
        self.location = location
        self.menu_items = menu_items
    
    def get_store_link(self) -> str:
        return f"https://www.example.com/store/{self.store_id}"
    
    def to_dict(self):
        return {
            "store_id": self.store_id,
            "name": self.name,
            "location": self.location,
            "menu_items": [item.to_dict() for item in self.menu_items]
        }
    
    @classmethod
    def from_dict(cls, data):
        menu_items = [MenuItem.from_dict(item) for item in data["menu_items"]]
        return cls(
            store_id=data["store_id"],
            name=data["name"],
            location=tuple(data["location"]),
            menu_items=menu_items
        )

class ReceiptSystem:
    def __init__(self):
        self.customers = []
        self.stores = []
        self.receipts = {}  # Map customer_id to list of receipts
        
    def register_customer(self, customer: Customer):
        """Register a new customer in the system"""
        # Check if customer already exists
        if any(c.customer_id == customer.customer_id for c in self.customers):
            raise ValueError(f"Customer with ID {customer.customer_id} already exists")
        
        if any(c.email == customer.email for c in self.customers):
            raise ValueError(f"Customer with email {customer.email} already exists")
            
        self.customers.append(customer)
        self.receipts[customer.customer_id] = []
        
    def add_store(self, store: Store):
        """Add a new store to the system"""
        if any(s.store_id == store.store_id for s in self.stores):
            raise ValueError(f"Store with ID {store.store_id} already exists")
            
        self.stores.append(store)
    
    def process_receipt(self, receipt: Receipt, customer_id=None):
        """
        Process a receipt by extracting text, identifying ingredients,
        and calculating shelf life
        """
        # Simulate OCR and ingredient extraction
        # In a real system, this would use actual OCR and NLP
        sample_ingredients = ["beef", "chicken", "lettuce", "tomato", 
                              "cheese", "bread", "milk", "eggs", "rice", "pasta"]
        
        # Randomly select 2-5 ingredients from the sample list
        num_ingredients = random.randint(2, 5)
        receipt.ingredients = random.sample(sample_ingredients, num_ingredients)
        
        # Generate some fake OCR text
        receipt.ocr_text = f"Receipt #{receipt.receipt_id}\n"
        receipt.ocr_text += f"Date: {receipt.upload_date.strftime('%Y-%m-%d')}\n"
        receipt.ocr_text += "Items:\n"
        for ingredient in receipt.ingredients:
            receipt.ocr_text += f"- {ingredient.capitalize()} ${random.uniform(1.99, 15.99):.2f}\n"
        
        # Calculate shelf life based on ingredients (simplified)
        # In a real system, this would use a more sophisticated algorithm
        shelf_life_days = 7  # Default shelf life is 7 days
        if "milk" in receipt.ingredients or "eggs" in receipt.ingredients:
            shelf_life_days = 3  # Dairy products have shorter shelf life
        
        receipt.shelf_life = receipt.upload_date + timedelta(days=shelf_life_days)
        
        # Associate receipt with customer if provided
        if customer_id and customer_id in self.receipts:
            self.receipts[customer_id].append(receipt)
        
    def get_recommendations(self, customer: Customer) -> List[MenuItem]:
        """
        Generate personalized recommendations for a customer based on
        their purchase history, preferences, and item shelf life
        """
        all_menu_items = []
        for store in self.stores:
            all_menu_items.extend(store.menu_items)
            
        if not all_menu_items:
            return []
        
        # Get customer's receipts and extract all ingredients
        customer_ingredients = set(customer.favorite_food)
        if customer.customer_id in self.receipts:
            for receipt in self.receipts[customer.customer_id]:
                customer_ingredients.update(receipt.ingredients)
        
        # Find menu items that match the customer's ingredients
        matching_items = []
        for item in all_menu_items:
            if any(ingredient in item.ingredients for ingredient in customer_ingredients):
                matching_items.append(item)
        
        if matching_items:
            # Return up to 3 matching items, prioritizing those with more matching ingredients
            matching_items.sort(key=lambda x: sum(1 for ing in customer_ingredients if ing in x.ingredients), reverse=True)
            return matching_items[:3]
        else:
            # If no matches found, return random items
            num_recommendations = min(len(all_menu_items), random.randint(1, 3))
            return random.sample(all_menu_items, num_recommendations)
    
    def to_dict(self):
        return {
            "customers": [c.to_dict() for c in self.customers],
            "stores": [s.to_dict() for s in self.stores],
            "receipts": {
                customer_id: [r.to_dict() for r in receipts] 
                for customer_id, receipts in self.receipts.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data):
        system = cls()
        
        # Load stores first
        for store_data in data.get("stores", []):
            store = Store.from_dict(store_data)
            system.stores.append(store)
        
        # Load customers
        for customer_data in data.get("customers", []):
            customer = Customer.from_dict(customer_data)
            system.customers.append(customer)
        
        # Load receipts
        for customer_id, receipts_data in data.get("receipts", {}).items():
            system.receipts[customer_id] = [Receipt.from_dict(r) for r in receipts_data]
        
        return system

def load_sample_data():
    """Initialize sample data for demonstration"""
    # Create menu items
    menu_item1 = MenuItem("M1", "Burger", ["beef", "lettuce", "tomato"], 9.99)
    menu_item2 = MenuItem("M2", "Pizza", ["dough", "cheese", "tomato"], 12.99)
    menu_item3 = MenuItem("M3", "Chicken Salad", ["chicken", "lettuce", "tomato"], 8.99)
    menu_item4 = MenuItem("M4", "Pasta Primavera", ["pasta", "tomato", "vegetables"], 11.99)
    menu_item5 = MenuItem("M5", "Greek Yogurt", ["milk", "cultures"], 4.99)
    menu_item6 = MenuItem("M6", "Fried Rice", ["rice", "eggs", "vegetables"], 10.99)
    
    # Create stores with menu items
    store1 = Store("S1", "Downtown Deli", (40.7128, -74.0060), [menu_item1, menu_item3, menu_item5])
    store2 = Store("S2", "Uptown Bistro", (40.8230, -73.9712), [menu_item2, menu_item4, menu_item6])
    
    # Create system and add stores
    system = ReceiptSystem()
    system.add_store(store1)
    system.add_store(store2)
    
    # Create a sample customer for demo purposes
    sample_customer = Customer(
        customer_id="C1",
        email="sample@example.com",
        birthdate=datetime(1990, 1, 1),
        gender="Other",
        address="123 Main St",
        favorite_food=["cheese", "chicken"]
    )
    system.register_customer(sample_customer)

    # Create a sample receipt
    # First, create a small fake image
    image_data = create_sample_image()
    
    # Create the receipt
    receipt = Receipt(
        receipt_id="R1",
        upload_date=datetime.now(),
        image_data=image_data,
        ocr_text="",
        ingredients=[],
        quantity=1,
        shelf_life=datetime.now()
    )
    
    # Process the receipt
    system.process_receipt(receipt, sample_customer.customer_id)
    
    return system

def create_sample_image():
    """Create a sample image for demo purposes"""
    # Create a small blank image
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    
    # Save it to a bytes buffer
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

def save_system_state(system):
    """Save the current system state to session_state"""
    st.session_state['system_data'] = system.to_dict()

def load_system_state():
    """Load the system state from session_state or initialize new system"""
    if 'system_data' in st.session_state:
        return ReceiptSystem.from_dict(st.session_state['system_data'])
    else:
        return load_sample_data()

def get_image_base64(image_data):
    """Convert image bytes to base64 for HTML display"""
    return base64.b64encode(image_data).decode("utf-8")

def main():
    st.set_page_config(
        page_title="Smart Receipt System",
        page_icon="🧾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS for better styling to match the mobile app designs
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subheader {
        font-size: 1.8rem;
        color: #2E7D32;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .app-header {
        background-color: #f8f8f8;
        padding: 1rem;
        border-radius: 15px 15px 0 0;
        border-bottom: 1px solid #eee;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
    }
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .product-card {
        padding: 0.8rem;
        border-radius: 10px;
        margin-bottom: 0.7rem;
        background-color: #f9f9f9;
        display: flex;
        align-items: center;
        border: 1px solid #eee;
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .product-image {
        width: 50px;
        height: 50px;
        border-radius: 5px;
        margin-right: 15px;
        object-fit: cover;
    }
    .product-details {
        flex: 1;
    }
    .product-name {
        font-weight: bold;
        margin-bottom: 0.2rem;
    }
    .expiry-item {
        display: flex;
        align-items: center;
        padding: 0.7rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        transition: all 0.2s;
    }
    .expiry-expired {
        background: linear-gradient(to right, #f9d7da, #f8d7da);
        border-left: 5px solid #dc3545;
    }
    .expiry-today {
        background: linear-gradient(to right, #f9d7da, #ffecb5);
        border-left: 5px solid #e74c3c;
    }
    .expiry-soon {
        background: linear-gradient(to right, #ffecb5, #ffe082);
        border-left: 5px solid #ff9800;
    }
    .expiry-week {
        background: linear-gradient(to right, #ffe082, #dcedc8);
        border-left: 5px solid #ffc107;
    }
    .expiry-safe {
        background: linear-gradient(to right, #dcedc8, #c8e6c9);
        border-left: 5px solid #4caf50;
    }
    .expiry-badge {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        font-weight: bold;
        font-size: 0.9rem;
        margin-left: auto;
    }
    .badge-exp {
        background-color: #bdbdbd;
        color: white;
    }
    .badge-3d {
        background-color: #e74c3c;
        color: white;
    }
    .badge-7d {
        background-color: #ff9800;
        color: white;
    }
    .badge-14d {
        background-color: #ffc107;
        color: white;
    }
    .badge-152d {
        background-color: #4caf50;
        color: white;
    }
    .badge-77d {
        background-color: #4caf50;
        color: white;
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .badge-green {
        background-color: #E8F5E9;
        color: #2E7D32;
        border: 1px solid #C8E6C9;
    }
    .badge-blue {
        background-color: #E3F2FD;
        color: #1565C0;
        border: 1px solid #BBDEFB;
    }
    .category-item {
        display: flex;
        align-items: center;
        padding: 0.8rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
        border: 1px solid #ddd;
        transition: background-color 0.2s;
    }
    .category-item:hover {
        background-color: #f5f5f5;
    }
    .category-icon {
        width: 40px;
        height: 40px;
        margin-right: 15px;
        object-fit: contain;
    }
    .category-name {
        font-size: 1.1rem;
        color: #555;
    }
    .barcode-scanner {
        border: 2px dashed #ddd;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    .food-expiry-list {
        margin-top: 1rem;
    }
    .food-item {
        display: flex;
        align-items: center;
        padding: 0.7rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        background-color: #fff;
        border: 1px solid #eee;
    }
    .food-icon {
        width: 30px;
        height: 30px;
        margin-right: 1rem;
    }
    .food-name {
        flex: 1;
        font-weight: 500;
    }
    .food-date {
        margin-right: 1rem;
    }
    .delete-button {
        color: #bbb;
        background: transparent;
        border: none;
        cursor: pointer;
    }
    .add-button {
        background-color: #e0f2e0;
        width: 40px;
        height: 40px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 100;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .mobile-container {
        max-width: 450px;
        margin: 0 auto;
        border: 1px solid #ddd;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .app-tabs {
        display: flex;
        justify-content: space-around;
        background-color: #f9f9f9;
        padding: 0.5rem;
        border-top: 1px solid #eee;
    }
    .app-tab {
        padding: 0.5rem 1rem;
        text-align: center;
        font-size: 0.8rem;
        color: #777;
    }
    .app-tab-active {
        color: #4CAF50;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.markdown("<h1 class='main-header'>Smart Receipt Processing System</h1>", unsafe_allow_html=True)
    
    # Load system
    system = load_system_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1622/1622816.png", width=100)
        st.title("Navigation")
        
        page = st.radio(
            "Select a page",
            ["Home", "Food Expiry Tracking", "Receipt Upload", "View Receipts", "Recommendations", "Store Marketplace"]
        )
        
        st.divider()
        if st.button("Reset Demo Data", type="secondary"):
            st.session_state.pop('system_data', None)
            st.experimental_rerun()
    
    # Page content
    if page == "Home":
        show_home_page(system)
    elif page == "Food Expiry Tracking":
        show_food_expiry(system)
    elif page == "Receipt Upload":
        show_receipt_upload(system)
    elif page == "View Receipts":
        show_receipts(system)
    elif page == "Recommendations":
        show_recommendations(system)
    elif page == "Store Marketplace":
        show_store_marketplace(system)
    
    # Save the current state
    save_system_state(system)

def show_home_page(system):
    st.markdown("## Welcome to Smart Receipt System")
    
    st.info("""
    This system helps you track your food purchases, extract ingredients from receipts, 
    calculate shelf life, and receive personalized food recommendations!
    """)
    
    # Create a mock-up of the mobile app UI
    st.markdown("### 📱 Mobile App Preview")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### 📋 System Stats")
        st.metric("Customers", len(system.customers))
        st.metric("Stores", len(system.stores))
        total_receipts = sum(len(receipts) for receipts in system.receipts.values())
        st.metric("Total Receipts", total_receipts)
        
        st.markdown("#### 🔄 How It Works")
        st.markdown("""
        1. Register your account
        2. Upload your receipts
        3. We'll extract ingredients and calculate shelf life
        4. Get personalized food recommendations
        5. Find stores that match your food preferences
        """)
    
    with col2:
        st.markdown("<div class='mobile-container'>", unsafe_allow_html=True)
        st.markdown("<div class='app-header'>Smart Receipt App</div>", unsafe_allow_html=True)
        
        # Generate some sample expiring foods for the demo
        st.markdown("<h3 style='padding-left: 1rem; padding-top: 1rem;'>Food Expiration Dates</h3>", unsafe_allow_html=True)

        foods = [
            {"name": "Eggs", "days": 0, "status": "expiry-today"},
            {"name": "Cheese", "days": 0, "status": "expiry-today"},
            {"name": "Milk", "days": 1, "status": "expiry-soon"},
            {"name": "Ham", "days": 3, "status": "expiry-soon"},
            {"name": "Butter", "days": 7, "status": "expiry-week"},
            {"name": "Mushrooms", "days": 14, "status": "expiry-safe"},
            {"name": "Tomatoes", "days": 25, "status": "expiry-safe"}
        ]
        
        for food in foods:
            if food["days"] == 0:
                day_text = "Today"
            elif food["days"] == 1:
                day_text = "Tomorrow"
            else:
                day_text = f"In {food['days']} days"
                
            st.markdown(f"""
            <div class='{food["status"]} expiry-item'>
                <img src='https://cdn-icons-png.flaticon.com/512/1147/1147805.png' class='food-icon' />
                <div class='food-name'>{food["name"]}</div>
                <div class='food-date'>{day_text}</div>
                <button class='delete-button'>🗑️</button>
            </div>
            """, unsafe_allow_html=True)
        
        # Add a floating action button
        st.markdown("""
        <div class='add-button'>+</div>
        <div class='app-tabs'>
            <div class='app-tab app-tab-active'>List</div>
            <div class='app-tab'>Scan</div>
            <div class='app-tab'>Stores</div>
            <div class='app-tab'>Profile</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_food_expiry(system):
    st.markdown("<h2 class='subheader'>Food Expiry Tracking</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='mobile-container'>", unsafe_allow_html=True)
        st.markdown("<div class='app-header'>Food Expiration Dates</div>", unsafe_allow_html=True)
        
        # Generate some sample expiring foods for the demo (similar to Image 1)
        foods = [
            {"name": "Eggs", "days": 0, "status": "expiry-today"},
            {"name": "Cheese", "days": 0, "status": "expiry-today"},
            {"name": "Milk", "days": 1, "status": "expiry-soon"},
            {"name": "Ham", "days": 3, "status": "expiry-soon"},
            {"name": "Butter", "days": 7, "status": "expiry-week"},
            {"name": "Mushrooms", "days": 14, "status": "expiry-safe"},
            {"name": "Tomatoes", "days": 25, "status": "expiry-safe"}
        ]
        
        for food in foods:
            if food["days"] == 0:
                day_text = "Today"
            elif food["days"] == 1:
                day_text = "Tomorrow"
            else:
                day_text = f"In {food['days']} days"
                
            st.markdown(f"""
            <div class='{food["status"]} expiry-item'>
                <img src='https://cdn-icons-png.flaticon.com/512/1147/1147805.png' class='food-icon' />
                <div class='food-name'>{food["name"]}</div>
                <div class='food-date'>{day_text}</div>
                <button class='delete-button'>🗑️</button>
            </div>
            """, unsafe_allow_html=True)
        
        # Add a floating action button
        st.markdown("""
        <div class='add-button'>+</div>
        <div class='app-tabs'>
            <div class='app-tab app-tab-active'>List</div>
            <div class='app-tab'>Scan</div>
            <div class='app-tab'>Stores</div>
            <div class='app-tab'>Profile</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='mobile-container'>", unsafe_allow_html=True)
        st.markdown("<div class='app-header'>Expiry Reminder</div>", unsafe_allow_html=True)
        
        # Generate sample expiry reminders (similar to Image 2)
        items = [
            {"name": "Expired Milk", "production": "Nov 16, 2024", "shelf_life": "7 Days", "expiry": "Nov 23, 2024", "badge": "EXP", "badge_class": "badge-exp"},
            {"name": "Fresh Yogurt", "production": "Nov 15, 2024", "shelf_life": "14 Days", "expiry": "Nov 29, 2024", "badge": "3D", "badge_class": "badge-3d"},
            {"name": "Orange Juice", "production": "Nov 03, 2024", "shelf_life": "1 Month", "expiry": "Dec 03, 2024", "badge": "7D", "badge_class": "badge-7d"},
            {"name": "Canned Soup", "production": "Oct 27, 2024", "shelf_life": "6 Months", "expiry": "Apr 27, 2025", "badge": "152D", "badge_class": "badge-152d"},
            {"name": "Frozen Pizza", "production": "Nov 11, 2024", "shelf_life": "3 Months", "expiry": "Feb 11, 2025", "badge": "77D", "badge_class": "badge-77d"}
        ]
        
        for item in items:
            st.markdown(f"""
            <div style="padding: 0.8rem; margin-bottom: 0.8rem; background-color: #f9f9f9; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center;">
                    <img src="https://cdn-icons-png.flaticon.com/512/1147/1147805.png" style="width: 40px; height: 40px; margin-right: 10px;">
                    <div style="flex-grow: 1;">
                        <div style="font-weight: bold;">{item["name"]}</div>
                        <div style="font-size: 0.9rem; color: #666;">Production: {item["production"]}</div>
                        <div style="font-size: 0.9rem; color: #666;">Shelf Life: {item["shelf_life"]}</div>
                        <div style="font-size: 0.9rem; color: #666;">Expiry: {item["expiry"]}</div>
                    </div>
                    <div class="{item["badge_class"]} expiry-badge">{item["badge"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add bottom tabs
        st.markdown("""
        <div class='app-tabs'>
            <div class='app-tab'>List</div>
            <div class='app-tab app-tab-active'>Reminder</div>
            <div class='app-tab'>Stores</div>
            <div class='app-tab'>Profile</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_receipt_upload(system):
    st.markdown("<h2 class='subheader'>Receipt Upload & Processing</h2>", unsafe_allow_html=True)
    
    if not system.customers:
        st.warning("Please register a customer first!")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Upload Receipt")
        
        # Customer selection
        customer_emails = [c.email for c in system.customers]
        selected_email = st.selectbox("Select Customer", customer_emails)
        selected_customer = next((c for c in system.customers if c.email == selected_email), None)
        
        st.markdown("#### Scan Barcode")
        
        # Barcode scanner simulation
        st.markdown("""
        <div class='barcode-scanner'>
            <img src="https://cdn-icons-png.flaticon.com/512/1799/1799767.png" style="width: 60px; height: 60px; margin-bottom: 10px;">
            <p>Position the barcode within the frame to scan</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("receipt_form"):
            receipt_id = st.text_input("Receipt ID", value=f"R{sum(len(receipts) for receipts in system.receipts.values())+1}")
            uploaded_file = st.file_uploader("Upload Receipt Image", type=['png', 'jpg', 'jpeg'])
            quantity = st.number_input("Quantity", min_value=1, value=1)
            
            # Show image preview if uploaded
            if uploaded_file:
                try:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Receipt Preview", width=200)
                except:
                    st.error("Failed to preview image")
            
            submit_button = st.form_submit_button("Process Receipt")
            
            if submit_button:
                if uploaded_file is None:
                    st.error("Please upload a receipt image!")
                else:
                    try:
                        # Reset buffer to start and read the file
                        uploaded_file.seek(0)
                        image_data = uploaded_file.read()
                        
                        receipt = Receipt(
                            receipt_id=receipt_id,
                            upload_date=datetime.now(),
                            image_data=image_data,
                            ocr_text="",  # Will be filled by processing
                            ingredients=[],  # Will be filled by processing
                            quantity=quantity,
                            shelf_life=datetime.now()  # Will be updated after processing
                        )
                        
                        # Process the receipt
                        system.process_receipt(receipt, selected_customer.customer_id)
                        
                        st.success("✅ Receipt processed successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error processing receipt: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Show a mobile app mockup of the barcode scanning interface (similar to Image 4)
        st.markdown("<div class='mobile-container'>", unsafe_allow_html=True)
        st.markdown("<div class='app-header'>Barcode Scanner</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="position: relative; padding: 1rem;">
            <img src="https://www.pngall.com/wp-content/uploads/5/Barcode-PNG-Image-File.png" 
                 style="width: 100%; border: 2px dashed #ccc; padding: 15px; margin-bottom: 15px;">
            
            <div style="margin-top: 1rem;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <img src="https://cdn-icons-png.flaticon.com/512/1198/1198420.png" style="width: 30px; height: 30px; margin-right: 10px;">
                    <div style="font-weight: bold;">Product Name</div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <img src="https://cdn-icons-png.flaticon.com/512/2413/2413288.png" style="width: 30px; height: 30px; margin-right: 10px;">
                    <div>Expiry Date: <input type="text" placeholder="yyyy-mm-dd" style="border: 1px solid #ddd; padding: 5px; border-radius: 5px;"></div>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <img src="https://cdn-icons-png.flaticon.com/512/1332/1332655.png" style="width: 30px; height: 30px; margin-right: 10px;">
                    <div>Quantity: <input type="number" value="1" style="border: 1px solid #ddd; padding: 5px; border-radius: 5px; width: 60px;"></div>
                </div>
            </div>
            
            <button style="background-color: #4CAF50; color: white; padding: 0.8rem; border: none; border-radius: 5px; width: 100%; margin-top: 1rem; font-weight: bold;">Scan Barcode</button>
        </div>
        """, unsafe_allow_html=True)
        
        # Add bottom tabs
        st.markdown("""
        <div class='app-tabs'>
            <div class='app-tab'>List</div>
            <div class='app-tab app-tab-active'>Scan</div>
            <div class='app-tab'>Stores</div>
            <div class='app-tab'>Profile</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_receipts(system):
    st.markdown("<h2 class='subheader'>Receipt History</h2>", unsafe_allow_html=True)
    
    if not system.customers:
        st.warning("Please register a customer first!")
        return
    
    # Customer selection
    customer_emails = [c.email for c in system.customers]
    selected_email = st.selectbox("Select Customer", customer_emails)
    selected_customer = next((c for c in system.customers if c.email == selected_email), None)
    
    if selected_customer and selected_customer.customer_id in system.receipts and system.receipts[selected_customer.customer_id]:
        st.markdown(f"### Receipts for {selected_customer.email}")
        
        receipts = system.receipts[selected_customer.customer_id]
        
        # Display receipts in a more visual way
        for receipt in receipts:
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if receipt.image_data:
                        st.image(receipt.image_data, caption=f"Receipt {receipt.receipt_id}", width=150)
                    else:
                        st.markdown("""
                        <div style="width: 150px; height: 200px; background-color: #f5f5f5; display: flex; align-items: center; justify-content: center; border-radius: 5px;">
                            <span style="color: #999;">No Image</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"#### Receipt {receipt.receipt_id}")
                    st.markdown(f"**Upload Date:** {receipt.upload_date.strftime('%Y-%m-%d')}")
                    
                    # Display ingredients with badges
                    st.markdown("**Ingredients:**")
                    ingredient_html = ""
                    for ingredient in receipt.ingredients:
                        ingredient_html += f'<span class="badge badge-blue">{ingredient}</span>'
                    st.markdown(ingredient_html, unsafe_allow_html=True)
                    
                    # Display shelf life with appropriate color
                    days_remaining = (receipt.shelf_life - datetime.now()).days
                    if days_remaining > 3:
                        st.success(f"**Shelf Life Until:** {receipt.shelf_life.strftime('%Y-%m-%d')} ({days_remaining} days remaining)")
                    elif days_remaining > 0:
                        st.warning(f"**Shelf Life Until:** {receipt.shelf_life.strftime('%Y-%m-%d')} (Only {days_remaining} days remaining!)")
                    else:
                        st.error(f"**Shelf Life Until:** {receipt.shelf_life.strftime('%Y-%m-%d')} (Past shelf life!)")
                    
                    # Display OCR text in an expander
                    with st.expander("View OCR Text"):
                        st.text(receipt.ocr_text)
            
            st.divider()
    else:
        st.info("No receipts found for this customer. Upload a receipt in the 'Receipt Upload' page.")
        
        # Add a demo mock-up of a receipt
        st.markdown("### Receipt Demo")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/1611/1611154.png", width=150)
        
        with col2:
            st.markdown("#### Sample Receipt")
            st.markdown("**Upload Date:** 2024-03-01")
            st.markdown("**Ingredients:**")
            st.markdown('<span class="badge badge-blue">milk</span> <span class="badge badge-blue">eggs</span> <span class="badge badge-blue">bread</span>', unsafe_allow_html=True)
            st.success("**Shelf Life Until:** 2024-03-04 (2 days remaining)")
            
            with st.expander("View OCR Text"):
                st.text("""Receipt #R123
Date: 2024-03-01
Items:
- Milk $3.99
- Eggs $2.49
- Bread $1.99
Total: $8.47""")

def show_recommendations(system):
    st.markdown("<h2 class='subheader'>Food Recommendations</h2>", unsafe_allow_html=True)
    
    if not system.customers:
        st.warning("Please register a customer first!")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Customer Selection")
        
        # Customer selection
        customer_emails = [c.email for c in system.customers]
        selected_email = st.selectbox("Select Customer", customer_emails)
        selected_customer = next((c for c in system.customers if c.email == selected_email), None)
        
        if selected_customer:
            st.markdown("#### Customer Profile")
            st.write(f"ID: {selected_customer.customer_id}")
            st.write(f"Email: {selected_customer.email}")
            
            st.markdown("#### Favorite Foods")
            favorite_html = ""
            for food in selected_customer.favorite_food:
                favorite_html += f'<span class="badge badge-green">{food}</span>'
            st.markdown(favorite_html, unsafe_allow_html=True)
            
            st.markdown("#### Recently Purchased Ingredients")
            if selected_customer.customer_id in system.receipts and system.receipts[selected_customer.customer_id]:
                all_ingredients = set()
                for receipt in system.receipts[selected_customer.customer_id]:
                    all_ingredients.update(receipt.ingredients)
                
                ingredient_html = ""
                for ingredient in all_ingredients:
                    ingredient_html += f'<span class="badge badge-blue">{ingredient}</span>'
                st.markdown(ingredient_html, unsafe_allow_html=True)
            else:
                st.info("No receipts uploaded yet!")
            
            if st.button("Get Recommendations"):
                st.session_state['show_recommendations'] = True
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        if 'show_recommendations' in st.session_state and st.session_state['show_recommendations'] and selected_customer:
            recommendations = system.get_recommendations(selected_customer)
            
            if recommendations:
                # Display recommendations as a modern product list
                st.markdown("### Recommended Items")
                
                for item in recommendations:
                    st.markdown(f"""
                    <div class="product-card">
                        <img src="https://cdn-icons-png.flaticon.com/512/1147/1147805.png" class="product-image">
                        <div class="product-details">
                            <div class="product-name">{item.name}</div>
                            <div style="color: #2E7D32; font-weight: bold; margin-bottom: 5px;">${item.price:.2f}</div>
                    """, unsafe_allow_html=True)
                    
                    ingredient_html = ""
                    for ingredient in item.ingredients:
                        if ingredient in selected_customer.favorite_food:
                            ingredient_html += f'<span class="badge badge-green">{ingredient}</span>'
                        else:
                            ingredient_html += f'<span class="badge badge-blue">{ingredient}</span>'
                    st.markdown(ingredient_html, unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
                    
                    # Show why this item was recommended
                    if selected_customer.favorite_food:
                        matching_ingredients = [food for food in selected_customer.favorite_food if food in item.ingredients]
                        if matching_ingredients:
                            st.markdown(f"✓ **Contains your favorite:** {', '.join(matching_ingredients)}")
                    
                    # Find store
                    store = next((s for s in system.stores if any(mi.item_id == item.item_id for mi in s.menu_items)), None)
                    if store:
                        st.write(f"**Available at:** {store.name}")
                        st.button(f"Add to Cart", key=f"add_{item.item_id}")
            else:
                st.info("No recommendations available at this time.")
        else:
            # Show a demo recommendation
            st.markdown("### Sample Recommendations")
            
            demo_items = [
                {"name": "Greek Yogurt", "price": 4.99, "ingredients": ["milk", "cultures"], "favorite": ["milk"]},
                {"name": "Chicken Salad", "price": 8.99, "ingredients": ["chicken", "lettuce", "tomato"], "favorite": ["chicken"]},
                {"name": "Pizza", "price": 12.99, "ingredients": ["dough", "cheese", "tomato"], "favorite": ["cheese"]}
            ]
            
            for item in demo_items:
                st.markdown(f"""
                <div class="product-card">
                    <img src="https://cdn-icons-png.flaticon.com/512/1147/1147805.png" class="product-image">
                    <div class="product-details">
                        <div class="product-name">{item["name"]}</div>
                        <div style="color: #2E7D32; font-weight: bold; margin-bottom: 5px;">${item["price"]:.2f}</div>
                """, unsafe_allow_html=True)
                
                ingredient_html = ""
                for ingredient in item["ingredients"]:
                    if ingredient in item["favorite"]:
                        ingredient_html += f'<span class="badge badge-green">{ingredient}</span>'
                    else:
                        ingredient_html += f'<span class="badge badge-blue">{ingredient}</span>'
                st.markdown(ingredient_html, unsafe_allow_html=True)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
                
                if item["favorite"]:
                    st.markdown(f"✓ **Contains your favorite:** {', '.join(item['favorite'])}")
                
                st.button(f"Add to Cart (Demo)", key=f"demo_{item['name']}")

def show_store_marketplace(system):
    st.markdown("<h2 class='subheader'>Store Marketplace</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Display all available stores
        st.markdown("### Available Stores")
        
        for store in system.stores:
            with st.container():
                st.markdown(f"""
                <div class='card'>
                    <h3>{store.name}</h3>
                    <p><strong>Location:</strong> {store.location[0]}, {store.location[1]}</p>
                    <p><strong>Available Items:</strong> {len(store.menu_items)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View {store.name}", key=f"view_{store.store_id}"):
                    st.session_state['selected_store'] = store.store_id
    
    with col2:
        # Show the store catalog selection interface (similar to Image 3)
        st.markdown("<div class='mobile-container'>", unsafe_allow_html=True)
        st.markdown("<div class='app-header'>Product Categories</div>", unsafe_allow_html=True)
        
        # Display food categories
        categories = [
            {"name": "Fruit & Veg", "icon": "https://cdn-icons-png.flaticon.com/512/2153/2153786.png"},
            {"name": "Dairy", "icon": "https://cdn-icons-png.flaticon.com/512/2674/2674486.png"},
            {"name": "Meat", "icon": "https://cdn-icons-png.flaticon.com/512/776/776450.png"},
            {"name": "Fish", "icon": "https://cdn-icons-png.flaticon.com/512/1691/1691169.png"},
            {"name": "Frozen Meat", "icon": "https://cdn-icons-png.flaticon.com/512/2514/2514042.png"},
            {"name": "Frozen Fish", "icon": "https://cdn-icons-png.flaticon.com/512/2927/2927347.png"},
            {"name": "Flowers", "icon": "https://cdn-icons-png.flaticon.com/512/628/628324.png"},
            {"name": "Poultry & Eggs", "icon": "https://cdn-icons-png.flaticon.com/512/1046/1046751.png"}
        ]
        
        for category in categories:
            st.markdown(f"""
            <div class="category-item">
                <img src="{category['icon']}" class="category-icon">
                <div class="category-name">{category['name']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add bottom tabs
        st.markdown("""
        <div class='app-tabs'>
            <div class='app-tab'>List</div>
            <div class='app-tab'>Scan</div>
            <div class='app-tab app-tab-active'>Stores</div>
            <div class='app-tab'>Profile</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Check if a store is selected to display its details
        selected_store_id = st.session_state.get('selected_store')
        if selected_store_id:
            selected_store = next((s for s in system.stores if s.store_id == selected_store_id), None)
            if selected_store:
                st.markdown(f"### {selected_store.name} Menu Items")
                
                for item in selected_store.menu_items:
                    st.markdown(f"""
                    <div class="product-card">
                        <img src="https://cdn-icons-png.flaticon.com/512/1147/1147805.png" class="product-image">
                        <div class="product-details">
                            <div class="product-name">{item.name}</div>
                            <div style="color: #2E7D32; font-weight: bold; margin-bottom: 5px;">${item.price:.2f}</div>
                    """, unsafe_allow_html=True)
                    
                    ingredient_html = ""
                    for ingredient in item.ingredients:
                        ingredient_html += f'<span class="badge badge-blue">{ingredient}</span>'
                    st.markdown(ingredient_html, unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
                    st.button(f"Add {item.name} to Cart", key=f"cart_{item.item_id}")

if __name__ == "__main__":
    main()