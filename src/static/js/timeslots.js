
function addTimeslot(start="", ende="", dauer="", kategorie="") {
    const tbody = document.getElementById("timeslot-body");
    const row = document.createElement("tr");

    row.innerHTML = `
        <td><input type="time" class="ts-start" value="${start}"></td>
        <td><input type="time" class="ts-ende" value="${ende}"></td>
        <td><input type="number" class="ts-dauer" value="${dauer}" min="0"></td>
        <td><input type="text" class="ts-kategorie" value="${kategorie}"></td>
        <td><button type="button" onclick="this.parentElement.parentElement.remove()">–</button></td>
    `;

    tbody.appendChild(row);
}

document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("event-create-form");
    const timeslotsInput = document.getElementById("id_timeslots");

    if (!form || !timeslotsInput) {
        return;
    }

    form.addEventListener("submit", function() {
        const rows = document.querySelectorAll("#timeslot-body tr");
        const data = [];

        rows.forEach(row => {
            data.push({
                start: row.querySelector(".ts-start").value,
                ende: row.querySelector(".ts-ende").value,
                dauer: row.querySelector(".ts-dauer").value,
                kategorie: row.querySelector(".ts-kategorie").value
            });
        });

        timeslotsInput.value = JSON.stringify(data);
    });
});
