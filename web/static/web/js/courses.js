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
        toast.style.zIndex = '99999';
        toast.style.transition = 'opacity 0.3s ease';
        toast.style.fontWeight = '600';
        toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i> ${message}`;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // ====================================================
    // MODAL CREAR CURSO
    // ====================================================
    const btnTriggerNewCourse = document.getElementById('btn-new-course-trigger');
    const modalNewCourse = document.getElementById('modal-new-course');
    const btnCloseNewCourse = document.getElementById('btn-close-new-course');
    const btnCancelNewCourse = document.getElementById('btn-cancel-new-course');
    const formNewCourse = document.getElementById('form-new-course');

    if (btnTriggerNewCourse && modalNewCourse) {
        btnTriggerNewCourse.addEventListener('click', function () {
            modalNewCourse.style.display = 'flex';
        });
    }

    function closeNewCourseModal() {
        if (modalNewCourse) modalNewCourse.style.display = 'none';
    }

    if (btnCloseNewCourse) btnCloseNewCourse.addEventListener('click', closeNewCourseModal);
    if (btnCancelNewCourse) btnCancelNewCourse.addEventListener('click', closeNewCourseModal);

    // Previsualización de imagen para el nuevo curso
    const courseDropArea = document.getElementById('course-drop-area');
    const courseFileInput = document.getElementById('course-file-input');
    const coursePreviewContainer = document.getElementById('course-preview-container');
    const coursePreviewImg = document.getElementById('course-preview-img');
    const courseBtnRemoveImg = document.getElementById('course-btn-remove-img');

    if (courseDropArea && courseFileInput) {
        courseDropArea.addEventListener('click', () => courseFileInput.click());
        courseFileInput.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    if (coursePreviewImg) coursePreviewImg.src = e.target.result;
                    if (coursePreviewContainer) coursePreviewContainer.style.display = 'block';
                    if (courseDropArea) courseDropArea.style.display = 'none';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    if (courseBtnRemoveImg) {
        courseBtnRemoveImg.addEventListener('click', function (e) {
            e.stopPropagation();
            if (courseFileInput) courseFileInput.value = '';
            if (coursePreviewImg) coursePreviewImg.src = '';
            if (coursePreviewContainer) coursePreviewContainer.style.display = 'none';
            if (courseDropArea) courseDropArea.style.display = 'block';
        });
    }

    // Tag Input para Crear Curso
    const inputCourseTag = document.getElementById('input-course-tag');
    const pillsCourseTag = document.getElementById('pills-course-tag');
    const hiddenCourseTags = document.getElementById('hidden-course-tags');
    let courseTagsList = [];

    function renderCourseTags() {
        if (!pillsCourseTag) return;
        pillsCourseTag.innerHTML = '';
        courseTagsList.forEach((tag, index) => {
            const pill = document.createElement('span');
            pill.style.cssText = 'background: var(--primary-orange, #f97316); color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; display: inline-flex; align-items: center; gap: 6px;';
            pill.innerHTML = `#${tag} <i class="fas fa-times" style="cursor:pointer;" data-index="${index}"></i>`;
            pill.querySelector('i').addEventListener('click', function () {
                courseTagsList.splice(index, 1);
                renderCourseTags();
            });
            pillsCourseTag.appendChild(pill);
        });
        if (hiddenCourseTags) hiddenCourseTags.value = courseTagsList.join(',');
    }

    if (inputCourseTag) {
        inputCourseTag.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                const val = this.value.trim().replace(/^#/, '');
                if (val && !courseTagsList.includes(val)) {
                    courseTagsList.push(val);
                    renderCourseTags();
                }
                this.value = '';
            }
        });
    }

    // Submit Crear Curso
    if (formNewCourse) {
        formNewCourse.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(formNewCourse);
            if (hiddenCourseTags) formData.set('tags', hiddenCourseTags.value);

            fetch('/courses/api/courses/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message || 'Curso creado con éxito.');
                    closeNewCourseModal();
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    showToast(data.message || 'Error al crear el curso.', 'error');
                }
            })
            .catch(() => {
                showToast('Error de red o servidor.', 'error');
            });
        });
    }

    // ====================================================
    // MODAL EDITAR CURSO (Detalle de Curso)
    // ====================================================
    const btnTriggerEditCourse = document.getElementById('btn-edit-course-trigger');
    const modalEditCourse = document.getElementById('modal-edit-course');
    const btnCloseEditCourse = document.getElementById('btn-close-edit-course');
    const btnCancelEditCourse = document.getElementById('btn-cancel-edit-course');
    const formEditCourse = document.getElementById('form-edit-course');

    if (btnTriggerEditCourse && modalEditCourse) {
        btnTriggerEditCourse.addEventListener('click', function () {
            modalEditCourse.style.display = 'flex';
        });
    }

    function closeEditCourseModal() {
        if (modalEditCourse) modalEditCourse.style.display = 'none';
    }

    if (btnCloseEditCourse) btnCloseEditCourse.addEventListener('click', closeEditCourseModal);
    if (btnCancelEditCourse) btnCancelEditCourse.addEventListener('click', closeEditCourseModal);

    // Previsualización de imagen para editar curso
    const editCourseDropArea = document.getElementById('edit-course-drop-area');
    const editCourseFileInput = document.getElementById('edit-course-file-input');
    const editCoursePreviewContainer = document.getElementById('edit-course-preview-container');
    const editCoursePreviewImg = document.getElementById('edit-course-preview-img');
    const editCourseBtnRemoveImg = document.getElementById('edit-course-btn-remove-img');

    if (editCourseDropArea && editCourseFileInput) {
        editCourseDropArea.addEventListener('click', () => editCourseFileInput.click());
        editCourseFileInput.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    if (editCoursePreviewImg) editCoursePreviewImg.src = e.target.result;
                    if (editCoursePreviewContainer) editCoursePreviewContainer.style.display = 'block';
                    if (editCourseDropArea) editCourseDropArea.style.display = 'none';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    if (editCourseBtnRemoveImg) {
        editCourseBtnRemoveImg.addEventListener('click', function (e) {
            e.stopPropagation();
            if (editCourseFileInput) editCourseFileInput.value = '';
            if (editCoursePreviewImg) editCoursePreviewImg.src = '';
            if (editCoursePreviewContainer) editCoursePreviewContainer.style.display = 'none';
            if (editCourseDropArea) editCourseDropArea.style.display = 'block';
        });
    }

    // Submit Editar Curso
    if (formEditCourse) {
        formEditCourse.addEventListener('submit', function (e) {
            e.preventDefault();
            const courseId = formEditCourse.getAttribute('data-course-id');
            const formData = new FormData(formEditCourse);

            fetch(`/courses/api/courses/${courseId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message || 'Curso actualizado correctamente.');
                    closeEditCourseModal();
                    setTimeout(() => {
                        if (data.data && data.data.slug) {
                            window.location.href = `/courses/${data.data.slug}/`;
                        } else {
                            window.location.reload();
                        }
                    }, 1000);
                } else {
                    showToast(data.message || 'Error al actualizar el curso.', 'error');
                }
            })
            .catch(() => {
                showToast('Error de red o servidor.', 'error');
            });
        });
    }
});
