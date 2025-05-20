const backendUrl = "http://127.0.0.1:5500"; // Use 5500 if that’s your Flask server port

// Admin login form
const adminForm = document.getElementById("admin-login-form");
const adminMsg = document.getElementById("admin-login-msg");

adminForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  adminMsg.textContent = "";

  const email = document.getElementById("admin-email").value.trim();
  const password = document.getElementById("admin-password").value.trim();

  try {
    const res = await fetch(`${backendUrl}/admin-login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    if (res.ok) {
      localStorage.setItem("token", data.token);
      localStorage.setItem("role", "admin");
      window.location.href = "/admin";
    } else {
      adminMsg.textContent = data.error || "Login failed";
    }
  } catch (error) {
    adminMsg.textContent = "Error connecting to server";
  }
});

// Google OAuth callback (for One Tap or Sign-In button)
function handleCredentialResponse(response) {
  fetch(`${backendUrl}/google-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: response.credential }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.token) {
        localStorage.setItem("token", data.token);
        localStorage.setItem("role", data.role);
        window.location.href = data.role === "admin" ? "/admin" : "/user";
      } else {
        document.getElementById("google-login-msg").textContent = data.error || "Login failed";
      }
    })
    .catch(() => {
      document.getElementById("google-login-msg").textContent = "Error connecting to server";
    });
}

// Expose Google callback globally
window.handleCredentialResponse = handleCredentialResponse;
