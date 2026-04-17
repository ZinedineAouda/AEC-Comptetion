import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';

export default function RecommendationsScreen() {
  const zone3Exposure = 35.4; 
  const zone1Exposure = 4.2;

  const getAlerts = () => {
    let alerts = [];
    if (zone3Exposure > 30) {
      alerts.push({
        id: 1, type: 'critical', emoji: '⚠️',
        title: 'DANGER: Surconcentration in Zone III',
        desc: `High risk exposure (${zone3Exposure}% of portfolio) identified in heavily seismic zones (Algiers, Chlef, etc). Halt new commercial underwritings or rapidly execute facultative reinsurance treaties.`
      });
    }
    if (zone1Exposure < 10) {
      alerts.push({
        id: 2, type: 'opportunity', emoji: '✅',
        title: 'Sous-concentration in Zone I',
        desc: `Opportunity to balance the portfolio. Risk levels are minimal but market share in Zone I (Laghouat, M'Sila) is only ${zone1Exposure}%. Expand commercial efforts here.`
      });
    }
    return alerts;
  };

  const alertColors = {
    critical: { bg: '#450a0a', border: '#ef4444', text: '#fca5a5' },
    opportunity: { bg: '#052e16', border: '#10b981', text: '#6ee7b7' }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.headerTitle}>RPA Strategy Engine</Text>
      <Text style={styles.subtitle}>Automated balance recommendations derived from current thresholds.</Text>

      {getAlerts().map((alert) => {
        const theme = alertColors[alert.type];
        return (
          <View key={alert.id} style={[styles.alertCard, { backgroundColor: theme.bg, borderColor: theme.border }]}>
            <Text style={[styles.alertTitle, { color: theme.text }]}>{alert.emoji} {alert.title}</Text>
            <Text style={styles.alertDesc}>{alert.desc}</Text>
          </View>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a', padding: 20 },
  headerTitle: { fontSize: 24, fontWeight: '800', color: '#f8fafc', marginBottom: 4 },
  subtitle: { fontSize: 15, color: '#94a3b8', marginBottom: 30 },
  alertCard: { padding: 20, borderRadius: 16, borderWidth: 1, marginBottom: 20 },
  alertTitle: { fontSize: 17, fontWeight: '700', marginBottom: 10 },
  alertDesc: { fontSize: 15, color: '#f1f5f9', lineHeight: 22 }
});
