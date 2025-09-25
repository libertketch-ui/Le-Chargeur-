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
import hashlib

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="BusConnect Cameroun - Fusion Edition", description="Ultimate bus booking system with Yango, Bolt & TicketCam fusion")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# === FUSION MODELS (BusConnect + TicketCam) ===

# Mobile Money Integration (from TicketCam)
class MobileMoneyProvider(BaseModel):
    name: str  # "Orange Money", "MTN Money", "Express Union Mobile"
    code: str  # "OM", "MOMO", "EUM"
    fees_percent: float = 0.02
    min_amount: int = 1000
    max_amount: int = 2000000
    logo_url: str
    ussd_code: str

class MobileMoneyPayment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str
    provider: str  # OM, MOMO, EUM
    phone_number: str
    amount: int
    transaction_id: Optional[str] = None
    status: str = "pending"  # pending, success, failed, cancelled
    fees: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None

# Enhanced User with Cameroon-specific features
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    phone: str
    first_name: str
    last_name: str
    user_type: str = "client"
    status: str = "active"
    preferred_language: str = "fr"  # fr, en
    preferred_payment: str = "mobile_money"
    mobile_money_accounts: List[Dict[str, str]] = []  # [{"provider": "OM", "number": "237XXX"}]
    home_city: Optional[str] = None
    work_city: Optional[str] = None
    frequent_destinations: List[str] = []
    subscription_type: str = "standard"
    loyalty_points: int = 0
    total_trips: int = 0
    carbon_offset_trips: int = 0
    referral_code: str = Field(default_factory=lambda: f"REF{random.randint(100000, 999999)}")
    referred_by: Optional[str] = None
    profile_complete: bool = False
    documents_verified: bool = False
    emergency_contact: Optional[Dict[str, str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Enhanced Service Classes with Cameroon market pricing
class ServiceClass(BaseModel):
    name: str
    display_name: str
    price_multiplier: float
    amenities: List[str]
    description: str
    max_passengers: int
    comfort_level: int  # 1-5 stars
    popular_with: List[str]  # ["business", "families", "students", "tourists"]
    available_cities: List[str] = []  # Cities where this class is available

# Smart Route with AI-powered features
class SmartRoute(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    base_price: int
    dynamic_price: int  # AI-adjusted price based on demand
    company: str
    available_seats: int
    total_seats: int
    service_class: str
    amenities: List[str]
    distance_km: int
    route_popularity: int  # 1-100 based on bookings
    weather_impact: str = "none"  # none, light, moderate, severe
    traffic_prediction: str = "normal"  # light, normal, heavy
    intermediate_stops: List[Dict[str, Any]] = []
    driver_info: Dict[str, Any]
    vehicle_info: Dict[str, Any]
    safety_features: List[str]
    real_time_updates: List[str] = []
    carbon_footprint: float  # kg CO2 per passenger
    eco_friendly: bool = False
    price_history: List[Dict[str, Any]] = []
    demand_level: str = "normal"  # low, normal, high, peak
    promotional_rate: Optional[float] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# Enhanced Booking with full TicketCam integration
class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    route_id: str
    booking_reference: str = Field(default_factory=lambda: f"TC{random.randint(100000, 999999)}")
    passenger_count: int
    passenger_details: List[Dict[str, str]] = []
    seat_numbers: List[str]
    service_class: str = "economy"
    total_base_price: int
    taxes_and_fees: int = 0
    discount_amount: int = 0
    final_price: int
    payment_method: str = "mobile_money"
    payment_details: Optional[MobileMoneyPayment] = None
    promo_code: Optional[str] = None
    carbon_offset: bool = False
    carbon_offset_price: int = 0
    insurance: bool = False
    insurance_price: int = 0
    baggage: List[Dict[str, Any]] = []
    special_requests: str = ""
    booking_for_other: Optional[Dict[str, str]] = None
    scheduled_departure: Optional[datetime] = None
    is_advance_booking: bool = False
    status: str = "confirmed"  # pending_payment, confirmed, cancelled, completed, refunded
    qr_code: str = ""
    electronic_ticket: Dict[str, Any] = {}
    check_in_status: str = "pending"  # pending, checked_in, boarded, no_show
    rating: Optional[int] = None
    review: Optional[str] = None
    refund_policy: Dict[str, Any] = {}
    cancellation_fee: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    departure_reminder_sent: bool = False
    follow_up_sent: bool = False

# Popular Routes (TicketCam style)
class PopularRoute(BaseModel):
    origin: str
    destination: str
    base_price: int
    currency: str = "FCFA"
    weekly_bookings: int
    average_duration: str
    companies_count: int
    next_departure: str
    route_image: Optional[str] = None
    special_offer: Optional[str] = None

# Smart Notifications
class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: str  # price_drop, route_update, payment, reminder, promo
    title: str
    message: str
    action_url: Optional[str] = None
    read: bool = False
    priority: str = "normal"  # low, normal, high, urgent
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# === DATA CONSTANTS ===

# Mobile Money Providers in Cameroon
MOBILE_MONEY_PROVIDERS = [
    {
        "name": "Orange Money",
        "code": "OM",
        "fees_percent": 0.015,
        "min_amount": 500,
        "max_amount": 2000000,
        "logo_url": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=100",
        "ussd_code": "#150#"
    },
    {
        "name": "MTN Mobile Money",
        "code": "MOMO",
        "fees_percent": 0.02,
        "min_amount": 500,
        "max_amount": 2000000,
        "logo_url": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=100",
        "ussd_code": "*126#"
    },
    {
        "name": "Express Union Mobile",
        "code": "EUM",
        "fees_percent": 0.01,
        "min_amount": 1000,
        "max_amount": 5000000,
        "logo_url": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=100",
        "ussd_code": "#144#"
    }
]

# Enhanced Cameroon Cities with detailed info
CAMEROON_CITIES_ENHANCED = [
    # Major Cities (from TicketCam popular routes)
    {"name": "Yaoundé", "region": "Centre", "lat": 3.8667, "lng": 11.5167, "major": True, "airport": True, "population": 4500000, "economic_level": "high"},
    {"name": "Douala", "region": "Littoral", "lat": 4.0611, "lng": 9.7067, "major": True, "airport": True, "population": 3700000, "economic_level": "high"},
    {"name": "Bafoussam", "region": "Ouest", "lat": 5.4667, "lng": 10.4167, "major": True, "airport": True, "population": 450000, "economic_level": "medium"},
    {"name": "Bamenda", "region": "Nord-Ouest", "lat": 5.9667, "lng": 10.1667, "major": True, "airport": True, "population": 500000, "economic_level": "medium"},
    {"name": "Bertoua", "region": "Est", "lat": 4.5833, "lng": 13.6833, "major": True, "airport": True, "population": 300000, "economic_level": "medium"},
    {"name": "Garoua", "region": "Nord", "lat": 9.3000, "lng": 13.4000, "major": True, "airport": True, "population": 450000, "economic_level": "medium"},
    {"name": "Maroua", "region": "Nord", "lat": 10.5833, "lng": 14.3167, "major": True, "airport": True, "population": 400000, "economic_level": "medium"},
    {"name": "Ngaoundéré", "region": "Adamaoua", "lat": 7.3167, "lng": 13.5833, "major": True, "airport": True, "population": 300000, "economic_level": "medium"},
    # Add more cities with economic data for smart pricing...
    {"name": "Kribi", "region": "Sud", "lat": 2.9333, "lng": 9.9167, "major": True, "airport": False, "population": 70000, "economic_level": "low"},
    {"name": "Limbe", "region": "Sud-Ouest", "lat": 4.0167, "lng": 9.2000, "major": True, "airport": False, "population": 120000, "economic_level": "medium"},
]

# Enhanced Service Classes with Cameroon market reality
SERVICE_CLASSES_ENHANCED = [
    {
        "name": "economy",
        "display_name": "Économique",
        "price_multiplier": 1.0,
        "amenities": ["Siège standard", "Bagages inclus", "Arrêts fréquents"],
        "description": "Transport abordable pour tous",
        "max_passengers": 45,
        "comfort_level": 2,
        "popular_with": ["students", "daily_commuters", "budget_travelers"],
        "available_cities": [city["name"] for city in CAMEROON_CITIES_ENHANCED]
    },
    {
        "name": "comfort",
        "display_name": "Confort",
        "price_multiplier": 1.4,
        "amenities": ["Sièges inclinables", "WiFi", "Collations", "Prises USB", "Climatisation"],
        "description": "Plus de confort pour vos voyages",
        "max_passengers": 35,
        "comfort_level": 3,
        "popular_with": ["business", "families", "tourists"],
        "available_cities": ["Yaoundé", "Douala", "Bafoussam", "Bamenda", "Bertoua"]
    },
    {
        "name": "vip",
        "display_name": "VIP",
        "price_multiplier": 2.2,
        "amenities": ["Sièges cuir", "Service personnalisé", "Repas inclus", "WiFi premium", "Toilettes privées"],
        "description": "Voyage de luxe à la camerounaise",
        "max_passengers": 20,
        "comfort_level": 5,
        "popular_with": ["business", "government", "diaspora"],
        "available_cities": ["Yaoundé", "Douala", "Bafoussam"]
    },
    {
        "name": "express",
        "display_name": "Express",
        "price_multiplier": 1.7,
        "amenities": ["Trajet direct", "WiFi", "Collations", "Arrivée garantie", "Peu d'arrêts"],
        "description": "Rapide et efficace",
        "max_passengers": 40,
        "comfort_level": 4,
        "popular_with": ["business", "urgent_travel"],
        "available_cities": ["Yaoundé", "Douala", "Bafoussam", "Bamenda"]
    }
]

# Popular Routes (TicketCam integration)
POPULAR_ROUTES_DATA = [
    {
        "origin": "Yaoundé",
        "destination": "Douala", 
        "base_price": 4500,
        "weekly_bookings": 450,
        "average_duration": "4h30",
        "companies_count": 8,
        "next_departure": "06:00",
        "special_offer": "15% de réduction ce weekend"
    },
    {
        "origin": "Douala",
        "destination": "Bafoussam",
        "base_price": 3500,
        "weekly_bookings": 320,
        "average_duration": "3h45",
        "companies_count": 6,
        "next_departure": "05:30",
        "special_offer": None
    },
    {
        "origin": "Yaoundé",
        "destination": "Bertoua",
        "base_price": 5000,
        "weekly_bookings": 180,
        "average_duration": "5h15",
        "companies_count": 4,
        "next_departure": "07:00",
        "special_offer": "Nouveau: Service VIP disponible"
    },
    {
        "origin": "Yaoundé",
        "destination": "Bamenda",
        "base_price": 6500,
        "weekly_bookings": 250,
        "average_duration": "6h00",
        "companies_count": 5,
        "next_departure": "06:30",
        "special_offer": None
    }
]

# Enhanced Bus Companies with real Cameroon operators
BUS_COMPANIES_ENHANCED = [
    {
        "name": "Express Union",
        "rating": 4.5,
        "safety_rating": 4.7,
        "fleet_size": 150,
        "specialties": ["long_distance", "vip_service"],
        "payment_methods": ["OM", "MOMO", "EUM", "cash"],
        "founded_year": 1995,
        "headquarters": "Douala",
        "routes_count": 45,
        "logo_color": "#1e40af"
    },
    {
        "name": "Touristique Express",
        "rating": 4.3,
        "safety_rating": 4.5,
        "fleet_size": 120,
        "specialties": ["comfort", "reliability"],
        "payment_methods": ["OM", "MOMO", "cash"],
        "founded_year": 1990,
        "headquarters": "Yaoundé",
        "routes_count": 38,
        "logo_color": "#059669"
    },
    {
        "name": "Central Voyages",
        "rating": 4.2,
        "safety_rating": 4.4,
        "fleet_size": 100,
        "specialties": ["affordable", "frequent"],
        "payment_methods": ["MOMO", "OM", "cash"],
        "founded_year": 2000,
        "headquarters": "Bafoussam",
        "routes_count": 32,
        "logo_color": "#dc2626"
    },
    {
        "name": "Guaranti Express",
        "rating": 4.6,
        "safety_rating": 4.8,
        "fleet_size": 75,
        "specialties": ["luxury", "safety"],
        "payment_methods": ["EUM", "OM", "MOMO", "cash"],
        "founded_year": 1998,
        "headquarters": "Douala",
        "routes_count": 25,
        "logo_color": "#7c3aed"
    }
]

# === UTILITY FUNCTIONS ===

def calculate_distance(lat1, lon1, lat2, lon2):
    """Enhanced distance calculation"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return int(R * c)

def calculate_dynamic_price(base_price, demand_level, time_until_departure, service_class):
    """AI-powered dynamic pricing"""
    multiplier = 1.0
    
    # Demand-based pricing
    demand_multipliers = {"low": 0.85, "normal": 1.0, "high": 1.15, "peak": 1.35}
    multiplier *= demand_multipliers.get(demand_level, 1.0)
    
    # Time-based pricing (last minute or advance booking)
    if time_until_departure < 2:  # Less than 2 hours
        multiplier *= 1.2
    elif time_until_departure > 720:  # More than 30 days
        multiplier *= 0.9
    
    # Service class adjustment
    service_multipliers = {"economy": 1.0, "comfort": 1.4, "vip": 2.2, "express": 1.7}
    multiplier *= service_multipliers.get(service_class, 1.0)
    
    return int(base_price * multiplier)

def generate_electronic_ticket(booking):
    """Generate secure electronic ticket with QR code"""
    ticket_data = {
        "reference": booking.booking_reference,
        "passenger_name": f"{booking.passenger_details[0].get('name', 'N/A')}",
        "route": f"{booking.route_id}",
        "seats": booking.seat_numbers,
        "departure": booking.scheduled_departure.isoformat() if booking.scheduled_departure else None,
        "class": booking.service_class,
        "issued_at": datetime.utcnow().isoformat()
    }
    
    # Generate secure hash for QR code
    ticket_string = str(ticket_data)
    qr_hash = hashlib.sha256(ticket_string.encode()).hexdigest()[:16]
    
    return {
        "qr_code": f"TC_{booking.booking_reference}_{qr_hash}",
        "ticket_data": ticket_data,
        "security_hash": qr_hash,
        "mobile_display_url": f"/ticket/{booking.booking_reference}",
        "pdf_download_url": f"/ticket/{booking.booking_reference}/pdf"
    }

# === ENHANCED API ENDPOINTS ===

@api_router.get("/")
async def root():
    return {
        "message": "BusConnect Cameroun - Fusion Edition", 
        "version": "3.0",
        "features": [
            "Yandex Yango Advanced Search",
            "Bolt Security & Premium",
            "TicketCam Mobile Money Integration",
            "AI Dynamic Pricing",
            "Smart Notifications",
            "Electronic Tickets"
        ]
    }

@api_router.get("/popular-routes")
async def get_popular_routes():
    """Get popular routes with real-time data (TicketCam style)"""
    enhanced_routes = []
    
    for route_data in POPULAR_ROUTES_DATA:
        # Add real-time enhancements
        enhanced_route = {
            **route_data,
            "current_price": calculate_dynamic_price(
                route_data["base_price"], 
                random.choice(["normal", "high"]), 
                random.randint(5, 48), 
                "economy"
            ),
            "seats_available": random.randint(5, 40),
            "next_3_departures": [
                f"{6 + i}:{random.randint(0, 59):02d}" for i in range(3)
            ],
            "price_trend": random.choice(["stable", "increasing", "decreasing"]),
            "weather_status": random.choice(["clear", "rainy", "cloudy"])
        }
        enhanced_routes.append(enhanced_route)
    
    return {"popular_routes": enhanced_routes}

@api_router.get("/mobile-money/providers")
async def get_mobile_money_providers():
    """Get available mobile money providers"""
    return {"providers": MOBILE_MONEY_PROVIDERS}

@api_router.post("/mobile-money/initiate")
async def initiate_mobile_money_payment(payment_data: dict):
    """Initiate mobile money payment"""
    booking_id = payment_data.get("booking_id")
    provider = payment_data.get("provider")
    phone = payment_data.get("phone_number")
    amount = payment_data.get("amount")
    
    # Find provider
    provider_info = next((p for p in MOBILE_MONEY_PROVIDERS if p["code"] == provider), None)
    if not provider_info:
        raise HTTPException(status_code=400, detail="Invalid mobile money provider")
    
    # Calculate fees
    fees = int(amount * provider_info["fees_percent"])
    total_amount = amount + fees
    
    # Create payment record
    payment = MobileMoneyPayment(
        booking_id=booking_id,
        provider=provider,
        phone_number=phone,
        amount=amount,
        fees=fees,
        transaction_id=f"{provider}_{random.randint(100000000, 999999999)}"
    )
    
    # In real implementation, integrate with actual mobile money API
    # For demo, simulate successful initiation
    
    await db.mobile_payments.insert_one(payment.dict())
    
    return {
        "payment_id": payment.id,
        "transaction_id": payment.transaction_id,
        "ussd_code": provider_info["ussd_code"],
        "total_amount": total_amount,
        "fees": fees,
        "instructions": f"Composez {provider_info['ussd_code']} et suivez les instructions pour payer {total_amount} FCFA",
        "status": "initiated"
    }

@api_router.get("/search/smart")
async def smart_search(
    origin: str = Query(...),
    destination: str = Query(...),
    departure_date: str = Query(...),
    passengers: int = Query(1),
    service_class: str = Query("economy"),
    budget_max: Optional[int] = Query(None),
    time_preference: str = Query("any")
):
    """AI-powered smart search with dynamic pricing"""
    
    # Get city information
    origin_city = next((city for city in CAMEROON_CITIES_ENHANCED if city["name"] == origin), None)
    dest_city = next((city for city in CAMEROON_CITIES_ENHANCED if city["name"] == destination), None)
    
    if not origin_city or not dest_city:
        raise HTTPException(status_code=404, detail="City not found")
    
    distance = calculate_distance(origin_city["lat"], origin_city["lng"], dest_city["lat"], dest_city["lng"])
    
    # Generate smart routes with AI pricing
    routes = []
    
    for i in range(random.randint(3, 8)):
        company = random.choice(BUS_COMPANIES_ENHANCED)
        
        # Base price calculation considering economic levels
        base_multiplier = 1.0
        if origin_city["economic_level"] == "high" or dest_city["economic_level"] == "high":
            base_multiplier *= 1.2
        
        base_price = max(2000, int(distance * random.randint(40, 70) * base_multiplier))
        
        # AI dynamic pricing
        demand_level = random.choice(["low", "normal", "high"])
        hours_until = random.randint(1, 48)
        dynamic_price = calculate_dynamic_price(base_price, demand_level, hours_until, service_class)
        
        # Generate departure time based on preference
        if time_preference == "morning":
            hour = random.randint(5, 11)
        elif time_preference == "afternoon":
            hour = random.randint(12, 17)
        elif time_preference == "evening":
            hour = random.randint(18, 23)
        else:
            hour = random.randint(5, 23)
        
        departure_time = f"{hour:02d}:{random.randint(0, 59):02d}"
        
        # Calculate arrival
        travel_duration = (distance / 60) + random.uniform(0.5, 2)
        arrival_hour = (hour + int(travel_duration)) % 24
        arrival_minute = random.randint(0, 59)
        arrival_time = f"{arrival_hour:02d}:{arrival_minute:02d}"
        
        service_info = next((s for s in SERVICE_CLASSES_ENHANCED if s["name"] == service_class), SERVICE_CLASSES_ENHANCED[0])
        
        # Skip if budget filter doesn't match
        if budget_max and dynamic_price > budget_max:
            continue
        
        route = SmartRoute(
            origin=origin,
            destination=destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration=f"{int(travel_duration)}h{int((travel_duration % 1) * 60):02d}",
            base_price=base_price,
            dynamic_price=dynamic_price,
            company=company["name"],
            available_seats=random.randint(5, service_info["max_passengers"] - 5),
            total_seats=service_info["max_passengers"],
            service_class=service_class,
            amenities=service_info["amenities"],
            distance_km=distance,
            route_popularity=random.randint(60, 95),
            demand_level=demand_level,
            driver_info={
                "name": random.choice(["Mamadou Diallo", "Jean Baptiste", "Hassan Njoya"]),
                "rating": round(random.uniform(4.0, 5.0), 1),
                "experience_years": random.randint(5, 20)
            },
            vehicle_info={
                "model": random.choice(["Mercedes Sprinter", "Iveco Daily", "Toyota Hiace"]),
                "year": random.randint(2018, 2024),
                "plate_number": f"CM-{random.randint(1000, 9999)}-XX"
            },
            carbon_footprint=round(distance * 0.12 * (1.0 if service_class == "economy" else 1.3), 2),
            eco_friendly=random.choice([True, False])
        )
        
        routes.append(route)
    
    # Sort by price by default
    routes.sort(key=lambda r: r.dynamic_price)
    
    return {
        "routes": [r.dict() for r in routes],
        "total": len(routes),
        "search_metadata": {
            "origin_info": origin_city,
            "destination_info": dest_city,
            "distance_km": distance,
            "average_price": int(sum(r.dynamic_price for r in routes) / len(routes)) if routes else 0,
            "price_trends": "Prices are currently normal for this route"
        }
    }

@api_router.post("/bookings/fusion")
async def create_fusion_booking(booking_data: dict):
    """Create booking with full fusion features"""
    
    user_id = booking_data.get("user_id")
    route_id = booking_data.get("route_id")
    service_class = booking_data.get("service_class", "economy")
    passenger_count = booking_data.get("passenger_count", 1)
    payment_method = booking_data.get("payment_method", "mobile_money")
    
    # Generate pricing
    base_price = booking_data.get("base_price", 5000)
    service_info = next((s for s in SERVICE_CLASSES_ENHANCED if s["name"] == service_class), SERVICE_CLASSES_ENHANCED[0])
    
    total_base_price = int(base_price * service_info["price_multiplier"] * passenger_count)
    taxes_and_fees = int(total_base_price * 0.05)  # 5% taxes
    
    # Apply discounts
    discount_amount = 0
    promo_code = booking_data.get("promo_code")
    if promo_code == "WEEKEND15":
        discount_amount = int(total_base_price * 0.15)
    
    final_price = total_base_price + taxes_and_fees - discount_amount
    
    # Create booking
    booking = Booking(
        user_id=user_id,
        route_id=route_id,
        passenger_count=passenger_count,
        passenger_details=booking_data.get("passenger_details", []),
        seat_numbers=booking_data.get("seat_numbers", [f"{i}A" for i in range(1, passenger_count + 1)]),
        service_class=service_class,
        total_base_price=total_base_price,
        taxes_and_fees=taxes_and_fees,
        discount_amount=discount_amount,
        final_price=final_price,
        payment_method=payment_method,
        promo_code=promo_code,
        carbon_offset=booking_data.get("carbon_offset", False),
        insurance=booking_data.get("insurance", False),
        baggage=booking_data.get("baggage", []),
        special_requests=booking_data.get("special_requests", ""),
        refund_policy={
            "cancellation_allowed": True,
            "free_cancellation_hours": 2,
            "refund_percentage": 80
        }
    )
    
    # Generate electronic ticket
    booking.electronic_ticket = generate_electronic_ticket(booking)
    booking.qr_code = booking.electronic_ticket["qr_code"]
    
    # Save booking
    await db.bookings.insert_one(booking.dict())
    
    # If mobile money payment, create payment record
    if payment_method == "mobile_money" and booking_data.get("mobile_money_provider"):
        payment_result = await initiate_mobile_money_payment({
            "booking_id": booking.id,
            "provider": booking_data["mobile_money_provider"],
            "phone_number": booking_data["mobile_money_phone"],
            "amount": final_price
        })
        booking.payment_details = payment_result
    
    return booking

@api_router.get("/notifications/{user_id}")
async def get_user_notifications(user_id: str):
    """Get smart notifications for user"""
    
    # Generate sample smart notifications
    notifications = [
        {
            "id": str(uuid.uuid4()),
            "type": "price_drop",
            "title": "💰 Baisse de prix détectée !",
            "message": "Le trajet Yaoundé → Douala est maintenant à 3,800 FCFA (-15%)",
            "priority": "high",
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "type": "route_update",
            "title": "🚌 Nouveau service VIP disponible",
            "message": "Service VIP maintenant disponible sur Yaoundé → Bertoua",
            "priority": "normal",
            "created_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "id": str(uuid.uuid4()),
            "type": "promo",
            "title": "🎁 Offre spéciale weekend",
            "message": "15% de réduction avec le code WEEKEND15. Valable jusqu'à dimanche !",
            "priority": "high",
            "created_at": datetime.utcnow() - timedelta(hours=5)
        }
    ]
    
    return {"notifications": notifications}

@api_router.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """Get analytics dashboard data"""
    
    analytics = {
        "total_users": 15420,
        "total_bookings": 3280,
        "total_revenue": 185000000,
        "mobile_money_usage": {
            "Orange Money": 45.2,
            "MTN Mobile Money": 38.7,
            "Express Union Mobile": 16.1
        },
        "popular_service_classes": {
            "economy": 62.3,
            "comfort": 25.8,
            "express": 8.7,
            "vip": 3.2
        },
        "top_routes": [
            {"route": "Yaoundé → Douala", "bookings": 1250},
            {"route": "Douala → Bafoussam", "bookings": 890},
            {"route": "Yaoundé → Bamenda", "bookings": 650}
        ],
        "customer_satisfaction": 4.6,
        "on_time_performance": 87.3
    }
    
    return analytics

@api_router.get("/cities/enhanced")
async def get_enhanced_cities():
    """Get enhanced city information"""
    return {"cities": CAMEROON_CITIES_ENHANCED}

@api_router.get("/companies/enhanced") 
async def get_enhanced_companies():
    """Get enhanced bus company information"""
    return {"companies": BUS_COMPANIES_ENHANCED}

@api_router.get("/service-classes/enhanced")
async def get_enhanced_service_classes():
    """Get enhanced service classes"""
    return {"service_classes": SERVICE_CLASSES_ENHANCED}

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