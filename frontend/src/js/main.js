import {
  login,
  register,
  fetchMe,
  fetchAccounts,
  fetchTransactions,
  createAccount,
  createTransaction,
  fetchCategories,
  createCategory,
} from "./api.js";

const views = {
  auth: document.getElementById("auth-view"),
  dashboard: document.getElementById("dashboard-view"),
  accounts: document.getElementById("accounts-view"),
  transactions: document.getElementById("transactions-view"),
  categories: document.getElementById("categories-view"),
};

const loginForm = document.getElementById("login-form");
const authError = document.getElementById("auth-error");

const dashboardSummary = document.getElementById("dashboard-summary");

const accountsList = document.getElementById("accounts-list");
const accountForm = document.getElementById("account-form");
const accountFormMessage = document.getElementById("account-form-message");

const transactionsList = document.getElementById("transactions-list");
const transactionForm = document.getElementById("transaction-form");
const transactionFormMessage = document.getElementById("transaction-form-message");
const transactionAccountSelect = document.getElementById("transaction-account");
const transactionCategorySelect = document.getElementById("transaction-category");

const categoriesList = document.getElementById("categories-list");
const categoryForm = document.getElementById("category-form");
const categoryFormMessage = document.getElementById("category-form-message");

const nav = document.getElementById("nav");
const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebar-toggle");
const userBtn = document.getElementById("user-btn");
const userMenu = document.getElementById("user-menu");
const toastContainer = document.getElementById("toast-container");

const authTitle = document.querySelector("#auth-view h2");
const authEmailLabel = document.getElementById("auth-email-label");
const authConfirmLabel = document.getElementById("auth-confirm-label");
const authSubmitBtn = loginForm.querySelector('button[type="submit"]');
const authToggleBtn = document.getElementById("auth-toggle-btn");
const authToggleText = document.getElementById("auth-toggle-text");
const authSwitchLogin = document.getElementById("auth-switch-login");
const authSwitchSignup = document.getElementById("auth-switch-signup");

let authMode = "login";

function showToast(message, type = "error", title) {
  if (!toastContainer) return;
  const kind = type || "error";

  let resolvedTitle = title;
  if (!resolvedTitle) {
    if (kind === "success") resolvedTitle = "Success";
    else if (kind === "warning") resolvedTitle = "Warning";
    else resolvedTitle = "Error";
  }

  let iconClass = "fa-circle-info";
  if (kind === "success") iconClass = "fa-circle-check";
  else if (kind === "warning") iconClass = "fa-triangle-exclamation";
  else if (kind === "error") iconClass = "fa-circle-xmark";

  const toast = document.createElement("div");
  toast.className = `toast toast-${kind}`;
  toast.innerHTML = `
    <div class="toast-strip"></div>
    <div class="toast-content">
      <div class="toast-header">
        <span class="toast-icon"><i class="fa-solid ${iconClass}"></i></span>
        <span class="toast-title">${resolvedTitle}</span>
      </div>
      <div class="toast-message">${message}</div>
    </div>
    <button type="button" class="toast-close" aria-label="Close">&times;</button>
  `;
  toastContainer.appendChild(toast);

  // Trigger show state
  requestAnimationFrame(() => {
    toast.classList.add("show");
  });

  const remove = () => {
    toast.classList.remove("show");
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 200);
  };

  const closeBtn = toast.querySelector(".toast-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", remove);
  }

  setTimeout(remove, 15000);
}

function setAuthMode(mode) {
  authMode = mode;
  if (mode === "login") {
    if (authTitle) authTitle.textContent = "Sign In";
    authEmailLabel.classList.add("hidden");
    authConfirmLabel.classList.add("hidden");
    authSubmitBtn.textContent = "Login";
    authToggleText.textContent = "Don’t have an account?";
    authToggleBtn.textContent = "Sign up";
    authSwitchLogin.classList.add("active");
    authSwitchLogin.setAttribute("aria-selected", "true");
    authSwitchSignup.classList.remove("active");
    authSwitchSignup.setAttribute("aria-selected", "false");
  } else {
    if (authTitle) authTitle.textContent = "Create Account";
    authEmailLabel.classList.remove("hidden");
    authConfirmLabel.classList.remove("hidden");
    authSubmitBtn.textContent = "Sign up";
    authToggleText.textContent = "Already have an account?";
    authToggleBtn.textContent = "Sign in";
    authSwitchSignup.classList.add("active");
    authSwitchSignup.setAttribute("aria-selected", "true");
    authSwitchLogin.classList.remove("active");
    authSwitchLogin.setAttribute("aria-selected", "false");
  }
}

function showView(name) {
  Object.entries(views).forEach(([key, el]) => {
    if (!el) return;
    el.classList.toggle("hidden", key !== name);
  });

  // Extra safety: auth view should never show sidebar or hamburger
  const hasToken = !!localStorage.getItem("access_token");
  if (name === "auth" || !hasToken) {
    sidebar.classList.add("hidden");
    sidebar.classList.remove("sidebar-open");
    sidebarToggle.classList.add("hidden");
    userMenu.classList.add("hidden");
  } else {
    sidebar.classList.remove("hidden");
    sidebarToggle.classList.remove("hidden");
  }
}

function setAuthedUI(authed) {
  if (authed) {
    nav.classList.remove("hidden");
    sidebar.classList.remove("hidden");
    sidebarToggle.classList.remove("hidden");
  } else {
    nav.classList.add("hidden");
    sidebar.classList.add("hidden");
    sidebar.classList.remove("sidebar-open");
    sidebarToggle.classList.add("hidden");
    userMenu.classList.add("hidden");
  }
}

function setActiveSidebar(viewName) {
  const buttons = nav.querySelectorAll("button[data-view]");
  buttons.forEach((btn) => {
    const isActive = viewName && btn.dataset.view === viewName;
    btn.classList.toggle("active", isActive);
  });
}

async function loadDashboard() {
  try {
    const [accounts, txs] = await Promise.all([
      fetchAccounts(),
      fetchTransactions({ limit: 5 }),
    ]);

    const totalBalance = accounts.reduce(
      (sum, acc) => sum + Number(acc.balance || 0),
      0
    );

    dashboardSummary.textContent = `Accounts: ${accounts.length} • Total balance: ${totalBalance.toFixed(
      2
    )} • Recent transactions: ${txs.length}`;
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

async function populateTransactionAccounts() {
  if (!transactionAccountSelect) return;
  try {
    const accounts = await fetchAccounts();
    transactionAccountSelect.innerHTML = "";

    if (!accounts.length) {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "No accounts available";
      opt.disabled = true;
      opt.selected = true;
      transactionAccountSelect.appendChild(opt);
      return;
    }

    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Select an account";
    placeholder.disabled = true;
    placeholder.selected = true;
    transactionAccountSelect.appendChild(placeholder);

    for (const acc of accounts) {
      const opt = document.createElement("option");
      opt.value = acc.id;
      opt.textContent = `${acc.name} (${acc.account_type})`;
      transactionAccountSelect.appendChild(opt);
    }
  } catch (err) {
    showToast(err.message || "Failed to load accounts.", "error");
  }
}

async function loadTransactions() {
  transactionsList.innerHTML = "";
  try {
    const txs = await fetchTransactions({ limit: 10 });
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

async function loadCategories() {
  categoriesList.innerHTML = "";
  try {
    const cats = await fetchCategories();
    if (!cats.length) {
      categoriesList.innerHTML = "<li>No categories yet.</li>";
      return;
    }
    for (const c of cats) {
      const li = document.createElement("li");
      li.textContent = `${c.name} (${c.category_type})${
        c.is_system ? " [system]" : ""
      }`;
      categoriesList.appendChild(li);
    }
  } catch (err) {
    categoriesList.innerHTML = `<li class="error">Failed to load categories: ${err.message}</li>`;
  }
}

async function populateTransactionCategories() {
  if (!transactionCategorySelect) return;
  try {
    const cats = await fetchCategories();
    transactionCategorySelect.innerHTML = "";

    const uncategorized = document.createElement("option");
    uncategorized.value = "";
    uncategorized.textContent = "Uncategorized";
    transactionCategorySelect.appendChild(uncategorized);

    if (!cats.length) {
      return;
    }

    for (const c of cats) {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = `${c.name} (${c.category_type})`;
      transactionCategorySelect.appendChild(opt);
    }
  } catch (err) {
    showToast(err.message || "Failed to load categories.", "error");
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
    setActiveSidebar("dashboard");
    showView("dashboard");
    await loadDashboard();
  } catch {
    localStorage.removeItem("access_token");
    setAuthedUI(false);
    setActiveSidebar(null);
    showView("auth");
  }
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  authError.textContent = "";

  const formData = new FormData(loginForm);
  const username = formData.get("username");
  const email = formData.get("email");
  const password = formData.get("password");
  const confirmPassword = formData.get("password_confirm");

  try {
    let data;
    if (authMode === "signup") {
      if (!email) {
        showToast("Email is required to sign up.", "error");
        return;
      }

      const emailStr = String(email);
      const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailStr);
      if (!emailValid) {
        showToast("Please enter a valid email address.", "error");
        return;
      }

      const pwd = String(password || "");
      const pwdConfirm = String(confirmPassword || "");
      const pwdPattern = /^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;
      if (!pwdPattern.test(pwd)) {
        showToast(
          "Password must be at least 8 characters and include 1 uppercase letter, 1 number, and 1 symbol.",
          "error"
        );
        return;
      }
      if (pwd !== pwdConfirm) {
        showToast("Passwords do not match.", "error");
        return;
      }

      await register({ username, email, password });
      data = await login(username, password);
    } else {
      data = await login(username, password);
    }
    localStorage.setItem("access_token", data.access_token);
    loginForm.reset();
    setAuthedUI(true);
    setActiveSidebar("dashboard");
    showView("dashboard");
    await loadDashboard();
  } catch (err) {
    showToast(err.message || "Authentication failed.", "error");
  }
});

authToggleBtn.addEventListener("click", () => {
  setAuthMode(authMode === "login" ? "signup" : "login");
});

authSwitchLogin.addEventListener("click", () => {
  setAuthMode("login");
});

authSwitchSignup.addEventListener("click", () => {
  setAuthMode("signup");
});

nav.addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-view]");
  if (!btn) return;
  const view = btn.dataset.view;
  setActiveSidebar(view);
  showView(view);
  sidebar.classList.remove("sidebar-open");

  if (view === "dashboard") {
    await loadDashboard();
  } else if (view === "accounts") {
    await loadAccounts();
  } else if (view === "transactions") {
    await populateTransactionAccounts();
    await populateTransactionCategories();
    await loadTransactions();
  } else if (view === "categories") {
    await loadCategories();
  }
});

function handleLogout() {
  localStorage.removeItem("access_token");
  setAuthedUI(false);
  setActiveSidebar(null);
  showView("auth");
}

sidebarToggle.addEventListener("click", () => {
  sidebar.classList.toggle("sidebar-open");
});

userBtn.addEventListener("click", () => {
  userMenu.classList.toggle("hidden");
});

userMenu.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;
  const action = btn.dataset.action;
  if (action === "logout") {
    handleLogout();
  } else if (action === "profile") {
    // Placeholder for future profile view
    alert("Profile editing coming soon.");
  }
  userMenu.classList.add("hidden");
});

accountForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  accountFormMessage.textContent = "";
  const formData = new FormData(accountForm);

  const payload = {
    name: formData.get("name"),
    account_type: formData.get("account_type"),
    balance: Number(formData.get("balance") || 0),
    currency: formData.get("currency") || "USD",
    is_active: true,
  };

  const bankPayload = {
    bank_name: formData.get("bank_name") || null,
    account_number: formData.get("account_number") || null,
    routing_number: formData.get("routing_number") || null,
  };

  if (bankPayload.bank_name || bankPayload.account_number || bankPayload.routing_number) {
    payload.bank_account = bankPayload;
  }

  try {
    await createAccount(payload);
    accountForm.reset();
    accountFormMessage.textContent = "Account created.";
    await loadAccounts();
    await populateTransactionAccounts();
  } catch (err) {
    showToast(err.message || "Failed to create account.", "error");
  }
});

transactionForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  transactionFormMessage.textContent = "";

  const formData = new FormData(transactionForm);

  const payload = {
    account_id: formData.get("account_id"),
    amount: Number(formData.get("amount")),
    transaction_date: formData.get("transaction_date"),
    transaction_type: formData.get("transaction_type"),
    description: formData.get("description") || null,
    category_id: formData.get("category_id") || null,
  };

  if (!payload.account_id || Number.isNaN(payload.amount)) {
    showToast("Account ID and amount are required.", "error");
    return;
  }

  try {
    await createTransaction(payload);
    transactionForm.reset();
    transactionFormMessage.textContent = "Transaction created.";
    await loadTransactions();
  } catch (err) {
    showToast(err.message || "Failed to create transaction.", "error");
  }
});

categoryForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  categoryFormMessage.textContent = "";
  const formData = new FormData(categoryForm);

  const payload = {
    name: formData.get("name"),
    category_type: formData.get("category_type"),
  };

  try {
    await createCategory(payload);
    categoryForm.reset();
    categoryFormMessage.textContent = "Category created.";
    await loadCategories();
    await populateTransactionCategories();
  } catch (err) {
    showToast(err.message || "Failed to create category.", "error");
  }
});

document.addEventListener("DOMContentLoaded", bootstrap);

// Initialize auth mode
setAuthMode("login");

