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
                if (Array.isArray(r.answer) && r.answer.length > 0) {
                    let msg2 = {
                        name: "Sam",
                        answers: r.answer,
                        tag: r.answer[0].toLowerCase() // Use the first answer for tag checking
                    };
                    this.messages.push(msg2);
                    this.updateChatText(msg2);
                    this.args.messageInput.val(''); // Clear the input

                    // Check for follow-up action
                    if (msg2.tag === "gender") {
                        this.askUserForMoreInfo();
                    }
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

    askUserForMoreInfo() {
        const followUp = prompt("Is that all you're feeling? Would you like to tell me more or see a nearby doctor? (type 'more' or 'doctor')");
        if (followUp.toLowerCase() === 'more') {
            this.updateChatText({ name: "Sam", message: "State the symptoms you have, for potential diagnosis." });
        } else if (followUp.toLowerCase() === 'doctor') {
            this.getUserLocation((lat, lng) => {
                $('#map').show(); // Show the map
                this.initMap(lat, lng);
            });
        }
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
                html += `<div class="messages__item messages__item--support">${item.answers[0]}</div>`;
            } else {
                html += `<div class="messages__item messages__item--support">${item.answers[1]}</div>`;
            }
        } else {
            html += `<div class="messages__item messages__item--visitor">${item.message}</div>`;
        }
        return html;
    }

    getUserLocation(callback) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((position) => {
                callback(position.coords.latitude, position.coords.longitude);
            }, () => {
                alert('Unable to retrieve your location.');
            });
        } else {
            alert('Geolocation is not supported by this browser.');
        }
    }

    initMap(lat, lng) {
        const userLocation = { lat: lat, lng: lng };
        const map = new google.maps.Map(document.getElementById('map'), {
            center: userLocation,
            zoom: 15,
        });

        const service = new google.maps.places.PlacesService(map);
        service.nearbySearch({
            location: userLocation,
            radius: 5000, // 5 km radius
            type: ['hospital']
        }, (results, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK) {
                for (let i = 0; i < results.length; i++) {
                    this.createMarker(results[i], map);
                }
            }
        });
    }

    createMarker(place, map) {
        const marker = new google.maps.Marker({
            map: map,
            position: place.geometry.location,
        });

        const infowindow = new google.maps.InfoWindow();
        google.maps.event.addListener(marker, 'click', () => {
            infowindow.setContent(place.name);
            infowindow.open(map, marker);
        });
    }
}

$(document).ready(() => {
    const chatbox = new Chatbox();
});