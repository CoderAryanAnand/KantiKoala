let currentMode = 'flashcards';
let currentIndex = 0;
let isFlipped = false;
let writeQueue = [];
let cards = []; // The currently active set of cards (filtered or all)
let starredOnly = false;

document.addEventListener('DOMContentLoaded', () => {
    // allCards is defined in the HTML template
    cards = [...allCards];
    
    updateStats();
    updateFlashcardView();
    renderList();
    
    // Show star filter if we have cards
    if (allCards.length > 0) {
        document.getElementById('star-filter-container').classList.remove('hidden');
    }
});

function updateStats() {
    document.getElementById('total-cards').textContent = cards.length;
    const starredCount = allCards.filter(c => c.starred).length;
    document.getElementById('starred-count').textContent = starredCount;
}

function toggleStarFilter() {
    starredOnly = !starredOnly;
    
    if (starredOnly) {
        cards = allCards.filter(c => c.starred);
    } else {
        cards = [...allCards];
    }
    
    currentIndex = 0;
    updateStats();
    updateFlashcardView();
    
    // If in write mode, reset it
    if (currentMode === 'write') {
        initWriteMode();
    }
}

function switchMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-section').forEach(el => el.classList.add('hidden'));
    document.getElementById(`mode-${mode}`).classList.remove('hidden');
    
    // Update tabs styling
    const tabs = ['flashcards', 'write', 'list'];
    tabs.forEach(t => {
        const el = document.getElementById(`tab-${t}`);
        if (t === mode) {
            el.classList.remove('text-zinc-500', 'hover:text-zinc-900', 'dark:text-zinc-400', 'dark:hover:text-zinc-200', 'bg-transparent');
            el.classList.add('bg-blue-100', 'text-blue-700', 'dark:bg-blue-900/30', 'dark:text-blue-400');
        } else {
            el.classList.add('text-zinc-500', 'hover:text-zinc-900', 'dark:text-zinc-400', 'dark:hover:text-zinc-200', 'bg-transparent');
            el.classList.remove('bg-blue-100', 'text-blue-700', 'dark:bg-blue-900/30', 'dark:text-blue-400');
        }
    });

    if (mode === 'write') initWriteMode();
}

// --- Flashcards Mode ---

function updateFlashcardView() {
    const container = document.getElementById('flashcard-inner');
    
    if (cards.length === 0) {
        document.getElementById('card-front-content').textContent = starredOnly ? "Keine markierten Karten vorhanden." : "Keine Karten vorhanden.";
        document.getElementById('card-back-content').textContent = "";
        document.getElementById('current-card-index').textContent = "0";
        return;
    }
    
    const card = cards[currentIndex];
    const side = document.getElementById('flashcard-side').value;
    
    const frontContent = side === 'term' ? card.term : card.definition;
    const backContent = side === 'term' ? card.definition : card.term;
    
    document.getElementById('card-front-content').textContent = frontContent;
    document.getElementById('card-back-content').textContent = backContent;
    document.getElementById('current-card-index').textContent = currentIndex + 1;
    
    // Update star buttons state
    updateStarButtons(card.starred);
    
    // Reset flip
    container.classList.remove('rotate-y-180');
    isFlipped = false;
}

function updateStarButtons(isStarred) {
    const btns = [document.getElementById('star-btn-front'), document.getElementById('star-btn-back')];
    btns.forEach(btn => {
        if (isStarred) {
            btn.classList.add('text-yellow-400');
            btn.classList.remove('text-zinc-300');
            btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clip-rule="evenodd" /></svg>`;
        } else {
            btn.classList.remove('text-yellow-400');
            btn.classList.add('text-zinc-300');
            btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>`;
        }
    });
}

function toggleStarCurrent() {
    if (cards.length === 0) return;
    const card = cards[currentIndex];
    card.starred = !card.starred;
    
    // Update UI
    updateStarButtons(card.starred);
    updateStats();
    
    // If we are in filtered mode and unstar, we might want to remove it or just keep it until refresh
    // For now, let's keep it visible to avoid confusion, but update the count
}

function flipCard() {
    const inner = document.getElementById('flashcard-inner');
    if (isFlipped) {
        inner.classList.remove('rotate-y-180');
    } else {
        inner.classList.add('rotate-y-180');
    }
    isFlipped = !isFlipped;
}

function nextCard() {
    if (currentIndex < cards.length - 1) {
        currentIndex++;
        updateFlashcardView();
    } else {
        // Loop back to start? Or just stop?
        // Let's loop for better UX
        currentIndex = 0;
        updateFlashcardView();
    }
}

function prevCard() {
    if (currentIndex > 0) {
        currentIndex--;
        updateFlashcardView();
    } else {
        currentIndex = cards.length - 1;
        updateFlashcardView();
    }
}

// --- Write Mode ---

function initWriteMode() {
    // Shuffle cards for write mode
    writeQueue = [...cards].sort(() => Math.random() - 0.5);
    
    document.getElementById('write-remaining').textContent = writeQueue.length;
    document.getElementById('write-progress').style.width = '0%';
    
    showNextWriteCard();
}

function showNextWriteCard() {
    const container = document.getElementById('write-active'); // Note: ID might have changed in HTML, let's check
    // In new HTML, the container is just the parent div, we toggle visibility of finished state
    
    const finished = document.getElementById('write-finished');
    const input = document.getElementById('write-input');
    
    if (writeQueue.length === 0) {
        // Show finished state
        // We need to hide the input area
        // In the new HTML structure, the input area is inside the main card
        // Let's just hide the main card content and show finished
        // Actually, let's look at the HTML structure again.
        // There is #write-finished and the input area is in the same parent but not wrapped in a single ID that toggles with finished.
        // Wait, I see: <div id="write-finished" class="hidden ...">
        // And the input stuff is just inside <div class="bg-white ...">
        // I should probably wrap the active content in a div to toggle it easily.
        // Let's assume I can just hide the input and prompt.
        
        // Let's use the structure I defined in the HTML replacement:
        // The input and prompt are direct children of the card div.
        // I should probably wrap them in a div with id="write-active-area" in the HTML, but I didn't.
        // Let's just hide the specific elements.
        
        document.getElementById('write-prompt').parentElement.classList.add('hidden'); // Hides the whole card
        document.getElementById('write-finished').classList.remove('hidden');
        document.getElementById('write-progress').style.width = '100%';
        return;
    }
    
    // Ensure active area is visible
    document.getElementById('write-prompt').parentElement.classList.remove('hidden');
    document.getElementById('write-finished').classList.add('hidden');
    
    // Reset UI
    document.getElementById('write-feedback').classList.add('hidden');
    document.getElementById('btn-check').classList.remove('hidden');
    document.getElementById('btn-next-write').classList.add('hidden');
    document.getElementById('btn-override').classList.add('hidden');
    
    input.value = '';
    input.disabled = false;
    input.focus();
    
    const card = writeQueue[0];
    const answerSide = 'term'; // Default to answering with term (seeing definition)
    // We could add a toggle for this in write mode too
    
    // For now let's assume: Show Definition -> Type Term
    // Or make it random? Or configurable?
    // The HTML has a "write-answer-side" select in the old version, but I removed it in the new one to simplify.
    // Let's assume: Show Definition, Type Term.
    
    document.getElementById('write-prompt').textContent = card.definition;
    
    // Update progress
    const total = cards.length;
    const current = total - writeQueue.length;
    const percent = (current / total) * 100;
    document.getElementById('write-progress').style.width = `${percent}%`;
    document.getElementById('write-remaining').textContent = writeQueue.length;
}

function checkAnswer() {
    const input = document.getElementById('write-input');
    const userVal = input.value.trim();
    if (!userVal) return;
    
    const card = writeQueue[0];
    const correctVal = card.term; // Assuming we type term
    
    const feedback = document.getElementById('write-feedback');
    feedback.classList.remove('hidden');
    
    input.disabled = true;
    document.getElementById('btn-check').classList.add('hidden');
    document.getElementById('btn-next-write').classList.remove('hidden');
    
    if (userVal.toLowerCase() === correctVal.toLowerCase()) {
        feedback.className = "mb-6 p-4 rounded-md text-sm bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";
        feedback.innerHTML = `<strong>Richtig!</strong>`;
        
        // Auto advance after short delay if correct
        setTimeout(() => nextWriteCard(), 1000);
    } else {
        feedback.className = "mb-6 p-4 rounded-md text-sm bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400";
        feedback.innerHTML = `
            <p class="font-bold">Nicht ganz...</p>
            <p class="mt-1">Deine Antwort: <span class="line-through">${userVal}</span></p>
            <p class="mt-1">Richtige Lösung: <strong>${correctVal}</strong></p>
        `;
        document.getElementById('btn-override').classList.remove('hidden');
    }
}

function overrideAnswer() {
    // User claims they were right
    const feedback = document.getElementById('write-feedback');
    feedback.className = "mb-6 p-4 rounded-md text-sm bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400";
    feedback.innerHTML = `<strong>Okay, als richtig gewertet.</strong>`;
    setTimeout(() => nextWriteCard(), 800);
}

function nextWriteCard() {
    writeQueue.shift();
    showNextWriteCard();
}

// --- List / Edit Mode ---

function renderList() {
    const container = document.getElementById('cards-list');
    container.innerHTML = '';
    
    // Always show allCards in list mode for editing
    allCards.forEach((card, index) => {
        const div = document.createElement('div');
        div.className = 'p-4 flex gap-4 items-start group hover:bg-zinc-50 dark:hover:bg-zinc-700/30 transition-colors';
        div.innerHTML = `
            <div class="pt-8">
                <button onclick="toggleStarInList(${index})" class="text-zinc-300 hover:text-yellow-400 transition-colors ${card.starred ? 'text-yellow-400' : ''}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="${card.starred ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                </button>
            </div>
            <div class="flex-1">
                <label class="block text-xs text-zinc-500 mb-1">Begriff</label>
                <input type="text" value="${card.term}" onchange="updateCard(${index}, 'term', this.value)" class="w-full p-2 border rounded dark:bg-zinc-700 dark:border-zinc-600 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all">
            </div>
            <div class="flex-1">
                <label class="block text-xs text-zinc-500 mb-1">Definition</label>
                <input type="text" value="${card.definition}" onchange="updateCard(${index}, 'definition', this.value)" class="w-full p-2 border rounded dark:bg-zinc-700 dark:border-zinc-600 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all">
            </div>
            <button onclick="removeCard(${index})" class="mt-7 p-2 text-zinc-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-all" title="Karte löschen">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            </button>
        `;
        container.appendChild(div);
    });
}

function toggleStarInList(index) {
    allCards[index].starred = !allCards[index].starred;
    renderList();
    updateStats();
    // If we are in filtered mode, this might affect the view, but we are in list mode now.
    // When switching back to flashcards, the filter will be reapplied if active.
    if (starredOnly) {
        cards = allCards.filter(c => c.starred);
    }
}

function addCardInput() {
    allCards.push({ term: '', definition: '', starred: false });
    renderList();
    updateStats();
    if (!starredOnly) cards = [...allCards];
}

function updateCard(index, field, value) {
    allCards[index][field] = value;
}

function removeCard(index) {
    allCards.splice(index, 1);
    renderList();
    updateStats();
    if (starredOnly) {
        cards = allCards.filter(c => c.starred);
    } else {
        cards = [...allCards];
    }
}

async function saveSet() {
    const response = await fetch(`/tools/lernkarten/${SET_ID}/update`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ cards: allCards }) // Send all cards
    });
    
    if (response.ok) {
        // Show a nice toast or just reload
        // For now, reload to ensure sync
        window.location.reload();
    } else {
        alert('Fehler beim Speichern');
    }
}

async function deleteSet() {
    if (!confirm('Möchtest du dieses Set wirklich löschen?')) return;
    
    const response = await fetch(`/tools/lernkarten/${SET_ID}/delete`, {
        method: 'DELETE'
    });
    
    if (response.ok) {
        window.location.href = '/tools/lernkarten';
    }
}

async function exportSet() {
    const response = await fetch(`/tools/lernkarten/${SET_ID}/export`);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `flashcards-${SET_ID}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
