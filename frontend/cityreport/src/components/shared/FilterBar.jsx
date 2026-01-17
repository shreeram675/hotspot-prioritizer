import React from 'react';
import { Search, Filter } from 'lucide-react';
import Card from './Card';
import './FilterBar.css';

const FilterBar = ({ onSearch, onFilterChange, onSortChange }) => {
    return (
      <Card className="filter-bar mb-lg" padding="sm">
        <div className="flex flex-col md:flex-row gap-md items-center w-full">
          <div className="search-container flex-1 w-full">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder="Search reports..."
              className="search-input"
              onChange={(e) => onSearch(e.target.value)}
            />
          </div>

          <div className="filters-container flex gap-sm w-full md:w-auto overflow-x-auto">
            <select
              className="filter-select"
              onChange={(e) => onFilterChange("category", e.target.value)}
            >
              <option value="">All Categories</option>
              <option value="road_issues">Road Issues</option>
              <option value="waste_management">Waste Management</option>
            </select>

            <select
              className="filter-select"
              onChange={(e) => onFilterChange("status", e.target.value)}
            >
              <option value="">All Status</option>
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="Resolved">Resolved</option>
            </select>

            <select
              className="filter-select"
              onChange={(e) => onSortChange(e.target.value)}
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="upvotes">Most Upvoted</option>
            </select>
          </div>
        </div>
      </Card>
    );
};

export default FilterBar;
