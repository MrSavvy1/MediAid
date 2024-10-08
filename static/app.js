class Chatbox {
    constructor() {
        this.args = {
            chatBox: $('.chatbox'),
            sendButton: $('#sendButton'),
            messageInput: $('#messageInput'),
            chatMessages: $('#chatboxMessages')
        };

        this.messages = [];
        this.specificTags = ["greeting", "goodbye", "work", "who", "thanks", "joke", "name", "age", "gender", "not_understand"];
        this.init();
    }

    init() {
        this.args.sendButton.on('click', () => this.onSendButton());
        this.args.messageInput.on("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton();
            }
        });
    }

    onSendButton() {
        const text1 = this.args.messageInput.val().trim();
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 };
        this.messages.push(msg1);
        this.updateChatText(msg1);

        $.ajax({
            type: 'POST',
            url: `http://127.0.0.1:5000/predict`,
            contentType: 'application/json',
            data: JSON.stringify({ message: text1 }),
            success: (r) => {
                let msg2 = {
                    name: "Sam",
                    message1: r.answer[0],
                    message2: r.answer[1],
                    message3: r.answer[2],
                    message4: r.answer[3]
                };
                this.messages.push(msg2);
                this.updateChatText(msg2);
                this.args.messageInput.val(''); // Clear the input
            },
            error: (error) => {
                console.error('Error:', error);
                this.updateChatText({ name: "Sam", message: "An error occurred. Please try again." });
                this.args.messageInput.val(''); // Clear the input
            }
        });
    }

    updateChatText(message) {
        const html = this.formatMessage(message);
        this.args.chatMessages.append(html);
        this.args.chatMessages.scrollTop(this.args.chatMessages[0].scrollHeight); // Scroll to bottom
    }

    formatMessage(item) {
        let html = '';
        if (item.name === "Sam") {
            // Example of specific tag checking
            if (this.specificTags.includes(item.message1.toLowerCase())) {
                html += `<div class="messages__item messages__item--support">${item.message2 || ''}</div>`;
            } else if (item.message1 === "center") {
                html += `<div class="messages__item messages__item--support">You can ask me if you want anything else.</div>`;
                html += `<div class="messages__item messages__item--support">Nearby medical centers: ${item.message4.join(', ')}</div>`;
                html += `<div class="messages__item messages__item--support">Precautions: ${item.message3.join(', ')}</div>`;
            } else {
                html += `<div class="messages__item messages__item--support">${item.message1 || ''}</div>`;
            }
        } else {
            html += `<div class="messages__item messages__item--visitor">${item.message}</div>`;
        }
        return html;
    }
}

$(document).ready(() => {
    const chatbox = new Chatbox();
});
