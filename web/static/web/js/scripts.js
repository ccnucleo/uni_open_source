document.addEventListener('DOMContentLoaded', function () {

    function getCSRFToken() {
        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenInput) return tokenInput.value;
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === ('csrftoken=')) {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showToast(message, type='success') {
        const toast = document.createElement('div');
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.padding = '15px 25px';
        toast.style.background = type === 'success' ? '#22c55e' : '#ef4444';
        toast.style.color = 'white';
        toast.style.borderRadius = '8px';
        toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        toast.style.zIndex = '9999';
        toast.style.transition = 'opacity 0.3s ease';
        toast.style.fontWeight = '600';
        toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>  ${message}`;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    let isEditMode = false;
    let originalData = { sobreMi: '', tags: [], contacts: {} };
    let currentEditingProject = null;
    let currentFilters = { search: '', theme: 'all', tech: 'all', sort: 'recent' };

    const interesesSugerencias = ['IA', 'Big Data', 'Machine Learning', 'Desarrollo Web', 'Deep Learning', 'Robótica', 'Ciberseguridad', 'Cloud Computing', 'Blockchain', 'IoT', 'Data Science'];
    let interesesIndex = 4;

    const tecnologiasSugerencias = ['Python', 'Django', 'JavaScript', 'React', 'Node.js', 'Angular', 'Vue.js', 'TensorFlow', 'Docker', 'AWS'];
    let tecnologiasIndex = 4;

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
    // FUNCIÓN DINÁMICA DE "LEER MÁS"
    // ============================================
    function checkReadMore() {
        if (!displaySobreMi) return;
        const textEl = displaySobreMi.querySelector('.user-text');
        
        if (textEl) {
            let btn = displaySobreMi.querySelector('.btn-read-more');
            
            if(!textEl.classList.contains('expanded')) {
                textEl.style.maxHeight = '120px';
            }

            // Validar si el contenido excede el alto visible (130px de margen)
            if (textEl.scrollHeight > 130) {
                if (!btn) {
                    btn = document.createElement('button');
                    btn.className = 'btn-read-more';
                    btn.style.cssText = 'display: inline-block; background: none; border: none; color: var(--orange-primary); cursor: pointer; font-weight: 600; padding: 0; margin-top: 8px; font-size: 0.9rem;';
                    btn.textContent = 'Leer más';
                    
                    btn.addEventListener('click', function(e) {
                        e.stopPropagation(); 
                        textEl.classList.toggle('expanded');
                        if (textEl.classList.contains('expanded')) {
                            textEl.style.maxHeight = textEl.scrollHeight + 'px';
                            btn.textContent = 'Mostrar menos';
                        } else {
                            textEl.style.maxHeight = '120px';
                            btn.textContent = 'Leer más';
                        }
                    });
                    displaySobreMi.appendChild(btn);
                }
            } else {
                if (btn) btn.remove();
            }
        }
    }
    // Revisar al iniciar
    checkReadMore();


    if (btnDesc && btnProy) {
        btnDesc.addEventListener('click', function () {
            btnDesc.classList.add('active');
            btnProy.classList.remove('active');
            if(viewGeneral) viewGeneral.style.display = 'block';
            if(viewProjects) viewProjects.style.display = 'none';
        });

        btnProy.addEventListener('click', function () {
            btnProy.classList.add('active');
            btnDesc.classList.remove('active');
            if(viewGeneral) viewGeneral.style.display = 'none';
            if(viewProjects) viewProjects.style.display = 'block';
            updateProjectCount();
        });
    }

    const profileAvatar = document.getElementById('profile-avatar');
    const profileFullname = document.getElementById('profile-fullname');
    const photoPreviewImg = document.getElementById('photo-preview-img');
    const inputPhoto = document.getElementById('input-photo');
    const inputNombre = document.getElementById('input-nombre');
    const inputApellido = document.getElementById('input-apellido');
    const btnSaveModal = document.getElementById('btn-save-modal');

    let selectedPhotoFile = null;
    let isAvatarRemoved = false; 

    if (btnEditProfile && modal) {
        btnEditProfile.addEventListener('click', function () {
            if(inputNombre && profileFullname) inputNombre.value = profileFullname.dataset.nombre || '';
            if(inputApellido && profileFullname) inputApellido.value = profileFullname.dataset.apellido || '';
            if(photoPreviewImg && profileAvatar) photoPreviewImg.src = profileAvatar.src;
            
            selectedPhotoFile = null;
            isAvatarRemoved = false;
            
            const userSpan = document.querySelector('.username');
            const inputUsername = document.getElementById('input-username');
            if (userSpan && inputUsername) {
                inputUsername.value = userSpan.textContent.replace('@', '').trim();
            }
            modal.classList.add('active');
        });
    }

    const closeModal = function () { if (modal) modal.classList.remove('active'); };
    if (btnCancelModal) btnCancelModal.addEventListener('click', closeModal);
    if (btnCloseModal) btnCloseModal.addEventListener('click', closeModal);

    if (inputPhoto) {
        inputPhoto.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    showToast('La imagen no debe superar los 5MB', 'error');
                    this.value = ''; return;
                }
                if (!file.type.startsWith('image/')) {
                    showToast('Por favor selecciona una imagen válida', 'error');
                    this.value = ''; return;
                }
                selectedPhotoFile = file;
                isAvatarRemoved = false;
                
                const reader = new FileReader();
                reader.onload = function (event) {
                    if(photoPreviewImg) photoPreviewImg.src = event.target.result;
                    const btnRm = document.getElementById('btn-remove-photo');
                    if(btnRm) btnRm.style.display = 'inline-flex';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    const btnRemovePhoto = document.getElementById('btn-remove-photo');
    if (btnRemovePhoto) {
        btnRemovePhoto.addEventListener('click', function () {
            if(photoPreviewImg) photoPreviewImg.src = photoPreviewImg.dataset.default;
            selectedPhotoFile = null;
            isAvatarRemoved = true; 
            if(inputPhoto) inputPhoto.value = '';
            this.style.display = 'none';
        });
    }

    if (btnSaveModal) {
        btnSaveModal.addEventListener('click', function () {
            const nombre = inputNombre ? inputNombre.value.trim() : '';
            const apellido = inputApellido ? inputApellido.value.trim() : '';
            const inputUsr = document.getElementById('input-username');
            const newUsername = inputUsr ? inputUsr.value.trim() : '';

            if (!nombre || !apellido) {
                showToast('El nombre y apellido son obligatorios', 'error');
                return;
            }

            btnSaveModal.classList.add('btn-loading');

            const formData = new FormData();
            formData.append('update_type', 'basic_info');
            formData.append('first_name', nombre);
            formData.append('last_name', apellido);
            formData.append('username', newUsername);
            
            if (selectedPhotoFile) {
                formData.append('avatar', selectedPhotoFile);
            } else if (isAvatarRemoved) {
                formData.append('remove_avatar', 'true');
            }

            fetch('/accounts/api/update-profile/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRFToken() },
                body: formData
            })
            .then(res => {
                if (!res.ok) throw new Error("Fallo en el servidor");
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    if (profileFullname) {
                        profileFullname.dataset.nombre = nombre;
                        profileFullname.dataset.apellido = apellido;
                        profileFullname.innerHTML = nombre + '<br>' + apellido;
                    }
                    const userSpan = document.querySelector('.username');
                    if (newUsername && userSpan) userSpan.textContent = '@' + newUsername;
                    
                    if (selectedPhotoFile || isAvatarRemoved) {
                        if (profileAvatar) profileAvatar.src = photoPreviewImg.src;
                        const topbarAv = document.querySelector('.topbar-avatar img');
                        if (topbarAv) topbarAv.src = photoPreviewImg.src;
                    }
                    
                    if (modal) modal.classList.remove('active');
                    selectedPhotoFile = null;
                    isAvatarRemoved = false;
                    showToast(data.message, 'success');
                } else {
                    showToast(data.error, 'error');
                }
            })
            .catch((err) => {
                console.error(err);
                showToast('Error de conexión', 'error');
            })
            .finally(() => {
                btnSaveModal.classList.remove('btn-loading');
            });
        });
    }

    const saveOriginalData = function () {
        const displayText = displaySobreMi ? displaySobreMi.querySelector('.user-text') : null;
        originalData.sobreMi = displayText ? displayText.innerText : '';

        originalData.tags = [];
        document.querySelectorAll('#card-descripcion .tag').forEach((tag) => {
            const content = tag.querySelector('.tag-content');
            const input = tag.querySelector('.tag-input');
            originalData.tags.push({
                element: tag,
                text: content ? content.textContent : '',
                inputValue: input ? input.value : '',
                isPlaceholder: content ? content.classList.contains('placeholder') : false
            });
        });

        originalData.contacts = {};
        document.querySelectorAll('.contact-item').forEach(contact => {
            const type = contact.dataset.type;
            const display = contact.querySelector('.contact-display');
            if (display) {
                originalData.contacts[type] = {
                    text: display.textContent,
                    isPlaceholder: display.classList.contains('placeholder')
                };
            }
        });
    };

    const restoreOriginalData = function () {
        if (originalData.sobreMi) {
            if (displaySobreMi) {
                displaySobreMi.innerHTML = `<div class="user-text" style="white-space: pre-wrap; word-break: break-word; padding: 10px 0; color: var(--gray-700); line-height: 1.6; max-height: 120px; overflow: hidden; transition: max-height 0.3s ease;">${originalData.sobreMi}</div>`;
                setTimeout(checkReadMore, 50);
            }
            if (textareaSobreMi) {
                textareaSobreMi.value = originalData.sobreMi;
            }
        } else {
            if (displaySobreMi) displaySobreMi.innerHTML = '<div class="placeholder-text">Aquí va tu descripción detallada</div>';
            if (textareaSobreMi) textareaSobreMi.value = '';
        }
        if (counterSobreMi && textareaSobreMi) counterSobreMi.textContent = `${textareaSobreMi.value.length}/200`;

        document.querySelectorAll('.tag-new').forEach(tag => tag.remove());

        originalData.tags.forEach(item => {
            if (item.element) {
                item.element.classList.remove('tag-deleted');
                item.element.style.display = ''; 
                const content = item.element.querySelector('.tag-content');
                const input = item.element.querySelector('.tag-input');
                if (content) {
                    content.textContent = item.text;
                    if (item.isPlaceholder) content.classList.add('placeholder');
                    else content.classList.remove('placeholder');
                }
                if (input) input.value = item.inputValue;
            }
        });

        document.querySelectorAll('.contact-item').forEach(contact => {
            const type = contact.dataset.type;
            if (originalData.contacts[type]) {
                const display = contact.querySelector('.contact-display');
                const input = contact.querySelector('.contact-input');
                if (display) {
                    display.textContent = originalData.contacts[type].text;
                    if (originalData.contacts[type].isPlaceholder) display.classList.add('placeholder');
                    else display.classList.remove('placeholder');
                }
                if (input) input.value = originalData.contacts[type].isPlaceholder ? '' : originalData.contacts[type].text;
            }
        });
    };

    const toggleEditMode = function (enable) {
        isEditMode = enable;
        if (enable) {
            saveOriginalData();
            if(cardInfo) cardInfo.classList.add('edit-mode');
            if(btnEditCard) btnEditCard.style.display = 'none';
            if(editButtons) editButtons.classList.add('active');
            document.querySelectorAll('.empty-msg').forEach(msg => msg.style.display = 'none');
        } else {
            if(cardInfo) cardInfo.classList.remove('edit-mode');
            if(btnEditCard) btnEditCard.style.display = 'inline-flex';
            if(editButtons) editButtons.classList.remove('active');
            document.querySelectorAll('.editing').forEach(el => el.classList.remove('editing'));
            if(editSobreMi) editSobreMi.classList.remove('active');
            if(displaySobreMi) displaySobreMi.style.display = 'block';

            ['tags-intereses', 'tags-tecnologias'].forEach(id => {
                const container = document.getElementById(id);
                if (container) {
                    const visible = container.querySelectorAll('.tag:not(.tag-deleted)');
                    const msg = container.querySelector('.empty-msg');
                    if (msg) msg.style.display = visible.length === 0 ? 'block' : 'none';
                }
            });
            setTimeout(checkReadMore, 50);
        }
    };

    if (btnEditCard) btnEditCard.addEventListener('click', () => toggleEditMode(true));
    if (btnCancelCard) btnCancelCard.addEventListener('click', () => { restoreOriginalData(); toggleEditMode(false); });

    if (btnSaveCard) {
        btnSaveCard.addEventListener('click', function () {
            let sobreMiText = textareaSobreMi ? textareaSobreMi.value.trim() : '';
            // JS Regex: Limpiamos los excesos de Enters antes de mandar a Django
            sobreMiText = sobreMiText.replace(/\n{3,}/g, '\n\n'); 

            btnSaveCard.classList.add('btn-loading');
            
            const formData = new FormData();
            formData.append('update_type', 'detailed_info');
            formData.append('bio', sobreMiText);

            const linkedinInput = document.getElementById('input-linkedin');
            const githubInput = document.getElementById('input-github');
            const emailInput = document.getElementById('input-email');

            formData.append('linkedin', linkedinInput ? linkedinInput.value.trim() : '');
            formData.append('github', githubInput ? githubInput.value.trim() : '');
            formData.append('contact_email', emailInput ? emailInput.value.trim() : '');

            const intereses = [];
            document.querySelectorAll('#tags-intereses .tag:not(.tag-deleted)').forEach(tag => {
                const input = tag.querySelector('.tag-input');
                const content = tag.querySelector('.tag-content');
                let val = input && input.value.trim() ? input.value.trim() : '';
                if (!val && content && !content.classList.contains('placeholder')) val = content.textContent.trim();
                if (val) intereses.push(val);
            });
            formData.append('intereses', intereses.join(','));

            const tecnologias = [];
            document.querySelectorAll('#tags-tecnologias .tag:not(.tag-deleted)').forEach(tag => {
                const input = tag.querySelector('.tag-input');
                const content = tag.querySelector('.tag-content');
                let val = input && input.value.trim() ? input.value.trim() : '';
                if (!val && content && !content.classList.contains('placeholder')) val = content.textContent.trim();
                if (val) tecnologias.push(val);
            });
            formData.append('tecnologias', tecnologias.join(','));

            fetch('/accounts/api/update-profile/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRFToken() },
                body: formData
            })
            .then(res => {
                if (!res.ok) throw new Error("Fallo de comunicación con servidor");
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    if (displaySobreMi) {
                        if (sobreMiText !== '') {
                            displaySobreMi.innerHTML = `<div class="user-text" style="white-space: pre-wrap; word-break: break-word; padding: 10px 0; color: var(--gray-700); line-height: 1.6; max-height: 120px; overflow: hidden; transition: max-height 0.3s ease;">${sobreMiText}</div>`;
                        } else {
                            displaySobreMi.innerHTML = '<div class="placeholder-text">Aquí va tu descripción detallada</div>';
                        }
                    }

                    document.querySelectorAll('.tag-deleted').forEach(t => t.remove());
                    document.querySelectorAll('.tag-new').forEach(t => t.classList.remove('tag-new'));

                    document.querySelectorAll('#card-descripcion .tag').forEach(tag => {
                        const input = tag.querySelector('.tag-input');
                        const content = tag.querySelector('.tag-content');
                        if (input && content) {
                            if (input.value.trim() !== '') {
                                content.textContent = input.value.trim();
                                content.classList.remove('placeholder');
                            }
                        }
                    });

                    document.querySelectorAll('.contact-item').forEach(contact => {
                        const input = contact.querySelector('.contact-input');
                        const display = contact.querySelector('.contact-display');
                        if (input && display && input.value.trim() !== '') {
                            display.textContent = input.value.trim();
                            display.classList.remove('placeholder');
                        }
                    });

                    toggleEditMode(false);
                    showToast(data.message, 'success');
                } else {
                    showToast(data.error, 'error');
                }
            })
            .catch((err) => {
                console.error(err);
                showToast('Error interno del servidor. Intenta de nuevo.', 'error');
            })
            .finally(() => {
                btnSaveCard.classList.remove('btn-loading');
            });
        });
    }

    if (cardInfo) {
        cardInfo.addEventListener('click', function (e) {
            if (!isEditMode) return;
            if (e.target.closest('.btn-delete-tag')) return;
            if (e.target.closest('.btn-read-more')) return;

            const tag = e.target.closest('.tag');
            const contact = e.target.closest('.contact-item');
            const sobreMiDisplayEl = e.target.closest('.sobre-mi-display');

            if (tag && !tag.classList.contains('editing')) {
                tag.classList.add('editing');
                const input = tag.querySelector('.tag-input');
                const content = tag.querySelector('.tag-content');
                if (input && content) {
                    input.value = content.classList.contains('placeholder') ? '' : content.textContent;
                    input.focus();
                }
            } else if (contact && !contact.classList.contains('editing')) {
                contact.classList.add('editing');
                const input = contact.querySelector('.contact-input');
                const display = contact.querySelector('.contact-display');
                if (input && display) {
                    input.value = display.classList.contains('placeholder') ? '' : display.textContent;
                    input.focus();
                }
            } else if (sobreMiDisplayEl) {
                if(displaySobreMi) displaySobreMi.style.display = 'none';
                if(editSobreMi) editSobreMi.classList.add('active');
                
                const userText = displaySobreMi ? displaySobreMi.querySelector('.user-text') : null;
                if (textareaSobreMi) {
                    textareaSobreMi.value = userText ? userText.innerText : '';
                    if (counterSobreMi) counterSobreMi.textContent = `${textareaSobreMi.value.length}/200`;
                    
                    textareaSobreMi.style.height = 'auto';
                    textareaSobreMi.style.height = Math.min(textareaSobreMi.scrollHeight, 180) + 'px';
                    textareaSobreMi.style.overflowY = textareaSobreMi.scrollHeight > 180 ? 'auto' : 'hidden';
                    
                    textareaSobreMi.focus();
                }
            }
        });
    }

    if (textareaSobreMi) {
        textareaSobreMi.addEventListener('input', function () {
            this.style.height = 'auto';
            const newHeight = Math.min(this.scrollHeight, 180);
            this.style.height = newHeight + 'px';
            this.style.overflowY = this.scrollHeight > 180 ? 'auto' : 'hidden';
            
            const count = this.value.length;
            if (counterSobreMi) {
                counterSobreMi.textContent = `${count}/200`;
                counterSobreMi.classList.remove('warning', 'limit');
                if (count >= 200) counterSobreMi.classList.add('limit');
                else if (count >= 180) counterSobreMi.classList.add('warning');
            }
        });
    }

    document.addEventListener('input', function (e) {
        if (e.target.classList.contains('tag-input')) {
            const tag = e.target.closest('.tag');
            const counter = tag ? tag.querySelector('.tag-counter') : null;
            if (counter) {
                const maxLength = tag.dataset.maxlength || 25;
                counter.textContent = `${e.target.value.length}/${maxLength}`;
            }
        }
    });

    document.addEventListener('focusout', function (e) {
        if (e.target.classList.contains('tag-input')) {
            setTimeout(() => {
                const tag = e.target.closest('.tag');
                if (tag && !tag.contains(document.activeElement)) {
                    const input = e.target;
                    const content = tag.querySelector('.tag-content');
                    if (content) {
                        if (input.value.trim() !== '') {
                            content.textContent = input.value.trim();
                            content.classList.remove('placeholder');
                        } else {
                            content.textContent = tag.dataset.placeholder;
                            content.classList.add('placeholder');
                        }
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
                    if (display) {
                        if (input.value.trim() !== '') {
                            display.textContent = input.value.trim();
                            display.classList.remove('placeholder');
                        }
                    }
                    contact.classList.remove('editing');
                }
            }, 100);
        }
    });

    function createNewTag(placeholder, maxLength, isFilled = false) {
        const tag = document.createElement('div');
        tag.className = 'tag tag-new';
        tag.dataset.placeholder = placeholder;
        tag.dataset.maxlength = maxLength;
        
        const contentClass = isFilled ? 'tag-content' : 'tag-content placeholder';
        
        tag.innerHTML = `
            <button class="btn-delete-tag" title="Eliminar"><i class="fas fa-times"></i></button>
            <span class="${contentClass}">${placeholder}</span>
            <input type="text" class="tag-input" maxlength="${maxLength}" placeholder="${placeholder}">
            <span class="tag-counter">0/${maxLength}</span>
        `;
        return tag;
    }

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

    const btnAddInteres = document.getElementById('btn-add-interes');
    if (btnAddInteres) {
        btnAddInteres.addEventListener('click', function () {
            const container = document.getElementById('tags-intereses');
            if (container) {
                const sug = getNextInteresSugerencia();
                const nt = createNewTag(sug, 25, true);
                container.insertBefore(nt, this);
                nt.classList.add('editing');
                const inp = nt.querySelector('.tag-input');
                if(inp) {
                    inp.value = sug;
                    inp.focus();
                }
            }
        });
    }

    const btnAddTecnologia = document.getElementById('btn-add-tecnologia');
    if (btnAddTecnologia) {
        btnAddTecnologia.addEventListener('click', function () {
            const container = document.getElementById('tags-tecnologias');
            if(container) {
                const sug = getNextTecnologiaSugerencia();
                const nt = createNewTag(sug, 20, true);
                container.insertBefore(nt, this);
                nt.classList.add('editing');
                const inp = nt.querySelector('.tag-input');
                if(inp) {
                    inp.value = sug;
                    inp.focus();
                }
            }
        });
    }

    document.addEventListener('click', function (e) {
        if (e.target.closest('.btn-delete-tag')) {
            e.stopPropagation();
            const tag = e.target.closest('.tag');
            if (tag) {
                if (tag.classList.contains('tag-new')) {
                    tag.remove();
                } else {
                    tag.classList.add('tag-deleted');
                    tag.style.display = 'none';
                }
            }
        }
    });

    document.querySelectorAll('.dropdown').forEach(dropdown => {
        const btn = dropdown.querySelector('.dropdown-btn');
        if (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                document.querySelectorAll('.dropdown.active').forEach(d => {
                    if (d !== dropdown) d.classList.remove('active');
                });
                dropdown.classList.toggle('active');
            });
        }
    });

    document.addEventListener('click', function () {
        document.querySelectorAll('.dropdown.active').forEach(d => d.classList.remove('active'));
    });

    document.querySelectorAll('#dropdown-ordenar .dropdown-content a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            currentFilters.sort = this.dataset.sort;
            document.querySelectorAll('#dropdown-ordenar .dropdown-content a').forEach(a => a.classList.remove('active'));
            this.classList.add('active');
            applyFilters();
            const drop = document.getElementById('dropdown-ordenar');
            if (drop) drop.classList.remove('active');
        });
    });

    document.querySelectorAll('#dropdown-temas .dropdown-content a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            currentFilters.theme = this.dataset.theme;
            document.querySelectorAll('#dropdown-temas .dropdown-content a').forEach(a => a.classList.remove('active'));
            this.classList.add('active');
            applyFilters();
            const drop = document.getElementById('dropdown-temas');
            if (drop) drop.classList.remove('active');
        });
    });

    document.querySelectorAll('#dropdown-tecnologias .dropdown-content a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            currentFilters.tech = this.dataset.tech;
            document.querySelectorAll('#dropdown-tecnologias .dropdown-content a').forEach(a => a.classList.remove('active'));
            this.classList.add('active');
            applyFilters();
            const drop = document.getElementById('dropdown-tecnologias');
            if (drop) drop.classList.remove('active');
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            currentFilters.search = this.value.toLowerCase();
            if (searchClear) searchClear.classList.toggle('visible', this.value.length > 0);
            applyFilters();
        });
    }

    if (searchClear) {
        searchClear.addEventListener('click', function () {
            if (searchInput) searchInput.value = '';
            currentFilters.search = '';
            searchClear.classList.remove('visible');
            applyFilters();
        });
    }

    const btnClearFilters = document.getElementById('btn-clear-filters');
    if (btnClearFilters) {
        btnClearFilters.addEventListener('click', function () {
            currentFilters = { search: '', theme: 'all', tech: 'all', sort: 'recent' };
            if (searchInput) searchInput.value = '';
            if (searchClear) searchClear.classList.remove('visible');
            document.querySelectorAll('.dropdown-content a').forEach(a => a.classList.remove('active'));
            const sortRecent = document.querySelector('[data-sort="recent"]');
            if (sortRecent) sortRecent.classList.add('active');
            const themeAll = document.querySelector('[data-theme="all"]');
            if (themeAll) themeAll.classList.add('active');
            const techAll = document.querySelector('[data-tech="all"]');
            if (techAll) techAll.classList.add('active');
            applyFilters();
        });
    }

    function applyFilters() {
        const cards = document.querySelectorAll('.project-card-full');
        let visibleCount = 0;

        cards.forEach(card => {
            const name = card.dataset.name ? card.dataset.name.toLowerCase() : '';
            const theme = card.dataset.theme;
            const tech = card.dataset.tech;
            let show = true;

            if (currentFilters.search && !name.includes(currentFilters.search)) show = false;
            if (currentFilters.theme !== 'all' && theme !== currentFilters.theme) show = false;
            if (currentFilters.tech !== 'all' && (!tech || !tech.includes(currentFilters.tech))) show = false;

            card.style.display = show ? '' : 'none';
            if (show) visibleCount++;
        });

        sortProjects();

        if (noResults && projectsGrid && searchTerm) {
            if (visibleCount === 0) {
                noResults.style.display = 'block';
                projectsGrid.style.display = 'none';
                searchTerm.textContent = currentFilters.search || 'los filtros seleccionados';
            } else {
                noResults.style.display = 'none';
                projectsGrid.style.display = 'grid';
            }
        }

        updateProjectCount();
    }

    function sortProjects() {
        if (!projectsGrid) return;
        const cards = Array.from(projectsGrid.querySelectorAll('.project-card-full'));

        cards.sort((a, b) => {
            switch (currentFilters.sort) {
                case 'recent': return new Date(b.dataset.date || 0) - new Date(a.dataset.date || 0);
                case 'oldest': return new Date(a.dataset.date || 0) - new Date(b.dataset.date || 0);
                case 'az': return (a.dataset.name || '').localeCompare(b.dataset.name || '');
                case 'za': return (b.dataset.name || '').localeCompare(a.dataset.name || '');
                case 'views': return parseInt(b.dataset.views || 0) - parseInt(a.dataset.views || 0);
                case 'collaborators': return parseInt(b.dataset.collaborators || 0) - parseInt(a.dataset.collaborators || 0);
                default: return 0;
            }
        });

        cards.forEach(card => projectsGrid.appendChild(card));
    }

    function updateProjectCount() {
        const allCards = document.querySelectorAll('.project-card-full');
        const visibleCards = Array.from(allCards).filter(card => card.style.display !== 'none');
        if (projectCount) projectCount.textContent = `(${visibleCards.length})`;
        const statProyectos = document.getElementById('stat-proyectos');
        if (statProyectos) statProyectos.textContent = allCards.length;
    }

    const btnViewGrid = document.getElementById('btn-view-grid');
    const btnViewList = document.getElementById('btn-view-list');
    
    if (btnViewGrid && btnViewList && projectsGrid) {
        btnViewGrid.addEventListener('click', function () {
            projectsGrid.classList.remove('list-view');
            this.classList.add('active');
            btnViewList.classList.remove('active');
        });

        btnViewList.addEventListener('click', function () {
            projectsGrid.classList.add('list-view');
            this.classList.add('active');
            btnViewGrid.classList.remove('active');
        });
    }

    const modalNewProject = document.getElementById('modal-new-project');
    const btnNewProjectTrigger = document.getElementById('btn-new-project');

    if (btnNewProjectTrigger && modalNewProject) {
        btnNewProjectTrigger.addEventListener('click', () => modalNewProject.classList.add('active'));
        
        const btnCloseNew = document.getElementById('btn-close-new-project');
        const btnCancelNew = document.getElementById('btn-cancel-new-project');
        
        if(btnCloseNew) btnCloseNew.addEventListener('click', () => { modalNewProject.classList.remove('active'); resetNewProjectForm(); });
        if(btnCancelNew) btnCancelNew.addEventListener('click', () => { modalNewProject.classList.remove('active'); resetNewProjectForm(); });
    }

    function resetNewProjectForm() {
        if(document.getElementById('input-project-name')) document.getElementById('input-project-name').value = '';
        if(document.getElementById('input-project-desc')) document.getElementById('input-project-desc').value = '';
        if(document.getElementById('select-project-theme')) document.getElementById('select-project-theme').value = '';
        if(document.getElementById('select-project-tech')) document.getElementById('select-project-tech').value = '';
        if(document.getElementById('input-project-repo')) document.getElementById('input-project-repo').value = '';
        if(document.getElementById('count-project-name')) document.getElementById('count-project-name').textContent = '0';
        if(document.getElementById('count-project-desc')) document.getElementById('count-project-desc').textContent = '0';
        
        const preview = document.getElementById('new-project-image-preview');
        if (preview) {
            preview.innerHTML = '<i class="fas fa-cloud-upload-alt"></i><span>Haz clic o arrastra una imagen</span>';
            preview.classList.remove('has-image');
        }
        
        if(document.getElementById('input-project-p1')) document.getElementById('input-project-p1').value = '';
        if(document.getElementById('input-project-p2')) document.getElementById('input-project-p2').value = '';
        if(document.getElementById('input-project-p3')) document.getElementById('input-project-p3').value = '';
        if(document.getElementById('input-project-tags')) document.getElementById('input-project-tags').value = '';
        if(document.getElementById('new-project-tags-list')) document.getElementById('new-project-tags-list').innerHTML = '';
        if(document.getElementById('gallery-preview-grid')) document.getElementById('gallery-preview-grid').innerHTML = '';
        if(document.getElementById('input-gallery-images')) document.getElementById('input-gallery-images').value = '';
        window.newProjectTagsArray = [];
    }

    const inputProjectName = document.getElementById('input-project-name');
    if (inputProjectName) {
        inputProjectName.addEventListener('input', function () {
            const countLabel = document.getElementById('count-project-name');
            if(countLabel) countLabel.textContent = this.value.length;
        });
    }

    const inputProjectDesc = document.getElementById('input-project-desc');
    if (inputProjectDesc) {
        inputProjectDesc.addEventListener('input', function () {
            const countLabel = document.getElementById('count-project-desc');
            if(countLabel) countLabel.textContent = this.value.length;
        });
    }

    const newProjectImagePreview = document.getElementById('new-project-image-preview');
    const inputProjectImage = document.getElementById('input-project-image');

    if (newProjectImagePreview && inputProjectImage) {
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
    }

    const btnSaveNewProject = document.getElementById('btn-save-new-project');
    if (btnSaveNewProject) {
        btnSaveNewProject.addEventListener('click', function () {
            const name = document.getElementById('input-project-name').value.trim();
            const desc = document.getElementById('input-project-desc').value.trim();
            const theme = document.getElementById('select-project-theme').value;
            const tech = document.getElementById('select-project-tech').value;

            if (!name) { showToast('Por favor, ingresa un nombre para el proyecto', 'error'); return; }
            if (!desc) { showToast('Por favor, ingresa una descripción', 'error'); return; }

            const previewImg = newProjectImagePreview.querySelector('img');
            const imageSrc = previewImg ? previewImg.src : null;

            const newCard = createProjectCard({
                name, desc, theme, tech,
                date: new Date().toISOString().split('T')[0],
                views: 0, collaborators: 1, imageSrc: imageSrc
            });
            if(projectsGrid) projectsGrid.appendChild(newCard);
            if(modalNewProject) modalNewProject.classList.remove('active');
            resetNewProjectForm();
            updateProjectCount();
        });
    }

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

        let imageContent = data.imageSrc ? `<img src="${data.imageSrc}" alt="Imagen del proyecto">` : '<div class="project-card-img-placeholder"></div>';

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

    const modalEditProject = document.getElementById('modal-edit-project');
    const editProjectImagePreview = document.getElementById('edit-project-image-preview');
    const inputEditProjectImage = document.getElementById('input-edit-project-image');

    if (projectsGrid) {
        projectsGrid.addEventListener('click', function (e) {
            const editBtn = e.target.closest('.btn-edit-card-icon');
            if (editBtn) {
                e.preventDefault();
                e.stopPropagation();
                
                const card = editBtn.closest('.project-card-full');
                if (card) {
                    currentEditingProject = card;
                    openEditProjectModal(card);
                }
            }
        });
    }

    function openEditProjectModal(card) {
        const titleEl = card.querySelector('.project-card-title');
        const descEl = card.querySelector('.project-card-desc');

        const name = titleEl && titleEl.classList.contains('placeholder') ? '' : card.dataset.name;
        const desc = descEl && descEl.classList.contains('placeholder') ? '' : descEl.textContent;

        const editNameInp = document.getElementById('edit-project-name');
        if(editNameInp) editNameInp.value = name;
        
        const editDescInp = document.getElementById('edit-project-desc');
        if(editDescInp) editDescInp.value = desc;
        
        const editTheme = document.getElementById('edit-project-theme');
        if(editTheme) editTheme.value = card.dataset.theme || '';
        
        const editTech = document.getElementById('edit-project-tech');
        if(editTech) editTech.value = card.dataset.tech ? card.dataset.tech.split(',')[0] : '';
        
        const countName = document.getElementById('count-edit-project-name');
        if(countName) countName.textContent = name ? name.length : 0;
        
        const countDesc = document.getElementById('count-edit-project-desc');
        if(countDesc) countDesc.textContent = desc ? desc.length : 0;

        const cardImg = card.querySelector('.project-card-img img');
        if (editProjectImagePreview) {
            if (cardImg) {
                editProjectImagePreview.innerHTML = `<img src="${cardImg.src}" alt="Preview">`;
                editProjectImagePreview.classList.add('has-image');
            } else {
                editProjectImagePreview.innerHTML = '<i class="fas fa-cloud-upload-alt"></i><span>Haz clic o arrastra una imagen</span>';
                editProjectImagePreview.classList.remove('has-image');
            }
        }
        if(inputEditProjectImage) inputEditProjectImage.value = '';

        if(modalEditProject) modalEditProject.classList.add('active');
    }

    function resetEditProjectForm() {
        if(document.getElementById('edit-project-tags-list')) document.getElementById('edit-project-tags-list').innerHTML = '';
        if(document.getElementById('input-edit-project-tags')) document.getElementById('input-edit-project-tags').value = '';
        if(document.getElementById('edit-project-p1')) document.getElementById('edit-project-p1').value = '';
        if(document.getElementById('edit-project-p2')) document.getElementById('edit-project-p2').value = '';
        if(document.getElementById('edit-project-p3')) document.getElementById('edit-project-p3').value = '';
        if(document.getElementById('edit-gallery-preview-grid')) document.getElementById('edit-gallery-preview-grid').innerHTML = '';
        if(document.getElementById('input-edit-gallery-images')) document.getElementById('input-edit-gallery-images').value = '';
        window.editProjectTagsArray = [];
    }

    const btnCloseEditProject = document.getElementById('btn-close-edit-project');
    const btnCancelEditProject = document.getElementById('btn-cancel-edit-project');
    
    if (btnCloseEditProject) btnCloseEditProject.addEventListener('click', () => { if(modalEditProject) modalEditProject.classList.remove('active'); currentEditingProject = null; resetEditProjectForm(); });
    if (btnCancelEditProject) btnCancelEditProject.addEventListener('click', () => { if(modalEditProject) modalEditProject.classList.remove('active'); currentEditingProject = null; resetEditProjectForm(); });

    const editProjectName = document.getElementById('edit-project-name');
    if (editProjectName) editProjectName.addEventListener('input', function () { 
        const ct = document.getElementById('count-edit-project-name');
        if(ct) ct.textContent = this.value.length; 
    });

    const editProjectDesc = document.getElementById('edit-project-desc');
    if (editProjectDesc) editProjectDesc.addEventListener('input', function () { 
        const ct = document.getElementById('count-edit-project-desc');
        if(ct) ct.textContent = this.value.length; 
    });

    if (editProjectImagePreview && inputEditProjectImage) {
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
    }

    window.newProjectTagsArray = [];
    window.editProjectTagsArray = [];

    function setupTagsLogic(inputId, listId, arrayVarName) {
        const input = document.getElementById(inputId);
        const list = document.getElementById(listId);
        if (!input || !list) return;

        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const value = this.value.trim();
                if (value && !window[arrayVarName].includes(value)) {
                    window[arrayVarName].push(value);
                    renderTags(list, window[arrayVarName]);
                }
                this.value = '';
            }
        });

        list.addEventListener('click', function(e) {
            if (e.target.classList.contains('tag-chip-remove')) {
                const index = e.target.getAttribute('data-index');
                window[arrayVarName].splice(index, 1);
                renderTags(list, window[arrayVarName]);
            }
        });
    }

    function renderTags(listElement, currentArray) {
        if(!listElement) return;
        listElement.innerHTML = '';
        currentArray.forEach((tag, index) => {
            const chip = document.createElement('span');
            chip.className = 'tag-chip';
            chip.innerHTML = `#${tag} <span class="tag-chip-remove" data-index="${index}">x</span>`;
            listElement.appendChild(chip);
        });
    }

    setupTagsLogic('input-project-tags', 'new-project-tags-list', 'newProjectTagsArray');
    setupTagsLogic('input-edit-project-tags', 'edit-project-tags-list', 'editProjectTagsArray');

    function setupGallery(dropAreaId, inputId, previewGridId) {
        const dropArea = document.getElementById(dropAreaId);
        const input = document.getElementById(inputId);
        const previewGrid = document.getElementById(previewGridId);
        if (!dropArea || !input || !previewGrid) return;

        dropArea.addEventListener('click', () => input.click());

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, e => { e.preventDefault(); e.stopPropagation(); }, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.style.borderColor = 'var(--orange-primary)';
                dropArea.style.backgroundColor = 'var(--orange-light)';
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.style.borderColor = 'var(--gray-300)';
                dropArea.style.backgroundColor = 'white';
            });
        });

        dropArea.addEventListener('drop', (e) => handleFiles(e.dataTransfer.files));
        input.addEventListener('change', function() { handleFiles(this.files); this.value = ''; });

        function handleFiles(files) {
            Array.from(files).forEach(file => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        const thumbDiv = document.createElement('div');
                        thumbDiv.className = 'gallery-thumbnail';
                        thumbDiv.innerHTML = `
                            <img src="${event.target.result}" alt="Gallery image">
                            <button type="button" class="gallery-thumbnail-remove" title="Eliminar"><i class="fas fa-times"></i></button>
                        `;
                        thumbDiv.querySelector('.gallery-thumbnail-remove').addEventListener('click', function(e) {
                            e.stopPropagation();
                            thumbDiv.remove();
                        });
                        previewGrid.appendChild(thumbDiv);
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    }

    setupGallery('gallery-upload-area', 'input-gallery-images', 'gallery-preview-grid');
    setupGallery('edit-gallery-upload-area', 'input-edit-gallery-images', 'edit-gallery-preview-grid');

    const btnSaveEditProject = document.getElementById('btn-save-edit-project');
    if (btnSaveEditProject) {
        btnSaveEditProject.addEventListener('click', function () {
            if (!currentEditingProject) return;

            const name = document.getElementById('edit-project-name').value.trim();
            const desc = document.getElementById('edit-project-desc').value.trim();
            const theme = document.getElementById('edit-project-theme').value;
            const tech = document.getElementById('edit-project-tech').value;

            const themeNames = { 'web': 'Web', 'mobile': 'Móvil', 'ia': 'IA', 'data': 'Data', 'iot': 'IoT', 'games': 'Juegos', 'security': 'Seguridad', 'automation': 'Automatización', 'api': 'API', 'devops': 'DevOps', 'research': 'Investigación' };
            const techNames = { 'python': 'Python', 'javascript': 'JavaScript', 'java': 'Java', 'react': 'React', 'angular': 'Angular', 'vue': 'Vue.js', 'node': 'Node.js', 'django': 'Django', 'flask': 'Flask', 'tensorflow': 'TensorFlow', 'docker': 'Docker', 'aws': 'AWS' };

            const titleEl = currentEditingProject.querySelector('.project-card-title');
            const descEl = currentEditingProject.querySelector('.project-card-desc');

            if (name) {
                currentEditingProject.dataset.name = name;
                if(titleEl) { titleEl.textContent = name; titleEl.classList.remove('placeholder'); }
            } else {
                currentEditingProject.dataset.name = 'Nuevo Proyecto';
                if(titleEl) { titleEl.textContent = 'Nuevo Proyecto'; titleEl.classList.add('placeholder'); }
            }

            if (desc) {
                if(descEl) { descEl.textContent = desc; descEl.classList.remove('placeholder'); }
            } else {
                if(descEl) { descEl.textContent = 'Descripción del proyecto'; descEl.classList.add('placeholder'); }
            }

            currentEditingProject.dataset.theme = theme;
            currentEditingProject.dataset.tech = tech;

            const tagsContainer = currentEditingProject.querySelector('.project-card-tags');
            if(tagsContainer) {
                tagsContainer.innerHTML = '';
                if (tech) tagsContainer.innerHTML += `<span class="tag-tech">${techNames[tech] || tech}</span>`;
                if (theme) tagsContainer.innerHTML += `<span class="tag-theme">${themeNames[theme] || theme}</span>`;
            }

            if (inputEditProjectImage && inputEditProjectImage.files && inputEditProjectImage.files[0]) {
                const previewImg = editProjectImagePreview ? editProjectImagePreview.querySelector('img') : null;
                if (previewImg) {
                    const cardImgContainer = currentEditingProject.querySelector('.project-card-img');
                    if(cardImgContainer) cardImgContainer.innerHTML = `<img src="${previewImg.src}" alt="Imagen del proyecto">`;
                }
            }

            if(modalEditProject) modalEditProject.classList.remove('active');
            currentEditingProject = null;
        });
    }

    const btnDeleteProject = document.getElementById('btn-delete-project');
    if (btnDeleteProject) {
        btnDeleteProject.addEventListener('click', function () {
            if (!currentEditingProject) return;
            if (confirm('¿Estás seguro de que deseas eliminar este proyecto?')) {
                const cardToRemove = currentEditingProject;
                cardToRemove.classList.add('removing');

                if(modalEditProject) modalEditProject.classList.remove('active');
                currentEditingProject = null;

                setTimeout(() => {
                    cardToRemove.remove();
                    updateProjectCount();
                    if(projectsGrid) {
                        projectsGrid.style.display = 'none';
                        projectsGrid.offsetHeight;
                        projectsGrid.style.display = 'grid';
                    }
                }, 300);
            }
        });
    }

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => {
                modal.classList.remove('active');
                if(modal.id === 'modal-edit-project') resetEditProjectForm();
                if(modal.id === 'modal-new-project') resetNewProjectForm();
            });
            currentEditingProject = null;
        }
    });

    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function (e) {
            if (e.target === this) {
                this.classList.remove('active');
                if(this.id === 'modal-edit-project') resetEditProjectForm();
                if(this.id === 'modal-new-project') resetNewProjectForm();
                currentEditingProject = null;
            }
        });
    });

    if (document.getElementById('project-count')) {
        updateProjectCount();
    }
});