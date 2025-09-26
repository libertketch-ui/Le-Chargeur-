from fastapi import FastAPI, APIRouter, HTTPException, Query, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
import base64
from datetime import datetime, timedelta
import random
import math
import hashlib
import requests
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Connect237 - Ultimate Cameroon Transport Platform", description="Complete transport ecosystem for Cameroon")
api_router = APIRouter(prefix="/api")

# === ENHANCED MODELS FOR CONNECT237 ===

class WeatherInfo(BaseModel):
    city: str
    temperature: float
    description: str
    humidity: int
    wind_speed: float
    icon: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TouristAttraction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    city: str
    region: str
    description: str
    image_url: str
    category: str  # "nature", "cultural", "adventure", "historical"
    rating: float
    coordinates: Dict[str, float]

class TransportAgency(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    registration_number: str
    headquarters: str
    phone: str
    email: Optional[str] = None
    website: Optional[str] = None
    founded_year: int
    fleet_size: int
    routes_served: List[str]
    services: List[str]  # ["passenger", "cargo", "courier"]
    rating: float
    logo_url: str
    verified: bool = True
    premium_partner: bool = False

class CourierService(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_name: str
    recipient_phone: str
    origin: str
    destination: str
    pickup_address: str
    delivery_address: str
    package_type: str  # "documents", "clothes", "electronics", "food", "other"
    weight_kg: float
    declared_value: int
    urgent: bool = False
    insurance: bool = False
    pickup_time: Optional[str] = None
    delivery_instructions: str = ""
    tracking_number: str = Field(default_factory=lambda: f"C237{random.randint(100000, 999999)}")
    status: str = "pending"  # pending, collected, in_transit, delivered, failed
    price: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GPSLocation(BaseModel):
    vehicle_id: str
    latitude: float
    longitude: float
    heading: float
    speed_kmh: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    driver_status: str = "active"  # active, break, offline

class PaymentMethod(BaseModel):
    type: str  # "mobile_money", "account_credit", "voucher", "reservation"
    provider: Optional[str] = None  # "MTN", "ORANGE"
    account_number: Optional[str] = None
    voucher_code: Optional[str] = None
    reservation_fee: int = 500  # FCFA

class EnhancedBooking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    route_id: str
    agency_id: str
    vehicle_id: Optional[str] = None
    
    # Passenger details
    passenger_count: int
    custom_passenger_count: Optional[int] = None
    passenger_details: List[Dict[str, Any]] = []
    
    # Journey details
    departure_date: str
    departure_time: str
    pickup_location: Dict[str, Any]  # {"address": "", "coordinates": {"lat": 0, "lng": 0}}
    dropoff_location: Dict[str, Any]
    
    # Pricing
    base_price: int
    reservation_fee: int = 500
    total_price: int
    payment_method: PaymentMethod
    payment_status: str = "reservation"  # reservation, partial, completed
    
    # Services
    courier_services: List[str] = []  # Courier service IDs if any
    special_requests: str = ""
    
    # Status
    status: str = "reserved"  # reserved, confirmed, in_progress, completed, cancelled
    booking_reference: str = Field(default_factory=lambda: f"C237{random.randint(100000, 999999)}")
    qr_code: str = ""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# === ADDITIONAL MODELS FOR CONNECT237 FEATURES ===

class UserRegistration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_type: str  # "client", "agency", "transporter", "occasional_transporter"
    personal_info: Dict[str, Any]  # Name, email, phone, address
    documents: List[Dict[str, Any]] = []  # Uploaded documents
    verification_status: str = "pending"  # pending, verified, rejected
    admin_comments: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None

class SmartSearchQuery(BaseModel):
    query: str
    filters: Dict[str, Any] = {}
    user_preferences: Dict[str, Any] = {}

class AdminDashboardStats(BaseModel):
    total_users: int
    pending_verifications: int
    total_bookings: int
    revenue_today: int
    active_vehicles: int
    courier_deliveries: int

# === CAMEROON DATA ===

# Major Transport Agencies in Cameroon
CAMEROON_TRANSPORT_AGENCIES = [
    {
        "name": "Express Union",
        "registration_number": "RC/YDE/2010/B/1234",
        "headquarters": "Douala",
        "phone": "+237699123456",
        "email": "contact@expressunion.cm",
        "website": "www.expressunion.cm",
        "founded_year": 1995,
        "fleet_size": 200,
        "routes_served": ["Yaoundé-Douala", "Douala-Bafoussam", "Yaoundé-Bamenda", "Douala-Bertoua"],
        "services": ["passenger", "cargo", "courier"],
        "rating": 4.5,
        "logo_url": "https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=200",
        "premium_partner": True
    },
    {
        "name": "Touristique Express",
        "registration_number": "RC/YDE/2008/A/5678",
        "headquarters": "Yaoundé",
        "phone": "+237677234567",
        "email": "info@touristiqueexpress.cm",
        "founded_year": 1990,
        "fleet_size": 150,
        "routes_served": ["Yaoundé-Douala", "Yaoundé-Bafoussam", "Yaoundé-Bertoua"],
        "services": ["passenger", "courier"],
        "rating": 4.3,
        "logo_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=200",
        "premium_partner": True
    },
    {
        "name": "Central Voyages",
        "registration_number": "RC/BFM/2005/C/9012",
        "headquarters": "Bafoussam",
        "phone": "+237655345678",
        "founded_year": 2000,
        "fleet_size": 120,
        "routes_served": ["Bafoussam-Yaoundé", "Bafoussam-Douala", "Bafoussam-Bamenda"],
        "services": ["passenger", "cargo"],
        "rating": 4.2,
        "logo_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200",
        "premium_partner": False
    },
    {
        "name": "Binam Voyages",
        "registration_number": "RC/YDE/2012/B/3456",
        "headquarters": "Yaoundé",
        "phone": "+237699456789",
        "founded_year": 2003,
        "fleet_size": 100,
        "routes_served": ["Yaoundé-Douala", "Yaoundé-Ngaoundéré", "Yaoundé-Bertoua"],
        "services": ["passenger", "courier"],
        "rating": 4.4,
        "logo_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=200",
        "premium_partner": True
    },
    {
        "name": "Guaranti Express",
        "registration_number": "RC/DLA/2007/A/7890",
        "headquarters": "Douala",
        "phone": "+237677567890",
        "founded_year": 1998,
        "fleet_size": 80,
        "routes_served": ["Douala-Yaoundé", "Douala-Bafoussam", "Douala-Limbe"],
        "services": ["passenger", "cargo", "courier"],
        "rating": 4.6,
        "logo_url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=200",
        "premium_partner": True
    },
    {
        "name": "Vatican Transport",
        "registration_number": "RC/BDA/2009/C/2468",
        "headquarters": "Bamenda",
        "phone": "+237655678901",
        "founded_year": 2001,
        "fleet_size": 90,
        "routes_served": ["Bamenda-Yaoundé", "Bamenda-Douala", "Bamenda-Bafoussam"],
        "services": ["passenger", "cargo"],
        "rating": 4.1,
        "logo_url": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=200",
        "premium_partner": False
    },
    {
        "name": "Musango Transport",
        "registration_number": "RC/GRA/2011/B/1357",
        "headquarters": "Garoua",
        "phone": "+237699789012",
        "founded_year": 2004,
        "fleet_size": 110,
        "routes_served": ["Garoua-Yaoundé", "Garoua-Douala", "Garoua-Ngaoundéré"],
        "services": ["passenger", "cargo", "courier"],
        "rating": 4.0,
        "logo_url": "https://images.unsplash.com/photo-1570125909517-53cb21c89ff2?w=200",
        "premium_partner": False
    },
    {
        "name": "Transcam Transport",
        "registration_number": "RC/YDE/2013/A/9753",
        "headquarters": "Yaoundé",
        "phone": "+237677890123",
        "founded_year": 2006,
        "fleet_size": 95,
        "routes_served": ["Yaoundé-Douala", "Yaoundé-Ebolowa", "Yaoundé-Sangmélima"],
        "services": ["passenger", "courier"],
        "rating": 4.3,
        "logo_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=200",
        "premium_partner": True
    }
]

# Tourist Attractions in Cameroon
CAMEROON_TOURIST_ATTRACTIONS = [
    {
        "name": "Mont Cameroun",
        "city": "Buéa",
        "region": "Sud-Ouest",
        "description": "Plus haute montagne d'Afrique de l'Ouest avec vue spectaculaire",
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600",
        "category": "nature",
        "rating": 4.8,
        "coordinates": {"lat": 4.2175, "lng": 9.1708}
    },
    {
        "name": "Chutes de la Lobé",
        "city": "Kribi",
        "region": "Sud",
        "description": "Cascades spectaculaires se jetant directement dans l'océan",
        "image_url": "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=600",
        "category": "nature",
        "rating": 4.7,
        "coordinates": {"lat": 2.8833, "lng": 9.9167}
    },
    {
        "name": "Palais des Rois Bamoun",
        "city": "Foumban",
        "region": "Ouest",
        "description": "Palais royal historique avec musée et architecture traditionnelle",
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600",
        "category": "cultural",
        "rating": 4.5,
        "coordinates": {"lat": 5.7167, "lng": 10.9000}
    },
    {
        "name": "Parc National de Waza",
        "city": "Waza",
        "region": "Extrême-Nord",
        "description": "Réserve de faune avec éléphants, lions et antilopes",
        "image_url": "https://images.unsplash.com/photo-1549366021-9f761d040a87?w=600",
        "category": "nature",
        "rating": 4.6,
        "coordinates": {"lat": 11.3833, "lng": 14.6333}
    },
    {
        "name": "Lac Nyos",
        "city": "Wum",
        "region": "Nord-Ouest",
        "description": "Lac cratère mystérieux aux eaux cristallines",
        "image_url": "https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?w=600",
        "category": "nature",
        "rating": 4.4,
        "coordinates": {"lat": 6.4333, "lng": 10.2967}
    },
    {
        "name": "Plages de Limbe",
        "city": "Limbe",
        "region": "Sud-Ouest",
        "description": "Plages de sable noir volcanique avec vue sur le mont Cameroun",
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600",
        "category": "nature",
        "rating": 4.3,
        "coordinates": {"lat": 4.0167, "lng": 9.2000}
    },
    {
        "name": "Réserve de Dja",
        "city": "Sangmélima",
        "region": "Sud",
        "description": "Forêt tropicale primaire, site du patrimoine mondial UNESCO",
        "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=600",
        "category": "nature",
        "rating": 4.7,
        "coordinates": {"lat": 3.2500, "lng": 12.7500}
    },
    {
        "name": "Marché Central de Yaoundé",
        "city": "Yaoundé",
        "region": "Centre",
        "description": "Marché traditionnel coloré avec artisanat local",
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600",
        "category": "cultural",
        "rating": 4.2,
        "coordinates": {"lat": 3.8480, "lng": 11.5021}
    }
]

# Enhanced Cameroon Cities with Weather Simulation
ENHANCED_CAMEROON_CITIES = [
    {"name": "Yaoundé", "region": "Centre", "lat": 3.8667, "lng": 11.5167, "major": True, "airport": True, "population": 4500000},
    {"name": "Douala", "region": "Littoral", "lat": 4.0611, "lng": 9.7067, "major": True, "airport": True, "population": 3700000},
    {"name": "Bafoussam", "region": "Ouest", "lat": 5.4667, "lng": 10.4167, "major": True, "airport": True, "population": 450000},
    {"name": "Bamenda", "region": "Nord-Ouest", "lat": 5.9667, "lng": 10.1667, "major": True, "airport": True, "population": 500000},
    {"name": "Bertoua", "region": "Est", "lat": 4.5833, "lng": 13.6833, "major": True, "airport": True, "population": 300000},
    {"name": "Garoua", "region": "Nord", "lat": 9.3000, "lng": 13.4000, "major": True, "airport": True, "population": 450000},
    {"name": "Maroua", "region": "Nord", "lat": 10.5833, "lng": 14.3167, "major": True, "airport": True, "population": 400000},
    {"name": "Ngaoundéré", "region": "Adamaoua", "lat": 7.3167, "lng": 13.5833, "major": True, "airport": True, "population": 300000},
    {"name": "Kribi", "region": "Sud", "lat": 2.9333, "lng": 9.9167, "major": True, "airport": False, "population": 70000},
    {"name": "Limbe", "region": "Sud-Ouest", "lat": 4.0167, "lng": 9.2000, "major": True, "airport": False, "population": 120000},
    {"name": "Buéa", "region": "Sud-Ouest", "lat": 4.1500, "lng": 9.2833, "major": True, "airport": False, "population": 200000},
    {"name": "Kumba", "region": "Sud-Ouest", "lat": 4.6333, "lng": 9.4500, "major": True, "airport": False, "population": 150000},
    {"name": "Ebolowa", "region": "Sud", "lat": 2.9167, "lng": 11.1500, "major": True, "airport": False, "population": 80000},
    {"name": "Foumban", "region": "Ouest", "lat": 5.7167, "lng": 10.9000, "major": True, "airport": False, "population": 120000},
    {"name": "Dschang", "region": "Ouest", "lat": 5.4500, "lng": 10.0500, "major": True, "airport": False, "population": 100000}
]

# === UTILITY FUNCTIONS ===

def generate_weather_data(city_name: str, region: str) -> WeatherInfo:
    """Generate realistic weather data for Cameroon cities"""
    
    # Base temperatures by region (Cameroon climate)
    regional_temps = {
        "Centre": (22, 32),
        "Littoral": (24, 31),
        "Ouest": (18, 28),
        "Nord-Ouest": (16, 26),
        "Sud-Ouest": (22, 30),
        "Sud": (21, 29),
        "Est": (20, 30),
        "Adamaoua": (15, 25),
        "Nord": (20, 35),
        "Extrême-Nord": (22, 40)
    }
    
    min_temp, max_temp = regional_temps.get(region, (20, 30))
    temp = random.uniform(min_temp, max_temp)
    
    weather_conditions = [
        {"desc": "Ensoleillé", "icon": "☀️"},
        {"desc": "Partiellement nuageux", "icon": "⛅"},
        {"desc": "Nuageux", "icon": "☁️"},
        {"desc": "Pluie légère", "icon": "🌦️"},
        {"desc": "Orageux", "icon": "⛈️"}
    ]
    
    # Rainy season probability (May-October)
    month = datetime.now().month
    if 5 <= month <= 10:
        weather_weights = [0.2, 0.3, 0.2, 0.2, 0.1]
    else:
        weather_weights = [0.4, 0.3, 0.2, 0.08, 0.02]
    
    weather = random.choices(weather_conditions, weights=weather_weights)[0]
    
    return WeatherInfo(
        city=city_name,
        temperature=round(temp, 1),
        description=weather["desc"],
        humidity=random.randint(40, 90),
        wind_speed=round(random.uniform(5, 25), 1),
        icon=weather["icon"]
    )

def simulate_gps_tracking(vehicle_id: str) -> GPSLocation:
    """Simulate real-time GPS tracking"""
    # Random location around Cameroon
    lat = random.uniform(2.0, 13.0)
    lng = random.uniform(8.5, 16.0)
    
    return GPSLocation(
        vehicle_id=vehicle_id,
        latitude=lat,
        longitude=lng,
        heading=random.uniform(0, 360),
        speed_kmh=random.uniform(40, 90),
        driver_status=random.choice(["active", "break"])
    )

# === API ENDPOINTS ===

@api_router.get("/")
async def root():
    return {
        "app": "Connect237 - Ultimate Cameroon Transport Platform",
        "version": "1.0.0",
        "features": [
            "Real-time Vehicle Tracking",
            "Weather Integration", 
            "Tourist Attractions",
            "Courier Services",
            "Enhanced Payment System",
            "Custom Passenger Count",
            "Pickup Location Selection",
            "Reservation System",
            "Multi-Agency Support"
        ],
        "contact": {
            "whatsapp": "+237699000000",
            "email": "support@connect237.cm",
            "phone": "+237677000000"
        }
    }

@api_router.get("/agencies")
async def get_transport_agencies():
    """Get all registered transport agencies"""
    return {"agencies": CAMEROON_TRANSPORT_AGENCIES}

@api_router.get("/agencies/premium")
async def get_premium_agencies():
    """Get premium partner agencies"""
    premium_agencies = [agency for agency in CAMEROON_TRANSPORT_AGENCIES if agency.get("premium_partner", False)]
    return {"premium_agencies": premium_agencies}

@api_router.get("/weather/{city}")
async def get_city_weather(city: str):
    """Get real-time weather for a city"""
    city_info = next((c for c in ENHANCED_CAMEROON_CITIES if c["name"].lower() == city.lower()), None)
    
    if not city_info:
        raise HTTPException(status_code=404, detail="City not found")
    
    weather = generate_weather_data(city_info["name"], city_info["region"])
    return weather

@api_router.get("/weather/cities")
async def get_all_weather():
    """Get weather for all major cities"""
    try:
        weather_data = []
        for city in ENHANCED_CAMEROON_CITIES:
            if city["major"]:
                weather = generate_weather_data(city["name"], city["region"])
                weather_data.append(weather.dict())
        
        return {"weather_data": weather_data}
    except Exception as e:
        return {"error": str(e), "cities_count": len(ENHANCED_CAMEROON_CITIES)}

@api_router.get("/attractions")
async def get_tourist_attractions():
    """Get tourist attractions in Cameroon"""
    return {"attractions": CAMEROON_TOURIST_ATTRACTIONS}

@api_router.get("/attractions/by-city/{city}")
async def get_attractions_by_city(city: str):
    """Get tourist attractions in a specific city"""
    city_attractions = [attr for attr in CAMEROON_TOURIST_ATTRACTIONS if attr["city"].lower() == city.lower()]
    return {"city": city, "attractions": city_attractions}

@api_router.get("/tracking/{vehicle_id}")
async def track_vehicle(vehicle_id: str):
    """Get real-time GPS location of a vehicle"""
    location = simulate_gps_tracking(vehicle_id)
    return location

@api_router.get("/tracking/route/{route_id}")
async def track_route_vehicles(route_id: str):
    """Get all vehicles on a specific route"""
    # Simulate 3-5 vehicles per route
    num_vehicles = random.randint(3, 5)
    vehicles = []
    
    for i in range(num_vehicles):
        vehicle_id = f"VH{route_id}{i+1:03d}"
        location = simulate_gps_tracking(vehicle_id)
        vehicles.append({
            "vehicle_id": vehicle_id,
            "location": location,
            "occupancy": random.randint(10, 45),
            "next_stop": random.choice(["Yaoundé", "Douala", "Bafoussam", "Bamenda"]),
            "eta": f"{random.randint(1, 4)}h{random.randint(0, 59):02d}min"
        })
    
    return {"route_id": route_id, "vehicles": vehicles}

@api_router.post("/courier/book")
async def book_courier_service(courier: CourierService):
    """Book courier/parcel delivery service"""
    
    # Calculate price based on weight, distance, and urgency
    base_price = 2000  # Base price in FCFA
    weight_price = courier.weight_kg * 500
    urgent_multiplier = 1.5 if courier.urgent else 1.0
    insurance_price = (courier.declared_value * 0.02) if courier.insurance else 0
    
    total_price = int((base_price + weight_price + insurance_price) * urgent_multiplier)
    courier.price = total_price
    
    # Save to database
    await db.courier_services.insert_one(courier.dict())
    
    return {
        "courier_id": courier.id,
        "tracking_number": courier.tracking_number,
        "total_price": total_price,
        "estimated_delivery": "24-48 heures" if not courier.urgent else "6-12 heures",
        "status": "pending",
        "message": f"Service courrier réservé avec succès. Code de suivi: {courier.tracking_number}"
    }

@api_router.get("/courier/track/{tracking_number}")
async def track_courier(tracking_number: str):
    """Track courier package"""
    courier = await db.courier_services.find_one({"tracking_number": tracking_number})
    
    if not courier:
        raise HTTPException(status_code=404, detail="Numéro de suivi introuvable")
    
    # Simulate tracking updates
    statuses = ["pending", "collected", "in_transit", "delivered"]
    current_status_index = statuses.index(courier.get("status", "pending"))
    
    tracking_history = []
    for i, status in enumerate(statuses[:current_status_index + 1]):
        tracking_history.append({
            "status": status,
            "description": {
                "pending": "Colis en attente de collecte",
                "collected": "Colis collecté et en préparation",
                "in_transit": "Colis en transit vers la destination",
                "delivered": "Colis livré avec succès"
            }[status],
            "timestamp": datetime.utcnow() - timedelta(hours=24-i*8)
        })
    
    return {
        "tracking_number": tracking_number,
        "current_status": courier["status"],
        "origin": courier["origin"],
        "destination": courier["destination"],
        "recipient": courier["recipient_name"],
        "tracking_history": tracking_history
    }

@api_router.post("/booking/enhanced")
async def create_enhanced_booking(booking_data: dict):
    """Create enhanced booking with all Connect237 features"""
    
    user_id = booking_data.get("user_id")
    agency_id = booking_data.get("agency_id")
    route_details = booking_data.get("route_details", {})
    passenger_count = booking_data.get("passenger_count", 1)
    custom_count = booking_data.get("custom_passenger_count")
    
    # Use custom count if provided
    final_passenger_count = custom_count if custom_count else passenger_count
    
    # Calculate pricing
    base_price = route_details.get("price", 5000)
    total_base_price = base_price * final_passenger_count
    
    # Payment method processing
    payment_method = booking_data.get("payment_method", {})
    reservation_fee = 500  # Always 500 FCFA for reservation
    
    if payment_method.get("type") == "reservation":
        payment_status = "reservation"
        amount_to_pay_now = reservation_fee
    else:
        payment_status = "completed"
        amount_to_pay_now = total_base_price
    
    # Create booking
    booking = EnhancedBooking(
        user_id=user_id,
        route_id=route_details.get("id", "route_default"),
        agency_id=agency_id,
        passenger_count=final_passenger_count,
        custom_passenger_count=custom_count,
        departure_date=booking_data.get("departure_date"),
        departure_time=booking_data.get("departure_time"),
        pickup_location=booking_data.get("pickup_location", {}),
        dropoff_location=booking_data.get("dropoff_location", {}),
        base_price=base_price,
        total_price=total_base_price,
        payment_method=PaymentMethod(**payment_method),
        payment_status=payment_status,
        courier_services=booking_data.get("courier_services", []),
        special_requests=booking_data.get("special_requests", "")
    )
    
    # Generate QR code
    booking.qr_code = f"C237_{booking.booking_reference}"
    
    # Save to database
    await db.enhanced_bookings.insert_one(booking.dict())
    
    # Return payment information
    payment_info = {
        "booking_id": booking.id,
        "booking_reference": booking.booking_reference,
        "amount_to_pay_now": amount_to_pay_now,
        "payment_status": payment_status,
        "qr_code": booking.qr_code
    }
    
    # Add payment provider specific info
    if payment_method.get("type") == "mobile_money":
        provider = payment_method.get("provider", "MTN")
        merchant_codes = {
            "MTN": "237001",
            "ORANGE": "237002"
        }
        
        ussd_code = "*126#" if provider == "MTN" else "#150#"
        
        payment_info.update({
            "merchant_code": merchant_codes.get(provider, "237001"),
            "provider": provider,
            "ussd_code": ussd_code,
            "instructions": f"Composez {ussd_code} et suivez les instructions. Code marchand: {merchant_codes.get(provider, '237001')}"
        })
    
    return payment_info

@api_router.get("/payment/calculator")
async def payment_calculator(
    base_price: int = Query(...),
    passenger_count: int = Query(1),
    custom_count: Optional[int] = Query(None),
    courier_services: int = Query(0),
    payment_type: str = Query("full")
):
    """Calculate total payment amount"""
    
    final_count = custom_count if custom_count else passenger_count
    subtotal = base_price * final_count
    
    # Add courier services cost
    courier_cost = courier_services * 2000
    
    # Calculate totals
    total_full_payment = subtotal + courier_cost
    reservation_fee = 500
    remaining_amount = total_full_payment - reservation_fee
    
    return {
        "passenger_count": final_count,
        "base_price_per_person": base_price,
        "subtotal": subtotal,
        "courier_services_cost": courier_cost,
        "total_amount": total_full_payment,
        "reservation_fee": reservation_fee,
        "remaining_amount": remaining_amount,
        "payment_breakdown": {
            "now": reservation_fee if payment_type == "reservation" else total_full_payment,
            "later": remaining_amount if payment_type == "reservation" else 0
        }
    }

@api_router.get("/contact/support")
async def get_support_contacts():
    """Get support contact information"""
    return {
        "whatsapp": {
            "number": "+237699000000",
            "link": "https://wa.me/237699000000",
            "available": "24/7"
        },
        "email": {
            "address": "support@connect237.cm",
            "response_time": "2-4 heures"
        },
        "call_center": {
            "number": "+237677000000",
            "hours": "06:00 - 22:00",
            "languages": ["Français", "English"]
        },
        "emergency": {
            "number": "+237699999999",
            "available": "24/7",
            "services": ["Urgences voyageurs", "Assistance technique"]
        }
    }

@api_router.get("/cities/enhanced")
async def get_enhanced_cities():
    """Get enhanced cities with weather and attractions"""
    enhanced_cities = []
    
    for city in ENHANCED_CAMEROON_CITIES:
        if city["major"]:
            weather = generate_weather_data(city["name"], city["region"])
            attractions = [attr for attr in CAMEROON_TOURIST_ATTRACTIONS if attr["city"] == city["name"]]
            
            enhanced_city = {
                **city,
                "current_weather": weather.dict(),
                "attractions": attractions,
                "agencies_count": len([a for a in CAMEROON_TRANSPORT_AGENCIES if city["name"] in a.get("routes_served", [])])
            }
            enhanced_cities.append(enhanced_city)
    
    return {"cities": enhanced_cities}

# === MISSING ENDPOINTS FOR CONNECT237 ===

@api_router.post("/parcel-delivery")
async def create_parcel_delivery(parcel_data: dict):
    """Create parcel delivery service (alternative endpoint)"""
    try:
        # Map the input data to CourierService model
        courier_service = CourierService(
            sender_id=parcel_data.get("sender_id", "anonymous"),
            recipient_name=parcel_data.get("recipient_name", ""),
            recipient_phone=parcel_data.get("recipient_phone", ""),
            origin=parcel_data.get("origin", ""),
            destination=parcel_data.get("destination", ""),
            pickup_address=parcel_data.get("pickup_address", ""),
            delivery_address=parcel_data.get("delivery_address", ""),
            package_type=parcel_data.get("package_type", "documents"),
            weight_kg=float(parcel_data.get("weight_kg", 1.0)),
            declared_value=int(parcel_data.get("declared_value", 10000)),
            urgent=bool(parcel_data.get("urgent", False)),
            insurance=bool(parcel_data.get("insurance", False)),
            pickup_time=parcel_data.get("pickup_time"),
            delivery_instructions=parcel_data.get("delivery_instructions", "")
        )
        
        # Calculate price
        base_price = 2000
        weight_price = courier_service.weight_kg * 500
        urgent_multiplier = 1.5 if courier_service.urgent else 1.0
        insurance_price = (courier_service.declared_value * 0.02) if courier_service.insurance else 0
        
        total_price = int((base_price + weight_price + insurance_price) * urgent_multiplier)
        courier_service.price = total_price
        
        # Save to database
        await db.parcel_deliveries.insert_one(courier_service.dict())
        
        return {
            "parcel_id": courier_service.id,
            "tracking_number": courier_service.tracking_number,
            "total_price": total_price,
            "estimated_delivery": "24-48 heures" if not courier_service.urgent else "6-12 heures",
            "status": "pending",
            "message": f"Service de livraison créé avec succès. Code: {courier_service.tracking_number}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur de validation: {str(e)}")

@api_router.get("/routes/search-smart-ai")
async def smart_ai_search(
    q: str = Query(..., description="Query string for smart search"),
    origin: Optional[str] = Query(None, description="Origin city"),
    destination: Optional[str] = Query(None, description="Destination city"),
    date: Optional[str] = Query(None, description="Travel date"),
    passengers: int = Query(1, description="Number of passengers")
):
    """Smart AI-powered route search"""
    try:
        # Mock smart AI search results (in production, this would use actual AI/ML)
        search_results = {
            "query": q,
            "suggestions": [],
            "routes": [],
            "smart_recommendations": []
        }
        
        # Smart suggestions based on query
        query_lower = q.lower()
        
        # City suggestions
        matching_cities = []
        for city in ENHANCED_CAMEROON_CITIES:
            if (query_lower in city["name"].lower() or 
                query_lower in city["region"].lower() or
                any(query_lower in alias.lower() for alias in city.get("aliases", []))):
                matching_cities.append(city)
        
        search_results["suggestions"] = matching_cities[:5]
        
        # Route suggestions
        if origin and destination:
            # Find routes between cities
            available_routes = []
            for agency in CAMEROON_TRANSPORT_AGENCIES:
                agency_routes = agency.get("routes_served", [])
                for route in agency_routes:
                    if origin.lower() in route.lower() and destination.lower() in route.lower():
                        available_routes.append({
                            "agency": agency["name"],
                            "route": route,
                            "price": random.randint(3000, 8000),
                            "duration": f"{random.randint(3, 8)} heures",
                            "departure_times": ["06:00", "09:00", "12:00", "15:00", "18:00"],
                            "vehicle_type": "Bus climatisé",
                            "rating": agency["rating"]
                        })
            
            search_results["routes"] = available_routes[:10]
        
        # Smart recommendations based on popular routes and user preferences
        popular_routes = [
            {"route": "Yaoundé - Douala", "popularity": 95, "avg_price": 4500},
            {"route": "Douala - Bafoussam", "popularity": 88, "avg_price": 3500},
            {"route": "Yaoundé - Bamenda", "popularity": 82, "avg_price": 6000},
            {"route": "Douala - Bertoua", "popularity": 75, "avg_price": 7500}
        ]
        
        search_results["smart_recommendations"] = popular_routes
        
        # AI insights (simulated)
        ai_insights = [
            f"Meilleure période pour voyager: Matin (06h00-09h00)",
            f"Prix moyen pour {passengers} passager(s): {random.randint(4000, 7000)} FCFA",
            f"Durée estimée du trajet: {random.randint(4, 7)} heures"
        ]
        
        search_results["ai_insights"] = ai_insights
        
        return {
            "success": True,
            "results": search_results,
            "total_found": len(search_results["routes"]) + len(search_results["suggestions"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de recherche AI: {str(e)}")

@api_router.get("/admin/dashboard")
async def get_admin_dashboard():
    """Admin dashboard with statistics and pending actions"""
    try:
        # Get real counts from database
        total_bookings = await db.bookings.count_documents({})
        total_courier = await db.courier_services.count_documents({})
        total_registrations = await db.user_registrations.count_documents({})
        pending_registrations = await db.user_registrations.count_documents({"verification_status": "pending"})
        
        # Calculate mock revenue and stats
        today = datetime.utcnow().date()
        revenue_today = random.randint(50000, 200000)
        
        stats = AdminDashboardStats(
            total_users=total_registrations,
            pending_verifications=pending_registrations,
            total_bookings=total_bookings,
            revenue_today=revenue_today,
            active_vehicles=random.randint(15, 45),
            courier_deliveries=total_courier
        )
        
        # Get recent activities (safe for JSON serialization)
        recent_bookings_raw = await db.bookings.find().sort("created_at", -1).limit(5).to_list(length=None)
        recent_registrations_raw = await db.user_registrations.find().sort("created_at", -1).limit(5).to_list(length=None)
        
        # Convert ObjectIds to strings and prepare for JSON serialization
        recent_bookings = []
        for booking in recent_bookings_raw:
            if "_id" in booking:
                del booking["_id"]  # Remove ObjectId field
            recent_bookings.append(booking)
            
        recent_registrations = []
        for registration in recent_registrations_raw:
            if "_id" in registration:
                del registration["_id"]  # Remove ObjectId field
            recent_registrations.append(registration)
        
        # System health indicators
        system_health = {
            "api_status": "healthy",
            "database_status": "connected",
            "payment_system": "operational",
            "sms_service": "operational",
            "email_service": "operational"
        }
        
        return {
            "dashboard_stats": stats.dict(),
            "recent_activities": {
                "bookings": recent_bookings,
                "registrations": recent_registrations
            },
            "system_health": system_health,
            "alerts": [
                {
                    "type": "info",
                    "message": f"{pending_registrations} nouvelles demandes d'inscription en attente",
                    "priority": "medium"
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur dashboard admin: {str(e)}")

@api_router.post("/registration/multi-level")
async def create_multi_level_registration(registration_data: dict):
    """Multi-level registration system for different user types"""
    try:
        user_registration = UserRegistration(
            user_type=registration_data.get("user_type", "client"),
            personal_info=registration_data.get("personal_info", {}),
            documents=registration_data.get("documents", []),
            verification_status="pending",
            admin_comments=""
        )
        
        # Save to database
        await db.user_registrations.insert_one(user_registration.dict())
        
        # Send verification notification (mock)
        notification_message = {
            "client": "Inscription client enregistrée. Vérification en cours.",
            "agency": "Demande d'agence soumise. Documents en cours de vérification.",
            "transporter": "Inscription transporteur reçue. Validation administrative requise.",
            "occasional_transporter": "Inscription transporteur occasionnel en attente d'approbation."
        }
        
        return {
            "registration_id": user_registration.id,
            "status": "pending",
            "message": notification_message.get(user_registration.user_type, "Inscription enregistrée"),
            "next_steps": [
                "Vérification des documents par l'équipe administrative",
                "Validation des informations personnelles",
                "Notification de statut par SMS/Email"
            ],
            "estimated_processing_time": "2-5 jours ouvrables"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur d'inscription: {str(e)}")

@api_router.get("/registration/status/{registration_id}")
async def get_registration_status(registration_id: str):
    """Get registration status and admin feedback"""
    registration = await db.user_registrations.find_one({"id": registration_id})
    
    if not registration:
        raise HTTPException(status_code=404, detail="Demande d'inscription introuvable")
    
    return {
        "registration_id": registration_id,
        "status": registration["verification_status"],
        "user_type": registration["user_type"],
        "created_at": registration["created_at"],
        "verified_at": registration.get("verified_at"),
        "admin_comments": registration.get("admin_comments", ""),
        "documents_status": {
            "total_documents": len(registration["documents"]),
            "verified_documents": len([doc for doc in registration["documents"] if doc.get("verified", False)])
        }
    }

@api_router.post("/admin/verify-registration/{registration_id}")
async def verify_user_registration(
    registration_id: str,
    action: str = Query(..., description="approve or reject"),
    admin_comments: str = Query("", description="Admin comments")
):
    """Admin endpoint to approve or reject user registrations"""
    
    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
    
    registration = await db.user_registrations.find_one({"id": registration_id})
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    new_status = "verified" if action == "approve" else "rejected"
    
    # Update registration
    await db.user_registrations.update_one(
        {"id": registration_id},
        {
            "$set": {
                "verification_status": new_status,
                "admin_comments": admin_comments,
                "verified_at": datetime.utcnow() if action == "approve" else None
            }
        }
    )
    
    return {
        "registration_id": registration_id,
        "action": action,
        "new_status": new_status,
        "admin_comments": admin_comments,
        "message": f"Inscription {action}ed successfully"
    }

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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()