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
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="BusConnect Cameroun - Complete Registration System", description="Advanced registration system with document validation")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# === ENHANCED USER REGISTRATION MODELS ===

class DocumentUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    document_type: str  # "authorization_transport", "driving_license", "vehicle_photo", "identity_card"
    file_name: str
    file_data: str  # base64 encoded
    file_size: int
    mime_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    validation_status: str = "pending"  # pending, approved, rejected
    admin_notes: Optional[str] = None
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None

class Vehicle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str
    brand: str
    model: str
    year: int
    plate_number: str
    capacity: int
    vehicle_type: str  # "bus", "minibus", "car"
    color: str
    insurance_expiry: str
    technical_control_expiry: str
    photos: List[str] = []  # Document IDs
    features: List[str] = []  # ["AC", "WiFi", "TV", etc.]
    status: str = "pending_validation"  # pending_validation, approved, rejected, active, maintenance
    validation_notes: Optional[str] = None
    routes_assigned: List[str] = []  # List of route IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ValidationCode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    code: str
    code_type: str  # "sms", "email", "registration"
    phone_or_email: str
    expires_at: datetime
    used: bool = False
    attempts: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EnhancedUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: Optional[EmailStr] = None
    phone: str
    first_name: str
    last_name: str
    user_type: str  # "client", "agency", "individual_transport", "occasional_transport"
    
    # Registration info
    registration_status: str = "pending_validation"  # pending_validation, documents_required, approved, rejected
    email_verified: bool = False
    phone_verified: bool = False
    
    # Agency specific fields
    agency_name: Optional[str] = None
    agency_address: Optional[str] = None
    agency_license_number: Optional[str] = None
    
    # Transport provider fields
    driving_license_number: Optional[str] = None
    driving_license_expiry: Optional[str] = None
    transport_experience_years: Optional[int] = None
    preferred_routes: List[str] = []
    
    # Documents
    uploaded_documents: List[str] = []  # Document IDs
    vehicles: List[str] = []  # Vehicle IDs
    
    # Validation
    validation_notes: Optional[str] = None
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    
    # Standard fields
    subscription_type: str = "standard"
    loyalty_points: int = 0
    profile_complete: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserRegistration(BaseModel):
    email: Optional[EmailStr] = None
    phone: str
    first_name: str
    last_name: str
    user_type: str
    
    # Agency fields (if user_type == "agency")
    agency_name: Optional[str] = None
    agency_address: Optional[str] = None
    agency_license_number: Optional[str] = None
    
    # Transport provider fields (if user_type in ["individual_transport", "occasional_transport"])
    driving_license_number: Optional[str] = None
    driving_license_expiry: Optional[str] = None
    transport_experience_years: Optional[int] = None
    
    # Client preferences
    preferred_language: str = "fr"

class AdminAction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    action_type: str  # "approve_user", "reject_user", "approve_document", "reject_document", "approve_vehicle"
    target_id: str  # User ID, Document ID, or Vehicle ID
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Route(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider_id: str  # User ID of transport provider
    vehicle_id: str
    origin: str
    destination: str
    departure_times: List[str]  # ["06:00", "14:00", "20:00"]
    duration: str
    base_price: int
    service_class: str
    available_days: List[str]  # ["monday", "tuesday", etc.]
    max_passengers: int
    amenities: List[str]
    status: str = "active"  # active, inactive, suspended
    created_at: datetime = Field(default_factory=datetime.utcnow)

# === UTILITY FUNCTIONS ===

def generate_validation_code():
    """Generate 6-digit validation code"""
    return str(random.randint(100000, 999999))

def validate_phone_number(phone: str) -> bool:
    """Validate Cameroon phone number format"""
    # Cameroon phone patterns: +237XXXXXXXXX or 237XXXXXXXXX or 6XXXXXXXX
    patterns = [
        r'^\+237[67]\d{8}$',  # +237XXXXXXXXX
        r'^237[67]\d{8}$',    # 237XXXXXXXXX  
        r'^[67]\d{8}$'        # 6XXXXXXXX or 7XXXXXXXX
    ]
    
    return any(re.match(pattern, phone) for pattern in patterns)

def normalize_phone_number(phone: str) -> str:
    """Normalize phone number to +237XXXXXXXXX format"""
    # Remove spaces and special chars except +
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    if clean_phone.startswith('+237'):
        return clean_phone
    elif clean_phone.startswith('237'):
        return '+' + clean_phone
    elif clean_phone.startswith(('6', '7')) and len(clean_phone) == 9:
        return '+237' + clean_phone
    else:
        raise ValueError("Invalid phone number format")

async def send_sms_code(phone: str, code: str) -> bool:
    """Send SMS validation code (mock implementation)"""
    try:
        # In real implementation, integrate with SMS provider (Twilio, etc.)
        print(f"SMS to {phone}: Your BusConnect validation code is: {code}")
        return True
    except Exception as e:
        print(f"SMS sending failed: {e}")
        return False

async def send_email_code(email: str, code: str) -> bool:
    """Send email validation code (mock implementation)"""
    try:
        # In real implementation, integrate with email service
        print(f"Email to {email}: Your BusConnect validation code is: {code}")
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

# === REGISTRATION API ENDPOINTS ===

@api_router.get("/")
async def root():
    return {
        "message": "BusConnect Cameroun - Complete Registration System", 
        "version": "4.0",
        "user_types": ["client", "agency", "individual_transport", "occasional_transport"],
        "features": [
            "Multi-level User Registration",
            "Document Upload & Validation", 
            "SMS/Email Verification",
            "Admin Approval System",
            "Vehicle Management"
        ]
    }

@api_router.post("/register/initiate")
async def initiate_registration(registration: UserRegistration):
    """Step 1: Initiate user registration with basic info"""
    
    # Validate phone number
    if not validate_phone_number(registration.phone):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    # Normalize phone
    normalized_phone = normalize_phone_number(registration.phone)
    
    # Check if user already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"phone": normalized_phone},
            {"email": registration.email} if registration.email else {}
        ]
    })
    
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists with this phone or email")
    
    # Validate required fields based on user type
    if registration.user_type == "agency":
        if not all([registration.agency_name, registration.agency_address]):
            raise HTTPException(status_code=400, detail="Agency name and address are required")
    
    elif registration.user_type in ["individual_transport", "occasional_transport"]:
        if not all([registration.driving_license_number, registration.driving_license_expiry]):
            raise HTTPException(status_code=400, detail="Driving license information is required")
    
    # Create user record
    user_data = registration.dict()
    user_data["phone"] = normalized_phone
    user = EnhancedUser(**user_data)
    
    # Determine initial status based on user type
    if user.user_type == "client":
        user.registration_status = "pending_validation"  # Just needs phone/email verification
    else:
        user.registration_status = "documents_required"  # Needs document upload
    
    await db.users.insert_one(user.dict())
    
    # Send validation code
    code = generate_validation_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Prefer phone verification for Cameroon market
    if normalized_phone:
        validation_code = ValidationCode(
            user_id=user.id,
            code=code,
            code_type="sms",
            phone_or_email=normalized_phone,
            expires_at=expires_at
        )
        
        success = await send_sms_code(normalized_phone, code)
        if not success and registration.email:
            # Fallback to email if SMS fails
            validation_code.code_type = "email"
            validation_code.phone_or_email = registration.email
            success = await send_email_code(registration.email, code)
    
    elif registration.email:
        validation_code = ValidationCode(
            user_id=user.id,
            code=code,
            code_type="email", 
            phone_or_email=registration.email,
            expires_at=expires_at
        )
        success = await send_email_code(registration.email, code)
    
    else:
        raise HTTPException(status_code=400, detail="Phone number or email is required")
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send validation code")
    
    await db.validation_codes.insert_one(validation_code.dict())
    
    return {
        "user_id": user.id,
        "registration_status": user.registration_status,
        "verification_sent_to": validation_code.phone_or_email,
        "verification_method": validation_code.code_type,
        "next_step": "verify_contact" if user.user_type == "client" else "upload_documents",
        "message": f"Validation code sent to {validation_code.phone_or_email}"
    }

@api_router.post("/register/verify")
async def verify_registration_code(user_id: str, code: str):
    """Step 2: Verify SMS/Email code"""
    
    # Find validation code
    validation_record = await db.validation_codes.find_one({
        "user_id": user_id,
        "used": False,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    
    if not validation_record:
        raise HTTPException(status_code=404, detail="Invalid or expired validation code")
    
    # Check code
    if validation_record["code"] != code:
        # Increment attempts
        await db.validation_codes.update_one(
            {"id": validation_record["id"]},
            {"$inc": {"attempts": 1}}
        )
        
        if validation_record["attempts"] >= 2:  # 3 attempts total
            await db.validation_codes.update_one(
                {"id": validation_record["id"]},
                {"$set": {"used": True}}
            )
            raise HTTPException(status_code=429, detail="Too many attempts. Request new code.")
        
        raise HTTPException(status_code=400, detail="Invalid validation code")
    
    # Mark code as used
    await db.validation_codes.update_one(
        {"id": validation_record["id"]},
        {"$set": {"used": True}}
    )
    
    # Update user verification status
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_fields = {}
    if validation_record["code_type"] == "sms":
        update_fields["phone_verified"] = True
    else:
        update_fields["email_verified"] = True
    
    # If client, complete registration
    if user["user_type"] == "client":
        update_fields["registration_status"] = "approved"
        update_fields["profile_complete"] = True
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": update_fields}
    )
    
    return {
        "success": True,
        "user_type": user["user_type"],
        "registration_status": update_fields.get("registration_status", user["registration_status"]),
        "next_step": "complete" if user["user_type"] == "client" else "upload_documents",
        "message": "Verification successful"
    }

@api_router.post("/register/upload-document")
async def upload_document(
    user_id: str = Form(...),
    document_type: str = Form(...),  # "authorization_transport", "driving_license", "vehicle_photo", "identity_card"
    file: UploadFile = File(...)
):
    """Step 3: Upload required documents"""
    
    # Validate user exists and needs documents
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["registration_status"] not in ["documents_required", "pending_validation"]:
        raise HTTPException(status_code=400, detail="User not in document upload phase")
    
    # Validate document type for user type
    valid_docs = {
        "agency": ["authorization_transport", "identity_card"],
        "individual_transport": ["driving_license", "vehicle_photo", "identity_card"], 
        "occasional_transport": ["driving_license", "vehicle_photo", "identity_card"]
    }
    
    if document_type not in valid_docs.get(user["user_type"], []):
        raise HTTPException(status_code=400, detail=f"Invalid document type for {user['user_type']}")
    
    # Validate file
    if file.size > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")
    
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, PDF allowed")
    
    # Read and encode file
    file_data = await file.read()
    file_base64 = base64.b64encode(file_data).decode('utf-8')
    
    # Create document record
    document = DocumentUpload(
        user_id=user_id,
        document_type=document_type,
        file_name=file.filename,
        file_data=file_base64,
        file_size=file.size,
        mime_type=file.content_type
    )
    
    await db.documents.insert_one(document.dict())
    
    # Update user's uploaded documents
    await db.users.update_one(
        {"id": user_id},
        {
            "$push": {"uploaded_documents": document.id},
            "$set": {"registration_status": "pending_validation"}
        }
    )
    
    # Check if all required documents uploaded
    user_docs = await db.documents.find({"user_id": user_id}).to_list(100)
    uploaded_types = [doc["document_type"] for doc in user_docs]
    
    required_docs = valid_docs[user["user_type"]]
    all_uploaded = all(doc_type in uploaded_types for doc_type in required_docs)
    
    return {
        "document_id": document.id,
        "uploaded_documents": uploaded_types,
        "required_documents": required_docs,
        "all_required_uploaded": all_uploaded,
        "next_step": "wait_approval" if all_uploaded else "upload_more_documents",
        "message": f"Document {document_type} uploaded successfully"
    }

@api_router.post("/register/add-vehicle")
async def add_vehicle(
    user_id: str,
    vehicle_data: Dict[str, Any]
):
    """Add vehicle for transport providers"""
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["user_type"] not in ["individual_transport", "occasional_transport"]:
        raise HTTPException(status_code=400, detail="Only transport providers can add vehicles")
    
    # Create vehicle record
    vehicle = Vehicle(
        owner_id=user_id,
        **vehicle_data
    )
    
    await db.vehicles.insert_one(vehicle.dict())
    
    # Update user's vehicles
    await db.users.update_one(
        {"id": user_id},
        {"$push": {"vehicles": vehicle.id}}
    )
    
    return {
        "vehicle_id": vehicle.id,
        "status": "pending_validation",
        "message": "Vehicle added successfully. Waiting for admin approval."
    }

# === ADMIN ENDPOINTS ===

@api_router.get("/admin/pending-users")
async def get_pending_users():
    """Get users pending admin approval"""
    
    users = await db.users.find({
        "registration_status": "pending_validation",
        "user_type": {"$in": ["agency", "individual_transport", "occasional_transport"]}
    }).to_list(100)
    
    # Enrich with document info
    for user in users:
        if user["uploaded_documents"]:
            docs = await db.documents.find({
                "id": {"$in": user["uploaded_documents"]}
            }).to_list(100)
            user["documents"] = docs
        else:
            user["documents"] = []
    
    return {"pending_users": users}

@api_router.get("/admin/user/{user_id}/details")
async def get_user_details_for_admin(user_id: str):
    """Get complete user details for admin review"""
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get documents
    documents = []
    if user["uploaded_documents"]:
        documents = await db.documents.find({
            "id": {"$in": user["uploaded_documents"]}
        }).to_list(100)
    
    # Get vehicles
    vehicles = []
    if user["vehicles"]:
        vehicles = await db.vehicles.find({
            "id": {"$in": user["vehicles"]}
        }).to_list(100)
    
    return {
        "user": user,
        "documents": documents,
        "vehicles": vehicles
    }

@api_router.post("/admin/approve-user")
async def approve_user(user_id: str, admin_id: str, notes: Optional[str] = None):
    """Approve user registration"""
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user status
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "registration_status": "approved",
                "validation_notes": notes,
                "validated_by": admin_id,
                "validated_at": datetime.utcnow(),
                "profile_complete": True
            }
        }
    )
    
    # Log admin action
    admin_action = AdminAction(
        admin_id=admin_id,
        action_type="approve_user",
        target_id=user_id,
        notes=notes
    )
    await db.admin_actions.insert_one(admin_action.dict())
    
    # Auto-approve user's documents and vehicles
    await db.documents.update_many(
        {"user_id": user_id},
        {
            "$set": {
                "validation_status": "approved",
                "validated_by": admin_id,
                "validated_at": datetime.utcnow()
            }
        }
    )
    
    await db.vehicles.update_many(
        {"owner_id": user_id},
        {
            "$set": {
                "status": "approved",
                "validation_notes": "Auto-approved with user"
            }
        }
    )
    
    return {
        "success": True,
        "message": f"User {user['first_name']} {user['last_name']} approved successfully"
    }

@api_router.post("/admin/reject-user")
async def reject_user(user_id: str, admin_id: str, reason: str):
    """Reject user registration"""
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "registration_status": "rejected",
                "validation_notes": reason,
                "validated_by": admin_id,
                "validated_at": datetime.utcnow()
            }
        }
    )
    
    # Log admin action
    admin_action = AdminAction(
        admin_id=admin_id,
        action_type="reject_user",
        target_id=user_id,
        notes=reason
    )
    await db.admin_actions.insert_one(admin_action.dict())
    
    return {
        "success": True,
        "message": f"User registration rejected: {reason}"
    }

@api_router.get("/admin/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard statistics"""
    
    # Count users by status
    user_stats = {}
    for status in ["pending_validation", "approved", "rejected"]:
        count = await db.users.count_documents({"registration_status": status})
        user_stats[status] = count
    
    # Count by user type
    type_stats = {}
    for user_type in ["client", "agency", "individual_transport", "occasional_transport"]:
        count = await db.users.count_documents({"user_type": user_type})
        type_stats[user_type] = count
    
    # Recent registrations
    recent_users = await db.users.find({}).sort("created_at", -1).limit(10).to_list(10)
    
    # Pending documents
    pending_docs = await db.documents.count_documents({"validation_status": "pending"})
    
    return {
        "user_statistics": user_stats,
        "type_statistics": type_stats,
        "recent_registrations": recent_users,
        "pending_documents": pending_docs,
        "total_users": sum(type_stats.values())
    }

# === PUBLIC ENDPOINTS ===

@api_router.get("/users/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile (public info only)"""
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return only safe fields
    safe_profile = {
        "id": user["id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "user_type": user["user_type"],
        "registration_status": user["registration_status"],
        "profile_complete": user.get("profile_complete", False)
    }
    
    if user["user_type"] == "agency":
        safe_profile["agency_name"] = user.get("agency_name")
    
    return safe_profile

@api_router.get("/providers/approved")
async def get_approved_providers():
    """Get approved transport providers for public display"""
    
    providers = await db.users.find({
        "user_type": {"$in": ["agency", "individual_transport", "occasional_transport"]},
        "registration_status": "approved"
    }).to_list(100)
    
    # Get their vehicles and routes
    for provider in providers:
        if provider["vehicles"]:
            vehicles = await db.vehicles.find({
                "id": {"$in": provider["vehicles"]},
                "status": "approved"
            }).to_list(100)
            provider["approved_vehicles"] = vehicles
        
        # Get routes (to be implemented)
        provider["active_routes"] = []
    
    return {"approved_providers": providers}

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