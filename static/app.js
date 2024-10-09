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
        this.onSendButton = this.onSendButton.bind(this); // Bind here
        this.init();
    }

    init() {
        this.args.sendButton.on('click', this.onSendButton);
        this.args.messageInput.on("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton();
            }
        });
        this.args.closeHospitalInfo.on('click', () => {
            this.args.hospitalInfo.hide(); // Hide the hospital info box
        });
    }

    async getNearbyHospitals() {
        // Fetch the user's location
        const g = await this.getUserLocation();

        if (g) {
            const response = await $.ajax({
                type: 'GET',
                url: `https://maps.googleapis.com/maps/api/place/nearbysearch/json`,
                data: {
                    location: `${g.lat},${g.lng}`,  // User's latitude and longitude
                    radius: 5000,  // Search within 5 km
                    type: 'hospital',
                    key: 'YOUR_GOOGLE_MAPS_API_KEY' // Add your API key here
                }
            });

            return response.results.map(place => `${place.name} - ${place.vicinity}`).slice(0, 3); // Get top 3 hospitals
        }

        return ["Unable to retrieve location."];
    }

    getUserLocation() {
        return new Promise((resolve) => {
            // Get user's location using Geolocation API
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition((position) => {
                    resolve({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    });
                }, () => {
                    resolve(null);
                });
            } else {
                resolve(null);
            }
        });
    }

    async onSendButton() {
        const text1 = this.args.messageInput.val().trim();
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 };
        this.messages.push(msg1);
        this.updateChatText(msg1);

        // Check if user is asking for hospitals
        if (text1.toLowerCase().includes("hospital") || text1.toLowerCase().includes("medical center")) {
            const hospitals = await this.getNearbyHospitals();
            let msg2 = { name: "Sam", answers: hospitals };
            this.messages.push(msg2);
            this.updateChatText(msg2);
            this.args.messageInput.val(''); // Clear the input
            return; // Skip the AJAX request
        }

        $.ajax({
            type: 'POST',
            url: `http://127.0.0.1:5000/predict`,
            contentType: 'application/json',
            data: JSON.stringify({ message: text1 }),
            success: (r) => {
                if (Array.isArray(r.answer) && r.answer.length > 0) {
                    let msg2 = {
                        name: "Sam",
                        answers: r.answer,
                        tag: r.answer[0].toLowerCase() // Use the first answer for tag checking
                    };
                    this.messages.push(msg2);
                    this.updateChatText(msg2);
                    this.args.messageInput.val(''); // Clear the input
                } else {
                    this.updateChatText({ name: "Sam", message: "No valid response received." });
                }
            },
            error: (error) => {
                console.error('Error:', error);
                this.updateChatText({ name: "Sam", message: "An error occurred. Please try again." });
                this.args.messageInput.val(''); // Clear the input
            }
        });
    }

    showHospitalInfo(hospitals) {
        // Format hospital information for display
        const hospitalHTML = hospitals.map(hospital => 
            `<div>${hospital.name} - ${hospital.address}</div>`
        ).join('');
        
        this.args.hospitalList.html(hospitalHTML);
        this.args.hospitalInfo.show(); // Show the hospital info box
    }


    updateChatText(message) {
        const html = this.formatMessage(message);
        this.args.chatMessages.append(html);
        this.args.chatMessages.scrollTop(this.args.chatMessages[0].scrollHeight); // Scroll to bottom
    }

    formatMessage(item) {
        let html = '';
        if (item.name === "Sam") {
            if (!this.specificTags.includes(item.tag)) {
                // Display multiple answers with their corresponding labels
                if (item.answers.length > 0) {
                    html += `<div class="messages__item messages__item--support"><strong>Diagnose Disease:</strong> ${item.answers[0]}</div>`;
                }
                if (item.answers.length > 1) {
                    html += `<div class="messages__item messages__item--support"><strong>Diagnosis:</strong> ${item.answers[1]}</div>`;
                }
                if (item.answers.length > 2) {
                    html += `<div class="messages__item messages__item--support"><strong>Precaution:</strong> ${item.answers[2]}</div>`;
                }
            } else {
                html += `<div class="messages__item messages__item--support">${item.answers[1]}</div>`;
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
