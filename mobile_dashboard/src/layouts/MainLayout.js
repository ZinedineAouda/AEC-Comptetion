import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import OverviewScreen from '../screens/OverviewScreen';
import MapScreen from '../screens/MapScreen';
import SimulationScreen from '../screens/SimulationScreen';
import RecommendationsScreen from '../screens/RecommendationsScreen';

const Tab = createBottomTabNavigator();

export default function MainLayout() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: '#0f172a', shadowColor: 'transparent', elevation: 0 },
        headerTintColor: '#f8fafc',
        headerTitleStyle: { fontWeight: '800', fontSize: 20 },
        tabBarStyle: { backgroundColor: '#0f172a', borderTopColor: '#334155', paddingBottom: 5 },
        tabBarActiveTintColor: '#3b82f6',
        tabBarInactiveTintColor: '#64748b',
        tabBarLabelPosition: 'below-icon'
      }}
    >
      <Tab.Screen 
        name="Overview" 
        component={OverviewScreen} 
        options={{ title: 'GAM Dashboard', tabBarLabel: 'Overview' }} 
      />
      <Tab.Screen 
        name="Map" 
        component={MapScreen} 
        options={{ title: 'RPA Geographic Exposure', tabBarLabel: 'GIS Map' }} 
      />
      <Tab.Screen 
        name="Simulation" 
        component={SimulationScreen} 
        options={{ title: 'Catastrophe Simulation', tabBarLabel: 'Simulations' }} 
      />
      <Tab.Screen 
        name="Recommendations" 
        component={RecommendationsScreen} 
        options={{ title: 'Strategic Recommendations', tabBarLabel: 'Insights' }} 
      />
    </Tab.Navigator>
  );
}
