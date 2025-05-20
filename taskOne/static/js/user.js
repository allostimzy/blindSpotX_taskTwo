// user.js
document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  if (!token || role !== "user") {
    // Not logged in or not user -> redirect to login
    window.location.href = "index.html";
  }

  document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "/";
  });
});
