class Chatbox {
    constructor() {
        this.args = {
            chatBox: $('.chatbox'),
            sendButton: $('#sendButton'),
            messageInput: $('#messageInput'),
            chatMessages: $('#chatboxMessages'),
            hospital_Info: $('.hospital_Info'),
            mapDiv: $('#mapDiv'),
            mapElement: $('.hospital_Map'),
            hospitalList: $('#hospitalList')
        };

        this.messages = [];
        this.specificTags = ["greeting", "goodbye", "work", "medical", "center", "who", "thanks", "joke", "name", "age", "gender", "redirect", "hospital", "not_understand"];
        this.onSendButton = this.onSendButton.bind(this);
        this.init();
    }

    init() {
        this.args.sendButton.on('click', this.onSendButton);
        this.args.messageInput.on("keyup", (e) => {
            if (e.key === "Enter") {
                this.onSendButton();
            }
        }); 
        this.showMap(); 
        this.showMap(); 
        //this.args.closeMapButton.on('click', () => this.args.hospital_Info.hide()); // Close the hospital info
    }

    getUserLocation() {
        return new Promise((resolve, reject) => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition((position) => {
                    resolve({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    });
                }, (error) => {
                    console.error('Error getting user location:', error);
                    resolve(null);
                }, {
                    enableHighAccuracy: true // Enable high accuracy
                });
            } else {
                console.error('Geolocation not supported');
                resolve(null);
            }
        });
    }

    async getNearbyHospitals(lat, lng) {
        return new Promise((resolve, reject) => {
            const location = new google.maps.LatLng(lat, lng);
            const request = {
                location: location,
                radius: '5000',
                type: ['hospital']
            };

            const service = new google.maps.places.PlacesService(this.args.mapElement[0]);

            service.nearbySearch(request, (results, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK) {
                    const hospitals = results.slice(0, 3).map(place => ({
                        name: place.name,
                        vicinity: place.vicinity,
                        geometry: place.geometry
                    }));
                    resolve(hospitals);
                } else {
                    console.error('Error fetching nearby hospitals:', status);
                    resolve([]);
                }
            });
        });
    }

    async showMap() {
        const userLocation = await this.getUserLocation();
        if (!userLocation) {
            alert('Could not get your location');
            return;
        }

        const lat = userLocation.lat;
        const lng = userLocation.lng;

        // Toggle the visibility of the mapDiv
        //this.args.mapDiv.toggle();

        const map = new google.maps.Map(this.args.mapDiv[0], {
            center: { lat: lat, lng: lng },
            zoom: 12
        });

        // Mark the user's location
        const advancedMarker = new google.maps.marker.AdvancedMarkerElement({
            position: { lat: lat, lng: lng },
            map: map,
            title: 'Your Location',
            icon: {
                url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png', // Custom blue dot marker
                scaledSize: new google.maps.Size(30, 30) // Customize size
            }
        }); 

        const hospitals = await this.getNearbyHospitals(lat, lng);

        if (hospitals && hospitals.length > 0) {
            hospitals.forEach(hospital => {
                const advancedMarker = new google.maps.marker.AdvancedMarkerElement({
                    position: hospital.geometry.location,
                    map: map,
                    title: hospital.name
                });
            });


            this.displayHospitalsList(hospitals);

            // Send the hospital list to the chatbox
            /*
            const hospitalMessages = hospitals.map(hospital => `${hospital.name}, located at ${hospital.vicinity}`);
            let msg2 = { name: "Sam", answers: hospitalMessages };
            this.messages.push(msg2);
            this.updateChatText(msg2);
            */
        } else {
            console.log('No hospitals found');
        }
    }

    displayHospitalsList(hospitals) {
        // Clear the existing list
        this.args.hospitalList.empty();

        hospitals.forEach(hospital => {
            const listItem = `
                <div class="hospital-item">
                    <strong>${hospital.name}</strong><br>
                    Address: ${hospital.vicinity}
                </div>`;
            this.args.hospitalList.append(listItem);
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
        /*
        if (text1.toLowerCase().includes("hospital") || text1.toLowerCase().includes("medical center")) {
            const userLocation = await this.getUserLocation();  // First, get user location
            if (userLocation) {
                const hospitals = await this.getNearbyHospitals(userLocation.lat, userLocation.lng);
                let msg2 = { name: "Sam", answers: hospitals };
                this.messages.push(msg2);
                this.updateChatText(msg2);

                // Show the map with user's current location and hospitals
                if (hospitals.length > 0) {
                    this.showMap(userLocation.lat, userLocation.lng); // Pass the user's location
                } else {
                    this.updateChatText({ name: "Sam", message: "No hospitals found nearby." });
                }
            } else {
                this.updateChatText({ name: "Sam", message: "Unable to get your location." });
            }

            this.args.messageInput.val(''); // Clear the input
            return;
        }
*/


        this.args.messageInput.val('');
        // If not hospital-related, send to the backend
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
                        tag: r.answer[0].toLowerCase()
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

    

    updateChatText(message) {
        console.log("updateChatText called for message: ", message);
    
        const html = this.formatMessage(message);
        this.args.chatMessages.append(html);
        this.args.chatMessages.scrollTop(this.args.chatMessages[0].scrollHeight);
    
        // Check if the message is from the bot (e.g., "Sam") and contains specific tags
        if (message.name === "Sam") {
            if (message.tag === "redirect" && message.answers[2] === "map") {
                this.showMap();
                this.args.mapElement.show();
    
                // After showing map, append a custom message (if needed)
                const customMessage = `<div class="messages__item messages__item--support">If you still have a health complaint, please kindly state it</div>`;
                this.args.chatMessages.append(customMessage);
                this.args.chatMessages.scrollTop(this.args.chatMessages[0].scrollHeight);
    
            } else if (!this.specificTags.includes(message.tag)) {
                // Append a custom message when the bot's message does not match a specific tag
                const customMessage = `<div class="messages__item messages__item--support">Tell me any other health challenge that you may be experiencing if any</div>`;
                this.args.chatMessages.append(customMessage);
                this.args.chatMessages.scrollTop(this.args.chatMessages[0].scrollHeight);
            }
        }
    }

    formatMessage(item) {
        let html = '';
        if (item.name === "Sam") {
            if (!this.specificTags.includes(item.tag)) {
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