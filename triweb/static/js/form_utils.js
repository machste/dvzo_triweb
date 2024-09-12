const form = document.getElementById("form");
const form_inputs = document.querySelectorAll("#form input,select,textarea");
const form_save_btn = document.getElementById("form-save-btn");
const form_reset_btn = document.getElementById("form-reset-btn");

function save_original_values() {
    for (const el of form_inputs) {
        if (el.nodeName == "SELECT" && el.multiple) {
            el.orig_value = []
            for (const option of el.selectedOptions) {
                el.orig_value.push(option.index)
            }
        } else {
            el.orig_value = el.value;
        }
    }
}

function have_values_changed() {
    let changed = false;
    for (const el of form_inputs) {
        if (el.nodeName == "SELECT" && el.multiple) {
            if (el.selectedOptions.length != el.orig_value.length) {
                changed = true;
            } else {
                for (let i = 0; i < el.orig_value.length; i++) {
                    if (el.orig_value[0] !== el.selectedOptions[0].index);
                }
                for (const option of el.selectedOptions) {
                    el.orig_value.push(option.index);
                }
            }
        } else {
            if (el.orig_value !== el.value) {
                changed = true;
            }
        }
        if (changed) {
            break;
        }
    }
    return changed;
}

function disable_form_buttons(state=true) {
    form_save_btn.disabled = state;
    form_reset_btn.disabled = state;
}

function update_form_buttons() {
    disable_form_buttons(!have_values_changed());
}

function toggle_pwd_input(n=1) {
    let password = document.getElementById(`password${n}`);
    let eye_open = document.getElementById(`eye-open${n}`);
    let eye_closed = document.getElementById(`eye-closed${n}`);

    eye_closed.classList.remove("d-none");

    if (password.type === "password") {
        password.type = "text";
        eye_open.style.display = "none";
        eye_closed.style.display = "block";
    } else {
        password.type = "password";
        eye_open.style.display = "block";
        eye_closed.style.display = "none";
    }
}

save_original_values();
form.addEventListener("input", update_form_buttons);
form.addEventListener("reset", disable_form_buttons);
