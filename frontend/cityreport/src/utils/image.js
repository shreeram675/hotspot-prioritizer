const getBackendBaseUrl = () => {
    const configUrl = import.meta.env.VITE_API_URL || 'http://localhost:8005';

    // If the browser is accessing via an IP address (e.g., 192.168.1.5), 
    // and the backend is set to localhost, we should use the same IP for the backend.
    if (configUrl.includes('localhost') && window.location.hostname !== 'localhost') {
        return configUrl.replace('localhost', window.location.hostname);
    }

    return configUrl;
};

export const getImageUrl = (url) => {
    if (!url) return 'https://via.placeholder.com/800x400?text=No+Image+Available';

    // If it's already a full URL (like unsplash), return it
    if (url.startsWith('http')) return url;

    const baseUrl = getBackendBaseUrl().replace(/\/$/, ''); // Remove trailing slash
    let relativePath = url.startsWith('/') ? url : `/${url}`; // Ensure leading slash

    // Auto-correct /uploads/ to /upload/image/ if it looks like a UUID path
    if (relativePath.startsWith('/uploads/')) {
        relativePath = relativePath.replace('/uploads/', '/upload/image/');
    }

    // If it's a relative path from our backend (starts with /upload)
    if (relativePath.startsWith('/upload')) {
        return `${baseUrl}${relativePath}`;
    }

    return url;
};
