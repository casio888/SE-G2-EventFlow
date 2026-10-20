
function addTimeslot(start="", end="", duration="", category="") {
    const tbody = document.getElementById("timeslot-body");
    const row = document.createElement("tr");

    row.innerHTML = `
        <td><input type="time" class="ts-start" value="${start}"></td>
        <td><input type="time" class="ts-end" value="${end}"></td>
        <td><input type="number" class="ts-duration" value="${duration}" min="0"></td>
        <td><input type="text" class="ts-category" value="${category}"></td>
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
                end: row.querySelector(".ts-end").value,
                duration: row.querySelector(".ts-duration").value,
                category: row.querySelector(".ts-category").value
            });
        });

        timeslotsInput.value = JSON.stringify(data);
    });
});
