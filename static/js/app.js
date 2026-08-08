// Client-side validation for the School Management & Student Information System.
// Server-side validation is also enforced in app.py; this improves user experience.

document.addEventListener("DOMContentLoaded", function () {
    var phoneInput = document.querySelector("input[name='phone']");
    var form = phoneInput ? phoneInput.closest("form") : null;

    if (form) {
        form.addEventListener("submit", function (event) {
            var phone = phoneInput.value.trim();
            if (phone && !/^[0-9]{10}$/.test(phone)) {
                event.preventDefault();
                alert("Enter a valid 10-digit phone number.");
            }
        });
    }

    var marksInput = document.querySelector("input[name='marks']");
    if (marksInput) {
        marksInput.closest("form").addEventListener("submit", function (event) {
            var marks = parseFloat(marksInput.value);
            if (isNaN(marks) || marks < 0 || marks > 100) {
                event.preventDefault();
                alert("Marks must be between 0 and 100.");
            }
        });
    }
});
