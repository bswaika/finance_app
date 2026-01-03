import { login, fetchMe, fetchAccounts, fetchRecentTransactions } from "./api.js";

const views = {
  auth: document.getElementById("auth-view"),
  dashboard: document.getElementById("dashboard-view"),
  accounts: document.getElementById("accounts-view"),
  transactions: document.getElementById("transactions-view"),
};

const loginForm = document.getElementById("login-form");
const authError = document.getElementById("auth-error");
const accountsList = document.getElementById("accounts-list");
const transactionsList = document.getElementById("transactions-list");
const dashboardSummary = document.getElementById("dashboard-summary");
const nav = document.getElementById("nav");
const logoutBtn = document.getElementById("logout-btn");

function showView(name) {
  Object.entries(views).forEach(([key, el]) => {
    if (!el) return;
    el.classList.toggle("hidden", key !== name);
  });
}

function setAuthedUI(authed) {
  if (authed) {
    nav.classList.remove("hidden");
    logoutBtn.classList.remove("hidden");
  } else {
    nav.classList.add("hidden");
    logoutBtn.classList.add("hidden");
  }
}

async function loadDashboard() {
  try {
    const [accounts, transactions] = await Promise.all([
      fetchAccounts(),
      fetchRecentTransactions({ limit: 5 }),
    ]);

    const totalBalance = accounts.reduce(
      (sum, acc) => sum + Number(acc.balance || 0),
      0
    );

    dashboardSummary.textContent = `Accounts: ${accounts.length} • Total balance: ${totalBalance.toFixed(
      2
    )}`;
  } catch (err) {
    dashboardSummary.textContent = `Failed to load dashboard: ${err.message}`;
  }
}

async function loadAccounts() {
  accountsList.innerHTML = "";
  try {
    const accounts = await fetchAccounts();
    if (!accounts.length) {
      accountsList.innerHTML = "<li>No accounts yet.</li>";
      return;
    }
    for (const acc of accounts) {
      const li = document.createElement("li");
      li.textContent = `${acc.name} (${acc.account_type}) — ${Number(
        acc.balance || 0
      ).toFixed(2)} ${acc.currency || ""}`;
      accountsList.appendChild(li);
    }
  } catch (err) {
    accountsList.innerHTML = `<li class="error">Failed to load accounts: ${err.message}</li>`;
  }
}

async function loadTransactions() {
  transactionsList.innerHTML = "";
  try {
    const txs = await fetchRecentTransactions({ limit: 10 });
    if (!txs.length) {
      transactionsList.innerHTML = "<li>No transactions yet.</li>";
      return;
    }
    for (const tx of txs) {
      const li = document.createElement("li");
      li.textContent = `${tx.transaction_date} • ${tx.description || ""} • ${
        tx.amount
      }`;
      transactionsList.appendChild(li);
    }
  } catch (err) {
    transactionsList.innerHTML = `<li class="error">Failed to load transactions: ${err.message}</li>`;
  }
}

async function bootstrap() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    setAuthedUI(false);
    showView("auth");
    return;
  }

  try {
    await fetchMe();
    setAuthedUI(true);
    showView("dashboard");
    await loadDashboard();
  } catch {
    localStorage.removeItem("access_token");
    setAuthedUI(false);
    showView("auth");
  }
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  authError.textContent = "";

  const formData = new FormData(loginForm);
  const username = formData.get("username");
  const password = formData.get("password");

  try {
    const data = await login(username, password);
    localStorage.setItem("access_token", data.access_token);
    setAuthedUI(true);
    showView("dashboard");
    await loadDashboard();
  } catch (err) {
    authError.textContent = err.message;
  }
});

nav.addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-view]");
  if (!btn) return;
  const view = btn.dataset.view;
  showView(view);

  if (view === "dashboard") {
    await loadDashboard();
  } else if (view === "accounts") {
    await loadAccounts();
  } else if (view === "transactions") {
    await loadTransactions();
  }
});

logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("access_token");
  setAuthedUI(false);
  showView("auth");
});

document.addEventListener("DOMContentLoaded", bootstrap);


