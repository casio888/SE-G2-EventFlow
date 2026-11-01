document.addEventListener("DOMContentLoaded", function() {
    const body = document.getElementById("timeslot-body");

    if (!body) {
        return;
    }

    const prefix = body.dataset.prefix;
    const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
    const initialForms = Number(document.getElementById(`id_${prefix}-INITIAL_FORMS`).value);
    const emptyRow = document.getElementById("timeslot-empty-row");
    const addButton = document.getElementById("timeslot-add");
    const indexPattern = new RegExp(`${prefix}-\\d+-`);

    function toMinutes(value) {
        const [hours, minutes] = value.split(":").map(Number);
        return hours * 60 + minutes;
    }

    function updateDuration(row) {
        const start = row.querySelector("input[name$='-start']").value;
        const end = row.querySelector("input[name$='-end']").value;
        const minutes = start && end ? toMinutes(end) - toMinutes(start) : 0;
        row.querySelector(".timeslot-duration").textContent = minutes > 0 ? `${minutes} min` : "–";
    }

    function reindexRows() {
        const rows = body.querySelectorAll(".timeslot-row");

        rows.forEach(function(row, index) {
            const replacement = `${prefix}-${index}-`;

            row.querySelectorAll("input").forEach(function(input) {
                input.name = input.name.replace(indexPattern, replacement);
                input.id = input.id.replace(indexPattern, replacement);
            });

            row.querySelectorAll("label").forEach(function(label) {
                label.htmlFor = label.htmlFor.replace(indexPattern, replacement);
            });
        });

        totalForms.value = rows.length;
    }

    function addRow() {
        const index = Number(totalForms.value);
        const template = document.createElement("template");
        template.innerHTML = emptyRow.innerHTML.replaceAll("__prefix__", index);

        const row = template.content.querySelector(".timeslot-row");
        body.appendChild(row);
        totalForms.value = index + 1;
        row.querySelector("input[name$='-start']").focus();
    }

    addButton.addEventListener("click", addRow);

    body.addEventListener("click", function(event) {
        const removeButton = event.target.closest(".timeslot-remove");

        if (removeButton && body.querySelectorAll(".timeslot-row").length > initialForms) {
            removeButton.closest(".timeslot-row").remove();
            reindexRows();
        }
    });

    body.addEventListener("input", function(event) {
        const row = event.target.closest(".timeslot-row");

        if (row) {
            updateDuration(row);
        }
    });

    body.querySelectorAll(".timeslot-row").forEach(updateDuration);
});
