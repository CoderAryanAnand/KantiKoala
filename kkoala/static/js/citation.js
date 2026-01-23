/**
 * Citation Generator JavaScript
 * Handles citation form, groups, and API interactions
 */

// Global state
let currentStyle = 'apa';
let currentType = 'book';
let groups = [];
let editingCitation = null;

// API base URL
const API_BASE = '/api/citations';

// Get CSRF token from the page
function getCsrfToken() {
    return document.getElementById('csrf-token')?.value || '';
}

// Format date from input to German format
function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('de-CH', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

// -------------------------------
// Field Configurations for all source types
// -------------------------------

const SOURCE_TYPE_NAMES = {
    'book': 'Buch',
    'anthology': 'Sammelband',
    'anthology_chapter': 'Beitrag in Sammelband',
    'journal_article': 'Zeitschriftenartikel',
    'newspaper_article': 'Zeitungsartikel',
    'thesis': 'Hochschulschrift',
    'website': 'Webseite',
    'online_media_article': 'Online-Artikel',
    'ebook': 'E-Book',
    'blog': 'Blog',
    'social_media': 'Social Media',
    'online_lexicon': 'Online-Lexikon',
    'ai': 'KI-Tool',
    'podcast': 'Podcast',
    'song': 'Song',
    'film': 'Film',
    'streaming_series': 'Streaming-Serie',
    'video_stream': 'Video',
    'game': 'Videospiel',
    'image_web': 'Bild (Web)',
    'interview': 'Interview',
    'article': 'Artikel'
};

const FIELD_CONFIGS = {
    book: [
        { name: 'authors', label: 'Autor(en)', placeholder: 'Nachname, V.', hint: 'z.B. Müller, H. & Schmidt, K.' },
        { name: 'year', label: 'Jahr', placeholder: '2024' },
        { name: 'title', label: 'Titel', placeholder: 'Buchtitel', fullWidth: true },
        { name: 'subtitle', label: 'Untertitel', placeholder: 'Optional', fullWidth: true },
        { name: 'publisher', label: 'Verlag', placeholder: 'Verlagsname' },
        { name: 'place', label: 'Ort', placeholder: 'Verlagsort' },
        { name: 'edition', label: 'Auflage', placeholder: 'z.B. 2. Aufl.' }
    ],
    anthology: [
        { name: 'editors', label: 'Herausgeber', placeholder: 'Nachname, V.', hint: 'z.B. Müller, H. (Hg.)' },
        { name: 'year', label: 'Jahr', placeholder: '2024' },
        { name: 'title', label: 'Titel', placeholder: 'Titel des Sammelbands', fullWidth: true },
        { name: 'subtitle', label: 'Untertitel', placeholder: 'Optional', fullWidth: true },
        { name: 'publisher', label: 'Verlag', placeholder: 'Verlagsname' },
        { name: 'place', label: 'Ort', placeholder: 'Verlagsort' }
    ],
    anthology_chapter: [
        { name: 'authors', label: 'Autor(en) des Beitrags', placeholder: 'Nachname, V.' },
        { name: 'year', label: 'Jahr', placeholder: '2024' },
        { name: 'title', label: 'Titel des Beitrags', placeholder: 'Beitragstitel', fullWidth: true },
        { name: 'editors', label: 'Herausgeber', placeholder: 'Nachname, V.' },
        { name: 'container_title', label: 'Titel des Sammelbands', placeholder: 'Sammelbandtitel', fullWidth: true },
        { name: 'publisher', label: 'Verlag', placeholder: 'Verlagsname' },
        { name: 'place', label: 'Ort', placeholder: 'Verlagsort' },
        { name: 'pages', label: 'Seiten', placeholder: 'z.B. 45-67' }
    ],
    journal_article: [
        { name: 'authors', label: 'Autor(en)', placeholder: 'Nachname, V.' },
        { name: 'year', label: 'Jahr', placeholder: '2024' },
        { name: 'title', label: 'Artikeltitel', placeholder: 'Titel des Artikels', fullWidth: true },
        { name: 'journal', label: 'Zeitschrift', placeholder: 'Name der Zeitschrift', fullWidth: true },
        { name: 'volume', label: 'Band', placeholder: 'z.B. 12' },
        { name: 'issue', label: 'Ausgabe/Nr.', placeholder: 'z.B. 3' },
        { name: 'pages', label: 'Seiten', placeholder: 'z.B. 45-67' }
    ],
    newspaper_article: [
        { name: 'authors', label: 'Autor(en)', placeholder: 'Nachname, V.' },
        { name: 'title', label: 'Artikeltitel', placeholder: 'Titel des Artikels', fullWidth: true },
        { name: 'newspaper', label: 'Zeitung', placeholder: 'Name der Zeitung' },
        { name: 'date', label: 'Datum', placeholder: 'TT.MM.JJJJ', type: 'date' },
        { name: 'pages', label: 'Seiten', placeholder: 'z.B. S. 5' }
    ],
    thesis: [
        { name: 'authors', label: 'Autor(en)', placeholder: 'Nachname, V.' },
        { name: 'year', label: 'Jahr', placeholder: '2024' },
        { name: 'title', label: 'Titel', placeholder: 'Titel der Arbeit', fullWidth: true },
        { name: 'thesis_type', label: 'Art der Arbeit', placeholder: 'z.B. Masterarbeit, Dissertation' },
        { name: 'university', label: 'Hochschule', placeholder: 'Name der Universität' },
        { name: 'place', label: 'Ort', placeholder: 'Stadt' }
    ],
    website: [
        { name: 'authors', label: 'Autor(en)', placeholder: 'Nachname, V. (optional)' },
        { name: 'title', label: 'Titel der Seite', placeholder: 'Seitentitel', fullWidth: true },
        { name: 'site_name', label: 'Webseitenname', placeholder: 'z.B. Wikipedia' },
        { name: 'date', label: 'Veröffentlichungsdatum', placeholder: 'TT.MM.JJJJ', type: 'date' },
        { name: 'url', label: 'URL', placeholder: 'https://...', fullWidth: true, type: 'url' },
        { name: 'access_date', label: 'Zugriffsdatum', placeholder: 'TT.MM.JJJJ', type: 'date' }
    ],
    online_media_article: [
        { name: 'authors', label: 'Autor(en)', placeholder: 'Nachname, V.' },
        { name: 'title', label: 'Artikeltitel', placeholder: 'Titel des Artikels', fullWidth: true },
        { name: 'publication', label: 'Publikation/Medium', placeholder: 'z.B. Spiegel Online' },
        { name: 'date', label: 'Datum', placeholder: 'TT.MM.JJJJ', type: 'date' },
        { name: 'url', label: 'URL', placeholder: 'https://...', fullWidth: true, type: 'url' },
        { name: 'access_date', label: 'Zugriffsdatum', placeholder: 'TT.MM.JJJJ', type: 'date' }
    ],
    ebook: [
        { name: 'authors', label: 'Autor(en)', placeholder: 'Nachname, V.' },
        { name: 'year', label: 'Jahr', placeholder: '2024' },
        { name: 'title', label: 'Titel', placeholder: 'Buchtitel', fullWidth: true },
        { name: 'publisher', label: 'Verlag', placeholder: 'Verlagsname' },
        { name: 'place', label: 'Ort', placeholder: 'Verlagsort' },
        { name: 'identifier', label: 'DOI/ISBN', placeholder: 'z.B. doi:10.1234/5678' }
    ],
    blog: [
        { name: 'authors', label: 'Autor(en)', placeholder: 'Nachname, V.' },
        { name: 'title', label: 'Beitragstitel', placeholder: 'Titel des Blogbeitrags', fullWidth: true },
        { name: 'blog_name', label: 'Blogname', placeholder: 'Name des Blogs' },
        { name: 'date', label: 'Datum', placeholder: 'TT.MM.JJJJ', type: 'date' },
        { name: 'url', label: 'URL', placeholder: 'https://...', fullWidth: true, type: 'url' },
        { name: 'access_date', label: 'Zugriffsdatum', placeholder: 'TT.MM.JJJJ', type: 'date' }
    ],
    social_media: [
        { name: 'authors', label: 'Name/Account', placeholder: 'z.B. Max Mustermann' },
        { name: 'handle', label: 'Handle/Username', placeholder: 'z.B. @username' },
        { name: 'title', label: 'Beitragsinhalt', placeholder: 'Text des Beitrags (gekürzt)', fullWidth: true },
        { name: 'platform', label: 'Plattform', placeholder: 'z.B. Twitter, Instagram' },
        { name: 'date', label: 'Datum', placeholder: 'TT.MM.JJJJ', type: 'date' },
        { name: 'url', label: 'URL', placeholder: 'https://...', fullWidth: true, type: 'url' },
        { name: 'access_date', label: 'Zugriffsdatum', placeholder: 'TT.MM.JJJJ', type: 'date' }
    ],
    online_lexicon: [
        { name: 'authors', label: 'Autor(en)', placeholder: 'Nachname, V. (optional)' },
        { name: 'title', label: 'Lemma/Artikeltitel', placeholder: 'Stichwort', fullWidth: true },
        { name: 'lexicon', label: 'Lexikon', placeholder: 'z.B. Wikipedia, Duden Online' },
        { name: 'date', label: 'Datum der Version', placeholder: 'TT.MM.JJJJ', type: 'date' },
        { name: 'url', label: 'URL', placeholder: 'https://...', fullWidth: true, type: 'url' },
        { name: 'access_date', label: 'Zugriffsdatum', placeholder: 'TT.MM.JJJJ', type: 'date' }
    ],
    ai: [
        { name: 'ai_name', label: 'KI-Tool', placeholder: 'z.B. ChatGPT, Claude' },
        { name: 'version', label: 'Version', placeholder: 'z.B. GPT-4, 3.5' },
        { name: 'prompt', label: 'Prompt/Anfrage', placeholder: 'Deine Eingabe an die KI', fullWidth: true },
        { name: 'date', label: 'Datum', placeholder: 'TT.MM.JJJJ', type: 'date' },
        { name: 'usage_type', label: 'Art der Verwendung', placeholder: 'z.B. Als Inspiration verwendet', fullWidth: true }
    ],
    podcast: [
        { name: 'authors', label: 'Host/Sprecher', placeholder: 'Nachname, V.' },
        { name: 'title', label: 'Episodentitel', placeholder: 'Titel der Episode', fullWidth: true },
        { name: 'podcast_name', label: 'Podcast-Name', placeholder: 'Name des Podcasts' },
        { name: 'date', label: 'Datum', placeholder: 'TT.MM.JJJJ', type: 'date' },
        { name: 'url', label: 'URL', placeholder: 'https://...', fullWidth: true, type: 'url' },
        { name: 'access_date', label: 'Zugriffsdatum', placeholder: 'TT.MM.JJJJ', type: 'date' }
    ],
    song: [
        { name: 'authors', label: 'Künstler/Band', placeholder: 'Name des Künstlers' },
        { name: 'title', label: 'Songtitel', placeholder: 'Titel des Songs', fullWidth: true },
        { name: 'album', label: 'Album', placeholder: 'Name des Albums' },
        { name: 'label', label: 'Label', placeholder: 'Plattenlabel' },
        { name: 'year', label: 'Jahr', placeholder: '2024' }
    ],
    film: [
        { name: 'directors', label: 'Regisseur(e)', placeholder: 'Nachname, V.' },
        { name: 'title', label: 'Filmtitel', placeholder: 'Titel des Films', fullWidth: true },
        { name: 'distributor', label: 'Studio/Anbieter', placeholder: 'z.B. Warner Bros.' },
        { name: 'country', label: 'Land', placeholder: 'z.B. USA' },
        { name: 'year', label: 'Jahr', placeholder: '2024' }
    ],
    streaming_series: [
        { name: 'episode_title', label: 'Episodentitel', placeholder: 'Titel der Episode', fullWidth: true },
        { name: 'credits', label: 'Credits', placeholder: 'Drehbuch: X, Regie: Y' },
        { name: 'series', label: 'Serienname', placeholder: 'Name der Serie' },
        { name: 'season', label: 'Staffel', placeholder: 'z.B. 1' },
        { name: 'episode_num', label: 'Folge', placeholder: 'z.B. 5' },
        { name: 'platform', label: 'Plattform', placeholder: 'z.B. Netflix' },
        { name: 'year', label: 'Jahr', placeholder: '2024' },
        { name: 'access_date', label: 'Zugriffsdatum', placeholder: 'TT.MM.JJJJ', type: 'date' }
    ],
    video_stream: [
        { name: 'username', label: 'Kanal/Username', placeholder: 'Name des Kanals' },
        { name: 'title', label: 'Videotitel', placeholder: 'Titel des Videos', fullWidth: true },
        { name: 'date', label: 'Veröffentlichungsdatum', placeholder: 'TT.MM.JJJJ', type: 'date' },
        { name: 'url', label: 'URL', placeholder: 'https://...', fullWidth: true, type: 'url' },
        { name: 'access_date', label: 'Zugriffsdatum', placeholder: 'TT.MM.JJJJ', type: 'date' }
    ],
    game: [
        { name: 'title', label: 'Spieltitel', placeholder: 'Name des Spiels', fullWidth: true },
        { name: 'company', label: 'Entwickler/Publisher', placeholder: 'z.B. Nintendo' },
        { name: 'platform', label: 'Plattform', placeholder: 'z.B. PlayStation 5' },
        { name: 'year', label: 'Jahr', placeholder: '2024' }
    ],
    image_web: [
        { name: 'number', label: 'Abbildungsnummer', placeholder: 'z.B. 1' },
        { name: 'authors', label: 'Urheber/Künstler', placeholder: 'Nachname, V.' },
        { name: 'title', label: 'Bildtitel/Beschreibung', placeholder: 'Titel oder Beschreibung', fullWidth: true },
        { name: 'date', label: 'Datum', placeholder: 'TT.MM.JJJJ', type: 'date' },
        { name: 'url', label: 'URL', placeholder: 'https://...', fullWidth: true, type: 'url' },
        { name: 'access_date', label: 'Zugriffsdatum', placeholder: 'TT.MM.JJJJ', type: 'date' }
    ],
    interview: [
        { name: 'interviewer', label: 'Interviewer', placeholder: 'Nachname, V.' },
        { name: 'interviewee', label: 'Interviewte Person', placeholder: 'Nachname, V.' },
        { name: 'place', label: 'Ort', placeholder: 'Ort des Interviews' },
        { name: 'date', label: 'Datum', placeholder: 'TT.MM.JJJJ', type: 'date' }
    ],
    // Legacy article type (maps to journal_article)
    article: [
        { name: 'authors', label: 'Autor(en)', placeholder: 'Nachname, V.' },
        { name: 'year', label: 'Jahr', placeholder: '2024' },
        { name: 'title', label: 'Artikeltitel', placeholder: 'Titel des Artikels', fullWidth: true },
        { name: 'journal', label: 'Zeitschrift', placeholder: 'Name der Zeitschrift', fullWidth: true },
        { name: 'volume', label: 'Band', placeholder: 'z.B. 12' },
        { name: 'issue', label: 'Ausgabe', placeholder: 'z.B. 3' },
        { name: 'pages', label: 'Seiten', placeholder: 'z.B. 45-67' }
    ]
};

// -------------------------------
// Style and Type Selection
// -------------------------------

function initStyleButtons() {
    document.querySelectorAll('.style-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            currentStyle = btn.dataset.style;
            updateStyleButtons();
            updatePreview();
        });
    });
}

function updateStyleButtons() {
    document.querySelectorAll('.style-btn').forEach(btn => {
        if (btn.dataset.style === currentStyle) {
            btn.classList.add('border-blue-500', 'bg-blue-500', 'text-white');
            btn.classList.remove('border-zinc-300', 'dark:border-zinc-600', 'text-zinc-700', 'dark:text-zinc-300');
        } else {
            btn.classList.remove('border-blue-500', 'bg-blue-500', 'text-white');
            btn.classList.add('border-zinc-300', 'dark:border-zinc-600', 'text-zinc-700', 'dark:text-zinc-300');
        }
    });
}

function initTypeButtons() {
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            currentType = btn.dataset.type;
            updateTypeButtons();
            renderFormFields();
            updatePreview();
        });
    });
}

function updateTypeButtons() {
    document.querySelectorAll('.type-btn').forEach(btn => {
        if (btn.dataset.type === currentType) {
            btn.classList.add('border-green-500', 'bg-green-500', 'text-white');
            btn.classList.remove('border-zinc-300', 'dark:border-zinc-600', 'text-zinc-700', 'dark:text-zinc-300');
        } else {
            btn.classList.remove('border-green-500', 'bg-green-500', 'text-white');
            btn.classList.add('border-zinc-300', 'dark:border-zinc-600', 'text-zinc-700', 'dark:text-zinc-300');
        }
    });
}

// -------------------------------
// Dynamic Form Fields
// -------------------------------

function renderFormFields(data = {}) {
    const container = document.getElementById('dynamic-fields');
    if (!container) return;
    
    const fields = FIELD_CONFIGS[currentType] || FIELD_CONFIGS['book'];
    
    let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4">';
    
    fields.forEach(field => {
        const value = data[field.name] || '';
        const colSpan = field.fullWidth ? 'md:col-span-2' : '';
        const inputType = field.type || 'text';
        
        html += `
            <div class="${colSpan}">
                <label class="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">${field.label}</label>
                <input type="${inputType}" name="${field.name}" value="${escapeHtml(value)}" placeholder="${field.placeholder}" 
                    class="w-full px-4 py-2.5 rounded-lg border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-700 text-zinc-800 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none">
                ${field.hint ? `<p class="text-xs text-zinc-500 dark:text-zinc-400 mt-1">${field.hint}</p>` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    
    // Re-attach input listeners for preview
    initFormListeners();
    
    // Set today's date for date fields if empty
    const today = new Date().toISOString().split('T')[0];
    container.querySelectorAll('input[type="date"]').forEach(input => {
        if (!input.value && input.name.includes('access')) {
            input.value = today;
        }
    });
}

// -------------------------------
// Citation Preview
// -------------------------------

function getFormData() {
    const container = document.getElementById('dynamic-fields');
    if (!container) return {};
    
    const data = {};
    container.querySelectorAll('input').forEach(input => {
        let value = input.value.trim();
        // Format date if it's a date input
        if (input.type === 'date' && value) {
            value = formatDate(value);
        }
        data[input.name] = value;
    });
    return data;
}

async function updatePreview() {
    const data = getFormData();
    const previewEl = document.getElementById('citation-preview');
    
    // Check if we have minimum required data
    const hasData = Object.values(data).some(v => v);
    if (!hasData) {
        previewEl.innerHTML = '<span class="text-zinc-400 dark:text-zinc-500 italic">Fülle die Felder aus, um eine Vorschau zu sehen...</span>';
        document.getElementById('save-citation').disabled = true;
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/format`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCsrfToken()
            },
            body: JSON.stringify({
                style: currentStyle,
                sourceType: currentType,
                data: data
            })
        });
        
        const result = await response.json();
        if (response.ok) {
            previewEl.innerHTML = result.formattedCitation;
            document.getElementById('save-citation').disabled = false;
        } else {
            previewEl.innerHTML = `<span class="text-red-500">${result.error}</span>`;
        }
    } catch (error) {
        console.error('Preview error:', error);
        previewEl.innerHTML = '<span class="text-red-500">Fehler beim Generieren der Vorschau</span>';
    }
}

function initFormListeners() {
    document.querySelectorAll('#citation-form input').forEach(input => {
        input.addEventListener('input', debounce(updatePreview, 300));
    });
}

// Debounce helper
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// -------------------------------
// Groups Management
// -------------------------------

async function loadGroups() {
    try {
        const response = await fetch(`${API_BASE}/groups`);
        groups = await response.json();
        renderGroups();
        updateGroupSelect();
    } catch (error) {
        console.error('Error loading groups:', error);
    }
}

function renderGroups() {
    const container = document.getElementById('groups-container');
    
    if (groups.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-zinc-500 dark:text-zinc-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <p>Noch keine Gruppen vorhanden.</p>
                <p class="text-sm">Erstelle eine neue Gruppe, um Zitate zu speichern.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = groups.map(group => `
        <div class="bg-white dark:bg-zinc-800 rounded-xl shadow-lg overflow-hidden" data-group-id="${group.id}">
            <div class="p-4 border-b border-zinc-200 dark:border-zinc-700 flex items-center justify-between">
                <h3 class="font-semibold text-zinc-800 dark:text-white">${escapeHtml(group.name)}</h3>
                <div class="flex items-center gap-2">
                    <button onclick="openEditGroupModal(${group.id}, '${escapeHtml(group.name)}')" class="p-1.5 text-zinc-500 hover:text-blue-600 dark:hover:text-blue-400" title="Bearbeiten">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                    </button>
                    <button onclick="deleteGroup(${group.id})" class="p-1.5 text-zinc-500 hover:text-red-600 dark:hover:text-red-400" title="Löschen">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            </div>
            <div class="p-4 space-y-3">
                ${group.citations.length === 0 
                    ? '<p class="text-sm text-zinc-500 dark:text-zinc-400 italic">Keine Zitate in dieser Gruppe.</p>'
                    : group.citations.map(citation => `
                        <div class="group p-3 bg-zinc-50 dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-zinc-700">
                            <div class="flex items-start justify-between gap-2">
                                <div class="text-sm text-zinc-700 dark:text-zinc-300 flex-grow">${citation.formattedCitation}</div>
                                <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button onclick="copyCitationText(\`${escapeHtml(citation.formattedCitation.replace(/`/g, '\\`'))}\`)" class="p-1 text-zinc-500 hover:text-blue-600 dark:hover:text-blue-400" title="Kopieren">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                        </svg>
                                    </button>
                                    <button onclick="openEditCitationModal(${citation.id})" class="p-1 text-zinc-500 hover:text-blue-600 dark:hover:text-blue-400" title="Bearbeiten">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                        </svg>
                                    </button>
                                    <button onclick="deleteCitation(${citation.id})" class="p-1 text-zinc-500 hover:text-red-600 dark:hover:text-red-400" title="Löschen">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                            <div class="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                                ${getSourceTypeName(citation.sourceType)} • ${getStyleName(citation.style)}
                            </div>
                        </div>
                    `).join('')
                }
            </div>
        </div>
    `).join('');
}

function getSourceTypeName(type) {
    return SOURCE_TYPE_NAMES[type] || type;
}

function getStyleName(style) {
    const names = {
        'apa': 'APA',
        'mla': 'MLA',
        'chicago': 'Chicago',
        'kanti_baden': 'Kanti Baden'
    };
    return names[style] || style.toUpperCase();
}

function updateGroupSelect() {
    const select = document.getElementById('target-group');
    select.innerHTML = '<option value="">Gruppe wählen...</option>' +
        groups.map(g => `<option value="${g.id}">${escapeHtml(g.name)}</option>`).join('');
}

async function createGroup() {
    const nameInput = document.getElementById('new-group-name');
    const name = nameInput.value.trim();
    
    if (!name) {
        alert('Bitte gib einen Gruppennamen ein.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/groups`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCsrfToken()
            },
            body: JSON.stringify({ name })
        });
        
        if (response.ok) {
            nameInput.value = '';
            loadGroups();
        } else {
            const result = await response.json();
            alert(result.error || 'Fehler beim Erstellen der Gruppe');
        }
    } catch (error) {
        console.error('Error creating group:', error);
        alert('Fehler beim Erstellen der Gruppe');
    }
}

async function deleteGroup(groupId) {
    if (!confirm('Möchtest du diese Gruppe und alle Zitate darin wirklich löschen?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/groups/${groupId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRF-Token': getCsrfToken()
            }
        });
        
        if (response.ok) {
            loadGroups();
        } else {
            const result = await response.json();
            alert(result.error || 'Fehler beim Löschen der Gruppe');
        }
    } catch (error) {
        console.error('Error deleting group:', error);
        alert('Fehler beim Löschen der Gruppe');
    }
}

// -------------------------------
// Edit Group Modal
// -------------------------------

function openEditGroupModal(groupId, groupName) {
    document.getElementById('edit-group-id').value = groupId;
    document.getElementById('edit-group-name').value = groupName;
    document.getElementById('edit-group-modal').classList.remove('hidden');
}

function closeEditGroupModal() {
    document.getElementById('edit-group-modal').classList.add('hidden');
}

async function saveGroupName() {
    const groupId = document.getElementById('edit-group-id').value;
    const name = document.getElementById('edit-group-name').value.trim();
    
    if (!name) {
        alert('Bitte gib einen Gruppennamen ein.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/groups/${groupId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCsrfToken()
            },
            body: JSON.stringify({ name })
        });
        
        if (response.ok) {
            closeEditGroupModal();
            loadGroups();
        } else {
            const result = await response.json();
            alert(result.error || 'Fehler beim Speichern');
        }
    } catch (error) {
        console.error('Error updating group:', error);
        alert('Fehler beim Speichern');
    }
}

// -------------------------------
// Save Citation
// -------------------------------

async function saveCitation() {
    const groupId = document.getElementById('target-group').value;
    
    if (!groupId) {
        alert('Bitte wähle eine Gruppe aus.');
        return;
    }
    
    const data = getFormData();
    
    try {
        const response = await fetch(`${API_BASE}/groups/${groupId}/citations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCsrfToken()
            },
            body: JSON.stringify({
                style: currentStyle,
                sourceType: currentType,
                data: data
            })
        });
        
        if (response.ok) {
            // Clear form
            document.querySelectorAll('#citation-form input').forEach(input => {
                if (input.type !== 'date' || !input.name.includes('access')) {
                    input.value = '';
                }
            });
            updatePreview();
            loadGroups();
        } else {
            const result = await response.json();
            alert(result.error || 'Fehler beim Speichern des Zitats');
        }
    } catch (error) {
        console.error('Error saving citation:', error);
        alert('Fehler beim Speichern des Zitats');
    }
}

async function deleteCitation(citationId) {
    if (!confirm('Möchtest du dieses Zitat wirklich löschen?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/citations/${citationId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRF-Token': getCsrfToken()
            }
        });
        
        if (response.ok) {
            loadGroups();
        } else {
            const result = await response.json();
            alert(result.error || 'Fehler beim Löschen des Zitats');
        }
    } catch (error) {
        console.error('Error deleting citation:', error);
        alert('Fehler beim Löschen des Zitats');
    }
}

// -------------------------------
// Edit Citation Modal
// -------------------------------

function openEditCitationModal(citationId) {
    // Find the citation in our groups data
    let citation = null;
    for (const group of groups) {
        citation = group.citations.find(c => c.id === citationId);
        if (citation) break;
    }
    
    if (!citation) {
        alert('Zitat nicht gefunden');
        return;
    }
    
    editingCitation = citation;
    
    const formContainer = document.getElementById('edit-citation-form');
    document.getElementById('edit-citation-id').value = citationId;
    
    // Build style options including Kanti Baden
    const styleOptions = `
        <option value="apa" ${citation.style === 'apa' ? 'selected' : ''}>APA</option>
        <option value="mla" ${citation.style === 'mla' ? 'selected' : ''}>MLA</option>
        <option value="chicago" ${citation.style === 'chicago' ? 'selected' : ''}>Chicago</option>
        <option value="kanti_baden" ${citation.style === 'kanti_baden' ? 'selected' : ''}>Kanti Baden</option>
    `;
    
    // Build source type options
    const typeOptions = Object.entries(SOURCE_TYPE_NAMES).map(([value, label]) => 
        `<option value="${value}" ${citation.sourceType === value ? 'selected' : ''}>${label}</option>`
    ).join('');
    
    // Build form based on source type
    formContainer.innerHTML = `
        <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
                <label class="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Zitierstil</label>
                <select id="edit-style" class="w-full px-4 py-2.5 rounded-lg border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-700 text-zinc-800 dark:text-white">
                    ${styleOptions}
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">Quellentyp</label>
                <select id="edit-source-type" class="w-full px-4 py-2.5 rounded-lg border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-700 text-zinc-800 dark:text-white" onchange="updateEditFormFields()">
                    ${typeOptions}
                </select>
            </div>
        </div>
        <div id="edit-fields-container">
            ${buildEditFields(citation.sourceType, citation.data)}
        </div>
    `;
    
    document.getElementById('edit-citation-modal').classList.remove('hidden');
}

function buildEditFields(sourceType, data) {
    const fields = FIELD_CONFIGS[sourceType] || FIELD_CONFIGS['book'];
    let html = '<div class="grid grid-cols-2 gap-4">';
    
    fields.forEach(field => {
        const value = data[field.name] || '';
        const colSpan = field.fullWidth ? 'col-span-2' : '';
        const inputType = field.type || 'text';
        
        html += `
            <div class="${colSpan}">
                <label class="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">${field.label}</label>
                <input type="${inputType}" name="${field.name}" value="${escapeHtml(value)}" placeholder="${field.placeholder}" 
                    class="w-full px-4 py-2.5 rounded-lg border border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-700 text-zinc-800 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none">
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

function updateEditFormFields() {
    const sourceType = document.getElementById('edit-source-type').value;
    const container = document.getElementById('edit-fields-container');
    container.innerHTML = buildEditFields(sourceType, editingCitation?.data || {});
}

function closeEditCitationModal() {
    document.getElementById('edit-citation-modal').classList.add('hidden');
    editingCitation = null;
}

async function updateCitation() {
    const citationId = document.getElementById('edit-citation-id').value;
    const style = document.getElementById('edit-style').value;
    const sourceType = document.getElementById('edit-source-type').value;
    
    const data = {};
    document.querySelectorAll('#edit-fields-container input').forEach(input => {
        let value = input.value.trim();
        // Format date if it's a date input
        if (input.type === 'date' && value) {
            value = formatDate(value);
        }
        data[input.name] = value;
    });
    
    try {
        const response = await fetch(`${API_BASE}/citations/${citationId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCsrfToken()
            },
            body: JSON.stringify({
                style,
                sourceType,
                data
            })
        });
        
        if (response.ok) {
            closeEditCitationModal();
            loadGroups();
        } else {
            const result = await response.json();
            alert(result.error || 'Fehler beim Aktualisieren des Zitats');
        }
    } catch (error) {
        console.error('Error updating citation:', error);
        alert('Fehler beim Aktualisieren des Zitats');
    }
}

// -------------------------------
// Copy Functionality
// -------------------------------

function copyCitation() {
    const previewEl = document.getElementById('citation-preview');
    const text = previewEl.innerText || previewEl.textContent;
    
    if (text && !text.includes('Fülle die Felder aus')) {
        copyToClipboard(text);
    }
}

function copyCitationText(text) {
    // Remove HTML tags for clipboard
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = text;
    const plainText = tempDiv.textContent || tempDiv.innerText;
    copyToClipboard(plainText);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show brief confirmation (could be enhanced with a toast notification)
        const btn = document.getElementById('copy-citation');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg> Kopiert!';
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Copy failed:', err);
    });
}

// -------------------------------
// Utility Functions
// -------------------------------

function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// -------------------------------
// Initialization
// -------------------------------

document.addEventListener('DOMContentLoaded', () => {
    initStyleButtons();
    initTypeButtons();
    renderFormFields(); // Render initial fields
    loadGroups();
    
    // Event listeners
    document.getElementById('create-group').addEventListener('click', createGroup);
    document.getElementById('new-group-name').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') createGroup();
    });
    document.getElementById('save-citation').addEventListener('click', saveCitation);
    document.getElementById('copy-citation').addEventListener('click', copyCitation);
});
