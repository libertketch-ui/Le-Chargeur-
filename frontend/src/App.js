import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
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
  Leaf
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [activeTab, setActiveTab] = useState("search");
  const [cities, setCities] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState({ id: "user123", first_name: "Jean", last_name: "Dupont" });

  // Search form state
  const [searchForm, setSearchForm] = useState({
    origin: "",
    destination: "",
    departure_date: "",
    passengers: 1
  });

  // Booking form state
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [selectedBaggage, setSelectedBaggage] = useState([]);
  const [baggageOptions, setBaggageOptions] = useState([]);
  const [promoCode, setPromoCode] = useState("");
  const [carbonOffset, setCarbonOffset] = useState(false);

  // Tracking state
  const [trackingReference, setTrackingReference] = useState("");
  const [trackingInfo, setTrackingInfo] = useState(null);

  useEffect(() => {
    loadCities();
    loadOffers();
    loadBaggageOptions();
    loadUserBookings();
  }, []);

  const loadCities = async () => {
    try {
      const response = await axios.get(`${API}/cities`);
      setCities(response.data.cities);
    } catch (error) {
      console.error("Error loading cities:", error);
      toast.error("Erreur lors du chargement des villes");
    }
  };

  const loadOffers = async () => {
    try {
      const response = await axios.get(`${API}/offers`);
      setOffers(response.data.offers);
    } catch (error) {
      console.error("Error loading offers:", error);
    }
  };

  const loadBaggageOptions = async () => {
    try {
      const response = await axios.get(`${API}/baggage/options`);
      setBaggageOptions(response.data.baggage_options);
    } catch (error) {
      console.error("Error loading baggage options:", error);
    }
  };

  const loadUserBookings = async () => {
    try {
      const response = await axios.get(`${API}/bookings/user/${user.id}`);
      setBookings(response.data.bookings);
    } catch (error) {
      console.error("Error loading bookings:", error);
    }
  };

  const searchRoutes = async () => {
    if (!searchForm.origin || !searchForm.destination || !searchForm.departure_date) {
      toast.error("Veuillez remplir tous les champs de recherche");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/search`, searchForm);
      setRoutes(response.data.routes);
      toast.success(`${response.data.total} trajets trouvés`);
    } catch (error) {
      console.error("Error searching routes:", error);
      toast.error("Erreur lors de la recherche");
    } finally {
      setLoading(false);
    }
  };

  const selectRoute = (route) => {
    setSelectedRoute(route);
    setActiveTab("booking");
  };

  const toggleBaggage = (option) => {
    const existing = selectedBaggage.find(b => b.type === option.type);
    if (existing) {
      setSelectedBaggage(selectedBaggage.filter(b => b.type !== option.type));
    } else {
      setSelectedBaggage([...selectedBaggage, { 
        type: option.type, 
        quantity: 1, 
        price: option.price 
      }]);
    }
  };

  const createBooking = async () => {
    if (!selectedRoute) {
      toast.error("Aucun trajet sélectionné");
      return;
    }

    setLoading(true);
    try {
      const bookingData = {
        user_id: user.id,
        route_id: selectedRoute.id,
        passenger_count: searchForm.passengers,
        seat_numbers: Array.from({length: searchForm.passengers}, (_, i) => `${i + 1}A`),
        baggage: selectedBaggage,
        promo_code: promoCode || null,
        carbon_offset: carbonOffset
      };

      const response = await axios.post(`${API}/bookings`, bookingData);
      toast.success(`Réservation confirmée ! Référence: ${response.data.booking_reference}`);
      
      setBookings([...bookings, response.data]);
      setActiveTab("tickets");
      setSelectedRoute(null);
      setSelectedBaggage([]);
      setPromoCode("");
      setCarbonOffset(false);
    } catch (error) {
      console.error("Error creating booking:", error);
      toast.error("Erreur lors de la réservation");
    } finally {
      setLoading(false);
    }
  };

  const trackBooking = async () => {
    if (!trackingReference) {
      toast.error("Veuillez saisir une référence de réservation");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`${API}/track/${trackingReference}`);
      setTrackingInfo(response.data);
      toast.success("Informations de suivi mises à jour");
    } catch (error) {
      console.error("Error tracking booking:", error);
      toast.error("Référence introuvable");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'on_time': return 'bg-green-500';
      case 'delayed': return 'bg-yellow-500';
      case 'boarding': return 'bg-blue-500';
      case 'en_route': return 'bg-purple-500';
      case 'arrived': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status) => {
    switch(status) {
      case 'on_time': return 'À l\'heure';
      case 'delayed': return 'Retardé';
      case 'boarding': return 'Embarquement';
      case 'en_route': return 'En route';
      case 'arrived': return 'Arrivé';
      default: return 'Inconnu';
    }
  };

  const getAmenityIcon = (amenity) => {
    switch(amenity.toLowerCase()) {
      case 'wifi': return <Wifi className="w-4 h-4" />;
      case 'ac': return <Car className="w-4 h-4" />;
      case 'toilettes': return <Coffee className="w-4 h-4" />;
      case 'prises usb': return <Zap className="w-4 h-4" />;
      case 'collations': return <Utensils className="w-4 h-4" />;
      case 'télévision': return <Monitor className="w-4 h-4" />;
      default: return <CheckCircle className="w-4 h-4" />;
    }
  };

  const getBaggageIcon = (type) => {
    switch(type) {
      case 'carry_on': return <Backpack className="w-5 h-5" />;
      case 'checked': return <Briefcase className="w-5 h-5" />;
      case 'extra': return <Plus className="w-5 h-5" />;
      case 'bike': return <Bike className="w-5 h-5" />;
      case 'sports': return <Dumbbell className="w-5 h-5" />;
      default: return <Briefcase className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto p-4 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🚌 BusConnect Cameroun
          </h1>
          <p className="text-gray-600">Votre compagnon de voyage intelligent</p>
        </div>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5 mb-8 bg-white shadow-md rounded-lg">
            <TabsTrigger 
              value="search" 
              className="flex items-center gap-2 data-[state=active]:bg-blue-500 data-[state=active]:text-white"
              data-testid="search-tab"
            >
              <Search className="w-4 h-4" />
              Recherche
            </TabsTrigger>
            <TabsTrigger 
              value="tracking" 
              className="flex items-center gap-2 data-[state=active]:bg-blue-500 data-[state=active]:text-white"
              data-testid="tracking-tab"
            >
              <Navigation className="w-4 h-4" />
              Suivi Live
            </TabsTrigger>
            <TabsTrigger 
              value="tickets" 
              className="flex items-center gap-2 data-[state=active]:bg-blue-500 data-[state=active]:text-white"
              data-testid="tickets-tab"
            >
              <Ticket className="w-4 h-4" />
              Mes Billets
            </TabsTrigger>
            <TabsTrigger 
              value="offers" 
              className="flex items-center gap-2 data-[state=active]:bg-blue-500 data-[state=active]:text-white"
              data-testid="offers-tab"
            >
              <Gift className="w-4 h-4" />
              Offres
            </TabsTrigger>
            <TabsTrigger 
              value="profile" 
              className="flex items-center gap-2 data-[state=active]:bg-blue-500 data-[state=active]:text-white"
              data-testid="profile-tab"
            >
              <User className="w-4 h-4" />
              Profil
            </TabsTrigger>
          </TabsList>

          {/* Search Tab */}
          <TabsContent value="search" className="space-y-6">
            <Card data-testid="search-form">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="w-5 h-5" />
                  Rechercher un trajet
                </CardTitle>
                <CardDescription>
                  Trouvez le meilleur trajet pour votre destination
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="origin">Ville de départ</Label>
                    <Select onValueChange={(value) => setSearchForm({...searchForm, origin: value})}>
                      <SelectTrigger data-testid="origin-select">
                        <SelectValue placeholder="Sélectionnez la ville de départ" />
                      </SelectTrigger>
                      <SelectContent>
                        {cities.map((city) => (
                          <SelectItem key={city.name} value={city.name}>
                            {city.name} ({city.region})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="destination">Ville d'arrivée</Label>
                    <Select onValueChange={(value) => setSearchForm({...searchForm, destination: value})}>
                      <SelectTrigger data-testid="destination-select">
                        <SelectValue placeholder="Sélectionnez la ville d'arrivée" />
                      </SelectTrigger>
                      <SelectContent>
                        {cities.map((city) => (
                          <SelectItem key={city.name} value={city.name}>
                            {city.name} ({city.region})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="date">Date de départ</Label>
                    <Input
                      type="date"
                      value={searchForm.departure_date}
                      onChange={(e) => setSearchForm({...searchForm, departure_date: e.target.value})}
                      data-testid="departure-date"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="passengers">Nombre de passagers</Label>
                    <Select onValueChange={(value) => setSearchForm({...searchForm, passengers: parseInt(value)})}>
                      <SelectTrigger data-testid="passengers-select">
                        <SelectValue placeholder="1 passager" />
                      </SelectTrigger>
                      <SelectContent>
                        {[1,2,3,4,5,6].map((num) => (
                          <SelectItem key={num} value={num.toString()}>
                            {num} passager{num > 1 ? 's' : ''}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Button 
                  onClick={searchRoutes} 
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  disabled={loading}
                  data-testid="search-button"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Search className="w-4 h-4 mr-2" />}
                  Rechercher
                </Button>
              </CardContent>
            </Card>

            {/* Search Results */}
            {routes.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-xl font-semibold">Trajets disponibles ({routes.length})</h3>
                {routes.map((route) => (
                  <Card key={route.id} className="hover:shadow-lg transition-shadow" data-testid={`route-${route.id}`}>
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-4">
                          <div className="text-center">
                            <div className="font-bold text-lg">{route.departure_time}</div>
                            <div className="text-sm text-gray-600">{route.origin}</div>
                          </div>
                          
                          <div className="flex flex-col items-center px-4">
                            <Route className="w-5 h-5 text-blue-500" />
                            <div className="text-xs text-gray-500">{route.duration}</div>
                          </div>
                          
                          <div className="text-center">
                            <div className="font-bold text-lg">{route.arrival_time}</div>
                            <div className="text-sm text-gray-600">{route.destination}</div>
                          </div>
                        </div>

                        <div className="text-right">
                          <div className="text-2xl font-bold text-blue-600">{route.price.toLocaleString()} FCFA</div>
                          <div className="text-sm text-gray-600">{route.available_seats} places disponibles</div>
                        </div>
                      </div>

                      <div className="flex justify-between items-center mb-4">
                        <div>
                          <Badge variant="secondary" className="mr-2">{route.company}</Badge>
                          <Badge variant="outline">{route.bus_type}</Badge>
                        </div>
                        
                        <div className="flex gap-2">
                          {route.amenities.map((amenity, idx) => (
                            <div key={idx} className="flex items-center gap-1 text-xs text-gray-600">
                              {getAmenityIcon(amenity)}
                              <span>{amenity}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <Button 
                        onClick={() => selectRoute(route)}
                        className="w-full bg-green-600 hover:bg-green-700"
                        data-testid={`select-route-${route.id}`}
                      >
                        Sélectionner ce trajet
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Tracking Tab */}
          <TabsContent value="tracking" className="space-y-6">
            <Card data-testid="tracking-form">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Navigation className="w-5 h-5" />
                  Suivi en temps réel
                </CardTitle>
                <CardDescription>
                  Suivez votre bus en temps réel
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="tracking-ref">Référence de réservation</Label>
                  <Input
                    placeholder="Ex: BC123456"
                    value={trackingReference}
                    onChange={(e) => setTrackingReference(e.target.value)}
                    data-testid="tracking-reference"
                  />
                </div>
                
                <Button 
                  onClick={trackBooking}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  disabled={loading}
                  data-testid="track-button"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Compass className="w-4 h-4 mr-2" />}
                  Suivre mon trajet
                </Button>
              </CardContent>
            </Card>

            {/* Tracking Results */}
            {trackingInfo && (
              <Card data-testid="tracking-info">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bus className="w-5 h-5" />
                    Statut du trajet - {trackingInfo.booking_reference}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center gap-4">
                    <div className={`w-4 h-4 rounded-full ${getStatusColor(trackingInfo.status)}`} />
                    <div>
                      <div className="font-semibold">{getStatusText(trackingInfo.status)}</div>
                      <div className="text-sm text-gray-600">
                        Actuellement à {trackingInfo.current_location}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold mb-2">Prochains arrêts</h4>
                      <div className="space-y-2">
                        {trackingInfo.next_stops.map((stop, idx) => (
                          <div key={idx} className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-blue-500 rounded-full" />
                            <span className="text-sm">{idx + 1}. {stop}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <div className="text-sm text-gray-600">Arrivée estimée</div>
                        <div className="font-semibold">{trackingInfo.estimated_arrival}</div>
                        {trackingInfo.delay_minutes > 0 && (
                          <div className="text-sm text-yellow-600">
                            Retard: {trackingInfo.delay_minutes} min
                          </div>
                        )}
                      </div>

                      <div>
                        <div className="text-sm text-gray-600">Distance restante</div>
                        <div className="font-semibold">{trackingInfo.distance_remaining_km} km</div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Mises à jour en direct</h4>
                    <div className="space-y-2">
                      {trackingInfo.live_updates.map((update, idx) => (
                        <div key={idx} className="text-sm bg-blue-50 p-2 rounded">
                          {update}
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tickets Tab */}
          <TabsContent value="tickets" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Ticket className="w-5 h-5" />
                  Mes billets ({bookings.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {bookings.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Ticket className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>Aucun billet trouvé</p>
                    <p className="text-sm">Réservez votre premier trajet dans l'onglet Recherche</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {bookings.map((booking) => (
                      <Card key={booking.id} className="border-l-4 border-l-blue-500" data-testid={`ticket-${booking.booking_reference}`}>
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start mb-4">
                            <div>
                              <div className="font-bold text-lg">Référence: {booking.booking_reference}</div>
                              <div className="text-sm text-gray-600">
                                {booking.passenger_count} passager{booking.passenger_count > 1 ? 's' : ''}
                              </div>
                            </div>
                            
                            <div className="text-right">
                              <div className="font-bold text-xl text-green-600">
                                {booking.total_price.toLocaleString()} FCFA
                              </div>
                              <Badge variant="outline" className="text-green-600 border-green-600">
                                {booking.status}
                              </Badge>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                              <div className="text-sm text-gray-600">Sièges réservés</div>
                              <div className="font-semibold">{booking.seat_numbers.join(', ')}</div>
                            </div>
                            
                            {booking.baggage.length > 0 && (
                              <div>
                                <div className="text-sm text-gray-600">Bagages</div>
                                <div className="flex gap-2">
                                  {booking.baggage.map((bag, idx) => (
                                    <Badge key={idx} variant="secondary">
                                      {bag.type} x{bag.quantity}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>

                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <QrCode className="w-4 h-4" />
                              <span className="text-sm">Code QR: {booking.qr_code}</span>
                            </div>
                            
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => {
                                setTrackingReference(booking.booking_reference);
                                setActiveTab("tracking");
                              }}
                              data-testid={`track-booking-${booking.booking_reference}`}
                            >
                              Suivre le trajet
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

          {/* Offers Tab */}
          <TabsContent value="offers" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Gift className="w-5 h-5" />
                  Offres spéciales
                </CardTitle>
                <CardDescription>
                  Profitez de nos promotions exclusives
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {offers.map((offer) => (
                    <Card key={offer.id} className="overflow-hidden" data-testid={`offer-${offer.id}`}>
                      {offer.image_url && (
                        <div className="h-32 bg-gradient-to-r from-blue-500 to-purple-600 relative">
                          <img 
                            src={offer.image_url} 
                            alt={offer.title}
                            className="w-full h-full object-cover opacity-75"
                          />
                          <div className="absolute inset-0 bg-black bg-opacity-30" />
                        </div>
                      )}
                      
                      <CardContent className="p-4">
                        <h3 className="font-bold text-lg mb-2">{offer.title}</h3>
                        <p className="text-sm text-gray-600 mb-4">{offer.description}</p>
                        
                        <div className="flex justify-between items-center">
                          {offer.discount_percent && (
                            <Badge variant="secondary" className="bg-green-100 text-green-800">
                              -{offer.discount_percent}%
                            </Badge>
                          )}
                          
                          {offer.cashback_amount && (
                            <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                              +{offer.cashback_amount} FCFA
                            </Badge>
                          )}

                          {offer.type === 'carbon_offset' && (
                            <Badge variant="secondary" className="bg-green-100 text-green-800">
                              <Leaf className="w-3 h-3 mr-1" />
                              Éco-responsable
                            </Badge>
                          )}
                        </div>

                        {offer.code && (
                          <div className="mt-4 p-2 bg-gray-100 rounded text-center">
                            <div className="text-xs text-gray-600">Code promo</div>
                            <div className="font-mono font-bold">{offer.code}</div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Profile Tab */}
          <TabsContent value="profile" className="space-y-6">
            <Card data-testid="user-profile">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Mon Profil
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                    {user.first_name[0]}{user.last_name[0]}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold">{user.first_name} {user.last_name}</h3>
                    <p className="text-gray-600">Client BusConnect</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="text-center p-4">
                    <div className="text-2xl font-bold text-blue-600">{bookings.length}</div>
                    <div className="text-sm text-gray-600">Voyages effectués</div>
                  </Card>
                  
                  <Card className="text-center p-4">
                    <div className="text-2xl font-bold text-green-600">2,500</div>
                    <div className="text-sm text-gray-600">Points fidélité</div>
                  </Card>
                  
                  <Card className="text-center p-4">
                    <div className="text-2xl font-bold text-purple-600">5</div>
                    <div className="text-sm text-gray-600">Codes promo utilisés</div>
                  </Card>
                </div>

                <div>
                  <h4 className="font-semibold mb-4">Progression Fidélité</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Vers le statut Premium</span>
                      <span>{bookings.length}/10 voyages</span>
                    </div>
                    <Progress value={(bookings.length / 10) * 100} className="w-full" />
                    <p className="text-xs text-gray-600">
                      Plus que {10 - bookings.length} voyages pour débloquer des avantages exclusifs !
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">Préférences</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Notifications</span>
                      <Badge variant="outline">Activées</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Newsletter</span>
                      <Badge variant="outline">Abonné</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Compensation carbone</span>
                      <Badge variant="outline">Préférée</Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Booking Modal/Section */}
        {selectedRoute && activeTab === "booking" && (
          <Card className="mt-8" data-testid="booking-form">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Ticket className="w-5 h-5" />
                Finaliser la réservation
              </CardTitle>
              <CardDescription>
                {selectedRoute.origin} → {selectedRoute.destination} | {selectedRoute.departure_time}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Baggage Selection */}
              <div>
                <h4 className="font-semibold mb-4">Sélection des bagages</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {baggageOptions.map((option) => (
                    <Card 
                      key={option.type}
                      className={`cursor-pointer transition-all ${
                        selectedBaggage.some(b => b.type === option.type) 
                          ? 'ring-2 ring-blue-500 bg-blue-50' 
                          : 'hover:shadow-md'
                      }`}
                      onClick={() => toggleBaggage(option)}
                      data-testid={`baggage-${option.type}`}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center gap-3 mb-2">
                          {getBaggageIcon(option.type)}
                          <div className="flex-1">
                            <div className="font-medium">{option.name}</div>
                            <div className="text-xs text-gray-600">{option.description}</div>
                          </div>
                          {option.included ? (
                            <Badge variant="secondary" className="bg-green-100 text-green-800">
                              Inclus
                            </Badge>
                          ) : (
                            <div className="text-right">
                              <div className="font-bold text-sm">+{option.price} FCFA</div>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Promo Code */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="promo">Code promotionnel (optionnel)</Label>
                  <Input
                    placeholder="Ex: WEEKEND15"
                    value={promoCode}
                    onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                    data-testid="promo-code-input"
                  />
                </div>
                
                <div className="flex items-center space-x-2 pt-6">
                  <input
                    type="checkbox"
                    id="carbon-offset"
                    checked={carbonOffset}
                    onChange={(e) => setCarbonOffset(e.target.checked)}
                    className="rounded"
                    data-testid="carbon-offset-checkbox"
                  />
                  <Label htmlFor="carbon-offset" className="text-sm">
                    Compensation carbone (+500 FCFA) <Leaf className="w-3 h-3 inline text-green-600" />
                  </Label>
                </div>
              </div>

              {/* Price Summary */}
              <Card className="bg-gray-50">
                <CardContent className="p-4">
                  <h4 className="font-semibold mb-3">Récapitulatif des prix</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Trajet ({searchForm.passengers} passager{searchForm.passengers > 1 ? 's' : ''})</span>
                      <span>{(selectedRoute.price * searchForm.passengers).toLocaleString()} FCFA</span>
                    </div>
                    
                    {selectedBaggage.map((bag, idx) => (
                      <div key={idx} className="flex justify-between">
                        <span>{bag.type} (x{bag.quantity})</span>
                        <span>{(bag.price * bag.quantity).toLocaleString()} FCFA</span>
                      </div>
                    ))}
                    
                    {carbonOffset && (
                      <div className="flex justify-between">
                        <span>Compensation carbone</span>
                        <span>500 FCFA</span>
                      </div>
                    )}
                    
                    {promoCode && (
                      <div className="flex justify-between text-green-600">
                        <span>Code promo ({promoCode})</span>
                        <span>-15%</span>
                      </div>
                    )}
                    
                    <div className="border-t pt-2 font-bold text-lg">
                      <div className="flex justify-between">
                        <span>Total</span>
                        <span className="text-blue-600">
                          {((selectedRoute.price * searchForm.passengers) + 
                            selectedBaggage.reduce((sum, bag) => sum + (bag.price * bag.quantity), 0) +
                            (carbonOffset ? 500 : 0)).toLocaleString()} FCFA
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
                  onClick={() => {setSelectedRoute(null); setActiveTab("search");}}
                  className="flex-1"
                  data-testid="cancel-booking"
                >
                  Annuler
                </Button>
                <Button 
                  onClick={createBooking}
                  disabled={loading}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                  data-testid="confirm-booking"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <CheckCircle className="w-4 h-4 mr-2" />}
                  Confirmer la réservation
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
      
      <Toaster />
    </div>
  );
}

export default App;