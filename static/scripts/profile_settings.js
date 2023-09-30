document.addEventListener('DOMContentLoaded', function() {
    function HTMLDecode(html) {
        var txt = document.createElement("textarea");
        txt.innerHTML = html;
        return txt.value;
    }
    function addInterest(interest) {
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = "interest";
        checkbox.checked = true;
        checkbox.classList.add("form-check-input");
        checkbox.value = interest;

        const label = document.createElement("label");
        label.classList.add("form-check-label");
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(interest));

        interestList.appendChild(label);
    }

    const preview = document.getElementById('preview');
    const image = document.getElementById('image_input');

    image.onchange = function() {
        if (image.value.endsWith(".png") || image.value.endsWith(".jfif") || image.value.endsWith(".pjp") || image.value.endsWith(".jpg") || image.value.endsWith(".pjpeg") || image.value.endsWith(".jpeg")) {
            const reader = new FileReader();
            reader.onload = function() {
                preview.src = reader.result;
            };
            reader.readAsDataURL(image_input.files[0]);
        } else if (!image.value || image.value == "") {
            image.value = null;
        } else {
            image.value = null;
            document.getElementById('warning0').innerHTML = "Supported image formats are PNG/JPG!";
            setTimeout(function() {
                document.getElementById('warning0').innerHTML = "";
            }, 3000);
        }
    };

    const interestInput = document.getElementById("interestInput");
    const interestList = document.getElementById("interestList");

    interestInput.addEventListener("keyup", function (event) {
        if (event.key === " " && interestInput.value.trim() !== "") {
            let bool1 = true;
            let interest = interestInput.value.trim();
            for (var i = 0; i < list.length; i++) {
                list[i] = HTMLDecode(list[i]);
            }
            if (interest[0] == '#') {
                interest = interest.slice(1);
                let interest_proper = interest.charAt(0).toUpperCase() + interest.slice(1).toLowerCase();

                let current_interests = document.getElementsByName('interest');
                for (let current_interest of current_interests) {
                    if (current_interest.value == interest_proper) {
                        bool1 = false;
                    }
                }

                if (list.includes(interest_proper) && bool1) {
                    addInterest(interest_proper);
                    document.getElementById('warning').innerHTML = ""
                } else {
                    document.getElementById('warning').innerHTML = "Interest already included or does not exist!"
                }

                interestInput.value = "";
            } else {
                document.getElementById('warning').innerHTML = "Interests must start with '#'!";
                interestInput.value = "";
            }
        }
    });
});