/**
 * CampusMate AI - Main Frontend Logic
 * Interactive UI behaviors, sample notice loaders, checklist interactions,
 * real-time status updates, and Gemini Q&A integration.
 */

import { checkHealth, analyzeNotice, askNoticeQuestion } from './api.js';
import { state } from './state.js';
import { showToast, escapeHtml, copyToClipboard, formatFileSize } from './utils.js';

// Realistic sample notices for 1-click testing
const SAMPLE_NOTICES = {
  exam: `INDIAN INSTITUTE OF TECHNOLOGY BHILAI
OFFICE OF DEAN OF ACADEMIC AFFAIRS
NOTICE REF: IITBHI/ACAD/AUTUMN-2026/891
Date: 10 October 2026

Subject: Schedule and Instructions for Autumn Semester 2026 End-Semester Examinations

1. The End-Semester Examinations for all B.Tech, M.Tech, and M.Sc batches will commence on 15 November 2026 and conclude on 28 November 2026.
2. Students must strictly report to their examination halls at least 30 minutes prior to exam commencement (8:30 AM for Shift-1, 1:30 PM for Shift-2).
3. Carrying a physical Institute Identity Card and a printed copy of the Examination Admit Card is mandatory. No student will be allowed entry without both documents.
4. All laboratory project reports and pending continuous evaluation assignments must be uploaded to the Academic Portal before 05 November 2026, 5:00 PM. Submissions past this deadline will incur an automatic 20% mark penalty.
5. Seating arrangements and hall allocations will be posted on the academic notice board and student email portals 24 hours prior to each exam.

Queries may be directed to academics@iitbhilai.ac.in.
By Order,
Dean (Academic Affairs)`,

  hostel: `CAMPUS HOSTEL ADMINISTRATION & STUDENT AFFAIRS
CIRCULAR: HOSTEL FEE PAYMENT & ROOM ALLOCATION (SPRING 2027)
Notice No: HA/2026/FEE-11
Date: 08 October 2026

Attention: All Hostellers (Blocks A, B, C, and D)

This is to notify all registered students that the hostel renewal portal is now open for the upcoming Spring 2027 semester.
Key Guidelines:
1. The deadline for full hostel and mess advance payment (Rs. 28,500) is 20 November 2026 at 11:59 PM.
2. A late payment fee of Rs. 100 per day will be levied from 21 November 2026 to 25 November 2026.
3. Students requesting room changes must submit Form-H to the Warden's Office before 15 November 2026, 4:00 PM.
4. Clearance certificates must be signed by your wing representative prior to room vacating for semester break.
5. Room allocation lists will be published on 01 December 2026.

Hostel Office Contact: hosteladmin@campus.edu
Chief Warden`,

  hackathon: `CENTRE FOR INNOVATION AND ENTREPRENEURSHIP
HACKTOBERFEST 2026: 36-HOUR ANNUAL HACKATHON
Date: 05 October 2026

Calling all campus innovators and student developers! The annual campus hackathon 'Hacktoberfest 2026' will take place at the Central Innovation Center.
Schedule & Rules:
1. Team Registration Deadline: 25 October 2026 by 6:00 PM on the campus hackathon portal.
2. Shortlisting Announcement: 28 October 2026.
3. Hackathon Kick-off: 07 November 2026 at 9:00 AM (Central Innovation Complex, 3rd Floor).
4. Project Submission Deadline: 08 November 2026 at 9:00 PM.
5. Teams must consist of 2 to 4 members. Cross-department teams are eligible.
6. Participants must bring their own laptops and college ID cards. Food and Wi-Fi will be provided.`
};

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initTabs();
  initFileInput();
  initLanguageSelector();
  initSampleSelector();
  initActions();
  initAskForm();
  checkHealthStatus();
});

function initTheme() {
  const themeToggle = document.getElementById('theme-toggle');
  const storedTheme = state.theme || 'dark';
  state.setTheme(storedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const nextTheme = state.theme === 'dark' ? 'light' : 'dark';
      state.setTheme(nextTheme);
      updateThemeButtonIcon(nextTheme);
    });
    updateThemeButtonIcon(storedTheme);
  }
}

function updateThemeButtonIcon(currentTheme) {
  const icon = document.querySelector('#theme-toggle .theme-icon');
  if (icon) {
    icon.textContent = currentTheme === 'dark' ? '🌙' : '☀️';
  }
}

async function checkHealthStatus() {
  const statusBadge = document.getElementById('system-status');
  const res = await checkHealth();
  if (statusBadge) {
    if (res.status === 'ok') {
      statusBadge.innerHTML = `<span class="status-dot online"></span> AI Ready (${res.version})`;
      statusBadge.classList.add('online');
    } else {
      statusBadge.innerHTML = `<span class="status-dot offline"></span> System Offline`;
      statusBadge.classList.add('offline');
    }
  }
}

function initTabs() {
  const tabBtns = document.querySelectorAll('.input-tab-btn');
  const textPane = document.getElementById('text-input-pane');
  const filePane = document.getElementById('file-input-pane');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      state.setActiveTab(target);

      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      if (target === 'text') {
        textPane.classList.remove('hidden');
        filePane.classList.add('hidden');
      } else {
        textPane.classList.add('hidden');
        filePane.classList.remove('hidden');
      }
    });
  });

  // Textarea character counter
  const textarea = document.getElementById('notice-text');
  const charCount = document.getElementById('char-count');
  if (textarea && charCount) {
    textarea.addEventListener('input', () => {
      state.rawText = textarea.value;
      charCount.textContent = `${textarea.value.length} characters`;
    });
  }
}

function initFileInput() {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const previewBox = document.getElementById('file-preview-card');
  const previewName = document.getElementById('preview-filename');
  const previewSize = document.getElementById('preview-filesize');
  const previewThumb = document.getElementById('preview-thumbnail');
  const removeBtn = document.getElementById('remove-file-btn');

  if (!dropZone || !fileInput) return;

  dropZone.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      dropZone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
    });
  });

  dropZone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleSelectedFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files.length > 0) {
      handleSelectedFile(fileInput.files[0]);
    }
  });

  if (removeBtn) {
    removeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      state.selectedFile = null;
      fileInput.value = '';
      previewBox.classList.add('hidden');
      dropZone.classList.remove('hidden');
    });
  }

  function handleSelectedFile(file) {
    const validExts = ['.pdf', '.png', '.jpg', '.jpeg', '.webp', '.txt'];
    const lowerName = file.name.toLowerCase();
    const isValid = validExts.some(ext => lowerName.endsWith(ext));

    if (!isValid) {
      showToast('Unsupported format. Please upload PDF, PNG, JPG, or TXT.', 'error');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      showToast('File exceeds 10 MB maximum limit.', 'error');
      return;
    }

    state.selectedFile = file;
    previewName.textContent = file.name;
    previewSize.textContent = formatFileSize(file.size);

    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewThumb.src = e.target.result;
        previewThumb.classList.remove('hidden');
      };
      reader.readAsDataURL(file);
    } else {
      previewThumb.classList.add('hidden');
    }

    dropZone.classList.add('hidden');
    previewBox.classList.remove('hidden');
    showToast(`Loaded ${file.name}`, 'info');
  }
}

function initLanguageSelector() {
  const langPills = document.querySelectorAll('.lang-pill');
  langPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const lang = pill.dataset.lang;
      state.setLanguage(lang);
      langPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      showToast(`Language set to ${lang}`, 'info');
    });
  });
}

function initSampleSelector() {
  const sampleSelect = document.getElementById('sample-notices-select');
  const textarea = document.getElementById('notice-text');
  const charCount = document.getElementById('char-count');

  if (!sampleSelect || !textarea) return;

  sampleSelect.addEventListener('change', () => {
    const key = sampleSelect.value;
    if (key && SAMPLE_NOTICES[key]) {
      // Switch to text tab if on file tab
      const textTabBtn = document.querySelector('[data-tab="text"]');
      if (textTabBtn) textTabBtn.click();

      textarea.value = SAMPLE_NOTICES[key];
      state.rawText = textarea.value;
      if (charCount) charCount.textContent = `${textarea.value.length} characters`;
      showToast(`Loaded sample notice: ${sampleSelect.options[sampleSelect.selectedIndex].text}`, 'success');
    }
  });
}

function initActions() {
  const analyzeBtn = document.getElementById('analyze-btn');
  const clearBtn = document.getElementById('clear-btn');

  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', handleAnalyzeClick);
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      state.clearAll();
      const textarea = document.getElementById('notice-text');
      if (textarea) textarea.value = '';
      const charCount = document.getElementById('char-count');
      if (charCount) charCount.textContent = '0 characters';

      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';
      const dropZone = document.getElementById('drop-zone');
      const previewBox = document.getElementById('file-preview-card');
      if (dropZone) dropZone.classList.remove('hidden');
      if (previewBox) previewBox.classList.add('hidden');

      const sampleSelect = document.getElementById('sample-notices-select');
      if (sampleSelect) sampleSelect.value = '';

      renderEmptyState();
      showToast('All fields cleared', 'info');
    });
  }
}

async function handleAnalyzeClick() {
  const textarea = document.getElementById('notice-text');
  const textValue = textarea ? textarea.value.trim() : '';

  // Validate input presence
  if (state.activeTab === 'text' && (!textValue || textValue.length < 15)) {
    showToast('Please paste a college notice with at least 15 characters.', 'warning');
    return;
  }

  if (state.activeTab === 'file' && !state.selectedFile) {
    showToast('Please select or drop a notice document (PDF/Image).', 'warning');
    return;
  }

  const analyzeBtn = document.getElementById('analyze-btn');
  const btnText = analyzeBtn.querySelector('.btn-text');
  const btnSpinner = analyzeBtn.querySelector('.btn-spinner');
  const statusBanner = document.getElementById('processing-status');

  // Set loading state
  state.isAnalyzing = true;
  analyzeBtn.disabled = true;
  if (btnText) btnText.textContent = 'Analyzing with Gemini...';
  if (btnSpinner) btnSpinner.classList.remove('hidden');
  if (statusBanner) {
    statusBanner.classList.remove('hidden');
    statusBanner.textContent = 'CampusMate AI is reading notice and extracting intelligence...';
  }

  try {
    const payload = {
      text: state.activeTab === 'text' ? textValue : null,
      file: state.activeTab === 'file' ? state.selectedFile : null,
      language: state.language
    };

    const result = await analyzeNotice(payload);
    state.analysisResult = result;
    state.activeNoticeContext = textValue || result.notice_title;
    state.resetChecklist();

    renderResults(result);
    showToast('Notice analysis complete!', 'success');

    // On mobile screens, scroll down to results smoothly
    const resultsContainer = document.getElementById('results-section');
    if (window.innerWidth < 1024 && resultsContainer) {
      resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
  } catch (err) {
    console.error('Analysis error:', err);
    showToast(err.message || 'Analysis failed. Please check Gemini API configuration.', 'error');
  } finally {
    state.isAnalyzing = false;
    analyzeBtn.disabled = false;
    if (btnText) btnText.textContent = 'Analyze Notice';
    if (btnSpinner) btnSpinner.classList.add('hidden');
    if (statusBanner) statusBanner.classList.add('hidden');
  }
}

function renderResults(data) {
  const resultsContainer = document.getElementById('results-section');
  if (!resultsContainer) return;

  const urgencyColors = {
    urgent: 'badge-urgent',
    upcoming: 'badge-upcoming',
    informational: 'badge-info'
  };
  const urgencyKey = (data.urgency || 'Informational').toLowerCase();
  const urgencyBadgeClass = urgencyColors[urgencyKey] || 'badge-info';

  // Build HTML
  let html = `
    <!-- 1. Header Overview Card -->
    <div class="result-card overview-card">
      <div class="overview-header">
        <div class="title-wrap">
          <span class="badge ${urgencyBadgeClass}">${escapeHtml(data.urgency || 'Notice')}</span>
          <h2 class="notice-main-title">${escapeHtml(data.notice_title || 'College Notice')}</h2>
        </div>
        <button id="copy-summary-btn" class="action-icon-btn" title="Copy Summary">
          <span>📋</span> Copy Summary
        </button>
      </div>

      <div class="meta-pills-row">
        <div class="meta-pill">
          <span class="meta-label">Issuing Authority:</span>
          <span class="meta-value">${escapeHtml(data.issuing_authority || 'Not mentioned')}</span>
        </div>
        <div class="meta-pill">
          <span class="meta-label">Notice Date:</span>
          <span class="meta-value">${escapeHtml(data.notice_date || 'Not mentioned')}</span>
        </div>
        <div class="meta-pill">
          <span class="meta-label">Output Language:</span>
          <span class="meta-value">${escapeHtml(data.language || 'English')}</span>
        </div>
      </div>
    </div>

    <!-- 2. AI Executive Summary Card -->
    <div class="result-card">
      <div class="card-title-row">
        <div class="title-with-icon">
          <span class="card-icon">⚡</span>
          <h3>AI Notice Summary</h3>
        </div>
      </div>
      <ul class="summary-list">
        ${(data.summary || []).map(item => `
          <li class="summary-item">
            <span class="bullet-dot"></span>
            <span>${escapeHtml(item)}</span>
          </li>
        `).join('')}
      </ul>
    </div>

    <!-- 3. Important Dates & Deadlines -->
    <div class="result-card">
      <div class="card-title-row">
        <div class="title-with-icon">
          <span class="card-icon">📅</span>
          <h3>Important Dates & Deadlines</h3>
        </div>
        <span class="card-count-badge">${(data.dates || []).length} events</span>
      </div>

      ${data.dates && data.dates.length > 0 ? `
        <div class="table-responsive">
          <table class="dates-table">
            <thead>
              <tr>
                <th>Event / Milestone</th>
                <th>Date</th>
                <th>Time</th>
                <th>Venue / Location</th>
                <th>Category</th>
              </tr>
            </thead>
            <tbody>
              ${data.dates.map(d => `
                <tr>
                  <td class="table-event-name"><strong>${escapeHtml(d.event)}</strong></td>
                  <td class="table-date">${escapeHtml(d.date)}</td>
                  <td class="table-time ${d.time === 'Not mentioned' ? 'muted' : ''}">${escapeHtml(d.time)}</td>
                  <td class="table-venue ${d.venue === 'Not mentioned' ? 'muted' : ''}">${escapeHtml(d.venue)}</td>
                  <td><span class="category-tag tag-${escapeHtml(d.category || 'event')}">${escapeHtml(d.category || 'event')}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      ` : `
        <div class="empty-substate">
          <p>No specific dates or deadlines were explicitly mentioned in this notice.</p>
        </div>
      `}
    </div>

    <!-- 4. Interactive Student Action Checklist -->
    <div class="result-card">
      <div class="card-title-row">
        <div class="title-with-icon">
          <span class="card-icon">✅</span>
          <h3>Your Action Checklist</h3>
        </div>
        <button id="reset-checklist-btn" class="text-btn">Reset</button>
      </div>

      <div class="progress-wrap">
        <div class="progress-info">
          <span id="checklist-progress-text">0 of ${(data.action_items || []).length} completed</span>
          <span id="checklist-progress-percent">0%</span>
        </div>
        <div class="progress-track">
          <div id="checklist-progress-bar" class="progress-bar-fill" style="width: 0%"></div>
        </div>
      </div>

      ${data.action_items && data.action_items.length > 0 ? `
        <div class="checklist-items-container">
          ${data.action_items.map((item, idx) => `
            <div class="checklist-item ${state.checklistCompleted[`task_${idx}`] ? 'completed' : ''}" data-index="${idx}">
              <input type="checkbox" id="check-${idx}" class="custom-checkbox" ${state.checklistCompleted[`task_${idx}`] ? 'checked' : ''}>
              <label for="check-${idx}" class="checklist-label">
                <span class="checkbox-box"></span>
                <span class="task-text">${escapeHtml(item)}</span>
              </label>
            </div>
          `).join('')}
        </div>
      ` : `
        <div class="empty-substate">
          <p>No explicit action items were found in this notice.</p>
        </div>
      `}
    </div>

    <!-- 5. Key Facts & Missing Information Grid -->
    <div class="two-col-grid">
      <!-- Key Facts -->
      <div class="result-card">
        <div class="card-title-row">
          <div class="title-with-icon">
            <span class="card-icon">📌</span>
            <h3>Key Facts</h3>
          </div>
        </div>
        ${data.important_information && data.important_information.length > 0 ? `
          <div class="facts-grid">
            ${data.important_information.map(info => `
              <div class="fact-card">
                <span class="fact-label">${escapeHtml(info.label)}</span>
                <span class="fact-value">${escapeHtml(info.value)}</span>
              </div>
            `).join('')}
          </div>
        ` : `
          <p class="muted">No additional key facts extracted.</p>
        `}
      </div>

      <!-- Missing Information -->
      <div class="result-card missing-card">
        <div class="card-title-row">
          <div class="title-with-icon">
            <span class="card-icon">⚠️</span>
            <h3>Missing Information</h3>
          </div>
        </div>
        <p class="card-desc-text">Important details absent from the official notice:</p>
        ${data.missing_information && data.missing_information.length > 0 ? `
          <ul class="missing-list">
            ${data.missing_information.map(m => `
              <li class="missing-item">
                <span class="missing-bullet">✕</span>
                <span>${escapeHtml(m)}</span>
              </li>
            `).join('')}
          </ul>
        ` : `
          <p class="text-success">All critical details appear to be covered in this notice.</p>
        `}
      </div>
    </div>

    <!-- 6. Ask Your Notice Panel -->
    <div class="result-card qa-card">
      <div class="card-title-row">
        <div class="title-with-icon">
          <span class="card-icon">💬</span>
          <h3>Ask Your Notice</h3>
        </div>
      </div>
      <p class="card-desc-text">Ask any question strictly based on the notice you just analyzed.</p>

      <!-- Suggested Question Chips -->
      <div class="suggested-chips-row">
        <span class="chips-label">Suggestions:</span>
        <button class="chip-btn" data-question="When is the examination or event?">When is the exam?</button>
        <button class="chip-btn" data-question="What documents should I carry?">What documents needed?</button>
        <button class="chip-btn" data-question="What is the submission deadline?">Submission deadline?</button>
        <button class="chip-btn" data-question="Where is the venue located?">Where is the venue?</button>
        <button class="chip-btn" data-question="Is attendance compulsory?">Attendance mandatory?</button>
      </div>

      <!-- Question Input -->
      <form id="ask-notice-form" class="qa-input-form">
        <input type="text" id="qa-question-input" class="qa-input" placeholder="e.g., What documents do I need to carry?" required maxlength="500">
        <button type="submit" id="ask-btn" class="qa-submit-btn">
          <span class="btn-text">Ask</span>
        </button>
      </form>

      <!-- QA Conversation Stream -->
      <div id="qa-thread" class="qa-thread"></div>
    </div>
  `;

  resultsContainer.innerHTML = html;

  // Bind interactive elements inside newly rendered HTML
  bindRenderedEvents(data);
}

function bindRenderedEvents(data) {
  // Copy summary
  const copyBtn = document.getElementById('copy-summary-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const summaryText = (data.summary || []).join('\n• ');
      const fullCopy = `${data.notice_title}\nIssuing Authority: ${data.issuing_authority}\n\nSummary:\n• ${summaryText}`;
      copyToClipboard(fullCopy, 'Notice summary copied to clipboard!');
    });
  }

  // Checklist interactions
  const checklistItems = document.querySelectorAll('.checklist-item');
  checklistItems.forEach(item => {
    const idx = item.dataset.index;
    const checkbox = item.querySelector('.custom-checkbox');

    const toggle = () => {
      state.toggleChecklist(idx);
      item.classList.toggle('completed', state.checklistCompleted[`task_${idx}`]);
      checkbox.checked = !!state.checklistCompleted[`task_${idx}`];
      updateChecklistProgress(data.action_items.length);
    };

    checkbox.addEventListener('change', toggle);
  });

  const resetBtn = document.getElementById('reset-checklist-btn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      state.resetChecklist();
      checklistItems.forEach(item => {
        item.classList.remove('completed');
        const cb = item.querySelector('.custom-checkbox');
        if (cb) cb.checked = false;
      });
      updateChecklistProgress(data.action_items.length);
      showToast('Checklist reset', 'info');
    });
  }

  updateChecklistProgress(data.action_items ? data.action_items.length : 0);

  // Suggested questions chips
  const chips = document.querySelectorAll('.chip-btn');
  const qaInput = document.getElementById('qa-question-input');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      if (qaInput) {
        qaInput.value = chip.dataset.question;
        qaInput.focus();
      }
    });
  });

  // Ask form submit
  const qaForm = document.getElementById('ask-notice-form');
  if (qaForm) {
    qaForm.addEventListener('submit', handleAskSubmit);
  }
}

function updateChecklistProgress(totalCount) {
  if (totalCount === 0) return;
  let completed = 0;
  for (let i = 0; i < totalCount; i++) {
    if (state.checklistCompleted[`task_${i}`]) completed++;
  }
  const pct = Math.round((completed / totalCount) * 100);

  const progText = document.getElementById('checklist-progress-text');
  const progPct = document.getElementById('checklist-progress-percent');
  const progBar = document.getElementById('checklist-progress-bar');

  if (progText) progText.textContent = `${completed} of ${totalCount} completed`;
  if (progPct) progPct.textContent = `${pct}%`;
  if (progBar) progBar.style.width = `${pct}%`;
}

async function handleAskSubmit(e) {
  e.preventDefault();
  const qaInput = document.getElementById('qa-question-input');
  if (!qaInput) return;
  const question = qaInput.value.trim();
  if (!question) return;

  if (!state.activeNoticeContext) {
    showToast('Please analyze a notice first before asking questions.', 'warning');
    return;
  }

  const askBtn = document.getElementById('ask-btn');
  const btnText = askBtn ? askBtn.querySelector('.btn-text') : null;
  if (askBtn) askBtn.disabled = true;
  if (btnText) btnText.textContent = 'Thinking...';

  try {
    const res = await askNoticeQuestion({
      noticeText: state.activeNoticeContext,
      question: question,
      language: state.language
    });

    state.addQA(question, res.answer, res.found_in_notice);
    renderQAThread();
    qaInput.value = '';
  } catch (err) {
    console.error('QA Error:', err);
    showToast(err.message || 'Failed to answer question.', 'error');
  } finally {
    if (askBtn) askBtn.disabled = false;
    if (btnText) btnText.textContent = 'Ask';
  }
}

function renderQAThread() {
  const thread = document.getElementById('qa-thread');
  if (!thread) return;

  thread.innerHTML = state.qaHistory.map(item => `
    <div class="qa-item">
      <div class="qa-question-bubble">
        <span class="user-avatar">👤 Student:</span>
        <span class="question-text">${escapeHtml(item.question)}</span>
        <span class="qa-time">${item.timestamp}</span>
      </div>
      <div class="qa-answer-bubble">
        <div class="answer-badge-row">
          <span class="badge ${item.foundInNotice ? 'badge-found' : 'badge-not-found'}">
            ${item.foundInNotice ? '✓ Grounded in Notice' : '⚠️ Not Mentioned in Notice'}
          </span>
          <span class="ai-avatar">✨ CampusMate AI</span>
        </div>
        <p class="answer-text">${escapeHtml(item.answer)}</p>
      </div>
    </div>
  `).join('');
}

function renderEmptyState() {
  const container = document.getElementById('results-section');
  if (!container) return;

  container.innerHTML = `
    <div class="empty-state-card">
      <div class="empty-illustration">
        <img src="/assets/logo.svg" alt="CampusMate AI" class="empty-logo">
      </div>
      <h3 class="empty-title">Ready to Understand Your Notice</h3>
      <p class="empty-desc">
        Paste any college circular, exam timetable, or upload a document on the left, then click <strong>Analyze Notice</strong>.
      </p>
      <div class="features-highlight-grid">
        <div class="feature-badge">⚡ 3-Bullet Summary</div>
        <div class="feature-badge">📅 Dates & Deadlines</div>
        <div class="feature-badge">✅ Action Checklist</div>
        <div class="feature-badge">💬 Grounded Q&A</div>
        <div class="feature-badge">🌐 English • हिंदी • Hinglish</div>
      </div>
    </div>
  `;
}
