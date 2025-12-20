let currentMode = 'flashcards';
let currentIndex = 0;
let isFlipped = false;
let writeQueue = [];
let wrongAnswers = []; // Cards answered wrong in current round
let currentRound = 1;
let totalCardsInSession = 0; // Track total for progress
let correctInSession = 0; // Track correct answers
let cards = []; // The currently active set of cards (filtered or all)
let starredOnly = false;
let autoplayInterval = null;
let isAutoplayActive = false;

document.addEventListener('DOMContentLoaded', () => {
    // allCards is defined in the HTML template
    cards = [...allCards];
    
    updateStats();
    updateFlashcardView();
    renderList();
    renderStaticTermsList(); // Render the terms list in flashcard mode
    
    // Show star filter if we have cards
    if (allCards.length > 0) {
        document.getElementById('star-filter-container').classList.remove('hidden');
    }
    
    // Keyboard navigation
    document.addEventListener('keydown', handleKeyboard);
});

function handleKeyboard(e) {
    // Don't trigger if user is typing in an input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    if (currentMode === 'flashcards') {
        switch(e.key) {
            case 'ArrowLeft':
                prevCard();
                break;
            case 'ArrowRight':
                nextCard();
                break;
            case ' ':
            case 'ArrowUp':
            case 'ArrowDown':
                e.preventDefault();
                flipCard();
                break;
            case 's':
                toggleStarCurrent();
                break;
        }
    }
}

function updateStats() {
    document.getElementById('total-cards').textContent = cards.length;
    const starredCount = allCards.filter(c => c.starred).length;
    const starredCountEl = document.getElementById('starred-count');
    if (starredCountEl) starredCountEl.textContent = starredCount;
    
    // Update star filter button text and style
    const filterBtn = document.getElementById('star-filter-btn');
    if (filterBtn) {
        if (starredOnly) {
            filterBtn.textContent = 'Alle Karten zeigen';
            filterBtn.className = 'text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 border border-blue-600 px-3 py-1 rounded-md transition-colors';
        } else {
            filterBtn.textContent = `Nur markierte lernen (${starredCount})`;
            filterBtn.className = 'text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/30 px-3 py-1 rounded-md transition-colors';
        }
    }
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
    // Stop autoplay when switching modes
    if (isAutoplayActive) {
        toggleAutoplay();
    }
    
    currentMode = mode;
    document.querySelectorAll('.mode-section').forEach(el => el.classList.add('hidden'));
    document.getElementById(`mode-${mode}`).classList.remove('hidden');
    
    // Update tabs styling (border-bottom style)
    const tabs = ['flashcards', 'write', 'list'];
    tabs.forEach(t => {
        const el = document.getElementById(`tab-${t}`);
        if (t === mode) {
            el.classList.remove('border-transparent', 'text-zinc-500', 'dark:text-zinc-400');
            el.classList.add('border-blue-600', 'text-blue-600', 'font-semibold');
        } else {
            el.classList.add('border-transparent', 'text-zinc-500', 'dark:text-zinc-400');
            el.classList.remove('border-blue-600', 'text-blue-600', 'font-semibold');
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
    
    const frontEl = document.getElementById('card-front-content');
    const backEl = document.getElementById('card-back-content');
    
    frontEl.textContent = frontContent;
    backEl.textContent = backContent;
    
    adjustFontSize(frontEl, frontContent);
    adjustFontSize(backEl, backContent);
    
    document.getElementById('current-card-index').textContent = currentIndex + 1;
    
    // Update star buttons state
    updateStarButtons(card.starred);
    
    // Reset flip
    container.classList.remove('rotate-y-180');
    isFlipped = false;
}

function adjustFontSize(element, text) {
    element.classList.remove('text-4xl', 'text-3xl', 'text-2xl', 'text-xl', 'text-lg', 'text-base', 'text-sm');
    
    const len = text.length;
    if (len > 300) {
        element.classList.add('text-sm');
    } else if (len > 150) {
        element.classList.add('text-base');
    } else if (len > 80) {
        element.classList.add('text-lg');
    } else if (len > 40) {
        element.classList.add('text-2xl');
    } else {
        element.classList.add('text-4xl');
    }
}

function updateStarButtons(isStarred) {
    const btns = [document.getElementById('star-btn-front'), document.getElementById('star-btn-back')];
    btns.forEach(btn => {
        if (isStarred) {
            btn.className = 'absolute top-4 right-4 z-20 p-2 transition-colors';
            btn.style.color = '#facc15'; // Yellow when starred
            btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clip-rule="evenodd" /></svg>`;
        } else {
            btn.className = 'absolute top-4 right-4 z-20 p-2 transition-colors text-zinc-300 dark:text-zinc-500 hover:text-zinc-400';
            btn.style.color = ''; // Reset to use class colors
            btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>`;
        }
    });
}

function toggleStarCurrent() {
    if (cards.length === 0) return;
    
    const card = cards[currentIndex];
    // Find the card in allCards to update it there too
    const originalCard = allCards.find(c => c.id === card.id);
    if (originalCard) {
        originalCard.starred = !originalCard.starred;
        
        // Update UI
        updateStarButtons(originalCard.starred);
        updateStats();
        renderStaticTermsList();
        
        // Save to server
        fetch(`/tools/lernkarten/card/${originalCard.id}/star`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ starred: originalCard.starred })
        }).catch(err => console.error('Failed to save star', err));
    }
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

// --- Shuffle & Autoplay ---

function shuffleCards() {
    // Fisher-Yates shuffle
    const shuffled = [...cards];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    cards = shuffled;
    currentIndex = 0;
    updateFlashcardView();
    
    // Show brief feedback
    showToast('Karten gemischt!');
}

function toggleAutoplay() {
    const btn = document.getElementById('btn-autoplay');
    
    if (isAutoplayActive) {
        // Stop autoplay
        clearInterval(autoplayInterval);
        autoplayInterval = null;
        isAutoplayActive = false;
        btn.classList.remove('bg-blue-100', 'dark:bg-blue-900/30', 'text-blue-600', 'dark:text-blue-400');
        btn.classList.add('text-zinc-500');
    } else {
        // Start autoplay
        isAutoplayActive = true;
        btn.classList.add('bg-blue-100', 'dark:bg-blue-900/30', 'text-blue-600', 'dark:text-blue-400');
        btn.classList.remove('text-zinc-500');
        
        autoplayInterval = setInterval(() => {
            if (isFlipped) {
                // Move to next card
                nextCard();
            } else {
                // Flip the card
                flipCard();
            }
        }, 3000); // 3 seconds per side
    }
}

function showToast(message) {
    // Create a simple toast notification
    const existing = document.getElementById('toast-notification');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.id = 'toast-notification';
    toast.className = 'fixed bottom-8 left-1/2 transform -translate-x-1/2 bg-zinc-800 dark:bg-zinc-700 text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity duration-300';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// --- Write Mode ---

function initWriteMode() {
    // Reset state for new session
    writeQueue = [...cards].sort(() => Math.random() - 0.5);
    wrongAnswers = [];
    currentRound = 1;
    totalCardsInSession = cards.length;
    correctInSession = 0;
    
    document.getElementById('write-remaining').textContent = writeQueue.length;
    document.getElementById('write-progress').style.width = '0%';
    
    showNextWriteCard();
}

function showNextWriteCard() {
    const activeArea = document.getElementById('write-active-area');
    const finished = document.getElementById('write-finished');
    
    if (writeQueue.length === 0) {
        // Show finished state with stats
        activeArea.classList.add('hidden');
        finished.classList.remove('hidden');
        document.getElementById('write-progress').style.width = '100%';
        
        // Update finished message with stats
        finished.innerHTML = `
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 mb-4">
                <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            </div>
            <h2 class="text-2xl font-bold text-zinc-900 dark:text-white mb-2">Gut gemacht!</h2>
            <p class="text-zinc-500 dark:text-zinc-400 mb-2">Du hast alle ${totalCardsInSession} Begriffe gelernt.</p>
            <p class="text-zinc-500 dark:text-zinc-400 mb-6">${currentRound > 1 ? `Benötigte Runden: ${currentRound}` : 'Perfekt beim ersten Versuch!'}</p>
            <button onclick="initWriteMode()" class="text-blue-600 dark:text-blue-400 font-medium hover:text-blue-800 dark:hover:text-blue-300">Nochmal lernen</button>
        `;
        return;
    }
    
    const input = document.getElementById('write-input');
    if (!input) return; // Guard against missing elements during transition
    
    // Ensure active area is visible
    activeArea.classList.remove('hidden');
    finished.classList.add('hidden');
    
    // Reset UI
    document.getElementById('write-feedback').classList.add('hidden');
    document.getElementById('btn-check').classList.remove('hidden');
    document.getElementById('btn-check').textContent = 'Antworten';
    document.getElementById('btn-next-write').classList.add('hidden');
    document.getElementById('btn-override').classList.add('hidden');
    
    input.value = '';
    input.disabled = false;
    input.focus();
    
    const card = writeQueue[0];
    card._requiresTyping = false; // Reset typing requirement for new card
    const answerSide = 'term'; // Default to answering with term (seeing definition)
    // We could add a toggle for this in write mode too
    
    // For now let's assume: Show Definition -> Type Term
    // Or make it random? Or configurable?
    // The HTML has a "write-answer-side" select in the old version, but I removed it in the new one to simplify.
    // Let's assume: Show Definition, Type Term.
    
    document.getElementById('write-prompt').textContent = card.definition;
    
    // Update progress - based on correct answers vs total
    const percent = (correctInSession / totalCardsInSession) * 100;
    document.getElementById('write-progress').style.width = `${percent}%`;
    document.getElementById('write-remaining').textContent = writeQueue.length;
}

function checkAnswer() {
    const input = document.getElementById('write-input');
    const userVal = input.value.trim();
    
    const card = writeQueue[0];
    const correctVal = card.term;
    
    const feedback = document.getElementById('write-feedback');
    feedback.classList.remove('hidden');
    
    // Handle empty answer - require typing the correct answer
    if (!userVal) {
        card._wasCorrect = false;
        card._requiresTyping = true;
        
        feedback.className = "mb-6 p-4 rounded-md text-sm bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400";
        feedback.innerHTML = `
            <p class="font-bold">Keine Antwort eingegeben</p>
            <p class="mt-2">Tippe die richtige Antwort ein, um fortzufahren:</p>
            <p class="mt-1 text-lg font-bold">${escapeHtml(correctVal)}</p>
        `;
        
        // Change button to verify typed answer
        document.getElementById('btn-check').textContent = 'Bestätigen';
        input.placeholder = 'Richtige Antwort eintippen...';
        input.focus();
        return;
    }
    
    // If user was required to type the correct answer after empty submission
    if (card._requiresTyping) {
        if (userVal.toLowerCase() === correctVal.toLowerCase()) {
            // They typed it correctly, now they can proceed (but still counts as wrong)
            feedback.className = "mb-6 p-4 rounded-md text-sm bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400";
            feedback.innerHTML = `<strong>Gut! Jetzt geht's weiter.</strong>`;
            
            input.disabled = true;
            document.getElementById('btn-check').classList.add('hidden');
            document.getElementById('btn-next-write').classList.remove('hidden');
            document.getElementById('btn-check').textContent = 'Antworten';
            
            setTimeout(() => nextWriteCard(false), 1000);
        } else {
            // Still not correct, keep trying
            feedback.innerHTML = `
                <p class="font-bold">Das stimmt noch nicht ganz.</p>
                <p class="mt-2">Tippe genau ein:</p>
                <p class="mt-1 text-lg font-bold">${escapeHtml(correctVal)}</p>
            `;
            input.value = '';
            input.focus();
        }
        return;
    }
    
    input.disabled = true;
    document.getElementById('btn-check').classList.add('hidden');
    document.getElementById('btn-next-write').classList.remove('hidden');
    
    // Store for later use in nextWriteCard
    card._wasCorrect = userVal.toLowerCase() === correctVal.toLowerCase();
    
    if (card._wasCorrect) {
        feedback.className = "mb-6 p-4 rounded-md text-sm bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";
        feedback.innerHTML = `<strong>Richtig!</strong>`;
        
        // Auto advance after short delay if correct
        setTimeout(() => nextWriteCard(true), 1000);
    } else {
        feedback.className = "mb-6 p-4 rounded-md text-sm bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400";
        feedback.innerHTML = `
            <p class="font-bold">Nicht ganz...</p>
            <p class="mt-1">Deine Antwort: <span class="line-through">${escapeHtml(userVal)}</span></p>
            <p class="mt-1">Richtige Lösung: <strong>${escapeHtml(correctVal)}</strong></p>
            <p class="mt-3 text-xs">Tippe die richtige Antwort ein, um fortzufahren:</p>
        `;
        
        // Require typing the correct answer
        card._requiresTyping = true;
        input.disabled = false;
        input.value = '';
        input.placeholder = 'Richtige Antwort eintippen...';
        input.focus();
        document.getElementById('btn-check').classList.remove('hidden');
        document.getElementById('btn-check').textContent = 'Bestätigen';
        document.getElementById('btn-next-write').classList.add('hidden');
        document.getElementById('btn-override').classList.remove('hidden');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function overrideAnswer() {
    // User claims they were right - mark as correct and skip typing requirement
    const card = writeQueue[0];
    card._wasCorrect = true;
    card._requiresTyping = false;
    
    const input = document.getElementById('write-input');
    input.disabled = true;
    
    document.getElementById('btn-check').classList.add('hidden');
    document.getElementById('btn-check').textContent = 'Antworten';
    document.getElementById('btn-override').classList.add('hidden');
    document.getElementById('btn-next-write').classList.remove('hidden');
    
    const feedback = document.getElementById('write-feedback');
    feedback.className = "mb-6 p-4 rounded-md text-sm bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400";
    feedback.innerHTML = `<strong>Okay, als richtig gewertet.</strong>`;
    setTimeout(() => nextWriteCard(true), 800);
}

function nextWriteCard(wasCorrect = false) {
    const card = writeQueue.shift();
    
    if (wasCorrect || card._wasCorrect) {
        // Correct answer - count it
        correctInSession++;
    } else {
        // Wrong answer - add to wrong answers for next round
        wrongAnswers.push(card);
    }
    
    // Check if current round is done
    if (writeQueue.length === 0) {
        if (wrongAnswers.length > 0) {
            // Start next round with wrong answers
            currentRound++;
            writeQueue = [...wrongAnswers].sort(() => Math.random() - 0.5);
            wrongAnswers = [];
            
            // Show round transition
            showRoundTransition();
            return;
        }
        // All done - show finished
    }
    
    showNextWriteCard();
}

function showRoundTransition() {
    const activeArea = document.getElementById('write-active-area');
    const finished = document.getElementById('write-finished');
    
    // Update the UI to show round info
    activeArea.innerHTML = `
        <div class="text-center py-12">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-orange-100 dark:bg-orange-900/30 mb-4">
                <svg class="w-8 h-8 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
            </div>
            <h2 class="text-2xl font-bold text-zinc-900 dark:text-white mb-2">Runde ${currentRound}</h2>
            <p class="text-zinc-500 dark:text-zinc-400 mb-6">
                ${writeQueue.length} ${writeQueue.length === 1 ? 'Begriff' : 'Begriffe'} noch zu lernen
            </p>
            <button onclick="continueWriteMode()" class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-md transition-colors">
                Weiter lernen
            </button>
        </div>
    `;
}

function continueWriteMode() {
    // Restore the active area HTML
    const activeArea = document.getElementById('write-active-area');
    activeArea.innerHTML = `
        <!-- Progress Bar -->
        <div class="w-full bg-zinc-200 dark:bg-zinc-800 rounded-full h-2.5 mb-8">
            <div id="write-progress" class="bg-blue-600 h-2.5 rounded-full transition-all duration-300" style="width: 0%"></div>
        </div>

        <div class="bg-white dark:bg-zinc-900 shadow-lg rounded-xl p-8 border border-zinc-200 dark:border-zinc-800">
            <div class="mb-2 text-xs font-bold text-zinc-400 uppercase tracking-wider">Frage</div>
            <div id="write-prompt" class="text-xl text-zinc-800 dark:text-zinc-100 mb-8 font-medium leading-relaxed"></div>
            
            <div id="write-feedback" class="mb-6 p-4 rounded-md text-sm hidden"></div>

            <div class="relative">
                <label for="write-input" class="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Deine Antwort</label>
                <input type="text" id="write-input" class="w-full rounded-md border-zinc-300 dark:border-zinc-700 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-3 border dark:bg-zinc-800 dark:text-white" placeholder="Antwort eingeben..." autocomplete="off" onkeydown="if(event.key==='Enter') checkAnswer()">
                
                <div class="mt-6 flex justify-between items-center">
                    <div class="text-sm text-zinc-500 dark:text-zinc-400">
                        Runde ${currentRound} • Verbleibend: <span id="write-remaining" class="font-bold">0</span>
                    </div>
                    <div class="flex space-x-3">
                        <button onclick="overrideAnswer()" id="btn-override" class="items-center px-4 py-2 border border-yellow-400 dark:border-yellow-500 text-sm font-medium rounded-md shadow-sm text-yellow-700 dark:text-yellow-300 bg-yellow-50 dark:bg-yellow-900/30 hover:bg-yellow-100 dark:hover:bg-yellow-900/50 focus:outline-none hidden">
                            Ich hatte recht
                        </button>
                        <button onclick="checkAnswer()" id="btn-check" class="items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            Antworten
                        </button>
                        <button onclick="nextWriteCard()" id="btn-next-write" class="items-center px-6 py-2 border border-zinc-300 dark:border-zinc-700 text-sm font-medium rounded-md shadow-sm text-zinc-700 dark:text-zinc-200 bg-white dark:bg-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-700 focus:outline-none hidden">
                            Nächste Karte
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    showNextWriteCard();
}

// --- List / Edit Mode ---

function renderList() {
    const container = document.getElementById('cards-list');
    container.innerHTML = '';
    
    // Always show allCards in list mode for editing
    allCards.forEach((card, index) => {
        const div = document.createElement('div');
        div.className = 'p-6 flex gap-6 items-start group hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors';
        
        // Create elements properly to handle special characters
        div.innerHTML = `
            <div class="pt-8 text-sm text-zinc-400 dark:text-zinc-500 font-mono w-8 text-center">
                ${index + 1}
            </div>
            <div class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="group/input">
                    <label class="block text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider mb-2 transition-colors group-focus-within/input:text-blue-600 dark:group-focus-within/input:text-blue-400">Begriff</label>
                    <input type="text" data-index="${index}" data-field="term" class="card-input w-full p-0 border-b-2 border-zinc-200 dark:border-zinc-600 bg-transparent focus:border-blue-500 dark:focus:border-blue-400 hover:border-blue-300 dark:hover:border-blue-500 focus:ring-0 text-zinc-800 dark:text-zinc-100 pb-2 transition-colors placeholder-zinc-400 dark:placeholder-zinc-500 font-medium text-lg outline-none" placeholder="Begriff eingeben..." ${!IS_OWNER ? 'disabled' : ''}>
                </div>
                <div class="group/input">
                    <label class="block text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider mb-2 transition-colors group-focus-within/input:text-blue-600 dark:group-focus-within/input:text-blue-400">Definition</label>
                    <input type="text" data-index="${index}" data-field="definition" class="card-input w-full p-0 border-b-2 border-zinc-200 dark:border-zinc-600 bg-transparent focus:border-blue-500 dark:focus:border-blue-400 hover:border-blue-300 dark:hover:border-blue-500 focus:ring-0 text-zinc-800 dark:text-zinc-100 pb-2 transition-colors placeholder-zinc-400 dark:placeholder-zinc-500 text-lg outline-none" placeholder="Definition eingeben..." ${!IS_OWNER ? 'disabled' : ''}>
                </div>
            </div>
            <div class="pt-6 flex flex-col gap-2">
                 <button class="star-btn p-2 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors ${card.starred ? '' : 'text-zinc-300 dark:text-zinc-500 hover:text-zinc-400'}" data-index="${index}" style="${card.starred ? 'color: #facc15;' : ''}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="${card.starred ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                </button>
                ${IS_OWNER ? `
                <button class="delete-btn p-2 text-zinc-400 dark:text-zinc-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-full transition-all" data-index="${index}" title="Karte löschen">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
                ` : ''}
            </div>
        `;
        
        // Set values safely (handles quotes and special chars)
        const inputs = div.querySelectorAll('.card-input');
        inputs[0].value = card.term;
        inputs[1].value = card.definition;
        
        container.appendChild(div);
    });
    
    // Add event listeners
    container.querySelectorAll('.card-input').forEach(input => {
        input.addEventListener('change', (e) => {
            const idx = parseInt(e.target.dataset.index);
            const field = e.target.dataset.field;
            allCards[idx][field] = e.target.value;
        });
    });
    
    container.querySelectorAll('.star-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = parseInt(e.currentTarget.dataset.index);
            toggleStarInList(idx);
        });
    });
    
    container.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = parseInt(e.currentTarget.dataset.index);
            removeCard(idx);
        });
    });
}

function toggleStarInList(index) {
    allCards[index].starred = !allCards[index].starred;
    renderList();
    renderStaticTermsList(); // Also update the static list
    updateStats();
    // If we are in filtered mode, this might affect the view, but we are in list mode now.
    // When switching back to flashcards, the filter will be reapplied if active.
    if (starredOnly) {
        cards = allCards.filter(c => c.starred);
    }
}

// Render the read-only terms list in flashcard mode with working star buttons
function renderStaticTermsList() {
    const container = document.getElementById('static-terms-list');
    if (!container) return;

    container.innerHTML = '';

    allCards.forEach((card, index) => {
        const div = document.createElement('div');
        div.className = 'group flex items-start p-4 border-b border-zinc-100 dark:border-zinc-700 last:border-0 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors';

        const termDiv = document.createElement('div');
        termDiv.className = 'w-1/3 pr-4 border-r-2 border-zinc-100 dark:border-zinc-700 text-zinc-800 dark:text-zinc-100 font-medium break-words';
        termDiv.textContent = card.term;

        const defDiv = document.createElement('div');
        defDiv.className = 'flex-1 pl-4 text-zinc-600 dark:text-zinc-400 break-words';
        defDiv.textContent = card.definition;

        const btnContainer = document.createElement('div');
        btnContainer.className = 'flex items-center ml-4 flex-shrink-0';

        const starBtn = document.createElement('button');
        starBtn.className = 'p-1 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors';
        if (card.starred) {
            starBtn.style.color = '#facc15'; // Yellow when starred
            starBtn.innerHTML = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clip-rule="evenodd" /></svg>`;
        } else {
            starBtn.classList.add('text-zinc-300', 'dark:text-zinc-500', 'hover:text-zinc-400');
            starBtn.innerHTML = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>`;
        }
        starBtn.onclick = () => toggleStarInStaticList(index);

        btnContainer.appendChild(starBtn);
        div.appendChild(termDiv);
        div.appendChild(defDiv);
        div.appendChild(btnContainer);
        container.appendChild(div);
    });
}

// Toggle star in the static list (flashcard mode) and save immediately
async function toggleStarInStaticList(index) {
    allCards[index].starred = !allCards[index].starred;
    
    // Update both views
    renderStaticTermsList();
    updateStats();
    
    // Update the cards array if needed
    if (starredOnly) {
        cards = allCards.filter(c => c.starred);
    } else {
        cards = [...allCards];
    }
    
    // Update the current flashcard star buttons if viewing it
    if (currentIndex < cards.length) {
        updateStarButtons(cards[currentIndex].starred);
    }
    
    // Save to server immediately (using new endpoint)
    try {
        await fetch(`/tools/lernkarten/card/${allCards[index].id}/star`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ starred: allCards[index].starred })
        });
    } catch (error) {
        console.error('Failed to save star status:', error);
    }
}

function addCardInput() {
    // Check if the last card is empty
    if (allCards.length > 0) {
        const lastCard = allCards[allCards.length - 1];
        if (!lastCard.term.trim() || !lastCard.definition.trim()) {
            alert("Bitte fülle die letzte Karte aus, bevor du eine neue hinzufügst.");
            return;
        }
    }
    allCards.push({ term: '', definition: '', starred: false });
    renderList();
    updateStats();
    if (!starredOnly) cards = [...allCards];
    
    // Focus on the new term input
    const inputs = document.querySelectorAll('#cards-list .card-input[data-field="term"]');
    if (inputs.length > 0) {
        inputs[inputs.length - 1].focus();
    }
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
    // Validation: Check for empty fields
    const invalidCards = allCards.filter(c => !c.term.trim() || !c.definition.trim());
    if (invalidCards.length > 0) {
        alert('Bitte fülle alle Begriffe und Definitionen aus.');
        return;
    }

    const saveBtn = document.querySelector('button[onclick="saveSet()"]');
    const originalText = saveBtn.textContent;
    saveBtn.textContent = 'Speichern...';
    saveBtn.disabled = true;

    try {
        const response = await fetch(`/tools/lernkarten/${SET_ID}/update`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ cards: allCards })
        });
        
        if (response.ok) {
            // Show success feedback
            saveBtn.textContent = '✓ Gespeichert!';
            saveBtn.classList.remove('bg-green-600', 'hover:bg-green-700');
            saveBtn.classList.add('bg-green-500');
            
            // Update the cards reference for other modes
            cards = starredOnly ? allCards.filter(c => c.starred) : [...allCards];
            updateStats();
            
            setTimeout(() => {
                saveBtn.textContent = originalText;
                saveBtn.classList.add('bg-green-600', 'hover:bg-green-700');
                saveBtn.classList.remove('bg-green-500');
                saveBtn.disabled = false;
            }, 2000);
        } else {
            throw new Error('Save failed');
        }
    } catch (error) {
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;
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
    // Use ID if available, otherwise we might need to fetch it or use token
    // But export route likely needs ID or token. Let's assume token works if backend supports it.
    // Wait, export route wasn't updated to use token_or_id. I should check that.
    // Assuming I update export route too.
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

async function togglePublicStatus() {
    const isPublic = document.getElementById('public-toggle').checked;
    const label = document.getElementById('public-label');
    
    label.textContent = isPublic ? 'Öffentlich' : 'Privat';
    
    try {
        const response = await fetch(`/tools/lernkarten/${SET_ID}/update`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({is_public: isPublic})
        });
        
        if (response.ok) {
            // Reload to update UI (e.g. show/hide share button)
            window.location.reload();
        } else {
            alert('Fehler beim Aktualisieren des Status');
            // Revert toggle
            document.getElementById('public-toggle').checked = !isPublic;
            label.textContent = !isPublic ? 'Öffentlich' : 'Privat';
        }
    } catch (e) {
        console.error(e);
        alert('Fehler beim Aktualisieren des Status');
    }
}

function shareSet() {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
        alert('Link in die Zwischenablage kopiert!');
    }).catch(err => {
        console.error('Fehler beim Kopieren:', err);
        alert('Konnte Link nicht kopieren. Bitte kopiere die URL aus der Adresszeile.');
    });
}
