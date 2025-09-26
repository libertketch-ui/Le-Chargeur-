import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { Button } from "./components/ui/button";
import { Badge } from "./components/ui/badge";
import { 
  Smartphone, 
  Copy, 
  CheckCircle, 
  ArrowLeft,
  Phone,
  CreditCard
} from "lucide-react";

const PaymentKeypad = ({ paymentInfo, onClose, onComplete }) => {
  const [enteredAmount, setEnteredAmount] = useState("");
  const [step, setStep] = useState("display"); // display, confirm, success

  const keypadNumbers = [
    ['1', '2', '3'],
    ['4', '5', '6'], 
    ['7', '8', '9'],
    ['*', '0', '#']
  ];

  const handleKeyPress = (key) => {
    if (key === '*') {
      setEnteredAmount("");
    } else if (key === '#') {
      if (enteredAmount === paymentInfo.amount_to_pay_now.toString()) {
        setStep("confirm");
      }
    } else {
      setEnteredAmount(prev => prev + key);
    }
  };

  const confirmPayment = () => {
    setStep("success");
    setTimeout(() => {
      onComplete();
    }, 2000);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR').format(price);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-md">
        <CardHeader className={`text-center ${
          paymentInfo.provider === 'MTN' 
            ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' 
            : 'bg-gradient-to-r from-orange-500 to-orange-600'
        } text-white`}>
          <div className="flex items-center justify-between">
            <Button variant="ghost" size="sm" onClick={onClose} className="text-white">
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div className="flex items-center gap-2">
              {paymentInfo.provider === 'MTN' ? (
                <div className="w-8 h-8 bg-yellow-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-xs">MTN</span>
                </div>
              ) : (
                <div className="w-8 h-8 bg-orange-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-xs">OM</span>
                </div>
              )}
              <CardTitle className="text-lg">
                {paymentInfo.provider === 'MTN' ? 'MTN Mobile Money' : 'Orange Money'}
              </CardTitle>
            </div>
            <div className="w-6"></div>
          </div>
        </CardHeader>
        
        <CardContent className="p-6">
          {step === "display" && (
            <>
              {/* Payment Information */}
              <div className="text-center mb-6">
                <div className="bg-gray-100 p-4 rounded-lg mb-4">
                  <div className="text-sm text-gray-600 mb-1">Code Marchand Entreprise</div>
                  <div className="text-2xl font-bold text-blue-600 flex items-center justify-center gap-2">
                    {paymentInfo.merchant_code}
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => navigator.clipboard.writeText(paymentInfo.merchant_code)}
                    >
                      <Copy className="w-3 h-3" />
                    </Button>
                  </div>
                </div>

                <div className="text-sm text-gray-600 mb-2">Montant à payer</div>
                <div className="text-3xl font-bold text-green-600">
                  {formatPrice(paymentInfo.amount_to_pay_now)} FCFA
                </div>
              </div>

              {/* Instructions */}
              <div className="bg-blue-50 p-4 rounded-lg mb-6">
                <div className="text-sm text-blue-800">
                  <div className="font-semibold mb-2">Instructions:</div>
                  <div className="space-y-1">
                    <div>1. Composez {paymentInfo.ussd_code}</div>
                    <div>2. Sélectionnez "Paiement marchand"</div>
                    <div>3. Saisissez le code: {paymentInfo.merchant_code}</div>
                    <div>4. Confirmez le montant: {formatPrice(paymentInfo.amount_to_pay_now)} FCFA</div>
                  </div>
                </div>
              </div>

              {/* Keypad */}
              <div>
                <div className="text-center mb-4">
                  <div className="text-lg font-semibold">Saisissez le montant</div>
                  <div className="text-2xl font-mono bg-gray-100 p-3 rounded-lg mt-2">
                    {enteredAmount || "0"} FCFA
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  {keypadNumbers.flat().map((key) => (
                    <Button
                      key={key}
                      variant="outline"
                      className="h-14 text-xl font-semibold"
                      onClick={() => handleKeyPress(key)}
                    >
                      {key}
                    </Button>
                  ))}
                </div>

                <div className="text-center text-xs text-gray-500 mt-4">
                  * = Effacer | # = Confirmer
                </div>
              </div>
            </>
          )}

          {step === "confirm" && (
            <div className="text-center space-y-6">
              <CheckCircle className="w-16 h-16 text-green-600 mx-auto" />
              <div>
                <h3 className="text-lg font-semibold mb-2">Confirmer le paiement</h3>
                <p className="text-gray-600">
                  Vous vous apprêtez à payer {formatPrice(paymentInfo.amount_to_pay_now)} FCFA
                </p>
              </div>
              
              <div className="flex gap-4">
                <Button variant="outline" onClick={() => setStep("display")} className="flex-1">
                  Retour
                </Button>
                <Button onClick={confirmPayment} className="flex-1 bg-green-600 hover:bg-green-700">
                  Confirmer
                </Button>
              </div>
            </div>
          )}

          {step === "success" && (
            <div className="text-center space-y-6">
              <CheckCircle className="w-16 h-16 text-green-600 mx-auto animate-pulse" />
              <div>
                <h3 className="text-lg font-semibold mb-2 text-green-600">Paiement Réussi !</h3>
                <p className="text-gray-600">
                  Votre réservation est confirmée
                </p>
                <div className="bg-green-50 p-3 rounded-lg mt-4">
                  <div className="text-sm">
                    Référence: <span className="font-mono font-bold">{paymentInfo.booking_reference}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentKeypad;