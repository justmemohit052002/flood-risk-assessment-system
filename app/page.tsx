"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Globe, MapPin, Shield, Image as ImageIcon, UploadIcon, Camera, TrendingUp, Loader2, Map } from "lucide-react";
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { useRef, useState, useEffect } from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

export default function Home() {

  const [imagePreview, setImagePreview] = useState<string>("");

  const [selectedImage, setSelectedImage] = useState<File | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const [showAlert, setShowAlert] = useState(false);

  const [alertMessage, setAlertMessage] = useState('');


  const [isLoading, setIsLoading] = useState(false);

  const [analysisType, setAnalysisType] = useState<'coordinates' | 'image'>('coordinates');


  const [map, setMap] = useState<null>(null);

  const [mapError, setMapError] = useState(true);

  const mapRef = useRef<HTMLDivElement>(null);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024 || !file.type.startsWith("image/")) {
        setAlertMessage(file.size > 10 * 1024 * 1024 ? 'Image size must be less than 10MB' : 'Please select a valid image file');
        setShowAlert(true);
        return;
      }

      setSelectedImage(file);

      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target?.result as string);
      reader.readAsDataURL(file);
    }
  }

  return (
    <div className="min-h-screen bg-background-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">

          <div className="flex items-center justify-center">
            <div className="p-3 bg-blue-100 rounded-full mr-4">
              <Globe className="h-8 w-8 text-blue-600" />
            </div>
            <h1 className="text-3xl font-bold text-slate-900">Flood Detection System</h1>
          </div>
          <p className="text-slate-600">Analyze flood risk using coordinates or upload images for AI-powered terrain analysis</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* input section */}
          
          {/* Card */}

          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className='flex items-center gap-2'>
                <Shield className="h-5 w-5 text-blue-600"></Shield>
                Analyze Flood Risk
              </CardTitle>
            </CardHeader>

            <CardContent>
              <Tabs>
                <TabsList>
                  <TabsTrigger value="coordinates" className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    Coordinates
                  </TabsTrigger>
                  <TabsTrigger value="image" className="flex items-center gap-2">
                    <ImageIcon className="h-4 w-4" />
                    Image Analysis
                  </TabsTrigger>
                </TabsList>


                <TabsContent value="coordinates" className="mt-4 space-y-4">

                  <div className="gird grid cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="latitude">Latitude</Label>
                      <Input type="number" id="latitude" placeholder="Enter latitude"/>
                    </div>
                  </div>

                   <div className="gird grid cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="latitude">Longitude</Label>
                      <Input type="number" id="latitude" placeholder="Enter longitude"/>
                    </div>
                  </div>

                  {/* Button */}

                  <Button 
                    className="w-full" 
                    onClick={() => {
                      setAnalysisType('coordinates');
                      setIsLoading(true);
                      // Add your coordinate analysis logic here
                      setTimeout(() => setIsLoading(false), 3000); // Simulate API call
                    }}
                  > 
                    <MapPin className="mr-2 h-4 w-4"/> Analyze Coordinates
                  </Button>
                </TabsContent>

                <TabsContent value="image" className="mt-4 space-y-4">
                  <div className="space-y-4">
                    <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center" >

                      <input ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleImageUpload}
                        className="hidden"
                      />
                      {!imagePreview ? (
                        <div className="space-y-4">
                          <UploadIcon
                            className="h-12
                          w-12 mx-auto
                          text-slate-400
                            "
                          />
                          <div>
                          
                          <p className="text-sm font-medium text-slate-700">Upload terrain image</p>
                          <p className="text-xs text-slate-500 mt-1"> JPG, PNG, or GIF to 10MB</p>
                          </div>
                          <Button
                            onClick={() =>
                              fileInputRef.current?.click()
                          }
                            variant="outline"
                            size="sm"
                             
                          >
                            {" "}
                            <Camera
                            className="mr-2 h-4 w-4 "
                            />
                            Choose Image
                          </Button>
                        </div>
                      ): (
                          <div className="space-y-4">

                            <img src={imagePreview}
                              alt="Preview"
                              className="max-h-48
                              mx-auto rounded-lg
                              shadow-sm "
                            />
                          </div>
                      )}
                    </div>

                    <Button onClick={() => { }} className="w-full">
                      <ImageIcon className="mr-2 h-4 w-4" />
                      Analyze Image
                    </Button>
                  </div>
                </TabsContent>

              </Tabs>
            </CardContent>
          </Card>


          {/* result sections */}

          <Card className="shadow-lg border-0
          bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className='flex items-center gap-2'>
                <TrendingUp className="h-5 w-5 text-green-600"/>
                Risk Assessment
              </CardTitle>
            </CardHeader>

            <CardContent>
              {/* isLoading */}
              {isLoading && (
                <div className="flex flex-col
                items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-600 mb-4" />
                                     <p className="text-slate-600">
                     {analysisType === 'coordinates' ? 'Analyzing coordinates...' : 'Analyzing image...'}
                   </p>
                </div>
              )}

               
            </CardContent>
          </Card>
        </div>

        {/* Map area */}

        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5 text-green-600" />
              Interactive Map
            </CardTitle>
          </CardHeader>
          <CardContent>
            {mapError ? (
              <div className="w-full h-80 rounded-lg border border-slate-200 bg-slate-50 flex flex-col items-center justify-center">
                <Map className="h-16 w-16 text-slate-300 mb-4" />
                <h3 className="text-lg font-semibold text-slate-700 mb-2">Map Not Avaialable</h3>

                <p className="text-slate-500 text-center max-w-d"> To enable the interactive map, set up a Google Maps API key in .enev.local </p>
            </div>
            ) : (
                <div ref={mapRef} className="w-full h-80 rounded-lg border border-slate-200" />
            )}
          </CardContent>

        </Card>

      </div>

      {/* alert dialog */}

      <AlertDialog open={showAlert} onOpenChange={setShowAlert}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Input Error</AlertDialogTitle>
            <AlertDialogDescription>{alertMessage}</AlertDialogDescription>
          </AlertDialogHeader>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
