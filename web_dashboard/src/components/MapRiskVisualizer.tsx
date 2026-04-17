import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Shield, MapPin, Activity, Layers, Info } from 'lucide-react';
import './MapRiskVisualizer.css';

interface MapProps {
    showZones?: boolean;
    showLocations?: boolean;
    onFeatureSelect?: (feature: any) => void;
    onStatsReady?: (stats: any) => void;
}

const MapRiskVisualizer: React.FC<MapProps> = ({ 
    showZones = true, 
    showLocations = true,
    onFeatureSelect,
    onStatsReady
}) => {
    const [geoMap, setGeoMap] = useState<any>(null);
    const [geoLocs, setGeoLocs] = useState<any>(null);
    const [communeData, setCommuneData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchGeo = async () => {
            try {
                const [mapRes, locsRes, rpaRes] = await Promise.all([
                    fetch('http://localhost:8000/api/geo/map'),
                    fetch('http://localhost:8000/api/geo/locations'),
                    fetch('/communes_rpa_full.json')
                ]);
                const mapJson = await mapRes.json();
                const locsJson = await locsRes.json();
                const rpaJson = await rpaRes.json();
                
                if (mapJson && !mapJson.error) setGeoMap(mapJson);
                if (locsJson && !locsJson.error) setGeoLocs(locsJson);
                if (rpaJson) setCommuneData(rpaJson);

                // Calculate Intelligence Stats via Full Portfolio Audit
                if (mapJson && locsJson && rpaJson && onStatsReady) {
                    const exposure_breakdown: any = { III: 0, II: 0, I: 0, '0': 0 };
                    
                    // Audit every single one of the 3,182 asset points
                    locsJson.features?.forEach((loc: any) => {
                        // Helper to find zone for this loc
                        const info = getPinpointZoneLocally(loc, mapJson, rpaJson);
                        if (info) {
                            const z = info.zone;
                            if (z === '3' || z === 'III') exposure_breakdown.III++;
                            else if (z === '2' || z === 'II' || z === 'IIb' || z === 'IIa') exposure_breakdown.II++;
                            else if (z === '1' || z === 'I') exposure_breakdown.I++;
                            else exposure_breakdown['0']++;
                        }
                    });

                    const stats = {
                        total_policies: locsJson.features?.length || 0,
                        total_zones: mapJson.features?.length || 0,
                        by_zone: exposure_breakdown, // Distribute based on asset density
                        exposure_breakdown
                    };
                    onStatsReady(stats);
                }
            } catch (err) {
                console.error("Geo fetch failed", err);
            } finally {
                setLoading(false);
            }
        };
        fetchGeo();
    }, []);

    // Local helper for initial audit (avoids dependency issue in useEffect)
    const getPinpointZoneLocally = (feature: any, map: any, rpa: any) => {
        if (!map || !feature.geometry || !rpa) return null;
        const coords = feature.geometry.coordinates;
        const communeName = normalizeName(feature.properties?.NAME || "");
        
        let detectedWilayaRaw = null;
        for (const wilaya of map.features) {
            const geometries = wilaya.geometry.type === "Polygon" ? [wilaya.geometry.coordinates] : wilaya.geometry.coordinates;
            for (const shape of geometries) {
                const polygon = wilaya.geometry.type === "Polygon" ? shape : shape[0];
                if (isPointInPoly(coords, polygon)) {
                    detectedWilayaRaw = wilaya.properties.NAME_1;
                    break;
                }
            }
            if (detectedWilayaRaw) break;
        }

        if (!detectedWilayaRaw) return null;
        const detectedWilaya = normalizeName(detectedWilayaRaw);
        const wilayaEntry = rpa[detectedWilaya];
        if (wilayaEntry) {
            if (wilayaEntry.groups) {
                for (const [zone, communes] of Object.entries(wilayaEntry.groups)) {
                    if ((communes as string[]).some(c => normalizeName(c) === communeName)) return { zone, wilaya: detectedWilaya };
                }
            }
            return { zone: wilayaEntry.default, wilaya: detectedWilaya };
        }
        return null;
    };



    const normalizeName = (name: string) => {
        if (!name) return "";
        return name.toUpperCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "") // Remove accents
            .replace(/-/g, " ")
            .replace(/[^A-Z0-9 ]/g, "") // Strip Arabic and special chars
            .replace(/\s+/g, " ") // Multi-space to single
            .trim();
    };

    const isPointInPoly = (point: number[], vs: any[]) => {
        const x = point[0], y = point[1];
        let inside = false;
        for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
            const xi = vs[i][0], yi = vs[i][1];
            const xj = vs[j][0], yj = vs[j][1];
            const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
            if (intersect) inside = !inside;
        }
        return inside;
    };

    const getCommuneZone = (feature: any) => {
        if (!geoMap || !feature.geometry || !communeData) return null;
        const coords = feature.geometry.coordinates;
        const communeName = normalizeName(feature.properties?.NAME || "");
        
        let detectedWilayaRaw = null;
        for (const wilaya of geoMap.features) {
            if (!wilaya.geometry) continue;
            const geometries = wilaya.geometry.type === "Polygon" ? [wilaya.geometry.coordinates] : wilaya.geometry.coordinates;
            for (const shape of geometries) {
                const polygon = wilaya.geometry.type === "Polygon" ? shape : shape[0];
                if (isPointInPoly(coords, polygon)) {
                    detectedWilayaRaw = wilaya.properties.NAME_1;
                    break;
                }
            }
            if (detectedWilayaRaw) break;
        }

        if (!detectedWilayaRaw) return null;
        const detectedWilaya = normalizeName(detectedWilayaRaw);
        const wilayaEntry = communeData[detectedWilaya];
                           
        if (wilayaEntry) {
            if (wilayaEntry.groups) {
                for (const [zone, communes] of Object.entries(wilayaEntry.groups)) {
                    if ((communes as string[]).some(c => normalizeName(c) === communeName)) return { zone, wilaya: detectedWilaya };
                }
            }
            return { zone: wilayaEntry.default, wilaya: detectedWilaya };
        }
        return null;
    };


    const getStyle = (feature: any) => {
        const zone = feature?.properties?.zone_rpa;
        let color = '#d1d5db'; 
        
        if (zone === 3 || zone === 'III') color = '#ef4444';
        else if (zone === 2 || zone === 'II' || zone === 'IIa' || zone === 'IIb') color = '#fbbf24';
        else if (zone === 1 || zone === 'I') color = '#22c55e';
        else if (zone === 0 || zone === '0') color = '#9ca3af';

        return {
            fillColor: color,
            weight: 0.8,
            opacity: 1,
            color: '#4b5563',
            fillOpacity: 0.6,
        };
    };

    const pointToLayer = (feature: any, latlng: L.LatLng) => {
        const resolvedInfo = getCommuneZone(feature);
        const resolvedZone = resolvedInfo?.zone;
        
        let markerColor = "white";
        const z = String(resolvedZone);
        if (z === "3" || z === "III") markerColor = "#ef4444";
        else if (z === "2" || z === "II" || z === "IIb" || z === "IIa") markerColor = "#fbbf24";
        else if (z === "1" || z === "I") markerColor = "#22c55e";

        return L.circleMarker(latlng, {
            radius: 4,
            fillColor: markerColor,
            color: "black",
            weight: 1,
            opacity: 1,
            fillOpacity: 1
        });
    };

    const onEachFeature = (feature: any, layer: any) => {
        layer.on({
            mouseover: (e: any) => {
                const target = e.target;
                target.setStyle({ fillOpacity: 0.8, weight: 2, color: '#111827' });
                if (onFeatureSelect) onFeatureSelect(feature.properties);
            },
            mouseout: (e: any) => {
                const target = e.target;
                target.setStyle(getStyle(feature));
                if (onFeatureSelect) onFeatureSelect(null);
            }
        });
        
        if (feature.properties && feature.properties.NAME_1) {
            layer.bindTooltip(`${feature.properties.NAME_1} (RPA ${feature.properties.zone_rpa})`, { sticky: true, className: 'region-tooltip' });
        }
    };

    const onEachLocation = (feature: any, layer: any) => {
        const communeName = feature.properties?.NAME;
        const resolvedInfo = getCommuneZone(feature);
        const resolvedZone = resolvedInfo?.zone;
        
        layer.on({
            click: () => {
                if (onFeatureSelect) {
                    onFeatureSelect({
                        ...feature.properties,
                        NAME_1: feature.properties.NAME,
                        zone_rpa: resolvedZone || "Check PDF",
                        is_commune: true
                    });
                }
            }
        });

        if (communeName) {
            const tooltipContent = resolvedZone 
                ? `${communeName} (Pinpoint RPA ${resolvedZone})`
                : `${communeName}`;
            layer.bindTooltip(tooltipContent, { direction: 'top', offset: [0, -5] });
        }
    };




    if (loading) {
        return (
            <div className="map-loading-card">
                <Shield className="spin" size={32} />
                <p>Decoding Geospatial Packages...</p>
            </div>
        );
    }

    return (
        <div className="map-wrapper shadow-premium">
            <div className="map-container-inner">
                <MapContainer 
                    center={[28.0, 3.0]} 
                    zoom={5} 
                    style={{ height: '100%', width: '100%' }}
                    zoomControl={true}
                >
                    <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                    />
                    {geoMap && showZones && (
                        <GeoJSON 
                            data={geoMap} 
                            style={getStyle}
                            onEachFeature={onEachFeature}
                        />
                    )}
                    {geoLocs && showLocations && (
                        <GeoJSON 
                            data={geoLocs} 
                            pointToLayer={pointToLayer}
                            onEachFeature={onEachLocation}
                        />
                    )}
                </MapContainer>
            </div>
        </div>
    );
};



export default MapRiskVisualizer;

