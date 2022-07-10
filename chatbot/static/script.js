const submitBtn = document.getElementById('submit-btn');
const inputMsg = document.getElementById('input-msg');
const chatbotFrame = document.getElementById('chatbot-frame');
const csrf = document.getElementsByName('csrfmiddlewaretoken');
const last_question_tag = document.getElementsByName('last_question_tag');
const pb_resolu_count = document.getElementsByName('pb_resolu_count');
const wait = document.getElementsByName('wait');

inputMsg.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        submitBtn.click();
    }
});

submitBtn.addEventListener('click', (e) => {
    e.preventDefault();
    
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', csrf[0].value)
    fd.append('text', inputMsg.value);
    fd.append('sender', 'user');
    fd.append('last_question_tag', last_question_tag[0].value);
    fd.append('pb_resolu_count', pb_resolu_count[0].value);
    fd.append('wait', wait[0].value);

    inputMsg.value = '';

    $.ajax({
        type: 'POST',
        enctype: 'multipart/form-data',
        data: fd,
        success: (responses) => {
            console.log(responses);
            console.log(responses.bot);
            console.log(responses.vars);
            last_question_tag[0].value = responses.vars.last_question_tag;
            pb_resolu_count[0].value = responses.vars.pb_resolu_count;
            wait[0].value = responses.vars.wait;
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
            if (responses.bot.extra === 'end') {
                inputMsg.disabled = true;
                chatbotFrame.innerHTML += 
                    `<div class="fin-discussion">
                        <img src="/static/remove.png" alt="fin" width="25">
                        <span>Le bot a mis fin à la discussion</span>
                    </div>`;
            }
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
