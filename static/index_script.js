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

// Click Outside Logic
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

const searchForm = document.getElementById("search")
const field1 = document.getElementById("game_name_1")
const field2 = document.getElementById("game_name_2")

searchForm.addEventListener('submit', function(event) {
    const re = /\s*(?:#|$)\s*/;

    const name1 = field1.value.trim().split(re).join(" ");
    const name2 = field2.value.trim().split(re).join(" ");

    if (name1 == name2) {
        event.preventDefault(); // Prevent form submission

        Swal.fire({
            title: "Players must not be the same!",
            width: 500,
            color: "#716add",
            background: "#fff",
            backdrop: `
                rgba(0,0,123,0.2)
                url("/images/nyan-cat.gif")
                left top
                no-repeat
            `
        });
    }
});