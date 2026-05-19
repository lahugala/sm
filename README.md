# SMS Gateway Web App

A modern, responsive single-page application built with Vue 3 and Vite that serves as a powerful frontend for your Android SMS Gateway. This application allows you to connect to an Android device (running a compatible SMS Gateway server app) and seamlessly manage your text messaging workflows directly from your browser.

## 🚀 Features

* **Send & Schedule SMS:** Compose messages, add multiple recipients, and optionally schedule them for later.
* **Bulk Messaging:** Import contacts via CSV or vCard (.vcf) formats to send bulk SMS campaigns.
* **Contact Management:** Save frequently used contacts for easy access later without needing to re-import.
* **Advanced Routing:** Choose between SIM 1 or SIM 2, set message priority, and specify time-to-live (TTL).
* **Delivery Reports:** Track the exact status of your sent messages (Pending, Sent, Delivered, Failed).
* **History & Logs:** View past messages, including delivery statuses and error logs.
* **Modern UI/UX:** A stunning, fully responsive dark-mode interface built with custom CSS, featuring smooth transitions and micro-animations.

## 🛠️ Technology Stack

* **Frontend Framework:** Vue 3 (Composition API, `<script setup>`)
* **Build Tool:** Vite
* **Routing:** Vue Router
* **State Management:** Reactive Vue store patterns (Custom)
* **Styling:** Vanilla CSS with custom design system tokens (Dark mode, glassmorphism, responsive grid/flexbox layouts)

## 📦 Getting Started

### Prerequisites
* Node.js (v16.0 or higher recommended)
* npm or yarn
* An Android device running the SMS Gateway app

### Installation

1. Clone the repository and navigate to the project folder.
2. Install the dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173`.

## ⚙️ Configuration

Before sending messages, you need to configure your gateway connection:
1. Open the **Settings** page in the application.
2. Enter your Android device's local IP address or your cloud API endpoint.
3. Provide the correct API key/credentials as configured in your mobile gateway app.
4. Save your configuration to establish the connection.

## 📝 Contact Formatting

When importing contacts via CSV:
* Ensure your CSV file has columns for `name` and `phone`.
* Phone numbers should ideally be in international format (e.g., `+1234567890`).

## 📄 License

This project is open-source and available for customization and personal use.
