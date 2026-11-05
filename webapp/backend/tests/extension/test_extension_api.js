/**
 * Automated Extension-to-Backend Integration Verification Suite
 * Tests that all message actions dispatched by background.js connect cleanly to the backend.
 */

const BASE_URL = process.env.AGENT_BASE_URL || 'http://127.0.0.1:8000';

async function runTests() {
  console.log(`Starting Extension Integration Tests against: ${BASE_URL}\n`);
  let passed = 0;
  let failed = 0;

  async function test(name, fn) {
    try {
      await fn();
      console.log(`  ✓ PASSED: ${name}`);
      passed++;
    } catch (err) {
      console.error(`  ✗ FAILED: ${name} ->`, err.message);
      failed++;
    }
  }

  // 1. Health Check
  await test('CHECK_AGENT_HEALTH -> GET /api/health', async () => {
    const res = await fetch(`${BASE_URL}/api/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.status !== 'online') throw new Error(`Expected online status, got ${data.status}`);
  });

  // 2. VLM Visual Audit
  await test('RUN_VISUAL_AUDIT -> POST /api/vlm/audit', async () => {
    const res = await fetch(`${BASE_URL}/api/vlm/audit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productName: 'Sony WH-1000XM5', category: 'headphones' })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!data.success || !data.audit) throw new Error('Missing audit data in response');
  });

  // 3. Ask Honest Agent
  await test('ASK_HONEST_QUESTION -> POST /api/agent/ask', async () => {
    const res = await fetch(`${BASE_URL}/api/agent/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: 'Air Jordan 4 Military Black', tier: 'all' })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!data.success || !data.price_matrix) throw new Error('Missing price matrix');
  });

  // 4. In-Cart Alternative Comparison
  await test('COMPARE_IN_CART -> POST /api/agent/compare-in-cart', async () => {
    const res = await fetch(`${BASE_URL}/api/agent/compare-in-cart`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productTitle: 'Generic Noise Cancelling Headphones', currentPrice: 50.0 })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!data.success || !data.top_alternative) throw new Error('Missing top alternative');
  });

  // 5. Recommendations
  await test('GET_RECOMMENDATIONS -> POST /api/agent/recommend', async () => {
    const res = await fetch(`${BASE_URL}/api/agent/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'laptop', category: 'laptops' })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!data.success || !data.recommendation) throw new Error('Missing recommendation');
  });

  console.log(`\nResults: ${passed} passed, ${failed} failed.`);
  if (failed > 0) {
    process.exit(1);
  }
}

runTests();
