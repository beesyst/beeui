(() => {
  const root = document.documentElement;
  if (root) {
    root.setAttribute("data-beeui", "ready");
  }

  const sidebar = document.getElementById("beeui-sidebar-menu");
  if (sidebar) {
    const syncSidebarState = () => {
      const isOpen = sidebar.classList.contains("show");
      root?.setAttribute("data-beeui-sidebar", isOpen ? "open" : "closed");
    };

    syncSidebarState();
    sidebar.addEventListener("transitionend", syncSidebarState);
    sidebar.addEventListener("click", syncSidebarState);
  }
})();
