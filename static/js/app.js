document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector("[data-sidebar]");
  const toggle = document.querySelector("[data-sidebar-toggle]");
  const closeButton = document.querySelector("[data-sidebar-close]");
  const backdrop = document.querySelector("[data-sidebar-backdrop]");
  const desktopQuery = window.matchMedia("(min-width: 1024px)");

  const setSidebar = (isOpen) => {
    if (!sidebar || !toggle || !backdrop) return;

    const mobileOpen = isOpen && !desktopQuery.matches;
    sidebar.classList.toggle("is-open", mobileOpen);
    toggle.setAttribute("aria-expanded", String(mobileOpen));
    toggle.setAttribute("aria-label", mobileOpen ? "Close navigation" : "Open navigation");
    backdrop.hidden = !mobileOpen;
    document.body.classList.toggle("sidebar-open", mobileOpen);

    if (desktopQuery.matches) {
      sidebar.removeAttribute("inert");
    } else if (mobileOpen) {
      sidebar.removeAttribute("inert");
    } else {
      sidebar.setAttribute("inert", "");
    }
  };

  if (sidebar && toggle && backdrop) {
    setSidebar(false);
    toggle.addEventListener("click", () => setSidebar(!sidebar.classList.contains("is-open")));
    closeButton?.addEventListener("click", () => setSidebar(false));
    backdrop.addEventListener("click", () => setSidebar(false));
    sidebar.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setSidebar(false)));
    desktopQuery.addEventListener("change", () => setSidebar(false));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && sidebar.classList.contains("is-open")) {
        setSidebar(false);
        toggle.focus();
      }
    });
  }

  document.querySelectorAll("[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
});
