import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { TrendingUp, Calendar, DollarSign, Percent, ChevronDown, RefreshCw } from 'lucide-react';
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const SimpleIPOView = () => {
  const [data, setData] = useState([]);
  const [selectedIPO, setSelectedIPO] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/ipos');
      const jsonData = await response.json();
      setData(jsonData);
      if (jsonData.length > 0) {
        setSelectedIPO(jsonData[0]);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      // Call the refresh endpoint
      const refreshResponse = await fetch('http://localhost:8000/api/refresh', {
        method: 'POST'
      });

      if (!refreshResponse.ok) {
        throw new Error('Refresh failed');
      }

      // Refetch the data
      await fetchData();
    } catch (error) {
      console.error('Error refreshing data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const formatValue = (value, key) => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'number') {
      if (key === 'ipo_size') return `₹ ${value.toLocaleString()} Cr`;
      if (key === 'ipo_price') return `₹ ${value.toLocaleString()}`;
      if (key === 'subscription_percent') return `${value.toLocaleString()}%`;
      if (key === 'ipo_gmp') return `₹ ${value.toLocaleString()}`;
      return value.toLocaleString();
    }
    return value;
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'close':
        return 'bg-red-100 text-red-800';
      case 'upcoming':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getIcon = (key) => {
    switch (key) {
      case 'ipo_price':
      case 'ipo_size':
      case 'ipo_gmp':
        return <DollarSign className="h-5 w-5 text-gray-500" />;
      case 'subscription_percent':
        return <Percent className="h-5 w-5 text-gray-500" />;
      case 'open_date':
      case 'close_date':
      case 'gmp_updated_date':
        return <Calendar className="h-5 w-5 text-gray-500" />;
      case 'status':
        return <TrendingUp className="h-5 w-5 text-gray-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="w-full min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-6xl">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="text-2xl font-bold text-gray-800">IPO Details</CardTitle>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg 
                ${refreshing ? 'bg-gray-300' : 'bg-blue-600 hover:bg-blue-700'} 
                text-white transition-colors`}
            >
              <RefreshCw className={`h-5 w-5 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refreshing...' : 'Refresh Data'}
            </button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <select
              className="w-full p-3 mb-6 border rounded-lg bg-white shadow-sm appearance-none pr-10 text-gray-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
              onChange={(e) => {
                const selected = data.find(ipo => ipo.ipo_name === e.target.value);
                setSelectedIPO(selected);
              }}
              value={selectedIPO?.ipo_name || ''}
            >
              {data.slice(0, 10).map((ipo, index) => (
                <option key={index} value={ipo.ipo_name}>
                  {ipo.ipo_name}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-3.5 h-5 w-5 text-gray-400 pointer-events-none" />
          </div>

          {selectedIPO && (
            <div className="bg-white rounded-lg overflow-hidden border border-gray-100">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-6">
                <div className="col-span-2">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold text-gray-800">{selectedIPO.ipo_name}</h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedIPO.status)}`}>
                      {selectedIPO.status}
                    </span>
                  </div>
                </div>

                {Object.entries(selectedIPO).map(([key, value]) => {
                  if (key === 'ipo_name' || key === 'status') return null;
                  const icon = getIcon(key);
                  return (
                    <div key={key} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                        {icon}
                        <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                      </div>
                      <div className="text-lg font-semibold text-gray-800">
                        {formatValue(value, key)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SimpleIPOView;