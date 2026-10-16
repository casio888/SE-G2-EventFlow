document.addEventListener("DOMContentLoaded", function () {
    const timeslotSelect = document.getElementById("id_timeslot");
    const durationDisplay = document.getElementById("timeslot-duration");

    function updateTimeslotDuration() {
        const selectedOption = timeslotSelect.selectedOptions[0];
        const duration = selectedOption?.dataset.duration;
        durationDisplay.textContent = duration
            ? `${duration} Minuten`
            : "";
    }

    timeslotSelect.addEventListener("change", updateTimeslotDuration);
    updateTimeslotDuration();
});
