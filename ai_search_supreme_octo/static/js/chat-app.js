// RAG Research System - Chat Interface JavaScript

class ChatInterface {
    constructor() {
        this.socket = null;
        this.uploadedFile = null;
        this.isResearching = false;
        this.initializeElements();
        this.setupEventListeners();
        this.initializeSplitter();
        this.connectWebSocket();
        this.updateSettingsDisplay();
        this.addWelcomeMessage();
    }

    initializeElements() {
        this.messages = document.getElementById('messages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.output = document.getElementById('output');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.fileInput = document.getElementById('fileInput');
        this.fileNameDisplay = document.getElementById('fileNameDisplay');
        this.clearFileButton = document.getElementById('clearFileButton');
        this.numSearches = document.getElementById('numSearches');
        this.numRewordings = document.getElementById('numRewordings');
        this.exportButton = document.getElementById('exportButton');
    }

    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        this.clearFileButton.addEventListener('click', () => this.clearFile());
        
        this.numSearches.addEventListener('input', () => this.updateSettingsDisplay());
        this.numRewordings.addEventListener('input', () => this.updateSettingsDisplay());
        
        this.exportButton.addEventListener('click', () => this.exportResults());
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
    }

    initializeSplitter() {
        const splitter = document.getElementById('splitter');
        const leftPanel = document.querySelector('.left-panel');
        const rightPanel = document.querySelector('.right-panel');
        const container = document.querySelector('.container');
        
        let isDragging = false;
        let startX = 0;
        let startLeftWidth = 0;
        let startRightWidth = 0;

        splitter.addEventListener('mousedown', (e) => {
            if (window.innerWidth <= 768) return;
            isDragging = true;
            startX = e.clientX;
            const containerRect = container.getBoundingClientRect();
            const leftRect = leftPanel.getBoundingClientRect();
            const rightRect = rightPanel.getBoundingClientRect();
            startLeftWidth = leftRect.width;
            startRightWidth = rightRect.width;
            splitter.classList.add('dragging');
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const deltaX = e.clientX - startX;
            const containerRect = container.getBoundingClientRect();
            const totalWidth = containerRect.width - 20 - 10;
            let newLeftWidth = startLeftWidth + deltaX;
            let newRightWidth = startRightWidth - deltaX;
            const minWidth = 300;
            
            if (newLeftWidth < minWidth) {
                newLeftWidth = minWidth;
                newRightWidth = totalWidth - minWidth;
            } else if (newRightWidth < minWidth) {
                newRightWidth = minWidth;
                newLeftWidth = totalWidth - minWidth;
            }
            
            const leftPercent = (newLeftWidth / totalWidth) * 100;
            const rightPercent = (newRightWidth / totalWidth) * 100;
            leftPanel.style.flex = `0 0 ${leftPercent}%`;
            rightPanel.style.flex = `0 0 ${rightPercent}%`;
        });

        document.addEventListener('mouseup', () => {
            if (!isDragging) return;
            isDragging = false;
            splitter.classList.remove('dragging');
        });
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.socket = new WebSocket(`${protocol}//${window.location.host}/ws`);
        
        this.socket.onopen = () => {
            this.connectionStatus.textContent = 'Connected';
            this.connectionStatus.className = 'connection-status connected';
        };
        
        this.socket.onclose = () => {
            this.connectionStatus.textContent = 'Disconnected';
            this.connectionStatus.className = 'connection-status disconnected';
            setTimeout(() => this.connectWebSocket(), 3000);
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.connectionStatus.textContent = 'Error';
            this.connectionStatus.className = 'connection-status disconnected';
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
    }

    handleMessage(data) {
        switch (data.type) {
            case 'progress':
                this.addMessage('progress', data.content.message || 'Processing...');
                break;
            case 'research_step':
                this.addMessage('research_step', `🔍 ${data.content}`);
                break;
            case 'search_result':
                this.addMessage('search_result', `📄 ${data.content}`);
                break;
            case 'thinking':
                this.addMessage('thinking', data.content);
                break;
            case 'result':
                this.showFinalResult(data.content);
                this.addMessage('final_answer', 'Research completed! See results in the right panel.');
                this.isResearching = false;
                this.sendButton.disabled = false;
                this.sendButton.innerHTML = '<i class="fas fa-search"></i> Research';
                break;
            case 'error':
                this.addMessage('error', data.content);
                this.isResearching = false;
                this.sendButton.disabled = false;
                this.sendButton.innerHTML = '<i class="fas fa-search"></i> Research';
                break;
            default:
                this.addMessage('system', data.content || 'Unknown message type');
        }
    }

    addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'markdown-content';
        
        // Process markdown content
        const markdownInput = content || '';
        try {
            const unsafeHtml = window.markdownit().render(markdownInput);
            contentWrapper.innerHTML = DOMPurify.sanitize(unsafeHtml);
        } catch (e) {
            contentWrapper.textContent = markdownInput;
        }
        
        messageDiv.appendChild(contentWrapper);
        this.messages.appendChild(messageDiv);
        
        // Syntax highlighting
        contentWrapper.querySelectorAll('pre code').forEach((block) => {
            if (window.hljs) hljs.highlightElement(block);
        });
        
        // Add copy functionality
        this.addCopyButtons(contentWrapper);
        
        // Auto-scroll
        this.messages.scrollTop = this.messages.scrollHeight;
        
        // Limit messages (keep last 100)
        while (this.messages.children.length > 100) {
            this.messages.removeChild(this.messages.firstChild);
        }
    }

    addCopyButtons(element) {
        const codeBlocks = element.querySelectorAll('pre');
        codeBlocks.forEach(block => {
            const code = block.querySelector('code');
            const button = document.createElement('button');
            button.className = 'copy-button';
            button.textContent = 'Copy';
            
            button.addEventListener('click', () => {
                navigator.clipboard.writeText(code.innerText).then(() => {
                    button.textContent = 'Copied!';
                    button.classList.add('copied');
                    setTimeout(() => {
                        button.textContent = 'Copy';
                        button.classList.remove('copied');
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy:', err);
                    button.textContent = 'Error';
                });
            });
            
            block.appendChild(button);
        });
    }

    showFinalResult(result) {
        this.output.className = 'markdown-content';
        
        try {
            const markdownInput = result.answer || 'No answer provided';
            const unsafeHtml = window.markdownit().render(markdownInput);
            this.output.innerHTML = DOMPurify.sanitize(unsafeHtml);
        } catch (e) {
            this.output.textContent = result.answer || 'No answer provided';
        }
        
        // Apply syntax highlighting
        this.output.querySelectorAll('pre code').forEach((block) => {
            if (window.hljs) hljs.highlightElement(block);
        });
        
        // Add copy functionality
        this.addCopyButtons(this.output);
    }

    sendMessage() {
        if (this.isResearching || !this.socket || this.socket.readyState !== WebSocket.OPEN) return;
        
        let message = this.messageInput.value.trim();
        if (this.uploadedFile) {
            message = `Here is the content of the uploaded file:\n\n\`\`\`\n${this.uploadedFile}\n\`\`\`\n\n${message}`;
        }
        
        if (!message) return;
        
        this.isResearching = true;
        this.sendButton.disabled = true;
        this.sendButton.innerHTML = '<div class="progress-spinner"></div> Researching...';
        this.output.textContent = 'Research started... waiting for results.';
        this.output.className = 'status';
        
        // Clear messages for new research
        this.messages.innerHTML = '';
        
        this.socket.send(JSON.stringify({
            type: 'query',
            content: message,
            settings: {
                num_searches: parseInt(this.numSearches.value) || 3,
                num_rewordings: parseInt(this.numRewordings.value) || 3
            }
        }));
        
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.clearFile();
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            if (file.size > 1024 * 1024) {
                alert('File size must be less than 1MB');
                return;
            }
            
            this.fileNameDisplay.textContent = file.name;
            this.clearFileButton.style.display = 'inline-block';
            
            const reader = new FileReader();
            reader.onload = (e) => {
                this.uploadedFile = e.target.result;
            };
            reader.onerror = () => {
                this.fileNameDisplay.textContent = 'Error reading file.';
                this.uploadedFile = null;
            };
            reader.readAsText(file);
        }
    }

    clearFile() {
        this.fileInput.value = '';
        this.fileNameDisplay.textContent = 'No file selected';
        this.clearFileButton.style.display = 'none';
        this.uploadedFile = null;
    }

    updateSettingsDisplay() {
        document.getElementById('searchesValue').textContent = this.numSearches.value;
        document.getElementById('rewordingsValue').textContent = this.numRewordings.value;
    }

    exportResults() {
        const content = this.output.textContent || 'No results to export';
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `rag-research-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    addWelcomeMessage() {
        this.addMessage('system', 'Welcome! Ask any research question to get started. You can upload files to include their content in your research context.');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});