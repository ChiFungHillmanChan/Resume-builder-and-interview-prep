function populateMonths(monthSelect) {
    for (let month = 1; month <= 12; month++) {
        let option = document.createElement('option');
        option.value = month < 10 ? '0' + month : month; // Ensure two digits format
        option.textContent = month; // Display month as 1-12
        monthSelect.appendChild(option);
    }
}

// Function to populate years (from 1970 to current year)
function populateYears(yearSelect) {
    const currentYear = new Date().getFullYear();
    for (let year = currentYear; year >= 1970; year--) {
        let option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    }
}

// Populate start and end date selectors
window.onload = function() {
    // Get the select elements
    const startMonthSelect = document.getElementById('startMonth');
    const startYearSelect = document.getElementById('startYear');
    const endMonthSelect = document.getElementById('endMonth');
    const endYearSelect = document.getElementById('endYear');

    // Populate the month and year dropdowns
    populateMonths(startMonthSelect);
    populateMonths(endMonthSelect);
    populateYears(startYearSelect);
    populateYears(endYearSelect);
};