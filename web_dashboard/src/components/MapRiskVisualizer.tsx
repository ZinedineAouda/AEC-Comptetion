import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Shield, MapPin, Activity, Layers, Info } from 'lucide-react';
import './MapRiskVisualizer.css';

interface MapProps {
    activeLayers: any[];
    onFeatureSelect?: (feature: any) => void;
    onStatsReady?: (stats: any) => void;
}

const MapRiskVisualizer: React.FC<MapProps> = ({ 
    activeLayers = [],
    onFeatureSelect,
    onStatsReady
}) => {
    const [layerDataStore, setLayerDataStore] = useState<Record<string, any>>({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAll = async () => {
            setLoading(true);
            try {
                // Fetch basic stats from portfolio
                const statsRes = await fetch('http://localhost:8000/api/portfolio/stats');
                const statsJson = await statsRes.json();
                if (onStatsReady) onStatsReady(statsJson);
            } catch (err) {
                console.error("Stats fetch failed", err);
            } finally {
                setLoading(false);
            }
        };
        fetchAll();
    }, []);

    useEffect(() => {
        // Reactive layer fetching
        activeLayers.forEach(async (layer) => {
            if (!layerDataStore[layer.id]) {
                try {
                    const res = await fetch(`http://localhost:8000${layer.url}`);
                    const json = await res.json();
                    setLayerDataStore(prev => ({ ...prev, [layer.id]: json }));
                } catch (err) {
                    console.error(`Failed to fetch layer ${layer.id}`, err);
                }
            }
        });
    }, [activeLayers]);

    const getZoneColor = (zone: string | number) => {
        const z = String(zone).toUpperCase();
        if (z === '3' || z === 'III') return '#ef4444'; // Critical
        if (z === 'IIB') return '#f97316';               // High-Moderate
        if (z === '2' || z === 'II' || z === 'IIA') return '#fbbf24'; // Moderate
        if (z === '1' || z === 'I') return '#22c55e';    // Low
        return '#94a3b8';                                // Very Low
    };

    const getStyle = (feature: any, opacity = 0.6) => {
        const zone = feature?.properties?.zone_rpa;
        const color = getZoneColor(zone);

        return {
            fillColor: color,
            weight: 0.8,
            opacity: 1,
            color: '#4b5563',
            fillOpacity: opacity,
        };
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
                target.setStyle(getStyle(feature, layer.options.fillOpacity));
                if (onFeatureSelect) onFeatureSelect(null);
            }
        });
        
        if (feature.properties && feature.properties.NAME_1) {
            layer.bindTooltip(`${feature.properties.NAME_1} (Wilaya RPA ${feature.properties.zone_rpa})`, { sticky: true, className: 'region-tooltip' });
        }
    };

    if (loading) {
        return (
            <div className="map-loading-card">
                <Shield className="spin" size={32} />
                <p>Decoding Geospatial Packages...</p>
                <div className="sub-text">Connecting to Seismic Risk Engine...</div>
            </div>
        );
    }

    // Fallback if no layers are discovered globally
    if (activeLayers.length === 0 && !loading) {
        return (
            <div className="map-info-card">
                <Info className="text-blue-400" size={32} />
                <p>No active geospatial layers selected.</p>
                <div className="sub-text">Use the Layer Registry to project data onto the map.</div>
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
                        attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
                    />
                    
                    {activeLayers.map(layerDef => {
                        const data = layerDataStore[layerDef.id];
                        if (!data) return null;
                        
                        return (
                            <GeoJSON 
                                key={`layer-dynamic-${layerDef.id}`}
                                data={data} 
                                style={(f) => getStyle(f, layerDef.id.includes('gadm') ? 0.3 : 0.6)}
                                pointToLayer={(feature, latlng) => {
                                    const z = feature.properties?.zone_rpa || "I";
                                    const color = getZoneColor(z);
                                    return L.circleMarker(latlng, {
                                        radius: layerDef.id.includes('portfolio') ? 3 : 5,
                                        fillColor: color,
                                        color: layerDef.id.includes('portfolio') ? "#000" : "#ffffff",
                                        weight: 1,
                                        opacity: 1,
                                        fillOpacity: 0.8
                                    });
                                }}
                                onEachFeature={(feature, layer) => {
                                    layer.on({
                                        mouseover: (e: any) => {
                                            const target = e.target;
                                            if (target.setStyle) {
                                                target.setStyle({ fillOpacity: 1, weight: 2, color: '#111827' });
                                            }
                                            if (onFeatureSelect) onFeatureSelect(feature.properties);
                                        },
                                        mouseout: (e: any) => {
                                            const target = e.target;
                                            if (target.setStyle) {
                                                const z = feature.properties?.zone_rpa || "I";
                                                const color = getZoneColor(z);
                                                target.setStyle({
                                                    fillColor: color,
                                                    color: layerDef.id.includes('portfolio') ? "#000" : "#ffffff",
                                                    weight: 1,
                                                    fillOpacity: 0.8
                                                });
                                            }
                                            if (onFeatureSelect) onFeatureSelect(null);
                                        }
                                    });
                                    const title = feature.properties.NAME_1 || feature.properties.NAME || 'Asset';
                                    layer.bindTooltip(`<b>${title}</b><br/>Zone RPA: ${feature.properties.zone_rpa}`, { sticky: true });
                                }}
                            />
                        );
                    })}
                </MapContainer>

                {/* Floating Map Legend - Only shown when high-risk layers are visible */}
                {activeLayers.length > 0 && (
                    <div className="map-legend-overlay animate-fade-in">
                        <div className="legend-header">
                            <Shield size={12} className="text-blue-400" />
                            <span>RPA 99/2003 Seismic Intelligence</span>
                        </div>
                        <div className="legend-grid">
                            <div className="legend-item">
                                <span className="color-box" style={{ background: '#ef4444' }}></span>
                                <span>Zone III (Critical)</span>
                            </div>
                            <div className="legend-item">
                                <span className="color-box" style={{ background: '#f97316' }}></span>
                                <span>Zone IIb (Severe)</span>
                            </div>
                            <div className="legend-item">
                                <span className="color-box" style={{ background: '#fbbf24' }}></span>
                                <span>Zone IIa (Moderate)</span>
                            </div>
                            <div className="legend-item">
                                <span className="color-box" style={{ background: '#22c55e' }}></span>
                                <span>Zone I (Low)</span>
                            </div>
                        </div>
                        <div className="sub-text" style={{ fontSize: '9px', marginTop: '8px', opacity: 0.6 }}>
                            {activeLayers.length} layers currently projected
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MapRiskVisualizer;
