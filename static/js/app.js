// -----------------------------------------------------------------------------
// SMART STUDY RESOURCE FINDER - FRONTEND JAVASCRIPT
// Handles AJAX API requests, DOM rendering, Modals, and Filtering
// -----------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    // DOM Element References
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const subjectFilter = document.getElementById('subjectFilter');
    const difficultyFilter = document.getElementById('difficultyFilter');
    const resourceTypeFilter = document.getElementById('resourceTypeFilter');
    const resetFiltersBtn = document.getElementById('resetFiltersBtn');
    const resultsCount = document.getElementById('resultsCount');
    const searchBadge = document.getElementById('searchBadge');
    const resourcesGrid = document.getElementById('resourcesGrid');

    // Modal References
    const resourceModal = document.getElementById('resourceModal');
    const openAddModalBtn = document.getElementById('openAddModalBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    const resourceForm = document.getElementById('resourceForm');
    const modalTitle = document.getElementById('modalTitle');
    const saveResourceBtn = document.getElementById('saveResourceBtn');

    const detailModal = document.getElementById('detailModal');
    const closeDetailModalBtn = document.getElementById('closeDetailModalBtn');
    const closeDetailModalBtn2 = document.getElementById('closeDetailModalBtn2');

    // State Variables
    let currentResources = [];

    // -------------------------------------------------------------------------
    // INITIALIZATION
    // -------------------------------------------------------------------------
    loadSubjects();
    loadResources();

    // -------------------------------------------------------------------------
    // EVENT LISTENERS
    // -------------------------------------------------------------------------
    searchBtn.addEventListener('click', loadResources);

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            loadResources();
        }
    });

    // Instant filter changes
    subjectFilter.addEventListener('change', loadResources);
    difficultyFilter.addEventListener('change', loadResources);
    resourceTypeFilter.addEventListener('change', loadResources);

    // Search mode radio toggle
    document.querySelectorAll('input[name="searchMode"]').forEach(radio => {
        radio.addEventListener('change', loadResources);
    });

    // Reset filters button
    resetFiltersBtn.addEventListener('click', () => {
        searchInput.value = '';
        subjectFilter.value = '';
        difficultyFilter.value = '';
        resourceTypeFilter.value = '';
        document.getElementById('modeSemantic').checked = true;
        loadResources();
    });

    // Modal Triggers
    openAddModalBtn.addEventListener('click', () => openFormModal());
    closeModalBtn.addEventListener('click', closeFormModal);
    cancelModalBtn.addEventListener('click', closeFormModal);

    closeDetailModalBtn.addEventListener('click', closeDetailModal);
    closeDetailModalBtn2.addEventListener('click', closeDetailModal);

    // Close modal on background overlay click
    window.addEventListener('click', (e) => {
        if (e.target === resourceModal) closeFormModal();
        if (e.target === detailModal) closeDetailModal();
    });

    // Form Submission
    resourceForm.addEventListener('submit', handleFormSubmit);

    // -------------------------------------------------------------------------
    // API FUNCTIONS
    // -------------------------------------------------------------------------

    /**
     * Fetches distinct subjects from API to populate filter dropdown & datalist.
     */
    async function loadSubjects() {
        try {
            const res = await fetch('/api/subjects');
            const result = await res.json();
            if (result.success) {
                const subjects = result.data || [];
                const select = subjectFilter;
                const datalist = document.getElementById('subjectDatalist');

                // Preserve existing 'All Subjects' option
                select.innerHTML = '<option value="">All Subjects</option>';
                datalist.innerHTML = '';

                subjects.forEach(sub => {
                    const opt = document.createElement('option');
                    opt.value = sub;
                    opt.textContent = sub;
                    select.appendChild(opt);

                    const dataOpt = document.createElement('option');
                    dataOpt.value = sub;
                    datalist.appendChild(dataOpt);
                });
            }
        } catch (err) {
            console.error('Error loading subjects:', err);
        }
    }

    /**
     * Main function to fetch study resources based on search and filters.
     */
    async function loadResources() {
        const query = searchInput.value.trim();
        const mode = document.querySelector('input[name="searchMode"]:checked').value;
        const subject = subjectFilter.value;
        const difficulty = difficultyFilter.value;
        const resourceType = resourceTypeFilter.value;

        // Update UI status badge
        searchBadge.textContent = mode === 'semantic' ? 'Mode: Semantic AI Search' : 'Mode: Keyword Text Search';
        searchBadge.className = mode === 'semantic' ? 'badge badge-mode' : 'badge badge-subject';

        // Display loading indicator
        resourcesGrid.innerHTML = `
            <div class="loading-state">
                <i class="fa-solid fa-circle-notch fa-spin"></i>
                <p>Fetching resources from MongoDB Cloud...</p>
            </div>
        `;

        try {
            const urlParams = new URLSearchParams();
            if (query) urlParams.append('search', query);
            urlParams.append('mode', mode);
            if (subject) urlParams.append('subject', subject);
            if (difficulty) urlParams.append('difficulty', difficulty);
            if (resourceType) urlParams.append('resource_type', resourceType);

            const response = await fetch(`/api/resources?${urlParams.toString()}`);
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to fetch resources');
            }

            currentResources = result.data || [];
            resultsCount.textContent = `Found ${currentResources.length} study resource${currentResources.length === 1 ? '' : 's'}`;

            renderResourceCards(currentResources);
        } catch (err) {
            console.error('Error fetching resources:', err);
            resourcesGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-triangle-exclamation" style="color: var(--danger)"></i>
                    <h3>Error Loading Resources</h3>
                    <p>${err.message}</p>
                    <button class="btn btn-secondary" onclick="location.reload()" style="margin-top: 1rem">
                        <i class="fa-solid fa-rotate"></i> Retry
                    </button>
                </div>
            `;
        }
    }

    // -------------------------------------------------------------------------
    // RENDER FUNCTIONS
    // -------------------------------------------------------------------------

    /**
     * Renders array of resource objects into HTML card elements.
     */
    function renderResourceCards(resources) {
        if (!resources || resources.length === 0) {
            resourcesGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-folder-open"></i>
                    <h3>No Resources Found</h3>
                    <p>Try adjusting your search query or removing filters to see results.</p>
                </div>
            `;
            return;
        }

        resourcesGrid.innerHTML = '';

        resources.forEach(item => {
            const card = document.createElement('article');
            card.className = 'resource-card';

            const scoreBadgeHTML = item.score ? `
                <span class="score-badge" title="Vector Similarity Score">
                    <i class="fa-solid fa-bolt"></i> ${(item.score * 100).toFixed(1)}% Match
                </span>
            ` : '';

            const tagsHTML = (item.tags || []).map(tag => `<span class="tag-pill">#${escapeHTML(tag)}</span>`).join('');

            card.innerHTML = `
                <div class="card-top">
                    <div class="card-badges">
                        <span class="badge badge-subject">${escapeHTML(item.subject)}</span>
                        <span class="badge badge-difficulty">${escapeHTML(item.difficulty)}</span>
                        <span class="badge badge-type">${escapeHTML(item.resource_type)}</span>
                        ${scoreBadgeHTML}
                    </div>
                    <h3 class="card-title">${escapeHTML(item.title)}</h3>
                    <p class="card-description">${escapeHTML(item.description)}</p>
                    <div class="card-tags">${tagsHTML}</div>
                </div>
                <div class="card-actions">
                    <button class="btn btn-secondary btn-sm view-btn" data-id="${item.id}">
                        <i class="fa-solid fa-eye"></i> View Details
                    </button>
                    <div class="card-actions-right">
                        <button class="btn btn-icon-only btn-edit edit-btn" data-id="${item.id}" title="Edit Resource">
                            <i class="fa-solid fa-pen"></i>
                        </button>
                        <button class="btn btn-icon-only btn-danger delete-btn" data-id="${item.id}" title="Delete Resource">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;

            // Card Button Event Listeners
            card.querySelector('.view-btn').addEventListener('click', () => openDetailModal(item.id));
            card.querySelector('.edit-btn').addEventListener('click', () => openFormModal(item));
            card.querySelector('.delete-btn').addEventListener('click', () => deleteResource(item.id, item.title));

            resourcesGrid.appendChild(card);
        });
    }

    // -------------------------------------------------------------------------
    // MODAL LOGIC (ADD / EDIT / VIEW)
    // -------------------------------------------------------------------------

    function openFormModal(item = null) {
        resourceForm.reset();
        document.getElementById('resourceId').value = '';

        if (item) {
            modalTitle.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Edit Study Resource';
            document.getElementById('resourceId').value = item.id;
            document.getElementById('title').value = item.title || '';
            document.getElementById('subject').value = item.subject || '';
            document.getElementById('topic').value = item.topic || '';
            document.getElementById('difficulty').value = item.difficulty || 'Beginner';
            document.getElementById('resourceType').value = item.resource_type || 'Article';
            document.getElementById('description').value = item.description || '';
            document.getElementById('content').value = item.content || '';
            document.getElementById('tags').value = (item.tags || []).join(', ');
            document.getElementById('url').value = item.url || '';
        } else {
            modalTitle.innerHTML = '<i class="fa-solid fa-folder-plus"></i> Add New Study Resource';
        }

        resourceModal.classList.add('active');
    }

    function closeFormModal() {
        resourceModal.classList.remove('active');
    }

    async function openDetailModal(resourceId) {
        try {
            const res = await fetch(`/api/resources/${resourceId}`);
            const result = await res.json();
            if (!result.success) throw new Error(result.error);

            const item = result.data;
            document.getElementById('detailTitle').textContent = item.title;
            document.getElementById('detailSubject').textContent = item.subject;
            document.getElementById('detailDifficulty').textContent = item.difficulty;
            document.getElementById('detailType').textContent = item.resource_type;
            document.getElementById('detailTopic').innerHTML = `<i class="fa-solid fa-bookmark"></i> ${escapeHTML(item.topic)}`;
            document.getElementById('detailDescription').textContent = item.description;

            const contentElem = document.getElementById('detailContent');
            if (item.content) {
                contentElem.textContent = item.content;
                document.getElementById('detailContentSection').style.display = 'block';
            } else {
                document.getElementById('detailContentSection').style.display = 'none';
            }

            const tagsContainer = document.getElementById('detailTags');
            tagsContainer.innerHTML = (item.tags || []).map(t => `<span class="tag-pill">#${escapeHTML(t)}</span>`).join(' ');

            const urlBtn = document.getElementById('detailUrlBtn');
            if (item.url) {
                urlBtn.href = item.url;
                urlBtn.style.display = 'inline-flex';
            } else {
                urlBtn.style.display = 'none';
            }

            detailModal.classList.add('active');
        } catch (err) {
            alert('Failed to load resource details: ' + err.message);
        }
    }

    function closeDetailModal() {
        detailModal.classList.remove('active');
    }

    // -------------------------------------------------------------------------
    // FORM SUBMISSION & DELETE
    // -------------------------------------------------------------------------

    async function handleFormSubmit(e) {
        e.preventDefault();
        saveResourceBtn.disabled = true;
        saveResourceBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Saving & Embedding...';

        const id = document.getElementById('resourceId').value;
        const payload = {
            title: document.getElementById('title').value,
            subject: document.getElementById('subject').value,
            topic: document.getElementById('topic').value,
            difficulty: document.getElementById('difficulty').value,
            resource_type: document.getElementById('resourceType').value,
            description: document.getElementById('description').value,
            content: document.getElementById('content').value,
            tags: document.getElementById('tags').value,
            url: document.getElementById('url').value
        };

        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/resources/${id}` : '/api/resources';

        try {
            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await res.json();
            if (!result.success) throw new Error(result.error);

            closeFormModal();
            await loadSubjects();
            await loadResources();
        } catch (err) {
            alert('Error saving resource: ' + err.message);
        } finally {
            saveResourceBtn.disabled = false;
            saveResourceBtn.innerHTML = '<i class="fa-solid fa-save"></i> Save Resource';
        }
    }

    async function deleteResource(id, title) {
        if (!confirm(`Are you sure you want to delete "${title}"?`)) return;

        try {
            const res = await fetch(`/api/resources/${id}`, { method: 'DELETE' });
            const result = await res.json();

            if (!result.success) throw new Error(result.error);

            await loadSubjects();
            await loadResources();
        } catch (err) {
            alert('Failed to delete resource: ' + err.message);
        }
    }

    // Helper Utility
    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    }
});
