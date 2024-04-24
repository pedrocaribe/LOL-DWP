// Constants

const regionCtn = document.querySelector(".region-container")
const regionDropdown = document.querySelector(".region-dropdown")
const regionBtnText = document.querySelector(".region-button-text")
const playerInputs = document.querySelectorAll(".player")

regionCtn.addEventListener("click", () => {
    regionDropdown.classList.toggle("show") // Toggle visibility of dropdown
})

// Handle selecting a region from the dropdown and updating div and hidden input
regionDropdown.addEventListener("click", (event) => {
    const selectedRegion = event.target.textContent // Get the text content of the clicked list item
    const hiddenInput = document.getElementById("selected-region")

    regionBtnText.textContent = selectedRegion // Update the button text
    hiddenInput.value = selectedRegion
    regionDropdown.classList.remove("show") // Hide the dropdown after selection
    
    event.stopPropagation(); // Stop the click event from bubbling up 
})

document.addEventListener("click", (event) => {
    const isClickInsideContainer = regionCtn.contains(event.target)
    const isClickInsideDropdown = regionDropdown.contains(event.target)

    if (!isClickInsideContainer && !isClickInsideDropdown) {
        regionDropdown.classList.remove("show") // Close dropdown if clicked outside
    }
})

// Placeholder for your existing click-outside logic
document.addEventListener("click", (event) => {
    let clickedInside = false

    playerInputs.forEach((playerInput) => {
        if (playerInput.contains(event.target)) {
            clickedInside = true
            return // Stop iteration since we found a match
        }
    })

    if (!clickedInside) {
        playerInputs.forEach((playerInput) => {
            const hiddenDiv = playerInput.querySelector("label")
            const hiddenDiv2 = playerInput.querySelector(".tag-line")
            const inputField = playerInput.querySelector("input")

            if (inputField && inputField.value !== "") {
                hiddenDiv.style.display = "none"
                hiddenDiv2.style.display = "none"
            } else {
                hiddenDiv.style.display = ""
                hiddenDiv2.style.display = ""
            }
        })
    }
})

// Logic for input focus and blur
playerInputs.forEach((playerInput) => {
    const inputField = playerInput.querySelector("input")

    inputField.addEventListener("focus", () => {
        const hiddenDiv = playerInput.querySelector("label")
        const hiddenDiv2 = playerInput.querySelector(".tag-line")
        hiddenDiv.style.display = "none"
        hiddenDiv2.style.display = "none"
    })

    inputField.addEventListener("blur", () => {
        if (inputField.value === "") {
            const hiddenDiv = playerInput.querySelector("label")
            const hiddenDiv2 = playerInput.querySelector(".tag-line")
            hiddenDiv.style.display = "" // Reset to default
            hiddenDiv2.style.display = "" // Reset to default
        }
    })
})

