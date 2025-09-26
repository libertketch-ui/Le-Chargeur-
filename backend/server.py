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

@api_router.get("/weather/all")
async def get_all_weather():
    """Get weather for all major cities"""
    weather_data = []
    for city in ENHANCED_CAMEROON_CITIES:
        if city["major"]:
            weather = generate_weather_data(city["name"], city["region"])
            weather_data.append(weather)
    
    return {"weather_data": weather_data}

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
        
        payment_info.update({
            "merchant_code": merchant_codes.get(provider, "237001"),
            "provider": provider,
            "ussd_code": "*126#" if provider == "MTN" else "#150#",
            "instructions": f"Composez {payment_info['ussd_code']} et suivez les instructions. Code marchand: {payment_info['merchant_code']}"
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