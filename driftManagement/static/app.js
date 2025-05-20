document.addEventListener("DOMContentLoaded", () => {
    // Toggle
    const toggleButtons = document.querySelectorAll(".toggle-button");

    toggleButtons.forEach(button => {
        button.addEventListener("click", () => {
            const targetId = button.getAttribute("data-target");
            const target = document.getElementById(targetId);
            if (target.style.display === "none") {
                target.style.display = "block";
                button.textContent = "Hide";
            } else {
                target.style.display = "none";
                button.textContent = "Show";
            }
        });
    });

    // Refresh button event
    const refreshBtn = document.getElementById("refresh-btn");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", () => {
            location.reload();
        });
    }

    // auto-refresh data every 60 seconds 
    setInterval(() => {
        fetch(window.location.href)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, "text/html");

                const newSnapshots = doc.querySelector("#snapshot-block").innerHTML;
                const newDrift = doc.querySelector("#drift-block").innerHTML;

                document.querySelector("#snapshot-block").innerHTML = newSnapshots;
                document.querySelector("#drift-block").innerHTML = newDrift;
            });
    }, 60000);
});
