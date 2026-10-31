/**
 * StudyFlow — Smart Study Planner V1
 * Frontend Interactive Controller & Simplified Theme Manager (Black, White, Purple)
 */

(function () {
    "use strict";

    // -------------------------------------------------------------------------
    // 1. Appearance / Theme Customization System (Clean: Dark, Light, Purple)
    // -------------------------------------------------------------------------
    const THEME_STORAGE_KEY = "studyflow_appearance_v1";

    const DEFAULT_SETTINGS = {
        theme: "dark"
    };

    function loadSettings() {
        try {
            const saved = localStorage.getItem(THEME_STORAGE_KEY);
            return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : { ...DEFAULT_SETTINGS };
        } catch (e) {
            console.warn("Could not read appearance settings from localStorage:", e);
            return { ...DEFAULT_SETTINGS };
        }
    }

    function saveSettings(settings) {
        try {
            localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(settings));
        } catch (e) {
            console.warn("Could not save appearance settings to localStorage:", e);
        }
    }

    function applySettings(settings) {
        const root = document.documentElement;
        const validThemes = ["dark", "light", "purple"];
        const chosenTheme = validThemes.includes(settings.theme) ? settings.theme : "dark";
        root.setAttribute("data-theme", chosenTheme);
    }

    function syncModalUI(settings) {
        document.querySelectorAll(".theme-card-option").forEach(btn => {
            btn.classList.toggle("active", btn.dataset.themeValue === settings.theme);
        });
    }

    // -------------------------------------------------------------------------
    // 2. Dynamic Subject Rows for Study Planner
    // -------------------------------------------------------------------------
    function initStudyPlannerRows() {
        const subjectsContainer = document.getElementById("subjects-container");
        const addSubjectButton = document.getElementById("add-subject");
        const subjectCountPill = document.getElementById("subject-count");
        const maxSubjects = 6;

        if (!subjectsContainer || !addSubjectButton) return;

        function updateRows() {
            const rows = subjectsContainer.querySelectorAll(".subject-row");

            rows.forEach((row, index) => {
                const label = row.querySelector(".subject-row-label");
                if (label) label.textContent = `Subject ${index + 1}`;

                const removeBtn = row.querySelector(".btn-remove-subject");
                if (removeBtn) {
                    removeBtn.disabled = rows.length === 1;
                    removeBtn.title = rows.length === 1 ? "At least one subject required" : "Remove this subject";
                }
            });

            if (subjectCountPill) {
                subjectCountPill.textContent = `${rows.length} / ${maxSubjects}`;
            }

            addSubjectButton.disabled = rows.length >= maxSubjects;
            addSubjectButton.textContent = rows.length >= maxSubjects
                ? "Maximum 6 Subjects Reached"
                : "+ Add Another Subject";
        }

        addSubjectButton.addEventListener("click", () => {
            const currentRows = subjectsContainer.querySelectorAll(".subject-row").length;
            if (currentRows >= maxSubjects) return;

            const nextIndex = currentRows + 1;
            const row = document.createElement("div");
            row.className = "subject-row";
            row.innerHTML = `
                <div class="subject-row-label">Subject ${nextIndex}</div>
                <div>
                    <input type="text"
                           name="subject_name"
                           maxlength="80"
                           placeholder="e.g. Data Structures"
                           required>
                </div>
                <div>
                    <select name="difficulty" required>
                        <option value="weak">Weak (High Focus)</option>
                        <option value="medium" selected>Medium (Standard)</option>
                        <option value="strong">Strong (Revision)</option>
                    </select>
                </div>
                <button type="button"
                        class="btn-remove-subject"
                        aria-label="Remove subject">
                    ✕
                </button>
            `;

            subjectsContainer.appendChild(row);
            updateRows();
            const input = row.querySelector("input[name='subject_name']");
            if (input) input.focus();
        });

        subjectsContainer.addEventListener("click", (event) => {
            const removeBtn = event.target.closest(".btn-remove-subject");
            if (!removeBtn) return;

            const rows = subjectsContainer.querySelectorAll(".subject-row");
            if (rows.length > 1) {
                removeBtn.closest(".subject-row").remove();
                updateRows();
            }
        });

        updateRows();
    }

    // -------------------------------------------------------------------------
    // 3. Task Management Filters & Instant Search
    // -------------------------------------------------------------------------
    function initTaskFilters() {
        const filterTabs = document.querySelectorAll(".filter-tab");
        const taskCards = document.querySelectorAll(".task-card");
        const searchInput = document.getElementById("task-search-input");
        const emptyFilteredState = document.getElementById("empty-filtered-tasks");

        if (!taskCards.length) return;

        let activeFilter = "all";
        let searchQuery = "";

        function applyFilter() {
            let visibleCount = 0;

            taskCards.forEach(card => {
                const category = card.dataset.category || "";
                const priority = card.dataset.priority || "";
                const title = (card.dataset.title || "").toLowerCase();
                const subject = (card.dataset.subject || "").toLowerCase();

                let matchesTab = false;
                if (activeFilter === "all") {
                    matchesTab = true;
                } else if (activeFilter === "pending") {
                    matchesTab = category !== "completed";
                } else if (activeFilter === "completed") {
                    matchesTab = category === "completed";
                } else if (activeFilter === "overdue") {
                    matchesTab = category === "overdue";
                } else if (activeFilter === "high") {
                    matchesTab = priority.toLowerCase() === "high";
                }

                const matchesSearch = !searchQuery || title.includes(searchQuery) || subject.includes(searchQuery);

                if (matchesTab && matchesSearch) {
                    card.style.display = "";
                    visibleCount++;
                } else {
                    card.style.display = "none";
                }
            });

            if (emptyFilteredState) {
                emptyFilteredState.style.display = visibleCount === 0 ? "block" : "none";
            }
        }

        filterTabs.forEach(tab => {
            tab.addEventListener("click", () => {
                filterTabs.forEach(t => t.classList.remove("active"));
                tab.classList.add("active");
                activeFilter = tab.dataset.filter || "all";
                applyFilter();
            });
        });

        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                searchQuery = e.target.value.trim().toLowerCase();
                applyFilter();
            });
        }
    }

    // -------------------------------------------------------------------------
    // 4. Modal Confirmations (Delete Task) & Settings Modal
    // -------------------------------------------------------------------------
    function initModals(settings) {
        const settingsModal = document.getElementById("appearance-modal");
        const openSettingsBtns = document.querySelectorAll(".btn-open-settings");
        const closeSettingsBtns = document.querySelectorAll(".btn-close-settings");

        const openSettings = () => {
            if (!settingsModal) return;
            syncModalUI(settings);
            settingsModal.classList.add("active");
            document.body.style.overflow = "hidden";
        };

        const closeSettings = () => {
            if (!settingsModal) return;
            settingsModal.classList.remove("active");
            document.body.style.overflow = "";
        };

        openSettingsBtns.forEach(btn => btn.addEventListener("click", (e) => {
            e.preventDefault();
            openSettings();
        }));

        closeSettingsBtns.forEach(btn => btn.addEventListener("click", closeSettings));

        if (settingsModal) {
            settingsModal.addEventListener("click", (e) => {
                if (e.target === settingsModal) closeSettings();
            });
        }

        // Theme selection click (Dark/Black, Light/White, Purple)
        document.querySelectorAll(".theme-card-option").forEach(card => {
            card.addEventListener("click", () => {
                settings.theme = card.dataset.themeValue;
                applySettings(settings);
                saveSettings(settings);
                syncModalUI(settings);
            });
        });

        // Reset Settings Button (Defaults to Black/Dark)
        const resetBtn = document.getElementById("btn-reset-appearance");
        if (resetBtn) {
            resetBtn.addEventListener("click", () => {
                settings = { ...DEFAULT_SETTINGS };
                applySettings(settings);
                saveSettings(settings);
                syncModalUI(settings);
            });
        }

        // Delete Task Confirmation Modal
        const deleteModal = document.getElementById("delete-task-modal");
        const deleteModalTaskTitle = document.getElementById("delete-modal-task-title");
        const confirmDeleteBtn = document.getElementById("confirm-delete-btn");
        const cancelDeleteBtn = document.getElementById("cancel-delete-btn");
        let activeDeleteForm = null;

        document.querySelectorAll(".delete-task-form").forEach(form => {
            form.addEventListener("submit", (e) => {
                e.preventDefault();
                activeDeleteForm = form;
                const taskTitle = form.dataset.taskTitle || "this task";
                if (deleteModalTaskTitle) {
                    deleteModalTaskTitle.textContent = `"${taskTitle}"`;
                }
                if (deleteModal) {
                    deleteModal.classList.add("active");
                    document.body.style.overflow = "hidden";
                }
            });
        });

        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener("click", () => {
                if (activeDeleteForm) {
                    activeDeleteForm.submit();
                }
            });
        }

        const closeDeleteModal = () => {
            if (deleteModal) {
                deleteModal.classList.remove("active");
                document.body.style.overflow = "";
            }
            activeDeleteForm = null;
        };

        if (cancelDeleteBtn) cancelDeleteBtn.addEventListener("click", closeDeleteModal);
        if (deleteModal) {
            deleteModal.addEventListener("click", (e) => {
                if (e.target === deleteModal) closeDeleteModal();
            });
        }
    }

    // -------------------------------------------------------------------------
    // 5. Mobile Navigation & Flash Alerts
    // -------------------------------------------------------------------------
    function initMobileNav() {
        const sidebar = document.querySelector(".sidebar");
        const toggleBtn = document.querySelector(".mobile-nav-toggle");
        const backdrop = document.querySelector(".mobile-sidebar-backdrop");

        if (!sidebar || !toggleBtn) return;

        const openNav = () => {
            sidebar.classList.add("open");
            if (backdrop) backdrop.classList.add("active");
            document.body.style.overflow = "hidden";
        };

        const closeNav = () => {
            sidebar.classList.remove("open");
            if (backdrop) backdrop.classList.remove("active");
            document.body.style.overflow = "";
        };

        toggleBtn.addEventListener("click", () => {
            if (sidebar.classList.contains("open")) closeNav();
            else openNav();
        });

        if (backdrop) backdrop.addEventListener("click", closeNav);

        document.querySelectorAll(".sidebar-nav .nav-link").forEach(link => {
            link.addEventListener("click", () => {
                if (window.innerWidth <= 768) closeNav();
            });
        });
    }

    function initFlashAlerts() {
        document.querySelectorAll(".flash-close-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const alert = btn.closest(".flash-alert");
                if (alert) alert.remove();
            });
        });
    }

    // -------------------------------------------------------------------------
    // Initialize on DOMContentLoaded
    // -------------------------------------------------------------------------
    document.addEventListener("DOMContentLoaded", () => {
        let currentSettings = loadSettings();
        applySettings(currentSettings);
        initStudyPlannerRows();
        initTaskFilters();
        initModals(currentSettings);
        initMobileNav();
        initFlashAlerts();
    });

})();
