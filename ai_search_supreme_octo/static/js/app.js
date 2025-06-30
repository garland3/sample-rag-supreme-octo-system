// RAG Research System - Professional UI JavaScript

class RAGInterface {
    constructor() {
        this.socket = null;
        this.md = null;
        this.currentFile = null;
        this.initializeElements();
        this.initializeMarkdown();
        this.setupEventListeners();
        this.connectWebSocket();
    }

    initializeElements() {
        this.questionInput = document.getElementById('questionInput');
        this.askButton = document.getElementById('askButton');
        this.fileInput = document.getElementById('fileInput');
        this.fileUploadBtn = document.getElementById('fileUploadBtn');
        this.filePreview = document.getElementById('filePreview');
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.resultsSection = document.getElementById('resultsSection');
        this.numSearches = document.getElementById('numSearches');
        this.numRewordings = document.getElementById('numRewordings');
    }

    initializeMarkdown() {
        // Initialize markdown-it with syntax highlighting
        this.md = window.markdownit({
            html: true,
            linkify: true,
            typographer: true,
            highlight: function (str, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        const highlighted = hljs.highlight(str, { language: lang }).value;
                        return `<pre class="hljs"><code class="language-${lang}">${highlighted}<button class="copy-btn" onclick="ragInterface.copyCode(this)"><i class="fas fa-copy"></i> Copy</button></code></pre>`;
                    } catch (__) {}
                }
                return `<pre class="hljs"><code>${this.md.utils.escapeHtml(str)}<button class="copy-btn" onclick="ragInterface.copyCode(this)"><i class="fas fa-copy"></i> Copy</button></code></pre>`;
            }
        });
    }

    setupEventListeners() {
        this.askButton.addEventListener('click', () => this.askQuestion());
        this.questionInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                this.askQuestion();
            }
        });

        this.fileUploadBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (event) => this.handleFileUpload(event));

        // Auto-resize textarea
        this.questionInput.addEventListener('input', () => {
            this.questionInput.style.height = 'auto';
            this.questionInput.style.height = Math.min(this.questionInput.scrollHeight, 200) + 'px';
        });
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.socket = new WebSocket(`${protocol}//${window.location.host}/ws`);
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
                case 'progress':
                    this.updateProgress(data.content);
                    break;
                case 'result':
                    this.showResult(data.content);
                    break;
                case 'error':
                    this.showError(data.content);
                    break;
            }
        };
        
        this.socket.onclose = () => {
            setTimeout(() => this.connectWebSocket(), 1000);
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showError('Connection error. Please refresh the page.');
        };
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Check file size (limit to 1MB)
        if (file.size > 1024 * 1024) {
            alert('File size must be less than 1MB');
            return;
        }

        // Check file type
        const allowedTypes = ['text/plain', 'text/markdown', 'application/json', 'text/csv', 'text/xml'];
        const fileExtensions = ['.txt', '.md', '.json', '.csv', '.xml', '.py', '.js', '.html', '.css'];
        
        const isAllowedType = allowedTypes.includes(file.type) || 
                            fileExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

        if (!isAllowedType) {
            alert('Please upload a text file (.txt, .md, .json, .csv, .xml, .py, .js, .html, .css)');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            this.currentFile = {
                name: file.name,
                content: e.target.result,
                size: file.size
            };
            this.showFilePreview();
        };
        reader.readAsText(file);
    }

    showFilePreview() {
        if (!this.currentFile) return;

        const sizeInKB = (this.currentFile.size / 1024).toFixed(1);
        const preview = this.currentFile.content.length > 500 
            ? this.currentFile.content.substring(0, 500) + '...' 
            : this.currentFile.content;

        this.filePreview.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file-text"></i>
                <span><strong>${this.currentFile.name}</strong> (${sizeInKB} KB)</span>
                <button class="remove-file" onclick="ragInterface.removeFile()">
                    <i class="fas fa-times"></i> Remove
                </button>
            </div>
            <div class="file-content">${preview}</div>
        `;
        this.filePreview.classList.add('show');
    }

    removeFile() {
        this.currentFile = null;
        this.filePreview.classList.remove('show');
        this.fileInput.value = '';
    }

    updateProgress(progress) {
        this.progressSection.style.display = 'block';
        
        // Add some visual variety based on the status
        const statusEmojis = {
            'generating_queries': '🤖',
            'queries_generated': '✅',
            'searching': '🔍',
            'search_complete': '📄',
            'searches_complete': '✅',
            'analyzing': '🧠',
            'analyzing_query': '🔬',
            'processing_sources': '📊',
            'analysis_complete': '✅',
            'all_analysis_complete': '✅',
            'synthesizing': '🔗',
            'compiling': '📝',
            'finalizing': '✨',
            'completed': '🎉'
        };
        
        if (progress.step && progress.total) {
            const percentage = (progress.step / progress.total) * 100;
            this.progressFill.style.width = `${percentage}%`;
            
            // Add a subtle animation pulse for active states
            const activeStates = ['searching', 'analyzing_query', 'processing_sources', 'compiling'];
            const isActive = activeStates.includes(progress.status);
            
            this.progressText.innerHTML = `
                <div class="progress-spinner ${isActive ? 'active' : ''}"></div>
                <span class="progress-step">Step ${progress.step}/${progress.total}</span>
                <span class="progress-message">${progress.message}</span>
            `;
            
            // Add a live activity log for detailed steps
            this.addProgressLog(progress.message, progress.status);
            
        } else {
            this.progressText.innerHTML = `
                <div class="progress-spinner"></div>
                <span class="progress-message">${progress.message || 'Processing...'}</span>
            `;
        }
    }
    
    addProgressLog(message, status) {
        // Create or update progress log
        let progressLog = document.getElementById('progressLog');
        if (!progressLog) {
            progressLog = document.createElement('div');
            progressLog.id = 'progressLog';
            progressLog.className = 'progress-log';
            progressLog.innerHTML = '<h4><i class="fas fa-list"></i> Activity Log</h4><div class="log-items"></div>';
            this.progressSection.appendChild(progressLog);
        }
        
        const logItems = progressLog.querySelector('.log-items');
        const logItem = document.createElement('div');
        logItem.className = 'log-item';
        logItem.innerHTML = `
            <span class="log-time">${new Date().toLocaleTimeString()}</span>
            <span class="log-message">${message}</span>
        `;
        
        // Add to top of log and limit to last 10 items
        logItems.insertBefore(logItem, logItems.firstChild);
        while (logItems.children.length > 10) {
            logItems.removeChild(logItems.lastChild);
        }
        
        // Auto scroll to show latest
        logItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    showResult(result) {
        this.progressSection.style.display = 'none';
        this.askButton.disabled = false;
        this.askButton.innerHTML = '<i class="fas fa-search"></i> Ask Question';
        
        // Clear progress log
        const progressLog = document.getElementById('progressLog');
        if (progressLog) {
            progressLog.remove();
        }
        
        // Process the answer with markdown
        const processedAnswer = this.md.render(result.answer);
        
        // Generate evaluation metrics display if available
        let evaluationHtml = '';
        if (result.evaluation_result) {
            const eval_result = result.evaluation_result;
            const metrics = eval_result.metrics;
            
            evaluationHtml = `
                <div class="evaluation-section">
                    <h3><i class="fas fa-chart-bar"></i> Quality Assessment</h3>
                    <div class="quality-score">
                        <div class="overall-score ${this.getScoreClass(eval_result.overall_score)}">
                            <span class="score-value">${eval_result.overall_score.toFixed(1)}</span>
                            <span class="score-label">Overall Score</span>
                        </div>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric">
                            <label>Accuracy</label>
                            <div class="metric-bar">
                                <div class="metric-fill" style="width: ${metrics.accuracy * 10}%"></div>
                                <span class="metric-value">${metrics.accuracy}/10</span>
                            </div>
                        </div>
                        <div class="metric">
                            <label>Completeness</label>
                            <div class="metric-bar">
                                <div class="metric-fill" style="width: ${metrics.completeness * 10}%"></div>
                                <span class="metric-value">${metrics.completeness}/10</span>
                            </div>
                        </div>
                        <div class="metric">
                            <label>Relevance</label>
                            <div class="metric-bar">
                                <div class="metric-fill" style="width: ${metrics.relevance * 10}%"></div>
                                <span class="metric-value">${metrics.relevance}/10</span>
                            </div>
                        </div>
                        <div class="metric">
                            <label>Clarity</label>
                            <div class="metric-bar">
                                <div class="metric-fill" style="width: ${metrics.clarity * 10}%"></div>
                                <span class="metric-value">${metrics.clarity}/10</span>
                            </div>
                        </div>
                        <div class="metric">
                            <label>Confidence</label>
                            <div class="metric-bar">
                                <div class="metric-fill" style="width: ${metrics.confidence * 10}%"></div>
                                <span class="metric-value">${metrics.confidence}/10</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="evaluation-reasoning">
                        <h4><i class="fas fa-brain"></i> Evaluation Reasoning</h4>
                        <p>${eval_result.reasoning}</p>
                    </div>
                </div>
            `;
        }
        
        const resultHtml = `
            <div class="result-card">
                <div class="result-answer">
                    <h2><i class="fas fa-lightbulb"></i> Answer</h2>
                    ${processedAnswer}
                </div>
                
                <div class="research-steps">
                    <h3><i class="fas fa-search"></i> Research Queries</h3>
                    ${result.research_steps.map((step, index) => `
                        <div class="research-step">
                            <div class="step-header" onclick="ragInterface.toggleStep(this)">
                                <span>
                                    <span class="status-indicator status-completed"></span>
                                    Query ${step.step_number}: ${step.query}
                                </span>
                                <span class="step-arrow"><i class="fas fa-chevron-down"></i></span>
                            </div>
                            <div class="step-content">
                                <div class="step-content-inner">
                                    ${this.md.render(step.analysis)}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                ${evaluationHtml}
                
                <div class="session-info">
                    <div>
                        <i class="fas fa-fingerprint"></i>
                        Session ID: <code>${result.session_id}</code>
                    </div>
                    <div class="session-actions">
                        <button class="session-btn" onclick="ragInterface.downloadSession('${result.session_id}')">
                            <i class="fas fa-download"></i> Download
                        </button>
                        <button class="session-btn" onclick="ragInterface.shareSession('${result.session_id}')">
                            <i class="fas fa-share"></i> Share
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        this.resultsSection.innerHTML = resultHtml;
        
        // Initialize syntax highlighting for any code blocks
        this.resultsSection.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
        
        // Smooth scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    getScoreClass(score) {
        if (score >= 8) return 'score-excellent';
        if (score >= 7) return 'score-good';
        if (score >= 5) return 'score-fair';
        return 'score-poor';
    }

    showError(error) {
        this.progressSection.style.display = 'none';
        this.askButton.disabled = false;
        this.askButton.innerHTML = '<i class="fas fa-search"></i> Ask Question';
        
        // Clear progress log
        const progressLog = document.getElementById('progressLog');
        if (progressLog) {
            progressLog.remove();
        }
        
        this.resultsSection.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <div>
                    <strong>Error:</strong> ${error}
                </div>
            </div>
        `;
    }

    toggleStep(header) {
        const content = header.nextElementSibling;
        const arrow = header.querySelector('.step-arrow i');
        const isExpanded = content.classList.contains('expanded');
        
        if (isExpanded) {
            content.classList.remove('expanded');
            arrow.className = 'fas fa-chevron-down';
            header.classList.remove('active');
        } else {
            content.classList.add('expanded');
            arrow.className = 'fas fa-chevron-up';
            header.classList.add('active');
        }
    }

    copyCode(button) {
        const code = button.parentElement.textContent.replace('Copy', '').trim();
        navigator.clipboard.writeText(code).then(() => {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i> Copied!';
            button.classList.add('copied');
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.classList.remove('copied');
            }, 2000);
        }).catch(() => {
            alert('Failed to copy code. Please select and copy manually.');
        });
    }

    askQuestion() {
        let question = this.questionInput.value.trim();
        if (!question) return;

        // Append file content if a file is uploaded
        if (this.currentFile) {
            question += `\n\n[File: ${this.currentFile.name}]\n${this.currentFile.content}`;
        }

        this.askButton.disabled = true;
        this.askButton.innerHTML = '<div class="progress-spinner"></div> Researching...';
        this.progressSection.style.display = 'block';
        this.progressFill.style.width = '0%';
        this.progressText.innerHTML = `
            <div class="progress-spinner"></div>
            Starting research...
        `;
        this.resultsSection.innerHTML = '';

        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'query',
                content: question,
                settings: {
                    num_searches: parseInt(this.numSearches.value) || 3,
                    num_rewordings: parseInt(this.numRewordings.value) || 3
                }
            }));
        } else {
            this.showError('WebSocket connection not available. Please refresh the page.');
        }
    }

    downloadSession(sessionId) {
        // Create a downloadable text file with the session results
        const content = this.resultsSection.textContent;
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `rag-session-${sessionId}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    shareSession(sessionId) {
        // Copy session URL to clipboard
        const url = `${window.location.origin}/?session=${sessionId}`;
        navigator.clipboard.writeText(url).then(() => {
            alert('Session URL copied to clipboard!');
        }).catch(() => {
            prompt('Copy this URL to share the session:', url);
        });
    }

    // Utility method to format text with markdown
    formatText(text) {
        return this.md.render(text);
    }
}

// Initialize the interface when the page loads
let ragInterface;
document.addEventListener('DOMContentLoaded', () => {
    ragInterface = new RAGInterface();
    // Make ragInterface globally available for onclick handlers
    window.ragInterface = ragInterface;
});
