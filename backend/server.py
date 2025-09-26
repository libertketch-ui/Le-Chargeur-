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

class Vehicle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agency_id: str
    agency_name: str
    model: str
    brand: str
    year: int
    color: str
    license_plate: str
    capacity: int
    vehicle_type: str  # "bus", "minibus", "car", "van"
    status: str = "active"  # active, maintenance, inactive
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    current_route: Optional[str] = None
    gps_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_maintenance: Optional[datetime] = None

class CourierCarrier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: str
    email: Optional[str] = None
    license_number: str
    vehicle_type: str  # "moto", "car", "van", "truck"
    coverage_areas: List[str]  # List of regions/cities they cover
    rating: float = 4.0
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AppSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    setting_key: str
    setting_value: str
    setting_type: str  # "text", "number", "boolean", "json"
    description: str
    updated_by: str  # admin user id
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PolicyDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    document_type: str  # "privacy", "terms", "conditions", "refund"
    language: str = "fr"  # Default French
    version: str = "1.0"
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# === CAMEROON DATA ===

# Agences de Transport Inter-urbain réelles du Cameroun - Toutes les 10 régions
CAMEROON_TRANSPORT_AGENCIES = [
    # RÉGION CENTRE (Yaoundé)
    {
        "name": "Touristique Express",
        "registration_number": "RC/YDE/2008/A/5678",
        "headquarters": "Yaoundé",
        "region": "Centre",
        "phone": "+237677234567",
        "email": "info@touristiqueexpress.cm",
        "website": "www.touristique.cm",
        "founded_year": 1990,
        "fleet_size": 150,
        "routes_served": ["Yaoundé-Douala", "Yaoundé-Ngaoundéré", "Yaoundé-Bertoua", "Yaoundé-Bafoussam"],
        "services": ["passenger", "courier", "tours"],
        "rating": 4.3,
        "logo_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=200",
        "premium_partner": True,
        "description": "Leader du transport vers le Nord et l'Est, bus modernes avec commodités"
    },
    {
        "name": "Binam Voyages",
        "registration_number": "RC/YDE/2012/B/3456",
        "headquarters": "Yaoundé",
        "region": "Centre", 
        "phone": "+237699456789",
        "founded_year": 2003,
        "fleet_size": 100,
        "routes_served": ["Yaoundé-Douala", "Yaoundé-Ngaoundéré", "Yaoundé-Bertoua"],
        "services": ["passenger", "courier"],
        "rating": 4.4,
        "logo_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=200",
        "premium_partner": True,
        "description": "Agence de transport et opérateur touristique de qualité"
    },

    # RÉGION LITTORAL (Douala) 
    {
        "name": "Finexs Voyages",
        "registration_number": "RC/DLA/2005/C/9012",
        "headquarters": "Douala",
        "region": "Littoral",
        "phone": "+237655345678",
        "email": "contact@finexs-voyages.net",
        "website": "finexs-voyages.net",
        "founded_year": 2000,
        "fleet_size": 120,
        "routes_served": ["Douala-Yaoundé", "Douala-Bafoussam", "Douala-Bamenda"],
        "services": ["passenger", "cargo", "VIP"],
        "rating": 4.2,
        "logo_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200",
        "premium_partner": True,
        "description": "Service VIP apprécié, agence principale à Akwa Douala"
    },
    {
        "name": "General Express Voyages",
        "registration_number": "RC/DLA/1990/A/1234",
        "headquarters": "Douala",
        "region": "Littoral",
        "phone": "+237677123456",
        "email": "info@generalexpressvoyages.com",
        "website": "generalexpressvoyages.com",
        "founded_year": 1990,
        "fleet_size": 180,
        "routes_served": ["Douala-Yaoundé", "Douala-Bafoussam", "Douala-Bamenda", "Douala-Bertoua"],
        "services": ["passenger", "cargo", "express"],
        "rating": 4.5,
        "logo_url": "https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=200",
        "premium_partner": True,
        "description": "Leader historique avec plus de 30 ans d'expérience, sécurité et confort"
    },
    {
        "name": "MEN Travel",
        "registration_number": "RC/DLA/2010/B/5678",
        "headquarters": "Douala",
        "region": "Littoral",
        "phone": "+237699234567",
        "founded_year": 2010,
        "fleet_size": 80,
        "routes_served": ["Douala-Yaoundé", "Douala-Limbe", "Douala-Edéa"],
        "services": ["passenger", "courier"],
        "rating": 4.1,
        "logo_url": "https://images.unsplash.com/photo-1506197603052-3cc9c3201bd?w=200",
        "premium_partner": False,
        "description": "Présent à Bonamoussadi, transport interurbain et envoi de colis"
    },

    # RÉGION OUEST (Bafoussam)
    {
        "name": "Central Voyages",
        "registration_number": "RC/BFM/2005/C/9012", 
        "headquarters": "Bafoussam",
        "region": "Ouest",
        "phone": "+237655345678",
        "founded_year": 2000,
        "fleet_size": 120,
        "routes_served": ["Bafoussam-Yaoundé", "Bafoussam-Douala", "Bafoussam-Bamenda"],
        "services": ["passenger", "cargo"],
        "rating": 4.2,
        "logo_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200",
        "premium_partner": False,
        "description": "Agence régionale forte dans l'Ouest Cameroun"
    },
    {
        "name": "Buca Voyages",
        "registration_number": "RC/BFM/2008/A/3456",
        "headquarters": "Bafoussam",
        "region": "Ouest",
        "phone": "+237677456789",
        "founded_year": 2008,
        "fleet_size": 90,
        "routes_served": ["Bafoussam-Dschang", "Bafoussam-Foumban", "Bafoussam-Yaoundé"],
        "services": ["passenger", "courier"],
        "rating": 4.0,
        "logo_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=200",
        "premium_partner": False,
        "description": "Desserte locale et inter-régionale dans l'Ouest"
    },

    # RÉGION NORD-OUEST (Bamenda)
    {
        "name": "Guarantee Express",
        "registration_number": "RC/BMD/2006/B/7890",
        "headquarters": "Bamenda",
        "region": "Nord-Ouest",
        "phone": "+237655567890",
        "founded_year": 2006,
        "fleet_size": 70,
        "routes_served": ["Bamenda-Yaoundé", "Bamenda-Douala", "Bamenda-Bafoussam"],
        "services": ["passenger", "cargo"],
        "rating": 3.9,
        "logo_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=200",
        "premium_partner": False,
        "description": "Transport fiable vers les centres urbains depuis Bamenda"
    },
    {
        "name": "Mezam Express",
        "registration_number": "RC/BMD/2012/A/2345",
        "headquarters": "Bamenda",
        "region": "Nord-Ouest",
        "phone": "+237699678901",
        "founded_year": 2012,
        "fleet_size": 50,
        "routes_served": ["Bamenda-Fundong", "Bamenda-Wum", "Bamenda-Ndop"],
        "services": ["passenger"],
        "rating": 3.8,
        "logo_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=200",
        "premium_partner": False,
        "description": "Desserte régionale Nord-Ouest, zones rurales"
    },

    # RÉGION SUD-OUEST (Buéa/Limbe)
    {
        "name": "Fako Express",
        "registration_number": "RC/BUE/2007/C/4567",
        "headquarters": "Buéa",
        "region": "Sud-Ouest", 
        "phone": "+237677789012",
        "founded_year": 2007,
        "fleet_size": 60,
        "routes_served": ["Buéa-Douala", "Limbe-Douala", "Buéa-Yaoundé"],
        "services": ["passenger", "courier"],
        "rating": 4.0,
        "logo_url": "https://images.unsplash.com/photo-1549366021-9f761d040a87?w=200",
        "premium_partner": False,
        "description": "Spécialiste Sud-Ouest, liaison Mont Cameroun"
    },
    {
        "name": "Southwest Transport",
        "registration_number": "RC/KBA/2010/B/8901",
        "headquarters": "Kumba",
        "region": "Sud-Ouest",
        "phone": "+237655890123",
        "founded_year": 2010,
        "fleet_size": 45,
        "routes_served": ["Kumba-Douala", "Kumba-Mamfé", "Kumba-Buéa"],
        "services": ["passenger"],
        "rating": 3.7,
        "logo_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=200",
        "premium_partner": False,
        "description": "Transport régional Sud-Ouest, desserte rurale"
    },

    # RÉGION SUD (Ebolowa)
    {
        "name": "Dja Express",
        "registration_number": "RC/EBL/2009/A/5678",
        "headquarters": "Ebolowa",
        "region": "Sud",
        "phone": "+237699901234",
        "founded_year": 2009,
        "fleet_size": 55,
        "routes_served": ["Ebolowa-Yaoundé", "Ebolowa-Sangmélima", "Ebolowa-Kribi"],
        "services": ["passenger", "courier"],
        "rating": 3.9,
        "logo_url": "https://images.unsplash.com/photo-1506197603052-3cc9c3201bd?w=200",
        "premium_partner": False,
        "description": "Desserte région Sud, liaison côtière Kribi"
    },
    {
        "name": "Océan Express", 
        "registration_number": "RC/KBI/2011/C/9012",
        "headquarters": "Kribi",
        "region": "Sud",
        "phone": "+237677012345",
        "founded_year": 2011,
        "fleet_size": 40,
        "routes_served": ["Kribi-Douala", "Kribi-Yaoundé", "Kribi-Ebolowa"],
        "services": ["passenger", "tourisme"],
        "rating": 4.1,
        "logo_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=200",
        "premium_partner": False,
        "description": "Transport côtier, spécialiste tourisme balnéaire"
    },

    # RÉGION EST (Bertoua)
    {
        "name": "Lom Express",
        "registration_number": "RC/BTA/2008/B/3456",
        "headquarters": "Bertoua",
        "region": "Est",
        "phone": "+237655123456",
        "founded_year": 2008,
        "fleet_size": 65,
        "routes_served": ["Bertoua-Yaoundé", "Bertoua-Batouri", "Bertoua-Yokadouma"],
        "services": ["passenger", "cargo"],
        "rating": 3.8,
        "logo_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=200",
        "premium_partner": False,
        "description": "Transport Est Cameroun, zones forestières"
    },
    {
        "name": "Kadey Voyages",
        "registration_number": "RC/BTI/2012/A/7890",
        "headquarters": "Batouri", 
        "region": "Est",
        "phone": "+237699234567",
        "founded_year": 2012,
        "fleet_size": 35,
        "routes_served": ["Batouri-Bertoua", "Batouri-Yokadouma", "Batouri-Yaoundé"],
        "services": ["passenger"],
        "rating": 3.6,
        "logo_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=200",
        "premium_partner": False,
        "description": "Desserte Est profond, liaisons transfrontalières"
    },

    # RÉGION ADAMAOUA (Ngaoundéré)  
    {
        "name": "Adamaoua Express",
        "registration_number": "RC/NGD/2005/C/2345",
        "headquarters": "Ngaoundéré",
        "region": "Adamaoua",
        "phone": "+237677345678",
        "founded_year": 2005,
        "fleet_size": 75,
        "routes_served": ["Ngaoundéré-Yaoundé", "Ngaoundéré-Garoua", "Ngaoundéré-Meiganga"],
        "services": ["passenger", "cargo"],
        "rating": 4.0,
        "logo_url": "https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=200",
        "premium_partner": False,
        "description": "Plaque tournante Adamaoua, liaison Nord-Sud"
    },
    {
        "name": "Plateau Voyages",
        "registration_number": "RC/MGG/2010/B/6789",
        "headquarters": "Meiganga",
        "region": "Adamaoua",
        "phone": "+237655456789",
        "founded_year": 2010,
        "fleet_size": 30,
        "routes_served": ["Meiganga-Ngaoundéré", "Meiganga-Tibati", "Meiganga-Yaoundé"],
        "services": ["passenger"],
        "rating": 3.7,
        "logo_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200",
        "premium_partner": False,
        "description": "Transport plateau Adamaoua, régions d'élevage"
    },

    # RÉGION NORD (Garoua)
    {
        "name": "Bénoué Express",
        "registration_number": "RC/GRA/2007/A/4567",
        "headquarters": "Garoua",
        "region": "Nord",
        "phone": "+237699567890",
        "founded_year": 2007,
        "fleet_size": 85,
        "routes_served": ["Garoua-Ngaoundéré", "Garoua-Maroua", "Garoua-Yaoundé"],
        "services": ["passenger", "cargo"],
        "rating": 3.9,
        "logo_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=200",
        "premium_partner": False,
        "description": "Transport Grand Nord, résistant climat sahélien"
    },
    {
        "name": "Faro Voyages",
        "registration_number": "RC/GRA/2011/C/8901",
        "headquarters": "Garoua",
        "region": "Nord", 
        "phone": "+237677678901",
        "founded_year": 2011,
        "fleet_size": 50,
        "routes_served": ["Garoua-Poli", "Garoua-Rey", "Garoua-Tcholliré"],
        "services": ["passenger"],
        "rating": 3.6,
        "logo_url": "https://images.unsplash.com/photo-1549366021-9f761d040a87?w=200",
        "premium_partner": False,
        "description": "Desserte régionale Nord, zones pastorales"
    },

    # RÉGION EXTRÊME-NORD (Maroua)
    {
        "name": "Diamaré Express",
        "registration_number": "RC/MRA/2006/B/1234",
        "headquarters": "Maroua",
        "region": "Extrême-Nord",
        "phone": "+237655789012",
        "founded_year": 2006,
        "fleet_size": 60,
        "routes_served": ["Maroua-Garoua", "Maroua-Kousseri", "Maroua-Mokolo"],
        "services": ["passenger", "cargo"],
        "rating": 3.8,
        "logo_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=200",
        "premium_partner": False,
        "description": "Transport Extrême-Nord, liaison Tchad"
    },
    {
        "name": "Sahel Voyages",
        "registration_number": "RC/KSI/2009/A/5678",
        "headquarters": "Kousseri",
        "region": "Extrême-Nord",
        "phone": "+237699890123",
        "founded_year": 2009,
        "fleet_size": 25,
        "routes_served": ["Kousseri-Maroua", "Kousseri-N'Djaména", "Kousseri-Waza"],
        "services": ["passenger", "transfrontalier"],
        "rating": 3.5,
        "logo_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=200",
        "premium_partner": False,
        "description": "Transport frontalier Cameroun-Tchad, zone sahélienne"
    },

    # NOUVELLES AGENCES AJOUTÉES
    {
        "name": "Easy Car",
        "registration_number": "RC/YDE/2015/C/8901",
        "headquarters": "Yaoundé",
        "region": "Centre",
        "phone": "+237677456789",
        "email": "contact@easycar.cm",
        "website": "www.easycar.cm",
        "founded_year": 2015,
        "fleet_size": 60,
        "routes_served": ["Yaoundé-Douala", "Yaoundé-Bafoussam", "Yaoundé-Bertoua"],
        "services": ["passenger", "VIP", "express"],
        "rating": 4.1,
        "logo_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=200",
        "premium_partner": False,
        "description": "Transport moderne et confortable, service express apprécié"
    },
    {
        "name": "Beko Express",
        "registration_number": "RC/DLA/2012/B/4567",
        "headquarters": "Douala",
        "region": "Littoral",
        "phone": "+237699567890",
        "email": "info@bekoexpress.cm",
        "founded_year": 2012,
        "fleet_size": 45,
        "routes_served": ["Douala-Yaoundé", "Douala-Bafoussam", "Douala-Limbe"],
        "services": ["passenger", "courier"],
        "rating": 3.9,
        "logo_url": "https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=200",
        "premium_partner": False,
        "description": "Transport fiable et ponctuel, spécialiste des liaisons courtes"
    },
    {
        "name": "Nkongsamba Express",
        "registration_number": "RC/LIT/2010/A/3456",
        "headquarters": "Nkongsamba",
        "region": "Littoral",
        "phone": "+237655678901",
        "email": "contact@nkongsambaexpress.cm",
        "founded_year": 2010,
        "fleet_size": 35,
        "routes_served": ["Nkongsamba-Douala", "Nkongsamba-Bafoussam", "Nkongsamba-Yaoundé"],
        "services": ["passenger", "cargo"],
        "rating": 4.0,
        "logo_url": "https://images.unsplash.com/photo-1506197603052-3cc9c3201bd?w=200",
        "premium_partner": False,
        "description": "Agence régionale connectant Nkongsamba aux grandes villes"
    },
    {
        "name": "Melong Express",
        "registration_number": "RC/LIT/2013/C/7890",
        "headquarters": "Melong",
        "region": "Littoral",
        "phone": "+237677789012",
        "email": "info@melongexpress.cm",
        "founded_year": 2013,
        "fleet_size": 25,
        "routes_served": ["Melong-Douala", "Melong-Bafoussam", "Melong-Nkongsamba"],
        "services": ["passenger"],
        "rating": 3.8,
        "logo_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=200",
        "premium_partner": False,
        "description": "Transport local et inter-urbain depuis Melong"
    },
    {
        "name": "Papa Ngassi Voyage",
        "registration_number": "RC/YDE/2005/B/2345",
        "headquarters": "Yaoundé",
        "region": "Centre",
        "phone": "+237699890123",
        "email": "contact@papangassi.cm",
        "founded_year": 2005,
        "fleet_size": 70,
        "routes_served": ["Yaoundé-Douala", "Yaoundé-Bamenda", "Yaoundé-Ngaoundéré"],
        "services": ["passenger", "VIP", "cargo"],
        "rating": 4.3,
        "logo_url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=200",
        "premium_partner": True,
        "description": "Agence familiale renommée, service VIP et confort premium"
    },
    {
        "name": "Noblesse Voyage",
        "registration_number": "RC/YDE/2008/A/6789",
        "headquarters": "Yaoundé",
        "region": "Centre",
        "phone": "+237655901234",
        "email": "info@noblessevoyage.cm",
        "website": "www.noblessevoyage.cm",
        "founded_year": 2008,
        "fleet_size": 50,
        "routes_served": ["Yaoundé-Douala", "Yaoundé-Bafoussam", "Yaoundé-Bertoua"],
        "services": ["passenger", "luxury", "VIP"],
        "rating": 4.4,
        "logo_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200",
        "premium_partner": True,
        "description": "Service haut de gamme, véhicules de luxe et confort exceptionnel"
    },
    {
        "name": "Nde Air Line",
        "registration_number": "RC/OUE/2011/C/1234",
        "headquarters": "Bangangté",
        "region": "Ouest",
        "phone": "+237677012345",
        "email": "contact@ndeairline.cm",
        "founded_year": 2011,
        "fleet_size": 40,
        "routes_served": ["Bangangté-Yaoundé", "Bangangté-Douala", "Bangangté-Bafoussam"],
        "services": ["passenger", "express"],
        "rating": 4.0,
        "logo_url": "https://images.unsplash.com/photo-1549366021-9f761d040a87?w=200",
        "premium_partner": False,
        "description": "Transport express région Ouest, ponctualité et rapidité"
    },
    {
        "name": "Avenir Voyage",
        "registration_number": "RC/DLA/2014/B/5678",
        "headquarters": "Douala",
        "region": "Littoral",
        "phone": "+237655123456",
        "email": "info@avenirvoyage.cm",
        "founded_year": 2014,
        "fleet_size": 55,
        "routes_served": ["Douala-Yaoundé", "Douala-Bamenda", "Douala-Bertoua"],
        "services": ["passenger", "tourism", "charter"],
        "rating": 4.2,
        "logo_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=200",
        "premium_partner": True,
        "description": "Agence moderne spécialisée dans le tourisme et transport charter"
    },
    {
        "name": "Keyla Express",
        "registration_number": "RC/YDE/2016/A/9012",
        "headquarters": "Yaoundé",
        "region": "Centre",
        "phone": "+237699234567",
        "email": "contact@keylaexpress.cm",
        "website": "www.keylaexpress.cm",
        "founded_year": 2016,
        "fleet_size": 30,
        "routes_served": ["Yaoundé-Douala", "Yaoundé-Ebolowa", "Yaoundé-Sangmélima"],
        "services": ["passenger", "express"],
        "rating": 3.9,
        "logo_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=200",
        "premium_partner": False,
        "description": "Agence récente dynamique, spécialiste des liaisons Sud"
    }
]

# Sites Touristiques Authentiques du Cameroun avec Images Réelles
CAMEROON_TOURIST_ATTRACTIONS = [
    {
        "name": "Mont Cameroun",
        "city": "Buéa",
        "region": "Sud-Ouest",
        "description": "Plus haute montagne d'Afrique de l'Ouest (4 095m), volcan actif avec vue spectaculaire sur l'Atlantique",
        "image_url": "https://images.unsplash.com/photo-1638336038216-da03b5a7752a?w=600",
        "category": "nature",
        "rating": 4.8,
        "coordinates": {"lat": 4.2175, "lng": 9.1708}
    },
    {
        "name": "Chutes de la Lobé",
        "city": "Kribi",
        "region": "Sud",
        "description": "Cascades uniques au monde se jetant directement dans l'océan Atlantique depuis 20m de hauteur",
        "image_url": "https://images.unsplash.com/photo-1704183683766-37137be69d4f?w=600",
        "category": "nature",
        "rating": 4.7,
        "coordinates": {"lat": 2.8833, "lng": 9.9167}
    },
    {
        "name": "Palais des Rois Bamoun",
        "city": "Foumban",
        "region": "Ouest",
        "description": "Palais royal historique du Sultan des Bamouns, architecture traditionnelle et musée des arts bamoun",
        "image_url": "https://images.unsplash.com/photo-1716460513823-f48135e1be21?w=600",
        "category": "cultural",
        "rating": 4.6,
        "coordinates": {"lat": 5.7167, "lng": 10.9000}
    },
    {
        "name": "Parc National de Waza",
        "city": "Waza",
        "region": "Extrême-Nord",
        "description": "Réserve de faune soudano-sahélienne avec éléphants, lions, girafes et plus de 370 espèces d'oiseaux",
        "image_url": "https://images.unsplash.com/photo-1637067788163-e43c2c4a40ed?w=600",
        "category": "nature",
        "rating": 4.6,
        "coordinates": {"lat": 11.3833, "lng": 14.6333}
    },
    {
        "name": "Lac Nyos",
        "city": "Wum",
        "region": "Nord-Ouest",
        "description": "Lac cratère mystérieux aux eaux cristallines, phénomène géologique unique au monde",
        "image_url": "https://images.unsplash.com/photo-1663999592206-36a55e51e9f2?w=600",
        "category": "nature",
        "rating": 4.4,
        "coordinates": {"lat": 6.4333, "lng": 10.2967}
    },
    {
        "name": "Plages de Limbe",
        "city": "Limbe",
        "region": "Sud-Ouest", 
        "description": "Plages de sable noir volcanique unique, jardins botaniques et vue imprenable sur le mont Cameroun",
        "image_url": "https://images.unsplash.com/photo-1673262791211-55f7a4e13118?w=600",
        "category": "nature",
        "rating": 4.3,
        "coordinates": {"lat": 4.0167, "lng": 9.2000}
    },
    {
        "name": "Réserve de Biosphère de Dja",
        "city": "Sangmélima",
        "region": "Sud",
        "description": "Forêt tropicale primaire classée UNESCO, habitat de gorilles, chimpanzés et éléphants de forêt",
        "image_url": "https://images.unsplash.com/photo-1689175693942-401457c06d2c?w=600",
        "category": "nature",
        "rating": 4.7,
        "coordinates": {"lat": 3.2000, "lng": 12.5000}
    },
    {
        "name": "Parc National de la Bénoué",
        "city": "Garoua",
        "region": "Nord",
        "description": "Savane soudanienne avec hippopotames, buffles, antilopes et plus de 300 espèces d'oiseaux",
        "image_url": "https://images.unsplash.com/photo-1671215737057-8d2badcfb04b?w=600",
        "category": "nature",
        "rating": 4.5,
        "coordinates": {"lat": 8.7000, "lng": 13.8000}
    },
    {
        "name": "Basilique Marie-Reine-des-Apôtres",
        "city": "Yaoundé",
        "region": "Centre",
        "description": "Monument religieux emblématique de Yaoundé, architecture moderne impressionnante du plateau Mvolyé",
        "image_url": "https://images.unsplash.com/photo-1751965681994-1a2ba3735dab?w=600",
        "category": "cultural",
        "rating": 4.4,
        "coordinates": {"lat": 3.8667, "lng": 11.5167}
    },
    {
        "name": "Cathédrale Saints-Pierre-et-Paul",
        "city": "Douala",
        "region": "Littoral",
        "description": "Cathédrale historique de Douala, architecture coloniale et centre spirituel de la capitale économique",
        "image_url": "https://images.unsplash.com/photo-1716460513823-f48135e1be21?w=600",
        "category": "cultural", 
        "rating": 4.2,
        "coordinates": {"lat": 4.0511, "lng": 9.7679}
    },
    {
        "name": "Rocher du Loup (Balessing)",
        "city": "Balessing",
        "region": "Ouest",
        "description": "Formation rocheuse spectaculaire dominant la plaine Tikar, site sacré et panorama exceptionnel",
        "image_url": "https://images.unsplash.com/photo-1704183683740-1400a49816b7?w=600",
        "category": "nature",
        "rating": 4.3,
        "coordinates": {"lat": 6.0000, "lng": 11.2000}
    },
    {
        "name": "Chutes de la Métché",
        "city": "Bertoua",
        "region": "Est",
        "description": "Cascade impressionnante de la région Est, site de baignade naturel en pleine forêt tropicale",
        "image_url": "https://images.unsplash.com/photo-1742925074349-863ebffd4f2c?w=600",
        "category": "nature",
        "rating": 4.1,
        "coordinates": {"lat": 4.5772, "lng": 13.6847}
    },
    {
        "name": "Marché Central de Yaoundé",
        "city": "Yaoundé",
        "region": "Centre",
        "description": "Plus grand marché du Cameroun, explosion de couleurs, saveurs et artisanat traditionnel",
        "image_url": "https://images.unsplash.com/photo-1687422809617-a7d97879b3b0?w=600",
        "category": "cultural",
        "rating": 4.0,
        "coordinates": {"lat": 3.8689, "lng": 11.5208}
    },
    {
        "name": "Parc National de Korup",
        "city": "Mundemba",
        "region": "Sud-Ouest",
        "description": "Une des plus anciennes forêts tropicales au monde, biodiversité exceptionnelle et écotourisme",
        "image_url": "https://images.unsplash.com/photo-1678189722525-ad58b1f20c1b?w=600",
        "category": "nature",
        "rating": 4.5,
        "coordinates": {"lat": 5.0667, "lng": 8.8500}
    },
    {
        "name": "Marché aux Poissons de Douala",
        "city": "Douala",
        "region": "Littoral",
        "description": "Marché traditionnel animé au bord du Wouri, poissons frais et ambiance authentique camerounaise",
        "image_url": "https://images.unsplash.com/photo-1585540083814-ea6ee8af9e4f?w=600",
        "category": "cultural",
        "rating": 3.9,
        "coordinates": {"lat": 4.0483, "lng": 9.7053}
    },
    {
        "name": "Station de Dschang",
        "city": "Dschang", 
        "region": "Ouest",
        "description": "Station climatique de montagne, climat tempéré et paysages verdoyants des hautes terres de l'Ouest",
        "image_url": "https://images.unsplash.com/photo-1631693570976-9c406a62adf6?w=600",
        "category": "nature",
        "rating": 4.2,
        "coordinates": {"lat": 5.4500, "lng": 10.0500}
    }
]

# Structure administrative simplifiée du Cameroun : Régions et Chefs-lieux
CAMEROON_ADMINISTRATIVE_STRUCTURE = {
    "Adamaoua": {
        "cities": [
            {"name": "Tibati", "lat": 6.4667, "lng": 12.6333, "type": "chef-lieu"},
            {"name": "Tignère", "lat": 7.3667, "lng": 12.6500, "type": "chef-lieu"},
            {"name": "Banyo", "lat": 6.7500, "lng": 11.8167, "type": "chef-lieu"},
            {"name": "Meiganga", "lat": 6.5167, "lng": 14.3000, "type": "chef-lieu"},
            {"name": "Ngaoundéré", "lat": 7.3167, "lng": 13.5833, "type": "chef-lieu"}
        ]
    },
    "Centre": {
        "cities": [
            {"name": "Nanga-Eboko", "lat": 4.6833, "lng": 12.3667, "type": "chef-lieu"},
            {"name": "Monatele", "lat": 4.1167, "lng": 11.3667, "type": "chef-lieu"},
            {"name": "Bafia", "lat": 4.7500, "lng": 11.2333, "type": "chef-lieu"},
            {"name": "Ntui", "lat": 4.4333, "lng": 11.5833, "type": "chef-lieu"},
            {"name": "Mfou", "lat": 3.7333, "lng": 11.6333, "type": "chef-lieu"},
            {"name": "Ngoumou", "lat": 3.6000, "lng": 11.4500, "type": "chef-lieu"},
            {"name": "Yaoundé", "lat": 3.8667, "lng": 11.5167, "type": "chef-lieu"},
            {"name": "Éséka", "lat": 3.6500, "lng": 10.7667, "type": "chef-lieu"},
            {"name": "Akonolinga", "lat": 3.7833, "lng": 12.2500, "type": "chef-lieu"},
            {"name": "Mbalmayo", "lat": 3.5167, "lng": 11.5000, "type": "chef-lieu"}
        ]
    },
    "Est": {
        "cities": [
            {"name": "Yokadouma", "lat": 3.5167, "lng": 15.0500, "type": "chef-lieu"},
            {"name": "Abong-Mbang", "lat": 3.9833, "lng": 13.1833, "type": "chef-lieu"},
            {"name": "Batouri", "lat": 4.4333, "lng": 14.3667, "type": "chef-lieu"},
            {"name": "Bertoua", "lat": 4.5833, "lng": 13.6833, "type": "chef-lieu"}
        ]
    },
    "Extrême-Nord": {
        "cities": [
            {"name": "Maroua", "lat": 10.5833, "lng": 14.3167, "type": "chef-lieu"},
            {"name": "Kousséri", "lat": 12.0833, "lng": 15.0333, "type": "chef-lieu"},
            {"name": "Yagoua", "lat": 10.3333, "lng": 15.2333, "type": "chef-lieu"},
            {"name": "Kaélé", "lat": 10.1000, "lng": 14.4667, "type": "chef-lieu"},
            {"name": "Mora", "lat": 11.0500, "lng": 14.0833, "type": "chef-lieu"},
            {"name": "Mokolo", "lat": 10.7333, "lng": 13.8000, "type": "chef-lieu"}
        ]
    },
    "Littoral": {
        "cities": [
            {"name": "Nkongsamba", "lat": 4.9500, "lng": 9.9333, "type": "chef-lieu"},
            {"name": "Yabassi", "lat": 4.4500, "lng": 9.9667, "type": "chef-lieu"},
            {"name": "Édéa", "lat": 3.8000, "lng": 10.1333, "type": "chef-lieu"},
            {"name": "Douala", "lat": 4.0611, "lng": 9.7067, "type": "chef-lieu"}
        ]
    },
    "Nord": {
        "cities": [
            {"name": "Garoua", "lat": 9.3000, "lng": 13.4000, "type": "chef-lieu"},
            {"name": "Poli", "lat": 8.4167, "lng": 13.2500, "type": "chef-lieu"},
            {"name": "Guider", "lat": 9.9333, "lng": 13.9500, "type": "chef-lieu"},
            {"name": "Tcholliré", "lat": 8.3833, "lng": 14.1833, "type": "chef-lieu"}
        ]
    },
    "Nord-Ouest": {
        "cities": [
            {"name": "Fundong", "lat": 6.2333, "lng": 10.2833, "type": "chef-lieu"},
            {"name": "Kumbo", "lat": 6.2000, "lng": 10.6667, "type": "chef-lieu"},
            {"name": "Nkambé", "lat": 6.5833, "lng": 11.0167, "type": "chef-lieu"},
            {"name": "Wum", "lat": 6.3833, "lng": 10.0667, "type": "chef-lieu"},
            {"name": "Bamenda", "lat": 5.9597, "lng": 10.1431, "type": "chef-lieu"},
            {"name": "Mbengwi", "lat": 6.1667, "lng": 9.7833, "type": "chef-lieu"},
            {"name": "Ndop", "lat": 6.0000, "lng": 10.4167, "type": "chef-lieu"}
        ]
    },
    "Ouest": {
        "cities": [
            {"name": "Mbouda", "lat": 5.6167, "lng": 10.2500, "type": "chef-lieu"},
            {"name": "Bafang", "lat": 5.1500, "lng": 10.1833, "type": "chef-lieu"},
            {"name": "Baham", "lat": 5.3667, "lng": 10.3833, "type": "chef-lieu"},
            {"name": "Bandjoun", "lat": 5.3667, "lng": 10.4167, "type": "chef-lieu"},
            {"name": "Dschang", "lat": 5.4500, "lng": 10.0500, "type": "chef-lieu"},
            {"name": "Bafoussam", "lat": 5.4731, "lng": 10.4206, "type": "chef-lieu"},
            {"name": "Bangangté", "lat": 5.1500, "lng": 10.5167, "type": "chef-lieu"},
            {"name": "Foumban", "lat": 5.7167, "lng": 10.9000, "type": "chef-lieu"}
        ]
    },
    "Sud": {
        "cities": [
            {"name": "Sangmélima", "lat": 2.9333, "lng": 11.9833, "type": "chef-lieu"},
            {"name": "Ebolowa", "lat": 2.9167, "lng": 11.1500, "type": "chef-lieu"},
            {"name": "Kribi", "lat": 2.9333, "lng": 9.9167, "type": "chef-lieu"},
            {"name": "Ambam", "lat": 2.3833, "lng": 11.2667, "type": "chef-lieu"}
        ]
    },
    "Sud-Ouest": {
        "cities": [
            {"name": "Limbé", "lat": 4.0167, "lng": 9.2000, "type": "chef-lieu"},
            {"name": "Bangem", "lat": 5.1167, "lng": 9.7833, "type": "chef-lieu"},
            {"name": "Menji", "lat": 5.4167, "lng": 9.9500, "type": "chef-lieu"},
            {"name": "Mamfé", "lat": 5.7667, "lng": 9.3167, "type": "chef-lieu"},
            {"name": "Kumba", "lat": 4.6333, "lng": 9.4500, "type": "chef-lieu"},
            {"name": "Mundemba", "lat": 4.9667, "lng": 8.8667, "type": "chef-lieu"}
        ]
    }
}

# Enhanced Cities, Villages and Localities in Cameroon  
ENHANCED_CAMEROON_CITIES = [
    # GRANDES VILLES PRINCIPALES
    {"name": "Yaoundé", "region": "Centre", "lat": 3.8667, "lng": 11.5167, "major": True, "airport": True, "population": 4500000, "type": "capitale"},
    {"name": "Douala", "region": "Littoral", "lat": 4.0611, "lng": 9.7067, "major": True, "airport": True, "population": 3700000, "type": "ville"},
    {"name": "Bafoussam", "region": "Ouest", "lat": 5.4667, "lng": 10.4167, "major": True, "airport": True, "population": 450000, "type": "ville"},
    {"name": "Bamenda", "region": "Nord-Ouest", "lat": 5.9667, "lng": 10.1667, "major": True, "airport": True, "population": 500000, "type": "ville"},
    {"name": "Bertoua", "region": "Est", "lat": 4.5833, "lng": 13.6833, "major": True, "airport": True, "population": 300000, "type": "ville"},
    {"name": "Garoua", "region": "Nord", "lat": 9.3000, "lng": 13.4000, "major": True, "airport": True, "population": 450000, "type": "ville"},
    {"name": "Maroua", "region": "Extrême-Nord", "lat": 10.5833, "lng": 14.3167, "major": True, "airport": True, "population": 400000, "type": "ville"},
    {"name": "Ngaoundéré", "region": "Adamaoua", "lat": 7.3167, "lng": 13.5833, "major": True, "airport": True, "population": 300000, "type": "ville"},
    
    # VILLES SECONDAIRES
    {"name": "Kribi", "region": "Sud", "lat": 2.9333, "lng": 9.9167, "major": True, "airport": False, "population": 70000, "type": "ville"},
    {"name": "Limbe", "region": "Sud-Ouest", "lat": 4.0167, "lng": 9.2000, "major": True, "airport": False, "population": 120000, "type": "ville"},
    {"name": "Buéa", "region": "Sud-Ouest", "lat": 4.1500, "lng": 9.2833, "major": True, "airport": False, "population": 200000, "type": "ville"},
    {"name": "Kumba", "region": "Sud-Ouest", "lat": 4.6333, "lng": 9.4500, "major": True, "airport": False, "population": 150000, "type": "ville"},
    {"name": "Ebolowa", "region": "Sud", "lat": 2.9167, "lng": 11.1500, "major": True, "airport": False, "population": 80000, "type": "ville"},
    {"name": "Foumban", "region": "Ouest", "lat": 5.7167, "lng": 10.9000, "major": True, "airport": False, "population": 120000, "type": "ville"},
    {"name": "Dschang", "region": "Ouest", "lat": 5.4500, "lng": 10.0500, "major": True, "airport": False, "population": 100000, "type": "ville"},
    
    # RÉGION CENTRE - Localités et Villages
    {"name": "Mbalmayo", "region": "Centre", "lat": 3.5167, "lng": 11.5000, "major": False, "airport": False, "population": 25000, "type": "commune"},
    {"name": "Obala", "region": "Centre", "lat": 4.1667, "lng": 11.5333, "major": False, "airport": False, "population": 15000, "type": "commune"},
    {"name": "Mfou", "region": "Centre", "lat": 3.7333, "lng": 11.6333, "major": False, "airport": False, "population": 8000, "type": "commune"},
    {"name": "Soa", "region": "Centre", "lat": 3.9500, "lng": 11.3833, "major": False, "airport": False, "population": 12000, "type": "commune"},
    {"name": "Ntui", "region": "Centre", "lat": 4.4333, "lng": 11.5833, "major": False, "airport": False, "population": 7000, "type": "commune"},
    {"name": "Bafia", "region": "Centre", "lat": 4.7500, "lng": 11.2333, "major": False, "airport": False, "population": 18000, "type": "commune"},
    {"name": "Nanga-Eboko", "region": "Centre", "lat": 4.6833, "lng": 12.3667, "major": False, "airport": False, "population": 9000, "type": "commune"},
    
    # RÉGION LITTORAL - Localités et Villages  
    {"name": "Edéa", "region": "Littoral", "lat": 3.8000, "lng": 10.1333, "major": False, "airport": False, "population": 45000, "type": "commune"},
    {"name": "Loum", "region": "Littoral", "lat": 4.7167, "lng": 9.7333, "major": False, "airport": False, "population": 30000, "type": "commune"},
    {"name": "Nkongsamba", "region": "Littoral", "lat": 4.9500, "lng": 9.9333, "major": False, "airport": False, "population": 120000, "type": "commune"},
    {"name": "Mbanga", "region": "Littoral", "lat": 4.4833, "lng": 9.5667, "major": False, "airport": False, "population": 25000, "type": "commune"},
    {"name": "Manjo", "region": "Littoral", "lat": 4.6833, "lng": 9.8333, "major": False, "airport": False, "population": 15000, "type": "commune"},
    {"name": "Yabassi", "region": "Littoral", "lat": 4.4500, "lng": 9.9667, "major": False, "airport": False, "population": 12000, "type": "commune"},
    
    # RÉGION OUEST - Localités et Villages
    {"name": "Mbouda", "region": "Ouest", "lat": 5.6167, "lng": 10.2500, "major": False, "airport": False, "population": 35000, "type": "commune"},
    {"name": "Bandjoun", "region": "Ouest", "lat": 5.3667, "lng": 10.4000, "major": False, "airport": False, "population": 20000, "type": "commune"},
    {"name": "Bangangté", "region": "Ouest", "lat": 5.1500, "lng": 10.5167, "major": False, "airport": False, "population": 25000, "type": "commune"},
    {"name": "Bafang", "region": "Ouest", "lat": 5.1667, "lng": 10.1833, "major": False, "airport": False, "population": 40000, "type": "commune"},
    {"name": "Kékem", "region": "Ouest", "lat": 5.2167, "lng": 10.0667, "major": False, "airport": False, "population": 15000, "type": "commune"},
    {"name": "Penka-Michel", "region": "Ouest", "lat": 5.4000, "lng": 10.1000, "major": False, "airport": False, "population": 8000, "type": "village"},
    
    # RÉGION NORD-OUEST - Localités et Villages
    {"name": "Wum", "region": "Nord-Ouest", "lat": 6.3833, "lng": 10.0667, "major": False, "airport": False, "population": 15000, "type": "commune"},
    {"name": "Fundong", "region": "Nord-Ouest", "lat": 6.2333, "lng": 10.2833, "major": False, "airport": False, "population": 12000, "type": "commune"},
    {"name": "Mbengwi", "region": "Nord-Ouest", "lat": 6.1833, "lng": 9.7167, "major": False, "airport": False, "population": 18000, "type": "commune"},
    {"name": "Ndop", "region": "Nord-Ouest", "lat": 6.0167, "lng": 10.4333, "major": False, "airport": False, "population": 10000, "type": "commune"},
    {"name": "Kumbo", "region": "Nord-Ouest", "lat": 6.2000, "lng": 10.6667, "major": False, "airport": False, "population": 35000, "type": "commune"},
    {"name": "Nkambe", "region": "Nord-Ouest", "lat": 6.5833, "lng": 10.6833, "major": False, "airport": False, "population": 20000, "type": "commune"},
    
    # RÉGION SUD-OUEST - Localités et Villages
    {"name": "Mamfé", "region": "Sud-Ouest", "lat": 5.7667, "lng": 9.3167, "major": False, "airport": False, "population": 25000, "type": "commune"},
    {"name": "Tiko", "region": "Sud-Ouest", "lat": 4.0667, "lng": 9.3600, "major": False, "airport": False, "population": 55000, "type": "commune"},
    {"name": "Idenau", "region": "Sud-Ouest", "lat": 4.1167, "lng": 8.9833, "major": False, "airport": False, "population": 8000, "type": "commune"},
    {"name": "Muyuka", "region": "Sud-Ouest", "lat": 4.3000, "lng": 9.4000, "major": False, "airport": False, "population": 12000, "type": "commune"},
    {"name": "Tombel", "region": "Sud-Ouest", "lat": 4.6833, "lng": 9.6167, "major": False, "airport": False, "population": 15000, "type": "commune"},
    
    # RÉGION SUD - Localités et Villages
    {"name": "Sangmélima", "region": "Sud", "lat": 2.9333, "lng": 11.9833, "major": False, "airport": False, "population": 18000, "type": "commune"},
    {"name": "Ambam", "region": "Sud", "lat": 2.3833, "lng": 11.2667, "major": False, "airport": False, "population": 12000, "type": "commune"},
    {"name": "Mvangan", "region": "Sud", "lat": 2.4667, "lng": 11.6167, "major": False, "airport": False, "population": 5000, "type": "commune"},
    {"name": "Campo", "region": "Sud", "lat": 2.3667, "lng": 9.8167, "major": False, "airport": False, "population": 8000, "type": "commune"},
    {"name": "Lolodorf", "region": "Sud", "lat": 3.2333, "lng": 10.7333, "major": False, "airport": False, "population": 7000, "type": "commune"},
    
    # RÉGION EST - Localités et Villages
    {"name": "Batouri", "region": "Est", "lat": 4.4333, "lng": 14.3667, "major": False, "airport": False, "population": 25000, "type": "commune"},
    {"name": "Yokadouma", "region": "Est", "lat": 3.5167, "lng": 15.0500, "major": False, "airport": False, "population": 30000, "type": "commune"},
    {"name": "Abong-Mbang", "region": "Est", "lat": 3.9833, "lng": 13.1833, "major": False, "airport": False, "population": 18000, "type": "commune"},
    {"name": "Doumé", "region": "Est", "lat": 4.2333, "lng": 13.4333, "major": False, "airport": False, "population": 8000, "type": "commune"},
    {"name": "Moloundou", "region": "Est", "lat": 2.0333, "lng": 15.1833, "major": False, "airport": False, "population": 12000, "type": "commune"},
    
    # RÉGION ADAMAOUA - Localités et Villages
    {"name": "Meiganga", "region": "Adamaoua", "lat": 6.5167, "lng": 14.3000, "major": False, "airport": False, "population": 20000, "type": "commune"},
    {"name": "Tibati", "region": "Adamaoua", "lat": 6.4667, "lng": 12.6333, "major": False, "airport": False, "population": 15000, "type": "commune"},
    {"name": "Banyo", "region": "Adamaoua", "lat": 6.7500, "lng": 11.8167, "major": False, "airport": False, "population": 18000, "type": "commune"},
    {"name": "Tignère", "region": "Adamaoua", "lat": 7.3667, "lng": 12.6500, "major": False, "airport": False, "population": 25000, "type": "commune"},
    
    # RÉGION NORD - Localités et Villages  
    {"name": "Poli", "region": "Nord", "lat": 8.4167, "lng": 13.2500, "major": False, "airport": False, "population": 15000, "type": "commune"},
    {"name": "Rey", "region": "Nord", "lat": 9.1667, "lng": 12.1833, "major": False, "airport": False, "population": 12000, "type": "commune"},
    {"name": "Tcholliré", "region": "Nord", "lat": 8.3833, "lng": 14.1167, "major": False, "airport": False, "population": 8000, "type": "commune"},
    {"name": "Guider", "region": "Nord", "lat": 9.9333, "lng": 13.9500, "major": False, "airport": False, "population": 35000, "type": "commune"},
    
    # RÉGION EXTRÊME-NORD - Localités et Villages
    {"name": "Kousseri", "region": "Extrême-Nord", "lat": 12.0833, "lng": 15.0333, "major": False, "airport": False, "population": 120000, "type": "commune"},
    {"name": "Mokolo", "region": "Extrême-Nord", "lat": 10.7333, "lng": 13.8000, "major": False, "airport": False, "population": 45000, "type": "commune"},
    {"name": "Mora", "region": "Extrême-Nord", "lat": 11.0500, "lng": 14.0833, "major": False, "airport": False, "population": 25000, "type": "commune"},
    {"name": "Waza", "region": "Extrême-Nord", "lat": 11.3833, "lng": 14.6333, "major": False, "airport": False, "population": 8000, "type": "commune"},
    {"name": "Yagoua", "region": "Extrême-Nord", "lat": 10.3333, "lng": 15.2333, "major": False, "airport": False, "population": 35000, "type": "commune"},
    {"name": "Bourrah", "region": "Extrême-Nord", "lat": 10.4833, "lng": 14.4167, "major": False, "airport": False, "population": 5000, "type": "village"},
    {"name": "Bogo", "region": "Extrême-Nord", "lat": 11.2667, "lng": 14.6000, "major": False, "airport": False, "population": 12000, "type": "commune"},

    # CHEFS-LIEUX D'ARRONDISSEMENTS SUPPLÉMENTAIRES
    
    # RÉGION CENTRE - Arrondissements
    {"name": "Akono", "region": "Centre", "lat": 3.5000, "lng": 11.4000, "major": False, "airport": False, "population": 6000, "type": "arrondissement"},
    {"name": "Akonolinga", "region": "Centre", "lat": 3.7833, "lng": 12.2500, "major": False, "airport": False, "population": 12000, "type": "arrondissement"},
    {"name": "Ayos", "region": "Centre", "lat": 3.9167, "lng": 12.5500, "major": False, "airport": False, "population": 8000, "type": "arrondissement"},
    {"name": "Biyem-Assi", "region": "Centre", "lat": 3.8500, "lng": 11.4833, "major": False, "airport": False, "population": 15000, "type": "arrondissement"},
    {"name": "Eseka", "region": "Centre", "lat": 3.6500, "lng": 10.7667, "major": False, "airport": False, "population": 20000, "type": "arrondissement"},
    {"name": "Evodoula", "region": "Centre", "lat": 4.3833, "lng": 11.8167, "major": False, "airport": False, "population": 5000, "type": "arrondissement"},
    {"name": "Makak", "region": "Centre", "lat": 3.4833, "lng": 11.8833, "major": False, "airport": False, "population": 7000, "type": "arrondissement"},
    {"name": "Mbangassina", "region": "Centre", "lat": 4.5833, "lng": 11.5500, "major": False, "airport": False, "population": 6000, "type": "arrondissement"},

    # RÉGION LITTORAL - Arrondissements
    {"name": "Dibombari", "region": "Littoral", "lat": 4.0833, "lng": 9.7000, "major": False, "airport": False, "population": 8000, "type": "arrondissement"},
    {"name": "Ekangte", "region": "Littoral", "lat": 4.7000, "lng": 9.8000, "major": False, "airport": False, "population": 5000, "type": "arrondissement"},
    {"name": "Kekem", "region": "Littoral", "lat": 5.2167, "lng": 10.0667, "major": False, "airport": False, "population": 12000, "type": "arrondissement"},
    {"name": "Melong", "region": "Littoral", "lat": 5.1167, "lng": 9.9500, "major": False, "airport": False, "population": 18000, "type": "arrondissement"},
    {"name": "Njombe-Penja", "region": "Littoral", "lat": 4.6167, "lng": 9.6500, "major": False, "airport": False, "population": 15000, "type": "arrondissement"},
    {"name": "Penja", "region": "Littoral", "lat": 4.6167, "lng": 9.6500, "major": False, "airport": False, "population": 10000, "type": "arrondissement"},

    # RÉGION OUEST - Arrondissements
    {"name": "Baham", "region": "Ouest", "lat": 5.3167, "lng": 10.3167, "major": False, "airport": False, "population": 12000, "type": "arrondissement"},
    {"name": "Batié", "region": "Ouest", "lat": 5.2833, "lng": 10.2833, "major": False, "airport": False, "population": 8000, "type": "arrondissement"},
    {"name": "Galim", "region": "Ouest", "lat": 5.6500, "lng": 10.8167, "major": False, "airport": False, "population": 6000, "type": "arrondissement"},
    {"name": "Kouoptamo", "region": "Ouest", "lat": 5.2000, "lng": 10.0500, "major": False, "airport": False, "population": 7000, "type": "arrondissement"},
    {"name": "Magba", "region": "Ouest", "lat": 5.7500, "lng": 10.8500, "major": False, "airport": False, "population": 5000, "type": "arrondissement"},
    {"name": "Penka-Michel", "region": "Ouest", "lat": 5.4000, "lng": 10.1000, "major": False, "airport": False, "population": 8000, "type": "arrondissement"},

    # RÉGION SUD-OUEST - Arrondissements
    {"name": "Akwaya", "region": "Sud-Ouest", "lat": 6.2833, "lng": 9.1333, "major": False, "airport": False, "population": 4000, "type": "arrondissement"},
    {"name": "Bangem", "region": "Sud-Ouest", "lat": 5.1167, "lng": 9.7833, "major": False, "airport": False, "population": 8000, "type": "arrondissement"},
    {"name": "Dikome-Balue", "region": "Sud-Ouest", "lat": 4.2000, "lng": 8.9167, "major": False, "airport": False, "population": 6000, "type": "arrondissement"},
    {"name": "Fontem", "region": "Sud-Ouest", "lat": 5.4000, "lng": 9.9000, "major": False, "airport": False, "population": 5000, "type": "arrondissement"},
    {"name": "Konye", "region": "Sud-Ouest", "lat": 4.8333, "lng": 9.2500, "major": False, "airport": False, "population": 7000, "type": "arrondissement"},
    {"name": "Nguti", "region": "Sud-Ouest", "lat": 5.4167, "lng": 9.4833, "major": False, "airport": False, "population": 9000, "type": "arrondissement"},

    # RÉGION SUD - Arrondissements
    {"name": "Bengbis", "region": "Sud", "lat": 2.8500, "lng": 12.4000, "major": False, "airport": False, "population": 7000, "type": "arrondissement"},
    {"name": "Biwong-Bane", "region": "Sud", "lat": 2.6167, "lng": 10.4167, "major": False, "airport": False, "population": 4000, "type": "arrondissement"},
    {"name": "Dja", "region": "Sud", "lat": 3.1500, "lng": 12.7000, "major": False, "airport": False, "population": 3000, "type": "arrondissement"},
    {"name": "Ebolowa I", "region": "Sud", "lat": 2.9167, "lng": 11.1500, "major": False, "airport": False, "population": 40000, "type": "arrondissement"},
    {"name": "Ebolowa II", "region": "Sud", "lat": 2.9000, "lng": 11.1333, "major": False, "airport": False, "population": 25000, "type": "arrondissement"},
    {"name": "Ma'an", "region": "Sud", "lat": 2.3667, "lng": 10.3167, "major": False, "airport": False, "population": 8000, "type": "arrondissement"},

    # RÉGION EST - Arrondissements
    {"name": "Belabo", "region": "Est", "lat": 4.9333, "lng": 13.3000, "major": False, "airport": False, "population": 12000, "type": "arrondissement"},
    {"name": "Bétare-Oya", "region": "Est", "lat": 5.6000, "lng": 14.0833, "major": False, "airport": False, "population": 15000, "type": "arrondissement"},
    {"name": "Diang", "region": "Est", "lat": 4.2000, "lng": 13.8000, "major": False, "airport": False, "population": 6000, "type": "arrondissement"},
    {"name": "Garoua-Boulaï", "region": "Est", "lat": 5.8000, "lng": 14.5333, "major": False, "airport": False, "population": 18000, "type": "arrondissement"},
    {"name": "Kenzou", "region": "Est", "lat": 4.7500, "lng": 13.9167, "major": False, "airport": False, "population": 5000, "type": "arrondissement"},
    {"name": "Lomié", "region": "Est", "lat": 3.1833, "lng": 13.6333, "major": False, "airport": False, "population": 8000, "type": "arrondissement"},

    # RÉGION ADAMAOUA - Arrondissements
    {"name": "Belel", "region": "Adamaoua", "lat": 7.9333, "lng": 14.4167, "major": False, "airport": False, "population": 8000, "type": "arrondissement"},
    {"name": "Kontcha", "region": "Adamaoua", "lat": 8.2000, "lng": 12.2333, "major": False, "airport": False, "population": 12000, "type": "arrondissement"},
    {"name": "Mayo-Baleo", "region": "Adamaoua", "lat": 7.7500, "lng": 12.8167, "major": False, "airport": False, "population": 6000, "type": "arrondissement"},
    {"name": "Nganha", "region": "Adamaoua", "lat": 6.8833, "lng": 15.3167, "major": False, "airport": False, "population": 4000, "type": "arrondissement"},
    {"name": "Ngaoundal", "region": "Adamaoua", "lat": 6.5000, "lng": 13.2767, "major": False, "airport": False, "population": 10000, "type": "arrondissement"},
    {"name": "Dir", "region": "Adamaoua", "lat": 7.1500, "lng": 13.1833, "major": False, "airport": False, "population": 7000, "type": "arrondissement"},

    # RÉGION NORD - Arrondissements  
    {"name": "Bibemi", "region": "Nord", "lat": 9.3500, "lng": 12.8167, "major": False, "airport": False, "population": 8000, "type": "arrondissement"},
    {"name": "Demsa", "region": "Nord", "lat": 9.5500, "lng": 13.6500, "major": False, "airport": False, "population": 10000, "type": "arrondissement"},
    {"name": "Figuil", "region": "Nord", "lat": 9.7500, "lng": 13.9667, "major": False, "airport": False, "population": 18000, "type": "arrondissement"},
    {"name": "Lagdo", "region": "Nord", "lat": 9.0667, "lng": 13.7333, "major": False, "airport": False, "population": 12000, "type": "arrondissement"},
    {"name": "Mayo-Oulo", "region": "Nord", "lat": 8.9000, "lng": 13.2000, "major": False, "airport": False, "population": 6000, "type": "arrondissement"},
    {"name": "Pitoa", "region": "Nord", "lat": 9.3833, "lng": 13.5167, "major": False, "airport": False, "population": 15000, "type": "arrondissement"},

    # RÉGION NORD-OUEST - Arrondissements
    {"name": "Ako", "region": "Nord-Ouest", "lat": 6.4167, "lng": 9.9833, "major": False, "airport": False, "population": 7000, "type": "arrondissement"},
    {"name": "Bafut", "region": "Nord-Ouest", "lat": 6.1000, "lng": 10.1167, "major": False, "airport": False, "population": 25000, "type": "arrondissement"},
    {"name": "Jakiri", "region": "Nord-Ouest", "lat": 6.3833, "lng": 10.4333, "major": False, "airport": False, "population": 14000, "type": "arrondissement"},
    {"name": "Misaje", "region": "Nord-Ouest", "lat": 6.6167, "lng": 9.9000, "major": False, "airport": False, "population": 8000, "type": "arrondissement"},
    {"name": "Oku", "region": "Nord-Ouest", "lat": 6.2500, "lng": 10.4667, "major": False, "airport": False, "population": 18000, "type": "arrondissement"},
    {"name": "Santa", "region": "Nord-Ouest", "lat": 5.9167, "lng": 10.1667, "major": False, "airport": False, "population": 20000, "type": "arrondissement"},

    # RÉGION EXTRÊME-NORD - Arrondissements additionnels
    {"name": "Dargala", "region": "Extrême-Nord", "lat": 10.7167, "lng": 13.6833, "major": False, "airport": False, "population": 6000, "type": "arrondissement"},
    {"name": "Dziguilao", "region": "Extrême-Nord", "lat": 10.4167, "lng": 14.9667, "major": False, "airport": False, "population": 4000, "type": "arrondissement"},
    {"name": "Guidiguis", "region": "Extrême-Nord", "lat": 10.4833, "lng": 14.9167, "major": False, "airport": False, "population": 8000, "type": "arrondissement"},
    {"name": "Hina", "region": "Extrême-Nord", "lat": 11.1833, "lng": 13.9833, "major": False, "airport": False, "population": 5000, "type": "arrondissement"},
    {"name": "Kaélé", "region": "Extrême-Nord", "lat": 10.1000, "lng": 14.4667, "major": False, "airport": False, "population": 32000, "type": "arrondissement"},
    {"name": "Kar-Hay", "region": "Extrême-Nord", "lat": 10.2000, "lng": 14.3833, "major": False, "airport": False, "population": 7000, "type": "arrondissement"},
    {"name": "Kolofata", "region": "Extrême-Nord", "lat": 11.0667, "lng": 14.2667, "major": False, "airport": False, "population": 15000, "type": "arrondissement"},
    {"name": "Logone-Birni", "region": "Extrême-Nord", "lat": 12.1167, "lng": 14.9667, "major": False, "airport": False, "population": 20000, "type": "arrondissement"},
    {"name": "Maga", "region": "Extrême-Nord", "lat": 10.9167, "lng": 15.2000, "major": False, "airport": False, "population": 25000, "type": "arrondissement"},
    {"name": "Meri", "region": "Extrême-Nord", "lat": 10.6167, "lng": 14.2500, "major": False, "airport": False, "population": 12000, "type": "arrondissement"}
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

@api_router.get("/weather/{city}")
async def get_city_weather(city: str):
    """Get real-time weather for a city"""
    city_info = next((c for c in ENHANCED_CAMEROON_CITIES if c["name"].lower() == city.lower()), None)
    
    if not city_info:
        raise HTTPException(status_code=404, detail="City not found")
    
    weather = generate_weather_data(city_info["name"], city_info["region"])
    return weather

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

# === ADVANCED ADMIN ENDPOINTS ===

@api_router.post("/admin/vehicles")
async def add_vehicle(vehicle_data: dict):
    """Admin endpoint to add new vehicles"""
    try:
        vehicle = Vehicle(
            agency_id=vehicle_data.get("agency_id"),
            agency_name=vehicle_data.get("agency_name"),
            model=vehicle_data.get("model"),
            brand=vehicle_data.get("brand"),
            year=int(vehicle_data.get("year")),
            color=vehicle_data.get("color"),
            license_plate=vehicle_data.get("license_plate"),
            capacity=int(vehicle_data.get("capacity")),
            vehicle_type=vehicle_data.get("vehicle_type"),
            driver_name=vehicle_data.get("driver_name", ""),
            driver_phone=vehicle_data.get("driver_phone", ""),
            current_route=vehicle_data.get("current_route", ""),
        )
        
        # Save to database
        await db.vehicles.insert_one(vehicle.dict())
        
        return {
            "vehicle_id": vehicle.id,
            "message": "Véhicule ajouté avec succès",
            "vehicle": vehicle.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de l'ajout du véhicule: {str(e)}")

@api_router.get("/admin/vehicles")
async def get_all_vehicles():
    """Get all vehicles with pagination"""
    vehicles = await db.vehicles.find().to_list(length=None)
    
    # Clean ObjectId for JSON serialization
    for vehicle in vehicles:
        if "_id" in vehicle:
            del vehicle["_id"]
            
    return {
        "vehicles": vehicles,
        "total": len(vehicles)
    }

@api_router.put("/admin/vehicles/{vehicle_id}")
async def update_vehicle(vehicle_id: str, vehicle_data: dict):
    """Update vehicle information"""
    vehicle = await db.vehicles.find_one({"id": vehicle_id})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Update vehicle data
    update_data = {
        "model": vehicle_data.get("model", vehicle["model"]),
        "brand": vehicle_data.get("brand", vehicle["brand"]),
        "year": int(vehicle_data.get("year", vehicle["year"])),
        "color": vehicle_data.get("color", vehicle["color"]),
        "license_plate": vehicle_data.get("license_plate", vehicle["license_plate"]),
        "capacity": int(vehicle_data.get("capacity", vehicle["capacity"])),
        "status": vehicle_data.get("status", vehicle["status"]),
        "driver_name": vehicle_data.get("driver_name", vehicle.get("driver_name", "")),
        "driver_phone": vehicle_data.get("driver_phone", vehicle.get("driver_phone", "")),
        "current_route": vehicle_data.get("current_route", vehicle.get("current_route", "")),
    }
    
    await db.vehicles.update_one(
        {"id": vehicle_id},
        {"$set": update_data}
    )
    
    return {
        "vehicle_id": vehicle_id,
        "message": "Véhicule mis à jour avec succès",
        "updated_data": update_data
    }

@api_router.delete("/admin/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: str):
    """Delete a vehicle"""
    result = await db.vehicles.delete_one({"id": vehicle_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return {"message": "Véhicule supprimé avec succès"}

@api_router.post("/admin/courier-carriers")
async def add_courier_carrier(carrier_data: dict):
    """Admin endpoint to add courier carriers"""
    try:
        carrier = CourierCarrier(
            name=carrier_data.get("name"),
            phone=carrier_data.get("phone"),
            email=carrier_data.get("email", ""),
            license_number=carrier_data.get("license_number"),
            vehicle_type=carrier_data.get("vehicle_type"),
            coverage_areas=carrier_data.get("coverage_areas", []),
            rating=float(carrier_data.get("rating", 4.0))
        )
        
        await db.courier_carriers.insert_one(carrier.dict())
        
        return {
            "carrier_id": carrier.id,
            "message": "Transporteur de colis ajouté avec succès",
            "carrier": carrier.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur: {str(e)}")

@api_router.get("/courier-carriers")
async def get_courier_carriers():
    """Get all active courier carriers"""
    carriers = await db.courier_carriers.find({"active": True}).to_list(length=None)
    
    for carrier in carriers:
        if "_id" in carrier:
            del carrier["_id"]
            
    return {"carriers": carriers}

@api_router.post("/admin/app-settings")
async def update_app_setting(setting_data: dict):
    """Admin endpoint to update app settings"""
    try:
        setting = AppSettings(
            setting_key=setting_data.get("setting_key"),
            setting_value=setting_data.get("setting_value"),
            setting_type=setting_data.get("setting_type", "text"),
            description=setting_data.get("description", ""),
            updated_by=setting_data.get("admin_id", "admin")
        )
        
        # Update or insert setting
        await db.app_settings.update_one(
            {"setting_key": setting.setting_key},
            {"$set": setting.dict()},
            upsert=True
        )
        
        return {
            "message": "Paramètre mis à jour avec succès",
            "setting": setting.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur: {str(e)}")

@api_router.get("/admin/app-settings")
async def get_app_settings():
    """Get all app settings"""
    settings = await db.app_settings.find().to_list(length=None)
    
    for setting in settings:
        if "_id" in setting:
            del setting["_id"]
            
    return {"settings": settings}

@api_router.post("/admin/policies")
async def create_policy_document(policy_data: dict):
    """Admin endpoint to create/update policy documents"""
    try:
        policy = PolicyDocument(
            title=policy_data.get("title"),
            content=policy_data.get("content"),
            document_type=policy_data.get("document_type"),
            language=policy_data.get("language", "fr"),
            version=policy_data.get("version", "1.0")
        )
        
        await db.policy_documents.insert_one(policy.dict())
        
        return {
            "policy_id": policy.id,
            "message": "Document de politique créé avec succès",
            "policy": policy.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur: {str(e)}")

@api_router.get("/policies")
async def get_policies():
    """Get all active policy documents"""
    policies = await db.policy_documents.find({"active": True}).to_list(length=None)
    
    for policy in policies:
        if "_id" in policy:
            del policy["_id"]
            
    return {"policies": policies}

@api_router.get("/policies/{document_type}")
async def get_policy_by_type(document_type: str):
    """Get specific policy document by type"""
    policy = await db.policy_documents.find_one({
        "document_type": document_type,
        "active": True
    })
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy document not found")
    
    if "_id" in policy:
        del policy["_id"]
        
    return {"policy": policy}

@api_router.get("/administrative-structure")
async def get_administrative_structure():
    """Get simplified administrative structure: Region → Cities (Chef-lieux)"""
    return {"structure": CAMEROON_ADMINISTRATIVE_STRUCTURE}

@api_router.get("/cities/{region}")
async def get_cities_by_region(region: str):
    """Get cities (chef-lieux) of a specific region"""
    if region not in CAMEROON_ADMINISTRATIVE_STRUCTURE:
        raise HTTPException(status_code=404, detail="Region not found")
    
    return {
        "region": region,
        "cities": CAMEROON_ADMINISTRATIVE_STRUCTURE[region]["cities"]
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