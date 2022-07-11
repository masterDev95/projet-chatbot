const submitBtn = document.getElementById('submit-btn');
const inputMsg = document.getElementById('input-msg');
const chatbotFrame = document.getElementById('chatbot-frame');
const csrf = document.getElementsByName('csrfmiddlewaretoken');
const last_question_tag = document.getElementsByName('last_question_tag');
const pb_resolu_count = document.getElementsByName('pb_resolu_count');
const wait = document.getElementsByName('wait');
const fabContainer = document.getElementById('fab-container');
const chatbotContainer = document.getElementById('chatbot-container');
const minimizeChatbot = document.getElementById('minimize-chatbot');
const footerElement = document.getElementsByTagName('footer')[0];
let firstOpen = true;

inputMsg.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        submitBtn.click();
    }
});

submitBtn.addEventListener('click', (e) => {
    e.preventDefault();

    if (inputMsg.value === '') return;
    
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

function chatbotMinimizeToggle() {
    if (firstOpen) {
        firstOpen = false;
        const videoContainer = document.createElement('div');
        const videoAnim = document.createElement('video');
        const firstMessageContainer = document.createElement('div');
        const sonRobot = document.createElement('audio');
        
        videoContainer.classList.add('video-container');
        videoAnim.src = '/static/anim-robot.mp4'
        videoAnim.autoplay = true;
        videoContainer.appendChild(videoAnim);

        firstMessageContainer.classList.add('msg');
        firstMessageContainer.id = 'bot';
        firstMessageContainer.innerText = 'Hello, I\'m EliBlue, how can I help you?';

        sonRobot.src = '/static/son-robot.mp3';
        sonRobot.volume = .5;

        footerElement.classList.add('closed');
        chatbotFrame.style.height = 'calc(100% - var(--hauteur-header) - 8px)';
        chatbotFrame.style.backgroundColor = '#90afe3';
        chatbotFrame.appendChild(videoContainer);
        document.body.appendChild(sonRobot);

        setTimeout(() => {
            sonRobot.play();
        }, 300);

        setTimeout(() => {
            chatbotFrame.style.backgroundColor = 'initial';
            chatbotFrame.removeChild(videoContainer);
            chatbotFrame.appendChild(firstMessageContainer);
            footerElement.classList.remove('closed');
            chatbotFrame.style.height = 'calc(100% - var(--hauteur-footer) - var(--hauteur-header) - 8px)';
        }, 2000);
    }
    chatbotContainer.classList.toggle('closed');
    fabContainer.classList.toggle('closed');
}

fabContainer.addEventListener('click', (e) => {
    chatbotMinimizeToggle();
});

minimizeChatbot.addEventListener('click', (e) => {
    chatbotMinimizeToggle();
});

