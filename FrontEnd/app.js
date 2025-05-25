const apiBase = "http://localhost:8080/api/applications";

// Load jobs on start
window.onload = () => loadApplications();

// Add application
document.getElementById("jobForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const data = {
    companyName: document.getElementById("companyName").value,
    dateApplied: document.getElementById("applicationDate").value,
    daysSinceUpdate: parseInt(document.getElementById("lastUpdated").value || 0),
    roleAppliedFor: document.getElementById("roleApplied").value,
    status: document.getElementById("status").value || "Unknown",
  };

  await fetch(apiBase, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  loadApplications();
  this.reset();
});

// Load applications
async function loadApplications() {
  const res = await fetch(apiBase);
  const jobs = await res.json();

  const tableBody = document.querySelector("#jobTable tbody");
  tableBody.innerHTML = "";

  jobs.forEach((job) => {
    const row = `<tr>
      <td>${job.id}</td>
      <td>${job.companyName}</td>
      <td>${job.roleAppliedFor}</td>
      <td>${job.dateApplied}</td>
      <td>${job.status}</td>
      <td>${job.daysSinceUpdate} day(s) ago</td>
    </tr>`;
    tableBody.innerHTML += row;
  });
}
