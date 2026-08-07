const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const chatForm = document.getElementById('chatForm');

// Auto-resize textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Handle Enter key (send) and Shift+Enter (newline)
messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// Handle form submission
function handleSubmit(e) {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Show loading indicator
    showLoadingIndicator();

    // Send to API
    sendMessage(message);
}

function addMessage(text, sender) {
    const messageGroup = document.createElement('div');
    messageGroup.className = 'message-group';

    const message = document.createElement('div');
    message.className = `message ${sender}-message`;

    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Parse markdown and render HTML
    content.innerHTML = parseMarkdown(text);

    message.appendChild(content);
    messageGroup.appendChild(message);
    chatMessages.appendChild(messageGroup);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showLoadingIndicator() {
    const messageGroup = document.createElement('div');
    messageGroup.className = 'message-group';
    messageGroup.id = 'loadingIndicator';

    const message = document.createElement('div');
    message.className = 'message bot-message';

    const content = document.createElement('div');
    content.className = 'message-content loading';
    content.innerHTML = '<span></span><span></span><span></span>';

    message.appendChild(content);
    messageGroup.appendChild(message);
    chatMessages.appendChild(messageGroup);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLoadingIndicator() {
    const loading = document.getElementById('loadingIndicator');
    if (loading) loading.remove();
}

async function sendMessage(message) {
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        removeLoadingIndicator();

        if (!response.ok) {
            const error = await response.json();
            addMessage(`Error: ${error.detail || 'Unknown error occurred'}`, 'bot');
            return;
        }

        const data = await response.json();
        addMessage(data.response, 'bot');
    } catch (error) {
        removeLoadingIndicator();
        addMessage(`Error: ${error.message}`, 'bot');
    }
}

// Markdown Parser (basic but comprehensive)
function parseMarkdown(text) {
    let html = escapeHtml(text);

    // Code blocks (triple backticks)
    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

    // Inline code (single backticks)
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Headers
    html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/_(.*?)_/g, '<em>$1</em>');

    // Links
    html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');

    // Blockquotes
    html = html.replace(/^&gt; (.*?)$/gm, '<blockquote>$1</blockquote>');

    // Unordered lists
    html = html.replace(/^\* (.*?)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    // Ordered lists
    html = html.replace(/^\d+\. (.*?)$/gm, '<li>$1</li>');

    // Line breaks
    html = html.replace(/\n\n/g, '</p><p>');
    html = '<p>' + html + '</p>';

    // Tables (simple pipe-delimited)
    html = html.replace(/\|(.+)\|/g, function(match) {
        const rows = match.split('\n').filter(r => r.trim());
        let table = '<table>';
        rows.forEach((row, idx) => {
            const cells = row.split('|').map(c => c.trim()).filter(c => c);
            const tag = idx === 0 ? 'th' : 'td';
            table += '<tr>' + cells.map(c => `<${tag}>${c}</${tag}>`).join('') + '</tr>';
        });
        table += '</table>';
        return table;
    });

    return html;
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Focus input on load
window.addEventListener('load', () => {
    messageInput.focus();
});
