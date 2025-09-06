// Financial Data Visualization App

// Global variables
let revenueChart = null;
let financialsChart = null;
let currentTicker = '';
let currentQuarters = 8;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Financial Data Visualization App initialized');
    
    // Set up event listeners
    document.getElementById('tickerSelect').addEventListener('change', function() {
        currentTicker = this.value;
        console.log('Ticker selected:', currentTicker);
        
        // Clear existing charts and data when ticker changes
        if (currentTicker) {
            clearCharts();
            clearDataTable();
            // Reset UI elements
            document.getElementById('revenueUnit').textContent = 'USD';
            document.getElementById('revenueCount').textContent = '0 quarters';
        }
    });
    
    document.getElementById('quartersSelect').addEventListener('change', function() {
        currentQuarters = parseInt(this.value);
        console.log('Quarters selected:', currentQuarters);
        // Don't auto-load data, just update the current quarters
    });
});

// Load revenue data and create chart
async function loadRevenueData() {
    const ticker = document.getElementById('tickerSelect').value;
    const quarters = parseInt(document.getElementById('quartersSelect').value);
    
    if (!ticker) {
        showToast('Please select a company first', 'warning');
        return;
    }
    
    showLoading('Loading revenue data...');
    
    try {
        const response = await axios.get(`/api/company/${ticker}/revenue?quarters=${quarters}`);
        const data = response.data;
        
        if (data.error) {
            showToast(data.error, 'warning');
            
            // Clear charts and table
            clearCharts();
            clearDataTable();
        } else {
            // Update UI elements
            document.getElementById('revenueUnit').textContent = data.unit;
            document.getElementById('revenueCount').textContent = `${data.data.length} quarters`;
            
            // Create or update revenue chart
            createRevenueChart(data);
            
            // Load comprehensive financial data
            try {
                await loadFinancialData(ticker, quarters);
            } catch (financialError) {
                console.warn('Error loading financial data:', financialError);
                // Continue even if financial data fails
            }
            
            showToast(`Successfully loaded data for ${ticker}`, 'success');
        }
        
    } catch (error) {
        console.error('Error loading revenue data:', error);
        showToast('Error loading revenue data: ' + error.message, 'error');
        
        // Clear charts and table on error
        clearCharts();
        clearDataTable();
    } finally {
        // Always hide loading modal
        hideLoading();
    }
}

// Load comprehensive financial data
async function loadFinancialData(ticker, quarters) {
    try {
        const response = await axios.get(`/api/company/${ticker}/financials?quarters=${quarters}`);
        const data = response.data;
        
        if (data.financials) {
            // Create financial metrics chart
            createFinancialsChart(data.financials);
            
            // Update data table
            updateDataTable(data.financials);
        }
        
    } catch (error) {
        console.error('Error loading financial data:', error);
        showToast('Error loading financial data: ' + error.message, 'error');
    }
}

// Create revenue chart
function createRevenueChart(data) {
    const ctx = document.getElementById('revenueChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (revenueChart) {
        revenueChart.destroy();
    }
    
    revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: `Revenue (${data.unit})`,
                data: data.data,
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                borderRadius: 4,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${data.ticker} - Quarterly Revenue Trend`,
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Revenue: $${context.parsed.y.toLocaleString()}M`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString() + 'M';
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Create financial metrics chart
function createFinancialsChart(financials) {
    const ctx = document.getElementById('financialsChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (financialsChart) {
        financialsChart.destroy();
    }
    
    // Prepare datasets
    const datasets = [];
    const colors = [
        { bg: 'rgba(54, 162, 235, 0.8)', border: 'rgba(54, 162, 235, 1)' },
        { bg: 'rgba(255, 99, 132, 0.8)', border: 'rgba(255, 99, 132, 1)' },
        { bg: 'rgba(75, 192, 192, 0.8)', border: 'rgba(75, 192, 192, 1)' },
        { bg: 'rgba(255, 205, 86, 0.8)', border: 'rgba(255, 205, 86, 1)' }
    ];
    
    let colorIndex = 0;
    for (const [metric, data] of Object.entries(financials)) {
        if (data.values && data.values.length > 0) {
            datasets.push({
                label: metric,
                data: data.values,
                backgroundColor: colors[colorIndex % colors.length].bg,
                borderColor: colors[colorIndex % colors.length].border,
                borderWidth: 2,
                borderRadius: 4,
                borderSkipped: false,
            });
            colorIndex++;
        }
    }
    
    if (datasets.length === 0) {
        return;
    }
    
    financialsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: financials.Revenue?.labels || financials['Net Income']?.labels || [],
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Financial Metrics Overview',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}M`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString() + 'M';
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Update data table
function updateDataTable(financials) {
    const tbody = document.getElementById('dataTableBody');
    tbody.innerHTML = '';
    
    // Get the labels (quarters) from the first available metric
    const labels = financials.Revenue?.labels || financials['Net Income']?.labels || [];
    
    if (labels.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No data available</td></tr>';
        return;
    }
    
    // Create table rows
    for (let i = 0; i < labels.length; i++) {
        const row = document.createElement('tr');
        
        const quarter = labels[i];
        const revenue = financials.Revenue?.values[i] || 0;
        const netIncome = financials['Net Income']?.values[i] || 0;
        const totalAssets = financials['Total Assets']?.values[i] || 0;
        const totalLiabilities = financials['Total Liabilities']?.values[i] || 0;
        
        row.innerHTML = `
            <td><strong>${quarter}</strong></td>
            <td>$${revenue.toLocaleString()}</td>
            <td>$${netIncome.toLocaleString()}</td>
            <td>$${totalAssets.toLocaleString()}</td>
            <td>$${totalLiabilities.toLocaleString()}</td>
        `;
        
        tbody.appendChild(row);
    }
}

// Show scrape modal
function scrapeData() {
    const modal = new bootstrap.Modal(document.getElementById('scrapeModal'));
    modal.show();
}

// Start scraping process
async function startScraping() {
    const ticker = document.getElementById('scrapeTickerSelect').value;
    const quarters = parseInt(document.getElementById('scrapeQuartersSelect').value);
    
    if (!ticker) {
        showToast('Please select a company to scrape', 'warning');
        return;
    }
    
    // Close the modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('scrapeModal'));
    modal.hide();
    
    showLoading(`Scraping financial data for ${ticker}...`);
    
    try {
        const formData = new FormData();
        formData.append('ticker', ticker);
        formData.append('quarters', quarters);
        
        const response = await axios.post('/api/scrape', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        const data = response.data;
        hideLoading();
        
        if (data.successful > 0) {
            showToast(`Successfully scraped ${data.successful}/${data.total} quarters for ${ticker}`, 'success');
            
            // Update the main ticker selection if it's empty
            if (!document.getElementById('tickerSelect').value) {
                document.getElementById('tickerSelect').value = ticker;
                currentTicker = ticker;
            }
            
            // Reload the data if this ticker is currently selected
            if (currentTicker === ticker) {
                setTimeout(() => {
                    loadRevenueData();
                }, 1000);
            }
        } else {
            showToast('No data was scraped. Please try again.', 'warning');
        }
        
    } catch (error) {
        console.error('Error scraping data:', error);
        showToast('Error scraping data: ' + error.message, 'error');
        hideLoading();
    }
}

// Load database statistics
async function loadDatabaseStats() {
    showLoading('Loading database statistics...');
    
    try {
        const response = await axios.get('/api/stats');
        const stats = response.data;
        
        hideLoading();
        
        const message = `
            <strong>Database Statistics:</strong><br>
            Companies: ${stats.companies}<br>
            Filings: ${stats.filings}<br>
            Financial Data Points: ${stats.financial_data_points}<br>
            Statement Types: ${JSON.stringify(stats.statement_types)}
        `;
        
        showToast(message, 'info', 10000);
        
    } catch (error) {
        console.error('Error loading stats:', error);
        showToast('Error loading database statistics: ' + error.message, 'error');
        hideLoading();
    }
}

// Utility functions
function showLoading(text = 'Loading...') {
    document.getElementById('loadingText').textContent = text;
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
    
    // Safety timeout - force close after 30 seconds
    setTimeout(() => {
        console.log('Loading timeout reached, force closing modal');
        forceCloseLoading();
    }, 30000);
}

function hideLoading() {
    console.log('hideLoading() called');
    const modalElement = document.getElementById('loadingModal');
    
    if (modalElement) {
        console.log('Modal element found');
        
        // Try multiple methods to hide the modal
        try {
            // Method 1: Get existing instance
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                console.log('Hiding modal via instance');
                modal.hide();
            } else {
                console.log('No instance found, creating new one to hide');
                const newModal = new bootstrap.Modal(modalElement);
                newModal.hide();
            }
        } catch (error) {
            console.log('Error hiding modal:', error);
        }
        
        // Method 2: Force hide with jQuery-style approach
        setTimeout(() => {
            console.log('Force hiding modal...');
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';
            modalElement.setAttribute('aria-hidden', 'true');
            modalElement.removeAttribute('aria-modal');
            
            // Remove backdrop
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => {
                backdrop.remove();
            });
            
            // Reset body classes and styles
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            
            console.log('Modal force-hidden');
        }, 50);
        
        // Method 3: Additional cleanup
        setTimeout(() => {
            console.log('Final cleanup...');
            const remainingBackdrops = document.querySelectorAll('.modal-backdrop');
            remainingBackdrops.forEach(backdrop => backdrop.remove());
            
            if (modalElement.classList.contains('show')) {
                modalElement.classList.remove('show');
                modalElement.style.display = 'none';
            }
            
            console.log('Final cleanup completed');
        }, 200);
        
    } else {
        console.log('Modal element not found!');
    }
}

function showToast(message, type = 'info', duration = 5000) {
    const toast = document.getElementById('toast');
    const toastBody = document.getElementById('toastBody');
    
    // Set message
    toastBody.innerHTML = message;
    
    // Set toast type
    toast.className = 'toast';
    if (type === 'success') {
        toast.classList.add('bg-success', 'text-white');
    } else if (type === 'error') {
        toast.classList.add('bg-danger', 'text-white');
    } else if (type === 'warning') {
        toast.classList.add('bg-warning', 'text-dark');
    } else {
        toast.classList.add('bg-info', 'text-white');
    }
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast, { delay: duration });
    bsToast.show();
}

// Clear charts
function clearCharts() {
    if (revenueChart) {
        revenueChart.destroy();
        revenueChart = null;
    }
    if (financialsChart) {
        financialsChart.destroy();
        financialsChart = null;
    }
}

// Clear data table
function clearDataTable() {
    const tbody = document.getElementById('dataTableBody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No data available</td></tr>';
}

// Force close loading modal (emergency function)
function forceCloseLoading() {
    console.log('forceCloseLoading() called');
    const modalElement = document.getElementById('loadingModal');
    
    if (modalElement) {
        // Force remove all modal-related elements
        modalElement.classList.remove('show', 'fade');
        modalElement.style.display = 'none';
        modalElement.setAttribute('aria-hidden', 'true');
        modalElement.removeAttribute('aria-modal');
        
        // Remove all backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        
        // Reset body
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        console.log('Loading modal force-closed');
    }
}

// Export functions for global access
window.loadRevenueData = loadRevenueData;
window.scrapeData = scrapeData;
window.startScraping = startScraping;
window.loadDatabaseStats = loadDatabaseStats;
window.forceCloseLoading = forceCloseLoading;
