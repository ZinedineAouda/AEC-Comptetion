import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';
import MainLayout from './src/layouts/MainLayout';

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="light" />
      <MainLayout />
    </NavigationContainer>
  );
}
