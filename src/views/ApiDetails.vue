<template>
  <div class="animate-in">
    <div class="page-header">
      <h1 class="page-title">API Details</h1>
      <p class="page-subtitle">Learn how to programmatically interact with the SMS Gateway</p>
    </div>

    <div class="api-grid">
      <!-- Intro Card -->
      <div class="card">
        <h3 class="section-title">🔌 Connection Overview</h3>
        <p class="endpoint-desc">
          The SMS Gateway exposes a REST API locally over HTTP or via the Cloud. To connect, use your gateway IP address (e.g., <code>http://192.168.1.x:8080</code>) and provide Basic Authentication credentials configured in the Android app. All responses are in JSON format.
        </p>
      </div>

      <!-- Endpoints -->
      <div class="card">
        <h3 class="section-title">POST /message</h3>
        <p class="endpoint-desc">Send an SMS or bulk SMS. Use <code>/messages</code> for Cloud mode.</p>
        
        <h4>Request Payload (JSON)</h4>
        <pre><code>{
  "message": "Hello World!",
  "phoneNumbers": ["+1234567890", "+0987654321"],
  "withDeliveryReport": true,
  "simNumber": 1,
  "priority": 0,
  "ttl": 3600,
  "scheduleAt": "2026-05-17T08:00:00.000Z"
}</code></pre>
      </div>

      <div class="card">
        <h3 class="section-title">GET /message/:id</h3>
        <p class="endpoint-desc">Get the delivery status of a specific message.</p>
        <h4>Response (JSON)</h4>
        <pre><code>{
  "id": "abc-123",
  "state": "Delivered",
  "recipients": [
    { "phoneNumber": "+1234567890", "state": "Delivered" }
  ]
}</code></pre>
      </div>

      <div class="card">
        <h3 class="section-title">GET /inbox</h3>
        <p class="endpoint-desc">Fetch received messages (Local Mode Only).</p>
        <h4>Query Parameters</h4>
        <ul class="param-list">
          <li><code>type</code>: 'SMS' | 'DATA_SMS' | 'MMS' (default 'SMS')</li>
          <li><code>limit</code>: Max results per page (default 50)</li>
          <li><code>offset</code>: Pagination offset (default 0)</li>
          <li><code>from</code>: Filter by sender number</li>
          <li><code>to</code>: Filter by recipient number</li>
        </ul>
      </div>
      
      <div class="card">
        <h3 class="section-title">POST /inbox/refresh</h3>
        <p class="endpoint-desc">Trigger a refresh of the inbox (re-reads messages from Android, Local Mode Only).</p>
        <h4>Request Payload (JSON)</h4>
        <pre><code>{
  "since": "2026-05-17T00:00:00.000Z",
  "until": "2026-05-18T00:00:00.000Z"
}</code></pre>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.api-grid {
  display: grid;
  gap: var(--space-lg);
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: var(--space-sm);
  font-family: var(--font-mono);
  color: var(--clr-accent-secondary);
}

.endpoint-desc {
  color: var(--clr-text-secondary);
  margin-bottom: var(--space-md);
  font-size: 14px;
}

pre {
  background: rgba(108, 99, 255, 0.05);
  border: 1px solid var(--clr-border);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--clr-text-primary);
}

h4 {
  font-size: 13px;
  margin-bottom: var(--space-sm);
  color: var(--clr-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.param-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.param-list li {
  margin-bottom: var(--space-xs);
  font-size: 13px;
  color: var(--clr-text-secondary);
  padding-left: 14px;
  position: relative;
}

.param-list li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: var(--clr-accent-primary);
}

.param-list code {
  background: rgba(108, 99, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--clr-accent-primary);
  font-family: var(--font-mono);
  font-size: 12px;
}
</style>
