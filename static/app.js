/**
 * Qwen3-TTS Web GUI - Frontend Logic
 */

(function () {
    'use strict';

    // DOM Elements
    const textInput = document.getElementById('text-input');
    const speakerSelect = document.getElementById('speaker-select');
    const languageSelect = document.getElementById('language-select');
    const instructInput = document.getElementById('instruct-input');
    const btnGenerate = document.getElementById('btn-generate');
    const btnDownload = document.getElementById('btn-download');
    const btnStop = document.getElementById('btn-stop');
    const btnClearHistory = document.getElementById('btn-clear-history');
    const btnCopyLink = document.getElementById('btn-copy-link');
    const audioPlayer = document.getElementById('audio-player');
    const charCount = document.getElementById('char-count');
    const speakerDesc = document.getElementById('speaker-desc');
    const loadingOverlay = document.getElementById('loading-overlay');
    const audioCard = document.getElementById('audio-card');
    const historyCard = document.getElementById('history-card');
    const historyList = document.getElementById('history-list');
    const audioInfo = document.getElementById('audio-info');
    const btnGenerateText = document.getElementById('btn-generate-text');
    const outputSize = document.getElementById('output-size');

    // State
    let currentAudioBlob = null;
    let currentAudioUrl = null;
    let isGenerating = false;
    let abortController = null;
    let serverHistory = [];
    let progressInterval = null;
    let statusInterval = null;

    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        init();
    });

    function init() {
        checkStatus();
        setupEventListeners();
        loadServerHistory();
        if (speakerDesc) {
            speakerDesc.textContent = speakerSelect.options[speakerSelect.selectedIndex].dataset.desc || '';
        }
        updateOutputSize();
    }

    function checkStatus() {
        // Status card removed
    }

    function setStatus(type, text, detail) {
        // Status card removed - no-op
    }

    function setupEventListeners() {
        // Character count
        textInput.addEventListener('input', () => {
            if (charCount) {
                charCount.textContent = `${textInput.value.length} characters`;
            }
        });

        // Speaker description
        speakerSelect.addEventListener('change', () => {
            if (speakerDesc) {
                const opt = speakerSelect.options[speakerSelect.selectedIndex];
                speakerDesc.textContent = opt.dataset.desc || '';
            }
        });

        // Generate
        btnGenerate.addEventListener('click', generate);

        // Download
        btnDownload.addEventListener('click', downloadAudio);

        // Stop
        btnStop.addEventListener('click', stopGeneration);

        // Clear history
        btnClearHistory.addEventListener('click', clearHistory);

        // Copy link
        btnCopyLink.addEventListener('click', copyLink);

        // Enter key shortcut
        textInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                generate();
            }
        });
    }

    // ====================
    // AUDIO GENERATION
    // ====================

    async function generate() {
        const text = textInput.value.trim();
        if (!text) {
            textInput.classList.add('is-invalid');
            setTimeout(() => textInput.classList.remove('is-invalid'), 2000);
            return;
        }

        if (isGenerating) return;
        isGenerating = true;

        // UI: Loading state
        loadingOverlay.classList.remove('d-none');
        audioCard.classList.add('d-none');
        btnDownload.classList.add('d-none');
        btnStop.classList.remove('d-none');
        btnGenerate.disabled = true;
        if (btnGenerateText) btnGenerateText.textContent = 'Generating...';
        setStatus('warning', 'Generating Audio', 'Please wait');

        // Start Progress & Status Animation
        startProgressAnimation();

        abortController = new AbortController();

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    speaker: speakerSelect.value,
                    language: languageSelect.value,
                    instruct: instructInput.value.trim(),
                }),
                signal: abortController.signal,
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(err.error || 'Generation failed');
            }

            const data = await response.json();

            // Decode base64 WAV
            const binaryStr = atob(data.audio_wav);
            const bytes = new Uint8Array(binaryStr.length);
            for (let i = 0; i < binaryStr.length; i++) {
                bytes[i] = binaryStr.charCodeAt(i);
            }

            // Create blob
            currentAudioBlob = new Blob([bytes], { type: 'audio/wav' });
            if (currentAudioUrl) {
                URL.revokeObjectURL(currentAudioUrl);
            }
            currentAudioUrl = URL.createObjectURL(currentAudioBlob);

            // Set audio source
            audioPlayer.src = currentAudioUrl;
            audioCard.classList.remove('d-none');
            audioCard.classList.add('fade-in');
            btnDownload.classList.remove('d-none');

            // Audio info
            const duration = audioPlayer.duration || 0;
            audioInfo.textContent = `${(duration).toFixed(1)}s • ${data.sample_rate}Hz • WAV`;

            // Auto play
            audioPlayer.play();

            setStatus('success', 'Done', 'Audio has been generated');

            // Live history update (non-blocking)
            if (data.filename) {
                addToHistory(text, speakerSelect.value, '', data.filename);
                renderHistory();
                updateOutputSize();
            }

            // Stop Progress Animation
            completeProgressAnimation();

        } catch (err) {
            if (err.name === 'AbortError') {
                setStatus('warning', 'Cancelled', 'Generation was stopped');
            } else {
                setStatus('danger', 'Error', err.message);
                console.error(err);
            }
        } finally {
            isGenerating = false;
            abortController = null;
            loadingOverlay.classList.add('d-none');
            btnGenerate.disabled = false;
            if (btnGenerateText) btnGenerateText.textContent = 'Generate';
            btnStop.classList.add('d-none');
            
            // Stop Progress Animation
            completeProgressAnimation();
        }
    }

    function startProgressAnimation() {
        const progressBar = document.getElementById('loading-progress-bar');
        const container = document.getElementById('loading-progress-container');
        const statusText = document.getElementById('loading-status-text');
        const detailText = document.getElementById('loading-detail');
        
        container.classList.remove('d-none');
        progressBar.style.width = '0%';
        progressBar.textContent = '';
        
        let width = 0;
        // Simulate progress over 15 seconds (fills up to 90%)
        const totalDuration = 15000;
        const intervalTime = 100;
        const steps = totalDuration / intervalTime;
        const increment = 90 / steps;
        
        progressInterval = setInterval(() => {
            if (width < 90) {
                width += increment;
                progressBar.style.width = width + '%';
            }
        }, intervalTime);

        // Rotate status messages
        const messages = [
            { t: 'Generating audio...', d: 'Model is processing the text' },
            { t: 'Extracting features...', d: 'Encoder is computing input features' },
            { t: 'Synthesizing speech...', d: 'Decoder is reconstructing audio' },
            { t: 'Almost done...', d: 'Finalizing output' }
        ];
        
        let msgIndex = 0;
        statusText.textContent = messages[0].t;
        detailText.textContent = messages[0].d;
        
        statusInterval = setInterval(() => {
            msgIndex = (msgIndex + 1) % messages.length;
            statusText.textContent = messages[msgIndex].t;
            detailText.textContent = messages[msgIndex].d;
        }, 4000);
    }

    function completeProgressAnimation() {
        const progressBar = document.getElementById('loading-progress-bar');
        const container = document.getElementById('loading-progress-container');
        
        clearInterval(progressInterval);
        clearInterval(statusInterval);
        
        // Jump to 100%
        progressBar.style.width = '100%';
        progressBar.classList.remove('bg-primary');
        progressBar.classList.add('bg-success');
        
        setTimeout(() => {
            container.classList.add('d-none');
            progressBar.classList.remove('bg-success');
            progressBar.classList.add('bg-primary');
            progressBar.style.width = '0%';
        }, 800);
    }

    function stopGeneration() {
        if (abortController) {
            abortController.abort();
        }
    }

    function downloadAudio() {
        if (!currentAudioUrl) return;

        // Get filename from URL
        const urlParts = currentAudioUrl.split('/');
        const filename = urlParts[urlParts.length - 1];

        // Create download link
        const a = document.createElement('a');
        a.href = `/play/${filename}`;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    function addToHistory(text, speaker, desc, filename) {
        // Add to server history
        serverHistory.unshift({
            id: Date.now(),
            text: text.substring(0, 100) + (text.length > 100 ? '...' : ''),
            fullText: text,
            speaker: speaker,
            desc: desc,
            timestamp: new Date().toISOString(),
            filename: filename,
            size: 0,
        });

        renderHistory();
        updateOutputSize();
    }

    function renderHistory() {
        historyCard.classList.remove('d-none');
        const emptyState = document.getElementById('history-empty-state');
        
        // Always clear the DOM first to prevent stale entries
        historyList.innerHTML = '';

        if (serverHistory.length === 0) {
            if (emptyState) emptyState.classList.remove('d-none');
            return;
        }

        if (emptyState) emptyState.classList.add('d-none');

        serverHistory.forEach((entry) => {
            const item = document.createElement('div');
            item.className = 'list-group-item';
            const date = new Date(entry.timestamp);
            const timeStr = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
            const sizeStr = formatBytes(entry.size || 0);
            const displayText = entry.fullText.length > 80 ? entry.fullText.substring(0, 80) + '...' : entry.fullText;
            
            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-start gap-2">
                    <div class="flex-grow-1" style="min-width:0">
                        <div class="d-flex align-items-center gap-2 mb-1">
                            <span class="badge bg-primary bg-opacity-25 text-primary" style="font-size:0.75rem">${entry.speaker}</span>
                            <small class="text-muted">${timeStr}</small>
                            <small class="text-muted">${sizeStr}</small>
                        </div>
                        <p class="mb-0 text-truncate" style="max-width:400px" title="${escapeHtml(entry.fullText)}">${escapeHtml(displayText)}</p>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-primary flex-shrink-0" data-file="${escapeHtml(entry.filename)}" title="Play audio">
                        <i class="bi bi-play-fill"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-danger flex-shrink-0" data-file-delete="${escapeHtml(entry.filename)}" title="Delete file">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            `;

            historyList.appendChild(item);
        });

        // Play buttons - play audio from server
        historyList.querySelectorAll('[data-file]').forEach(btn => {
            btn.addEventListener('click', () => {
                const filename = btn.dataset.file;
                playFromServer(filename);
            });
        });

        // Delete buttons
        historyList.querySelectorAll('[data-file-delete]').forEach(btn => {
            btn.addEventListener('click', () => {
                const filename = btn.dataset.fileDelete;
                deleteFromServer(filename);
            });
        });
    }

    async function loadServerHistory() {
        try {
            const response = await fetch('/history');
            const data = await response.json();
            
            if (!data.files || data.files.length === 0) {
                serverHistory = [];
                renderHistory();
                updateOutputSize();
                return;
            }

            // Completely replace serverHistory to avoid stale/duplicate entries
            serverHistory = [];
            data.files.forEach(f => {
                serverHistory.push({
                    id: Date.now() + Math.random(),
                    text: f.text || 'Unknown',
                    fullText: f.text || 'Unknown',
                    speaker: f.speaker || 'Unknown',
                    desc: '',
                    timestamp: new Date(f.created * 1000).toISOString(),
                    filename: f.filename,
                    size: f.size,
                });
            });

            renderHistory();
            updateOutputSize();
        } catch (err) {
            console.error('Failed to load history:', err);
        }
    }

    async function playFromServer(filename) {
        const url = `/play/${filename}`;
        
        audioPlayer.pause();
        audioPlayer.src = url;
        
        audioCard.classList.remove('d-none');
        audioCard.classList.add('fade-in');
        btnDownload.classList.remove('d-none');
        
        // For download
        currentAudioUrl = url;
        currentAudioBlob = null; // We load the file directly
        
        // Update audio info
        audioPlayer.addEventListener('loadedmetadata', function onMetadata() {
            if (audioPlayer.duration) {
                audioInfo.textContent = `${audioPlayer.duration.toFixed(1)}s • WAV • From server`;
            }
            audioPlayer.removeEventListener('loadedmetadata', onMetadata);
        }, { once: true });
        
        // Try to play
        audioPlayer.play().catch(err => {
            console.error('Play error:', err);
            setStatus('warning', 'Ready', 'Click the play button in the player');
        });
    }

    async function deleteFromServer(filename) {
        if (!confirm(`Delete file "${filename}"?`)) return;
        
        try {
            const response = await fetch(`/delete/${filename}`, { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                // Also remove from serverHistory
                serverHistory = serverHistory.filter(e => e.filename !== filename);
                renderHistory();
                updateOutputSize();
                setStatus('success', 'Deleted', 'File has been deleted');
            } else {
                setStatus('danger', 'Error', data.error || 'Delete failed');
            }
        } catch (err) {
            console.error('Delete error:', err);
            setStatus('danger', 'Error', 'Delete failed');
        }
    }

    function clearHistory() {
        if (!confirm('Delete all audio files in history?')) return;
        
        // Delete all files from server
        serverHistory.forEach(entry => {
            fetch(`/delete/${entry.filename}`, { method: 'POST' })
                .then(() => console.log('Deleted:', entry.filename))
                .catch(err => console.error('Delete error:', err));
        });
        
        serverHistory = [];
        renderHistory();
        updateOutputSize();
        setStatus('success', 'Deleted', 'All files have been deleted');
    }

    function copyLink() {
        if (!currentAudioUrl) return;
        // Copy audio as download (since blob URLs can't be shared)
        navigator.clipboard.writeText('Audio has been generated. Use the download button.').then(() => {
            const originalText = btnCopyLink.innerHTML;
            btnCopyLink.innerHTML = '<i class="bi bi-check-lg me-1"></i>Copied!';
            setTimeout(() => {
                btnCopyLink.innerHTML = originalText;
            }, 2000);
        });
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function formatNumber(num) {
        if (!num) return '0';
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async function updateOutputSize() {
        try {
            const response = await fetch('/output_size');
            const data = await response.json();
            if (outputSize) {
                outputSize.textContent = formatBytes(data.size);
            }
        } catch (err) {
            console.error('Failed to get output size:', err);
        }
    }
})();
