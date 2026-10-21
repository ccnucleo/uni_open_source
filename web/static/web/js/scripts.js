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

    function showToast(message, type = 'success') {
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
            if (!textEl.classList.contains('expanded')) {
                textEl.style.maxHeight = '120px';
            }

            if (textEl.scrollHeight > 130) {
                if (!btn) {
                    btn = document.createElement('button');
                    btn.className = 'btn-read-more';
                    btn.style.cssText = 'display: inline-block; background: none; border: none; color: var(--orange-primary); cursor: pointer; font-weight: 600; padding: 0; margin-top: 8px; font-size: 0.9rem;';
                    btn.textContent = 'Leer más';

                    btn.addEventListener('click', function (e) {
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
    checkReadMore();

    if (btnDesc && btnProy) {
        btnDesc.addEventListener('click', function () {
            btnDesc.classList.add('active');
            btnProy.classList.remove('active');
            if (viewGeneral) viewGeneral.style.display = 'block';
            if (viewProjects) viewProjects.style.display = 'none';
        });

        btnProy.addEventListener('click', function () {
            btnProy.classList.add('active');
            btnDesc.classList.remove('active');
            if (viewGeneral) viewGeneral.style.display = 'none';
            if (viewProjects) viewProjects.style.display = 'block';
            updateProjectCount();
        });
    }

    const profileAvatar = document.getElementById('profile-avatar');
    const profilePicContainer = document.getElementById('profile-pic-container');
    const profileFullname = document.getElementById('profile-fullname');
    const photoPreviewImg = document.getElementById('photo-preview-img');
    const inputPhoto = document.getElementById('input-photo');
    const inputNombre = document.getElementById('input-nombre');
    const inputApellido = document.getElementById('input-apellido');
    const btnSaveModal = document.getElementById('btn-save-modal');

    let selectedPhotoFile = null;
    let isAvatarRemoved = false;
    let avatarCropper = null;
    let croppedAvatarBlob = null;

    const openBasicModal = function () {
        if (!modal) return;
        if (inputNombre && profileFullname) inputNombre.value = profileFullname.dataset.nombre || '';
        if (inputApellido && profileFullname) inputApellido.value = profileFullname.dataset.apellido || '';

        const currentAvatar = document.getElementById('profile-avatar');
        const previewContainer = document.getElementById('modal-photo-preview');
        const btnRemovePhoto = document.getElementById('btn-remove-photo');
        
        if (currentAvatar && previewContainer) {
            const clonedAvatar = currentAvatar.cloneNode(true);
            clonedAvatar.id = 'photo-preview-img';
            
            if (clonedAvatar.tagName === 'DIV') {
                clonedAvatar.style.fontSize = '2rem';
                if (btnRemovePhoto) btnRemovePhoto.style.display = 'none';
            } else {
                if (btnRemovePhoto) btnRemovePhoto.style.display = 'inline-flex';
            }
            
            previewContainer.innerHTML = '';
            previewContainer.appendChild(clonedAvatar);
        }

        selectedPhotoFile = null;
        isAvatarRemoved = false;
        croppedAvatarBlob = null;
        if (avatarCropper) { avatarCropper.destroy(); avatarCropper = null; }

        const userSpan = document.querySelector('.username');
        const inputUsername = document.getElementById('input-username');
        if (userSpan && inputUsername) {
            inputUsername.value = userSpan.textContent.replace('@', '').trim();
        }
        modal.classList.add('active');
    };

    if (btnEditProfile) btnEditProfile.addEventListener('click', openBasicModal);
    if (profilePicContainer) profilePicContainer.addEventListener('click', openBasicModal);

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
                    const modalCrop = document.getElementById('modal-crop-avatar');
                    const cropImg = document.getElementById('crop-avatar-img');

                    if (modalCrop && cropImg) {
                        cropImg.src = event.target.result;
                        modalCrop.classList.add('active');

                        if (avatarCropper) { avatarCropper.destroy(); }

                        // Pequeño timeout para que el modal se muestre antes de inicializar cropper
                        setTimeout(() => {
                            avatarCropper = new Cropper(cropImg, {
                                aspectRatio: 1,
                                viewMode: 1,
                                autoCropArea: 1,
                            });
                        }, 100);
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Lógica para los botones del modal de recorte
    const btnConfirmCrop = document.getElementById('btn-confirm-crop');
    const btnCancelCrop = document.getElementById('btn-cancel-crop');
    const btnCloseCropModal = document.getElementById('btn-close-crop-modal');

    const closeCropModal = () => {
        const modalCrop = document.getElementById('modal-crop-avatar');
        if (modalCrop) modalCrop.classList.remove('active');
        if (avatarCropper) { avatarCropper.destroy(); avatarCropper = null; }
        if (inputPhoto) inputPhoto.value = '';
    };

    if (btnCancelCrop) btnCancelCrop.addEventListener('click', closeCropModal);
    if (btnCloseCropModal) btnCloseCropModal.addEventListener('click', closeCropModal);

    if (btnConfirmCrop) {
        btnConfirmCrop.addEventListener('click', function () {
            if (avatarCropper) {
                avatarCropper.getCroppedCanvas({ width: 400, height: 400 }).toBlob((blob) => {
                    croppedAvatarBlob = blob;
                    const previewEl = document.getElementById('photo-preview-img');
                    const newSrc = avatarCropper.getCroppedCanvas().toDataURL();
                    if (previewEl) {
                        if (previewEl.tagName === 'IMG') {
                            previewEl.src = newSrc;
                            previewEl.style.maxHeight = 'none';
                            previewEl.style.display = 'block';
                        } else {
                            // Era un div de iniciales; reemplazarlo por img
                            const img = document.createElement('img');
                            img.id = 'photo-preview-img';
                            img.src = newSrc;
                            img.alt = 'Preview';
                            img.style.cssText = 'width:100%;height:100%;object-fit:cover;display:block;border-radius:50%;';
                            previewEl.replaceWith(img);
                        }
                    }
                    const btnRm = document.getElementById('btn-remove-photo');
                    if (btnRm) btnRm.style.display = 'inline-flex';

                    closeCropModal();
                }, 'image/jpeg');
            }
        });
    }

    const btnRemovePhoto = document.getElementById('btn-remove-photo');
    if (btnRemovePhoto) {
        btnRemovePhoto.addEventListener('click', function () {
            // Actualizar preview del modal a iniciales
            const previewContainer = document.getElementById('modal-photo-preview');
            const oldPreview = document.getElementById('photo-preview-img');
            if (oldPreview && previewContainer) {
                const nombre = inputNombre ? inputNombre.value.trim() : '';
                const apellido = inputApellido ? inputApellido.value.trim() : '';
                const username = document.querySelector('.username')?.textContent?.replace('@', '').trim() || '';
                const initials = (() => {
                    if (nombre && apellido) return (nombre[0] + apellido[0]).toUpperCase();
                    return (username[0] || '?').toUpperCase();
                })();
                const avatarColors = ['#f97316', '#3b82f6', '#10b981', '#8b5cf6', '#ec4899', '#14b8a6', '#f43f5e', '#6366f1'];
                const getIdx = (str, len) => { let h = 0; for (let i = 0; i < str.length; i++) h = str.charCodeAt(i) + ((h << 5) - h); return Math.abs(h) % len; };
                const bgColor = avatarColors[getIdx(username, avatarColors.length)];
                const div = document.createElement('div');
                div.id = 'photo-preview-img';
                div.className = 'profile-initials-avatar';
                div.style.cssText = `width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:800;color:white;background:${bgColor};`;
                div.textContent = initials;
                oldPreview.replaceWith(div);
            }
            selectedPhotoFile = null;
            croppedAvatarBlob = null;
            isAvatarRemoved = true;
            if (inputPhoto) inputPhoto.value = '';
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

            const submitProfileData = () => {
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

                            if (croppedAvatarBlob || isAvatarRemoved) {
                                const avatarColors = ['#f97316', '#3b82f6', '#10b981', '#8b5cf6', '#ec4899', '#14b8a6', '#f43f5e', '#6366f1'];
                                const getIdx = (str, len) => { let h = 0; for (let i = 0; i < str.length; i++) h = str.charCodeAt(i) + ((h << 5) - h); return Math.abs(h) % len; };
                                const username = document.querySelector('.username')?.textContent?.replace('@', '').trim() || '';
                                const initials = (() => {
                                    const fn = (nombre || '').trim();
                                    const ln = (apellido || '').trim();
                                    if (fn && ln) return (fn[0] + ln[0]).toUpperCase();
                                    return (username[0] || '?').toUpperCase();
                                })();
                                const bgColor = avatarColors[getIdx(username, avatarColors.length)];

                                if (isAvatarRemoved) {
                                    // Quitar foto -> mostrar div con iniciales
                                    const oldEl = document.getElementById('profile-avatar');
                                    if (oldEl) {
                                        const div = document.createElement('div');
                                        div.id = 'profile-avatar';
                                        div.className = 'profile-initials-avatar';
                                        div.setAttribute('data-username', username);
                                        div.style.cssText = `width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:800;color:white;background:${bgColor};letter-spacing:0.02em;`;
                                        div.textContent = initials;
                                        oldEl.replaceWith(div);
                                    }
                                    const topbarAv = document.querySelector('.topbar-avatar');
                                    if (topbarAv) {
                                        topbarAv.innerHTML = `<div class="auto-avatar" data-name="${username}" style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:0.9rem;font-weight:800;color:white;background:${bgColor};">${initials}</div>`;
                                    }
                                } else if (croppedAvatarBlob || data.avatar_url) {
                                    // Subir foto nueva -> mostrar img confirmada por backend
                                    const previewEl = document.getElementById('photo-preview-img');
                                    const verifiedUrl = data.avatar_url ? (data.avatar_url + '?t=' + Date.now()) : '';
                                    const newSrc = verifiedUrl || (previewEl && previewEl.tagName === 'IMG' ? previewEl.src : '');
                                    const oldEl = document.getElementById('profile-avatar');
                                    if (oldEl && oldEl.tagName === 'IMG') {
                                        oldEl.src = newSrc;
                                    } else if (oldEl) {
                                        const img = document.createElement('img');
                                        img.src = newSrc;
                                        img.alt = 'Usuario';
                                        img.id = 'profile-avatar';
                                        img.style.cssText = 'width:100%;height:100%;object-fit:cover;display:block;';
                                        oldEl.replaceWith(img);
                                    }
                                    const topbarAv = document.querySelector('.topbar-avatar');
                                    if (topbarAv) {
                                        let topbarImg = topbarAv.querySelector('img');
                                        if (!topbarImg) {
                                            topbarImg = document.createElement('img');
                                            topbarImg.style.cssText = 'width:100%;height:100%;object-fit:cover;';
                                            topbarImg.alt = 'Avatar';
                                            topbarAv.innerHTML = '';
                                            topbarAv.appendChild(topbarImg);
                                        }
                                        topbarImg.src = newSrc;
                                    }
                                }
                            }

                            if (modal) modal.classList.remove('active');
                            selectedPhotoFile = null;
                            croppedAvatarBlob = null;
                            isAvatarRemoved = false;
                            showToast(data.message, 'success');
                        } else {
                            showToast(data.error, 'error');
                        }
                    })
                    .catch((err) => {
                        showToast('Error de conexión', 'error');
                    })
                    .finally(() => {
                        btnSaveModal.classList.remove('btn-loading');
                    });
            };

            if (croppedAvatarBlob) {
                formData.append('avatar', croppedAvatarBlob, 'avatar.jpg');
                submitProfileData();
            } else {
                if (isAvatarRemoved) {
                    formData.append('remove_avatar', 'true');
                }
                submitProfileData();
            }
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
            if (cardInfo) cardInfo.classList.add('edit-mode');
            if (btnEditCard) btnEditCard.style.display = 'none';
            if (editButtons) editButtons.classList.add('active');
            document.querySelectorAll('.empty-msg').forEach(msg => msg.style.display = 'none');
        } else {
            if (cardInfo) cardInfo.classList.remove('edit-mode');
            if (btnEditCard) btnEditCard.style.display = 'inline-flex';
            if (editButtons) editButtons.classList.remove('active');
            document.querySelectorAll('.editing').forEach(el => el.classList.remove('editing'));
            if (editSobreMi) editSobreMi.classList.remove('active');
            if (displaySobreMi) displaySobreMi.style.display = 'block';

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
                if (displaySobreMi) displaySobreMi.style.display = 'none';
                if (editSobreMi) editSobreMi.classList.add('active');

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
                if (inp) {
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
            if (container) {
                const sug = getNextTecnologiaSugerencia();
                const nt = createNewTag(sug, 20, true);
                container.insertBefore(nt, this);
                nt.classList.add('editing');
                const inp = nt.querySelector('.tag-input');
                if (inp) {
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
        const cards = document.querySelectorAll('.project-card-full, .project-showcase-card');
        let visibleCount = 0;

        cards.forEach(card => {
            const titleEl = card.querySelector('h2, h3, h4');
            const name = (card.dataset.name || (titleEl ? titleEl.textContent : '')).toLowerCase();
            const theme = card.dataset.theme;
            const tech = card.dataset.tech;
            let show = true;

            if (currentFilters.search && !name.includes(currentFilters.search)) show = false;
            if (theme && currentFilters.theme !== 'all' && theme !== currentFilters.theme) show = false;
            if (tech && currentFilters.tech !== 'all' && (!tech || !tech.includes(currentFilters.tech))) show = false;

            card.style.display = show ? 'flex' : 'none';
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
        const cards = Array.from(projectsGrid.querySelectorAll('.project-card-full, .project-showcase-card'));

        cards.sort((a, b) => {
            const titleA = (a.dataset.name || a.querySelector('h2, h3, h4')?.textContent || '').trim().toLowerCase();
            const titleB = (b.dataset.name || b.querySelector('h2, h3, h4')?.textContent || '').trim().toLowerCase();
            switch (currentFilters.sort) {
                case 'recent': return new Date(b.dataset.date || 0) - new Date(a.dataset.date || 0);
                case 'oldest': return new Date(a.dataset.date || 0) - new Date(b.dataset.date || 0);
                case 'az': return titleA.localeCompare(titleB);
                case 'za': return titleB.localeCompare(titleA);
                case 'views': return parseInt(b.dataset.views || 0) - parseInt(a.dataset.views || 0);
                case 'collaborators': return parseInt(b.dataset.collaborators || 0) - parseInt(a.dataset.collaborators || 0);
                default: return 0;
            }
        });

        cards.forEach(card => projectsGrid.appendChild(card));
    }

    function updateProjectCount() {
        const allCards = document.querySelectorAll('.project-card-full, .project-showcase-card');
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

    // ============================================
    // MODAL NUEVO PROYECTO (DISEÑO FIGMA / ANTI-SPAM)
    // ============================================
    const modalNewProject = document.getElementById('modal-real-new-project') || document.getElementById('modal-new-project');
    const btnNewProjectTrigger = document.getElementById('btn-new-project-trigger') || document.getElementById('btn-new-project');
    const btnCloseNew = document.getElementById('btn-close-real-new') || document.getElementById('btn-close-new-project');
    const btnCancelNew = document.getElementById('btn-cancel-real-new') || document.getElementById('btn-cancel-new-project');
    const formNewProject = document.getElementById('form-real-new') || document.getElementById('form-new-project');

    if (btnNewProjectTrigger && modalNewProject) {
        btnNewProjectTrigger.addEventListener('click', () => {
            modalNewProject.classList.add('active');
        });

        const closeMod = () => {
            modalNewProject.classList.remove('active');
            if (formNewProject) formNewProject.reset();
            resetImagePreview();
        };

        if (btnCloseNew) btnCloseNew.addEventListener('click', closeMod);
        if (btnCancelNew) btnCancelNew.addEventListener('click', closeMod);
    }

    // Contador del Textarea Resumen
    const newSummaryInput = document.getElementById('new-summary');
    if (newSummaryInput) {
        newSummaryInput.addEventListener('input', function () {
            const countLabel = document.getElementById('new-summary-counter');
            if (countLabel) countLabel.textContent = `${this.value.length}/150`;
        });
    }

    // Preview de la Portada
    const dropArea = document.getElementById('new-image-drop-area');
    const fileInput = document.getElementById('new-image');
    const previewContainer = document.getElementById('new-image-preview-container');
    const previewImg = document.getElementById('new-image-preview-img');
    const btnRemoveImg = document.getElementById('btn-remove-new-image');

    function resetImagePreview() {
        if (fileInput) fileInput.value = '';
        if (previewContainer) previewContainer.style.display = 'none';
        if (dropArea) dropArea.style.display = 'block';
    }

    if (dropArea && fileInput) {
        dropArea.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    if (previewImg) previewImg.src = e.target.result;
                    dropArea.style.display = 'none';
                    previewContainer.style.display = 'block';
                }
                reader.readAsDataURL(this.files[0]);
            }
        });

        if (btnRemoveImg) {
            btnRemoveImg.addEventListener('click', resetImagePreview);
        }
    }

    // Petición a Django con Fetch y FormData
    if (formNewProject) {
        formNewProject.addEventListener('submit', function (e) {
            e.preventDefault();
            const btnSubmit = document.getElementById('btn-submit-new-project');
            const originalText = btnSubmit.textContent;

            btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
            btnSubmit.disabled = true;
            btnSubmit.style.opacity = '0.7';

            const formData = new FormData(this);

            fetch('/projects/api/projects/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRFToken() },
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        showToast(data.message, 'success');
                        // Refrescamos la página tras un segundo para que la nueva tarjeta
                        // se renderice perfectamente con todos los datos y la imagen de Django.
                        setTimeout(() => {
                            window.location.reload();
                        }, 1200);
                    } else {
                        showToast(data.message || 'Error de validación', 'error');
                        btnSubmit.innerHTML = originalText;
                        btnSubmit.disabled = false;
                        btnSubmit.style.opacity = '1';
                    }
                })
                .catch(err => {
                    showToast('Error de conexión con el servidor', 'error');
                    btnSubmit.innerHTML = originalText;
                    btnSubmit.disabled = false;
                    btnSubmit.style.opacity = '1';
                });
        });
    }

    // ============================================
    // MANEJO DE EVENTOS GLOBALES DE CIERRE
    // ============================================
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => {
                modal.classList.remove('active');
                if (modal.id === 'modal-new-project' && formNewProject) { formNewProject.reset(); resetImagePreview(); }
            });
            currentEditingProject = null;
        }
    });

    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function (e) {
            if (e.target === this) {
                this.classList.remove('active');
                if (this.id === 'modal-new-project' && formNewProject) { formNewProject.reset(); resetImagePreview(); }
                currentEditingProject = null;
            }
        });
    });

    const dynamicWordEl = document.getElementById('dynamicWord');
    if (dynamicWordEl) {
        const words = ['Construye', 'Transforma', 'Impulsa', 'Desarrolla'];
        let wordIdx = 0;
        const animationDuration = 250;

        setInterval(() => {
            dynamicWordEl.classList.remove('slide-in');
            dynamicWordEl.classList.add('slide-out');

            setTimeout(() => {
                wordIdx = (wordIdx + 1) % words.length;
                dynamicWordEl.textContent = words[wordIdx];
                dynamicWordEl.classList.remove('slide-out');
                dynamicWordEl.classList.add('slide-in');
            }, animationDuration);
        }, 2600);
    }

    if (document.getElementById('project-count')) {
        updateProjectCount();
    }

    function initCollabPredictive(inputId, pillsAreaId, hiddenInputId, dropdownId) {
        const input = document.getElementById(inputId);
        const pillsArea = document.getElementById(pillsAreaId);
        const hiddenInput = document.getElementById(hiddenInputId);
        const dropdown = document.getElementById(dropdownId);
        
        if (!input || !pillsArea || !hiddenInput || !dropdown) return;

        let usersList = [];
        try {
            const rawUsers = document.getElementById('all_users_data')?.textContent;
            if(rawUsers) usersList = JSON.parse(rawUsers);
        } catch(e) {
            console.error("Error cargando usuarios:", e);
        }

        let selectedUsers = []; 

        function renderPills() {
            pillsArea.innerHTML = '';
            selectedUsers.forEach(user => {
                const pill = document.createElement('div');
                pill.className = 'pill-item collab-pill';
                pill.innerHTML = `@${user} <span data-user="${user}" style="cursor:pointer; color:red;">&times;</span>`;
                pillsArea.appendChild(pill);
            });
            hiddenInput.value = selectedUsers.join(',');
        }

        pillsArea.addEventListener('click', function(e) {
            if (e.target.tagName === 'SPAN') {
                const userToRemove = e.target.getAttribute('data-user');
                selectedUsers = selectedUsers.filter(u => u !== userToRemove);
                renderPills();
            }
        });

        input.addEventListener('input', function() {
            const val = this.value.toLowerCase().trim();
            dropdown.innerHTML = ''; 
            
            if (val.length > 0) {
                // Filtrar usuarios que coincidan y que no estén ya seleccionados
                const matches = usersList.filter(u => u.toLowerCase().includes(val) && !selectedUsers.includes(u));
                
                if (matches.length > 0) {
                    // Mostrar máximo 5 resultados sugeridos
                    matches.slice(0, 5).forEach(match => {
                        const div = document.createElement('div');
                        div.className = 'predictive-item';
                        div.textContent = `@${match}`;
                        
                        // Si hace clic en la sugerencia, agregarlo
                        div.addEventListener('click', function() {
                            selectedUsers.push(match);
                            input.value = ''; 
                            dropdown.style.display = 'none'; 
                            renderPills(); 
                        });
                        dropdown.appendChild(div);
                    });
                    dropdown.style.display = 'block';
                } else {
                    dropdown.style.display = 'none';
                }
            } else {
                dropdown.style.display = 'none';
            }
        });

        document.addEventListener('click', function(e) {
            if (!input.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    }

    initCollabPredictive(
        'input-new-collab',       
        'new-collab-pills',      
        'hidden-new-collaborators', 
        'new-collab-dropdown'    
    );

});