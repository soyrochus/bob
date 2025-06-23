function startStream(convId, msgId, agent) {
  const container = document.getElementById('messages');
  const wrapper = document.createElement('div');
  wrapper.className = 'flex items-start gap-3';
  wrapper.innerHTML = `<div class="w-10 h-10 flex items-center justify-center rounded-full bg-[#f1f2f4]">
<svg viewBox="0 0 48 48" width="36" height="36" fill="none" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="24" cy="28" rx="14" ry="10" fill="#fff" stroke="#121416" stroke-width="2"/>
  <ellipse cx="24" cy="14" rx="7" ry="6" fill="#fff" stroke="#121416" stroke-width="2"/>
  <ellipse cx="21.5" cy="13" rx="1.2" ry="1.2" fill="#121416"/>
  <path d="M31 13c2.5-2 6 2 3 4" stroke="#ffa726" stroke-width="2" fill="none"/>
  <path d="M30 13c2-1 5 2 2.2 3.3" stroke="#ffa726" stroke-width="2" fill="none"/>
  <path d="M29 15l2 1" stroke="#ffa726" stroke-width="2" fill="none"/>
</svg>
</div>
<div>
  <div class="text-[#6a7681] text-xs mb-1">Bob</div>
  <div class="bg-[#f1f2f4] rounded-xl px-4 py-3 text-[#121416] max-w-xl"><span class="bob-text markdown-body"></span></div>
</div>`;
  container.appendChild(wrapper);
  const textSpan = wrapper.querySelector('.bob-text');
  const source = new EventSource(`/${convId}/stream?user_msg_id=${msgId}&agent=${agent}`);
  let fullText = '';
  source.onmessage = (event) => {
    if (event.data === '[DONE]') {
      source.close();
    } else {
      fullText += event.data;
      textSpan.innerHTML = marked.parse(fullText);
    }
  };
}

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.markdown-body').forEach(el => {
    el.innerHTML = marked.parse(el.textContent);
  });
});

function openRenameModal(convId, currentTitle) {
  const modal = document.getElementById('rename-modal');
  const input = document.getElementById('rename-input');
  const ok = document.getElementById('rename-ok');
  const cancel = document.getElementById('rename-cancel');
  input.value = currentTitle;
  modal.classList.remove('hidden');

  cancel.onclick = () => {
    modal.classList.add('hidden');
  };

  ok.onclick = async () => {
    const title = input.value;
    const resp = await fetch(`/${convId}/rename`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `title=${encodeURIComponent(title)}`
    });
    if (resp.ok) {
      const html = await resp.text();
      const element = document.getElementById(`conv-${convId}`);
      if (element) element.outerHTML = html;
    }
    modal.classList.add('hidden');
  };
}
