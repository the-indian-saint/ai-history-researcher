import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { Card } from "@/components/ui/card";
import L from "leaflet";

// Fix for default marker icons in React Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

export interface GeoLocation {
    name: string;
    coordinates: number[]; // [lat, long]
    description: string;
    type: string;
}

interface HistoricalMapProps {
    locations: GeoLocation[];
}

export function HistoricalMap({ locations }: HistoricalMapProps) {
    // Default center (India)
    const center: [number, number] = [20.5937, 78.9629];
    const zoom = 5;

    if (!locations || locations.length === 0) {
        return (
            <div className="h-[400px] w-full bg-muted/20 flex items-center justify-center rounded-lg border">
                <p className="text-muted-foreground">No geographical data found for this period.</p>
            </div>
        );
    }

    return (
        <Card className="overflow-hidden border-primary/20 shadow-inner">
            <div className="h-[500px] w-full z-0 relative">
                <MapContainer
                    center={locations[0]?.coordinates as [number, number] || center}
                    zoom={zoom}
                    scrollWheelZoom={false}
                    style={{ height: "100%", width: "100%" }}
                >
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        className="map-tiles"
                    />
                    {locations.map((loc, idx) => (
                        <Marker key={idx} position={loc.coordinates as [number, number]}>
                            <Popup>
                                <div className="font-heading font-bold text-sm">{loc.name}</div>
                                <div className="text-xs text-muted-foreground mt-1 capitalize">{loc.type}</div>
                                <p className="text-xs mt-2">{loc.description}</p>
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>
            </div>
            <div className="p-2 bg-muted/30 text-xs text-center text-muted-foreground">
                Displaying {locations.length} historical locations
            </div>
        </Card>
    );
}
