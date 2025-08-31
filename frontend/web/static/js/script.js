// Global variables
let tickPollingInterval = null;
let noTicksCount = 0;

// Load account balance
async function loadStats() {  
    try {
        let response = await fetch("/stats");  
        let data = await response.json();
        if (data.balance) {
            document.getElementById("balance").innerText = data.balance;
        }
    } catch (error) {
        console.error("Error loading stats:", error);
    }
}

// Load available markets
async function loadMarkets() {
    try {
        let response = await fetch("/markets");
        let data = await response.json();
        
        if (data.markets && Array.isArray(data.markets)) {
            const marketSelect = document.getElementById("marketSelect");
            marketSelect.innerHTML = ""; // Clear existing options
            
            // Group markets by market name
            const marketGroups = {};
            data.markets.forEach(market => {
                const marketName = market.market || "Other";
                if (!marketGroups[marketName]) {
                    marketGroups[marketName] = [];
                }
                marketGroups[marketName].push(market);
            });
            
            // Create option groups for each market
            Object.keys(marketGroups).sort().forEach(marketName => {
                const optgroup = document.createElement("optgroup");
                optgroup.label = marketName;
                
                // Add options for each symbol in this market
                marketGroups[marketName].forEach(market => {
                    const option = document.createElement("option");
                    option.value = market.symbol;
                    option.textContent = market.display_name || market.symbol;
                    
                    // Add a visual indicator for markets likely to have tick streams
                    if (market.has_tick_stream === false) {
                        option.textContent += " (Limited data)";
                        option.classList.add("limited-data");
                    }
                    
                    optgroup.appendChild(option);
                });
                
                marketSelect.appendChild(optgroup);
            });
            
            // Enable the subscribe button
            document.getElementById("subscribeBtn").disabled = false;
            
            // Hide the loading message
            document.getElementById("marketLoadingMsg").style.display = "none";
        }
    } catch (error) {
        console.error("Error loading markets:", error);
        document.getElementById("marketLoadingMsg").textContent = "Error loading markets. Please try again.";
    }
}

// Subscribe to tick updates for selected symbol
async function subscribeTicks() {
    const marketSelect = document.getElementById("marketSelect");
    const symbol = marketSelect.value;
    const statusAlert = document.getElementById("statusAlert");
    
    if (!symbol) {
        showAlert("Please select a market first", "warning");
        return;
    }
    
    // Show loading state
    document.getElementById("subscribeBtn").disabled = true;
    document.getElementById("subscribeBtn").textContent = "Subscribing...";
    statusAlert.style.display = "none";
    
    try {
        const response = await fetch("/subscribe", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ symbol })
        });
        
        const data = await response.json();
        
        if (data.status === "subscribed") {
            // Update UI to show subscription is active
            document.getElementById("subscribeBtn").style.display = "none";
            document.getElementById("unsubscribeBtn").style.display = "inline-block";
            document.getElementById("currentSymbol").textContent = symbol;
            document.getElementById("subscriptionStatus").style.display = "block";
            
            // Clear any previous alerts
            statusAlert.style.display = "none";
            
            // Start polling for ticks
            startTickPolling();
        } else if (data.status === "error") {
            // Show error message
            showAlert(data.message, "error");
            
            // Reset button
            document.getElementById("subscribeBtn").disabled = false;
            document.getElementById("subscribeBtn").textContent = "Subscribe to Ticks";
        }
    } catch (error) {
        console.error("Error subscribing to ticks:", error);
        showAlert("Failed to subscribe. Please try again.", "error");
        
        // Reset button
        document.getElementById("subscribeBtn").disabled = false;
        document.getElementById("subscribeBtn").textContent = "Subscribe to Ticks";
    }
}

// Show an alert message
function showAlert(message, type) {
    const statusAlert = document.getElementById("statusAlert");
    statusAlert.textContent = message;
    statusAlert.className = "alert";
    
    switch (type) {
        case "info":
            statusAlert.classList.add("alert-info");
            break;
        case "warning":
            statusAlert.classList.add("alert-warning");
            break;
        case "error":
            statusAlert.classList.add("alert-error");
            break;
    }
    
    statusAlert.style.display = "block";
}

// Unsubscribe from tick updates
async function unsubscribeTicks() {
    try {
        const response = await fetch("/unsubscribe", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        if (data.status === "unsubscribed") {
            // Update UI to show subscription is inactive
            document.getElementById("subscribeBtn").style.display = "inline-block";
            document.getElementById("subscribeBtn").disabled = false;
            document.getElementById("subscribeBtn").textContent = "Subscribe to Ticks";
            document.getElementById("unsubscribeBtn").style.display = "none";
            document.getElementById("subscriptionStatus").style.display = "none";
            document.getElementById("streamStatus").style.display = "none";
            
            // Stop polling for ticks
            stopTickPolling();
            
            // Clear the ticks table
            document.getElementById("ticksTableBody").innerHTML = "";
            
            // Clear any alerts
            document.getElementById("statusAlert").style.display = "none";
        }
    } catch (error) {
        console.error("Error unsubscribing from ticks:", error);
        showAlert("Failed to unsubscribe. Please try again.", "error");
    }
}

// Start polling for ticks
function startTickPolling() {
    // Clear any existing interval
    stopTickPolling();
    
    // Reset counter
    noTicksCount = 0;
    
    // Poll for ticks every second
    tickPollingInterval = setInterval(loadTicks, 1000);
    
    // Load ticks immediately
    loadTicks();
}

// Stop polling for ticks
function stopTickPolling() {
    if (tickPollingInterval) {
        clearInterval(tickPollingInterval);
        tickPollingInterval = null;
    }
}

// Load latest ticks
async function loadTicks() {
    try {
        const response = await fetch("/ticks");
        const data = await response.json();
        
        // Update stream status indicator
        updateStreamStatus(data.available);
        
        if (data.ticks && Array.isArray(data.ticks)) {
            if (data.ticks.length > 0) {
                // Check if we have a special "unavailable" status tick
                const lastTick = data.ticks[data.ticks.length - 1];
                if (lastTick.status === "unavailable") {
                    // Show unavailable message
                    showAlert(lastTick.message, "warning");
                    // Add a special row to the table
                    addUnavailableTickRow(lastTick);
                    // Stop polling to avoid repeated messages
                    stopTickPolling();
                    return;
                }
                
                // We have ticks, update the table
                updateTicksTable(data.ticks);
                noTicksCount = 0;
            } else {
                // No ticks yet, increment counter
                noTicksCount++;
                
                // After 10 seconds with no ticks, show a message
                if (noTicksCount >= 10) {
                    showAlert("No tick data received yet. This market might have limited data availability.", "warning");
                }
            }
        }
    } catch (error) {
        console.error("Error loading ticks:", error);
    }
}

// Update the stream status indicator
function updateStreamStatus(isAvailable) {
    const streamStatus = document.getElementById("streamStatus");
    const statusIndicator = document.getElementById("statusIndicator");
    const statusText = document.getElementById("statusText");
    
    streamStatus.style.display = "block";
    
    if (isAvailable) {
        statusIndicator.className = "status-indicator status-active";
        statusText.textContent = "Active";
        statusText.className = "badge badge-success";
    } else {
        statusIndicator.className = "status-indicator status-inactive";
        statusText.textContent = "Inactive";
        statusText.className = "badge badge-danger";
    }
}

// Add a special row for unavailable tick streams
function addUnavailableTickRow(tick) {
    const tableBody = document.getElementById("ticksTableBody");
    tableBody.innerHTML = ""; // Clear existing rows
    
    const row = document.createElement("tr");
    row.className = "tick-unavailable";
    
    // Format the timestamp
    const date = new Date(tick.timestamp * 1000);
    const timeString = date.toLocaleTimeString();
    
    // Create cells
    row.innerHTML = `
        <td>${timeString}</td>
        <td colspan="3">${tick.message}</td>
    `;
    
    tableBody.appendChild(row);
}

// Update the ticks table with the latest data
function updateTicksTable(ticks) {
    const tableBody = document.getElementById("ticksTableBody");
    
    // Clear existing rows if we have more than 20
    if (tableBody.children.length > 20) {
        tableBody.innerHTML = "";
    }
    
    // Add new ticks to the table (newest first)
    ticks.slice(-10).reverse().forEach(tick => {
        // Skip special status ticks
        if (tick.status === "unavailable") {
            return;
        }
        
        // Check if we already have this tick (by timestamp)
        const existingRow = document.querySelector(`tr[data-timestamp="${tick.timestamp}"]`);
        if (existingRow) {
            return; // Skip if we already have this tick
        }
        
        const row = document.createElement("tr");
        row.setAttribute("data-timestamp", tick.timestamp);
        
        // Format the timestamp
        const date = new Date(tick.timestamp * 1000);
        const timeString = date.toLocaleTimeString();
        
        // Create cells
        row.innerHTML = `
            <td>${timeString}</td>
            <td>${tick.quote || "N/A"}</td>
            <td>${tick.bid || "N/A"}</td>
            <td>${tick.ask || "N/A"}</td>
        `;
        
        // Add to the beginning of the table
        tableBody.insertBefore(row, tableBody.firstChild);
        
        // Limit to 20 rows
        if (tableBody.children.length > 20) {
            tableBody.removeChild(tableBody.lastChild);
        }
    });
}

// Initialize the dashboard
window.onload = function() {
    // Load initial data
    loadStats();
    loadMarkets();
    
    // Set up polling for account balance
    setInterval(loadStats, 5000);
    
    // Hide unsubscribe button initially
    document.getElementById("unsubscribeBtn").style.display = "none";
    document.getElementById("subscriptionStatus").style.display = "none";
    document.getElementById("streamStatus").style.display = "none";
};