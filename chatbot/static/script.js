const submitBtn = document.getElementById('submit-btn');
const inputMsg = document.getElementById('input-msg');
const chatbotFrame = document.getElementById('chatbot-frame');
const csrf = document.getElementsByName('csrfmiddlewaretoken');

submitBtn.addEventListener('click', (e) => {
    e.preventDefault();
    
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', csrf[0].value)
    fd.append('text', inputMsg.value);
    fd.append('sender', 'user');

    inputMsg.value = '';

    $.ajax({
        type: 'POST',
        enctype: 'multipart/form-data',
        data: fd,
        success: (responses) => {
            console.log(responses);
            console.log(responses.bot)
            chatbotFrame.innerHTML += `<div class="msg" id="user">${responses.user.text}</div>`;
            chatbotFrame.innerHTML += `<div class="msg" id="bot">${responses.bot.text[0]}</div>`;
            if (responses.bot.extra === 'wait') {
                inputMsg.disabled = true;
                setTimeout(() => {
                    chatbotFrame.innerHTML += `<div class="msg" id="bot">${responses.bot.text[1]}</div>`;
                    chatbotFrame.scrollTop = chatbotFrame.scrollHeight;
                    inputMsg.disabled = false;
                }, 5000);
            }
            // if (responses.bot.exra === 'end') {
            //     inputMsg.disabled = true;
            //     chatbotFrame.innerHTML += `
            //         <div class="fin-discussion">
            //             <img src="/static/remove.png" alt="fin" width="25">
            //             <span>Le bot a mis fin à la discussion</span>
            //         </div>`;
            // }
            chatbotFrame.scrollTop = chatbotFrame.scrollHeight;
        },
        error: (error) => {
            console.log(error);
        },
        cache: false,
        contentType: false,
        processData: false,
    });
});
