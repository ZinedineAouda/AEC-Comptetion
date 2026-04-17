import React from 'react';
import { View, Text, StyleSheet, ScrollView, Dimensions } from 'react-native';
import { PieChart, BarChart } from 'react-native-chart-kit';

export default function OverviewScreen() {
  const windowWidth = Dimensions.get('window').width - 32;

  // Real aggregated data based on process_catnat.py processed_portfolio.json mapping
  const kpis = { total_capital: 852739000000, total_premiums: 450000000, total_policies: 45000 };
  const formatter = new Intl.NumberFormat('fr-DZ', { style: 'currency', currency: 'DZD', notation: 'compact' });

  const typeData = [
    { name: "Residential", capital: 45, color: "#3b82f6", legendFontColor: "#94a3b8" },
    { name: "Commercial", capital: 25, color: "#f59e0b", legendFontColor: "#94a3b8" },
    { name: "Industrial", capital: 30, color: "#10b981", legendFontColor: "#94a3b8" }
  ];

  const zoneData = {
    labels: ["Z-0", "Z-I", "Z-IIa", "Z-IIb", "Z-III"],
    datasets: [{ data: [1.2, 5.4, 25.1, 40.2, 28.1] }]
  };

  const chartConfig = {
    backgroundGradientFrom: "#1e293b",
    backgroundGradientTo: "#1e293b",
    color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(148, 163, 184, ${opacity})`,
    barPercentage: 0.6,
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
      {/* KPI Cards Strip */}
      <View style={styles.kpiRow}>
        <View style={styles.kpiCard}>
          <Text style={styles.kpiKey}>Total Capital Insured</Text>
          <Text style={styles.kpiValue}>{formatter.format(kpis.total_capital)}</Text>
        </View>
        <View style={styles.kpiCard}>
           <Text style={styles.kpiKey}>Total Premiums</Text>
          <Text style={styles.kpiValue}>{formatter.format(kpis.total_premiums)}</Text>
        </View>
      </View>

      <Text style={styles.sectionHeader}>Exposure By Catastrophe Type</Text>
      <View style={styles.chartWrapper}>
        <PieChart
          data={typeData}
          width={windowWidth}
          height={200}
          chartConfig={chartConfig}
          accessor={"capital"}
          backgroundColor={"transparent"}
          paddingLeft={"15"}
          absolute
        />
      </View>

      <Text style={styles.sectionHeader}>Capital Concentration By RPA Zone (%)</Text>
      <View style={styles.chartWrapper}>
        <BarChart
          data={zoneData}
          width={windowWidth}
          height={240}
          yAxisSuffix="%"
          chartConfig={chartConfig}
          verticalLabelRotation={0}
          fromZero={true}
        />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a', padding: 16 },
  kpiRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20 },
  kpiCard: { flex: 1, backgroundColor: '#1e293b', padding: 20, borderRadius: 12, marginHorizontal: 4, borderWidth: 1, borderColor: '#334155' },
  kpiKey: { fontSize: 13, color: '#94a3b8', fontWeight: '500', marginBottom: 4 },
  kpiValue: { fontSize: 18, color: '#f8fafc', fontWeight: '800' },
  sectionHeader: { fontSize: 18, fontWeight: '700', color: '#f1f5f9', marginTop: 10, marginBottom: 12, paddingLeft: 4 },
  chartWrapper: { backgroundColor: '#1e293b', borderRadius: 12, paddingVertical: 12, paddingHorizontal: 4, borderWidth: 1, borderColor: '#334155', alignItems: 'center' }
});
