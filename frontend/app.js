async function handleQuery() {
    const input = document.getElementById('queryInput');
    const resultsContainer = document.getElementById('resultsContainer');
    const sqlPreview = document.getElementById('sqlPreview');
    
    // Clear previous results
    resultsContainer.innerHTML = '<div class="loading">Processing...</div>';
    sqlPreview.textContent = '';

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: input.value.trim()
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }

        const data = await response.json();
        
        // Display results
        sqlPreview.textContent = data.sql;
        resultsContainer.innerHTML = data.html;
        
        // Add result count
        const countDiv = document.createElement('div');
        countDiv.className = 'result-count';
        countDiv.textContent = `${data.row_count} rows returned`;
        resultsContainer.prepend(countDiv);

    } catch (error) {
        resultsContainer.innerHTML = `
            <div class="error-alert">
                <div class="error-icon">!</div>
                <div class="error-message">${error.message}</div>
            </div>
        `;
    }
}