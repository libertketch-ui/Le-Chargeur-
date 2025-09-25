from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import random
import math

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="BusConnect Cameroun API", description="FlixBus-style bus booking system for Cameroon")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# === MODELS ===
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    phone: str
    first_name: str
    last_name: str
    user_type: str = "client"  # client, agency, transporter, occasional_transport
    status: str = "pending"  # pending, active, rejected
    documents: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    phone: str
    first_name: str
    last_name: str
    user_type: str = "client"
    documents: List[str] = []

class BusRoute(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    price: int
    company: str
    available_seats: int
    total_seats: int
    bus_type: str
    amenities: List[str]
    distance_km: int

class SearchQuery(BaseModel):
    origin: str
    destination: str
    departure_date: str
    passengers: int = 1

class BaggageItem(BaseModel):
    type: str  # carry_on, checked, extra, bike, sports
    quantity: int = 1
    price: int = 0

class PromoCode(BaseModel):
    code: str
    discount_percent: int
    valid_until: str
    description: str

class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    route_id: str
    passenger_count: int
    seat_numbers: List[str]
    baggage: List[BaggageItem]
    promo_code: Optional[str] = None
    carbon_offset: bool = False
    total_price: int
    status: str = "confirmed"
    booking_reference: str = Field(default_factory=lambda: f"BC{random.randint(100000, 999999)}")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    qr_code: str = ""

class BookingCreate(BaseModel):
    user_id: str
    route_id: str
    passenger_count: int
    seat_numbers: List[str]
    baggage: List[BaggageItem] = []
    promo_code: Optional[str] = None
    carbon_offset: bool = False

class TrackingInfo(BaseModel):
    booking_reference: str
    status: str  # on_time, delayed, boarding, en_route, arrived
    current_location: str
    next_stops: List[str]
    estimated_arrival: str
    delay_minutes: int = 0
    distance_remaining_km: int
    live_updates: List[str]

# === CITIES DATA ===
CAMEROON_CITIES = [
    # Centre Region
    {"name": "Yaoundé", "region": "Centre", "lat": 3.8667, "lng": 11.5167},
    {"name": "Mbalmayo", "region": "Centre", "lat": 3.5167, "lng": 11.5000},
    {"name": "Akonolinga", "region": "Centre", "lat": 3.7667, "lng": 12.2500},
    {"name": "Bafia", "region": "Centre", "lat": 4.7500, "lng": 11.2333},
    {"name": "Mfou", "region": "Centre", "lat": 3.7167, "lng": 11.6833},
    {"name": "Obala", "region": "Centre", "lat": 4.1667, "lng": 11.5333},
    {"name": "Ntui", "region": "Centre", "lat": 4.8167, "lng": 11.6333},
    {"name": "Monatélé", "region": "Centre", "lat": 3.7000, "lng": 11.3667},
    
    # Littoral Region  
    {"name": "Douala", "region": "Littoral", "lat": 4.0611, "lng": 9.7067},
    {"name": "Edéa", "region": "Littoral", "lat": 3.7833, "lng": 10.1333},
    {"name": "Nkongsamba", "region": "Littoral", "lat": 4.9500, "lng": 9.9333},
    {"name": "Loum", "region": "Littoral", "lat": 4.7167, "lng": 9.7333},
    {"name": "Mbanga", "region": "Littoral", "lat": 4.4833, "lng": 9.5667},
    {"name": "Manjo", "region": "Littoral", "lat": 4.8167, "lng": 9.8333},
    {"name": "Dizangué", "region": "Littoral", "lat": 3.6833, "lng": 10.6167},
    
    # Ouest Region
    {"name": "Bafoussam", "region": "Ouest", "lat": 5.4667, "lng": 10.4167},
    {"name": "Dschang", "region": "Ouest", "lat": 5.4500, "lng": 10.0500},
    {"name": "Mbouda", "region": "Ouest", "lat": 5.6167, "lng": 10.2500},
    {"name": "Bandjoun", "region": "Ouest", "lat": 5.3667, "lng": 10.4000},
    {"name": "Bangangté", "region": "Ouest", "lat": 5.1500, "lng": 10.5167},
    {"name": "Foumban", "region": "Ouest", "lat": 5.7167, "lng": 10.9000},
    {"name": "Kékem", "region": "Ouest", "lat": 5.3500, "lng": 10.0833},
    {"name": "Bafang", "region": "Ouest", "lat": 5.1667, "lng": 10.1833},
    
    # Nord-Ouest Region
    {"name": "Bamenda", "region": "Nord-Ouest", "lat": 5.9667, "lng": 10.1667},
    {"name": "Kumbo", "region": "Nord-Ouest", "lat": 6.2000, "lng": 10.6833},
    {"name": "Wum", "region": "Nord-Ouest", "lat": 6.3833, "lng": 10.0667},
    {"name": "Ndop", "region": "Nord-Ouest", "lat": 6.0167, "lng": 10.4500},
    {"name": "Mbengwi", "region": "Nord-Ouest", "lat": 6.1667, "lng": 9.9333},
    {"name": "Fundong", "region": "Nord-Ouest", "lat": 6.2333, "lng": 10.2833},
    
    # Sud-Ouest Region  
    {"name": "Buéa", "region": "Sud-Ouest", "lat": 4.1500, "lng": 9.2833},
    {"name": "Limbe", "region": "Sud-Ouest", "lat": 4.0167, "lng": 9.2000},
    {"name": "Kumba", "region": "Sud-Ouest", "lat": 4.6333, "lng": 9.4500},
    {"name": "Tiko", "region": "Sud-Ouest", "lat": 4.0667, "lng": 9.3667},
    {"name": "Mamfé", "region": "Sud-Ouest", "lat": 5.7667, "lng": 9.3000},
    {"name": "Tombel", "region": "Sud-Ouest", "lat": 4.6167, "lng": 9.6000},
    {"name": "Bangem", "region": "Sud-Ouest", "lat": 4.8167, "lng": 9.7667},
    
    # Sud Region
    {"name": "Ebolowa", "region": "Sud", "lat": 2.9167, "lng": 11.1500},
    {"name": "Kribi", "region": "Sud", "lat": 2.9333, "lng": 9.9167},
    {"name": "Sangmélima", "region": "Sud", "lat": 2.9167, "lng": 11.9833},
    {"name": "Ambam", "region": "Sud", "lat": 2.3833, "lng": 11.2667},
    {"name": "Campo", "region": "Sud", "lat": 2.3667, "lng": 9.8167},
    {"name": "Lolodorf", "region": "Sud", "lat": 3.2333, "lng": 10.7333},
    
    # Est Region
    {"name": "Bertoua", "region": "Est", "lat": 4.5833, "lng": 13.6833},
    {"name": "Batouri", "region": "Est", "lat": 4.4333, "lng": 14.3667},
    {"name": "Yokadouma", "region": "Est", "lat": 3.5167, "lng": 15.0833},
    {"name": "Abong-Mbang", "region": "Est", "lat": 3.9833, "lng": 13.1833},
    {"name": "Doumé", "region": "Est", "lat": 4.2333, "lng": 13.1500},
    
    # Adamaoua Region
    {"name": "Ngaoundéré", "region": "Adamaoua", "lat": 7.3167, "lng": 13.5833},
    {"name": "Meiganga", "region": "Adamaoua", "lat": 6.5167, "lng": 14.2833},
    {"name": "Tibati", "region": "Adamaoua", "lat": 6.4667, "lng": 12.6167},
    {"name": "Banyo", "region": "Adamaoua", "lat": 6.7500, "lng": 11.8167},
    {"name": "Tignère", "region": "Adamaoua", "lat": 7.3667, "lng": 12.6500},
    
    # Nord Region
    {"name": "Garoua", "region": "Nord", "lat": 9.3000, "lng": 13.4000},
    {"name": "Maroua", "region": "Nord", "lat": 10.5833, "lng": 14.3167},
    {"name": "Guider", "region": "Nord", "lat": 9.9333, "lng": 13.9500},
    {"name": "Mokolo", "region": "Nord", "lat": 10.7333, "lng": 13.8000},
    {"name": "Yagoua", "region": "Nord", "lat": 10.3333, "lng": 15.2333},
    {"name": "Kaélé", "region": "Nord", "lat": 10.1000, "lng": 14.4500},
    
    # Extrême-Nord Region
    {"name": "Kousseri", "region": "Extrême-Nord", "lat": 12.0833, "lng": 15.0333},
    {"name": "Mora", "region": "Extrême-Nord", "lat": 11.0500, "lng": 14.1333},
    {"name": "Waza", "region": "Extrême-Nord", "lat": 11.3833, "lng": 14.6333},
    {"name": "Kolofata", "region": "Extrême-Nord", "lat": 10.9667, "lng": 14.3000}
]

BUS_COMPANIES = [
    "Express Union", "Touristique Express", "Central Voyages", "Binam Voyages", 
    "Vatican Transport", "Transcam Transport", "Guaranti Express", "Musango Transport"
]

PROMO_CODES = [
    {"code": "BIENVENUE20", "discount_percent": 20, "valid_until": "2025-12-31", "description": "20% de réduction pour les nouveaux clients"},
    {"code": "WEEKEND15", "discount_percent": 15, "valid_until": "2025-12-31", "description": "15% de réduction pour les voyages du weekend"},
    {"code": "ETUDIANT10", "discount_percent": 10, "valid_until": "2025-12-31", "description": "10% de réduction pour les étudiants"},
    {"code": "FIDELITE", "discount_percent": 25, "valid_until": "2025-12-31", "description": "25% de réduction pour clients fidèles"}
]

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return int(R * c)

def generate_routes(origin_city, destination_city):
    """Generate realistic bus routes between two cities"""
    origin = next((city for city in CAMEROON_CITIES if city["name"] == origin_city), None)
    destination = next((city for city in CAMEROON_CITIES if city["name"] == destination_city), None)
    
    if not origin or not destination:
        return []
    
    distance = calculate_distance(origin["lat"], origin["lng"], destination["lat"], destination["lng"])
    
    # Generate 2-4 routes per city pair
    routes = []
    for i in range(random.randint(2, 4)):
        company = random.choice(BUS_COMPANIES)
        base_price = max(2500, distance * random.randint(45, 75))  # Price per km
        
        # Different departure times
        hour = random.randint(6, 22)
        minute = random.choice([0, 15, 30, 45])
        departure_time = f"{hour:02d}:{minute:02d}"
        
        # Calculate arrival time (average 60 km/h + stops)
        travel_hours = distance / 50 + random.uniform(0.5, 2)
        arrival_hour = (hour + int(travel_hours)) % 24
        arrival_minute = (minute + int((travel_hours % 1) * 60)) % 60
        arrival_time = f"{arrival_hour:02d}:{arrival_minute:02d}"
        
        duration = f"{int(travel_hours)}h{int((travel_hours % 1) * 60):02d}min"
        
        routes.append({
            "id": str(uuid.uuid4()),
            "origin": origin_city,
            "destination": destination_city,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "duration": duration,
            "price": base_price,
            "company": company,
            "available_seats": random.randint(15, 45),
            "total_seats": 45,
            "bus_type": random.choice(["Standard", "VIP", "Luxury"]),
            "amenities": random.sample(["WiFi", "AC", "Toilettes", "Prises USB", "Collations", "Télévision"], random.randint(2, 4)),
            "distance_km": distance
        })
    
    return routes

# === API ENDPOINTS ===

@api_router.get("/")
async def root():
    return {"message": "BusConnect Cameroun API - FlixBus Style", "version": "1.0"}

@api_router.get("/cities")
async def get_cities():
    """Get all available cities"""
    return {"cities": CAMEROON_CITIES}

@api_router.post("/search")
async def search_routes(query: SearchQuery):
    """Search for bus routes"""
    routes = generate_routes(query.origin, query.destination)
    return {"routes": routes, "total": len(routes)}

@api_router.get("/routes/popular")
async def get_popular_routes():
    """Get popular routes"""
    popular_pairs = [
        ("Yaoundé", "Douala"), ("Douala", "Bafoussam"), ("Yaoundé", "Bamenda"),
        ("Douala", "Buéa"), ("Yaoundé", "Bertoua"), ("Garoua", "Ngaoundéré")
    ]
    
    popular_routes = []
    for origin, destination in popular_pairs:
        routes = generate_routes(origin, destination)
        if routes:
            popular_routes.append(routes[0])  # Take first route
    
    return {"popular_routes": popular_routes}

@api_router.post("/users")
async def create_user(user: UserCreate):
    """Create new user"""
    user_dict = user.dict()
    user_obj = User(**user_dict)
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user by ID"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.post("/bookings")
async def create_booking(booking: BookingCreate):
    """Create new booking"""
    # Calculate total price
    base_price = 15000  # Base price, should be from route
    baggage_price = sum(item.price * item.quantity for item in booking.baggage)
    carbon_price = 500 if booking.carbon_offset else 0
    
    total_price = (base_price * booking.passenger_count) + baggage_price + carbon_price
    
    # Apply promo code if provided
    if booking.promo_code:
        promo = next((p for p in PROMO_CODES if p["code"] == booking.promo_code), None)
        if promo:
            discount = total_price * (promo["discount_percent"] / 100)
            total_price = int(total_price - discount)
    
    booking_dict = booking.dict()
    booking_dict["total_price"] = total_price
    booking_obj = Booking(**booking_dict)
    booking_obj.qr_code = f"QR_{booking_obj.booking_reference}"
    
    await db.bookings.insert_one(booking_obj.dict())
    return booking_obj

@api_router.get("/bookings/user/{user_id}")
async def get_user_bookings(user_id: str):
    """Get all bookings for a user"""
    bookings = await db.bookings.find({"user_id": user_id}).to_list(100)
    return {"bookings": bookings}

@api_router.get("/track/{reference}")
async def track_booking(reference: str):
    """Track booking in real-time"""
    # Simulate real-time tracking data
    statuses = ["on_time", "delayed", "boarding", "en_route", "arrived"]
    locations = ["Yaoundé", "Mbalmayo", "Edéa", "Douala"]
    
    tracking = TrackingInfo(
        booking_reference=reference,
        status=random.choice(statuses),
        current_location=random.choice(locations),
        next_stops=random.sample(locations, 2),
        estimated_arrival=f"{random.randint(14, 18)}:{random.randint(0, 59):02d}",
        delay_minutes=random.randint(0, 30),
        distance_remaining_km=random.randint(50, 300),
        live_updates=[
            "Bus parti à l'heure de Yaoundé",
            "Arrêt à Mbalmayo - 5 min",
            "Trafic fluide vers Edéa"
        ]
    )
    
    return tracking

@api_router.get("/offers")
async def get_offers():
    """Get current promotional offers"""
    offers = [
        {
            "id": str(uuid.uuid4()),
            "title": "Offre Weekend",
            "description": "15% de réduction sur tous les trajets du weekend",
            "discount_percent": 15,
            "code": "WEEKEND15",
            "valid_until": "2025-12-31",
            "type": "weekend_special",
            "image_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Cashback Fidélité",
            "description": "Après 5 voyages, recevez 2500 FCFA de cashback",
            "cashback_amount": 2500,
            "required_trips": 5,
            "type": "cashback",
            "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Compensation Carbone",
            "description": "Voyagez éco-responsable pour seulement 500 FCFA",
            "carbon_price": 500,
            "type": "carbon_offset",
            "image_url": "https://images.unsplash.com/photo-1569163139394-de4e4f43e4e5?w=400"
        }
    ]
    
    return {"offers": offers}

@api_router.get("/promo-codes")
async def get_promo_codes():
    """Get available promo codes"""
    return {"promo_codes": PROMO_CODES}

@api_router.post("/validate-promo/{code}")
async def validate_promo_code(code: str):
    """Validate promo code"""
    promo = next((p for p in PROMO_CODES if p["code"] == code), None)
    if not promo:
        raise HTTPException(status_code=404, detail="Code promo invalide")
    
    # Check expiry date
    from datetime import datetime
    valid_until = datetime.strptime(promo["valid_until"], "%Y-%m-%d")
    if valid_until < datetime.now():
        raise HTTPException(status_code=400, detail="Code promo expiré")
    
    return {"valid": True, "discount_percent": promo["discount_percent"], "description": promo["description"]}

@api_router.get("/baggage/options")
async def get_baggage_options():
    """Get baggage options and pricing"""
    options = [
        {
            "type": "carry_on",
            "name": "Bagage à main",
            "description": "8kg max, 42x32x25cm",
            "price": 0,
            "icon": "backpack",
            "included": True
        },
        {
            "type": "checked",
            "name": "Bagage soute",
            "description": "20kg max, 80x60x40cm",
            "price": 0,
            "icon": "suitcase",
            "included": True
        },
        {
            "type": "extra",
            "name": "Bagage supplémentaire",
            "description": "20kg max, dimensions standard",
            "price": 2500,
            "icon": "plus",
            "included": False
        },
        {
            "type": "bike",
            "name": "Transport vélo",
            "description": "Vélo standard, bien emballé",
            "price": 3000,
            "icon": "bike",
            "included": False
        },
        {
            "type": "sports",
            "name": "Équipement sportif",
            "description": "25kg max, équipement spécialisé",
            "price": 4000,
            "icon": "dumbbell",
            "included": False
        }
    ]
    
    return {"baggage_options": options}

# Include router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()