import React, { useState, useEffect, useRef } from 'react';

const LocationSearch = ({ onLocationSelect, className = "" }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [showDropdown, setShowDropdown] = useState(false);
    const searchRef = useRef(null);
    const debounceTimeout = useRef(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (searchRef.current && !searchRef.current.contains(event.target)) {
                setShowDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const fetchResults = async (searchQuery) => {
        if (!searchQuery.trim()) {
            setResults([]);
            return;
        }

        setIsLoading(true);
        try {
            // Added countrycodes=in (India) for better relevance and addressdetails=1 for context
            const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=5&countrycodes=in&addressdetails=1`);
            if (!response.ok) throw new Error("Network response was not ok");
            const data = await response.json();
            setResults(data);
            setShowDropdown(true);
        } catch (error) {
            console.error("Search error:", error);
            setResults([]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleInput = (e) => {
        const value = e.target.value;
        setQuery(value);

        if (debounceTimeout.current) {
            clearTimeout(debounceTimeout.current);
        }

        if (value.length > 2) {
            debounceTimeout.current = setTimeout(() => {
                fetchResults(value);
            }, 500); // Debounce 500ms
        } else {
            setResults([]);
            setShowDropdown(false);
        }
    };

    const handleManualSearch = (e) => {
        e.preventDefault();
        fetchResults(query);
    };

    const handleSelect = (item) => {
        const lat = parseFloat(item.lat);
        const lon = parseFloat(item.lon);
        // Use styled display_name or fallback
        setQuery(item.display_name);
        setShowDropdown(false);
        onLocationSelect(lat, lon);
    };

    return (
        <div ref={searchRef} className={`relative ${className}`}>
            <div className="relative flex shadow-sm rounded-lg border border-slate-300 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
                <input
                    type="text"
                    value={query}
                    onChange={handleInput}
                    onKeyDown={(e) => e.key === 'Enter' && handleManualSearch(e)}
                    placeholder="Search address, landmark..."
                    className="flex-1 pl-3 pr-4 py-2 text-sm border-none outline-none"
                    onFocus={() => {
                        if (results.length > 0) setShowDropdown(true);
                    }}
                />

                {isLoading ? (
                    <div className="px-3 py-2 flex items-center justify-center">
                        <svg className="animate-spin h-4 w-4 text-slate-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </div>
                ) : (
                    <button
                        onClick={handleManualSearch}
                        className="px-3 py-2 bg-gray-50 hover:bg-gray-100 border-l border-gray-200 text-slate-500 hover:text-blue-600 transition-colors"
                        title="Search"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </button>
                )}
            </div>

            {/* Suggestions Dropdown */}
            {showDropdown && results.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-xl border border-slate-200 overflow-hidden z-[2000] max-h-60 overflow-y-auto">
                    {results.map((item, index) => (
                        <button
                            key={index}
                            onClick={() => handleSelect(item)}
                            className="w-full text-left px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 border-b border-slate-100 last:border-none transition-colors"
                        >
                            {item.display_name}
                        </button>
                    ))}
                </div>
            )}

            {/* No Results Message */}
            {showDropdown && !isLoading && query.length > 2 && results.length === 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-xl border border-slate-200 p-3 text-center text-sm text-slate-500 z-[2000]">
                    No locations found
                </div>
            )}
        </div>
    );
};

export default LocationSearch;
