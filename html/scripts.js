// scripts.js

// Function to toggle the value and specifier fields
function toggleFields() {
    const dlTypeGet = document.getElementById("dl_type_get");
    const valueField = document.getElementById("value");
    const specifierField = document.getElementById("specifier");

    if (dlTypeGet.checked) {
        valueField.setAttribute("disabled", "disabled");
        specifierField.setAttribute("disabled", "disabled");
    } else {
        valueField.removeAttribute("disabled");
        specifierField.removeAttribute("disabled");
    }
}

// Initialize the state on page load
document.addEventListener('DOMContentLoaded', (event) => {
    toggleFields();
});

// Function to handle the send request (with validation for CMD specifier requirement)
function send_request() {
    var rk = document.getElementById("routing_key").value;
    console.log(rk);

    var dl_types = document.getElementsByName("dl_type");
    console.log(dl_types);
    var dl_type_checked = "GET";
    for (var i = 0; i < dl_types.length; i++) {
        if (dl_types[i].checked) dl_type_checked = dl_types[i].value;
    }
    if (dl_type_checked === "SET") {
        dl_type_checked = "PUT";
    } else if (dl_type_checked === "CMD") {
        dl_type_checked = "POST";
    }

    var value = Number(document.getElementById('value').value);
    var specifier = document.getElementById('specifier').value;
    var lockout_key = document.getElementById('lockout_key').value;

    // Validation for CMD specifier requirement
    if (dl_type_checked === "POST" && !specifier) {
        alert("Specifier is mandatory for CMD actions.");
        document.getElementById('specifier').focus();
        return false;
    }

    var payload = { "values": value };
    console.log(payload);
    var url = "http://localhost:8080/dl/" + rk;

    $.ajax({
        url: url,
        type: dl_type_checked,
        headers: {
            'lockout-key': lockout_key,
            'specifier': specifier
        },
        data: JSON.stringify(payload),
        contentType: "application/json",
        dataType: "json",
        success: function(data, status, xhr) {
            console.log(`Success: ${data}`);
            var result = document.getElementById("result");
            result.value = "Success: " + xhr.responseText;
        },
        error: function(xhr, status, error) {
            console.log("Error: " + xhr.responseText);
            var result = document.getElementById("result");
            result.value = xhr.responseText;
        }
    });

    return false;
}
