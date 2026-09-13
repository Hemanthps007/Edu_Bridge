// EduBridge — AI Advisor Chatbot Logic
async function sendMessage() {
  const inp = document.getElementById('chatInput');
  if (!inp) return;
  const msg = inp.value.trim();
  if (!msg) return;
  inp.value = '';

  const chatArea = document.getElementById('chatArea');
  if (!chatArea) return;

  // Append user bubble
  const userDiv = document.createElement('div');
  userDiv.className = 'msg-user';
  userDiv.innerHTML = `<div class="text-xs text-slate-200 leading-relaxed">${escapeHtml(msg)}</div>`;
  chatArea.appendChild(userDiv);

  // Append typing indicator
  const typingDiv = document.createElement('div');
  typingDiv.className = 'msg-ai';
  typingDiv.id = 'typingBubble';
  typingDiv.innerHTML = `
    <div class="flex items-center gap-1.5 py-1">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>`;
  chatArea.appendChild(typingDiv);
  chatArea.scrollTop = chatArea.scrollHeight;

  try {
    const res = await fetch('/api/chat/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    typingDiv.remove();

    const aiDiv = document.createElement('div');
    aiDiv.className = 'msg-ai';
    let sourcesHtml = '';
    if (data.sources && data.sources.length) {
      sourcesHtml = `<div class="mt-3 pt-2 border-t border-slate-100 flex items-center gap-1.5 flex-wrap text-[10px] text-slate-400">
        <i class="fa-solid fa-quote-left text-[8px]"></i> Sources: ${data.sources.map(s => `<span class="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-medium">${s}</span>`).join('')}
      </div>`;
    }

    aiDiv.innerHTML = `
      <div class="flex items-center gap-2 mb-2 pb-2 border-b border-slate-100">
        <div class="w-5 h-5 rounded bg-sky-100 text-sky-700 flex items-center justify-center text-[10px] font-bold">
          <i class="fa-solid fa-brain"></i>
        </div>
        <span class="font-bold text-xs text-slate-900">EduBridge AI</span>
      </div>
      <div class="prose-ai">${formatMarkdown(data.response || data.error)}</div>
      ${sourcesHtml}`;
    chatArea.appendChild(aiDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
  } catch (err) {
    typingDiv.remove();
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>');
}
