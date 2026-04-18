import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, Tooltip, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Shield, MapPin, Activity, Layers, Info, TrendingUp, DollarSign, Tag } from 'lucide-react';
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
    const [zoom, setZoom] = useState(7);

    useEffect(() => {
        const fetchAll = async () => {
            setLoading(true);
            try {
                const statsRes = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/portfolio/stats`);
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
        activeLayers.forEach(async (layer) => {
            if (!layerDataStore[layer.id]) {
                try {
                    const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${layer.url}`);
                    const json = await res.json();
                    setLayerDataStore(prev => ({ ...prev, [layer.id]: json }));
                } catch (err) {
                    console.error(`Failed to fetch layer ${layer.id}`, err);
                }
            }
        });
    }, [activeLayers]);

    const getRPAColor = (zone: string | number) => {
        const z = String(zone).toUpperCase();
        if (z === '3' || z === 'III') return '#ef4444';
        if (z === 'IIB') return '#f97316';
        if (z === '2' || z === 'II' || z === 'IIA') return '#fbbf24';
        if (z === '1' || z === 'I') return '#22c55e';
        return '#94a3b8';
    };

    const getQGISColor = (value: number) => {
        // Precise YlOrRd Scale re-calibrated for real Portfolio Exposure
        if (value > 10000000) return '#b91c1c'; // Very High (10M+)
        if (value > 3000000) return '#ea580c';  // High (3M - 10M)
        if (value > 750000) return '#f97316';   // Medium (750k - 3M)
        if (value > 150000) return '#facc15';   // Low (150k - 750k)
        if (value > 30000) return '#fef08a';    // Very Low (30k - 150k)
        if (value >= 0) return '#f3f4f6';       // Trace Exposure (<30k)
        return '#f1f5f9';                      // Null/Masked
    };

    const getFeatureColor = (feature: any, layerMetadata: any) => {
        const prop = layerMetadata?.targetProperty || 'zone_rpa';
        const val = feature.properties[prop];
        
        if (layerMetadata?.palette === 'YlOrRd' || layerMetadata?.scaleType === 'graduated') {
            return getQGISColor(Number(val) || 0);
        }
        if (layerMetadata?.palette === 'Blues') {
            return val > 1000000 ? '#1e3a8a' : '#bfdbfe';
        }
        if (layerMetadata?.palette === 'base') {
            return '#f1ece9';
        }
        return getRPAColor(val);
    };

    const getStyle = (feature: any, layerDef: any) => {
        const isBase = layerDef.metadata?.palette === 'base';
        const opacity = layerDef.id.includes('gadm') ? 1.0 : 0.6;
        const color = getFeatureColor(feature, layerDef.metadata);

        return {
            fillColor: color,
            weight: isBase ? 1.5 : 0.8,
            opacity: 1,
            color: isBase ? '#ffffff' : '#4b5563',
            fillOpacity: isBase ? 1.0 : opacity,
        };
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

    if (activeLayers.length === 0 && !loading) {
        return (
            <div className="map-info-card">
                <Info className="text-blue-400" size={32} />
                <p>No active geospatial layers selected.</p>
                <div className="sub-text">Use the Layer Registry to project data onto the map.</div>
            </div>
        );
    }

    const hasRiskLayer = activeLayers.some(l => l.metadata?.palette === 'RPA');
    const isZoomedIn = zoom >= 10;

    const ZoomTracker = ({ setZoom }: { setZoom: (z: number) => void }) => {
        const map = useMapEvents({
            zoomend: () => {
                setZoom(map.getZoom());
            },
        });
        return null;
    };

    return (
        <div className={`map-wrapper shadow-premium ${isZoomedIn ? 'is-zoomed-in' : ''}`}>
            <div className="map-container-inner">
                <MapContainer 
                    center={[35.0, 3.0]} 
                    zoom={7} 
                    style={{ height: '100%', width: '100%' }}
                    zoomControl={true}
                >
                    <ZoomTracker setZoom={setZoom} />
                    <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
                    />
                    
                    {activeLayers.map(layerDef => {
                        const data = layerDataStore[layerDef.id];
                        if (!data) return null;
                        
                        const isQGIS = layerDef.metadata?.palette === 'YlOrRd';
                        
                        return (
                            <GeoJSON 
                                key={`layer-dynamic-${layerDef.id}`}
                                data={data} 
                                style={(f) => getStyle(f, layerDef)}
                                pointToLayer={(feature, latlng) => {
                                    const color = getFeatureColor(feature, layerDef.metadata);
                                    return L.circleMarker(latlng, {
                                        radius: 5,
                                        fillColor: color,
                                        color: "#ffffff",
                                        weight: 1,
                                        opacity: 1,
                                        fillOpacity: 0.8
                                    });
                                }}
                                onEachFeature={(feature, layer) => {
                                    layer.on({
                                        mouseover: (e: any) => {
                                            const target = e.target;
                                            if (target.setStyle) target.setStyle({ fillOpacity: 1, weight: 2, color: '#111827' });
                                            if (onFeatureSelect) onFeatureSelect(feature.properties);
                                        },
                                        mouseout: (e: any) => {
                                            const target = e.target;
                                            if (target.setStyle) {
                                                const color = getFeatureColor(feature, layerDef.metadata);
                                                target.setStyle({
                                                    fillColor: color,
                                                    color: "#ffffff",
                                                    weight: 1,
                                                    fillOpacity: layerDef.id.includes('gadm') ? 0.3 : 0.6
                                                });
                                            }
                                            if (onFeatureSelect) onFeatureSelect(null);
                                        }
                                    });

                                    // Labels only appear on hover
                                    const name = feature.properties.NAME_2 || feature.properties.NAME_1 || 'Feature';
                                    layer.bindTooltip(`<b>${name}</b>`, { 
                                        permanent: false, 
                                        sticky: true, 
                                        direction: "top", 
                                        className: isQGIS ? "qgis-map-label" : "" 
                                    });
                                }}
                            />
                        );
                    })}
                </MapContainer>

                <div className="map-legend-stack">
                    {hasRiskLayer && (
                        <div className="map-legend-overlay animate-fade-in">
                            <div className="legend-header">
                                <Shield size={12} className="text-red-400" />
                                <span>RPA 99/2003 Seismic Intelligence</span>
                            </div>
                            <div className="legend-grid">
                                <div className="legend-item"><span className="color-box" style={{ background: '#ef4444' }}></span><span>III (Critical)</span></div>
                                <div className="legend-item"><span className="color-box" style={{ background: '#f97316' }}></span><span>IIb (Severe)</span></div>
                                <div className="legend-item"><span className="color-box" style={{ background: '#fbbf24' }}></span><span>IIa (Moderate)</span></div>
                                <div className="legend-item"><span className="color-box" style={{ background: '#22c55e' }}></span><span>I (Low)</span></div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MapRiskVisualizer;
