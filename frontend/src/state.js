/**
 * CampusMate AI - State Management
 * Holds client-side state, checklist persistence, and UI flags.
 */

const STORAGE_KEYS = {
  THEME: 'campusmate_theme',
  CHECKLIST: 'campusmate_checklist_state',
};

export const state = {
  theme: localStorage.getItem(STORAGE_KEYS.THEME) || 'dark',
  language: 'English',
  activeTab: 'text', // 'text' | 'file'
  rawText: '',
  selectedFile: null,
  isAnalyzing: false,
  isAsking: false,
  analysisResult: null,
  activeNoticeContext: '', // Stored text for Ask Your Notice
  checklistCompleted: JSON.parse(localStorage.getItem(STORAGE_KEYS.CHECKLIST) || '{}'),
  qaHistory: [],

  setTheme(newTheme) {
    this.theme = newTheme;
    localStorage.setItem(STORAGE_KEYS.THEME, newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  },

  setLanguage(lang) {
    this.language = lang;
  },

  setActiveTab(tab) {
    this.activeTab = tab;
  },

  toggleChecklist(index) {
    const key = `task_${index}`;
    this.checklistCompleted[key] = !this.checklistCompleted[key];
    localStorage.setItem(STORAGE_KEYS.CHECKLIST, JSON.stringify(this.checklistCompleted));
  },

  resetChecklist() {
    this.checklistCompleted = {};
    localStorage.removeItem(STORAGE_KEYS.CHECKLIST);
  },

  addQA(question, answer, foundInNotice) {
    this.qaHistory.unshift({
      question,
      answer,
      foundInNotice,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    });
  },

  clearAll() {
    this.rawText = '';
    this.selectedFile = null;
    this.analysisResult = null;
    this.activeNoticeContext = '';
    this.qaHistory = [];
    this.resetChecklist();
  }
};
