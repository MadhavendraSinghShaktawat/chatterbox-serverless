/**
 * Test script for ChatterboxTTS RunPod Serverless Function (JavaScript)
 */

// Configuration - Use environment variables for security
const RUNPOD_ENDPOINT = process.env.RUNPOD_ENDPOINT;
const RUNPOD_API_KEY = process.env.RUNPOD_API_KEY;

// Convert file to base64 (for Node.js)
function fileToBase64(filePath) {
    if (typeof require !== 'undefined') {
        const fs = require('fs');
        try {
            const fileBuffer = fs.readFileSync(filePath);
            return fileBuffer.toString('base64');
        } catch (error) {
            console.error("❌ Error reading file:", error);
            return null;
        }
    } else {
        console.error("❌ File reading not supported in browser. Use file input instead.");
        return null;
    }
}

// Test the RunPod endpoint
async function testRunPodEndpoint() {
    const testText = `
    So there I was, standing in the grocery store checkout line, when I noticed something absolutely bizarre. 
    The person in front of me was buying exactly 47 bananas. Not 46, not 48, but exactly 47. 
    I couldn't help but wonder what kind of life decisions led to this moment.
    `;

    // For Node.js testing, encode voice file
    let voiceBase64 = null;
    if (typeof require !== 'undefined') {
        voiceBase64 = fileToBase64("../voices/man1.mp3"); // Adjust path as needed
        if (!voiceBase64) {
            console.error("❌ Failed to encode voice file. Please check the path.");
            return;
        }
    } else {
        console.error("❌ Please provide base64 encoded voice file for browser testing");
        return;
    }

    const payload = {
        input: {
            text: testText.trim(),
            voice_file: voiceBase64,
            settings: {
                exaggeration: 0.7,
                cfg_weight: 0.5,
                temperature: 0.8,
                min_p: 0.05,
                top_p: 1.0,
                repetition_penalty: 1.2
            }
        }
    };

    console.log("🚀 Testing RunPod ChatterboxTTS Serverless Function...");
    console.log(`📝 Text length: ${testText.length} characters`);
    console.log(`🎵 Voice file size: ${voiceBase64.length} base64 characters`);
    console.log("⏳ Sending request...");

    try {
        const startTime = Date.now();
        
        const response = await fetch(RUNPOD_ENDPOINT, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${RUNPOD_API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const endTime = Date.now();
        const duration = (endTime - startTime) / 1000;

        console.log(`⏱️  Request took: ${duration.toFixed(2)} seconds`);
        console.log(`📊 Status Code: ${response.status}`);

        if (response.ok) {
            const result = await response.json();
            console.log("✅ Request successful!");
            console.log("📄 Response:", JSON.stringify(result, null, 2));

            // Save audio if present (Node.js only)
            if (result.output && result.output.audio_base64 && typeof require !== 'undefined') {
                const fs = require('fs');
                const audioBuffer = Buffer.from(result.output.audio_base64, 'base64');
                fs.writeFileSync('test_output.wav', audioBuffer);
                console.log("🎵 Audio saved to: test_output.wav");
            }

        } else {
            console.error(`❌ Request failed with status ${response.status}`);
            const errorText = await response.text();
            console.error("📄 Response:", errorText);
        }

    } catch (error) {
        console.error("❌ Request error:", error);
    }
}

// Generate example payload for manual testing
function generateExamplePayload() {
    console.log("\n" + "=".repeat(50));
    console.log("📋 Example Payload for Manual Testing:");
    console.log("=".repeat(50));
    
    const examplePayload = {
        input: {
            text: "Hello world! This is a test of ChatterboxTTS on RunPod.",
            voice_file: "BASE64_ENCODED_VOICE_FILE_HEREe", 
            settings: {
                exaggeration: 0.5,
                cfg_weight: 0.5,
                temperature: 0.8,
                min_p: 0.05,
                top_p: 1.0,
                repetition_penalty: 1.2
            }
        }
    };
    
    console.log(JSON.stringify(examplePayload, null, 2));
}

// Main execution
if (typeof require !== 'undefined' && require.main === module) {
    // Node.js execution
    console.log("🧪 ChatterboxTTS RunPod Serverless Test (Node.js)");
    console.log("=".repeat(50));
    
    if (!RUNPOD_API_KEY || RUNPOD_ENDPOINT.includes("YOUR_ENDPOINT_ID")) {
        console.log("⚠️  Please set environment variables:");
        console.log("   RUNPOD_ENDPOINT=https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run");
        console.log("   RUNPOD_API_KEY=your_actual_api_key");
        console.log();
        console.log("💡 Example usage:");
        console.log("   RUNPOD_ENDPOINT=https://api.runpod.ai/v2/abc123/run RUNPOD_API_KEY=your_key node test_runpod.js");
        console.log();
        generateExamplePayload();
    } else {
        testRunPodEndpoint();
    }
} else if (typeof window !== 'undefined') {
    // Browser execution
    console.log("🧪 ChatterboxTTS RunPod Serverless Test (Browser)");
    console.log("Use the testRunPodEndpoint() function after providing base64 voice data");
    generateExamplePayload();
} 