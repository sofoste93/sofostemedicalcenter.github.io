// Initialize variables for form pages
let currentPage = 1;
let language = "en";
const totalFormPages = 3;

// Set up event listeners
document.getElementById("language-submit").addEventListener("click", onLanguageSubmit);
document.querySelectorAll(".btn-next").forEach(btn => btn.addEventListener("click", onNextPage));
document.querySelectorAll(".btn-back").forEach(btn => btn.addEventListener("click", onPrevPage));
document.getElementById("btn-submit").addEventListener("click", onSubmitForm);

// Functions
function onLanguageSubmit() {
    language = document.getElementById("language-selection").value;
    // Load translations, render the Enter PIN page, and apply translations
    // ...
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
    // Validate form data, show the summary page, and apply translations
    // ...
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
