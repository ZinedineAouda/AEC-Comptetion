import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  Upload, Search, Filter, ArrowUpDown, ArrowUp, ArrowDown,
  FileSpreadsheet, Eye, X, ChevronLeft, ChevronRight,
  TrendingUp, TrendingDown, Shield, MapPin, Calendar,
  DollarSign, Layers, Activity, AlertTriangle, CheckCircle,
  Clock, Hash, Loader2, BarChart3, Building2
} from 'lucide-react';
import './MyDatabasePage.css';

interface Revision {
  avenant: number;
  date_effet: string;
  date_expiration: string;
  capital: number;
  premium: number;
  year: string;
}

interface Assessment {
  verdict: string;
  ratio: number;
  label: string;
  color: string;
}

interface PolicyProfile {
  policy_id: string;
  branch_code: string;
  type: string;
  wilaya: string;
  commune: string;
  zone_rpa: string;
  capital: number;
  premium: number;
  fair_premium: number;
  date_effet: string;
  date_expiration: string;
  revisions: Revision[];
  revision_count: number;
  assessment: Assessment;
}

interface PortfolioStats {
  total_policies: number;
  total_capital: number;
  total_premium: number;
  by_verdict: Record<string, number>;
  by_zone: Record<string, number>;
}

const VERDICT_LABELS: Record<string, { label: string; icon: React.ReactNode; cls: string }> = {
  SEVERELY_UNDERPRICED: { label: 'Underpriced', icon: <AlertTriangle size={14} />, cls: 'verdict-danger' },
  UNDERPRICED: { label: 'Below Market', icon: <TrendingDown size={14} />, cls: 'verdict-warning' },
  FAIR: { label: 'Fair Price', icon: <CheckCircle size={14} />, cls: 'verdict-success' },
  PROFITABLE: { label: 'Profitable', icon: <TrendingUp size={14} />, cls: 'verdict-info' },
  OVERPRICED: { label: 'Premium', icon: <DollarSign size={14} />, cls: 'verdict-purple' },
  NO_DATA: { label: 'No Data', icon: <Clock size={14} />, cls: 'verdict-muted' },
};

const ZONES = ['', '0', 'I', 'IIa', 'IIb', 'III'];
const VERDICTS = ['', 'SEVERELY_UNDERPRICED', 'UNDERPRICED', 'FAIR', 'PROFITABLE', 'OVERPRICED'];

const fmt = (n: number) => new Intl.NumberFormat('fr-DZ', { maximumFractionDigits: 0 }).format(n);

const MyDatabasePage: React.FC = () => {
  const [data, setData] = useState<PolicyProfile[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [limit] = useState(50);
  const [sortBy, setSortBy] = useState('policy_id');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [filterZone, setFilterZone] = useState('');
  const [filterVerdict, setFilterVerdict] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<PolicyProfile[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [stats, setStats] = useState<PortfolioStats | null>(null);
  const [selectedProfile, setSelectedProfile] = useState<PolicyProfile | null>(null);
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null);

  const fileRef = useRef<HTMLInputElement>(null);
  const searchTimer = useRef<any>(null);

  const showToast = (msg: string, type: 'success' | 'error' = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Fetch paginated data
  const fetchData = useCallback(async (pg = 0) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        offset: String(pg), limit: String(limit),
        sort_by: sortBy, sort_dir: sortDir,
        filter_zone: filterZone, filter_verdict: filterVerdict,
      });
      const res = await fetch(`http://localhost:8000/api/portfolio/data?${params}`);
      const json = await res.json();
      setData(json.data || []);
      setTotal(json.total || 0);
      setOffset(pg);
    } catch { showToast('Server unreachable', 'error'); }
    finally { setLoading(false); }
  }, [limit, sortBy, sortDir, filterZone, filterVerdict]);

  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/portfolio/stats');
      const json = await res.json();
      if (json.total_policies) setStats(json);
    } catch {}
  };

  useEffect(() => { fetchData(0); fetchStats(); }, [fetchData]);

  // Search
  const handleSearch = (q: string) => {
    setSearchQuery(q);
    if (searchTimer.current) clearTimeout(searchTimer.current);
    if (!q.trim()) {
      setSearchResults(null);
      return;
    }
    searchTimer.current = setTimeout(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/portfolio/search?q=${encodeURIComponent(q)}`);
        const json = await res.json();
        setSearchResults(json.results || []);
      } catch {}
    }, 300);
  };

  // Upload
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const res = await fetch('http://localhost:8000/api/portfolio/upload', { method: 'POST', body: fd });
      const json = await res.json();
      setUploadResult(json);
      if (json.status === 'success') {
        showToast(`Loaded ${json.unique_policies?.toLocaleString()} policies from ${json.sheets_processed?.join(', ')}`, 'success');
        await fetchData(0);
        await fetchStats();
      } else {
        showToast(json.message || 'Upload failed', 'error');
      }
    } catch { showToast('Upload failed', 'error'); }
    finally { setUploading(false); if (fileRef.current) fileRef.current.value = ''; }
  };

  // Sorting
  const handleSort = (col: string) => {
    if (sortBy === col) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(col);
      setSortDir('asc');
    }
  };

  const SortIcon = ({ col }: { col: string }) => {
    if (sortBy !== col) return <ArrowUpDown size={12} className="sort-idle" />;
    return sortDir === 'asc' ? <ArrowUp size={12} className="sort-active" /> : <ArrowDown size={12} className="sort-active" />;
  };

  const pageCount = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;
  const displayData = searchResults !== null ? searchResults : data;

  return (
    <div className="db-page">
      {/* Toast */}
      {toast && (
        <div className={`db-toast ${toast.type}`}>
          {toast.type === 'success' ? <CheckCircle size={18} /> : <AlertTriangle size={18} />}
          <span>{toast.msg}</span>
        </div>
      )}

      {/* Header */}
      <header className="db-header">
        <div className="db-title-group">
          <h1><BarChart3 size={28} /> Portfolio Intelligence</h1>
          <p>CATNAT Risk Portfolio — Upload, Analyze & Evaluate Pricing Compliance</p>
        </div>
        <div className="db-actions">
          <input ref={fileRef} type="file" accept=".xlsx,.xls" hidden onChange={handleUpload} />
          <button className="btn-upload" onClick={() => fileRef.current?.click()} disabled={uploading}>
            {uploading ? <Loader2 size={18} className="spin" /> : <Upload size={18} />}
            {uploading ? 'Processing...' : 'Upload CATNAT'}
          </button>
        </div>
      </header>

      {/* Stats Bar */}
      {stats && (
        <>
          <div className="db-stats-bar">
            <div className="stat-card">
              <FileSpreadsheet size={20} />
              <div>
                <span className="stat-value">{stats.total_policies.toLocaleString()}</span>
                <span className="stat-label">Unique Policies</span>
              </div>
            </div>
            <div className="stat-card">
              <DollarSign size={20} />
              <div>
                <span className="stat-value">{fmt(stats.total_capital)} DZD</span>
                <span className="stat-label">Total Capital</span>
              </div>
            </div>
            <div className="stat-card">
              <Activity size={20} />
              <div>
                <span className="stat-value">{fmt(stats.total_premium)} DZD</span>
                <span className="stat-label">Total Premiums</span>
              </div>
            </div>
            <div className="stat-card">
              <Shield size={20} />
              <div>
                <span className="stat-value">{Object.keys(stats.by_zone || {}).length}</span>
                <span className="stat-label">RPA Zones Active</span>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Toolbar: Search + Filters */}
      <div className="db-toolbar">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search by policy number, wilaya, or commune..."
            value={searchQuery}
            onChange={e => handleSearch(e.target.value)}
          />
          {searchQuery && (
            <button className="search-clear" onClick={() => { setSearchQuery(''); setSearchResults(null); }}>
              <X size={16} />
            </button>
          )}
        </div>
        <div className="filter-group">
          <Filter size={16} />
          <select value={filterZone} onChange={e => { setFilterZone(e.target.value); setOffset(0); }}>
            <option value="">All Zones</option>
            {ZONES.filter(Boolean).map(z => <option key={z} value={z}>Zone {z}</option>)}
          </select>
          <select value={filterVerdict} onChange={e => { setFilterVerdict(e.target.value); setOffset(0); }}>
            <option value="">All Verdicts</option>
            {VERDICTS.filter(Boolean).map(v => (
              <option key={v} value={v}>{VERDICT_LABELS[v]?.label || v}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="db-table-wrapper">
        {loading && <div className="table-loader"><Loader2 size={24} className="spin" /> Loading...</div>}
        <table className="db-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('policy_id')}>Policy ID <SortIcon col="policy_id" /></th>
              <th onClick={() => handleSort('type')}>Type <SortIcon col="type" /></th>
              <th onClick={() => handleSort('wilaya')}>Wilaya <SortIcon col="wilaya" /></th>
              <th onClick={() => handleSort('commune')}>Commune <SortIcon col="commune" /></th>
              <th onClick={() => handleSort('zone_rpa')}>Zone <SortIcon col="zone_rpa" /></th>
              <th onClick={() => handleSort('capital')}>Capital <SortIcon col="capital" /></th>
              <th onClick={() => handleSort('premium')}>Premium <SortIcon col="premium" /></th>
              <th onClick={() => handleSort('ratio')}>Verdict <SortIcon col="ratio" /></th>
              <th>Rev.</th>
              <th>Inspect</th>
            </tr>
          </thead>
          <tbody>
            {displayData.length === 0 && !loading && (
              <tr><td colSpan={10} className="empty-row">
                <FileSpreadsheet size={40} />
                <p>No data loaded. Upload a CATNAT XLSX file to begin analysis.</p>
              </td></tr>
            )}
            {displayData.map((p, i) => {
              const vd = VERDICT_LABELS[p.assessment.verdict] || VERDICT_LABELS['NO_DATA'];
              return (
                <tr key={`${p.policy_id}-${i}`} className={p.revision_count > 1 ? 'has-revisions' : ''}>
                  <td className="cell-policy">{p.policy_id}</td>
                  <td className="cell-type">{p.type}</td>
                  <td>{p.wilaya}</td>
                  <td>{p.commune}</td>
                  <td><span className={`zone-badge zone-${p.zone_rpa.replace('+', '')}`}>{p.zone_rpa}</span></td>
                  <td className="cell-num">{fmt(p.capital)}</td>
                  <td className="cell-num">{fmt(p.premium)}</td>
                  <td>
                    <span className={`verdict-badge ${vd.cls}`}>
                      {vd.icon} {vd.label}
                    </span>
                  </td>
                  <td className="cell-rev">
                    {p.revision_count > 1 && <span className="rev-badge">{p.revision_count}</span>}
                  </td>
                  <td>
                    <button className="btn-inspect" onClick={() => setSelectedProfile(p)}>
                      <Eye size={16} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {searchResults === null && total > 0 && (
        <div className="db-pagination">
          <span className="page-info">
            Showing {offset + 1}–{Math.min(offset + limit, total)} of {total.toLocaleString()} policies
          </span>
          <div className="page-controls">
            <button disabled={offset === 0} onClick={() => fetchData(Math.max(0, offset - limit))}>
              <ChevronLeft size={18} /> Prev
            </button>
            <span className="page-current">{currentPage} / {pageCount}</span>
            <button disabled={offset + limit >= total} onClick={() => fetchData(offset + limit)}>
              Next <ChevronRight size={18} />
            </button>
          </div>
        </div>
      )}

      {/* Inspect Modal */}
      {selectedProfile && (
        <div className="modal-overlay" onClick={() => setSelectedProfile(null)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2><Hash size={20} /> {selectedProfile.policy_id}</h2>
                <p className="modal-subtitle">{selectedProfile.wilaya} — {selectedProfile.commune}</p>
              </div>
              <button className="modal-close" onClick={() => setSelectedProfile(null)}><X size={22} /></button>
            </div>

            <div className="modal-body">
              {/* Identity Grid */}
              <div className="modal-section">
                <h3>Policy Identity</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <Building2 size={16} />
                    <div><span className="info-label">Type</span><span className="info-value">{selectedProfile.type}</span></div>
                  </div>
                  <div className="info-item">
                    <MapPin size={16} />
                    <div><span className="info-label">Zone RPA</span><span className="info-value">{selectedProfile.zone_rpa}</span></div>
                  </div>
                  <div className="info-item">
                    <Calendar size={16} />
                    <div><span className="info-label">Date Effet</span><span className="info-value">{selectedProfile.date_effet}</span></div>
                  </div>
                  <div className="info-item">
                    <Layers size={16} />
                    <div><span className="info-label">Branch</span><span className="info-value">{selectedProfile.branch_code}</span></div>
                  </div>
                </div>
              </div>

              {/* Pricing Assessment */}
              <div className="modal-section">
                <h3>Pricing Assessment</h3>
                <div className="pricing-grid">
                  <div className="pricing-card">
                    <span className="pricing-label">Actual Premium</span>
                    <span className="pricing-value">{fmt(selectedProfile.premium)} DZD</span>
                  </div>
                  <div className="pricing-card">
                    <span className="pricing-label">Fair Premium (RPA)</span>
                    <span className="pricing-value accent">{fmt(selectedProfile.fair_premium)} DZD</span>
                  </div>
                  <div className="pricing-card full">
                    <span className="pricing-label">Verdict</span>
                    <span className={`verdict-badge lg ${VERDICT_LABELS[selectedProfile.assessment.verdict]?.cls}`}>
                      {VERDICT_LABELS[selectedProfile.assessment.verdict]?.icon}
                      {selectedProfile.assessment.label}
                    </span>
                  </div>
                </div>
              </div>

              {/* Revision History */}
              {selectedProfile.revisions.length > 1 && (
                <div className="modal-section">
                  <h3>Revision History ({selectedProfile.revisions.length} entries)</h3>
                  <div className="revision-table-wrap">
                    <table className="revision-table">
                      <thead>
                        <tr>
                          <th>Avenant</th>
                          <th>Year</th>
                          <th>Date Effet</th>
                          <th>Date Expiration</th>
                          <th>Capital</th>
                          <th>Premium</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedProfile.revisions.map((r, i) => (
                          <tr key={i} className={r.avenant === 0 ? 'rev-base' : 'rev-avenant'}>
                            <td>{r.avenant === 0 ? 'Original' : `Avenant ${r.avenant}`}</td>
                            <td>{r.year}</td>
                            <td>{r.date_effet}</td>
                            <td>{r.date_expiration}</td>
                            <td>{fmt(r.capital)}</td>
                            <td>{fmt(r.premium)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyDatabasePage;
