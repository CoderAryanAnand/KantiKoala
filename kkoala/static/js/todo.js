// Retrieves the CSRF token from the meta tag for secure requests
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Opens the popup for creating a new category and focuses the input
function openCreateCategoryPopup() {
    document.getElementById('overlay').classList.remove('hidden');
    document.getElementById('create-category-popup').classList.remove('hidden');
    document.getElementById('category-name').focus();
}

// Closes all popups and clears the category name input
function closeAllPopups() {
    document.getElementById('overlay').classList.add('hidden');
    document.getElementById('create-category-popup').classList.add('hidden');
    document.getElementById('category-name').value = '';
}

// Expands or collapses a category and rotates the chevron icon
function toggleCategory(categoryId) {
    const content = document.getElementById(`category-${categoryId}`);
    const icon = document.getElementById(`icon-${categoryId}`);
    content.classList.toggle('expanded');
    icon.classList.toggle('rotated');
}

// Handles the creation of a new category via form submission
document.getElementById('create-category-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('category-name').value.trim();
    if (!name) {
        alert('Bitte geben Sie einen Kategorienamen ein.');
        return;
    }
    try {
        const response = await fetch('/api/todo/categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCsrfToken()
            },
            body: JSON.stringify({ name })
        });
        if (response.ok) {
            const data = await response.json();
            location.reload(); // Reload to show new category
        } else {
            const error = await response.json();
            alert(error.message || 'Fehler beim Erstellen der Kategorie');
        }
    } catch (error) {
        console.error('Error creating category:', error);
        alert('Fehler beim Erstellen der Kategorie');
    }
});

// Deletes a category after user confirmation and animates its removal
async function deleteCategory(categoryId) {
    if (!confirm('Möchten Sie diese Kategorie wirklich löschen? Alle Aufgaben werden ebenfalls gelöscht.')) {
        return;
    }
    try {
        const response = await fetch(`/api/todo/categories/${categoryId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRF-Token': getCsrfToken()
            }
        });
        if (response.ok) {
            // Animate and remove the category from the DOM
            const categoryEl = document.querySelector(`[data-category-id="${categoryId}"]`);
            categoryEl.style.transition = 'opacity 0.3s ease-out';
            categoryEl.style.opacity = '0';
            setTimeout(() => {
                categoryEl.remove();
                // If no categories left, reload the page
                const container = document.getElementById('categories-container');
                if (container.children.length === 0) {
                    location.reload();
                }
            }, 300);
        } else {
            const error = await response.json();
            alert(error.message || 'Fehler beim Löschen der Kategorie');
        }
    } catch (error) {
        console.error('Error deleting category:', error);
        alert('Fehler beim Löschen der Kategorie');
    }
}

// Adds a new todo item to a category and updates the DOM
async function addTodoItem(categoryId) {
    const input = document.getElementById(`new-item-${categoryId}`);
    const description = input.value.trim();
    if (!description) {
        alert('Bitte geben Sie eine Aufgabe ein.');
        return;
    }
    try {
        const response = await fetch(`/api/todo/categories/${categoryId}/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCsrfToken()
            },
            body: JSON.stringify({ description })
        });
        if (response.ok) {
            const data = await response.json();
            // Create and append the new item element to the DOM
            const itemsContainer = document.getElementById(`items-${categoryId}`);
            const itemEl = document.createElement('div');
            itemEl.className = 'flex items-start space-x-3 p-3 bg-zinc-50 dark:bg-zinc-700/50 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors group';
            itemEl.setAttribute('data-item-id', data.item.id);
            itemEl.setAttribute('data-category-id', categoryId);
            itemEl.setAttribute('draggable', 'true');
            
            itemEl.innerHTML = `
                <div class="cursor-move text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 mt-0.5 flex-shrink-0 drag-handle">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                    </svg>
                </div>
                <input type="checkbox" 
                       onchange="completeAndDeleteTodoItem(${data.item.id}, this)"
                       class="h-5 w-5 mt-0.5 flex-shrink-0 rounded border-zinc-300 dark:border-zinc-600 text-blue-600 focus:ring-blue-500 focus:ring-offset-0 cursor-pointer">
                <span class="flex-1 text-zinc-800 dark:text-zinc-200 break-words min-w-0 cursor-pointer" onclick="this.previousElementSibling.click()">
                    ${escapeHtml(data.item.description)}
                </span>
            `;
            
            // Attach drag listeners
            itemEl.addEventListener('dragstart', handleDragStart);
            itemEl.addEventListener('dragover', handleDragOver);
            itemEl.addEventListener('drop', handleDrop);
            itemEl.addEventListener('dragend', handleDragEnd);
            
            itemsContainer.appendChild(itemEl);
            updateItemCount(categoryId);
            input.value = '';
            input.focus();
        } else {
            const error = await response.json();
            alert(error.message || 'Fehler beim Hinzufügen der Aufgabe');
        }
    } catch (error) {
        console.error('Error adding item:', error);
        alert('Fehler beim Hinzufügen der Aufgabe');
    }
}

// Marks a todo item as completed, animates, and deletes it from backend and DOM
async function completeAndDeleteTodoItem(itemId, checkbox) {
    if (!checkbox.checked) {
        // Only allow checking, not unchecking
        checkbox.checked = false;
        return;
    }
    try {
        // Delete the item in backend and animate removal in DOM
        const delResponse = await fetch(`/api/todo/items/${itemId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRF-Token': getCsrfToken()
            }
        });
        if (delResponse.ok) {
            const itemEl = document.querySelector(`[data-item-id="${itemId}"]`);
            const categoryId = itemEl.closest('[data-category-id]').getAttribute('data-category-id');
            const textSpan = itemEl.querySelector('span');
            // Add strikethrough animation
            textSpan.classList.add('line-through', 'text-zinc-500', 'dark:text-zinc-500', 'strikethrough-animation');
            itemEl.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
            setTimeout(() => {
                itemEl.style.opacity = '0';
                itemEl.style.transform = 'translateX(20px)';
                setTimeout(() => {
                    itemEl.remove();
                    updateItemCount(categoryId);
                }, 300);
            }, 300);
        } else {
            checkbox.checked = false;
            const error = await delResponse.json();
            alert(error.message || 'Fehler beim Löschen der Aufgabe');
        }
    } catch (error) {
        console.error('Error deleting item:', error);
        checkbox.checked = false;
        alert('Fehler beim Löschen der Aufgabe');
    }
}

// Updates the item count in the category header after changes
function updateItemCount(categoryId) {
    const categoryEl = document.querySelector(`[data-category-id="${categoryId}"]`);
    const itemsContainer = document.getElementById(`items-${categoryId}`);
    const itemCount = itemsContainer.querySelectorAll('[data-item-id]').length;
    const countSpan = categoryEl.querySelector('.text-sm.text-zinc-500');
    if (countSpan) {
        countSpan.textContent = `(${itemCount})`;
    }
}

// Escapes HTML to prevent XSS when rendering user input
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// On page load, collapse all categories and reset icons
document.addEventListener('DOMContentLoaded', () => {
    const categories = document.querySelectorAll('[data-category-id]');
    categories.forEach(cat => {
        const categoryId = cat.getAttribute('data-category-id');
        const content = document.getElementById(`category-${categoryId}`);
        const icon = document.getElementById(`icon-${categoryId}`);
        if (content && icon) {
            content.classList.remove('expanded');
            icon.classList.remove('rotated');
        }
    });
    initDragAndDrop();
});

// Closes all popups when the Escape key is pressed
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeAllPopups();
    }
});

// Drag and Drop Logic
let draggedItem = null;

function initDragAndDrop() {
    const items = document.querySelectorAll('[draggable="true"]');
    items.forEach(item => {
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragover', handleDragOver);
        item.addEventListener('drop', handleDrop);
        item.addEventListener('dragend', handleDragEnd);
    });
}

function handleDragStart(e) {
    draggedItem = this;
    this.style.opacity = '0.4';
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', this.dataset.itemId);
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    if (draggedItem && draggedItem !== this) {
        // Check if we are in the same category
        if (draggedItem.dataset.categoryId !== this.dataset.categoryId) {
            return false;
        }

        const bounding = this.getBoundingClientRect();
        const offset = bounding.y + (bounding.height / 2);
        
        if (e.clientY - offset > 0) {
            this.parentNode.insertBefore(draggedItem, this.nextSibling);
        } else {
            this.parentNode.insertBefore(draggedItem, this);
        }
        
        // Save the new order
        saveOrder(this.dataset.categoryId);
    }
    return false;
}

function handleDragEnd(e) {
    this.style.opacity = '1';
    draggedItem = null;
}

async function saveOrder(categoryId) {
    const container = document.getElementById(`items-${categoryId}`);
    const items = container.querySelectorAll('[data-item-id]');
    const itemIds = Array.from(items).map(item => item.dataset.itemId);
    
    try {
        await fetch(`/api/todo/categories/${categoryId}/reorder`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCsrfToken()
            },
            body: JSON.stringify({ itemIds })
        });
    } catch (error) {
        console.error('Error saving order:', error);
    }
}