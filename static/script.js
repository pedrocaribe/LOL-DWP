const regionCtn = document.querySelector('.region-container');
const regionDropdown = document.querySelector('.region-dropdown');
const regionBtnText = document.querySelector('.region-button-text')

regionCtn.addEventListener('click', () => {
  regionDropdown.classList.toggle('show'); // Toggle visibility of dropdown
});

// Handle selecting a region from the dropdown (example)
regionDropdown.addEventListener('click', (event) => {
  const selectedRegion = event.target.textContent; // Get the text content of the clicked list item
  regionBtnText.textContent = selectedRegion; // Update the button text
  regionDropdown.classList.remove('show'); // Hide the dropdown after selection
});

document.addEventListener('click', (event) => {
  const isClickInsideContainer = regionCtn.contains(event.target);
  const isClickInsideDropdown = regionDropdown.contains(event.target);

  if (!isClickInsideContainer && !isClickInsideDropdown) {
    regionDropdown.classList.remove('show'); // Close if clicked outside
  }
});