// static/appwriteClient.js
import { Client, Account } from 'https://cdn.jsdelivr.net/npm/appwrite@14.0.1';

const client = new Client();
client
    .setEndpoint('https://cloud.appwrite.io/v1') // Your Appwrite endpoint
    .setProject('670da57a0034f6496f28'); // Your project ID

const account = new Account(client);

export { client, account };

