document.addEventListener('DOMContentLoaded', function() {

    // Custom Functions
    function HTMLDecode(html) {
        var txt = document.createElement("textarea");
        txt.innerHTML = html;
        return txt.value;
    }
    function addTag(tag) {
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = "tag";
        checkbox.checked = true;
        checkbox.classList.add("form-check-input");
        checkbox.value = tag;

        const label = document.createElement("label");
        label.classList.add("form-check-label");
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(tag));

        tagList.appendChild(label);
    }

    const post_id = id;

    const image = document.getElementById('image-input');
    const preview = document.getElementById('preview');
    const change = document.getElementById('change_status');
    const remove_preview = document.getElementById('remove_preview');
    const title = document.getElementById('title');
    const contents = document.getElementById('contents');
    const tagInput = document.getElementById("tagInput");
    const tagList = document.getElementById("tagList");
    const submit_button = document.getElementById("submit");


    // Remove current image button
    remove_preview.onclick = function() {
        document.getElementById('preview').src = '';
        remove_preview.style.display = 'none';
        image.value = null;
        change.value = "changed";
    };

    title.addEventListener('keyup', function() {
        if (title.value.length == 70) {
            document.getElementById("warning1").innerHTML = "Maximum characters reached!";

            setTimeout(function() {
                document.getElementById("warning1").innerHTML = "";
            }, 3000);
        } else {
            document.getElementById("warning1").innerHTML = "";
        }
    });

    contents.addEventListener('keyup', function() {
        if (contents.value.length == 640) {
            document.getElementById("warning2").innerHTML = "Maximum characters reached!";

            setTimeout(function() {
                document.getElementById("warning2").innerHTML = "";
            }, 3000);
        } else {
            document.getElementById("warning2").innerHTML = "";
        }
    });

    tagInput.addEventListener("keyup", function (event) {
        if (event.key === " " && tagInput.value.trim() !== "") {
            let bool1 = true;
            let tag = tagInput.value.trim();
            for (var i = 0; i < list.length; i++) {
                list[i] = HTMLDecode(list[i]);
            }
            if (tag[0] == '#') {
                tag = tag.slice(1);
                let tag_proper = tag.charAt(0).toUpperCase() + tag.slice(1).toLowerCase();

                let current_tags = document.getElementsByName('tag');
                for (let current_tag of current_tags) {
                    if (current_tag.value == tag_proper) {
                        bool1 = false;
                    }
                }

                if (list.includes(tag_proper) && bool1) {
                    addTag(tag_proper);
                    document.getElementById('warning3').innerHTML = ""
                } else {
                    document.getElementById('warning3').innerHTML = "Tag already included or does not exist!"
                }

                tagInput.value = "";
            } else if (tagList.innerHTML == "") {
                document.getElementById('warning3').innerHTML = "Include at least one tag with your post!";
            }
            else {
                document.getElementById('warning3').innerHTML = "Tags must start with '#'!";
                tagInput.value = "";
            }
        }
    });

    // Add preview if valid image is uploaded
    image.onchange = function() {
        if (!image.value || image.value == "") {
            preview.src = "";
            image.value = null;
            remove_preview.style.display = 'none';
        }
        else if (image.value.endsWith(".png") || image.value.endsWith(".jfif") || image.value.endsWith(".pjp") || image.value.endsWith(".jpg") || image.value.endsWith(".pjpeg") || image.value.endsWith(".jpeg")) {
            var reader = new FileReader();
            reader.onload = function() {
                remove_preview.style.display = 'block';
                preview.src = reader.result;
            };
            reader.readAsDataURL(image.files[0]);
        }
        else {
            preview.src = "";
            remove_preview.style.display = 'none';
            image.value = null;
            document.getElementById('warning0').innerHTML = "Supported image formats are PNG/JPG!";
            setTimeout(function() {
                document.getElementById('warning0').innerHTML = "";
            }, 3000);
        }

        change.value = "changed";
    };

    // Check tags
    submit_button.onclick = function() {
        if (tagList.innerHTML == "") {
            document.getElementById('warning3').innerHTML = "Include at least one tag with your post!";
            return false;
        }

        var tags = document.getElementsByName("tag");

        var check_tag = false;
        for (tag of tags) {
            if (tag.checked == true) {
                check_tag = true;
                break;
            }
        }

        if (check_tag == false) {
            document.getElementById('warning3').innerHTML = "Select at least one tag with your post!";
            setTimeout(function() {
                document.getElementById('warning3').innerHTML = "";
            }, 3000);
            return false;
        }

        console.log(post_id);

        // Send post_id to server
        const postid_input = document.createElement('input');
        postid_input.type = 'hidden';
        postid_input.name = 'post_id';
        postid_input.value = post_id;

        document.getElementById('form').appendChild(postid_input);
        return true;
    };
});