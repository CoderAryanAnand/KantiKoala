// Global state
let semesterTemplates = [];
let currentSubjectIdForGrade = null;
let currentGradeIdForEdit = null;
let currentSubjectIdForDreamCalc = null;
let semesterIdToDelete = null;
let subjectIdToDelete = null;
let gradeIdToDelete = null;

// Global state for popup editing (must be declared before functions that use them)
let editingSubjectId = null;
let editingSemesterId = null;
let currentSubjectIdForGradeDelete = null;

// DOM Elements
const overlay = document.getElementById("overlay");

// --- Initialization ---
document.addEventListener("DOMContentLoaded", async function() {
    await loadConstants();
    await loadSemesters();
    setupGlobalEventHandlers();
});

async function loadConstants() {
    try {
        const response = await fetch("/api/noten/constants");
        if (response.ok) {
            const data = await response.json();
            semesterTemplates = data.templates || [];
            populateTemplateSelect();
        }
    } catch (error) {
        console.error("Failed to load constants:", error);
    }
}

function populateTemplateSelect() {
    const select = document.getElementById("semesterTemplateSelect");
    if (!select) return;
    
    // Clear existing options except the first "no template" option
    while (select.options.length > 1) {
        select.remove(1);
    }
    
    // Add template options
    semesterTemplates.forEach(template => {
        const option = document.createElement("option");
        option.value = template.id;
        option.textContent = `${template.name} (${template.subjects.length} Fächer)`;
        select.appendChild(option);
    });
}

async function loadSemesters() {
    try {
        const response = await fetch("/api/noten/");
        if (response.ok) {
            const semesters = await response.json();
            const container = document.getElementById("semesters");
            container.innerHTML = "";
            semesters.forEach(sem => renderSemester(sem));
        }
    } catch (error) {
        console.error("Failed to load semesters:", error);
    }
}

// --- Rendering ---

function renderSemester(sem) {
    const container = document.getElementById("semesters");
    const semesterDiv = document.createElement("div");
    semesterDiv.className = "semester bg-white dark:bg-zinc-800 rounded-xl shadow-md border border-zinc-200 dark:border-zinc-700 mb-6";
    semesterDiv.dataset.id = sem.id;
    semesterDiv.id = `semester-${sem.id}`;

    // Current badge HTML
    const currentBadge = sem.is_current 
        ? `<span class="current-badge inline-flex items-center px-3 py-1 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">Aktuell</span>` 
        : '';

    const header = document.createElement("div");
    header.className = "dropdown-header flex items-center justify-between p-4 cursor-pointer";
    header.innerHTML = `
        <div class="flex items-center space-x-4 flex-wrap gap-2">
            <span class="semester-name font-bold text-xl text-zinc-900 dark:text-white">${sem.name}</span>
            ${currentBadge}
            <span class="semester-average text-sm font-medium text-green-600 dark:text-zinc-300" id="sem-avg-${sem.id}">
                Schnitt: ${sem.average.toFixed(2)} | Pluspunkte: ${sem.plus_points.toFixed(1)}
            </span>
        </div>
        <div class="flex items-center space-x-2">
            <button class="rename-semester-btn p-2 text-zinc-500 hover:text-blue-600 dark:hover:text-blue-400 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-700" title="Umbenennen">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z"></path></svg>
            </button>
            <button class="set-current-btn p-2 text-zinc-500 hover:text-green-600 dark:hover:text-green-400 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-700 ${sem.is_current ? 'hidden' : ''}" title="Als aktuell festlegen">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            </button>
            <svg class="chevron w-6 h-6 text-zinc-500 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
        </div>
    `;

    const content = document.createElement("div");
    content.className = "dropdown-content hidden p-4 border-t border-zinc-200 dark:border-zinc-700";
    
    const subjectsContainer = document.createElement("div");
    subjectsContainer.className = "subjects-container space-y-4";
    subjectsContainer.id = `subjects-container-${sem.id}`;
    
    sem.subjects.forEach(subject => {
        subjectsContainer.appendChild(renderSubject(subject));
    });

    const actionsDiv = document.createElement("div");
    actionsDiv.className = "flex gap-2 mt-4 flex-wrap";
    actionsDiv.innerHTML = `
        <button class="add-subject-btn px-3 py-2 text-sm font-semibold text-white bg-blue-600 rounded-md hover:bg-blue-700">Fach hinzufügen</button>
        <button class="delete-semester-btn px-3 py-2 text-sm font-semibold text-white bg-red-600 rounded-md hover:bg-red-700">Semester löschen</button>
    `;

    content.appendChild(subjectsContainer);
    content.appendChild(actionsDiv);
    semesterDiv.appendChild(header);
    semesterDiv.appendChild(content);
    container.appendChild(semesterDiv);

    // Event Listeners
    header.onclick = (e) => {
        if (!e.target.closest('button')) {
            content.classList.toggle("hidden");
            header.querySelector('.chevron').classList.toggle("rotate-180");
        }
    };

    header.querySelector('.rename-semester-btn').onclick = (e) => {
        e.stopPropagation();
        openSemesterRenamePopup(sem.id, sem.name);
    };

    const setCurrentBtn = header.querySelector('.set-current-btn');
    if (setCurrentBtn) {
        setCurrentBtn.onclick = (e) => {
            e.stopPropagation();
            setCurrentSemester(sem.id);
        };
    }

    actionsDiv.querySelector('.add-subject-btn').onclick = () => addSubjectPrompt(sem.id);
    actionsDiv.querySelector('.delete-semester-btn').onclick = () => openDeleteConfirm(sem.id, sem.name);

    // SortableJS
    if (typeof Sortable !== "undefined") {
        new Sortable(subjectsContainer, {
            animation: 150,
            handle: '.drag-handle',
            onEnd: function (evt) {
                // Save the new order to the server
                saveSubjectOrder(sem.id, subjectsContainer);
            }
        });
    }
}

function renderSubject(subject) {
    const subjectDiv = document.createElement("div");
    subjectDiv.className = "subject bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-lg";
    subjectDiv.dataset.id = subject.id;
    subjectDiv.dataset.countsAverage = subject.counts_average ? "true" : "false";
    subjectDiv.id = `subject-${subject.id}`;

    const avgText = subject.has_grades && subject.average !== null ? subject.average.toFixed(2) : "0";
    const countsText = subject.counts_average ? "" : " (zählt nicht)";

    const header = document.createElement("div");
    header.className = "dropdown-header flex items-center justify-between p-4 cursor-pointer";
    header.innerHTML = `
        <div class="flex items-center space-x-3">
            <span class="subject-title font-semibold text-lg text-zinc-800 dark:text-white">${subject.name}</span>
            <span class="subject-average text-sm text-zinc-500 dark:text-zinc-400" id="subj-avg-${subject.id}">
                Schnitt: ${avgText}${countsText}
            </span>
        </div>
        <div class="flex items-center space-x-2">
            <button class="edit-subject-btn p-1.5 text-zinc-500 hover:text-blue-600 dark:hover:text-blue-400 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-700">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z"></path></svg>
            </button>
            <svg class="chevron w-5 h-5 text-zinc-500 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            <span class="drag-handle cursor-grab active:cursor-grabbing ml-2 p-1 rounded text-zinc-500 hover:text-blue-600 dark:text-zinc-400 dark:hover:text-blue-400 hover:bg-zinc-100 dark:hover:bg-zinc-700">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 10h16M4 14h16"></path></svg>
            </span>
        </div>
    `;

    const content = document.createElement("div");
    content.className = "dropdown-content hidden p-4 border-t border-zinc-200 dark:border-zinc-700";
    
    const gradesList = document.createElement("div");
    gradesList.className = "grades-list space-y-2";
    gradesList.id = `grades-list-${subject.id}`;
    
    subject.grades.forEach(grade => {
        gradesList.appendChild(renderGradeRow(grade, subject.id));
    });

    const actionsDiv = document.createElement("div");
    actionsDiv.className = "flex flex-wrap gap-2 mt-4";
    actionsDiv.innerHTML = `
        <button class="add-grade-btn text-sm px-3 py-2 font-semibold text-white bg-blue-600 rounded-md hover:bg-blue-700">Note hinzufügen</button>
        <button class="dream-calc-btn text-sm px-3 py-2 font-semibold text-white bg-green-600 rounded-md hover:bg-green-700">Wunschnote</button>
        <button class="delete-subject-btn text-sm px-3 py-2 font-semibold text-white bg-red-600 rounded-md hover:bg-red-700">Fach löschen</button>
    `;

    content.appendChild(gradesList);
    content.appendChild(actionsDiv);
    subjectDiv.appendChild(header);
    subjectDiv.appendChild(content);

    // Event Listeners
    header.onclick = (e) => {
        if (!e.target.closest('button') && !e.target.classList.contains('drag-handle')) {
            content.classList.toggle("hidden");
            header.querySelector('.chevron').classList.toggle("rotate-180");
        }
    };

    header.querySelector('.edit-subject-btn').onclick = (e) => {
        e.stopPropagation();
        openSubjectPopup(subject.id, subject.name, subject.counts_average);
    };

    actionsDiv.querySelector('.add-grade-btn').onclick = () => openGradePopup(subject.id);
    actionsDiv.querySelector('.dream-calc-btn').onclick = () => openDreamCalcPopup(subject.id, subject.name);
    actionsDiv.querySelector('.delete-subject-btn').onclick = () => openDeleteSubjectConfirm(subject.id, subject.name);

    return subjectDiv;
}

function renderGradeRow(grade, subjectId) {
    const row = document.createElement("div");
    row.className = "grade-row grid grid-cols-[1fr_auto_auto_auto] items-center gap-x-4 p-2 rounded-md bg-zinc-50 dark:bg-zinc-700/50";
    row.id = `grade-${grade.id}`;
    
    const countsText = grade.counts ? "" : " (Zählt nicht)";
    
    row.innerHTML = `
        <div class="truncate">
            <strong class="text-zinc-800 dark:text-white">${grade.name}</strong>
        </div>
        <div class="text-sm text-zinc-700 dark:text-zinc-300">Note: ${grade.value}</div>
        <div class="text-sm text-zinc-700 dark:text-zinc-300">Gewichtung: ${grade.weight}${countsText}</div>
        <div class="flex space-x-1 justify-end">
            <button class="edit-grade-btn p-1.5 text-zinc-500 hover:text-blue-600 dark:hover:text-blue-400 rounded-md hover:bg-zinc-200 dark:hover:bg-zinc-600">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z"></path></svg>
            </button>
            <button class="delete-grade-btn p-1.5 text-zinc-500 hover:text-red-600 dark:hover:text-red-400 rounded-md hover:bg-zinc-200 dark:hover:bg-zinc-600">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
            </button>
        </div>
    `;

    row.querySelector('.edit-grade-btn').onclick = () => openGradePopup(subjectId, grade);
    row.querySelector('.delete-grade-btn').onclick = () => openDeleteGradeConfirm(grade.id, grade.name);

    return row;
}

// --- Semester Create Popup ---

function openSemesterCreatePopup() {
    document.getElementById("semesterNameInput").value = "";
    document.getElementById("semesterTemplateSelect").value = "";
    document.getElementById("semesterSetAsCurrent").checked = false;
    overlay.classList.remove("hidden");
    document.getElementById("semester-create-popup").classList.remove("hidden");
    document.getElementById("semesterNameInput").focus();
}

function closeSemesterCreatePopup() {
    overlay.classList.add("hidden");
    document.getElementById("semester-create-popup").classList.add("hidden");
}

async function saveSemesterCreate() {
    const name = document.getElementById("semesterNameInput").value.trim();
    const templateSelect = document.getElementById("semesterTemplateSelect");
    const templateId = templateSelect.value ? parseInt(templateSelect.value) : null;
    const setAsCurrent = document.getElementById("semesterSetAsCurrent").checked;
    
    if (!name) {
        alert("Bitte geben Sie einen Semesternamen ein.");
        return;
    }
    
    try {
        const payload = { 
            name: name, 
            set_as_current: setAsCurrent 
        };
        if (templateId !== null) {
            payload.template_id = templateId;
        }
        
        const response = await fetch("/api/noten/semester", {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            const sem = await response.json();
            closeSemesterCreatePopup();
            
            // Render the new semester
            renderSemester(sem);
            
            // If set as current, update badges selectively instead of reloading all
            if (setAsCurrent) {
                updateCurrentSemesterBadges(sem.id);
            }
        } else {
            const error = await response.json();
            alert(error.error || "Fehler beim Erstellen des Semesters");
        }
    } catch (error) {
        console.error("Error creating semester:", error);
    }
}

async function setCurrentSemester(semesterId) {
    try {
        const response = await fetch(`/api/noten/semester/${semesterId}/set-current`, {
            method: "POST",
            headers: getHeaders()
        });
        if (response.ok) {
            // Update badges in DOM without reloading all semesters
            updateCurrentSemesterBadges(semesterId);
        } else {
            const error = await response.json();
            alert(error.error || "Fehler beim Festlegen des aktuellen Semesters");
        }
    } catch (error) {
        console.error("Error setting current semester:", error);
    }
}

// --- API Actions ---

async function addSubjectPrompt(semesterId) {
    const name = prompt("Fachname eingeben:");
    if (!name) return;

    try {
        const response = await fetch(`/api/noten/semester/${semesterId}/subject`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ name: name, counts_average: name.toLowerCase() !== 'sport' })
        });
        if (response.ok) {
            const data = await response.json();
            // Append new subject
            const container = document.getElementById(`subjects-container-${semesterId}`);
            container.appendChild(renderSubject(data));
            // Update semester stats
            updateSemesterStats(semesterId, data.semester_stats);
        }
    } catch (error) {
        console.error("Error creating subject:", error);
    }
}

async function saveOrUpdateGrade() {
    const name = document.getElementById("gradeName").value.trim();
    const value = parseFloat(document.getElementById("gradeValue").value);
    const weight = parseFloat(document.getElementById("gradeWeight").value);
    const counts = document.getElementById("gradeCounts").checked;

    if (!name || isNaN(value) || isNaN(weight)) {
        alert("Bitte alle Felder korrekt ausfüllen.");
        return;
    }

    const payload = { name, value, weight, counts };
    
    try {
        let response;
        if (currentGradeIdForEdit) {
            // Update
            response = await fetch(`/api/noten/grade/${currentGradeIdForEdit}`, {
                method: "PUT",
                headers: getHeaders(),
                body: JSON.stringify(payload)
            });
        } else {
            // Create
            response = await fetch(`/api/noten/subject/${currentSubjectIdForGrade}/grade`, {
                method: "POST",
                headers: getHeaders(),
                body: JSON.stringify(payload)
            });
        }

        if (response.ok) {
            const data = await response.json();
            // Update UI
            if (currentGradeIdForEdit) {
                // Replace existing row
                const oldRow = document.getElementById(`grade-${data.id}`);
                const newRow = renderGradeRow(data, currentSubjectIdForGrade); 
                oldRow.replaceWith(newRow);
            } else {
                // Append new row
                const list = document.getElementById(`grades-list-${currentSubjectIdForGrade}`);
                list.appendChild(renderGradeRow(data, currentSubjectIdForGrade));
            }
            
            const subjectId = currentSubjectIdForGrade; 
            
            const avgSpan = document.getElementById(`subj-avg-${subjectId}`);
            if (avgSpan) {
                // Use data attribute to determine if subject counts towards average
                const subjectDiv = document.getElementById(`subject-${subjectId}`);
                const isCounting = subjectDiv && subjectDiv.dataset.countsAverage === "true";
                avgSpan.textContent = `Schnitt: ${data.subject_average !== null ? data.subject_average.toFixed(2) : 0}${isCounting ? '' : ' (zählt nicht)'}`;
            }

            // Update semester stats
            const subjectDiv = document.getElementById(`subject-${subjectId}`);
            const semesterDiv = subjectDiv.closest('.semester');
            if (semesterDiv) {
                updateSemesterStats(semesterDiv.dataset.id, data.semester_stats);
            }

            closeGradePopup();
        }
    } catch (error) {
        console.error("Error saving grade:", error);
    }
}

async function saveSubjectEdit() {
    const name = document.getElementById("subjectNameEdit").value.trim();
    const countsAverage = document.getElementById("subjectCountsAverage").checked;
    const subjectId = editingSubjectId; 

    if (!name) return;

    try {
        const response = await fetch(`/api/noten/subject/${subjectId}`, {
            method: "PUT",
            headers: getHeaders(),
            body: JSON.stringify({ name, counts_average: countsAverage })
        });

        if (response.ok) {
            const data = await response.json();
            // Update DOM
            const subjectDiv = document.getElementById(`subject-${subjectId}`);
            subjectDiv.querySelector('.subject-title').textContent = data.name;
            
            // Update data attribute for counts_average
            subjectDiv.dataset.countsAverage = data.counts_average ? "true" : "false";
            
            const avgSpan = document.getElementById(`subj-avg-${subjectId}`);
            const avgText = data.average !== null ? data.average.toFixed(2) : "0";
            avgSpan.textContent = `Schnitt: ${avgText}${data.counts_average ? '' : ' (zählt nicht)'}`;
            
            // Update semester stats
            const semesterDiv = subjectDiv.closest('.semester');
            updateSemesterStats(semesterDiv.dataset.id, data.semester_stats);
            
            closeSubjectPopup();
        }
    } catch (error) {
        console.error("Error updating subject:", error);
    }
}

async function saveSemesterRename() {
    const name = document.getElementById("semesterNameEdit").value.trim();
    const semesterId = editingSemesterId;

    if (!name) return;

    try {
        const response = await fetch(`/api/noten/semester/${semesterId}`, {
            method: "PUT",
            headers: getHeaders(),
            body: JSON.stringify({ name })
        });

        if (response.ok) {
            const data = await response.json();
            const semesterDiv = document.getElementById(`semester-${semesterId}`);
            semesterDiv.querySelector('.semester-name').textContent = data.name;
            closeSemesterRenamePopup();
        }
    } catch (error) {
        console.error("Error renaming semester:", error);
    }
}

async function confirmDeleteSemester() {
    if (!semesterIdToDelete) return;
    try {
        const response = await fetch(`/api/noten/semester/${semesterIdToDelete}`, {
            method: "DELETE",
            headers: getHeaders()
        });
        if (response.ok) {
            document.getElementById(`semester-${semesterIdToDelete}`).remove();
            closeDeleteConfirm();
        }
    } catch (error) {
        console.error("Error deleting semester:", error);
    }
}

async function confirmDeleteSubject() {
    if (!subjectIdToDelete) return;
    try {
        const response = await fetch(`/api/noten/subject/${subjectIdToDelete}`, {
            method: "DELETE",
            headers: getHeaders()
        });
        if (response.ok) {
            const data = await response.json();
            const subjectDiv = document.getElementById(`subject-${subjectIdToDelete}`);
            const semesterDiv = subjectDiv.closest('.semester');
            subjectDiv.remove();
            updateSemesterStats(semesterDiv.dataset.id, data.semester_stats);
            closeDeleteSubjectConfirm();
        }
    } catch (error) {
        console.error("Error deleting subject:", error);
    }
}

async function confirmDeleteGrade() {
    if (!gradeIdToDelete) return;
    try {
        const response = await fetch(`/api/noten/grade/${gradeIdToDelete}`, {
            method: "DELETE",
            headers: getHeaders()
        });
        if (response.ok) {
            const data = await response.json();
            document.getElementById(`grade-${gradeIdToDelete}`).remove();
            
            const subjectId = currentSubjectIdForGradeDelete; 
            const avgSpan = document.getElementById(`subj-avg-${subjectId}`);
            if (avgSpan) {
                 // Use data attribute to determine if subject counts towards average
                 const subjectDiv = document.getElementById(`subject-${subjectId}`);
                 const isCounting = subjectDiv && subjectDiv.dataset.countsAverage === "true";
                 avgSpan.textContent = `Schnitt: ${data.subject_average !== null ? data.subject_average.toFixed(2) : 0}${isCounting ? '' : ' (zählt nicht)'}`;
            }
            
            const subjectDiv = document.getElementById(`subject-${subjectId}`);
            const semesterDiv = subjectDiv.closest('.semester');
            updateSemesterStats(semesterDiv.dataset.id, data.semester_stats);

            closeDeleteGradeConfirm();
        }
    } catch (error) {
        console.error("Error deleting grade:", error);
    }
}

async function calculateDreamGradeFromPopup() {
    const wishedAvg = parseFloat(document.getElementById('wishedAvgInput').value);
    const nextWeight = parseFloat(document.getElementById('nextWeightInput').value);
    
    if (!currentSubjectIdForDreamCalc || isNaN(wishedAvg) || isNaN(nextWeight)) {
        return;
    }

    try {
        const response = await fetch(`/api/noten/subject/${currentSubjectIdForDreamCalc}/dream-grade`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ wished_average: wishedAvg, next_weight: nextWeight })
        });
        
        if (response.ok) {
            const data = await response.json();
            const outputP = document.getElementById('neededGradeOutput');
            if (data.message) {
                outputP.textContent = `Benötigte Note: ${data.needed_grade} (${data.message})`;
            } else {
                outputP.textContent = `Benötigte Note: ${data.needed_grade}`;
            }
        } else {
             const err = await response.json();
             document.getElementById('neededGradeOutput').textContent = `Fehler: ${err.error}`;
        }
    } catch (error) {
        console.error("Error calculating dream grade:", error);
    }
}

// --- Helpers ---

function getHeaders() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    return {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrfToken
    };
}

/**
 * Update current semester badges in DOM without reloading.
 * Removes badge from old current semester and adds to new one.
 * Also hides/shows the "set as current" button appropriately.
 */
function updateCurrentSemesterBadges(newCurrentSemesterId) {
    const semesters = document.querySelectorAll('.semester');
    
    semesters.forEach(semesterDiv => {
        const semesterId = semesterDiv.dataset.id;
        const header = semesterDiv.querySelector('.dropdown-header');
        const badgeContainer = header.querySelector('.flex.items-center.space-x-4');
        const setCurrentBtn = header.querySelector('.set-current-btn');
        let badge = badgeContainer.querySelector('.current-badge');
        
        if (String(semesterId) === String(newCurrentSemesterId)) {
            // This is the new current semester
            if (!badge) {
                // Add badge
                const newBadge = document.createElement('span');
                newBadge.className = 'current-badge inline-flex items-center px-3 py-1 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100';
                newBadge.textContent = 'Aktuell';
                // Insert after semester name
                const semesterName = badgeContainer.querySelector('.semester-name');
                semesterName.insertAdjacentElement('afterend', newBadge);
            }
            // Hide set-current button
            if (setCurrentBtn) {
                setCurrentBtn.classList.add('hidden');
            }
        } else {
            // This is not the current semester
            if (badge) {
                badge.remove();
            }
            // Show set-current button
            if (setCurrentBtn) {
                setCurrentBtn.classList.remove('hidden');
            }
        }
    });
}

function updateSemesterStats(semesterId, stats) {
    const span = document.getElementById(`sem-avg-${semesterId}`);
    if (span) {
        span.textContent = `Schnitt: ${stats.average.toFixed(2)} | Pluspunkte: ${stats.plus_points.toFixed(1)}`;
    }
}

/**
 * Save the order of subjects after drag-drop reordering.
 * @param {number} semesterId - The semester ID
 * @param {HTMLElement} container - The subjects container element
 */
async function saveSubjectOrder(semesterId, container) {
    const subjectElements = container.querySelectorAll('.subject');
    const order = Array.from(subjectElements).map(el => parseInt(el.dataset.id));
    
    try {
        const response = await fetch(`/api/noten/semester/${semesterId}/subjects/order`, {
            method: "PUT",
            headers: getHeaders(),
            body: JSON.stringify({ order: order })
        });
        
        if (!response.ok) {
            console.error("Failed to save subject order");
        }
    } catch (error) {
        console.error("Error saving subject order:", error);
    }
}

// --- Popups ---

function openGradePopup(subjectId, grade = null) {
    currentSubjectIdForGrade = subjectId;
    currentGradeIdForEdit = grade ? grade.id : null;
    
    overlay.classList.remove("hidden");
    document.getElementById("grade-popup").classList.remove("hidden");
    
    if (grade) {
        document.getElementById("grade-popup-title").textContent = "Note bearbeiten";
        document.getElementById("gradeName").value = grade.name;
        document.getElementById("gradeValue").value = grade.value;
        document.getElementById("gradeWeight").value = grade.weight;
        document.getElementById("gradeCounts").checked = grade.counts;
        document.getElementById("grade-popup-save-btn").textContent = "Speichern";
    } else {
        document.getElementById("grade-popup-title").textContent = "Note hinzufügen";
        document.getElementById("gradeName").value = "";
        document.getElementById("gradeValue").value = "";
        document.getElementById("gradeWeight").value = "1";
        document.getElementById("gradeCounts").checked = true;
        document.getElementById("grade-popup-save-btn").textContent = "Hinzufügen";
    }
}

function closeGradePopup() {
    overlay.classList.add("hidden");
    document.getElementById("grade-popup").classList.add("hidden");
}

function openSubjectPopup(subjectId, name, countsAverage) {
    editingSubjectId = subjectId;
    document.getElementById("subjectNameEdit").value = name;
    document.getElementById("subjectCountsAverage").checked = countsAverage;
    overlay.classList.remove("hidden");
    document.getElementById("subject-popup").classList.remove("hidden");
}

function closeSubjectPopup() {
    overlay.classList.add("hidden");
    document.getElementById("subject-popup").classList.add("hidden");
}

function openSemesterRenamePopup(semesterId, name) {
    editingSemesterId = semesterId;
    document.getElementById("semesterNameEdit").value = name;
    overlay.classList.remove("hidden");
    document.getElementById("semester-rename-popup").classList.remove("hidden");
}

function closeSemesterRenamePopup() {
    overlay.classList.add("hidden");
    document.getElementById("semester-rename-popup").classList.add("hidden");
}

function openDeleteConfirm(semesterId, name) {
    semesterIdToDelete = semesterId;
    document.getElementById('confirm-semester-name').textContent = `${name} löschen?`;
    overlay.classList.remove("hidden");
    document.getElementById("delete-confirm-popup").classList.remove("hidden");
}

function closeDeleteConfirm() {
    overlay.classList.add("hidden");
    document.getElementById("delete-confirm-popup").classList.add("hidden");
}

function openDeleteSubjectConfirm(subjectId, name) {
    subjectIdToDelete = subjectId;
    document.getElementById('confirm-subject-name').textContent = `${name} löschen?`;
    overlay.classList.remove("hidden");
    document.getElementById("delete-subject-confirm-popup").classList.remove("hidden");
}

function closeDeleteSubjectConfirm() {
    overlay.classList.add("hidden");
    document.getElementById("delete-subject-confirm-popup").classList.add("hidden");
}

function openDeleteGradeConfirm(gradeId, name) {
    gradeIdToDelete = gradeId;
    // Find subject ID from DOM
    const gradeRow = document.getElementById(`grade-${gradeId}`);
    const subjectDiv = gradeRow.closest('.subject');
    currentSubjectIdForGradeDelete = subjectDiv.dataset.id;

    document.getElementById('confirm-grade-name').textContent = `${name} löschen?`;
    overlay.classList.remove("hidden");
    document.getElementById("delete-grade-confirm-popup").classList.remove("hidden");
}

function closeDeleteGradeConfirm() {
    overlay.classList.add("hidden");
    document.getElementById("delete-grade-confirm-popup").classList.add("hidden");
}

function openDreamCalcPopup(subjectId, name) {
    currentSubjectIdForDreamCalc = subjectId;
    document.getElementById('dream-calc-subject-name').textContent = `Berechnen für ${name}`;
    document.getElementById('wishedAvgInput').value = '';
    document.getElementById('nextWeightInput').value = '';
    document.getElementById('neededGradeOutput').textContent = 'Benötigte Note: -';
    overlay.classList.remove("hidden");
    document.getElementById("dream-calc-popup").classList.remove("hidden");
}

function closeDreamCalcPopup() {
    overlay.classList.add("hidden");
    document.getElementById("dream-calc-popup").classList.add("hidden");
}

function setupGlobalEventHandlers() {
    // Static buttons
    const createSemesterBtn = document.getElementById("create-semester-btn");
    if (createSemesterBtn) createSemesterBtn.addEventListener("click", openSemesterCreatePopup);
    
    // Semester create popup
    const semesterCreateCancelBtn = document.getElementById("semester-create-cancel-btn");
    if (semesterCreateCancelBtn) semesterCreateCancelBtn.addEventListener("click", closeSemesterCreatePopup);
    
    const semesterCreateSaveBtn = document.getElementById("semester-create-save-btn");
    if (semesterCreateSaveBtn) semesterCreateSaveBtn.addEventListener("click", saveSemesterCreate);
    
    const gradePopupCancelBtn = document.getElementById("grade-popup-cancel-btn");
    if (gradePopupCancelBtn) gradePopupCancelBtn.addEventListener("click", closeGradePopup);
    
    const gradePopupSaveBtn = document.getElementById("grade-popup-save-btn");
    if (gradePopupSaveBtn) gradePopupSaveBtn.addEventListener("click", saveOrUpdateGrade);
    
    const subjectPopupCancelBtn = document.getElementById("subject-popup-cancel-btn");
    if (subjectPopupCancelBtn) subjectPopupCancelBtn.addEventListener("click", closeSubjectPopup);
    
    const subjectPopupSaveBtn = document.getElementById("subject-popup-save-btn");
    if (subjectPopupSaveBtn) subjectPopupSaveBtn.addEventListener("click", saveSubjectEdit);
    
    const deleteConfirmCancelBtn = document.getElementById("delete-confirm-cancel-btn");
    if (deleteConfirmCancelBtn) deleteConfirmCancelBtn.addEventListener("click", closeDeleteConfirm);
    
    const confirmDeleteBtn = document.getElementById("confirm-delete-btn");
    if (confirmDeleteBtn) confirmDeleteBtn.addEventListener("click", confirmDeleteSemester);
    
    const dreamCalcCalculateBtn = document.getElementById("dream-calc-calculate-btn");
    if (dreamCalcCalculateBtn) dreamCalcCalculateBtn.addEventListener("click", calculateDreamGradeFromPopup);
    
    const dreamCalcCloseBtn = document.getElementById("dream-calc-close-btn");
    if (dreamCalcCloseBtn) dreamCalcCloseBtn.addEventListener("click", closeDreamCalcPopup);
    
    const semesterRenameCancelBtn = document.getElementById("semester-rename-cancel-btn");
    if (semesterRenameCancelBtn) semesterRenameCancelBtn.addEventListener("click", closeSemesterRenamePopup);
    
    const semesterRenameSaveBtn = document.getElementById("semester-rename-save-btn");
    if (semesterRenameSaveBtn) semesterRenameSaveBtn.addEventListener("click", saveSemesterRename);
    
    const deleteSubjectCancelBtn = document.getElementById("delete-subject-cancel-btn");
    if (deleteSubjectCancelBtn) deleteSubjectCancelBtn.addEventListener("click", closeDeleteSubjectConfirm);
    
    const deleteSubjectConfirmBtn = document.getElementById("delete-subject-confirm-btn");
    if (deleteSubjectConfirmBtn) deleteSubjectConfirmBtn.addEventListener("click", confirmDeleteSubject);
    
    const deleteGradeCancelBtn = document.getElementById("delete-grade-cancel-btn");
    if (deleteGradeCancelBtn) deleteGradeCancelBtn.addEventListener("click", closeDeleteGradeConfirm);
    
    const deleteGradeConfirmBtn = document.getElementById("delete-grade-confirm-btn");
    if (deleteGradeConfirmBtn) deleteGradeConfirmBtn.addEventListener("click", confirmDeleteGrade);

    // Close popups on ESC
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeGradePopup();
            closeSubjectPopup();
            closeSemesterRenamePopup();
            closeSemesterCreatePopup();
            closeDeleteConfirm();
            closeDeleteSubjectConfirm();
            closeDeleteGradeConfirm();
            closeDreamCalcPopup();
        }
    });
}