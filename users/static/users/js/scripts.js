document.addEventListener('DOMContentLoaded', function () {

    // ============================================
    // VARIABLES GLOBALES
    // ============================================
    let isEditMode = false;
    let originalData = {
        sobreMi: '',
        tags: {},
        contacts: {}
    };
    let currentEditingProject = null;
    let currentFilters = {
        search: '',
        theme: 'all',
        tech: 'all',
        sort: 'recent'
    };

    // Sugerencias para intereses (empezamos en 4 para que no repita los que ya están)
    const interesesSugerencias = [
        'IA', 'Big Data', 'Machine Learning', 'Desarrollo Web', 'Deep Learning',
        'Robótica', 'Ciberseguridad', 'Cloud Computing', 'Blockchain', 'IoT',
        'Automatización', 'Data Science', 'Redes Neuronales', 'NLP', 'Computer Vision'
    ];
    let interesesIndex = 4;

    // Sugerencias para tecnologías (empezamos en 4 para que no repita los que ya están)
    const tecnologiasSugerencias = [
        'Python', 'Django', 'JavaScript', 'React', 'Node.js', 'Angular',
        'Vue.js', 'TensorFlow', 'PyTorch', 'Docker', 'Kubernetes', 'AWS',
        'MongoDB', 'PostgreSQL', 'Java', 'C++', 'Go', 'Rust', 'Flutter'
    ];
    let tecnologiasIndex = 4;

    // ============================================
    // ELEMENTOS DEL DOM
    // ============================================
    const cardInfo = document.getElementById('card-descripcion');
    const btnEditCard = document.getElementById('btn-edit-card');
    const editButtons = document.getElementById('edit-buttons');
    const btnCancelCard = document.getElementById('btn-cancel-card');
    const btnSaveCard = document.getElementById('btn-save-card');

    const btnDesc = document.getElementById('btn-desc');
    const btnProy = document.getElementById('btn-proy');
    const viewGeneral = document.getElementById('view-general');
    const viewProjects = document.getElementById('view-all-projects');

    const modal = document.getElementById('modal-edit-profile');
    const btnEditProfile = document.getElementById('btn-edit-profile');
    const btnCancelModal = document.getElementById('btn-cancel-modal');
    const btnCloseModal = document.getElementById('btn-close-modal');

    const displaySobreMi = document.getElementById('display-sobre-mi');
    const editSobreMi = document.getElementById('edit-sobre-mi');
    const textareaSobreMi = document.getElementById('textarea-sobre-mi');
    const counterSobreMi = document.getElementById('counter-sobre-mi');

    const projectsGrid = document.getElementById('projects-grid');
    const searchInput = document.getElementById('search-project');
    const searchClear = document.getElementById('search-clear');
    const noResults = document.getElementById('no-results');
    const searchTerm = document.getElementById('search-term');
    const projectCount = document.getElementById('project-count');

    // ============================================
    // NAVEGACIÓN DE PESTAÑAS
    // ============================================
    btnDesc.addEventListener('click', function () {
        btnDesc.classList.add('active');
        btnProy.classList.remove('active');
        viewGeneral.style.display = 'block';
        viewProjects.style.display = 'none';
    });

    btnProy.addEventListener('click', function () {
        btnProy.classList.add('active');
        btnDesc.classList.remove('active');
        viewGeneral.style.display = 'none';
        viewProjects.style.display = 'block';
        updateProjectCount();
    });

    // ============================================
    // CONTROL DEL MODAL DE PERFIL
    // ============================================
    const profileAvatar = document.getElementById('profile-avatar');
    const profileFullname = document.getElementById('profile-fullname');
    const photoPreviewImg = document.getElementById('photo-preview-img');
    const inputPhoto = document.getElementById('input-photo');
    const inputNombre = document.getElementById('input-nombre');
    const inputApellido = document.getElementById('input-apellido');
    const btnSaveModal = document.getElementById('btn-save-modal');

    let selectedPhotoFile = null;

    // Abrir modal y cargar datos actuales
    btnEditProfile.addEventListener('click', function () {
        const partes = profileFullname.innerHTML.split('<br>');
        inputNombre.value = profileFullname.dataset.nombre || '';
        inputApellido.value = profileFullname.dataset.apellido || '';
        photoPreviewImg.src = profileAvatar.src;
        selectedPhotoFile = null;
        // Cargar username actual sin el @
        document.getElementById('input-username').value =
            document.querySelector('.username').textContent.replace('@', '').trim();
        modal.classList.add('active');
    });

    // Cerrar modal
    const closeModal = function () {
        modal.classList.remove('active');
    };

    btnCancelModal.addEventListener('click', closeModal);
    btnCloseModal.addEventListener('click', closeModal);

    // Manejar selección de imagen
    inputPhoto.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) {
                alert('La imagen no debe superar los 5MB');
                this.value = '';
                return;
            }
            if (!file.type.startsWith('image/')) {
                alert('Por favor selecciona una imagen válida');
                this.value = '';
                return;
            }
            selectedPhotoFile = file;
            const reader = new FileReader();
            reader.onload = function (event) {
                photoPreviewImg.src = event.target.result;
                // Mostrar botón X
                document.getElementById('btn-remove-photo').style.display = 'inline-flex';
            };
            reader.readAsDataURL(file);
        }
    });

    // Botón para eliminar foto
    document.getElementById('btn-remove-photo').addEventListener('click', function () {
        const defaultSrc = photoPreviewImg.dataset.default;
        photoPreviewImg.src = defaultSrc;
        profileAvatar.src = defaultSrc;
        selectedPhotoFile = null;
        inputPhoto.value = '';
        this.style.display = 'none';
    });

    // Guardar cambios del perfil
    btnSaveModal.addEventListener('click', function () {
        const nombre = inputNombre.value.trim();
        const apellido = inputApellido.value.trim();

        if (!nombre) {
            alert('Por favor ingresa tu nombre');
            inputNombre.focus();
            return;
        }

        if (!apellido) {
            alert('Por favor ingresa tu apellido');
            inputApellido.focus();
            return;
        }

        profileFullname.dataset.nombre = nombre;
        profileFullname.dataset.apellido = apellido;
        profileFullname.innerHTML = nombre + '<br>' + apellido;

        if (selectedPhotoFile) {
            profileAvatar.src = photoPreviewImg.src;
            if (topbarAv) topbarAv.src = photoPreviewImg.src;
        }

        // Guardar username
        const newUsername = document.getElementById('input-username').value.trim();
        if (newUsername) {
            document.querySelector('.username').textContent = '@' + newUsername;
        }

        modal.classList.remove('active');
        selectedPhotoFile = null;
    });
    // ============================================
    // GUARDAR DATOS ORIGINALES
    // ============================================
    const saveOriginalData = function () {
        const displayText = displaySobreMi.querySelector('.user-text');
        originalData.sobreMi = displayText ? displayText.textContent : '';

        originalData.tags = {};
        document.querySelectorAll('#card-descripcion .tag').forEach((tag, index) => {
            const content = tag.querySelector('.tag-content');
            const isPlaceholder = content.classList.contains('placeholder');
            originalData.tags[index] = {
                text: content.textContent,
                isPlaceholder: isPlaceholder,
                placeholder: tag.dataset.placeholder
            };
        });

        originalData.contacts = {};
        document.querySelectorAll('.contact-item').forEach(contact => {
            const type = contact.dataset.type;
            const display = contact.querySelector('.contact-display');
            const isPlaceholder = display.classList.contains('placeholder');
            originalData.contacts[type] = {
                text: display.textContent,
                isPlaceholder: isPlaceholder
            };
        });
    };

    // ============================================
    // RESTAURAR DATOS ORIGINALES
    // ============================================
    const restoreOriginalData = function () {
        if (originalData.sobreMi) {
            displaySobreMi.innerHTML = `<span class="user-text">${originalData.sobreMi}</span>`;
            textareaSobreMi.value = originalData.sobreMi;
        } else {
            displaySobreMi.innerHTML = '<span class="placeholder-text">Aquí va tu descripción detallada</span>';
            textareaSobreMi.value = '';
        }
        counterSobreMi.textContent = `${textareaSobreMi.value.length}/200`;

        document.querySelectorAll('#card-descripcion .tag').forEach((tag, index) => {
            if (originalData.tags[index]) {
                const content = tag.querySelector('.tag-content');
                const input = tag.querySelector('.tag-input');
                content.textContent = originalData.tags[index].text;
                input.value = originalData.tags[index].isPlaceholder ? '' : originalData.tags[index].text;

                if (originalData.tags[index].isPlaceholder) {
                    content.classList.add('placeholder');
                } else {
                    content.classList.remove('placeholder');
                }

                const counter = tag.querySelector('.tag-counter');
                const maxLength = tag.dataset.maxlength || 25;
                counter.textContent = `${input.value.length}/${maxLength}`;
            }
        });

        document.querySelectorAll('.contact-item').forEach(contact => {
            const type = contact.dataset.type;
            if (originalData.contacts[type]) {
                const display = contact.querySelector('.contact-display');
                const input = contact.querySelector('.contact-input');
                display.textContent = originalData.contacts[type].text;
                input.value = originalData.contacts[type].isPlaceholder ? '' : originalData.contacts[type].text;

                if (originalData.contacts[type].isPlaceholder) {
                    display.classList.add('placeholder');
                } else {
                    display.classList.remove('placeholder');
                }
            }
        });
    };

    // ============================================
    // GESTIÓN DEL MODO EDICIÓN
    // ============================================
    const toggleEditMode = function (enable) {
        isEditMode = enable;
        if (enable) {
            saveOriginalData();
            cardInfo.classList.add('edit-mode');
            btnEditCard.style.display = 'none';
            editButtons.classList.add('active');
        } else {
            cardInfo.classList.remove('edit-mode');
            btnEditCard.style.display = 'inline-flex';
            editButtons.classList.remove('active');
            document.querySelectorAll('.editing').forEach(el => el.classList.remove('editing'));
            editSobreMi.classList.remove('active');
            displaySobreMi.style.display = 'block';
        }
    };

    btnEditCard.addEventListener('click', function () {
        toggleEditMode(true);
    });

    btnCancelCard.addEventListener('click', function () {
        restoreOriginalData();
        toggleEditMode(false);
    });

    btnSaveCard.addEventListener('click', function () {
        const sobreMiText = textareaSobreMi.value.trim();
        if (sobreMiText !== '') {
            displaySobreMi.innerHTML = `<span class="user-text">${sobreMiText}</span>`;
        } else {
            displaySobreMi.innerHTML = '<span class="placeholder-text">Aquí va tu descripción detallada</span>';
        }

        // Guardar tags - permitir vacío y restaurar placeholder
        document.querySelectorAll('#card-descripcion .tag').forEach(tag => {
            const input = tag.querySelector('.tag-input');
            const content = tag.querySelector('.tag-content');
            const inputValue = input.value.trim();
            const placeholder = tag.dataset.placeholder;

            if (inputValue !== '') {
                content.textContent = inputValue;
                content.classList.remove('placeholder');
            } else {
                content.textContent = placeholder;
                content.classList.add('placeholder');
                input.value = '';
            }
        });

        // Guardar contactos
        document.querySelectorAll('.contact-item').forEach(contact => {
            const input = contact.querySelector('.contact-input');
            const display = contact.querySelector('.contact-display');
            const inputValue = input.value.trim();

            if (inputValue !== '') {
                display.textContent = inputValue;
                display.classList.remove('placeholder');
            }
        });

        toggleEditMode(false);
    });

    // ============================================
    // INTERACCIÓN CON ELEMENTOS EDITABLES
    // ============================================
    cardInfo.addEventListener('click', function (e) {
        if (!isEditMode) return;
        if (e.target.closest('.btn-delete-tag')) return;

        const tag = e.target.closest('.tag');
        const contact = e.target.closest('.contact-item');
        const sobreMiDisplayEl = e.target.closest('.sobre-mi-display');

        if (tag && !tag.classList.contains('editing')) {
            tag.classList.add('editing');
            const input = tag.querySelector('.tag-input');
            const content = tag.querySelector('.tag-content');

            if (content.classList.contains('placeholder')) {
                input.value = '';
            } else {
                input.value = content.textContent;
            }
            input.focus();

        } else if (contact && !contact.classList.contains('editing')) {
            contact.classList.add('editing');
            const input = contact.querySelector('.contact-input');
            const display = contact.querySelector('.contact-display');

            if (display.classList.contains('placeholder')) {
                input.value = '';
            } else {
                input.value = display.textContent;
            }
            input.focus();

        } else if (sobreMiDisplayEl) {
            displaySobreMi.style.display = 'none';
            editSobreMi.classList.add('active');

            const userText = displaySobreMi.querySelector('.user-text');
            if (userText) {
                textareaSobreMi.value = userText.textContent;
            } else {
                textareaSobreMi.value = '';
            }
            counterSobreMi.textContent = `${textareaSobreMi.value.length}/200`;
            textareaSobreMi.focus();
        }
    });

    // ============================================
    // CONTADOR DE CARACTERES - SOBRE MÍ
    // ============================================
    textareaSobreMi.addEventListener('input', function () {
        const count = textareaSobreMi.value.length;
        counterSobreMi.textContent = `${count}/200`;

        counterSobreMi.classList.remove('warning', 'limit');
        if (count >= 200) {
            counterSobreMi.classList.add('limit');
        } else if (count >= 180) {
            counterSobreMi.classList.add('warning');
        }
    });

    // ============================================
    // CONTADORES DE CARACTERES - TAGS
    // ============================================
    document.addEventListener('input', function (e) {
        if (e.target.classList.contains('tag-input')) {
            const tag = e.target.closest('.tag');
            const counter = tag.querySelector('.tag-counter');
            const maxLength = tag.dataset.maxlength || 25;
            counter.textContent = `${e.target.value.length}/${maxLength}`;
        }
    });

    // ============================================
    // CERRAR EDICIÓN AL PERDER FOCO
    // ============================================
    document.addEventListener('focusout', function (e) {
        if (e.target.classList.contains('tag-input')) {
            setTimeout(() => {
                const tag = e.target.closest('.tag');
                if (tag && !tag.contains(document.activeElement)) {
                    const input = e.target;
                    const content = tag.querySelector('.tag-content');
                    const placeholder = tag.dataset.placeholder;

                    if (input.value.trim() !== '') {
                        content.textContent = input.value.trim();
                        content.classList.remove('placeholder');
                    } else {
                        content.textContent = placeholder;
                        content.classList.add('placeholder');
                    }
                    tag.classList.remove('editing');
                }
            }, 100);
        }

        if (e.target.classList.contains('contact-input')) {
            setTimeout(() => {
                const contact = e.target.closest('.contact-item');
                if (contact && !contact.contains(document.activeElement)) {
                    const input = e.target;
                    const display = contact.querySelector('.contact-display');

                    if (input.value.trim() !== '') {
                        display.textContent = input.value.trim();
                        display.classList.remove('placeholder');
                    }
                    contact.classList.remove('editing');
                }
            }, 100);
        }
    });

    // ============================================
    // OBTENER SIGUIENTE SUGERENCIA
    // ============================================
    function getNextInteresSugerencia() {
        const sugerencia = interesesSugerencias[interesesIndex];
        interesesIndex = (interesesIndex + 1) % interesesSugerencias.length;
        return sugerencia;
    }

    function getNextTecnologiaSugerencia() {
        const sugerencia = tecnologiasSugerencias[tecnologiasIndex];
        tecnologiasIndex = (tecnologiasIndex + 1) % tecnologiasSugerencias.length;
        return sugerencia;
    }

    // ============================================
    // AÑADIR NUEVO TAG - INTERESES
    // ============================================
    document.getElementById('btn-add-interes').addEventListener('click', function () {
        const container = document.getElementById('tags-intereses');
        const sugerencia = getNextInteresSugerencia();
        const newTag = createNewTag(sugerencia, 25);
        container.insertBefore(newTag, this);
        newTag.classList.add('editing');
        newTag.querySelector('.tag-input').focus();
    });

    // ============================================
    // AÑADIR NUEVO TAG - TECNOLOGÍAS
    // ============================================
    document.getElementById('btn-add-tecnologia').addEventListener('click', function () {
        const container = document.getElementById('tags-tecnologias');
        const sugerencia = getNextTecnologiaSugerencia();
        const newTag = createNewTag(sugerencia, 20);
        container.insertBefore(newTag, this);
        newTag.classList.add('editing');
        newTag.querySelector('.tag-input').focus();
    });

    // ============================================
    // FUNCIÓN PARA CREAR NUEVO TAG
    // ============================================
    function createNewTag(placeholder, maxLength) {
        const tag = document.createElement('div');
        tag.className = 'tag';
        tag.dataset.placeholder = placeholder;
        tag.dataset.maxlength = maxLength;

        tag.innerHTML = `
            <button class="btn-delete-tag" title="Eliminar">
                <i class="fas fa-times"></i>
            </button>
            <span class="tag-content placeholder">${placeholder}</span>
            <input type="text" class="tag-input" maxlength="${maxLength}" placeholder="${placeholder}">
            <span class="tag-counter">0/${maxLength}</span>
        `;

        return tag;
    }

    // ============================================
    // ELIMINAR TAG
    // ============================================
    document.addEventListener('click', function (e) {
        if (e.target.closest('.btn-delete-tag')) {
            e.stopPropagation();
            const tag = e.target.closest('.tag');
            if (tag) {
                tag.style.transform = 'scale(0.8)';
                tag.style.opacity = '0';
                setTimeout(() => {
                    tag.remove();
                }, 200);
            }
        }
    });

    // ============================================
    // DROPDOWNS
    // ============================================
    document.querySelectorAll('.dropdown').forEach(dropdown => {
        const btn = dropdown.querySelector('.dropdown-btn');

        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            document.querySelectorAll('.dropdown.active').forEach(d => {
                if (d !== dropdown) d.classList.remove('active');
            });
            dropdown.classList.toggle('active');
        });
    });

    document.addEventListener('click', function () {
        document.querySelectorAll('.dropdown.active').forEach(d => {
            d.classList.remove('active');
        });
    });

    // Selección en dropdown de ordenar
    document.querySelectorAll('#dropdown-ordenar .dropdown-content a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            currentFilters.sort = this.dataset.sort;
            document.querySelectorAll('#dropdown-ordenar .dropdown-content a').forEach(a => a.classList.remove('active'));
            this.classList.add('active');
            applyFilters();
            document.getElementById('dropdown-ordenar').classList.remove('active');
        });
    });

    // Selección en dropdown de temas
    document.querySelectorAll('#dropdown-temas .dropdown-content a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            currentFilters.theme = this.dataset.theme;
            document.querySelectorAll('#dropdown-temas .dropdown-content a').forEach(a => a.classList.remove('active'));
            this.classList.add('active');
            applyFilters();
            document.getElementById('dropdown-temas').classList.remove('active');
        });
    });

    // Selección en dropdown de tecnologías
    document.querySelectorAll('#dropdown-tecnologias .dropdown-content a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            currentFilters.tech = this.dataset.tech;
            document.querySelectorAll('#dropdown-tecnologias .dropdown-content a').forEach(a => a.classList.remove('active'));
            this.classList.add('active');
            applyFilters();
            document.getElementById('dropdown-tecnologias').classList.remove('active');
        });
    });

    // ============================================
    // BÚSQUEDA
    // ============================================
    searchInput.addEventListener('input', function () {
        currentFilters.search = this.value.toLowerCase();
        searchClear.classList.toggle('visible', this.value.length > 0);
        applyFilters();
    });

    searchClear.addEventListener('click', function () {
        searchInput.value = '';
        currentFilters.search = '';
        searchClear.classList.remove('visible');
        applyFilters();
    });

    // ============================================
    // LIMPIAR FILTROS
    // ============================================
    document.getElementById('btn-clear-filters').addEventListener('click', function () {
        currentFilters = { search: '', theme: 'all', tech: 'all', sort: 'recent' };
        searchInput.value = '';
        searchClear.classList.remove('visible');
        document.querySelectorAll('.dropdown-content a').forEach(a => a.classList.remove('active'));
        document.querySelector('[data-sort="recent"]').classList.add('active');
        document.querySelector('[data-theme="all"]').classList.add('active');
        document.querySelector('[data-tech="all"]').classList.add('active');
        applyFilters();
    });

    // ============================================
    // APLICAR FILTROS
    // ============================================
    function applyFilters() {
        const cards = document.querySelectorAll('.project-card-full');
        let visibleCount = 0;

        cards.forEach(card => {
            const name = card.dataset.name.toLowerCase();
            const theme = card.dataset.theme;
            const tech = card.dataset.tech;
            let show = true;

            if (currentFilters.search && !name.includes(currentFilters.search)) show = false;
            if (currentFilters.theme !== 'all' && theme !== currentFilters.theme) show = false;
            if (currentFilters.tech !== 'all' && !tech.includes(currentFilters.tech)) show = false;

            card.style.display = show ? '' : 'none';
            if (show) visibleCount++;
        });

        sortProjects();

        if (visibleCount === 0) {
            noResults.style.display = 'block';
            projectsGrid.style.display = 'none';
            searchTerm.textContent = currentFilters.search || 'los filtros seleccionados';
        } else {
            noResults.style.display = 'none';
            projectsGrid.style.display = 'grid';
        }

        updateProjectCount();
    }

    // ============================================
    // ORDENAR PROYECTOS
    // ============================================
    function sortProjects() {
        const cards = Array.from(projectsGrid.querySelectorAll('.project-card-full'));

        cards.sort((a, b) => {
            switch (currentFilters.sort) {
                case 'recent': return new Date(b.dataset.date) - new Date(a.dataset.date);
                case 'oldest': return new Date(a.dataset.date) - new Date(b.dataset.date);
                case 'az': return a.dataset.name.localeCompare(b.dataset.name);
                case 'za': return b.dataset.name.localeCompare(a.dataset.name);
                case 'views': return parseInt(b.dataset.views) - parseInt(a.dataset.views);
                case 'collaborators': return parseInt(b.dataset.collaborators) - parseInt(a.dataset.collaborators);
                default: return 0;
            }
        });

        cards.forEach(card => projectsGrid.appendChild(card));
    }

    // ============================================
    // ACTUALIZAR CONTADOR DE PROYECTOS
    // ============================================
    function updateProjectCount() {
        const allCards = document.querySelectorAll('.project-card-full');
        const visibleCards = Array.from(allCards).filter(card => card.style.display !== 'none');
        projectCount.textContent = `(${visibleCards.length})`;
        document.getElementById('stat-proyectos').textContent = allCards.length;
    }

    // ============================================
    // TOGGLE VISTA GRID/LISTA
    // ============================================
    document.getElementById('btn-view-grid').addEventListener('click', function () {
        projectsGrid.classList.remove('list-view');
        this.classList.add('active');
        document.getElementById('btn-view-list').classList.remove('active');
    });

    document.getElementById('btn-view-list').addEventListener('click', function () {
        projectsGrid.classList.add('list-view');
        this.classList.add('active');
        document.getElementById('btn-view-grid').classList.remove('active');
    });

    // ============================================
    // MODAL NUEVO PROYECTO
    // ============================================
    const modalNewProject = document.getElementById('modal-new-project');
    const btnNewProject = document.getElementById('btn-new-project');

    btnNewProject.addEventListener('click', () => modalNewProject.classList.add('active'));
    document.getElementById('btn-close-new-project').addEventListener('click', () => { modalNewProject.classList.remove('active'); resetNewProjectForm(); });
    document.getElementById('btn-cancel-new-project').addEventListener('click', () => { modalNewProject.classList.remove('active'); resetNewProjectForm(); });

    function resetNewProjectForm() {
        document.getElementById('input-project-name').value = '';
        document.getElementById('input-project-desc').value = '';
        document.getElementById('select-project-theme').value = '';
        document.getElementById('select-project-tech').value = '';
        document.getElementById('input-project-repo').value = '';
        document.getElementById('count-project-name').textContent = '0';
        document.getElementById('count-project-desc').textContent = '0';
        const preview = document.getElementById('new-project-image-preview');
        preview.innerHTML = '<i class="fas fa-cloud-upload-alt"></i><span>Haz clic o arrastra una imagen</span>';
        preview.classList.remove('has-image');
    }

    document.getElementById('input-project-name').addEventListener('input', function () {
        document.getElementById('count-project-name').textContent = this.value.length;
    });

    document.getElementById('input-project-desc').addEventListener('input', function () {
        document.getElementById('count-project-desc').textContent = this.value.length;
    });

    const newProjectImagePreview = document.getElementById('new-project-image-preview');
    const inputProjectImage = document.getElementById('input-project-image');

    newProjectImagePreview.addEventListener('click', () => inputProjectImage.click());

    inputProjectImage.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                newProjectImagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                newProjectImagePreview.classList.add('has-image');
            };
            reader.readAsDataURL(this.files[0]);
        }
    });

    document.getElementById('btn-save-new-project').addEventListener('click', function () {
        const name = document.getElementById('input-project-name').value.trim();
        const desc = document.getElementById('input-project-desc').value.trim();
        const theme = document.getElementById('select-project-theme').value;
        const tech = document.getElementById('select-project-tech').value;

        if (!name) { alert('Por favor, ingresa un nombre para el proyecto'); return; }
        if (!desc) { alert('Por favor, ingresa una descripción'); return; }

        // Obtener imagen si se subió una
        const previewImg = newProjectImagePreview.querySelector('img');
        const imageSrc = previewImg ? previewImg.src : null;

        const newCard = createProjectCard({
            name,
            desc,
            theme,
            tech,
            date: new Date().toISOString().split('T')[0],
            views: 0,
            collaborators: 1,
            imageSrc: imageSrc
        });
        projectsGrid.appendChild(newCard);
        modalNewProject.classList.remove('active');
        resetNewProjectForm();
        updateProjectCount();
    });

    // ============================================
    // CREAR TARJETA DE PROYECTO
    // ============================================
    function createProjectCard(data) {
        const themeNames = { 'web': 'Web', 'mobile': 'Móvil', 'ia': 'IA', 'data': 'Data', 'iot': 'IoT', 'games': 'Juegos', 'security': 'Seguridad', 'automation': 'Automatización', 'api': 'API', 'devops': 'DevOps', 'research': 'Investigación' };
        const techNames = { 'python': 'Python', 'javascript': 'JavaScript', 'java': 'Java', 'react': 'React', 'angular': 'Angular', 'vue': 'Vue.js', 'node': 'Node.js', 'django': 'Django', 'flask': 'Flask', 'tensorflow': 'TensorFlow', 'docker': 'Docker', 'aws': 'AWS' };

        const card = document.createElement('div');
        card.className = 'project-card-full';
        card.dataset.name = data.name || 'Nuevo Proyecto';
        card.dataset.date = data.date;
        card.dataset.views = data.views;
        card.dataset.collaborators = data.collaborators;
        card.dataset.theme = data.theme || '';
        card.dataset.tech = data.tech || '';

        const dateFormatted = new Date(data.date).toLocaleDateString('es-ES');
        const displayName = data.name || 'Nuevo Proyecto';
        const displayDesc = data.desc || 'Descripción del proyecto';
        const isNamePlaceholder = !data.name;
        const isDescPlaceholder = !data.desc;

        // Determinar contenido de la imagen
        let imageContent;
        if (data.imageSrc) {
            imageContent = `<img src="${data.imageSrc}" alt="Imagen del proyecto">`;
        } else {
            imageContent = '<div class="project-card-img-placeholder"></div>';
        }

        card.innerHTML = `
            <div class="project-card-img">${imageContent}</div>
            <div class="project-card-body">
                <h4 class="project-card-title ${isNamePlaceholder ? 'placeholder' : ''}">${displayName}</h4>
                <p class="project-card-desc ${isDescPlaceholder ? 'placeholder' : ''}">${displayDesc}</p>
                <div class="project-card-tags">
                    ${data.tech ? `<span class="tag-tech">${techNames[data.tech] || data.tech}</span>` : ''}
                    ${data.theme ? `<span class="tag-theme">${themeNames[data.theme] || data.theme}</span>` : ''}
                </div>
                <div class="project-card-meta">
                    <span><i class="fas fa-eye"></i> ${data.views}</span>
                    <span><i class="fas fa-users"></i> ${data.collaborators}</span>
                    <span><i class="fas fa-calendar"></i> ${dateFormatted}</span>
                </div>
            </div>
        `;

        return card;
    }

    // ============================================
    // MODAL EDITAR PROYECTO
    // ============================================
    const modalEditProject = document.getElementById('modal-edit-project');
    const editProjectImagePreview = document.getElementById('edit-project-image-preview');
    const inputEditProjectImage = document.getElementById('input-edit-project-image');

    projectsGrid.addEventListener('click', function (e) {
        const card = e.target.closest('.project-card-full');
        if (card) {
            currentEditingProject = card;
            openEditProjectModal(card);
        }
    });

    function openEditProjectModal(card) {
        const titleEl = card.querySelector('.project-card-title');
        const descEl = card.querySelector('.project-card-desc');

        // Si es placeholder, mostrar vacío
        const name = titleEl.classList.contains('placeholder') ? '' : card.dataset.name;
        const desc = descEl.classList.contains('placeholder') ? '' : descEl.textContent;

        document.getElementById('edit-project-name').value = name;
        document.getElementById('edit-project-desc').value = desc;
        document.getElementById('edit-project-theme').value = card.dataset.theme || '';
        document.getElementById('edit-project-tech').value = card.dataset.tech.split(',')[0] || '';
        document.getElementById('count-edit-project-name').textContent = name.length;
        document.getElementById('count-edit-project-desc').textContent = desc.length;

        // Cargar imagen actual del proyecto o resetear
        const cardImg = card.querySelector('.project-card-img img');
        if (cardImg) {
            editProjectImagePreview.innerHTML = `<img src="${cardImg.src}" alt="Preview">`;
            editProjectImagePreview.classList.add('has-image');
        } else {
            editProjectImagePreview.innerHTML = '<i class="fas fa-cloud-upload-alt"></i><span>Haz clic o arrastra una imagen</span>';
            editProjectImagePreview.classList.remove('has-image');
        }
        // Resetear el input de archivo
        inputEditProjectImage.value = '';

        modalEditProject.classList.add('active');
    }

    document.getElementById('btn-close-edit-project').addEventListener('click', () => { modalEditProject.classList.remove('active'); currentEditingProject = null; });
    document.getElementById('btn-cancel-edit-project').addEventListener('click', () => { modalEditProject.classList.remove('active'); currentEditingProject = null; });

    document.getElementById('edit-project-name').addEventListener('input', function () {
        document.getElementById('count-edit-project-name').textContent = this.value.length;
    });

    document.getElementById('edit-project-desc').addEventListener('input', function () {
        document.getElementById('count-edit-project-desc').textContent = this.value.length;
    });

    editProjectImagePreview.addEventListener('click', () => inputEditProjectImage.click());

    inputEditProjectImage.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                editProjectImagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                editProjectImagePreview.classList.add('has-image');
            };
            reader.readAsDataURL(this.files[0]);
        }
    });

    // ============================================
    // GUARDAR EDICIÓN DE PROYECTO
    // ============================================
    document.getElementById('btn-save-edit-project').addEventListener('click', function () {
        if (!currentEditingProject) return;

        const name = document.getElementById('edit-project-name').value.trim();
        const desc = document.getElementById('edit-project-desc').value.trim();
        const theme = document.getElementById('edit-project-theme').value;
        const tech = document.getElementById('edit-project-tech').value;

        const themeNames = { 'web': 'Web', 'mobile': 'Móvil', 'ia': 'IA', 'data': 'Data', 'iot': 'IoT', 'games': 'Juegos', 'security': 'Seguridad', 'automation': 'Automatización', 'api': 'API', 'devops': 'DevOps', 'research': 'Investigación' };
        const techNames = { 'python': 'Python', 'javascript': 'JavaScript', 'java': 'Java', 'react': 'React', 'angular': 'Angular', 'vue': 'Vue.js', 'node': 'Node.js', 'django': 'Django', 'flask': 'Flask', 'tensorflow': 'TensorFlow', 'docker': 'Docker', 'aws': 'AWS' };

        const titleEl = currentEditingProject.querySelector('.project-card-title');
        const descEl = currentEditingProject.querySelector('.project-card-desc');

        // Nombre
        if (name) {
            currentEditingProject.dataset.name = name;
            titleEl.textContent = name;
            titleEl.classList.remove('placeholder');
        } else {
            currentEditingProject.dataset.name = 'Nuevo Proyecto';
            titleEl.textContent = 'Nuevo Proyecto';
            titleEl.classList.add('placeholder');
        }

        // Descripción
        if (desc) {
            descEl.textContent = desc;
            descEl.classList.remove('placeholder');
        } else {
            descEl.textContent = 'Descripción del proyecto';
            descEl.classList.add('placeholder');
        }

        currentEditingProject.dataset.theme = theme;
        currentEditingProject.dataset.tech = tech;

        const tagsContainer = currentEditingProject.querySelector('.project-card-tags');
        tagsContainer.innerHTML = '';
        if (tech) tagsContainer.innerHTML += `<span class="tag-tech">${techNames[tech] || tech}</span>`;
        if (theme) tagsContainer.innerHTML += `<span class="tag-theme">${themeNames[theme] || theme}</span>`;

        // Guardar imagen SOLO si se subió una nueva
        if (inputEditProjectImage.files && inputEditProjectImage.files[0]) {
            const previewImg = editProjectImagePreview.querySelector('img');
            if (previewImg) {
                const cardImgContainer = currentEditingProject.querySelector('.project-card-img');
                cardImgContainer.innerHTML = `<img src="${previewImg.src}" alt="Imagen del proyecto">`;
            }
        }

        modalEditProject.classList.remove('active');
        currentEditingProject = null;
    });

    // ============================================
    // ELIMINAR PROYECTO
    // ============================================
    document.getElementById('btn-delete-project').addEventListener('click', function () {
        if (!currentEditingProject) return;
        if (confirm('¿Estás seguro de que deseas eliminar este proyecto?')) {
            const cardToRemove = currentEditingProject;

            cardToRemove.classList.add('removing');

            modalEditProject.classList.remove('active');
            currentEditingProject = null;

            setTimeout(() => {
                cardToRemove.remove();
                updateProjectCount();

                projectsGrid.style.display = 'none';
                projectsGrid.offsetHeight;
                projectsGrid.style.display = 'grid';
            }, 300);
        }
    });

    // ============================================
    // CERRAR MODALES CON ESCAPE Y OVERLAY
    // ============================================
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => modal.classList.remove('active'));
            currentEditingProject = null;
        }
    });

    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function (e) {
            if (e.target === this) {
                this.classList.remove('active');
                currentEditingProject = null;
            }
        });
    });

    // ============================================
    // INICIALIZACIÓN
    // ============================================
    updateProjectCount();

});