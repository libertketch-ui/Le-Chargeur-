import React, { useState, useEffect, useMemo } from "react";
import "./App.css";
import axios from "axios";
import RegistrationSystem from "./RegistrationSystem";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { Switch } from "./components/ui/switch";
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
  Zap as Lightning,
  Target,
  ArrowRight,
  DollarSign,
  Percent
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [currentView, setCurrentView] = useState("main"); // "main" or "registration"
  const [activeTab, setActiveTab] = useState("home");
  const [cities, setCities] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [popularRoutes, setPopularRoutes] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [mobileMoneyProviders, setMobileMoneyProviders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState({ 
    id: "user123", 
    first_name: "Jean", 
    last_name: "Dupont",
    subscription_type: "standard",
    loyalty_points: 2500,
    phone: "+237650123456",
    email: "jean.dupont@email.com",
    preferred_payment: "mobile_money"
  });

  // Fusion search state (TicketCam + BusConnect advanced)
  const [searchForm, setSearchForm] = useState({
    origin: "",
    destination: "",
    departure_date: "",
    passengers: 1,
    service_class: "economy",
    budget_max: null,
    time_preference: "any"
  });

  // Mobile Money integration state (from TicketCam)
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState("mobile_money");
  const [mobileMoneyForm, setMobileMoneyForm] = useState({
    provider: "OM",
    phone_number: "",
    amount: 0
  });

  // Smart features state
  const [smartSuggestions, setSmartSuggestions] = useState([]);
  const [priceAlerts, setPriceAlerts] = useState([]);
  const [weatherInfo, setWeatherInfo] = useState({});

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      await Promise.all([
        loadCities(),
        loadPopularRoutes(),
        loadMobileMoneyProviders(),
        loadUserBookings(),
        loadNotifications(),
        loadSmartSuggestions()
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

  const loadPopularRoutes = async () => {
    try {
      const response = await axios.get(`${API}/popular-routes`);
      setPopularRoutes(response.data.popular_routes);
    } catch (error) {
      console.error("Error loading popular routes:", error);
    }
  };

  const loadMobileMoneyProviders = async () => {
    try {
      const response = await axios.get(`${API}/mobile-money/providers`);
      setMobileMoneyProviders(response.data.providers);
    } catch (error) {
      console.error("Error loading mobile money providers:", error);
    }
  };

  const loadUserBookings = async () => {
    try {
      // Mock data for now
      setBookings([]);
    } catch (error) {
      console.error("Error loading bookings:", error);
    }
  };

  const loadNotifications = async () => {
    try {
      const response = await axios.get(`${API}/notifications/${user.id}`);
      setNotifications(response.data.notifications);
    } catch (error) {
      console.error("Error loading notifications:", error);
    }
  };

  const loadSmartSuggestions = async () => {
    // Mock smart suggestions based on user behavior
    const suggestions = [
      { 
        route: "Yaoundé → Douala", 
        reason: "Voyage fréquent", 
        price: 4200, 
        originalPrice: 4900,
        savings: 700,
        icon: "heart"
      },
      { 
        route: "Yaoundé → Bafoussam", 
        reason: "Nouvelle destination populaire", 
        price: 5800, 
        originalPrice: 6500,
        savings: 700,
        icon: "trending-up"
      }
    ];
    setSmartSuggestions(suggestions);
  };

  const performSmartSearch = async () => {
    if (!searchForm.origin || !searchForm.destination || !searchForm.departure_date) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }

    setLoading(true);
    try {
      const params = new URLSearchParams({
        origin: searchForm.origin,
        destination: searchForm.destination,
        departure_date: searchForm.departure_date,
        passengers: searchForm.passengers.toString(),
        service_class: searchForm.service_class,
        time_preference: searchForm.time_preference
      });

      if (searchForm.budget_max) {
        params.append('budget_max', searchForm.budget_max.toString());
      }

      const response = await axios.get(`${API}/search/smart?${params}`);
      setRoutes(response.data.routes);
      setActiveTab("results");
      toast.success(`${response.data.total} trajets trouvés avec prix dynamique`);
    } catch (error) {
      console.error("Error searching routes:", error);
      toast.error("Erreur lors de la recherche");
    } finally {
      setLoading(false);
    }
  };

  const selectRouteAndProceedToBooking = (route) => {
    setSearchForm(prev => ({ ...prev, selectedRoute: route }));
    setMobileMoneyForm(prev => ({ ...prev, amount: route.dynamic_price * searchForm.passengers }));
    setActiveTab("booking");
  };

  const createFusionBooking = async () => {
    if (!searchForm.selectedRoute) {
      toast.error("Aucun trajet sélectionné");
      return;
    }

    setLoading(true);
    try {
      const bookingData = {
        user_id: user.id,
        route_id: searchForm.selectedRoute.id,
        service_class: searchForm.service_class,
        passenger_count: searchForm.passengers,
        base_price: searchForm.selectedRoute.dynamic_price,
        payment_method: selectedPaymentMethod,
        mobile_money_provider: selectedPaymentMethod === "mobile_money" ? mobileMoneyForm.provider : null,
        mobile_money_phone: selectedPaymentMethod === "mobile_money" ? mobileMoneyForm.phone_number : null,
        passenger_details: [
          { name: `${user.first_name} ${user.last_name}`, phone: user.phone }
        ]
      };

      const response = await axios.post(`${API}/bookings/fusion`, bookingData);
      toast.success(`Réservation créée ! Référence: ${response.data.booking_reference}`);
      
      // If mobile money, show payment instructions
      if (selectedPaymentMethod === "mobile_money" && response.data.payment_details) {
        toast.info(response.data.payment_details.instructions);
      }
      
      setBookings([...bookings, response.data]);
      setActiveTab("tickets");
    } catch (error) {
      console.error("Error creating booking:", error);
      toast.error("Erreur lors de la réservation");
    } finally {
      setLoading(false);
    }
  };

  const getServiceClassIcon = (className) => {
    switch(className) {
      case 'economy': return <Bus className="w-4 h-4 text-blue-600" />;
      case 'comfort': return <Car className="w-4 h-4 text-green-600" />;
      case 'vip': return <Crown className="w-4 h-4 text-purple-600" />;
      case 'express': return <Lightning className="w-4 h-4 text-yellow-600" />;
      default: return <Bus className="w-4 h-4" />;
    }
  };

  const getServiceClassColor = (className) => {
    switch(className) {
      case 'economy': return 'from-blue-500 to-blue-600';
      case 'comfort': return 'from-green-500 to-green-600';
      case 'vip': return 'from-purple-500 to-purple-600';
      case 'express': return 'from-yellow-500 to-yellow-600';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  const getMobileMoneyIcon = (provider) => {
    switch(provider) {
      case 'OM': return <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold text-xs">OM</div>;
      case 'MOMO': return <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center text-white font-bold text-xs">MTN</div>;
      case 'EUM': return <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-xs">EU</div>;
      default: return <Smartphone className="w-8 h-8" />;
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR').format(price);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-blue-50 to-indigo-100">
      
      {/* Show Registration System or Main App */}
      {currentView === "registration" ? (
        <RegistrationSystem onComplete={() => setCurrentView("main")} />
      ) : (
        <>
        {/* Rest of the main app */}
      <div className="container mx-auto p-4 max-w-7xl">
        
        {/* Fusion Header (TicketCam + BusConnect style) */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="bg-gradient-to-r from-cyan-500 to-blue-600 p-4 rounded-2xl shadow-xl">
              <Bus className="w-10 h-10 text-white" />
            </div>
            <div>
              <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-600 to-blue-700 bg-clip-text text-transparent">
                BusConnect
              </h1>
              <p className="text-xl text-cyan-600 font-semibold tracking-wide">Cameroun</p>
            </div>
            {user.subscription_type === "premium" && (
              <Badge className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-4 py-2">
                <Crown className="w-4 h-4 mr-2" />
                Premium
              </Badge>
            )}
            <Button 
              onClick={() => setCurrentView("registration")}
              className="ml-auto bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
            >
              <User className="w-4 h-4 mr-2" />
              Inscription
            </Button>
          </div>
          
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Réservez vos billets de transport interurbain
            </h2>
            <p className="text-gray-600 text-lg">
              Rapide, sécurisé et pratique avec Mobile Money
            </p>
          </div>

          {/* Key Features (TicketCam style) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all">
              <CardContent className="p-6 text-center">
                <Search className="w-12 h-12 text-cyan-600 mx-auto mb-4" />
                <h3 className="font-bold text-lg mb-2">Recherche intelligente</h3>
                <p className="text-gray-600 text-sm">Prix dynamiques et suggestions IA</p>
              </CardContent>
            </Card>
            
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all">
              <CardContent className="p-6 text-center">
                <Smartphone className="w-12 h-12 text-orange-600 mx-auto mb-4" />
                <h3 className="font-bold text-lg mb-2">Mobile Money</h3>
                <p className="text-gray-600 text-sm">Orange Money & MTN Money</p>
              </CardContent>
            </Card>
            
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all">
              <CardContent className="p-6 text-center">
                <QrCode className="w-12 h-12 text-purple-600 mx-auto mb-4" />
                <h3 className="font-bold text-lg mb-2">Billet électronique</h3>
                <p className="text-gray-600 text-sm">QR code sécurisé</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Smart Notifications Bar */}
        {notifications.length > 0 && (
          <Card className="mb-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <Bell className="w-5 h-5" />
                <div className="flex-1 overflow-x-auto">
                  <div className="flex gap-4">
                    {notifications.slice(0, 3).map((notif, idx) => (
                      <div key={idx} className="whitespace-nowrap bg-white/20 px-3 py-2 rounded-lg">
                        <span className="text-sm font-medium">{notif.title}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Enhanced Navigation Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5 mb-8 bg-white shadow-xl rounded-2xl p-2">
            <TabsTrigger 
              value="home" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-blue-600 data-[state=active]:text-white rounded-xl transition-all"
              data-testid="home-tab"
            >
              <Bus className="w-4 h-4" />
              <span className="hidden md:inline">Accueil</span>
            </TabsTrigger>
            <TabsTrigger 
              value="search" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-blue-600 data-[state=active]:text-white rounded-xl transition-all"
              data-testid="search-tab"
            >
              <Search className="w-4 h-4" />
              <span className="hidden md:inline">Recherche</span>
            </TabsTrigger>
            <TabsTrigger 
              value="tickets" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-blue-600 data-[state=active]:text-white rounded-xl transition-all"
              data-testid="tickets-tab"
            >
              <Ticket className="w-4 h-4" />
              <span className="hidden md:inline">Billets</span>
            </TabsTrigger>
            <TabsTrigger 
              value="offers" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-blue-600 data-[state=active]:text-white rounded-xl transition-all"
              data-testid="offers-tab"
            >
              <Gift className="w-4 h-4" />
              <span className="hidden md:inline">Offres</span>
            </TabsTrigger>
            <TabsTrigger 
              value="profile" 
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500 data-[state=active]:to-blue-600 data-[state=active]:text-white rounded-xl transition-all"
              data-testid="profile-tab"
            >
              <User className="w-4 h-4" />
              <span className="hidden md:inline">Profil</span>
            </TabsTrigger>
          </TabsList>

          {/* Home Tab (TicketCam style with enhancements) */}
          <TabsContent value="home" className="space-y-6">
            
            {/* Quick Search Section */}
            <Card className="shadow-2xl border-0 bg-gradient-to-r from-white to-blue-50">
              <CardContent className="p-8">
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-800 mb-2">Rechercher un trajet</h3>
                  <p className="text-gray-600">Prix en temps réel avec IA</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <Select onValueChange={(value) => setSearchForm({...searchForm, origin: value})}>
                    <SelectTrigger className="h-12">
                      <SelectValue placeholder="Ville de départ" />
                    </SelectTrigger>
                    <SelectContent>
                      {cities.map((city) => (
                        <SelectItem key={city.name} value={city.name}>
                          <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            {city.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select onValueChange={(value) => setSearchForm({...searchForm, destination: value})}>
                    <SelectTrigger className="h-12">
                      <SelectValue placeholder="Ville d'arrivée" />
                    </SelectTrigger>
                    <SelectContent>
                      {cities.map((city) => (
                        <SelectItem key={city.name} value={city.name}>
                          <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            {city.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Input
                    type="date"
                    value={searchForm.departure_date}
                    onChange={(e) => setSearchForm({...searchForm, departure_date: e.target.value})}
                    className="h-12"
                    min={new Date().toISOString().split('T')[0]}
                  />

                  <Select onValueChange={(value) => setSearchForm({...searchForm, passengers: parseInt(value)})}>
                    <SelectTrigger className="h-12">
                      <SelectValue placeholder="1 passager" />
                    </SelectTrigger>
                    <SelectContent>
                      {[1,2,3,4,5,6].map((num) => (
                        <SelectItem key={num} value={num.toString()}>
                          <div className="flex items-center gap-2">
                            <Users className="w-4 h-4" />
                            {num} passager{num > 1 ? 's' : ''}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <Button 
                  onClick={performSmartSearch}
                  className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 shadow-lg"
                  disabled={loading}
                  data-testid="search-button-home"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  ) : (
                    <Search className="w-5 h-5 mr-2" />
                  )}
                  Rechercher les meilleurs prix
                </Button>
              </CardContent>
            </Card>

            {/* Popular Routes (TicketCam integration) */}
            <div>
              <h3 className="text-2xl font-bold text-gray-800 mb-6">Trajets populaires</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {popularRoutes.map((route, idx) => (
                  <Card key={idx} className="group hover:shadow-2xl transition-all duration-300 border-0 bg-white/90 backdrop-blur-sm cursor-pointer" 
                        onClick={() => {
                          setSearchForm({
                            ...searchForm,
                            origin: route.origin,
                            destination: route.destination,
                            departure_date: new Date().toISOString().split('T')[0]
                          });
                          setActiveTab("search");
                        }}>
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h4 className="font-bold text-lg text-gray-800">
                            {route.origin} → {route.destination}
                          </h4>
                          <p className="text-sm text-gray-600">
                            {route.companies_count} compagnies • {route.average_duration}
                          </p>
                        </div>
                        <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-cyan-600 transition-colors" />
                      </div>

                      <div className="flex justify-between items-center mb-4">
                        <div>
                          <span className="text-sm text-gray-600">À partir de</span>
                          <div className="flex items-baseline gap-2">
                            <span className="text-2xl font-bold text-cyan-600">
                              {formatPrice(route.current_price || route.base_price)} FCFA
                            </span>
                            {route.current_price && route.current_price < route.base_price && (
                              <span className="text-xs text-red-500 line-through">
                                {formatPrice(route.base_price)} FCFA
                              </span>
                            )}
                          </div>
                        </div>
                        
                        {route.price_trend && (
                          <div className="flex items-center gap-1">
                            {route.price_trend === 'decreasing' ? 
                              <TrendingDown className="w-4 h-4 text-green-600" /> :
                              route.price_trend === 'increasing' ?
                              <TrendingUp className="w-4 h-4 text-red-600" /> :
                              <div className="w-4 h-4 bg-gray-300 rounded-full" />
                            }
                            <span className="text-xs text-gray-500 capitalize">{route.price_trend}</span>
                          </div>
                        )}
                      </div>

                      <div className="flex justify-between items-center">
                        <div className="text-xs text-gray-500">
                          Prochain départ: {route.next_departure}
                        </div>
                        <div className="text-xs text-gray-500">
                          {route.seats_available} places disponibles
                        </div>
                      </div>

                      {route.special_offer && (
                        <div className="mt-3 p-2 bg-gradient-to-r from-yellow-100 to-orange-100 rounded-lg">
                          <p className="text-xs font-medium text-orange-800">{route.special_offer}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Smart Suggestions */}
            {smartSuggestions.length > 0 && (
              <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-purple-800">
                    <Target className="w-5 h-5" />
                    Suggestions intelligentes pour vous
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {smartSuggestions.map((suggestion, idx) => (
                      <Card key={idx} className="bg-white/70 hover:bg-white transition-all cursor-pointer">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold">{suggestion.route}</h4>
                            <Heart className="w-4 h-4 text-pink-500" />
                          </div>
                          <p className="text-sm text-gray-600 mb-3">{suggestion.reason}</p>
                          <div className="flex justify-between items-center">
                            <div>
                              <span className="font-bold text-green-600">{formatPrice(suggestion.price)} FCFA</span>
                              <span className="text-xs text-gray-500 ml-2 line-through">
                                {formatPrice(suggestion.originalPrice)} FCFA
                              </span>
                            </div>
                            <Badge className="bg-green-100 text-green-800">
                              Économisez {formatPrice(suggestion.savings)} FCFA
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

          {/* Enhanced Search Tab */}
          <TabsContent value="search" className="space-y-6">
            <Card className="shadow-xl">
              <CardHeader>
                <CardTitle>Recherche avancée avec IA</CardTitle>
                <CardDescription>Prix dynamiques et filtres intelligents</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Classe de service</Label>
                    <Select 
                      value={searchForm.service_class}
                      onValueChange={(value) => setSearchForm({...searchForm, service_class: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="economy">
                          <div className="flex items-center gap-2">
                            {getServiceClassIcon("economy")}
                            Économique
                          </div>
                        </SelectItem>
                        <SelectItem value="comfort">
                          <div className="flex items-center gap-2">
                            {getServiceClassIcon("comfort")}
                            Confort
                          </div>
                        </SelectItem>
                        <SelectItem value="vip">
                          <div className="flex items-center gap-2">
                            {getServiceClassIcon("vip")}
                            VIP
                          </div>
                        </SelectItem>
                        <SelectItem value="express">
                          <div className="flex items-center gap-2">
                            {getServiceClassIcon("express")}
                            Express
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Préférence horaire</Label>
                    <Select 
                      value={searchForm.time_preference}
                      onValueChange={(value) => setSearchForm({...searchForm, time_preference: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="any">Toute heure</SelectItem>
                        <SelectItem value="morning">Matin (5h-12h)</SelectItem>
                        <SelectItem value="afternoon">Après-midi (12h-18h)</SelectItem>
                        <SelectItem value="evening">Soir (18h-23h)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label>Budget maximum (optionnel)</Label>
                  <Input
                    type="number"
                    placeholder="Ex: 15000 FCFA"
                    value={searchForm.budget_max || ""}
                    onChange={(e) => setSearchForm({...searchForm, budget_max: e.target.value ? parseInt(e.target.value) : null})}
                  />
                </div>

                <Button 
                  onClick={performSmartSearch}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700"
                  disabled={loading}
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Search className="w-4 h-4 mr-2" />}
                  Recherche intelligente
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Results Tab */}
          <TabsContent value="results" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-xl font-bold">Résultats de recherche ({routes.length})</h3>
              <Badge className="bg-cyan-100 text-cyan-800">
                <Lightning className="w-3 h-3 mr-1" />
                Prix dynamiques IA
              </Badge>
            </div>

            {routes.map((route) => (
              <Card key={route.id} className="hover:shadow-xl transition-all border-0 bg-white/95">
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Route Info */}
                    <div className="lg:col-span-2">
                      <div className="flex items-center gap-4 mb-4">
                        <div className="text-center">
                          <div className="font-bold text-xl text-cyan-600">{route.departure_time}</div>
                          <div className="text-sm text-gray-600">{route.origin}</div>
                        </div>
                        
                        <div className="flex-1 flex flex-col items-center">
                          <div className="flex items-center w-full">
                            <div className="w-3 h-3 bg-cyan-500 rounded-full"></div>
                            <div className="flex-1 h-1 bg-gradient-to-r from-cyan-500 to-blue-600"></div>
                            <Bus className="w-6 h-6 text-cyan-600 mx-2" />
                            <div className="flex-1 h-1 bg-gradient-to-r from-cyan-500 to-blue-600"></div>
                            <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                          </div>
                          <div className="text-xs text-gray-500 mt-2">{route.duration} • {route.distance_km}km</div>
                        </div>
                        
                        <div className="text-center">
                          <div className="font-bold text-xl text-blue-600">{route.arrival_time}</div>
                          <div className="text-sm text-gray-600">{route.destination}</div>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2 mb-3">
                        <Badge className={`bg-gradient-to-r ${getServiceClassColor(route.service_class)} text-white`}>
                          {getServiceClassIcon(route.service_class)}
                          <span className="ml-1 capitalize">{route.service_class}</span>
                        </Badge>
                        
                        <Badge variant="outline">{route.company}</Badge>
                        
                        {route.eco_friendly && (
                          <Badge className="bg-green-100 text-green-800">
                            <Leaf className="w-3 h-3 mr-1" />
                            Éco
                          </Badge>
                        )}

                        <Badge variant="outline">
                          <Star className="w-3 h-3 mr-1" />
                          {route.driver_info?.rating || 4.5}
                        </Badge>
                      </div>

                      {route.amenities && (
                        <div className="flex flex-wrap gap-2">
                          {route.amenities.slice(0, 4).map((amenity, idx) => (
                            <div key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                              <Wifi className="w-3 h-3 inline mr-1" />
                              {amenity}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* AI Insights */}
                    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 rounded-lg">
                      <div className="text-sm font-semibold text-blue-800 mb-2">Analyse IA</div>
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between">
                          <span>Popularité:</span>
                          <span>{route.route_popularity}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Demande:</span>
                          <Badge 
                            variant="outline" 
                            className={
                              route.demand_level === 'high' ? 'border-red-500 text-red-700' :
                              route.demand_level === 'low' ? 'border-green-500 text-green-700' :
                              'border-yellow-500 text-yellow-700'
                            }
                          >
                            {route.demand_level}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Empreinte CO₂:</span>
                          <span>{route.carbon_footprint}kg</span>
                        </div>
                      </div>
                    </div>

                    {/* Price & Action */}
                    <div className="flex flex-col justify-between">
                      <div className="text-right mb-4">
                        <div className="flex items-center justify-end gap-2 mb-2">
                          {route.dynamic_price < route.base_price && (
                            <span className="text-sm text-gray-500 line-through">
                              {formatPrice(route.base_price)} FCFA
                            </span>
                          )}
                          <div className="text-2xl font-bold text-cyan-600">
                            {formatPrice(route.dynamic_price)} FCFA
                          </div>
                        </div>
                        
                        <div className="text-sm text-gray-600 mb-1">
                          {route.available_seats} places disponibles
                        </div>
                        
                        {route.dynamic_price < route.base_price && (
                          <Badge className="bg-green-100 text-green-800 text-xs">
                            <Percent className="w-3 h-3 mr-1" />
                            Économisez {formatPrice(route.base_price - route.dynamic_price)} FCFA
                          </Badge>
                        )}
                      </div>

                      <Button 
                        onClick={() => selectRouteAndProceedToBooking(route)}
                        className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Réserver
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Booking Tab with Mobile Money Integration */}
          <TabsContent value="booking" className="space-y-6">
            {searchForm.selectedRoute && (
              <Card className="shadow-2xl">
                <CardHeader className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white">
                  <CardTitle>Finaliser la réservation</CardTitle>
                  <CardDescription className="text-cyan-100">
                    {searchForm.selectedRoute.origin} → {searchForm.selectedRoute.destination}
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-8 space-y-6">
                  
                  {/* Payment Method Selection (TicketCam integration) */}
                  <div>
                    <h4 className="font-semibold mb-4">Mode de paiement</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {mobileMoneyProviders.map((provider) => (
                        <Card 
                          key={provider.code}
                          className={`cursor-pointer transition-all ${
                            mobileMoneyForm.provider === provider.code 
                              ? 'ring-2 ring-cyan-500 bg-cyan-50' 
                              : 'hover:shadow-md'
                          }`}
                          onClick={() => setMobileMoneyForm(prev => ({ ...prev, provider: provider.code }))}
                        >
                          <CardContent className="p-4 text-center">
                            {getMobileMoneyIcon(provider.code)}
                            <div className="mt-2">
                              <div className="font-semibold text-sm">{provider.name}</div>
                              <div className="text-xs text-gray-600">
                                Frais: {(provider.fees_percent * 100).toFixed(1)}%
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>

                    {selectedPaymentMethod === "mobile_money" && (
                      <div className="mt-4">
                        <Label>Numéro de téléphone Mobile Money</Label>
                        <Input
                          placeholder="+237 6XX XXX XXX"
                          value={mobileMoneyForm.phone_number}
                          onChange={(e) => setMobileMoneyForm(prev => ({ ...prev, phone_number: e.target.value }))}
                          className="mt-2"
                        />
                      </div>
                    )}
                  </div>

                  {/* Price Summary */}
                  <Card className="bg-gradient-to-r from-gray-50 to-cyan-50">
                    <CardContent className="p-6">
                      <h4 className="font-bold mb-4">Récapitulatif</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span>Prix du trajet ({searchForm.passengers} passager{searchForm.passengers > 1 ? 's' : ''})</span>
                          <span className="font-semibold">
                            {formatPrice(searchForm.selectedRoute.dynamic_price * searchForm.passengers)} FCFA
                          </span>
                        </div>
                        
                        <div className="flex justify-between text-sm">
                          <span>Taxes et frais (5%)</span>
                          <span>{formatPrice(Math.round(searchForm.selectedRoute.dynamic_price * searchForm.passengers * 0.05))} FCFA</span>
                        </div>
                        
                        {selectedPaymentMethod === "mobile_money" && (
                          <div className="flex justify-between text-sm">
                            <span>Frais Mobile Money</span>
                            <span>
                              {formatPrice(Math.round(mobileMoneyForm.amount * (mobileMoneyProviders.find(p => p.code === mobileMoneyForm.provider)?.fees_percent || 0.02)))} FCFA
                            </span>
                          </div>
                        )}
                        
                        <div className="border-t pt-3 font-bold text-lg">
                          <div className="flex justify-between">
                            <span>Total à payer</span>
                            <span className="text-cyan-600">
                              {formatPrice(Math.round(
                                (searchForm.selectedRoute.dynamic_price * searchForm.passengers * 1.05) +
                                (selectedPaymentMethod === "mobile_money" ? 
                                  mobileMoneyForm.amount * (mobileMoneyProviders.find(p => p.code === mobileMoneyForm.provider)?.fees_percent || 0.02) : 0)
                              ))} FCFA
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Action Buttons */}
                  <div className="flex gap-4">
                    <Button 
                      variant="outline" 
                      onClick={() => setActiveTab("results")}
                      className="flex-1"
                    >
                      Retour aux résultats
                    </Button>
                    <Button 
                      onClick={createFusionBooking}
                      disabled={loading || !mobileMoneyForm.phone_number}
                      className="flex-1 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
                    >
                      {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <CheckCircle className="w-4 h-4 mr-2" />}
                      Confirmer et Payer
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Other tabs would be similar to the original but enhanced with fusion features */}
          <TabsContent value="tickets" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Mes billets électroniques</CardTitle>
              </CardHeader>
              <CardContent>
                {bookings.length === 0 ? (
                  <div className="text-center py-8">
                    <QrCode className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <p className="text-gray-500 mb-4">Aucun billet trouvé</p>
                    <Button 
                      onClick={() => setActiveTab("home")}
                      className="bg-gradient-to-r from-cyan-500 to-blue-600"
                    >
                      Réserver un trajet
                    </Button>
                  </div>
                ) : (
                  <div className="grid gap-4">
                    {bookings.map((booking) => (
                      <Card key={booking.id} className="border-l-4 border-l-cyan-500">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-bold">Référence: {booking.booking_reference}</div>
                              <div className="text-sm text-gray-600">
                                {booking.passenger_count} passager{booking.passenger_count > 1 ? 's' : ''}
                              </div>
                            </div>
                            <Badge className="bg-green-100 text-green-800">
                              {booking.status}
                            </Badge>
                          </div>
                          <div className="mt-4 flex justify-between items-center">
                            <div className="text-2xl font-bold text-cyan-600">
                              {formatPrice(booking.final_price)} FCFA
                            </div>
                            <Button variant="outline" size="sm">
                              <QrCode className="w-4 h-4 mr-2" />
                              Voir le billet
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Profile and Offers tabs would be similar with fusion enhancements */}
          <TabsContent value="offers" className="space-y-6">
            <Card className="text-center py-12">
              <CardContent>
                <Gift className="w-16 h-16 mx-auto mb-4 text-cyan-500" />
                <h3 className="text-xl font-bold mb-2">Offres spéciales à venir</h3>
                <p className="text-gray-600">Restez connecté pour des promotions exclusives !</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="profile" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Mon profil BusConnect</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                    {user.first_name[0]}{user.last_name[0]}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">{user.first_name} {user.last_name}</h3>
                    <p className="text-gray-600">Client depuis 2024</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="text-center p-4 bg-cyan-50">
                    <div className="text-2xl font-bold text-cyan-600">{bookings.length}</div>
                    <div className="text-sm text-gray-600">Voyages effectués</div>
                  </Card>
                  
                  <Card className="text-center p-4 bg-green-50">
                    <div className="text-2xl font-bold text-green-600">{user.loyalty_points}</div>
                    <div className="text-sm text-gray-600">Points fidélité</div>
                  </Card>
                  
                  <Card className="text-center p-4 bg-purple-50">
                    <div className="text-2xl font-bold text-purple-600">5</div>
                    <div className="text-sm text-gray-600">Codes promo utilisés</div>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
      
      <Toaster />
      </>
      )}
    </div>
  );
}

export default App;