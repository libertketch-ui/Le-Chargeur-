import React, { useState, useEffect, useMemo } from "react";
import "./App.css";
import axios from "axios";
import RegistrationSystem from "./RegistrationSystem";
import PaymentKeypad from "./PaymentKeypad";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { Switch } from "./components/ui/switch";
import { Alert, AlertDescription } from "./components/ui/alert";
import { Textarea } from "./components/ui/textarea";
import { toast } from "sonner";
import { Toaster } from "./components/ui/sonner";
import { 
  Search, 
  Navigation, 
  Ticket, 
  Gift, 
  User, 
  MapPin, 
  Calendar, 
  Users, 
  Clock, 
  Bus,
  Wifi,
  Car,
  Coffee,
  Monitor,
  Zap,
  Utensils,
  CheckCircle,
  AlertCircle,
  Loader2,
  Plane,
  Plus,
  Bike,
  Dumbbell,
  Backpack,
  Briefcase,
  QrCode,
  Compass,
  Route,
  Star,
  Leaf,
  Shield,
  Phone,
  Crown,
  Heart,
  Award,
  Settings,
  CreditCard,
  Globe,
  TrendingUp,
  TrendingDown,
  Smartphone,
  Bell,
  Target,
  ArrowRight,
  DollarSign,
  Percent,
  CloudRain,
  Sun,
  Wind,
  Droplets,
  Mountain,
  Camera,
  Package,
  MessageCircle,
  Mail,
  PhoneCall,
  Calculator,
  CreditCard as PaymentCard,
  Banknote,
  Receipt,
  Map,
  Locate,
  Navigation2,
  Truck,
  Package2,
  Send,
  Eye,
  Download,
  Share2,
  Copy,
  ExternalLink,
  Minus,
  PlusCircle,
  MinusCircle,
  Timer,
  AlertTriangle,
  Info,
  Building
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Connect237 Logo Component
const Connect237Logo = ({ size = "normal" }) => {
  const logoSizes = {
    small: { container: "w-8 h-8", text: "text-lg" },
    normal: { container: "w-12 h-12", text: "text-2xl" },
    large: { container: "w-16 h-16", text: "text-3xl" }
  };
  
  const { container, text } = logoSizes[size];
  
  return (
    <div className="flex items-center gap-3">
      <div className={`${container} bg-gradient-to-br from-green-600 via-yellow-500 to-red-600 rounded-xl flex items-center justify-center shadow-xl`}>
        <div className="bg-white rounded-lg p-1">
          <div className="text-green-600 font-bold text-xs">237</div>
        </div>
      </div>
      <div>
        <h1 className={`${text} font-bold bg-gradient-to-r from-green-600 to-red-600 bg-clip-text text-transparent`}>
          Connect237
        </h1>
        <p className="text-xs text-gray-600 font-semibold">Transport & Courrier</p>
      </div>
    </div>
  );
};

function Connect237App() {
  const [activeTab, setActiveTab] = useState("home");
  const [cities, setCities] = useState([]);
  const [agencies, setAgencies] = useState([]);
  const [weatherData, setWeatherData] = useState([]);
  const [attractions, setAttractions] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [courierServices, setCourierServices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showRegistration, setShowRegistration] = useState(false);
  const [currentTourismSlide, setCurrentTourismSlide] = useState(0);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [adminVehicles, setAdminVehicles] = useState([]);
  const [courierCarriers, setCourierCarriers] = useState([]);
  const [selectedAgency, setSelectedAgency] = useState("");
  const [selectedCarrier, setSelectedCarrier] = useState("");
  const [selectedOriginRegion, setSelectedOriginRegion] = useState("");
  const [selectedDestinationRegion, setSelectedDestinationRegion] = useState("");
  const [selectedOriginDepartment, setSelectedOriginDepartment] = useState("");
  const [selectedDestinationDepartment, setSelectedDestinationDepartment] = useState("");
  const [availableOriginDepartments, setAvailableOriginDepartments] = useState([]);
  const [availableDestinationDepartments, setAvailableDestinationDepartments] = useState([]);
  const [availableOriginCities, setAvailableOriginCities] = useState([]);
  const [availableDestinationCities, setAvailableDestinationCities] = useState([]);
  const [routePricing, setRoutePricing] = useState([]);
  const [showWallet, setShowWallet] = useState(false);
  const [administrativeStructure, setAdministrativeStructure] = useState({});

  // Enhanced search state
  const [searchForm, setSearchForm] = useState({
    origin: "",
    destination: "",
    departure_date: "",
    departure_time: "",
    passengers: 1,
    custom_passenger_count: null,
    service_class: "economy",
    pickup_location: { address: "", coordinates: { lat: 0, lng: 0 } },
    dropoff_location: { address: "", coordinates: { lat: 0, lng: 0 } },
    additional_info: ""
  });

  // Enhanced payment state
  const [paymentForm, setPaymentForm] = useState({
    type: "mobile_money", // mobile_money, on_site, account_credit, voucher
    provider: "MTN", // MTN, ORANGE
    account_number: "",
    voucher_code: "",
    reservation_only: false
  });
  
  const [language, setLanguage] = useState("fr"); // fr, en

  // Calculator state
  const [calculator, setCalculator] = useState({
    visible: false,
    base_price: 0,
    total_amount: 0,
    reservation_fee: 500,
    remaining_amount: 0
  });

  // Courier state
  const [courierForm, setCourierForm] = useState({
    recipient_name: "",
    recipient_phone: "",
    origin: "",
    destination: "",
    pickup_address: "",
    delivery_address: "",
    package_type: "documents",
    weight_kg: 1,
    declared_value: 10000,
    urgent: false,
    insurance: false,
    pickup_time: "",
    delivery_instructions: ""
  });

  // Vehicle tracking state
  const [trackingData, setTrackingData] = useState({});
  const [selectedVehicle, setSelectedVehicle] = useState(null);

  const user = {
    id: "user123",
    name: "Jean Dupont",
    phone: "+237650123456",
    email: "jean@connect237.cm"
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // Auto-rotation des images touristiques toutes les 15 secondes
  useEffect(() => {
    if (attractions.length > 0) {
      const interval = setInterval(() => {
        setCurrentTourismSlide((prev) => (prev + 1) % attractions.length);
      }, 15000); // 15 secondes

      return () => clearInterval(interval);
    }
  }, [attractions]);

  const loadInitialData = async () => {
    try {
      await Promise.all([
        loadCities(),
        loadAgencies(),
        loadWeatherData(),
        loadAttractions(),
        loadUserBookings(),
        loadCourierCarriers(),
        loadAdministrativeStructure()
      ]);
    } catch (error) {
      console.error("Error loading initial data:", error);
      toast.error("Erreur lors du chargement des données");
    }
  };

  const loadCities = async () => {
    try {
      const response = await axios.get(`${API}/cities/enhanced`);
      setCities(response.data.cities);
    } catch (error) {
      console.error("Error loading cities:", error);
    }
  };

  const loadAgencies = async () => {
    try {
      const response = await axios.get(`${API}/agencies`);
      setAgencies(response.data.agencies);
    } catch (error) {
      console.error("Error loading agencies:", error);
    }
  };

  const loadWeatherData = async () => {
    try {
      const response = await axios.get(`${API}/weather/cities`);
      setWeatherData(response.data.weather_data);
    } catch (error) {
      console.error("Error loading weather:", error);
    }
  };

  const loadAttractions = async () => {
    try {
      const response = await axios.get(`${API}/attractions`);
      setAttractions(response.data.attractions);
    } catch (error) {
      console.error("Error loading attractions:", error);
    }
  };

  const loadUserBookings = async () => {
    try {
      setBookings([
        { id: "1", route: "Yaoundé → Douala", date: "2023-12-15", status: "confirmed", price: 5000 },
        { id: "2", route: "Douala → Bafoussam", date: "2023-12-20", status: "pending", price: 4500 }
      ]);
    } catch (error) {
      console.error("Error loading user bookings:", error);
    }
  };

  const loadCourierCarriers = async () => {
    try {
      const response = await axios.get(`${API}/courier-carriers`);
      setCourierCarriers(response.data.carriers || []);
    } catch (error) {
      console.error("Error loading courier carriers:", error);
      // Default carriers if API fails
      setCourierCarriers([
        { name: "Moto Express", vehicle_type: "moto", rating: 4.2, coverage_areas: ["Yaoundé", "Douala"] },
        { name: "City Delivery", vehicle_type: "car", rating: 4.0, coverage_areas: ["Douala", "Bafoussam"] },
        { name: "Speed Courier", vehicle_type: "van", rating: 4.3, coverage_areas: ["Yaoundé", "Bertoua"] }
      ]);
    }
  };

  const calculatePayment = async () => {
    if (!searchForm.origin || !searchForm.destination) {
      toast.error("Veuillez sélectionner une origine et une destination");
      return;
    }

    setLoading(true);
    try {
      const params = new URLSearchParams({
        base_price: "5000", // Mock base price
        passenger_count: searchForm.passengers.toString(),
        payment_type: paymentForm.reservation_only ? "reservation" : "full"
      });

      if (searchForm.custom_passenger_count) {
        params.append("custom_count", searchForm.custom_passenger_count.toString());
      }

      const response = await axios.get(`${API}/payment/calculator?${params}`);
      setCalculator({
        visible: true,
        ...response.data
      });
    } catch (error) {
      console.error("Error calculating payment:", error);
      toast.error("Erreur lors du calcul");
    } finally {
      setLoading(false);
    }
  };

  const createBooking = async () => {
    setLoading(true);
    try {
      const bookingData = {
        user_id: user.id,
        agency_id: "agency_001",
        route_details: {
          id: "route_001",
          price: calculator.base_price_per_person || 5000
        },
        passenger_count: searchForm.passengers,
        custom_passenger_count: searchForm.custom_passenger_count,
        departure_date: searchForm.departure_date,
        departure_time: searchForm.departure_time,
        pickup_location: searchForm.pickup_location,
        dropoff_location: searchForm.dropoff_location,
        payment_method: paymentForm,
        special_requests: ""
      };

      const response = await axios.post(`${API}/booking/enhanced`, bookingData);
      
      if (paymentForm.type === "mobile_money") {
        // Show payment interface
        setActiveTab("payment");
        toast.info(`Code marchand: ${response.data.merchant_code}`);
      } else {
        toast.success(`Réservation créée ! Référence: ${response.data.booking_reference}`);
      }
      
      setBookings([...bookings, response.data]);
    } catch (error) {
      console.error("Error creating booking:", error);
      toast.error("Erreur lors de la réservation");
    } finally {
      setLoading(false);
    }
  };

  const bookCourierService = async () => {
    if (!courierForm.recipient_name || !courierForm.origin || !courierForm.destination) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }

    setLoading(true);
    try {
      const courierData = {
        ...courierForm,
        sender_id: user.id
      };

      const response = await axios.post(`${API}/courier/book`, courierData);
      toast.success(`Service courrier réservé ! Code: ${response.data.tracking_number}`);
      setCourierServices([...courierServices, response.data]);
      
      // Reset form
      setCourierForm({
        recipient_name: "",
        recipient_phone: "",
        origin: "",
        destination: "",
        pickup_address: "",
        delivery_address: "",
        package_type: "documents",
        weight_kg: 1,
        declared_value: 10000,
        urgent: false,
        insurance: false,
        pickup_time: "",
        delivery_instructions: ""
      });
    } catch (error) {
      console.error("Error booking courier:", error);
      toast.error("Erreur lors de la réservation courrier");
    } finally {
      setLoading(false);
    }
  };

  const trackVehicles = async (routeId = "route_001") => {
    try {
      const response = await axios.get(`${API}/tracking/route/${routeId}`);
      setTrackingData(response.data);
    } catch (error) {
      console.error("Error tracking vehicles:", error);
      toast.error("Erreur lors du suivi des véhicules");
    }
  };

  const getWeatherIcon = (description) => {
    if (description.includes("Ensoleillé")) return <Sun className="w-5 h-5 text-yellow-500" />;
    if (description.includes("Nuageux")) return <CloudRain className="w-5 h-5 text-gray-500" />;
    if (description.includes("Pluie")) return <CloudRain className="w-5 h-5 text-blue-500" />;
    return <Sun className="w-5 h-5 text-yellow-500" />;
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR').format(price);
  };

  const loadAdministrativeStructure = async () => {
    try {
      const response = await axios.get(`${API}/administrative-structure`);
      setAdministrativeStructure(response.data.structure || {});
    } catch (error) {
      console.error("Error loading administrative structure:", error);
    }
  };

  // Filter departments by region
  const handleOriginRegionChange = (region) => {
    setSelectedOriginRegion(region);
    const departments = administrativeStructure[region]?.departments || {};
    setAvailableOriginDepartments(Object.entries(departments));
    setSelectedOriginDepartment("");
    setAvailableOriginCities([]);
    setSearchForm(prev => ({ ...prev, origin: "" }));
  };

  const handleDestinationRegionChange = (region) => {
    setSelectedDestinationRegion(region);
    const departments = administrativeStructure[region]?.departments || {};
    setAvailableDestinationDepartments(Object.entries(departments));
    setSelectedDestinationDepartment("");
    setAvailableDestinationCities([]);
    setSearchForm(prev => ({ ...prev, destination: "" }));
  };

  // Filter chef-lieux by department
  const handleOriginDepartmentChange = (department) => {
    setSelectedOriginDepartment(department);
    const departmentInfo = administrativeStructure[selectedOriginRegion]?.departments[department];
    if (departmentInfo) {
      setAvailableOriginCities([{
        name: departmentInfo.chef_lieu,
        type: "chef-lieu",
        department: department,
        region: selectedOriginRegion,
        lat: departmentInfo.lat,
        lng: departmentInfo.lng
      }]);
    }
    setSearchForm(prev => ({ ...prev, origin: "" }));
  };

  const handleDestinationDepartmentChange = (department) => {
    setSelectedDestinationDepartment(department);
    const departmentInfo = administrativeStructure[selectedDestinationRegion]?.departments[department];
    if (departmentInfo) {
      setAvailableDestinationCities([{
        name: departmentInfo.chef_lieu,
        type: "chef-lieu",
        department: department,
        region: selectedDestinationRegion,
        lat: departmentInfo.lat,
        lng: departmentInfo.lng
      }]);
    }
    setSearchForm(prev => ({ ...prev, destination: "" }));
  };

  // Get available regions
  const getAvailableRegions = () => {
    return Object.keys(administrativeStructure).sort();
  };

  // Get route pricing for selected destination
  const getRoutePricing = (origin, destination) => {
    if (!origin || !destination) return [];
    
    const routeAgencies = agencies.filter(agency => {
      const routeString = `${origin}-${destination}`;
      const reverseRouteString = `${destination}-${origin}`;
      return agency.routes_served.some(route => 
        route.includes(origin) && route.includes(destination) ||
        route === routeString || route === reverseRouteString
      );
    });

    return routeAgencies.map(agency => ({
      ...agency,
      price: Math.floor(Math.random() * 3000) + 2000, // Random price between 2000-5000
      departure_times: ["06:00", "09:00", "12:00", "15:00", "18:00"],
      available_seats: Math.floor(Math.random() * 30) + 5
    }));
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copié dans le presse-papiers");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-yellow-50 to-red-50">
      <div className="container mx-auto p-4 max-w-7xl">
        
        {/* Enhanced Header with Connect237 Branding and Language Selector */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex-1"></div>
            <div className="flex items-center justify-center">
              <Connect237Logo size="large" />
            </div>
            
            {/* Language Selector */}
            <div className="flex-1 flex justify-end">
              <div className="flex items-center gap-3">
                <div className="text-xs text-gray-600">
                  {language === "fr" ? "Langue:" : "Language:"}
                </div>
                <div className="flex bg-gray-200 rounded-lg overflow-hidden">
                  <button 
                    onClick={() => setLanguage("fr")}
                    className={`px-3 py-1 text-xs font-bold transition-all ${
                      language === "fr" ? 'bg-green-600 text-white' : 'text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    🇫🇷 FR
                  </button>
                  <button 
                    onClick={() => setLanguage("en")}
                    className={`px-3 py-1 text-xs font-bold transition-all ${
                      language === "en" ? 'bg-green-600 text-white' : 'text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    🇬🇧 EN
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              {language === "fr" ? "Plateforme Intégrée de Transport du Cameroun" : "Integrated Transport Platform of Cameroon"}
            </h2>
            <p className="text-gray-600 text-lg">
              {language === "fr" ? "Transport • Courrier • Suivi GPS • Météo • Tourisme" : "Transport • Courier • GPS Tracking • Weather • Tourism"}
            </p>
          </div>

          {/* Quick Contact Bar */}
          <div className="flex justify-center gap-4 mb-6">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => window.open("https://wa.me/237699000000", "_blank")}
              className="border-green-500 text-green-600 hover:bg-green-50"
            >
              <MessageCircle className="w-4 h-4 mr-2" />
              WhatsApp
            </Button>
            
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => window.open("mailto:support@connect237.cm", "_blank")}
              className="border-blue-500 text-blue-600 hover:bg-blue-50"
            >
              <Mail className="w-4 h-4 mr-2" />
              Email
            </Button>
            
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => window.open("tel:+237677000000", "_blank")}
              className="border-orange-500 text-orange-600 hover:bg-orange-50"
            >
              <PhoneCall className="w-4 h-4 mr-2" />
              Appel
            </Button>
          </div>

          {/* Weather Widget */}
          {weatherData.length > 0 && (
            <Card className="mb-6 bg-gradient-to-r from-blue-100 to-cyan-100 border-0">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-3">
                  <CloudRain className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-blue-800">Météo en temps réel</span>
                </div>
                <div className="flex overflow-x-auto gap-4 pb-2">
                  {weatherData.slice(0, 6).map((weather, idx) => (
                    <div key={idx} className="flex-shrink-0 bg-white/70 rounded-lg p-3 min-w-[120px] text-center">
                      <div className="font-semibold text-sm">{weather.city}</div>
                      <div className="flex items-center justify-center my-1">
                        {getWeatherIcon(weather.description)}
                      </div>
                      <div className="font-bold text-lg text-blue-600">{weather.temperature}°C</div>
                      <div className="text-xs text-gray-600">{weather.description}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Enhanced Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-6 mb-8 bg-white shadow-xl rounded-2xl p-2">
            <TabsTrigger 
              value="home" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-green-500 data-[state=active]:to-red-500 data-[state=active]:text-white rounded-xl transition-all"
            >
              <Bus className="w-4 h-4" />
              <span className="hidden md:inline">Accueil</span>
            </TabsTrigger>
            <TabsTrigger 
              value="search" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-green-500 data-[state=active]:to-red-500 data-[state=active]:text-white rounded-xl transition-all"
            >
              <Search className="w-4 h-4" />
              <span className="hidden md:inline">Recherche</span>
            </TabsTrigger>
            <TabsTrigger 
              value="courier" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-green-500 data-[state=active]:to-red-500 data-[state=active]:text-white rounded-xl transition-all"
            >
              <Package2 className="w-4 h-4" />
              <span className="hidden md:inline">Courrier</span>
            </TabsTrigger>
            <TabsTrigger 
              value="tracking" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-green-500 data-[state=active]:to-red-500 data-[state=active]:text-white rounded-xl transition-all"
            >
              <Map className="w-4 h-4" />
              <span className="hidden md:inline">Suivi GPS</span>
            </TabsTrigger>
            <TabsTrigger 
              value="tourism" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-green-500 data-[state=active]:to-red-500 data-[state=active]:text-white rounded-xl transition-all"
            >
              <Camera className="w-4 h-4" />
              <span className="hidden md:inline">Tourisme</span>
            </TabsTrigger>
            <TabsTrigger 
              value="profile" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-green-500 data-[state=active]:to-red-500 data-[state=active]:text-white rounded-xl transition-all"
            >
              <User className="w-4 h-4" />
              <span className="hidden md:inline">Profil</span>
            </TabsTrigger>
          </TabsList>

          {/* Home Tab */}
          <TabsContent value="home" className="space-y-6">
            
            {/* Main Services */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="hover:shadow-xl transition-all cursor-pointer" onClick={() => setActiveTab("search")}>
                <CardContent className="p-6 text-center">
                  <Bus className="w-12 h-12 text-green-600 mx-auto mb-4" />
                  <h3 className="font-bold text-lg mb-2">Transport Interurbain</h3>
                  <p className="text-gray-600 text-sm mb-4">Réservation avec {agencies.length} agences partenaires</p>
                  <Button className="w-full bg-gradient-to-r from-green-500 to-emerald-600">
                    Réserver un trajet
                  </Button>
                </CardContent>
              </Card>
              
              <Card className="hover:shadow-xl transition-all cursor-pointer" onClick={() => setActiveTab("courier")}>
                <CardContent className="p-6 text-center">
                  <Package2 className="w-12 h-12 text-yellow-600 mx-auto mb-4" />
                  <h3 className="font-bold text-lg mb-2">Service Courrier</h3>
                  <p className="text-gray-600 text-sm mb-4">Envoi de colis et documents</p>
                  <Button className="w-full bg-gradient-to-r from-yellow-500 to-orange-600">
                    Envoyer un colis
                  </Button>
                </CardContent>
              </Card>
              
              <Card className="hover:shadow-xl transition-all cursor-pointer" onClick={() => setActiveTab("tracking")}>
                <CardContent className="p-6 text-center">
                  <Map className="w-12 h-12 text-red-600 mx-auto mb-4" />
                  <h3 className="font-bold text-lg mb-2">Suivi GPS</h3>
                  <p className="text-gray-600 text-sm mb-4">Localisation temps réel des véhicules</p>
                  <Button className="w-full bg-gradient-to-r from-red-500 to-pink-600">
                    Suivre un véhicule
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Featured Agencies */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5" />
                  Agences Partenaires Premium
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {agencies.filter(agency => agency.premium_partner).slice(0, 4).map((agency) => (
                    <Card key={agency.name} className="text-center hover:shadow-md transition-all">
                      <CardContent className="p-4">
                        <img 
                          src={agency.logo_url} 
                          alt={agency.name}
                          className="w-16 h-16 mx-auto mb-3 rounded-lg object-cover"
                        />
                        <h4 className="font-semibold text-sm">{agency.name}</h4>
                        <div className="flex items-center justify-center gap-1 mt-2">
                          <Star className="w-3 h-3 text-yellow-500" />
                          <span className="text-xs">{agency.rating}</span>
                        </div>
                        <Badge variant="outline" className="mt-2 text-xs">
                          {agency.fleet_size} véhicules
                        </Badge>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Tourist Attractions Preview */}
            {attractions.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Mountain className="w-5 h-5" />
                    Découvrez le Cameroun
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {attractions.slice(0, 3).map((attraction, idx) => (
                      <Card key={idx} className="overflow-hidden hover:shadow-lg transition-all">
                        <div className="h-32 relative">
                          <img 
                            src={attraction.image_url}
                            alt={attraction.name}
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute top-2 right-2">
                            <Badge className="bg-black/70 text-white">
                              <Star className="w-3 h-3 mr-1" />
                              {attraction.rating}
                            </Badge>
                          </div>
                        </div>
                        <CardContent className="p-4">
                          <h4 className="font-semibold text-sm">{attraction.name}</h4>
                          <p className="text-xs text-gray-600">{attraction.city}, {attraction.region}</p>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="mt-2 w-full"
                            onClick={() => setActiveTab("tourism")}
                          >
                            En savoir plus
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Enhanced Search Tab */}
          <TabsContent value="search" className="space-y-6">
            <Card className="shadow-2xl">
              <CardHeader className="bg-gradient-to-r from-green-500 to-red-500 text-white">
                <CardTitle>Réservation de Transport</CardTitle>
                <CardDescription className="text-green-100">
                  Recherche avancée avec sélection du point de prise en charge
                </CardDescription>
              </CardHeader>
              <CardContent className="p-8 space-y-6">
                
                {/* 3-Level Hierarchical Route Selection */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <Label className="text-lg font-bold text-green-700">🌍 Point de Départ</Label>
                    
                    {/* Origin Region Selection */}
                    <div>
                      <Label>1️⃣ Région de départ</Label>
                      <Select onValueChange={handleOriginRegionChange}>
                        <SelectTrigger>
                          <SelectValue placeholder="Choisissez la région de départ" />
                        </SelectTrigger>
                        <SelectContent>
                          {getAvailableRegions().map((region) => (
                            <SelectItem key={region} value={region}>
                              🗺️ {region}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Origin Department Selection */}
                    <div>
                      <Label>2️⃣ Département de départ</Label>
                      <Select 
                        onValueChange={handleOriginDepartmentChange}
                        disabled={!selectedOriginRegion}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder={selectedOriginRegion ? "Choisissez le département" : "Sélectionnez d'abord une région"} />
                        </SelectTrigger>
                        <SelectContent>
                          {availableOriginDepartments.map(([deptName, deptInfo]) => (
                            <SelectItem key={deptName} value={deptName}>
                              🏛️ {deptName}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Origin Chef-lieu Selection */}
                    <div>
                      <Label>3️⃣ Chef-lieu de départ</Label>
                      <Select 
                        onValueChange={(value) => {
                          setSearchForm({...searchForm, origin: value});
                          if (searchForm.destination) {
                            const pricing = getRoutePricing(value, searchForm.destination);
                            setRoutePricing(pricing);
                          }
                        }}
                        disabled={!selectedOriginDepartment}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder={selectedOriginDepartment ? "Chef-lieu automatique" : "Choisissez d'abord un département"} />
                        </SelectTrigger>
                        <SelectContent>
                          {availableOriginCities.map((city) => (
                            <SelectItem key={city.name} value={city.name}>
                              <div className="flex items-center gap-2">
                                🏛️ {city.name} (Chef-lieu {city.department})
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {selectedOriginDepartment && availableOriginCities.length > 0 && (
                        <p className="text-xs text-green-600 mt-1">
                          ✅ Chef-lieu: {availableOriginCities[0]?.name}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Label className="text-lg font-bold text-red-700">🎯 Destination</Label>
                    
                    {/* Destination Region Selection */}
                    <div>
                      <Label>1️⃣ Région d'arrivée</Label>
                      <Select onValueChange={handleDestinationRegionChange}>
                        <SelectTrigger>
                          <SelectValue placeholder="Choisissez la région d'arrivée" />
                        </SelectTrigger>
                        <SelectContent>
                          {getAvailableRegions().map((region) => (
                            <SelectItem key={region} value={region}>
                              🗺️ {region}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Destination Department Selection */}
                    <div>
                      <Label>2️⃣ Département d'arrivée</Label>
                      <Select 
                        onValueChange={handleDestinationDepartmentChange}
                        disabled={!selectedDestinationRegion}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder={selectedDestinationRegion ? "Choisissez le département" : "Sélectionnez d'abord une région"} />
                        </SelectTrigger>
                        <SelectContent>
                          {availableDestinationDepartments.map(([deptName, deptInfo]) => (
                            <SelectItem key={deptName} value={deptName}>
                              🏛️ {deptName}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Destination Chef-lieu Selection */}
                    <div>
                      <Label>3️⃣ Chef-lieu d'arrivée</Label>
                      <Select 
                        onValueChange={(value) => {
                          setSearchForm({...searchForm, destination: value});
                          if (searchForm.origin) {
                            const pricing = getRoutePricing(searchForm.origin, value);
                            setRoutePricing(pricing);
                          }
                        }}
                        disabled={!selectedDestinationDepartment}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder={selectedDestinationDepartment ? "Chef-lieu automatique" : "Choisissez d'abord un département"} />
                        </SelectTrigger>
                        <SelectContent>
                          {availableDestinationCities.map((city) => (
                            <SelectItem key={city.name} value={city.name}>
                              <div className="flex items-center gap-2">
                                🏛️ {city.name} (Chef-lieu {city.department})
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {selectedDestinationDepartment && availableDestinationCities.length > 0 && (
                        <p className="text-xs text-green-600 mt-1">
                          ✅ Chef-lieu: {availableDestinationCities[0]?.name}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Real-time Pricing Display */}
                {routePricing.length > 0 && (
                  <Card className="border-2 border-green-200 bg-green-50">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-green-700">
                        <Bus className="w-5 h-5" />
                        Transporteurs Disponibles pour {searchForm.origin} → {searchForm.destination}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {routePricing.map((agency, idx) => (
                          <Card key={idx} className="hover:shadow-lg transition-all border border-gray-200">
                            <CardContent className="p-4">
                              <div className="flex justify-between items-start mb-2">
                                <h4 className="font-bold text-sm">{agency.name}</h4>
                                <Badge variant="outline" className="text-xs">
                                  {agency.rating}⭐
                                </Badge>
                              </div>
                              <div className="space-y-1 text-xs">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Prix:</span>
                                  <span className="font-bold text-green-600">{formatPrice(agency.price)} FCFA</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Sièges:</span>
                                  <span className="text-orange-600">{agency.available_seats} disponibles</span>
                                </div>
                                <div className="text-gray-600">
                                  <span>Horaires: </span>
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {agency.departure_times.slice(0, 3).map((time, timeIdx) => (
                                      <Badge key={timeIdx} variant="secondary" className="text-xs px-1 py-0">
                                        {time}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              </div>
                              <Button 
                                size="sm" 
                                className="w-full mt-3 bg-green-600 hover:bg-green-700"
                                onClick={() => setSelectedAgency(agency.name)}
                              >
                                Sélectionner
                              </Button>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Agency Selection and Passenger Count */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      🏢 Agence de Transport
                    </label>
                    <select 
                      value={selectedAgency}
                      onChange={(e) => setSelectedAgency(e.target.value)}
                      className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    >
                      <option value="">Sélectionnez une agence (optionnel)</option>
                      {agencies.map((agency, idx) => (
                        <option key={idx} value={agency.name}>
                          {agency.name} - {agency.region} ({agency.rating}⭐)
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      👤 Nombre de passagers
                    </label>
                    <div className="flex items-center gap-3">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setSearchForm(prev => ({
                          ...prev,
                          passengers: Math.max(1, prev.passengers - 1)
                        }))}
                      >
                        <MinusCircle className="w-4 h-4" />
                      </Button>
                      <span className="text-lg font-bold text-green-600 min-w-[3rem] text-center">
                        {searchForm.passengers}
                      </span>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setSearchForm(prev => ({
                          ...prev,
                          passengers: Math.min(50, prev.passengers + 1)
                        }))}
                      >
                        <PlusCircle className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Date and Time Selection */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Date de départ</Label>
                    <Input
                      type="date"
                      value={searchForm.departure_date}
                      onChange={(e) => setSearchForm({...searchForm, departure_date: e.target.value})}
                      min={new Date().toISOString().split('T')[0]}
                    />
                  </div>
                  
                  <div>
                    <Label>Heure de départ (précise)</Label>
                    <Input
                      type="time"
                      value={searchForm.departure_time}
                      onChange={(e) => setSearchForm({...searchForm, departure_time: e.target.value})}
                    />
                  </div>
                </div>

                {/* Additional Information */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    ℹ️ Informations additionnelles (optionnel)
                  </label>
                  <textarea
                    value={searchForm.additional_info || ''}
                    onChange={(e) => setSearchForm({...searchForm, additional_info: e.target.value})}
                    className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                    rows="3"
                    placeholder="Ajoutez des informations spécifiques : besoins spéciaux, préférences de siège, bagages supplémentaires, etc."
                  />
                </div>

                {/* Pickup Location */}
                <div>
                  <Label>Point de prise en charge (via Maps)</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                    <Input
                      placeholder="Adresse de prise en charge"
                      value={searchForm.pickup_location.address}
                      onChange={(e) => setSearchForm({
                        ...searchForm,
                        pickup_location: { ...searchForm.pickup_location, address: e.target.value }
                      })}
                    />
                    <Button variant="outline" className="flex items-center gap-2">
                      <Locate className="w-4 h-4" />
                      Sélectionner sur la carte
                    </Button>
                  </div>
                </div>

                {/* Payment Calculator */}
                <Card className="bg-yellow-50 border-yellow-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-semibold flex items-center gap-2">
                        <Calculator className="w-4 h-4" />
                        Calculatrice de prix
                      </h4>
                      <Button onClick={calculatePayment} disabled={loading} size="sm">
                        {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : "Calculer"}
                      </Button>
                    </div>
                    
                    {calculator.visible && (
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Prix par personne:</span>
                          <span className="font-semibold">{formatPrice(calculator.base_price_per_person || 5000)} FCFA</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Nombre de passagers:</span>
                          <span className="font-semibold">{calculator.passenger_count}</span>
                        </div>
                        <div className="flex justify-between text-lg font-bold border-t pt-2">
                          <span>Total:</span>
                          <span className="text-green-600">{formatPrice(calculator.total_amount)} FCFA</span>
                        </div>
                        <div className="bg-blue-50 p-2 rounded text-xs">
                          <div className="flex justify-between">
                            <span>Réservation (maintenant):</span>
                            <span className="font-semibold">{formatPrice(calculator.reservation_fee)} FCFA</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Solde (sur place):</span>
                            <span className="font-semibold">{formatPrice(calculator.remaining_amount)} FCFA</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Enhanced Payment Selection */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Mode de paiement</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      
                      {/* Reservation Option */}
                      <Card 
                        className={`cursor-pointer transition-all ${
                          paymentForm.type === "reservation" ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:shadow-md'
                        }`}
                        onClick={() => setPaymentForm({...paymentForm, type: "reservation"})}
                      >
                        <CardContent className="p-4 text-center">
                          <Timer className="w-8 h-8 text-blue-600 mx-auto mb-3" />
                          <h4 className="font-semibold">Réservation</h4>
                          <p className="text-sm text-gray-600 mb-2">500 FCFA maintenant</p>
                          <p className="text-xs text-gray-500">Solde 1h avant le voyage</p>
                        </CardContent>
                      </Card>

                      {/* Mobile Money Options */}
                      <Card 
                        className={`cursor-pointer transition-all ${
                          paymentForm.type === "mobile_money" ? 'ring-2 ring-green-500 bg-green-50' : 'hover:shadow-md'
                        }`}
                        onClick={() => setPaymentForm({...paymentForm, type: "mobile_money"})}
                      >
                        <CardContent className="p-4 text-center">
                          <Smartphone className="w-8 h-8 text-green-600 mx-auto mb-3" />
                          <h4 className="font-semibold">Mobile Money</h4>
                          <div className="flex justify-center gap-2 mt-2">
                            <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                              <span className="text-white font-bold text-xs">MTN</span>
                            </div>
                            <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                              <span className="text-white font-bold text-xs">OM</span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    {/* Mobile Money Provider Selection */}
                    {paymentForm.type === "mobile_money" && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                        <Card 
                          className={`cursor-pointer transition-all ${
                            paymentForm.provider === "MTN" ? 'ring-2 ring-yellow-500 bg-yellow-50' : 'hover:shadow-md'
                          }`}
                          onClick={() => setPaymentForm({...paymentForm, provider: "MTN"})}
                        >
                          <CardContent className="p-4 text-center">
                            <div className="w-16 h-16 bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center mx-auto mb-3 shadow-lg">
                              <span className="text-white font-bold text-lg">MTN</span>
                            </div>
                            <h4 className="font-semibold text-yellow-700">MTN Mobile Money</h4>
                            <p className="text-xs text-gray-600 mt-1">Code USSD: *126#</p>
                            <div className="text-xs text-yellow-600 mt-2 font-semibold">
                              🇨🇲 MTN Cameroun
                            </div>
                          </CardContent>
                        </Card>

                        <Card 
                          className={`cursor-pointer transition-all ${
                            paymentForm.provider === "ORANGE" ? 'ring-2 ring-orange-500 bg-orange-50' : 'hover:shadow-md'
                          }`}
                          onClick={() => setPaymentForm({...paymentForm, provider: "ORANGE"})}
                        >
                          <CardContent className="p-4 text-center">
                            <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-3 shadow-lg">
                              <span className="text-white font-bold text-sm">ORANGE</span>
                            </div>
                            <h4 className="font-semibold text-orange-700">Orange Money</h4>
                            <p className="text-xs text-gray-600 mt-1">Code USSD: #150#</p>
                            <div className="text-xs text-orange-600 mt-2 font-semibold">
                              🇨🇲 Orange Cameroun
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    )}

                    {/* Paiement sur place en option secondaire */}
                    {paymentForm.type === "on_site" && (
                      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200">
                        <CardContent className="p-4">
                          <h4 className="font-semibold text-blue-700 mb-2">Instructions de paiement sur place</h4>
                          <div className="space-y-2 text-sm">
                            <p className="flex items-center gap-2">
                              <CheckCircle className="w-4 h-4 text-green-600" />
                              Réservation: {formatPrice(searchForm.passengers * 500)} FCFA (maintenant)
                            </p>
                            <p className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-orange-600" />
                              Solde: {formatPrice(searchForm.passengers * 4500)} FCFA (au départ)
                            </p>
                            <p className="text-xs text-gray-600">
                              💳 Modes acceptés sur place: Espèces, Mobile Money MTN/Orange, Cartes bancaires
                            </p>
                            <div className="mt-2 p-2 bg-blue-50 rounded text-xs">
                              <div className="font-semibold text-blue-700">Détail du calcul:</div>
                              <div className="flex justify-between">
                                <span>500 FCFA × {searchForm.passengers} passager(s):</span>
                                <span className="font-bold">{formatPrice(searchForm.passengers * 500)} FCFA</span>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Account Credit and Voucher Options */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Card 
                        className={`cursor-pointer transition-all ${
                          paymentForm.type === "account_credit" ? 'ring-2 ring-purple-500 bg-purple-50' : 'hover:shadow-md'
                        }`}
                        onClick={() => setPaymentForm({...paymentForm, type: "account_credit"})}
                      >
                        <CardContent className="p-4 text-center">
                          <PaymentCard className="w-8 h-8 text-purple-600 mx-auto mb-3" />
                          <h4 className="font-semibold">Crédit Compte</h4>
                          <p className="text-sm text-gray-600">Solde disponible</p>
                        </CardContent>
                      </Card>

                      <Card 
                        className={`cursor-pointer transition-all ${
                          paymentForm.type === "voucher" ? 'ring-2 ring-pink-500 bg-pink-50' : 'hover:shadow-md'
                        }`}
                        onClick={() => setPaymentForm({...paymentForm, type: "voucher"})}
                      >
                        <CardContent className="p-4 text-center">
                          <Receipt className="w-8 h-8 text-pink-600 mx-auto mb-3" />
                          <h4 className="font-semibold">Bon de Réduction</h4>
                          <p className="text-sm text-gray-600">Code promo</p>
                        </CardContent>
                      </Card>
                    </div>

                    {/* Voucher Code Input */}
                    {paymentForm.type === "voucher" && (
                      <div className="mt-4">
                        <Label htmlFor="voucher-code">Code de réduction</Label>
                        <Input
                          id="voucher-code"
                          placeholder="Saisissez votre code"
                          value={paymentForm.voucher_code}
                          onChange={(e) => setPaymentForm({...paymentForm, voucher_code: e.target.value})}
                        />
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Action Buttons */}
                <div className="flex gap-4">
                  <Button 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => {
                      setSearchForm({
                        origin: "", destination: "", departure_date: "", departure_time: "",
                        passengers: 1, custom_passenger_count: null, service_class: "economy",
                        pickup_location: { address: "", coordinates: { lat: 0, lng: 0 } },
                        dropoff_location: { address: "", coordinates: { lat: 0, lng: 0 } },
                        additional_info: ""
                      });
                      setCalculator({ visible: false, base_price: 0, total_amount: 0, reservation_fee: 500, remaining_amount: 0 });
                    }}
                  >
                    Effacer
                  </Button>
                  <Button 
                    onClick={createBooking}
                    disabled={loading || !searchForm.origin || !searchForm.destination}
                    className="flex-1 bg-gradient-to-r from-green-500 to-red-500 hover:from-green-600 hover:to-red-600"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <CheckCircle className="w-4 h-4 mr-2" />}
                    Confirmer la réservation
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Courier Service Tab */}
          <TabsContent value="courier" className="space-y-6">
            <Card className="shadow-2xl">
              <CardHeader className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white">
                <CardTitle className="flex items-center gap-2">
                  <Package2 className="w-5 h-5" />
                  Service Courrier Inter-villes
                </CardTitle>
                <CardDescription className="text-yellow-100">
                  Transport sécurisé de colis et documents
                </CardDescription>
              </CardHeader>
              <CardContent className="p-8 space-y-6">
                
                {/* Recipient Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="recipient-name">Nom du destinataire *</Label>
                    <Input
                      id="recipient-name"
                      placeholder="Nom complet"
                      value={courierForm.recipient_name}
                      onChange={(e) => setCourierForm({...courierForm, recipient_name: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="recipient-phone">Téléphone du destinataire *</Label>
                    <Input
                      id="recipient-phone"
                      placeholder="+237 6XX XXX XXX"
                      value={courierForm.recipient_phone}
                      onChange={(e) => setCourierForm({...courierForm, recipient_phone: e.target.value})}
                    />
                  </div>
                </div>

                {/* 3-Level Courier Route Selection */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <Label className="text-sm font-bold text-yellow-700">📦 Expédition</Label>
                    
                    <div>
                      <Label className="text-xs">Région d'expédition</Label>
                      <Select onValueChange={(region) => {
                        const departments = administrativeStructure[region]?.departments || {};
                        // Store courier origin region departments for selection
                        setCourierForm({...courierForm, origin_region: region, origin_department: "", origin: ""});
                      }}>
                        <SelectTrigger className="h-10">
                          <SelectValue placeholder="Région" />
                        </SelectTrigger>
                        <SelectContent>
                          {getAvailableRegions().map((region) => (
                            <SelectItem key={region} value={region}>
                              🗺️ {region}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label className="text-xs">Département d'expédition</Label>
                      <Select 
                        onValueChange={(dept) => setCourierForm({...courierForm, origin_department: dept, origin: ""})}
                        disabled={!courierForm.origin_region}
                      >
                        <SelectTrigger className="h-10">
                          <SelectValue placeholder="Département" />
                        </SelectTrigger>
                        <SelectContent>
                          {courierForm.origin_region && Object.entries(administrativeStructure[courierForm.origin_region]?.departments || {}).map(([deptName]) => (
                            <SelectItem key={deptName} value={deptName}>
                              🏛️ {deptName}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label className="text-xs">Chef-lieu d'expédition</Label>
                      <Select 
                        onValueChange={(value) => setCourierForm({...courierForm, origin: value})}
                        disabled={!courierForm.origin_department}
                      >
                        <SelectTrigger className="h-10">
                          <SelectValue placeholder="Chef-lieu" />
                        </SelectTrigger>
                        <SelectContent>
                          {courierForm.origin_department && (
                            <SelectItem value={administrativeStructure[courierForm.origin_region]?.departments[courierForm.origin_department]?.chef_lieu}>
                              🏛️ {administrativeStructure[courierForm.origin_region]?.departments[courierForm.origin_department]?.chef_lieu}
                            </SelectItem>
                          )}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <Label className="text-sm font-bold text-orange-700">🎯 Destination</Label>
                    
                    <div>
                      <Label className="text-xs">Région de destination</Label>
                      <Select onValueChange={(region) => {
                        setCourierForm({...courierForm, dest_region: region, dest_department: "", destination: ""});
                      }}>
                        <SelectTrigger className="h-10">
                          <SelectValue placeholder="Région" />
                        </SelectTrigger>
                        <SelectContent>
                          {getAvailableRegions().map((region) => (
                            <SelectItem key={region} value={region}>
                              🗺️ {region}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label className="text-xs">Département de destination</Label>
                      <Select 
                        onValueChange={(dept) => setCourierForm({...courierForm, dest_department: dept, destination: ""})}
                        disabled={!courierForm.dest_region}
                      >
                        <SelectTrigger className="h-10">
                          <SelectValue placeholder="Département" />
                        </SelectTrigger>
                        <SelectContent>
                          {courierForm.dest_region && Object.entries(administrativeStructure[courierForm.dest_region]?.departments || {}).map(([deptName]) => (
                            <SelectItem key={deptName} value={deptName}>
                              🏛️ {deptName}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label className="text-xs">Chef-lieu de destination</Label>
                      <Select 
                        onValueChange={(value) => setCourierForm({...courierForm, destination: value})}
                        disabled={!courierForm.dest_department}
                      >
                        <SelectTrigger className="h-10">
                          <SelectValue placeholder="Chef-lieu" />
                        </SelectTrigger>
                        <SelectContent>
                          {courierForm.dest_department && (
                            <SelectItem value={administrativeStructure[courierForm.dest_region]?.departments[courierForm.dest_department]?.chef_lieu}>
                              🏛️ {administrativeStructure[courierForm.dest_region]?.departments[courierForm.dest_department]?.chef_lieu}
                            </SelectItem>
                          )}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>

                {/* Package Details */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label>Type de colis</Label>
                    <Select 
                      value={courierForm.package_type}
                      onValueChange={(value) => setCourierForm({...courierForm, package_type: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="documents">Documents</SelectItem>
                        <SelectItem value="clothes">Vêtements</SelectItem>
                        <SelectItem value="electronics">Électronique</SelectItem>
                        <SelectItem value="food">Produits alimentaires</SelectItem>
                        <SelectItem value="other">Autre</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="weight">Poids (kg)</Label>
                    <Input
                      id="weight"
                      type="number"
                      min="0.1"
                      max="50"
                      step="0.1"
                      value={courierForm.weight_kg}
                      onChange={(e) => setCourierForm({...courierForm, weight_kg: parseFloat(e.target.value)})}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="declared-value">Valeur déclarée (FCFA)</Label>
                    <Input
                      id="declared-value"
                      type="number"
                      min="1000"
                      value={courierForm.declared_value}
                      onChange={(e) => setCourierForm({...courierForm, declared_value: parseInt(e.target.value)})}
                    />
                  </div>
                </div>

                {/* Carrier Selection */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    🚚 Transporteur de colis
                  </label>
                  <select 
                    value={selectedCarrier}
                    onChange={(e) => setSelectedCarrier(e.target.value)}
                    className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option value="">Sélectionnez un transporteur</option>
                    {courierCarriers.map((carrier, idx) => (
                      <option key={idx} value={carrier.name}>
                        {carrier.name} - {carrier.vehicle_type} ({carrier.rating}⭐)
                      </option>
                    ))}
                  </select>
                  <p className="text-sm text-gray-600 mt-1">
                    Choisissez votre transporteur selon le type de véhicule et la zone de couverture
                  </p>
                </div>

                {/* Addresses */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="pickup-address">Adresse de collecte</Label>
                    <Textarea
                      id="pickup-address"
                      placeholder="Adresse complète de collecte"
                      value={courierForm.pickup_address}
                      onChange={(e) => setCourierForm({...courierForm, pickup_address: e.target.value})}
                      rows={3}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="delivery-address">Adresse de livraison</Label>
                    <Textarea
                      id="delivery-address"
                      placeholder="Adresse complète de livraison"
                      value={courierForm.delivery_address}
                      onChange={(e) => setCourierForm({...courierForm, delivery_address: e.target.value})}
                      rows={3}
                    />
                  </div>
                </div>

                {/* Service Options */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="urgent"
                      checked={courierForm.urgent}
                      onCheckedChange={(checked) => setCourierForm({...courierForm, urgent: checked})}
                    />
                    <Label htmlFor="urgent" className="text-sm">
                      Livraison urgente (+50%)
                    </Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="insurance"
                      checked={courierForm.insurance}
                      onCheckedChange={(checked) => setCourierForm({...courierForm, insurance: checked})}
                    />
                    <Label htmlFor="insurance" className="text-sm">
                      Assurance colis (2%)
                    </Label>
                  </div>

                  <div>
                    <Label htmlFor="pickup-time">Heure de collecte</Label>
                    <Input
                      id="pickup-time"
                      type="time"
                      value={courierForm.pickup_time}
                      onChange={(e) => setCourierForm({...courierForm, pickup_time: e.target.value})}
                    />
                  </div>
                </div>

                {/* Special Instructions */}
                <div>
                  <Label htmlFor="delivery-instructions">Instructions de livraison</Label>
                  <Textarea
                    id="delivery-instructions"
                    placeholder="Instructions spéciales pour la livraison..."
                    value={courierForm.delivery_instructions}
                    onChange={(e) => setCourierForm({...courierForm, delivery_instructions: e.target.value})}
                    rows={2}
                  />
                </div>

                {/* Action Button */}
                <Button 
                  onClick={bookCourierService}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 py-3"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Send className="w-4 h-4 mr-2" />}
                  Réserver le service courrier
                </Button>
              </CardContent>
            </Card>

            {/* Courier Services History */}
            {courierServices.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Mes envois</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {courierServices.map((service, idx) => (
                      <Card key={idx} className="border-l-4 border-l-orange-500">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-bold">Code: {service.tracking_number}</div>
                              <div className="text-sm text-gray-600">
                                {service.origin} → {service.destination}
                              </div>
                              <div className="text-sm text-gray-600">
                                Destinataire: {service.recipient_name}
                              </div>
                            </div>
                            <Badge className="bg-orange-100 text-orange-800">
                              {service.status}
                            </Badge>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* GPS Tracking Tab */}
          <TabsContent value="tracking" className="space-y-6">
            <Card className="shadow-2xl">
              <CardHeader className="bg-gradient-to-r from-red-500 to-pink-500 text-white">
                <CardTitle className="flex items-center gap-2">
                  <Map className="w-5 h-5" />
                  Suivi GPS en Temps Réel
                </CardTitle>
                <CardDescription className="text-red-100">
                  Localisation des véhicules sur les routes du Cameroun
                </CardDescription>
              </CardHeader>
              <CardContent className="p-8 space-y-6">
                
                <div className="flex gap-4 mb-6">
                  <Button 
                    onClick={() => trackVehicles("route_001")}
                    className="bg-gradient-to-r from-red-500 to-pink-500"
                  >
                    <Navigation2 className="w-4 h-4 mr-2" />
                    Actualiser positions
                  </Button>
                  
                  <Button variant="outline">
                    <Eye className="w-4 h-4 mr-2" />
                    Voir carte complète
                  </Button>
                </div>

                {/* Map Placeholder */}
                <Card className="h-64 bg-gray-100 border-2 border-dashed border-gray-300">
                  <CardContent className="h-full flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <Map className="w-16 h-16 mx-auto mb-4" />
                      <p className="font-semibold">Carte GPS Interactive</p>
                      <p className="text-sm">Suivi des véhicules en temps réel</p>
                    </div>
                  </CardContent>
                </Card>

                {/* Vehicle List */}
                {trackingData.vehicles && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Véhicules actifs ({trackingData.vehicles.length})</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {trackingData.vehicles.map((vehicle) => (
                          <Card 
                            key={vehicle.vehicle_id} 
                            className={`cursor-pointer transition-all ${
                              selectedVehicle === vehicle.vehicle_id ? 'ring-2 ring-red-500 bg-red-50' : 'hover:shadow-md'
                            }`}
                            onClick={() => setSelectedVehicle(vehicle.vehicle_id)}
                          >
                            <CardContent className="p-4">
                              <div className="flex items-center gap-3 mb-3">
                                <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                                  <Bus className="w-5 h-5 text-red-600" />
                                </div>
                                <div>
                                  <div className="font-semibold">{vehicle.vehicle_id}</div>
                                  <div className="text-xs text-gray-600">
                                    {vehicle.occupancy}/45 passagers
                                  </div>
                                </div>
                              </div>
                              
                              <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                  <span>Prochain arrêt:</span>
                                  <span className="font-semibold">{vehicle.next_stop}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>ETA:</span>
                                  <span className="font-semibold text-green-600">{vehicle.eta}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Vitesse:</span>
                                  <span className="font-semibold">
                                    {vehicle.location.speed_kmh.toFixed(0)} km/h
                                  </span>
                                </div>
                              </div>

                              <Progress 
                                value={(vehicle.occupancy / 45) * 100} 
                                className="mt-3" 
                              />
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tourism Tab with Auto-rotating Carousel */}
          <TabsContent value="tourism" className="space-y-6">
            
            {/* Hero Carousel Section */}
            {attractions.length > 0 && (
              <Card className="overflow-hidden">
                <div className="h-96 relative">
                  <img 
                    src={attractions[currentTourismSlide]?.image_url}
                    alt={attractions[currentTourismSlide]?.name}
                    className="w-full h-full object-cover transition-all duration-1000"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
                  
                  {/* Site Information Overlay */}
                  <div className="absolute bottom-6 left-6 text-white">
                    <h2 className="text-3xl font-bold mb-2">
                      {attractions[currentTourismSlide]?.name}
                    </h2>
                    <div className="flex items-center gap-2 mb-3">
                      <MapPin className="w-4 h-4" />
                      <span className="text-lg">{attractions[currentTourismSlide]?.city}, {attractions[currentTourismSlide]?.region}</span>
                    </div>
                    <p className="text-lg max-w-2xl">
                      {attractions[currentTourismSlide]?.description}
                    </p>
                  </div>
                  
                  {/* Progress Indicators */}
                  <div className="absolute bottom-6 right-6 flex gap-2">
                    {attractions.map((_, idx) => (
                      <div
                        key={idx}
                        className={`w-2 h-2 rounded-full transition-all ${
                          idx === currentTourismSlide ? 'bg-white' : 'bg-white/50'
                        }`}
                      />
                    ))}
                  </div>
                  
                  {/* Navigation Arrows */}
                  <button
                    onClick={() => setCurrentTourismSlide((prev) => 
                      prev === 0 ? attractions.length - 1 : prev - 1
                    )}
                    className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition-all"
                  >
                    ←
                  </button>
                  <button
                    onClick={() => setCurrentTourismSlide((prev) => 
                      (prev + 1) % attractions.length
                    )}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition-all"
                  >
                    →
                  </button>
                </div>
              </Card>
            )}

            {/* Traditional Grid View */}
            <Card>
              <CardHeader className="bg-gradient-to-r from-green-600 via-yellow-500 to-red-600 text-white">
                <CardTitle className="flex items-center gap-2">
                  <Mountain className="w-5 h-5" />
                  Tous les Sites Touristiques du Cameroun
                </CardTitle>
                <CardDescription className="text-green-100">
                  Découvrez la richesse touristique de toutes les régions
                </CardDescription>
              </CardHeader>
              <CardContent className="p-8">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {attractions.map((attraction, idx) => (
                    <Card 
                      key={idx} 
                      className={`overflow-hidden hover:shadow-xl transition-all cursor-pointer ${
                        idx === currentTourismSlide ? 'ring-2 ring-green-500' : ''
                      }`}
                      onClick={() => setCurrentTourismSlide(idx)}
                    >
                      <div className="h-48 relative">
                        <img 
                          src={attraction.image_url}
                          alt={attraction.name}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute top-3 right-3">
                          <Badge className="bg-black/70 text-white">
                            <Star className="w-3 h-3 mr-1" />
                            {attraction.rating}
                          </Badge>
                        </div>
                        <div className="absolute bottom-3 left-3">
                          <Badge className="bg-green-600 text-white">
                            {attraction.category}
                          </Badge>
                        </div>
                        
                        {/* Site Name Overlay */}
                        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                          <h4 className="text-white font-bold text-sm">{attraction.name}</h4>
                        </div>
                      </div>
                      <CardContent className="p-4">
                        <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                          <MapPin className="w-4 h-4" />
                          {attraction.city}, {attraction.region}
                        </div>
                        <p className="text-gray-600 text-xs line-clamp-2">
                          {attraction.description}
                        </p>
                        <div className="flex gap-2 mt-3">
                          <Button size="sm" className="flex-1 bg-gradient-to-r from-green-500 to-red-500 text-xs">
                            <Navigation className="w-3 h-3 mr-1" />
                            Itinéraire
                          </Button>
                          <Button variant="outline" size="sm">
                            <Share2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Profile Tab with Wallet */}
          <TabsContent value="profile" className="space-y-6">
            {/* Profile Sub-navigation */}
            <div className="flex gap-2 mb-6">
              <Button 
                variant={showWallet ? "outline" : "default"}
                onClick={() => setShowWallet(false)}
                className="flex items-center gap-2"
              >
                <User className="w-4 h-4" />
                Mon Profil
              </Button>
              <Button 
                variant={showWallet ? "default" : "outline"}
                onClick={() => setShowWallet(true)}
                className="flex items-center gap-2"
              >
                <CreditCard className="w-4 h-4" />
                Portefeuille
              </Button>
            </div>

            {!showWallet ? (
              /* Profile Content */
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="w-5 h-5" />
                      Mon Profil Connect237
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex items-center gap-4">
                      <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-red-500 rounded-full flex items-center justify-center text-white font-bold text-2xl">
                        JD
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold">{user.name}</h3>
                        <p className="text-gray-600">Membre depuis 2024</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge className="bg-green-100 text-green-800">
                            Client vérifié
                          </Badge>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <Card className="text-center p-4 bg-green-50">
                        <div className="text-2xl font-bold text-green-600">{bookings.length}</div>
                        <div className="text-sm text-gray-600">Voyages</div>
                      </Card>
                      
                      <Card className="text-center p-4 bg-yellow-50">
                        <div className="text-2xl font-bold text-yellow-600">{courierServices.length}</div>
                        <div className="text-sm text-gray-600">Colis envoyés</div>
                      </Card>
                      
                      <Card className="text-center p-4 bg-red-50">
                        <div className="text-2xl font-bold text-red-600">2,500</div>
                        <div className="text-sm text-gray-600">Points fidélité</div>
                      </Card>

                      <Card className="text-center p-4 bg-blue-50">
                        <div className="text-2xl font-bold text-blue-600">4.8</div>
                        <div className="text-sm text-gray-600">Note moyenne</div>
                      </Card>
                    </div>

                <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
                  <CardContent className="p-6">
                    <div className="text-center mb-4">
                      <Building className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                      <h4 className="font-bold text-lg text-blue-800">Services Professionnels</h4>
                      <p className="text-gray-600 text-sm">
                        Rejoignez Connect237 en tant que transporteur ou agence
                      </p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <Card className="text-center p-3 border border-blue-200">
                        <User className="w-6 h-6 text-green-600 mx-auto mb-2" />
                        <div className="text-sm font-semibold">Client</div>
                        <div className="text-xs text-gray-600">Voyageur régulier</div>
                      </Card>
                      
                      <Card className="text-center p-3 border border-blue-200">
                        <Building className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
                        <div className="text-sm font-semibold">Agence</div>
                        <div className="text-xs text-gray-600">Entreprise de transport</div>
                      </Card>
                      
                      <Card className="text-center p-3 border border-blue-200">
                        <Truck className="w-6 h-6 text-red-600 mx-auto mb-2" />
                        <div className="text-sm font-semibold">Transporteur</div>
                        <div className="text-xs text-gray-600">Conducteur indépendant</div>
                      </Card>
                    </div>
                    
                    <Button 
                      onClick={() => setShowRegistration(true)}
                      className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600"
                    >
                      <Users className="w-4 h-4 mr-2" />
                      Inscription Professionnelle
                    </Button>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-r from-green-50 to-red-50 border-0">
                  <CardContent className="p-6 text-center">
                    <Connect237Logo size="small" />
                    <h4 className="font-bold text-lg mt-4 mb-2">Merci de faire confiance à Connect237 !</h4>
                    <p className="text-gray-600">
                      Ensemble, nous connectons le Cameroun 🇨🇲
                    </p>
                  </CardContent>
                </Card>
              </CardContent>
            </Card>
            </>
            ) : (
            /* Wallet Content */
            <>
              <Card>
                <CardHeader className="bg-gradient-to-r from-green-500 to-yellow-500 text-white">
                  <CardTitle className="flex items-center gap-2">
                    <CreditCard className="w-5 h-5" />
                    Mon Portefeuille Connect237
                  </CardTitle>
                  <CardDescription className="text-green-100">
                    Gérez vos paiements et réservations
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6 p-6">
                  
                  {/* Wallet Balance */}
                  <Card className="bg-gradient-to-r from-green-600 to-red-600 text-white">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-center">
                        <div>
                          <h3 className="text-2xl font-bold">Solde disponible</h3>
                          <p className="text-4xl font-bold mt-2">12,500 FCFA</p>
                          <p className="text-green-100 text-sm mt-1">Dernière mise à jour: aujourd'hui</p>
                        </div>
                        <div className="text-6xl opacity-20">
                          💳
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Quick Actions */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Button className="flex items-center gap-2 h-16 bg-green-600 hover:bg-green-700">
                      <Plus className="w-5 h-5" />
                      Recharger
                    </Button>
                    <Button variant="outline" className="flex items-center gap-2 h-16">
                      <Send className="w-5 h-5" />
                      Transférer
                    </Button>
                    <Button variant="outline" className="flex items-center gap-2 h-16">
                      <Download className="w-5 h-5" />
                      Historique
                    </Button>
                  </div>

                  {/* Payment Methods */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <PaymentCard className="w-5 h-5" />
                        Modes de paiement
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center text-white font-bold">
                              MTN
                            </div>
                            <div>
                              <p className="font-semibold">MTN Mobile Money</p>
                              <p className="text-sm text-gray-600">+237 6XX XXX XXX</p>
                            </div>
                          </div>
                          <Badge className="bg-green-100 text-green-800">Vérifié</Badge>
                        </div>

                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-orange-600 rounded-lg flex items-center justify-center text-white font-bold">
                              OM
                            </div>
                            <div>
                              <p className="font-semibold">Orange Money</p>
                              <p className="text-sm text-gray-600">+237 6XX XXX XXX</p>
                            </div>
                          </div>
                          <Badge variant="outline">Non vérifié</Badge>
                        </div>

                        <Button variant="outline" className="w-full flex items-center gap-2">
                          <Plus className="w-4 h-4" />
                          Ajouter un mode de paiement
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Recent Transactions */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Receipt className="w-5 h-5" />
                        Transactions récentes
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 border-b">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                              <Minus className="w-4 h-4 text-red-600" />
                            </div>
                            <div>
                              <p className="font-semibold">Réservation Yaoundé-Douala</p>
                              <p className="text-sm text-gray-600">Aujourd'hui, 14:30</p>
                            </div>
                          </div>
                          <span className="text-red-600 font-bold">-500 FCFA</span>
                        </div>

                        <div className="flex items-center justify-between p-3 border-b">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                              <Plus className="w-4 h-4 text-green-600" />
                            </div>
                            <div>
                              <p className="font-semibold">Rechargement portefeuille</p>
                              <p className="text-sm text-gray-600">Hier, 09:15</p>
                            </div>
                          </div>
                          <span className="text-green-600 font-bold">+10,000 FCFA</span>
                        </div>

                        <div className="flex items-center justify-between p-3">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                              <Package className="w-4 h-4 text-orange-600" />
                            </div>
                            <div>
                              <p className="font-semibold">Envoi colis Douala-Bafoussam</p>
                              <p className="text-sm text-gray-600">Il y a 2 jours</p>
                            </div>
                          </div>
                          <span className="text-red-600 font-bold">-3,000 FCFA</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </CardContent>
              </Card>
            </>
            )}
          </TabsContent>
        </Tabs>

        {/* Registration System Modal */}
        {showRegistration && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-800">Inscription Connect237</h2>
                  <Button 
                    variant="ghost" 
                    onClick={() => setShowRegistration(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </Button>
                </div>
                <RegistrationSystem />
              </div>
            </div>
          </div>
        )}
      </div>
      
      <Toaster />
    </div>
  );
}

export default Connect237App;