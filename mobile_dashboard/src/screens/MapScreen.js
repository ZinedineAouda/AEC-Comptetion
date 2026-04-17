import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function MapScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.placeholderContainer}>
        <Text style={styles.icon}>🗺️</Text>
        <Text style={styles.devNote}>
          "// PLACEHOLDER: Teammate's Interactive QGIS RPA Map Goes Here."
        </Text>
        <Text style={styles.subText}>This component is structurally reserved for external GIS libraries.</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a', padding: 20, justifyContent: 'center' },
  placeholderContainer: { 
    height: '75%', backgroundColor: '#1e293b', 
    borderWidth: 3, borderColor: '#3b82f6', borderStyle: 'dashed',
    borderRadius: 20, alignItems: 'center', justifyContent: 'center', padding: 25 
  },
  icon: { fontSize: 60, marginBottom: 20 },
  devNote: { color: '#ef4444', fontWeight: '800', fontSize: 18, textAlign: 'center', marginBottom: 15 },
  subText: { color: '#94a3b8', textAlign: 'center', fontSize: 14 }
});
