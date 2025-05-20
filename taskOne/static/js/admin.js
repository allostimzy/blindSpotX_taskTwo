document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  if (!token || role !== "admin") {
    // Not logged in or not admin -> redirect to login
    window.location.href = "index.html";
    return;
  }

  const usersTable = document.getElementById("users-table");
  const usersTableBody = document.getElementById("users-table-body");

  // Fetch users from API
  fetch("/api/users", {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to fetch users");
      }
      return response.json();
    })
    .then((users) => {
      if (users.length === 0) {
        usersTableBody.innerHTML = `<tr><td colspan="2">No users found.</td></tr>`;
        return;
      }
      // Populate table rows
      usersTableBody.innerHTML = users.map(user => `
        <tr>
          <td>${user.email}</td>
          <td>${user.role}</td>
        </tr>
      `).join("");
    })
    .catch((err) => {
      console.error(err);
      usersTableBody.innerHTML = `<tr><td colspan="2">Error loading users.</td></tr>`;
    });

  document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "/";
  });
});
