/* ==========================================================================
   NEET 3-in-1 Hub - Equal Priority Application Logic
   ========================================================================== */

let currentSubject = 'biology'; // 'biology', 'physics', 'chemistry'
let currentMode = 'single'; // 'single' or 'multi'
let currentClassFilter = 'all'; // 'all', 'c11', 'c12'
let allChapters = [];
let selectedChapters = new Set();
let selectedCount = 15;

// Quiz State
let quizQuestions = [];
let currentQIndex = 0;
let userAnswers = {}; // q_index -> 'A'/'B'/'C'/'D'
let timerInterval = null;
let secondsRemaining = 0;

const BOT_DATA = {
    'biology': {
        name: 'GPT Biology Bot',
        handle: '@gptbiologybot',
        url: 'https://t.me/gptbiologybot',
        icon: '🧬',
        color: '#2e8b57',
        desc: '32 Chapters • 7,735 NCERT MCQs • PDF Report Cards & AI Diagnostics'
    },
    'physics': {
        name: 'GPT Physics Bot',
        handle: '@gptphysicsbot',
        url: 'https://t.me/gptphysicsbot',
        icon: '⚡',
        color: '#0284c7',
        desc: '20 Chapters • 5,000 MCQs with LaTeX Formulas & AI Diagnostics'
    },
    'chemistry': {
        name: 'GPT Chemistry Bot',
        handle: '@gptchemistrybot',
        url: 'https://t.me/gptchemistrybot',
        icon: '🧪',
        color: '#d97706',
        desc: '20 Chapters • 5,000 MCQs with Chemical Reactions & AI Diagnostics'
    }
};

function trackEvent(eventName) {
    try {
        fetch(`/api/track?event=${eventName}`);
    } catch (e) {}
}

document.addEventListener('DOMContentLoaded', () => {
    loadChapters();
    trackEvent('site_visit');
    document.querySelectorAll('a[href*="t.me"]').forEach(link => {
        link.addEventListener('click', () => trackEvent('telegram_click'));
    });
});

// Mobile Drawer Toggle
function toggleMobileMenu() {
    const menu = document.getElementById('nav-menu');
    menu.classList.toggle('mobile-open');
}

function closeMobileMenu() {
    const menu = document.getElementById('nav-menu');
    menu.classList.remove('mobile-open');
}

// ── 1. Select Subject (Updates Telegram Banner with Subject Theme) ──
function selectSubject(subj) {
    currentSubject = subj;
    selectedChapters.clear();
    
    document.querySelectorAll('.subj-tab').forEach(tab => tab.classList.remove('active'));
    document.getElementById(`subj-tab-${subj}`).classList.add('active');

    const botInfo = BOT_DATA[subj] || BOT_DATA['biology'];

    // Update Telegram Highlight Banner & Theme Border
    const tgBox = document.getElementById('subj-tg-box');
    tgBox.style.borderColor = botInfo.color;

    document.getElementById('tg-box-icon').innerText = botInfo.icon;
    document.getElementById('tg-box-title').innerText = `Practice ${botInfo.name} on Telegram (${botInfo.handle})`;
    document.getElementById('tg-box-desc').innerText = botInfo.desc;
    
    const tgBtn = document.getElementById('tg-box-btn');
    tgBtn.href = botInfo.url;
    tgBtn.innerText = `💬 Open ${botInfo.name} ➔`;

    // Update Web Step Titles
    const subjName = subj.charAt(0).toUpperCase() + subj.slice(1);
    document.getElementById('mode-step-title').innerText = `Select Web Mode (${subjName})`;
    document.getElementById('chapter-step-title').innerText = `Choose ${subjName} Chapter(s)`;

    // Update Result Bot Link
    const botResultBtn = document.getElementById('result-bot-btn');
    if (botResultBtn) {
        botResultBtn.href = botInfo.url;
        botResultBtn.innerText = `💬 Get PDF Report on ${botInfo.name} ➔`;
    }

    loadChapters();
}

// ── 2. Fetch & Filter Chapters ──
async function loadChapters() {
    const container = document.getElementById('chapters-container');
    container.innerHTML = '<div style="color:#a0aec0; padding:20px; text-align:center;">Loading chapters...</div>';
    
    try {
        const res = await fetch(`/api/chapters?subject=${currentSubject}`);
        const data = await res.json();
        allChapters = data.chapters || [];
        renderChapters();
    } catch (err) {
        console.error('Failed to load chapters:', err);
        container.innerHTML = '<div style="color:#fda4af; padding:20px; text-align:center;">Failed to load chapters. Please refresh.</div>';
    }
}

function filterClass(classType) {
    currentClassFilter = classType;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`tab-${classType}`).classList.add('active');
    renderChapters();
}

function filterChapters() {
    renderChapters();
}

function renderChapters() {
    const container = document.getElementById('chapters-container');
    const searchVal = (document.getElementById('chapter-search').value || '').toLowerCase().trim();

    const filtered = allChapters.filter(ch => {
        return ch.toLowerCase().includes(searchVal);
    });

    if (filtered.length === 0) {
        container.innerHTML = '<div style="color:#a0aec0; grid-column: 1/-1; padding: 24px; text-align: center;">No matching chapters found.</div>';
        return;
    }

    container.innerHTML = filtered.map(ch => {
        const isSelected = selectedChapters.has(ch);
        const selectedClass = isSelected ? 'selected' : '';
        const checkIcon = isSelected ? '✓' : '';

        return `
            <div class="ch-item ${selectedClass}" onclick="toggleChapter('${escapeJs(ch)}')">
                <div>${escapeHtml(ch)}</div>
                <div class="ch-checkbox">${checkIcon}</div>
            </div>
        `;
    }).join('');

    updateSelectedCountBadge();
}

function selectMode(mode) {
    currentMode = mode;
    document.getElementById('mode-single-card').classList.toggle('active', mode === 'single');
    document.getElementById('mode-multi-card').classList.toggle('active', mode === 'multi');
    selectedChapters.clear();
    renderChapters();
}

function toggleChapter(chName) {
    if (currentMode === 'single') {
        selectedChapters.clear();
        selectedChapters.add(chName);
    } else {
        if (selectedChapters.has(chName)) {
            selectedChapters.delete(chName);
        } else {
            selectedChapters.add(chName);
        }
    }
    renderChapters();
}

function selectAllChapters() {
    allChapters.forEach(ch => selectedChapters.add(ch));
    renderChapters();
}

function clearAllChapters() {
    selectedChapters.clear();
    renderChapters();
}

function updateSelectedCountBadge() {
    const count = selectedChapters.size;
    const badge = document.getElementById('selected-count-badge');
    badge.innerText = `${count} Chapter${count === 1 ? '' : 's'} Selected`;
}

// ── 3. Navigation Steps ──
function goToStep(stepName) {
    if (stepName === 'chapters') {
        document.getElementById('multi-controls').style.display = (currentMode === 'multi') ? 'flex' : 'none';
    }

    if (stepName === 'count') {
        if (selectedChapters.size === 0) {
            alert('Please select at least 1 chapter to continue.');
            return;
        }

        const summaryBox = document.getElementById('selected-summary-text');
        const list = Array.from(selectedChapters);
        const listText = list.slice(0, 5).map(c => `• ${c}`).join('<br>');
        const extraText = list.length > 5 ? `<br><em>... and ${list.length - 5} more</em>` : '';
        
        summaryBox.innerHTML = `
            <strong>${currentSubject.toUpperCase()} (${currentMode === 'single' ? 'Single Chapter' : 'Custom Multi-Chapter'}):</strong> ${list.length} Chapter(s) Selected<br>
            <div style="margin-top: 8px;">${listText}${extraText}</div>
        `;
    }

    document.querySelectorAll('.sim-step').forEach(step => step.classList.remove('active'));
    document.getElementById(`sim-step-${stepName}`).classList.add('active');

    if (window.innerWidth <= 768) {
        document.getElementById('simulator-app').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function selectCount(count) {
    selectedCount = count;
    document.querySelectorAll('.count-card').forEach(card => {
        const isThis = card.innerText.includes(count.toString());
        card.classList.toggle('active', isThis);
    });
}

// ── 4. Start & Run Quiz ──
async function startQuiz() {
    trackEvent('web_test_start');
    const chaptersParam = Array.from(selectedChapters).join('||');
    const qBox = document.getElementById('q-text-display');
    const optsBox = document.getElementById('q-options-container');

    goToStep('quiz');
    qBox.innerHTML = 'Loading questions...';
    optsBox.innerHTML = '';

    try {
        const res = await fetch(`/api/questions?subject=${currentSubject}&chapters=${encodeURIComponent(chaptersParam)}&count=${selectedCount}`);
        const data = await res.json();
        
        if (!data.questions || data.questions.length === 0) {
            qBox.innerHTML = 'No questions available for the selected choices.';
            return;
        }

        quizQuestions = data.questions;
        currentQIndex = 0;
        userAnswers = {};
        
        secondsRemaining = quizQuestions.length * 60;
        startTimer();

        renderCurrentQuestion();
    } catch (err) {
        console.error('Failed to load questions:', err);
        qBox.innerHTML = 'Error fetching questions. Please try again.';
    }
}

function startTimer() {
    clearInterval(timerInterval);
    const timerElem = document.getElementById('quiz-timer');
    
    timerInterval = setInterval(() => {
        secondsRemaining--;
        if (secondsRemaining <= 0) {
            clearInterval(timerInterval);
            alert("⏰ Time's up! Submitting test...");
            submitQuiz();
            return;
        }
        const m = Math.floor(secondsRemaining / 60);
        const s = secondsRemaining % 60;
        timerElem.innerText = `⏱ ${m}:${s < 10 ? '0' : ''}${s}`;
    }, 1000);
}

function renderCurrentQuestion() {
    const q = quizQuestions[currentQIndex];
    const total = quizQuestions.length;

    document.getElementById('quiz-q-num').innerText = `Q. ${currentQIndex + 1}/${total}`;
    
    const subjBadge = (q.subject || currentSubject).toUpperCase();
    document.getElementById('quiz-chapter-tag').innerText = `[${subjBadge}] ${q.chapter || 'NEET Practice'}`;

    const pct = ((currentQIndex + 1) / total) * 100;
    document.getElementById('quiz-progress-bar').style.width = `${pct}%`;

    document.getElementById('q-text-display').innerHTML = renderMath(q.question);

    const optsContainer = document.getElementById('q-options-container');
    const selectedAns = userAnswers[currentQIndex];
    const labels = ['A', 'B', 'C', 'D'];

    optsContainer.innerHTML = labels.map(label => {
        const optVal = q.options[label.toLowerCase()] || q.options[label] || '';
        const isSelected = selectedAns === label;
        const selClass = isSelected ? 'selected' : '';

        return `
            <div class="opt-btn ${selClass}" onclick="selectOption('${label}')">
                <span class="opt-key">${label}</span>
                <span>${renderMath(optVal)}</span>
            </div>
        `;
    }).join('');

    document.getElementById('btn-prev-q').style.visibility = (currentQIndex > 0) ? 'visible' : 'hidden';
    document.getElementById('btn-next-q').innerText = (currentQIndex < total - 1) ? 'Next ▶' : 'Finish';
}

function selectOption(label) {
    userAnswers[currentQIndex] = label;
    renderCurrentQuestion();
}

function navigateQuestion(delta) {
    const newIdx = currentQIndex + delta;
    if (newIdx >= 0 && newIdx < quizQuestions.length) {
        currentQIndex = newIdx;
        renderCurrentQuestion();
        
        if (window.innerWidth <= 768) {
            document.getElementById('quiz-question-box').scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    } else if (newIdx >= quizQuestions.length) {
        confirmSubmitQuiz();
    }
}

function confirmSubmitQuiz() {
    const answeredCount = Object.keys(userAnswers).length;
    const total = quizQuestions.length;

    if (confirm(`You have answered ${answeredCount} of ${total} questions. Ready to submit?`)) {
        submitQuiz();
    }
}

// ── 5. KaTeX Math & Chemistry Renderer ──
function renderMath(str) {
    if (!str) return '';
    const safe = escapeHtml(str);
    if (typeof katex === 'undefined') return safe;
    return safe.replace(/\$(.*?)\$/g, (match, expr) => {
        try {
            const rawExpr = expr.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
            return katex.renderToString(rawExpr, { throwOnError: false });
        } catch (e) {
            return match;
        }
    });
}

// ── 6. Markdown Renderer ──
function renderMarkdown(md) {
    if (!md) return '';

    let html = md;
    html = html.replace(/^### (.*$)/gim, '<h5 class="ai-h3">$1</h5>');
    html = html.replace(/^## (.*$)/gim, '<h4 class="ai-h2">$1</h4>');
    html = html.replace(/^# (.*$)/gim, '<h3 class="ai-h1">$1</h3>');

    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/g, '<ul class="ai-list">$1</ul>');
    html = html.replace(/<\/ul>\s*<ul class="ai-list">/g, '');

    const parts = html.split(/\n\n+/);
    html = parts.map(p => {
        p = p.trim();
        if (!p) return '';
        if (p.startsWith('<h') || p.startsWith('<ul') || p.startsWith('<li')) return p;
        return `<p class="ai-p">${p.replace(/\n/g, '<br>')}</p>`;
    }).join('');

    return html;
}

// ── 7. Submit & Scorecard ──
async function submitQuiz() {
    clearInterval(timerInterval);
    trackEvent('web_test_complete');

    let correct = 0;
    let wrong = 0;
    let unanswered = 0;
    const wrongAnswersList = [];

    quizQuestions.forEach((q, idx) => {
        const userAns = userAnswers[idx];
        const correctAns = (q.answer || '').toUpperCase();
        
        if (userAns === correctAns) {
            correct++;
        } else if (userAns) {
            wrong++;
            wrongAnswersList.push({
                question: `[${q.subject || currentSubject}] ${q.question}`,
                user_answer: `${userAns}. ${q.options[userAns.toLowerCase()] || ''}`,
                correct_answer: `${correctAns}. ${q.options[correctAns.toLowerCase()] || ''}`
            });
        } else {
            unanswered++;
            wrongAnswersList.push({
                question: `[${q.subject || currentSubject}] ${q.question}`,
                user_answer: 'Not answered',
                correct_answer: `${correctAns}. ${q.options[correctAns.toLowerCase()] || ''}`
            });
        }
    });

    const total = quizQuestions.length;
    const marks = correct * 4 - wrong * 1;
    const maxMarks = total * 4;
    const pct = Math.max(0, Math.round((marks / maxMarks) * 100));

    document.getElementById('score-marks').innerText = `${marks}/${maxMarks}`;
    document.getElementById('score-pct').innerText = `${pct}%`;
    document.getElementById('res-correct').innerText = correct;
    document.getElementById('res-wrong').innerText = wrong;
    document.getElementById('res-unanswered').innerText = unanswered;

    const circle = document.getElementById('score-circle-fill');
    const offset = 251.2 - (251.2 * (pct / 100));
    circle.style.strokeDashoffset = offset;

    const summaryText = `${currentSubject.toUpperCase()}: ${Array.from(selectedChapters).join(', ')}`;
    document.getElementById('result-ch-summary').innerText = `Tested: ${summaryText}`;

    goToStep('result');

    fetchAIAnalysis(summaryText, correct, total, wrongAnswersList);
}

async function fetchAIAnalysis(chapter, correct, total, wrongAnswers) {
    const box = document.getElementById('ai-analysis-content');
    box.innerHTML = `
        <div class="ai-pulse-loading">
            <div class="pulse-ring"></div>
            <p>Analyzing wrong answers & consulting AI for personalized revision tips...</p>
        </div>
    `;

    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chapter, correct, total, wrong_answers: wrongAnswers })
        });
        const data = await res.json();
        
        if (data.analysis) {
            box.innerHTML = renderMarkdown(data.analysis);
        } else {
            box.innerHTML = '<p class="ai-p">AI evaluation report temporarily unavailable.</p>';
        }
    } catch (err) {
        console.error('Failed AI analysis:', err);
        box.innerHTML = '<p class="ai-p">AI evaluation report completed offline.</p>';
    }
}

function resetSimulator() {
    clearInterval(timerInterval);
    selectedChapters.clear();
    selectSubject('biology');
    goToStep('mode');
}

// ── Helpers ──
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
}

function escapeJs(str) {
    if (!str) return '';
    return str.replace(/'/g, "\\'");
}
