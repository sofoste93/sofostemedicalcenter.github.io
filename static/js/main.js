// Initialize variables for form pages
let currentPage = 1;
let language = "en";
const totalFormPages = 3;
const summaryData = {};

// Set up event listeners
document.getElementById("language-submit").addEventListener("click", onLanguageSubmit);
document.querySelectorAll(".btn-next").forEach(btn => btn.addEventListener("click", onNextPage));
document.querySelectorAll(".btn-back").forEach(btn => btn.addEventListener("click", onPrevPage));
document.getElementById("btn-submit").addEventListener("click", onSubmitForm);

// Functions
function onLanguageSubmit() {
    language = document.getElementById("language-selection").value;
    loadTranslations();
}

function onNextPage() {
    if (currentPage < totalFormPages) {
        currentPage++;
        showFormPage(currentPage);
    }
}

function onPrevPage() {
    if (currentPage > 1) {
        currentPage--;
        showFormPage(currentPage);
    }
}

function onSubmitForm() {
    // Validate form data
    const formData = getFormData();
    if (!validateFormData(formData)) {
        alert("Please fill out all required fields.");
        return;
    }

    // Show the summary page and apply translations
    showSummaryPage(formData);
    applyTranslations();
}

function getFormData() {
    const formData = {
        // Add all the form fields and their values to this object
        sex: document.getElementById("sex").value,
        last_name: document.getElementById("last_name").value,
        first_name: document.getElementById("first_name").value,
        date_of_birth: document.getElementById("date_of_birth").value,
        place_of_birth: document.getElementById("place_of_birth").value,
        age: document.getElementById("age").value,
        recent_illnesses: document.getElementById("recent_illnesses").value,
        allergies: document.getElementById("allergies").value,
        heart_ailments: document.getElementById("heart_ailments").value,
        asthma: document.getElementById("asthma").value,
        diabetes: document.getElementById("diabetes").value,
        medications: document.getElementById("medications").value,
        dietary_supplements: document.getElementById("dietary_supplements").value,
        treatments: document.getElementById("treatments").value
    };
    return formData;
}

function validateFormData(data) {
    // You can add more specific validation rules here
    for (const key in data) {
        if (!data[key]) {
            return false;
        }
    }
    return true;
}

document.querySelectorAll(".language-button").forEach(btn => btn.addEventListener("click", onLanguageSubmit));

function onLanguageSubmit() {
    language = this.getAttribute('data-language');
    loadTranslations();
    window.location.href = "/enter-pin";
}

document.getElementById("pin-submit").addEventListener("click", onPinSubmit);

async function onPinSubmit(event) {
    event.preventDefault();
    const pin = document.getElementById("pin").value;

    const response = await fetch('/generate-pin');
    if (response.ok) {
        const data = await response.json();
        const generatedPin = data.pin;
        if (pin === generatedPin) {
            window.location.href = "/form-page-1";
        } else {
            alert("Incorrect PIN. Please try again.");
        }
    } else {
        alert("Error: Could not verify PIN.");
    }
}

function showFormPage(pageNumber) {
    // Hide all form pages and show the specified form page
    document.querySelectorAll(".form-page").forEach(page => page.style.display = "none");
    document.getElementById(`form-page-${pageNumber}`).style.display = "block";
}

document.getElementById("btn-request-pin").addEventListener("click", onRequestPin);

async function onRequestPin() {
    try {
        const response = await fetch('/generate-pin');
        if (response.ok) {
            const data = await response.json();
            const pin = data.pin;
            // Show the generated PIN to the user or send it via SMS (later)
            // ...
        } else {
            console.error("Error fetching PIN:", response.statusText);
        }
    } catch (error) {
        console.error("Error fetching PIN:", error);
    }
}

let translations = {};

async function loadTranslations() {
    try {
        const response = await fetch(`/static/translations/${language}.json`);
        if (response.ok) {
            translations = await response.json();
            applyTranslations();
        } else {
            console.error("Error fetching translations:", response.statusText);
        }
    } catch (error) {
        console.error("Error fetching translations:", error);
    }
}

function applyTranslations() {
    // Iterate through translation keys and update the text content of matching elements
    Object.keys(translations).forEach(key => {
        const elements = document.getElementsByClassName(key);
        Array.prototype.forEach.call(elements, el => {
            el.textContent = translations[key];
        });
    });
}

async function onPinSubmit() {
    const pin = document.getElementById("pin").value;

    // Verify the PIN by comparing it with the generated PIN
    // You may want to implement server-side verification for a real-world application
    const response = await fetch('/generate-pin');
    if (response.ok) {
        const data = await response.json();
        const generatedPin = data.pin;
        if (pin === generatedPin) {
            // Render the first form page
            showFormPage(1);
            applyTranslations();
        } else {
            alert("Incorrect PIN. Please try again.");
        }
    } else {
        alert("Error: Could not verify PIN.");
    }
}

function showFormPage(pageNumber) {
    // Hide all form pages and show the specified form page
    document.querySelectorAll(".form-page").forEach(page => page.style.display = "none");
    document.getElementById(`form-page-${pageNumber}`).style.display = "block";
}

function showSummaryPage(formData) {
    const summaryElement = document.getElementById("summary-data");
    summaryElement.innerHTML = "";
    for (const key in formData) {
        const dataElement = document.createElement("p");
        dataElement.textContent = `${translations[key] || key}: ${formData[key]}`;
        summaryElement.appendChild(dataElement);
    }

    showFormPage("summary");
}

document.getElementById("btn-request-pin").addEventListener("click", onRequestPin);

