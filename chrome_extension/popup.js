// Configuration
const FLASK_API_URL = 'http://localhost:5000/api/recommend';
const DJANGO_URL = 'http://localhost:8000';

// Elements
const form = document.getElementById('searchForm');
const submitBtn = document.getElementById('submitBtn');
const resultsDiv = document.getElementById('results');

// Form submission handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const vehicleMake = document.getElementById('vehicleMake').value;
    const vehicleModel = document.getElementById('vehicleModel').value;
    const regionCode = document.getElementById('regionCode').value;
    
    if (!vehicleMake || !vehicleModel || !regionCode) {
        showError('Please fill in all required fields');
        return;
    }
    
    await getRecommendations(vehicleMake, vehicleModel, regionCode);
});

// Get recommendations from Flask API
async function getRecommendations(make, model, region) {
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.textContent = 'Loading...';
    resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Analyzing plans...</p></div>';
    
    try {
        const response = await fetch(FLASK_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                vehicle_make: make,
                vehicle_model: model,
                region_code: region,
                top_n: 3,
                weights: {
                    cost: 0.30,
                    coverage: 0.25,
                    service: 0.25,
                    reliability: 0.20
                }
            })
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('No insurance plans found for this vehicle and region');
            }
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.recommendations && data.recommendations.length > 0) {
            displayResults(data.recommendations, make, model, region);
        } else {
            showError('No recommendations found');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to get recommendations. Make sure the Flask service is running.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Get Recommendations';
    }
}

// Display results
function displayResults(recommendations, make, model, region) {
    resultsDiv.innerHTML = '';
    
    recommendations.forEach(rec => {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        const scorePercentage = (rec.final_score * 100).toFixed(0);
        
        card.innerHTML = `
            <div class="result-header">
                <span class="rank-badge">#${rec.rank}</span>
                <span class="premium">$${Math.round(rec.premium_annual)}/yr</span>
            </div>
            <div class="insurer-name">${rec.insurer_name}</div>
            <div class="score-bar">
                <div class="score-fill" style="width: ${scorePercentage}%"></div>
            </div>
            <div class="rationale">${rec.rationale}</div>
        `;
        
        resultsDiv.appendChild(card);
    });
    
    // Add view details link
    const viewDetails = document.createElement('a');
    viewDetails.href = '#';
    viewDetails.className = 'view-details';
    viewDetails.textContent = '→ View Full Dashboard';
    viewDetails.onclick = (e) => {
        e.preventDefault();
        chrome.tabs.create({ 
            url: `${DJANGO_URL}/search/?make=${make}&model=${model}&region=${region}` 
        });
    };
    resultsDiv.appendChild(viewDetails);
}

// Show error message
function showError(message) {
    resultsDiv.innerHTML = `<div class="error">❌ ${message}</div>`;
}

// Save form state
form.addEventListener('input', () => {
    chrome.storage.local.set({
        vehicleMake: document.getElementById('vehicleMake').value,
        vehicleModel: document.getElementById('vehicleModel').value,
        regionCode: document.getElementById('regionCode').value
    });
});

// Restore form state on load
chrome.storage.local.get(['vehicleMake', 'vehicleModel', 'regionCode'], (result) => {
    if (result.vehicleMake) document.getElementById('vehicleMake').value = result.vehicleMake;
    if (result.vehicleModel) document.getElementById('vehicleModel').value = result.vehicleModel;
    if (result.regionCode) document.getElementById('regionCode').value = result.regionCode;
});

