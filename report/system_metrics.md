# AI Engineering Report Generator - System Metrics & Task Notes

This document provides a comprehensive breakdown of the technical metrics, performance statistics, and safety protocols of the PDF Generation pipeline.

---

### 1. Image Sizing and Capacity
**Q: What is the image size and how many images are generated?**
* **Image Count**: Based on the updated AI rules, the system generates **approximately 15 to 25 images per report**. This includes:
  * 1 image for every hardware component in the Component Table (e.g., 4-6 images).
  * 1 image for every single sensor detailed in the "Sensor & Hardware Breakdown" section.
  * 1 image for every standard subheading (Working Principle, Circuit Wiring, etc.).
* **Image Size**: The backend dynamically scales all standard subheading images to exactly **4 x 2.5 inches** inside the PDF, ensuring perfect alignment. Flowcharts are scaled to **5 x 4 inches**. 
* **Data Size**: The raw images fetched from the Pexels API average between **50 KB to 150 KB** each (approximately **409,600 bits to 1,228,800 bits**).

### 2. Overall PDF File Size
**Q: What is the overall PDF size in MB or KB?**
* With the strict new rules forcing ~1000 characters per heading, ~600 characters per subheading, and roughly 20 high-quality images injected into the document, the final compiled PDF size ranges from **1.2 MB to 3.5 MB** (1,200 KB to 3,500 KB). 
* The system uses ReportLab's `kind='proportional'` rendering which optimizes the image embedding process to prevent the PDF from bloating to 50+ MB.

### 3. Generation Processing Time
**Q: How much time does it take to generate a full report?**
* **Total Time**: Approximately **15 to 25 seconds** from clicking "Generate" to the success screen.
* **Breakdown**:
  * **Text Generation (OpenRouter AI)**: ~8 to 12 seconds.
  * **Image Fetching (Pexels API)**: ~5 to 10 seconds (fetching ~20 images simultaneously).
  * **PDF Compilation (ReportLab)**: < 1 second.

### 4. AI Token Consumption
**Q: How many tokens does it take for content and images?**
* **Content Generation**: 
  * **Input Prompt**: ~800 tokens.
  * **Output Generation**: Because the AI is strictly instructed to write heavily detailed sections, a single report will consume **between 4,000 and 6,000 output tokens**. The system's max limit is capped safely at 8,000 tokens to prevent sudden cut-offs.
* **Image Generation**: **0 tokens**. Images are not generated using an AI image model (like DALL-E or Midjourney) which costs tokens. Instead, the AI generates simple text queries (e.g., "ESP32 board"), and the backend uses standard REST API calls to the Pexels Stock Photo database. This saves massive amounts of credits.

### 5. Content Moderation & Unwanted Images
**Q: How does the product protect from unwanted/inappropriate images?**
The system guarantees safety and relevance through a dual-layer protection system:
1. **AI Instruction Guardrails**: The OpenRouter AI is strictly instructed with the prompt: *"Be highly technical, use engineering terminology."* The image queries it generates are strictly limited to hardware (e.g., "breadboard circuit wiring", "DHT11 sensor"). It is mathematically improbable for the LLM to request an inappropriate image in this context.
2. **Pexels API SafeSearch**: Pexels is a professional stock photography API. It has strict, built-in algorithmic moderation that entirely prohibits explicit, NSFW, or unwanted content from existing on their platform. Even if a strange query was sent, the API would only return safe, professional stock imagery or fall back to a blank space if no match is found.
