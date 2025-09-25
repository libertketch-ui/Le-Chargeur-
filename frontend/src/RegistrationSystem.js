import React, { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Textarea } from "./components/ui/textarea";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { Alert, AlertDescription } from "./components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { toast } from "sonner";
import { 
  User, 
  Building, 
  Car, 
  Truck, 
  Upload, 
  FileText, 
  Camera, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Phone, 
  Mail, 
  Shield, 
  Users, 
  Settings,
  Eye,
  Download,
  ThumbsUp,
  ThumbsDown,
  Loader2,
  Info,
  Smartphone,
  CreditCard,
  MapPin,
  Calendar
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RegistrationSystem = () => {
  const [currentStep, setCurrentStep] = useState("userType");
  const [registrationData, setRegistrationData] = useState({
    userType: "",
    email: "",
    phone: "",
    firstName: "",
    lastName: "",
    agencyName: "",
    agencyAddress: "",
    agencyLicenseNumber: "",
    drivingLicenseNumber: "",
    drivingLicenseExpiry: "",
    transportExperienceYears: 0,
    preferredLanguage: "fr"
  });
  const [userId, setUserId] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [uploadedDocuments, setUploadedDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [registrationStatus, setRegistrationStatus] = useState("");

  // Admin panel state
  const [adminView, setAdminView] = useState(false);
  const [pendingUsers, setPendingUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [adminNotes, setAdminNotes] = useState("");

  const userTypes = [
    {
      value: "client",
      label: "Client",
      description: "Je souhaite réserver des billets de transport",
      icon: <User className="w-8 h-8 text-blue-600" />,
      requirements: ["Numéro de téléphone valide", "Adresse email (optionnel)"]
    },
    {
      value: "agency",
      label: "Agence de voyage",
      description: "Je représente une agence de voyage",
      icon: <Building className="w-8 h-8 text-green-600" />,
      requirements: [
        "Autorisation de transport",
        "Informations de l'agence",
        "Documents d'identité",
        "Validation administrative"
      ]
    },
    {
      value: "individual_transport",
      label: "Particulier - Transport",
      description: "Je fais du transport de manière régulière",
      icon: <Car className="w-8 h-8 text-purple-600" />,
      requirements: [
        "Permis de conduire valide",
        "Photos du véhicule",
        "Assurance véhicule",
        "Contrôle technique",
        "Validation administrative"
      ]
    },
    {
      value: "occasional_transport",
      label: "Transport occasionnel",
      description: "Je souhaite transporter occasionnellement",
      icon: <Truck className="w-8 h-8 text-orange-600" />,
      requirements: [
        "Permis de conduire valide", 
        "Photos du véhicule",
        "Assurance véhicule",
        "Validation administrative"
      ]
    }
  ];

  const documentTypes = {
    authorization_transport: {
      label: "Autorisation de transport",
      description: "Document officiel d'autorisation de transport",
      icon: <FileText className="w-5 h-5" />
    },
    driving_license: {
      label: "Permis de conduire",
      description: "Permis de conduire valide (recto-verso)",
      icon: <CreditCard className="w-5 h-5" />
    },
    vehicle_photo: {
      label: "Photos du véhicule",
      description: "Photos extérieures et intérieures du véhicule",
      icon: <Camera className="w-5 h-5" />
    },
    identity_card: {
      label: "Pièce d'identité",
      description: "Carte d'identité ou passeport",
      icon: <User className="w-5 h-5" />
    }
  };

  useEffect(() => {
    if (adminView) {
      loadPendingUsers();
    }
  }, [adminView]);

  const loadPendingUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/pending-users`);
      setPendingUsers(response.data.pending_users);
    } catch (error) {
      console.error("Error loading pending users:", error);
      toast.error("Erreur lors du chargement des utilisateurs en attente");
    }
  };

  const initiateRegistration = async () => {
    if (!registrationData.phone || !registrationData.firstName || !registrationData.lastName) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        email: registrationData.email || null,
        phone: registrationData.phone,
        first_name: registrationData.firstName,
        last_name: registrationData.lastName,
        user_type: registrationData.userType,
        preferred_language: registrationData.preferredLanguage
      };

      // Add type-specific fields
      if (registrationData.userType === "agency") {
        payload.agency_name = registrationData.agencyName;
        payload.agency_address = registrationData.agencyAddress;
        payload.agency_license_number = registrationData.agencyLicenseNumber;
      }

      if (["individual_transport", "occasional_transport"].includes(registrationData.userType)) {
        payload.driving_license_number = registrationData.drivingLicenseNumber;
        payload.driving_license_expiry = registrationData.drivingLicenseExpiry;
        payload.transport_experience_years = registrationData.transportExperienceYears;
      }

      const response = await axios.post(`${API}/register/initiate`, payload);
      
      setUserId(response.data.user_id);
      setRegistrationStatus(response.data.registration_status);
      
      if (response.data.next_step === "verify_contact") {
        setCurrentStep("verification");
      } else {
        setCurrentStep("documents");
      }
      
      toast.success(response.data.message);
    } catch (error) {
      console.error("Registration error:", error);
      toast.error(error.response?.data?.detail || "Erreur lors de l'inscription");
    } finally {
      setLoading(false);
    }
  };

  const verifyCode = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      toast.error("Veuillez saisir le code de validation à 6 chiffres");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API}/register/verify?user_id=${userId}&code=${verificationCode}`
      );
      
      if (response.data.next_step === "complete") {
        setCurrentStep("complete");
        toast.success("Inscription terminée avec succès !");
      } else {
        setCurrentStep("documents");
        toast.success("Vérification réussie. Veuillez télécharger vos documents.");
      }
    } catch (error) {
      console.error("Verification error:", error);
      toast.error(error.response?.data?.detail || "Code de validation incorrect");
    } finally {
      setLoading(false);
    }
  };

  const uploadDocument = async (documentType, file) => {
    if (!file) {
      toast.error("Veuillez sélectionner un fichier");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('user_id', userId);
      formData.append('document_type', documentType);
      formData.append('file', file);

      const response = await axios.post(`${API}/register/upload-document`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setUploadedDocuments(response.data.uploaded_documents);
      toast.success(`Document ${documentTypes[documentType].label} téléchargé avec succès`);

      if (response.data.all_required_uploaded) {
        setCurrentStep("waitingApproval");
        toast.info("Tous les documents requis ont été téléchargés. En attente d'approbation.");
      }
    } catch (error) {
      console.error("Upload error:", error);
      toast.error(error.response?.data?.detail || "Erreur lors du téléchargement");
    } finally {
      setLoading(false);
    }
  };

  const approveUser = async (userId, notes = "") => {
    setLoading(true);
    try {
      await axios.post(`${API}/admin/approve-user?user_id=${userId}&admin_id=admin123&notes=${notes}`);
      toast.success("Utilisateur approuvé avec succès");
      loadPendingUsers();
      setSelectedUser(null);
    } catch (error) {
      console.error("Approval error:", error);
      toast.error("Erreur lors de l'approbation");
    } finally {
      setLoading(false);
    }
  };

  const rejectUser = async (userId, reason) => {
    if (!reason.trim()) {
      toast.error("Veuillez fournir une raison pour le rejet");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/admin/reject-user?user_id=${userId}&admin_id=admin123&reason=${encodeURIComponent(reason)}`);
      toast.success("Utilisateur rejeté");
      loadPendingUsers();
      setSelectedUser(null);
    } catch (error) {
      console.error("Rejection error:", error);
      toast.error("Erreur lors du rejet");
    } finally {
      setLoading(false);
    }
  };

  const getRequiredDocuments = (userType) => {
    switch (userType) {
      case "agency":
        return ["authorization_transport", "identity_card"];
      case "individual_transport":
      case "occasional_transport":
        return ["driving_license", "vehicle_photo", "identity_card"];
      default:
        return [];
    }
  };

  const getStepProgress = () => {
    const steps = {
      userType: 0,
      basicInfo: 25,
      verification: 50,
      documents: 75,
      waitingApproval: 90,
      complete: 100
    };
    return steps[currentStep] || 0;
  };

  if (adminView) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="container mx-auto max-w-7xl">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold">Administration - Validation des inscriptions</h1>
            <Button onClick={() => setAdminView(false)} variant="outline">
              Retour utilisateur
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Pending Users List */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-5 h-5" />
                    Utilisateurs en attente ({pendingUsers.length})
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {pendingUsers.map((user) => (
                    <Card 
                      key={user.id}
                      className={`cursor-pointer transition-all ${
                        selectedUser?.id === user.id ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:shadow-md'
                      }`}
                      onClick={() => setSelectedUser(user)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                          {userTypes.find(t => t.value === user.user_type)?.icon}
                          <div>
                            <div className="font-semibold">{user.first_name} {user.last_name}</div>
                            <div className="text-sm text-gray-600 capitalize">{user.user_type.replace('_', ' ')}</div>
                            {user.agency_name && (
                              <div className="text-xs text-blue-600">{user.agency_name}</div>
                            )}
                          </div>
                        </div>
                        <div className="mt-2 flex justify-between text-xs text-gray-500">
                          <span>{user.documents?.length || 0} documents</span>
                          <span>{new Date(user.created_at).toLocaleDateString()}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}

                  {pendingUsers.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <CheckCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p>Aucun utilisateur en attente</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Selected User Details */}
            <div className="lg:col-span-2">
              {selectedUser ? (
                <Card>
                  <CardHeader>
                    <CardTitle>
                      Validation de {selectedUser.first_name} {selectedUser.last_name}
                    </CardTitle>
                    <CardDescription>
                      {userTypes.find(t => t.value === selectedUser.user_type)?.label}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* User Info */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label>Informations personnelles</Label>
                        <div className="bg-gray-50 p-3 rounded-lg mt-2">
                          <div className="text-sm space-y-1">
                            <div><strong>Nom:</strong> {selectedUser.first_name} {selectedUser.last_name}</div>
                            <div><strong>Téléphone:</strong> {selectedUser.phone}</div>
                            <div><strong>Email:</strong> {selectedUser.email || "Non fourni"}</div>
                            <div><strong>Inscrit le:</strong> {new Date(selectedUser.created_at).toLocaleString()}</div>
                          </div>
                        </div>
                      </div>

                      {selectedUser.user_type === "agency" && (
                        <div>
                          <Label>Informations agence</Label>
                          <div className="bg-gray-50 p-3 rounded-lg mt-2">
                            <div className="text-sm space-y-1">
                              <div><strong>Nom:</strong> {selectedUser.agency_name}</div>
                              <div><strong>Adresse:</strong> {selectedUser.agency_address}</div>
                              <div><strong>N° Licence:</strong> {selectedUser.agency_license_number}</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {["individual_transport", "occasional_transport"].includes(selectedUser.user_type) && (
                        <div>
                          <Label>Informations transport</Label>
                          <div className="bg-gray-50 p-3 rounded-lg mt-2">
                            <div className="text-sm space-y-1">
                              <div><strong>Permis N°:</strong> {selectedUser.driving_license_number}</div>
                              <div><strong>Expiration:</strong> {selectedUser.driving_license_expiry}</div>
                              <div><strong>Expérience:</strong> {selectedUser.transport_experience_years} ans</div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Documents */}
                    <div>
                      <Label>Documents téléchargés ({selectedUser.documents?.length || 0})</Label>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
                        {selectedUser.documents?.map((doc) => (
                          <Card key={doc.id} className="bg-white">
                            <CardContent className="p-4">
                              <div className="flex items-center gap-3">
                                {documentTypes[doc.document_type]?.icon}
                                <div className="flex-1">
                                  <div className="font-semibold text-sm">
                                    {documentTypes[doc.document_type]?.label}
                                  </div>
                                  <div className="text-xs text-gray-600">
                                    {doc.file_name} • {(doc.file_size / 1024).toFixed(1)} KB
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    {new Date(doc.uploaded_at).toLocaleString()}
                                  </div>
                                </div>
                                <Button size="sm" variant="outline">
                                  <Eye className="w-3 h-3" />
                                </Button>
                              </div>
                            </CardContent>
                          </Card>
                        )) || (
                          <div className="col-span-2 text-center py-4 text-gray-500">
                            Aucun document téléchargé
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Admin Actions */}
                    <div>
                      <Label>Notes administratives</Label>
                      <Textarea
                        placeholder="Notes concernant cette validation..."
                        value={adminNotes}
                        onChange={(e) => setAdminNotes(e.target.value)}
                        className="mt-2"
                      />
                    </div>

                    <div className="flex gap-4">
                      <Button
                        onClick={() => rejectUser(selectedUser.id, adminNotes)}
                        variant="destructive"
                        disabled={loading}
                        className="flex-1"
                      >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <ThumbsDown className="w-4 h-4 mr-2" />}
                        Rejeter
                      </Button>
                      <Button
                        onClick={() => approveUser(selectedUser.id, adminNotes)}
                        disabled={loading}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                      >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <ThumbsUp className="w-4 h-4 mr-2" />}
                        Approuver
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card className="h-96 flex items-center justify-center">
                  <div className="text-center text-gray-500">
                    <Users className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <p>Sélectionnez un utilisateur à examiner</p>
                  </div>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="container mx-auto max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Inscription BusConnect</h1>
          <p className="text-gray-600">Rejoignez la plateforme de transport du Cameroun</p>
          
          <div className="mt-6">
            <Progress value={getStepProgress()} className="w-full max-w-md mx-auto" />
            <p className="text-sm text-gray-500 mt-2">Étape {getStepProgress()}%</p>
          </div>

          <Button 
            onClick={() => setAdminView(true)} 
            variant="ghost" 
            size="sm"
            className="mt-4"
          >
            <Settings className="w-4 h-4 mr-2" />
            Accès Admin
          </Button>
        </div>

        {/* Step 1: User Type Selection */}
        {currentStep === "userType" && (
          <Card>
            <CardHeader>
              <CardTitle>Quel est votre profil ?</CardTitle>
              <CardDescription>Choisissez le type de compte qui correspond à votre situation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {userTypes.map((type) => (
                  <Card 
                    key={type.value}
                    className={`cursor-pointer transition-all hover:shadow-lg ${
                      registrationData.userType === type.value 
                        ? 'ring-2 ring-blue-500 bg-blue-50' 
                        : 'hover:bg-gray-50'
                    }`}
                    onClick={() => setRegistrationData({...registrationData, userType: type.value})}
                  >
                    <CardContent className="p-6">
                      <div className="text-center mb-4">
                        {type.icon}
                        <h3 className="font-bold text-lg mt-2">{type.label}</h3>
                        <p className="text-sm text-gray-600 mt-2">{type.description}</p>
                      </div>
                      
                      <div className="border-t pt-4">
                        <div className="text-xs font-semibold text-gray-700 mb-2">Documents requis:</div>
                        <ul className="text-xs text-gray-600 space-y-1">
                          {type.requirements.map((req, idx) => (
                            <li key={idx} className="flex items-center gap-2">
                              <CheckCircle className="w-3 h-3 text-green-600" />
                              {req}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {registrationData.userType && (
                <div className="mt-6 text-center">
                  <Button 
                    onClick={() => setCurrentStep("basicInfo")}
                    className="bg-blue-600 hover:bg-blue-700"
                    size="lg"
                  >
                    Continuer avec "{userTypes.find(t => t.value === registrationData.userType)?.label}"
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Step 2: Basic Information */}
        {currentStep === "basicInfo" && (
          <Card>
            <CardHeader>
              <CardTitle>Informations personnelles</CardTitle>
              <CardDescription>
                Veuillez remplir vos informations de base
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="firstName">Prénom *</Label>
                  <Input
                    id="firstName"
                    value={registrationData.firstName}
                    onChange={(e) => setRegistrationData({...registrationData, firstName: e.target.value})}
                    placeholder="Votre prénom"
                  />
                </div>
                
                <div>
                  <Label htmlFor="lastName">Nom de famille *</Label>
                  <Input
                    id="lastName"
                    value={registrationData.lastName}
                    onChange={(e) => setRegistrationData({...registrationData, lastName: e.target.value})}
                    placeholder="Votre nom de famille"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="phone">Numéro de téléphone *</Label>
                  <div className="flex">
                    <div className="bg-gray-100 px-3 py-2 rounded-l-md border border-r-0 text-sm">+237</div>
                    <Input
                      id="phone"
                      value={registrationData.phone}
                      onChange={(e) => setRegistrationData({...registrationData, phone: e.target.value})}
                      placeholder="6XX XXX XXX"
                      className="rounded-l-none"
                    />
                  </div>
                  <div className="text-xs text-gray-600 mt-1 flex items-center gap-1">
                    <Smartphone className="w-3 h-3" />
                    Recevra le code de validation SMS
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="email">Adresse email (optionnel)</Label>
                  <Input
                    id="email"
                    type="email"
                    value={registrationData.email}
                    onChange={(e) => setRegistrationData({...registrationData, email: e.target.value})}
                    placeholder="votre@email.com"
                  />
                  <div className="text-xs text-gray-600 mt-1 flex items-center gap-1">
                    <Mail className="w-3 h-3" />
                    Alternative si SMS indisponible
                  </div>
                </div>
              </div>

              {/* Agency specific fields */}
              {registrationData.userType === "agency" && (
                <Card className="bg-green-50 border-green-200">
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Building className="w-5 h-5" />
                      Informations de l'agence
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="agencyName">Nom de l'agence *</Label>
                      <Input
                        id="agencyName"
                        value={registrationData.agencyName}
                        onChange={(e) => setRegistrationData({...registrationData, agencyName: e.target.value})}
                        placeholder="Nom officiel de l'agence"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="agencyAddress">Adresse de l'agence *</Label>
                      <Textarea
                        id="agencyAddress"
                        value={registrationData.agencyAddress}
                        onChange={(e) => setRegistrationData({...registrationData, agencyAddress: e.target.value})}
                        placeholder="Adresse complète de l'agence"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="agencyLicense">Numéro de licence (si disponible)</Label>
                      <Input
                        id="agencyLicense"
                        value={registrationData.agencyLicenseNumber}
                        onChange={(e) => setRegistrationData({...registrationData, agencyLicenseNumber: e.target.value})}
                        placeholder="Numéro d'autorisation de transport"
                      />
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Transport provider fields */}
              {["individual_transport", "occasional_transport"].includes(registrationData.userType) && (
                <Card className="bg-purple-50 border-purple-200">
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Car className="w-5 h-5" />
                      Informations de transport
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="licenseNumber">Numéro de permis de conduire *</Label>
                        <Input
                          id="licenseNumber"
                          value={registrationData.drivingLicenseNumber}
                          onChange={(e) => setRegistrationData({...registrationData, drivingLicenseNumber: e.target.value})}
                          placeholder="Numéro du permis"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="licenseExpiry">Date d'expiration du permis *</Label>
                        <Input
                          id="licenseExpiry"
                          type="date"
                          value={registrationData.drivingLicenseExpiry}
                          onChange={(e) => setRegistrationData({...registrationData, drivingLicenseExpiry: e.target.value})}
                        />
                      </div>
                    </div>
                    
                    <div>
                      <Label htmlFor="experience">Années d'expérience en transport</Label>
                      <Select onValueChange={(value) => setRegistrationData({...registrationData, transportExperienceYears: parseInt(value)})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Sélectionnez votre expérience" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="0">Débutant (moins d'1 an)</SelectItem>
                          <SelectItem value="1">1-2 ans</SelectItem>
                          <SelectItem value="3">3-5 ans</SelectItem>
                          <SelectItem value="6">6-10 ans</SelectItem>
                          <SelectItem value="11">Plus de 10 ans</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </CardContent>
                </Card>
              )}

              <div className="flex gap-4">
                <Button 
                  variant="outline" 
                  onClick={() => setCurrentStep("userType")}
                  className="flex-1"
                >
                  Retour
                </Button>
                <Button 
                  onClick={initiateRegistration}
                  disabled={loading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                  Continuer
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Verification */}
        {currentStep === "verification" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Vérification de contact
              </CardTitle>
              <CardDescription>
                Saisissez le code de validation reçu par SMS ou email
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  Un code de validation à 6 chiffres a été envoyé à votre numéro de téléphone. 
                  Si vous ne le recevez pas dans les 5 minutes, vérifiez votre boîte email.
                </AlertDescription>
              </Alert>

              <div className="max-w-sm mx-auto">
                <Label htmlFor="code">Code de validation</Label>
                <Input
                  id="code"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder="000000"
                  maxLength={6}
                  className="text-center text-2xl tracking-widest"
                />
              </div>

              <div className="text-center space-y-4">
                <Button 
                  onClick={verifyCode}
                  disabled={loading || verificationCode.length !== 6}
                  className="bg-green-600 hover:bg-green-700"
                  size="lg"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <CheckCircle className="w-4 h-4 mr-2" />}
                  Vérifier le code
                </Button>

                <div>
                  <Button variant="ghost" size="sm" className="text-blue-600">
                    Renvoyer le code
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 4: Document Upload */}
        {currentStep === "documents" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="w-5 h-5" />
                Téléchargement de documents
              </CardTitle>
              <CardDescription>
                Veuillez télécharger tous les documents requis pour validation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {getRequiredDocuments(registrationData.userType).map((docType) => (
                <Card key={docType} className="bg-gray-50">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className="bg-white p-2 rounded-lg">
                        {documentTypes[docType]?.icon}
                      </div>
                      
                      <div className="flex-1">
                        <h4 className="font-semibold">{documentTypes[docType]?.label}</h4>
                        <p className="text-sm text-gray-600 mb-3">{documentTypes[docType]?.description}</p>
                        
                        <div className="flex items-center gap-3">
                          <input
                            type="file"
                            id={`file-${docType}`}
                            accept=".jpg,.jpeg,.png,.pdf"
                            onChange={(e) => {
                              const file = e.target.files[0];
                              if (file) uploadDocument(docType, file);
                            }}
                            className="hidden"
                          />
                          
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => document.getElementById(`file-${docType}`).click()}
                          >
                            <Upload className="w-3 h-3 mr-2" />
                            Choisir fichier
                          </Button>
                          
                          {uploadedDocuments.includes(docType) && (
                            <Badge className="bg-green-100 text-green-800">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Téléchargé
                            </Badge>
                          )}
                        </div>
                        
                        <div className="text-xs text-gray-500 mt-2">
                          Formats acceptés: JPG, PNG, PDF • Taille max: 5MB
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}

              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Assurez-vous que tous les documents sont lisibles et de bonne qualité. 
                  Les documents flous ou illisibles seront rejetés.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        )}

        {/* Step 5: Waiting for Approval */}
        {currentStep === "waitingApproval" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-yellow-600" />
                En attente d'approbation
              </CardTitle>
              <CardDescription>
                Votre dossier est en cours de révision par notre équipe
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 text-center">
              <div className="bg-yellow-50 p-8 rounded-lg">
                <Clock className="w-16 h-16 mx-auto text-yellow-600 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Dossier en révision</h3>
                <p className="text-gray-600">
                  Notre équipe examine votre dossier et vos documents. 
                  Vous recevrez une notification dans les 24-48h.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="bg-blue-100 p-3 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                    <FileText className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="text-sm font-semibold">Documents reçus</div>
                  <div className="text-xs text-gray-600">Tous vos documents ont été téléchargés</div>
                </div>
                
                <div className="text-center">
                  <div className="bg-yellow-100 p-3 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                    <Eye className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div className="text-sm font-semibold">En cours d'examen</div>
                  <div className="text-xs text-gray-600">Vérification en cours</div>
                </div>
                
                <div className="text-center">
                  <div className="bg-gray-100 p-3 rounded-full w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-gray-400" />
                  </div>
                  <div className="text-sm font-semibold text-gray-400">Approbation</div>
                  <div className="text-xs text-gray-400">En attente</div>
                </div>
              </div>

              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Que se passe-t-il ensuite ?</strong><br />
                  • Notre équipe vérifie vos documents<br />
                  • Vous recevez une notification par SMS/Email<br />
                  • Si approuvé, vous pourrez utiliser la plateforme<br />
                  • Si des corrections sont nécessaires, nous vous contacterons
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        )}

        {/* Step 6: Complete */}
        {currentStep === "complete" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-600">
                <CheckCircle className="w-5 h-5" />
                Inscription terminée !
              </CardTitle>
              <CardDescription>
                Bienvenue dans la communauté BusConnect Cameroun
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 text-center">
              <div className="bg-green-50 p-8 rounded-lg">
                <CheckCircle className="w-16 h-16 mx-auto text-green-600 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Félicitations !</h3>
                <p className="text-gray-600">
                  Votre compte client a été créé avec succès. 
                  Vous pouvez maintenant rechercher et réserver vos trajets.
                </p>
              </div>

              <Button 
                className="bg-blue-600 hover:bg-blue-700" 
                size="lg"
                onClick={() => window.location.href = "/"}
              >
                Commencer à utiliser BusConnect
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default RegistrationSystem;