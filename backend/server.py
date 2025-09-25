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
app = FastAPI(title="BusConnect Cameroun API - Enhanced", description="Advanced bus booking system with Yango & Bolt features")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# === ENHANCED MODELS ===
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    phone: str
    first_name: str
    last_name: str
    user_type: str = "client"  # client, agency, transporter, occasional_transport
    status: str = "pending"  # pending, active, rejected
    documents: List[str] = []
    subscription_type: str = "standard"  # standard, premium, vip
    subscription_expires: Optional[datetime] = None
    emergency_contact: Optional[str] = None
    profile_photo: Optional[str] = None
    favorite_destinations: List[str] = []
    travel_preferences: Dict[str, Any] = {}
    loyalty_points: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    phone: str
    first_name: str
    last_name: str
    user_type: str = "client"
    documents: List[str] = []
    emergency_contact: Optional[str] = None

class ServiceClass(BaseModel):
    name: str  # economy, comfort, premium, vip, express
    price_multiplier: float
    amenities: List[str]
    description: str
    max_passengers: int

class BusStop(BaseModel):
    city: str
    stop_name: str
    coordinates: Dict[str, float]
    estimated_time: str
    stop_order: int

class BusRoute(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    base_price: int
    company: str
    available_seats: int
    total_seats: int
    service_classes: List[ServiceClass]
    amenities: List[str]
    distance_km: int
    intermediate_stops: List[BusStop] = []
    driver_info: Dict[str, Any] = {}
    vehicle_info: Dict[str, Any] = {}
    safety_features: List[str] = []
    can_schedule_advance: bool = True
    max_advance_days: int = 90

class MultiStopRequest(BaseModel):
    stops: List[Dict[str, str]]  # [{"city": "Yaoundé", "type": "pickup"}, {"city": "Bafoussam", "type": "dropoff"}]
    departure_date: str
    passengers: int = 1
    service_class: str = "economy"

class AdvancedSearchQuery(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    service_class: str = "economy"
    flexible_dates: bool = False
    max_transfers: int = 0
    prefer_direct: bool = True
    time_preference: str = "any"  # morning, afternoon, evening, any

class BaggageItem(BaseModel):
    type: str  # carry_on, checked, extra, bike, sports, fragile, documents
    quantity: int = 1
    price: int = 0
    weight_kg: Optional[float] = None
    dimensions: Optional[str] = None
    insurance: bool = False

class SafetyFeature(BaseModel):
    emergency_button: bool = True
    trip_sharing: bool = True
    audio_recording: bool = False
    driver_verification: bool = True
    real_time_monitoring: bool = True

class BookingForOther(BaseModel):
    passenger_name: str
    passenger_phone: str
    relationship: str  # family, friend, colleague
    emergency_contact: Optional[str] = None

class PromoCode(BaseModel):
    code: str
    discount_percent: int
    discount_amount: Optional[int] = None
    valid_until: str
    description: str
    usage_limit: int = 1
    min_amount: int = 0
    applicable_classes: List[str] = []

class PremiumSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plan_type: str  # monthly, yearly
    benefits: List[str]
    price: int
    auto_renewal: bool = True
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    route_id: str
    passenger_count: int
    seat_numbers: List[str]
    service_class: str = "economy"
    baggage: List[BaggageItem] = []
    promo_code: Optional[str] = None
    carbon_offset: bool = False
    total_price: int
    status: str = "confirmed"  # confirmed, cancelled, completed, in_progress
    booking_reference: str = Field(default_factory=lambda: f"BC{random.randint(100000, 999999)}")
    qr_code: str = ""
    booking_for_other: Optional[BookingForOther] = None
    safety_preferences: SafetyFeature = Field(default_factory=SafetyFeature)
    scheduled_departure: Optional[datetime] = None
    is_advance_booking: bool = False
    insurance: bool = False
    special_requests: str = ""
    rating: Optional[int] = None
    review: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BookingCreate(BaseModel):
    user_id: str
    route_id: str
    passenger_count: int
    seat_numbers: List[str]
    service_class: str = "economy"
    baggage: List[BaggageItem] = []
    promo_code: Optional[str] = None
    carbon_offset: bool = False
    booking_for_other: Optional[BookingForOther] = None
    scheduled_departure: Optional[str] = None
    insurance: bool = False
    special_requests: str = ""

class TrackingInfo(BaseModel):
    booking_reference: str
    status: str  # on_time, delayed, boarding, en_route, arrived, cancelled
    current_location: str
    next_stops: List[str]
    estimated_arrival: str
    delay_minutes: int = 0
    distance_remaining_km: int
    live_updates: List[str]
    driver_contact: Optional[str] = None
    emergency_contact: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Rating(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str
    user_id: str
    driver_rating: int
    service_rating: int
    cleanliness_rating: int
    punctuality_rating: int
    comment: str
    photos: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SupportTicket(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    booking_reference: Optional[str] = None
    category: str  # complaint, refund, lost_item, safety, general
    priority: str = "medium"  # low, medium, high, urgent
    title: str
    description: str
    status: str = "open"  # open, in_progress, resolved, closed
    attachments: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ParcelDelivery(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_name: str
    recipient_phone: str
    origin: str
    destination: str
    parcel_type: str  # documents, small_package, medium_package
    weight_kg: float
    declared_value: int
    insurance: bool = False
    delivery_instructions: str = ""
    tracking_code: str = Field(default_factory=lambda: f"PD{random.randint(100000, 999999)}")
    status: str = "pending"  # pending, collected, in_transit, delivered
    price: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

# === ENHANCED CITIES DATA ===
CAMEROON_CITIES = [
    # Centre Region
    {"name": "Yaoundé", "region": "Centre", "lat": 3.8667, "lng": 11.5167, "major": True, "airport": True},
    {"name": "Mbalmayo", "region": "Centre", "lat": 3.5167, "lng": 11.5000, "major": False, "airport": False},
    {"name": "Akonolinga", "region": "Centre", "lat": 3.7667, "lng": 12.2500, "major": False, "airport": False},
    {"name": "Bafia", "region": "Centre", "lat": 4.7500, "lng": 11.2333, "major": False, "airport": False},
    {"name": "Mfou", "region": "Centre", "lat": 3.7167, "lng": 11.6833, "major": False, "airport": False},
    {"name": "Obala", "region": "Centre", "lat": 4.1667, "lng": 11.5333, "major": False, "airport": False},
    {"name": "Ntui", "region": "Centre", "lat": 4.8167, "lng": 11.6333, "major": False, "airport": False},
    {"name": "Monatélé", "region": "Centre", "lat": 3.7000, "lng": 11.3667, "major": False, "airport": False},
    
    # Littoral Region  
    {"name": "Douala", "region": "Littoral", "lat": 4.0611, "lng": 9.7067, "major": True, "airport": True},
    {"name": "Edéa", "region": "Littoral", "lat": 3.7833, "lng": 10.1333, "major": False, "airport": False},
    {"name": "Nkongsamba", "region": "Littoral", "lat": 4.9500, "lng": 9.9333, "major": True, "airport": False},
    {"name": "Loum", "region": "Littoral", "lat": 4.7167, "lng": 9.7333, "major": False, "airport": False},
    {"name": "Mbanga", "region": "Littoral", "lat": 4.4833, "lng": 9.5667, "major": False, "airport": False},
    {"name": "Manjo", "region": "Littoral", "lat": 4.8167, "lng": 9.8333, "major": False, "airport": False},
    {"name": "Dizangué", "region": "Littoral", "lat": 3.6833, "lng": 10.6167, "major": False, "airport": False},
    
    # Ouest Region
    {"name": "Bafoussam", "region": "Ouest", "lat": 5.4667, "lng": 10.4167, "major": True, "airport": True},
    {"name": "Dschang", "region": "Ouest", "lat": 5.4500, "lng": 10.0500, "major": True, "airport": False},
    {"name": "Mbouda", "region": "Ouest", "lat": 5.6167, "lng": 10.2500, "major": False, "airport": False},
    {"name": "Bandjoun", "region": "Ouest", "lat": 5.3667, "lng": 10.4000, "major": False, "airport": False},
    {"name": "Bangangté", "region": "Ouest", "lat": 5.1500, "lng": 10.5167, "major": False, "airport": False},
    {"name": "Foumban", "region": "Ouest", "lat": 5.7167, "lng": 10.9000, "major": True, "airport": False},
    {"name": "Kékem", "region": "Ouest", "lat": 5.3500, "lng": 10.0833, "major": False, "airport": False},
    {"name": "Bafang", "region": "Ouest", "lat": 5.1667, "lng": 10.1833, "major": False, "airport": False},
    
    # Nord-Ouest Region
    {"name": "Bamenda", "region": "Nord-Ouest", "lat": 5.9667, "lng": 10.1667, "major": True, "airport": True},
    {"name": "Kumbo", "region": "Nord-Ouest", "lat": 6.2000, "lng": 10.6833, "major": False, "airport": False},
    {"name": "Wum", "region": "Nord-Ouest", "lat": 6.3833, "lng": 10.0667, "major": False, "airport": False},
    {"name": "Ndop", "region": "Nord-Ouest", "lat": 6.0167, "lng": 10.4500, "major": False, "airport": False},
    {"name": "Mbengwi", "region": "Nord-Ouest", "lat": 6.1667, "lng": 9.9333, "major": False, "airport": False},
    {"name": "Fundong", "region": "Nord-Ouest", "lat": 6.2333, "lng": 10.2833, "major": False, "airport": False},
    
    # Sud-Ouest Region  
    {"name": "Buéa", "region": "Sud-Ouest", "lat": 4.1500, "lng": 9.2833, "major": True, "airport": False},
    {"name": "Limbe", "region": "Sud-Ouest", "lat": 4.0167, "lng": 9.2000, "major": True, "airport": False},
    {"name": "Kumba", "region": "Sud-Ouest", "lat": 4.6333, "lng": 9.4500, "major": True, "airport": False},
    {"name": "Tiko", "region": "Sud-Ouest", "lat": 4.0667, "lng": 9.3667, "major": False, "airport": True},
    {"name": "Mamfé", "region": "Sud-Ouest", "lat": 5.7667, "lng": 9.3000, "major": False, "airport": False},
    {"name": "Tombel", "region": "Sud-Ouest", "lat": 4.6167, "lng": 9.6000, "major": False, "airport": False},
    {"name": "Bangem", "region": "Sud-Ouest", "lat": 4.8167, "lng": 9.7667, "major": False, "airport": False},
    
    # Sud Region
    {"name": "Ebolowa", "region": "Sud", "lat": 2.9167, "lng": 11.1500, "major": True, "airport": False},
    {"name": "Kribi", "region": "Sud", "lat": 2.9333, "lng": 9.9167, "major": True, "airport": False},
    {"name": "Sangmélima", "region": "Sud", "lat": 2.9167, "lng": 11.9833, "major": False, "airport": False},
    {"name": "Ambam", "region": "Sud", "lat": 2.3833, "lng": 11.2667, "major": False, "airport": False},
    {"name": "Campo", "region": "Sud", "lat": 2.3667, "lng": 9.8167, "major": False, "airport": False},
    {"name": "Lolodorf", "region": "Sud", "lat": 3.2333, "lng": 10.7333, "major": False, "airport": False},
    
    # Est Region
    {"name": "Bertoua", "region": "Est", "lat": 4.5833, "lng": 13.6833, "major": True, "airport": True},
    {"name": "Batouri", "region": "Est", "lat": 4.4333, "lng": 14.3667, "major": False, "airport": False},
    {"name": "Yokadouma", "region": "Est", "lat": 3.5167, "lng": 15.0833, "major": False, "airport": False},
    {"name": "Abong-Mbang", "region": "Est", "lat": 3.9833, "lng": 13.1833, "major": False, "airport": False},
    {"name": "Doumé", "region": "Est", "lat": 4.2333, "lng": 13.1500, "major": False, "airport": False},
    
    # Adamaoua Region
    {"name": "Ngaoundéré", "region": "Adamaoua", "lat": 7.3167, "lng": 13.5833, "major": True, "airport": True},
    {"name": "Meiganga", "region": "Adamaoua", "lat": 6.5167, "lng": 14.2833, "major": False, "airport": False},
    {"name": "Tibati", "region": "Adamaoua", "lat": 6.4667, "lng": 12.6167, "major": False, "airport": False},
    {"name": "Banyo", "region": "Adamaoua", "lat": 6.7500, "lng": 11.8167, "major": False, "airport": False},
    {"name": "Tignère", "region": "Adamaoua", "lat": 7.3667, "lng": 12.6500, "major": False, "airport": False},
    
    # Nord Region
    {"name": "Garoua", "region": "Nord", "lat": 9.3000, "lng": 13.4000, "major": True, "airport": True},
    {"name": "Maroua", "region": "Nord", "lat": 10.5833, "lng": 14.3167, "major": True, "airport": True},
    {"name": "Guider", "region": "Nord", "lat": 9.9333, "lng": 13.9500, "major": False, "airport": False},
    {"name": "Mokolo", "region": "Nord", "lat": 10.7333, "lng": 13.8000, "major": False, "airport": False},
    {"name": "Yagoua", "region": "Nord", "lat": 10.3333, "lng": 15.2333, "major": False, "airport": False},
    {"name": "Kaélé", "region": "Nord", "lat": 10.1000, "lng": 14.4500, "major": False, "airport": False},
    
    # Extrême-Nord Region
    {"name": "Kousseri", "region": "Extrême-Nord", "lat": 12.0833, "lng": 15.0333, "major": False, "airport": False},
    {"name": "Mora", "region": "Extrême-Nord", "lat": 11.0500, "lng": 14.1333, "major": False, "airport": False},
    {"name": "Waza", "region": "Extrême-Nord", "lat": 11.3833, "lng": 14.6333, "major": False, "airport": False},
    {"name": "Kolofata", "region": "Extrême-Nord", "lat": 10.9667, "lng": 14.3000, "major": False, "airport": False}
]

BUS_COMPANIES = [
    {
        "name": "Express Union", 
        "rating": 4.5, 
        "safety_rating": 4.7,
        "fleet_size": 150,
        "specialties": ["long_distance", "vip_service"]
    },
    {
        "name": "Touristique Express", 
        "rating": 4.3, 
        "safety_rating": 4.5,
        "fleet_size": 120,
        "specialties": ["comfort", "reliability"]
    },
    {
        "name": "Central Voyages", 
        "rating": 4.2, 
        "safety_rating": 4.4,
        "fleet_size": 100,
        "specialties": ["affordable", "frequent"]
    },
    {
        "name": "Binam Voyages", 
        "rating": 4.4, 
        "safety_rating": 4.6,
        "fleet_size": 80,
        "specialties": ["premium", "punctuality"]
    },
    {
        "name": "Vatican Transport", 
        "rating": 4.1, 
        "safety_rating": 4.3,
        "fleet_size": 90,
        "specialties": ["economy", "regional"]
    },
    {
        "name": "Transcam Transport", 
        "rating": 4.3, 
        "safety_rating": 4.5,
        "fleet_size": 110,
        "specialties": ["intercity", "comfort"]
    },
    {
        "name": "Guaranti Express", 
        "rating": 4.6, 
        "safety_rating": 4.8,
        "fleet_size": 75,
        "specialties": ["luxury", "safety"]
    },
    {
        "name": "Musango Transport", 
        "rating": 4.0, 
        "safety_rating": 4.2,
        "fleet_size": 95,
        "specialties": ["budget", "coverage"]
    }
]

SERVICE_CLASSES = [
    {
        "name": "economy",
        "display_name": "Économie",
        "price_multiplier": 1.0,
        "amenities": ["Siège standard", "Bagages inclus"],
        "description": "Service de base confortable et abordable",
        "max_passengers": 45
    },
    {
        "name": "comfort",
        "display_name": "Confort",
        "price_multiplier": 1.3,
        "amenities": ["Sièges inclinables", "WiFi", "Collations", "Prises USB"],
        "description": "Plus d'espace et de commodités",
        "max_passengers": 35
    },
    {
        "name": "premium",
        "display_name": "Premium",
        "price_multiplier": 1.6,
        "amenities": ["Sièges cuir", "Repas inclus", "WiFi premium", "Divertissement", "Service personnalisé"],
        "description": "Expérience de voyage de luxe",
        "max_passengers": 28
    },
    {
        "name": "vip",
        "display_name": "VIP",
        "price_multiplier": 2.0,
        "amenities": ["Cabines privées", "Service concierge", "Repas gastronomique", "WiFi haut débit", "Chauffeur dédié"],
        "description": "Service exclusif de première classe",
        "max_passengers": 16
    },
    {
        "name": "express",
        "display_name": "Express",
        "price_multiplier": 1.4,
        "amenities": ["Trajet direct", "WiFi", "Collations", "Arrivée garantie"],
        "description": "Trajet rapide sans arrêts intermédiaires",
        "max_passengers": 40
    }
]

ENHANCED_PROMO_CODES = [
    {"code": "BIENVENUE25", "discount_percent": 25, "valid_until": "2025-12-31", "description": "25% de réduction pour les nouveaux clients", "usage_limit": 1, "min_amount": 5000},
    {"code": "WEEKEND15", "discount_percent": 15, "valid_until": "2025-12-31", "description": "15% de réduction pour les voyages du weekend", "usage_limit": 5, "min_amount": 3000},
    {"code": "ETUDIANT20", "discount_percent": 20, "valid_until": "2025-12-31", "description": "20% de réduction pour les étudiants", "usage_limit": 10, "min_amount": 2000},
    {"code": "FIDELITE30", "discount_percent": 30, "valid_until": "2025-12-31", "description": "30% de réduction pour clients fidèles", "usage_limit": 3, "min_amount": 10000},
    {"code": "FAMILLE10", "discount_percent": 10, "valid_until": "2025-12-31", "description": "10% de réduction pour les familles (3+ personnes)", "usage_limit": 20, "min_amount": 15000},
    {"code": "PREMIUM50", "discount_amount": 5000, "valid_until": "2025-12-31", "description": "5000 FCFA de réduction sur les classes Premium", "usage_limit": 1, "min_amount": 20000, "applicable_classes": ["premium", "vip"]},
    {"code": "NOEL2024", "discount_percent": 40, "valid_until": "2025-01-31", "description": "Offre spéciale Nouvel An", "usage_limit": 1, "min_amount": 8000}
]

PREMIUM_BENEFITS = [
    "Réservation prioritaire",
    "Annulation gratuite jusqu'à 2h avant le départ",
    "Sélection de siège gratuite",
    "Support client 24/7",
    "Bagages supplémentaires gratuits",
    "Accès aux salons d'attente",
    "Remise de 10% sur tous les trajets",
    "Points fidélité doublés"
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

def generate_intermediate_stops(origin_city, destination_city, distance):
    """Generate intermediate stops between two cities"""
    stops = []
    if distance > 200:  # Add stops for longer journeys
        potential_stops = [city for city in CAMEROON_CITIES if city["major"]]
        # Simple logic to add 1-2 intermediate stops
        num_stops = min(2, distance // 150)
        for i in range(num_stops):
            stop = random.choice(potential_stops)
            if stop["name"] not in [origin_city, destination_city]:
                stops.append(BusStop(
                    city=stop["name"],
                    stop_name=f"Gare routière {stop['name']}",
                    coordinates={"lat": stop["lat"], "lng": stop["lng"]},
                    estimated_time=f"{random.randint(5, 20)} min",
                    stop_order=i + 1
                ))
    return stops

def get_service_class_info(class_name):
    """Get service class information"""
    return next((sc for sc in SERVICE_CLASSES if sc["name"] == class_name), SERVICE_CLASSES[0])

def generate_enhanced_routes(origin_city, destination_city, service_class="economy"):
    """Generate enhanced bus routes with multiple service classes"""
    origin = next((city for city in CAMEROON_CITIES if city["name"] == origin_city), None)
    destination = next((city for city in CAMEROON_CITIES if city["name"] == destination_city), None)
    
    if not origin or not destination:
        return []
    
    distance = calculate_distance(origin["lat"], origin["lng"], destination["lat"], destination["lng"])
    
    routes = []
    for i in range(random.randint(2, 5)):
        company = random.choice(BUS_COMPANIES)
        service_info = get_service_class_info(service_class)
        
        base_price = max(3000, distance * random.randint(50, 85))
        final_price = int(base_price * service_info["price_multiplier"])
        
        # Generate departure time
        hour = random.randint(5, 23)
        minute = random.choice([0, 15, 30, 45])
        departure_time = f"{hour:02d}:{minute:02d}"
        
        # Calculate arrival time
        travel_hours = (distance / 55) + random.uniform(0.5, 2)  # Account for stops and traffic
        arrival_hour = (hour + int(travel_hours)) % 24
        arrival_minute = (minute + int((travel_hours % 1) * 60)) % 60
        arrival_time = f"{arrival_hour:02d}:{arrival_minute:02d}"
        
        duration = f"{int(travel_hours)}h{int((travel_hours % 1) * 60):02d}min"
        
        # Generate driver and vehicle info
        driver_names = ["Mamadou Diallo", "Jean Baptiste", "Hassan Njoya", "Pierre Talla", "Ibrahim Souley"]
        vehicle_plates = [f"CM-{random.randint(1000, 9999)}-{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}"]
        
        route = BusRoute(
            id=str(uuid.uuid4()),
            origin=origin_city,
            destination=destination_city,
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration=duration,
            base_price=final_price,
            company=company["name"],
            available_seats=random.randint(int(service_info["max_passengers"] * 0.3), service_info["max_passengers"]),
            total_seats=service_info["max_passengers"],
            service_classes=[ServiceClass(
                name=service_info["name"],
                price_multiplier=service_info["price_multiplier"],
                amenities=service_info["amenities"],
                description=service_info["description"],
                max_passengers=service_info["max_passengers"]
            )],
            amenities=service_info["amenities"],
            distance_km=distance,
            intermediate_stops=generate_intermediate_stops(origin_city, destination_city, distance),
            driver_info={
                "name": random.choice(driver_names),
                "rating": round(random.uniform(4.0, 5.0), 1),
                "experience_years": random.randint(5, 20),
                "license_number": f"DL{random.randint(100000, 999999)}",
                "phone": f"+237{random.randint(600000000, 699999999)}"
            },
            vehicle_info={
                "plate_number": random.choice(vehicle_plates),
                "model": random.choice(["Mercedes Sprinter", "Iveco Daily", "Toyota Hiace", "Hyundai Universe"]),
                "year": random.randint(2018, 2024),
                "capacity": service_info["max_passengers"],
                "features": service_info["amenities"]
            },
            safety_features=[
                "Ceintures de sécurité", "Extincteur", "Trousse de secours", 
                "GPS tracking", "Caméras de surveillance", "Communication radio"
            ],
            can_schedule_advance=True,
            max_advance_days=90
        )
        
        routes.append(route)
    
    return routes

# === ENHANCED API ENDPOINTS ===

@api_router.get("/")
async def root():
    return {"message": "BusConnect Cameroun API - Enhanced with Yango & Bolt Features", "version": "2.0"}

@api_router.get("/cities")
async def get_cities():
    """Get all available cities with enhanced information"""
    return {"cities": CAMEROON_CITIES}

@api_router.get("/cities/popular")
async def get_popular_cities():
    """Get popular destinations based on user data"""
    popular = [city for city in CAMEROON_CITIES if city.get("major", False)]
    return {"popular_cities": popular[:10]}

@api_router.post("/search/advanced")
async def advanced_search(query: AdvancedSearchQuery):
    """Advanced search with flexible dates, service classes, and preferences"""
    routes = generate_enhanced_routes(query.origin, query.destination, query.service_class)
    
    # Apply filters
    if query.prefer_direct:
        routes = [r for r in routes if len(r.intermediate_stops) <= 1]
    
    if query.time_preference != "any":
        time_filters = {
            "morning": (5, 12),
            "afternoon": (12, 18),
            "evening": (18, 23)
        }
        start_hour, end_hour = time_filters.get(query.time_preference, (0, 24))
        routes = [r for r in routes if start_hour <= int(r.departure_time.split(':')[0]) < end_hour]
    
    return {
        "routes": [r.dict() for r in routes], 
        "total": len(routes),
        "search_params": query.dict()
    }

@api_router.post("/search/multi-stop")
async def multi_stop_search(query: MultiStopRequest):
    """Search for routes with multiple stops"""
    # This is a simplified version - in reality, you'd need complex routing algorithms
    all_routes = []
    
    for i in range(len(query.stops) - 1):
        current_stop = query.stops[i]
        next_stop = query.stops[i + 1]
        
        routes = generate_enhanced_routes(
            current_stop["city"], 
            next_stop["city"], 
            query.service_class
        )
        all_routes.extend(routes)
    
    return {"routes": [r.dict() for r in all_routes], "total": len(all_routes)}

@api_router.get("/suggestions/{user_id}")
async def get_smart_suggestions(user_id: str):
    """Get intelligent destination suggestions based on user history"""
    # This would typically analyze user's booking history
    # For now, return popular routes
    suggestions = [
        {"destination": "Douala", "reason": "Voyage fréquent", "discount": 10},
        {"destination": "Bafoussam", "reason": "Nouvelle destination", "discount": 15},
        {"destination": "Bamenda", "reason": "Recommandé pour vous", "discount": 5}
    ]
    
    return {"suggestions": suggestions}

@api_router.post("/users/enhanced")
async def create_enhanced_user(user: UserCreate):
    """Create new user with enhanced profile"""
    user_dict = user.dict()
    user_obj = User(**user_dict)
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get enhanced user profile"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's booking statistics
    bookings = await db.bookings.find({"user_id": user_id}).to_list(100)
    
    profile_stats = {
        "total_trips": len(bookings),
        "total_spent": sum(b.get("total_price", 0) for b in bookings),
        "favorite_destinations": user.get("favorite_destinations", []),
        "loyalty_points": user.get("loyalty_points", 0),
        "subscription_type": user.get("subscription_type", "standard")
    }
    
    return {"user": user, "stats": profile_stats}

@api_router.post("/bookings/enhanced")
async def create_enhanced_booking(booking: BookingCreate):
    """Create enhanced booking with all new features"""
    # Calculate total price with service class multiplier
    service_info = get_service_class_info(booking.service_class)
    base_price = 15000  # This should come from the actual route
    
    service_price = int(base_price * service_info["price_multiplier"])
    baggage_price = sum(item.price * item.quantity for item in booking.baggage)
    carbon_price = 500 if booking.carbon_offset else 0
    insurance_price = 1500 if booking.insurance else 0
    
    total_price = (service_price * booking.passenger_count) + baggage_price + carbon_price + insurance_price
    
    # Apply promo code if provided
    if booking.promo_code:
        promo = next((p for p in ENHANCED_PROMO_CODES if p["code"] == booking.promo_code), None)
        if promo and total_price >= promo.get("min_amount", 0):
            if promo.get("discount_percent"):
                discount = total_price * (promo["discount_percent"] / 100)
                total_price = int(total_price - discount)
            elif promo.get("discount_amount"):
                total_price = max(0, total_price - promo["discount_amount"])
    
    booking_dict = booking.dict()
    booking_dict["total_price"] = total_price
    booking_dict["service_class"] = booking.service_class
    
    # Handle advance booking
    if booking.scheduled_departure:
        booking_dict["scheduled_departure"] = datetime.fromisoformat(booking.scheduled_departure)
        booking_dict["is_advance_booking"] = True
    
    booking_obj = Booking(**booking_dict)
    booking_obj.qr_code = f"QR_{booking_obj.booking_reference}"
    
    await db.bookings.insert_one(booking_obj.dict())
    
    # Award loyalty points (10 points per 1000 FCFA spent)
    loyalty_points = total_price // 100
    await db.users.update_one(
        {"id": booking.user_id},
        {"$inc": {"loyalty_points": loyalty_points}}
    )
    
    return booking_obj

@api_router.get("/bookings/user/{user_id}/enhanced")
async def get_enhanced_user_bookings(user_id: str):
    """Get enhanced user bookings with full details"""
    bookings = await db.bookings.find({"user_id": user_id}).to_list(100)
    
    # Enrich bookings with route information
    for booking in bookings:
        if booking.get("route_id"):
            # In a real app, you'd fetch route details from the database
            booking["route_details"] = {
                "origin": "Yaoundé",
                "destination": "Douala",
                "company": "Express Union"
            }
    
    return {"bookings": bookings, "total": len(bookings)}

@api_router.get("/track/{reference}/enhanced")
async def track_booking_enhanced(reference: str):
    """Enhanced tracking with safety features"""
    # Get booking details
    booking = await db.bookings.find_one({"booking_reference": reference})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Simulate enhanced tracking data
    statuses = ["on_time", "delayed", "boarding", "en_route", "arrived"]
    locations = ["Yaoundé", "Mbalmayo", "Edéa", "Nkongsamba", "Douala"]
    
    tracking = TrackingInfo(
        booking_reference=reference,
        status=random.choice(statuses),
        current_location=random.choice(locations),
        next_stops=random.sample(locations, 2),
        estimated_arrival=f"{random.randint(14, 20)}:{random.randint(0, 59):02d}",
        delay_minutes=random.randint(0, 45),
        distance_remaining_km=random.randint(20, 250),
        live_updates=[
            f"Bus parti à l'heure de {booking.get('origin', 'Yaoundé')}",
            "Arrêt technique - 10 min",
            "Trafic fluide, arrivée prévue dans les temps"
        ],
        driver_contact="+237650123456",
        emergency_contact="+237677888999"
    )
    
    return tracking

@api_router.get("/offers/enhanced")
async def get_enhanced_offers():
    """Get enhanced promotional offers"""
    offers = [
        {
            "id": str(uuid.uuid4()),
            "title": "Offre Premium Découverte",
            "description": "Voyagez en classe Premium pour le prix du Confort",
            "discount_percent": 25,
            "code": "PREMIUM25",
            "valid_until": "2025-12-31",
            "type": "premium_upgrade",
            "target_audience": "new_premium",
            "image_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Réservation Anticipée",
            "description": "Réservez 30 jours à l'avance et économisez 20%",
            "discount_percent": 20,
            "code": "ADVANCE20",
            "valid_until": "2025-12-31",
            "type": "early_booking",
            "min_advance_days": 30,
            "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Programme Fidélité Plus",
            "description": "Cumulez des points et débloquez des voyages gratuits",
            "cashback_amount": 5000,
            "required_trips": 10,
            "type": "loyalty_program",
            "image_url": "https://images.unsplash.com/photo-1569163139394-de4e4f43e4e5?w=400"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Abonnement Premium",
            "description": "Accès illimité aux services premium et réductions exclusives",
            "monthly_price": 15000,
            "benefits": PREMIUM_BENEFITS,
            "type": "subscription",
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
        }
    ]
    
    return {"offers": offers}

@api_router.post("/premium/subscribe")
async def subscribe_premium(user_id: str, plan_type: str = "monthly"):
    """Subscribe to premium service"""
    prices = {"monthly": 15000, "yearly": 150000}
    price = prices.get(plan_type, 15000)
    
    expires_at = datetime.utcnow() + timedelta(days=30 if plan_type == "monthly" else 365)
    
    subscription = PremiumSubscription(
        user_id=user_id,
        plan_type=plan_type,
        benefits=PREMIUM_BENEFITS,
        price=price,
        expires_at=expires_at
    )
    
    await db.subscriptions.insert_one(subscription.dict())
    
    # Update user subscription status
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "subscription_type": "premium",
                "subscription_expires": expires_at
            }
        }
    )
    
    return subscription

@api_router.post("/bookings/{booking_id}/rate")
async def rate_booking(booking_id: str, rating_data: Rating):
    """Rate and review a completed booking"""
    await db.ratings.insert_one(rating_data.dict())
    
    # Update booking with rating
    await db.bookings.update_one(
        {"id": booking_id},
        {
            "$set": {
                "rating": rating_data.service_rating,
                "review": rating_data.comment
            }
        }
    )
    
    return {"message": "Rating submitted successfully", "rating": rating_data}

@api_router.post("/support/ticket")
async def create_support_ticket(ticket: SupportTicket):
    """Create support ticket"""
    await db.support_tickets.insert_one(ticket.dict())
    return ticket

@api_router.get("/support/tickets/{user_id}")
async def get_user_tickets(user_id: str):
    """Get user's support tickets"""
    tickets = await db.support_tickets.find({"user_id": user_id}).to_list(50)
    return {"tickets": tickets}

@api_router.post("/parcel/book")
async def book_parcel_delivery(parcel: ParcelDelivery):
    """Book parcel delivery service"""
    # Calculate price based on weight and distance
    base_price = 2000
    weight_price = parcel.weight_kg * 500
    insurance_price = (parcel.declared_value * 0.02) if parcel.insurance else 0
    
    total_price = int(base_price + weight_price + insurance_price)
    parcel.price = total_price
    
    await db.parcels.insert_one(parcel.dict())
    return parcel

@api_router.get("/parcel/track/{tracking_code}")
async def track_parcel(tracking_code: str):
    """Track parcel delivery"""
    parcel = await db.parcels.find_one({"tracking_code": tracking_code})
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    
    return parcel

@api_router.get("/analytics/popular-routes")
async def get_popular_routes():
    """Get analytics on popular routes"""
    # This would typically query actual booking data
    popular = [
        {"route": "Yaoundé - Douala", "bookings": 1250, "revenue": 18750000},
        {"route": "Douala - Bafoussam", "bookings": 890, "revenue": 12450000},
        {"route": "Yaoundé - Bamenda", "bookings": 670, "revenue": 10050000},
        {"route": "Bafoussam - Dschang", "bookings": 520, "revenue": 6240000}
    ]
    return {"popular_routes": popular}

@api_router.get("/baggage/enhanced-options")
async def get_enhanced_baggage_options():
    """Get enhanced baggage options with insurance"""
    options = [
        {
            "type": "carry_on",
            "name": "Bagage à main",
            "description": "8kg max, 42x32x25cm",
            "price": 0,
            "icon": "backpack",
            "included": True,
            "insurance_available": False
        },
        {
            "type": "checked",
            "name": "Bagage soute",
            "description": "25kg max, 80x60x40cm",
            "price": 0,
            "icon": "suitcase",
            "included": True,
            "insurance_available": True,
            "insurance_price": 1000
        },
        {
            "type": "extra",
            "name": "Bagage supplémentaire",
            "description": "25kg max, dimensions standard",
            "price": 3000,
            "icon": "plus",
            "included": False,
            "insurance_available": True,
            "insurance_price": 1500
        },
        {
            "type": "bike",
            "name": "Transport vélo",
            "description": "Vélo standard, bien emballé",
            "price": 4000,
            "icon": "bike",
            "included": False,
            "insurance_available": True,
            "insurance_price": 2000
        },
        {
            "type": "sports",
            "name": "Équipement sportif",
            "description": "30kg max, équipement spécialisé",
            "price": 5000,
            "icon": "dumbbell",
            "included": False,
            "insurance_available": True,
            "insurance_price": 2500
        },
        {
            "type": "fragile",
            "name": "Objets fragiles",
            "description": "Emballage spécialisé, manutention délicate",
            "price": 6000,
            "icon": "package",
            "included": False,
            "insurance_available": True,
            "insurance_price": 3000
        },
        {
            "type": "documents",
            "name": "Documents importants",
            "description": "Transport sécurisé de documents",
            "price": 1500,
            "icon": "file-text",
            "included": False,
            "insurance_available": True,
            "insurance_price": 500
        }
    ]
    
    return {"baggage_options": options}

@api_router.get("/service-classes")
async def get_service_classes():
    """Get all available service classes"""
    return {"service_classes": SERVICE_CLASSES}

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